"""
链上事件抓取器 - 使用 web3.py 从 BSC 链读取合约事件
"""

import time
from datetime import datetime, timezone
from typing import Optional

from web3 import Web3
from web3.contract.contract import ContractEvents

import config
from data.cache import (
    init_db,
    get_last_synced_block,
    update_sync_metadata,
    insert_wallet_created,
    insert_transaction_executed,
    insert_executed,
    insert_eth_transferred,
    insert_gas_received,
    commit,
)


def get_web3() -> Web3:
    """获取 Web3 实例"""
    return Web3(Web3.HTTPProvider(config.BSC_RPC_URL))


def get_contract(w3: Web3):
    """获取合约实例"""
    return w3.eth.contract(
        address=Web3.to_checksum_address(config.CONTRACT_ADDRESS),
        abi=config.CONTRACT_ABI,
    )


def get_block_timestamp(w3: Web3, block_number: int) -> datetime:
    """获取区块时间戳"""
    block = w3.eth.get_block(block_number)
    return datetime.fromtimestamp(block.timestamp, tz=timezone.utc)


def fetch_events_from_chain(
    w3: Optional[Web3] = None,
    from_block: int = 0,
    to_block: int = "latest",
    verbose: bool = False,
) -> dict:
    """
    从链上抓取所有事件并存储到缓存
    
    返回: 统计信息
    """
    if w3 is None:
        w3 = get_web3()

    contract = get_contract(w3)
    conn = init_db()

    # 获取最新区块
    latest_block = w3.eth.block_number
    if to_block == "latest":
        to_block = latest_block

    # 获取上次同步的区块
    last_synced = get_last_synced_block(conn)
    actual_from_block = max(from_block, last_synced + 1) if last_synced > 0 else from_block

    if actual_from_block >= to_block:
        if verbose:
            print("数据已是最新，无需同步")
        return {"synced": False, "message": "数据已是最新"}

    if verbose:
        print(f"开始同步区块 {actual_from_block} 到 {to_block}...")

    stats = {
        "wallet_created": 0,
        "transaction_executed": 0,
        "executed": 0,
        "eth_transferred": 0,
        "gas_received": 0,
    }

    # 批量获取事件 (每次 10000 个区块)
    batch_size = 10000
    current_block = actual_from_block

    while current_block <= to_block:
        end_block = min(current_block + batch_size - 1, to_block)

        if verbose:
            print(f"  处理区块 {current_block} - {end_block}...")

        # WalletCreated
        events = contract.events.WalletCreated().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_wallet_created(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "owner": event["args"]["owner"],
                "scw": event["args"]["scw"],
                "admin": event["args"]["admin"],
            })
            stats["wallet_created"] += 1

        # TransactionExecuted
        events = contract.events.TransactionExecuted().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_transaction_executed(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "owner": event["args"]["owner"],
                "scw": event["args"]["scw"],
                "admin": event["args"]["admin"],
                "created": event["args"]["created"],
            })
            stats["transaction_executed"] += 1

        # Executed (所有者执行)
        events = contract.events.Executed().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_executed(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "target": event["args"]["target"],
                "values": event["args"]["value"],
                "data": event["args"]["data"],
                "executor_type": "owner",
            })
            stats["executed"] += 1

        # ExecutedByAdmin
        events = contract.events.ExecutedByAdmin().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_executed(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "target": event["args"]["target"],
                "values": event["args"]["value"],
                "data": event["args"]["data"],
                "executor_type": "admin",
            })
            stats["executed"] += 1

        # ExecutedByEntry
        events = contract.events.ExecutedByEntry().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_executed(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "target": event["args"]["target"],
                "values": event["args"]["value"],
                "data": event["args"]["data"],
                "executor_type": "entry",
            })
            stats["executed"] += 1

        # EthTransfered
        events = contract.events.EthTransfered().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_eth_transferred(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "target": event["args"]["target"],
                "value": event["args"]["value"],
            })
            stats["eth_transferred"] += 1

        # GasReceived
        events = contract.events.GasReceived().get_logs(
            fromBlock=current_block, toBlock=end_block
        )
        for event in events:
            ts = datetime.fromtimestamp(event["blockData"]["timestamp"], tz=timezone.utc)
            insert_gas_received(conn, {
                "tx_hash": event["transactionHash"].hex(),
                "block_number": event["blockNumber"],
                "timestamp": ts,
                "from_addr": event["args"]["from"],
                "to_addr": event["args"]["to"],
                "token": event["args"]["token"],
                "amount": event["args"]["amount"],
            })
            stats["gas_received"] += 1

        commit(conn)
        update_sync_metadata(conn, end_block)
        current_block = end_block + 1

        # 避免 RPC 请求过快被限流
        time.sleep(0.1)

    conn.close()

    if verbose:
        print(f"同步完成!")
        print(f"  WalletCreated: {stats['wallet_created']}")
        print(f"  TransactionExecuted: {stats['transaction_executed']}")
        print(f"  Executed: {stats['executed']}")
        print(f"  EthTransfered: {stats['eth_transferred']}")
        print(f"  GasReceived: {stats['gas_received']}")

    stats["synced"] = True
    stats["from_block"] = actual_from_block
    stats["to_block"] = to_block

    return stats


def ensure_data_sync(w3: Optional[Web3] = None, verbose: bool = False) -> dict:
    """确保数据已同步，如果没有则执行同步"""
    return fetch_events_from_chain(w3=w3, verbose=verbose)


if __name__ == "__main__":
    print("开始同步链上数据...")
    result = ensure_data_sync(verbose=True)
    print(f"\n最终结果: {result}")
