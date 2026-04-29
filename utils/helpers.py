"""
通用工具函数
"""

import sqlite3
from datetime import datetime
from typing import Optional

import config
from data.cache import init_db


def shorten_address(address: str, chars: int = 6) -> str:
    """缩短地址显示"""
    if not address:
        return ""
    return f"{address[:chars]}...{address[-4:]}"


def format_bnb(value_wei: float) -> str:
    """格式化 BNB 金额"""
    bnb = value_wei / 1e18
    if bnb >= 1_000_000:
        return f"{bnb / 1_000_000:.2f}M"
    elif bnb >= 1_000:
        return f"{bnb / 1_000:.2f}K"
    else:
        return f"{bnb:.4f}"


def format_number(num: float) -> str:
    """格式化数字显示"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.0f}"


def get_token_name(address: Optional[str]) -> str:
    """获取代币名称"""
    if not address:
        return "Unknown"
    return config.KNOWN_TOKENS.get(address.lower(), shorten_address(address))


def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    return init_db()


def get_data_summary(conn: sqlite3.Connection) -> dict:
    """获取数据摘要信息"""
    summary = {}

    tables = {
        "wallet_created": "钱包创建",
        "transaction_executed": "交易执行",
        "executed": "批量调用",
        "eth_transferred": "ETH 转账",
        "gas_received": "Gas 代扣",
        "transfers": "代币转账",
    }

    for table, label in tables.items():
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        summary[label] = count

    # 获取最新数据时间
    latest_ts = conn.execute(
        "SELECT MAX(timestamp) FROM wallet_created"
    ).fetchone()[0]
    summary["latest_data_time"] = latest_ts

    return summary
