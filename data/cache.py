"""
数据缓存管理 - SQLite 本地存储
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional

import config


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """初始化数据库并创建表"""
    if db_path is None:
        db_path = config.CACHE_DB_PATH

    # 确保缓存目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # 创建事件表
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS wallet_created (
            tx_hash TEXT PRIMARY KEY,
            block_number INTEGER,
            timestamp TEXT,
            owner TEXT,
            scw TEXT,
            admin TEXT
        );

        CREATE TABLE IF NOT EXISTS transaction_executed (
            tx_hash TEXT PRIMARY KEY,
            block_number INTEGER,
            timestamp TEXT,
            owner TEXT,
            scw TEXT,
            admin TEXT,
            created BOOLEAN
        );

        CREATE TABLE IF NOT EXISTS executed (
            tx_hash TEXT,
            block_number INTEGER,
            timestamp TEXT,
            target TEXT,
            values TEXT,  -- JSON array
            data TEXT,    -- JSON array
            executor_type TEXT,
            PRIMARY KEY (tx_hash, target)
        );

        CREATE TABLE IF NOT EXISTS eth_transferred (
            tx_hash TEXT,
            block_number INTEGER,
            timestamp TEXT,
            target TEXT,
            value TEXT,
            PRIMARY KEY (tx_hash, target)
        );

        CREATE TABLE IF NOT EXISTS gas_received (
            tx_hash TEXT PRIMARY KEY,
            block_number INTEGER,
            timestamp TEXT,
            from_addr TEXT,
            to_addr TEXT,
            token TEXT,
            amount TEXT
        );

        CREATE TABLE IF NOT EXISTS transfers (
            tx_hash TEXT,
            block_number INTEGER,
            timestamp TEXT,
            from_addr TEXT,
            to_addr TEXT,
            value TEXT,
            token_address TEXT
        );

        CREATE TABLE IF NOT EXISTS sync_metadata (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_synced_block INTEGER,
            last_sync_time TEXT
        );
    """)

    # 初始化同步元数据
    conn.execute(
        "INSERT OR IGNORE INTO sync_metadata (id, last_synced_block, last_sync_time) VALUES (1, 0, NULL)"
    )
    conn.commit()

    return conn


def get_last_synced_block(conn: sqlite3.Connection) -> int:
    """获取上次同步的区块号"""
    row = conn.execute("SELECT last_synced_block FROM sync_metadata WHERE id = 1").fetchone()
    return row["last_synced_block"] if row else 0


def update_sync_metadata(conn: sqlite3.Connection, block_number: int):
    """更新同步元数据"""
    conn.execute(
        "UPDATE sync_metadata SET last_synced_block = ?, last_sync_time = ? WHERE id = 1",
        (block_number, datetime.utcnow().isoformat())
    )
    conn.commit()


def insert_wallet_created(conn: sqlite3.Connection, event: dict):
    """插入钱包创建事件"""
    conn.execute(
        """INSERT OR IGNORE INTO wallet_created 
           (tx_hash, block_number, timestamp, owner, scw, admin)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["owner"].lower(),
            event["scw"].lower(),
            event["admin"].lower(),
        )
    )


def insert_transaction_executed(conn: sqlite3.Connection, event: dict):
    """插入交易执行事件"""
    conn.execute(
        """INSERT OR IGNORE INTO transaction_executed 
           (tx_hash, block_number, timestamp, owner, scw, admin, created)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["owner"].lower(),
            event["scw"].lower(),
            event["admin"].lower(),
            event["created"],
        )
    )


def insert_executed(conn: sqlite3.Connection, event: dict):
    """插入批量执行事件"""
    conn.execute(
        """INSERT OR IGNORE INTO executed 
           (tx_hash, block_number, timestamp, target, values, data, executor_type)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["target"].lower(),
            str(event["values"]),
            str(event["data"]),
            event["executor_type"],
        )
    )


def insert_eth_transferred(conn: sqlite3.Connection, event: dict):
    """插入 ETH 转账事件"""
    conn.execute(
        """INSERT OR IGNORE INTO eth_transferred 
           (tx_hash, block_number, timestamp, target, value)
           VALUES (?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["target"].lower(),
            str(event["value"]),
        )
    )


def insert_gas_received(conn: sqlite3.Connection, event: dict):
    """插入 Gas 代扣事件"""
    conn.execute(
        """INSERT OR IGNORE INTO gas_received 
           (tx_hash, block_number, timestamp, from_addr, to_addr, token, amount)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["from_addr"].lower(),
            event["to_addr"].lower(),
            str(event["token"]),
            str(event["amount"]),
        )
    )


def insert_transfer(conn: sqlite3.Connection, event: dict):
    """插入 Transfer 事件"""
    conn.execute(
        """INSERT OR IGNORE INTO transfers 
           (tx_hash, block_number, timestamp, from_addr, to_addr, value, token_address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event["tx_hash"],
            event["block_number"],
            event["timestamp"].isoformat(),
            event["from_addr"].lower(),
            event["to_addr"].lower(),
            str(event["value"]),
            event.get("token_address"),
        )
    )


def commit(conn: sqlite3.Connection):
    """提交事务"""
    conn.commit()
