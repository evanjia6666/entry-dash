"""
数据模型定义 - 使用 dataclass 定义各类事件的数据结构
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WalletCreatedEvent:
    """钱包创建事件"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    owner: str
    scw: str
    admin: str


@dataclass
class TransactionExecutedEvent:
    """交易执行事件"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    owner: str
    scw: str
    admin: str
    created: bool


@dataclass
class ExecutedEvent:
    """执行批量调用事件 (基类)"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    target: str  # 目标合约地址
    values: list  # uint256[]
    data: list    # bytes[]
    executor_type: str  # "owner" | "admin" | "entry"


@dataclass
class EthTransferredEvent:
    """ETH 转账事件"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    target: str
    value: int  # wei


@dataclass
class GasReceivedEvent:
    """Gas 代扣事件"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    from_addr: str
    to_addr: str
    token: int
    amount: int  # wei


@dataclass
class TransferEvent:
    """ERC-20 Transfer 事件"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    from_addr: str
    to_addr: str
    value: int  # wei
    token_address: Optional[str] = None


@dataclass
class EventCache:
    """事件缓存汇总"""
    wallet_created: list[WalletCreatedEvent]
    transaction_executed: list[TransactionExecutedEvent]
    executed: list[ExecutedEvent]
    eth_transferred: list[EthTransferredEvent]
    gas_received: list[GasReceivedEvent]
    transfers: list[TransferEvent]
