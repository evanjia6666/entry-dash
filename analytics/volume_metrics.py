"""
交易量统计指标计算
"""

import sqlite3
from datetime import timedelta

import pandas as pd


def get_eth_transferred_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取所有 ETH 转账记录"""
    df = pd.read_sql_query(
        "SELECT * FROM eth_transferred ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )
    # 转换为 BNB 单位
    if not df.empty:
        df["value_bnb"] = pd.to_numeric(df["value"]) / 1e18
    return df


def get_executed_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取所有执行记录"""
    return pd.read_sql_query(
        "SELECT * FROM executed ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )


def get_gas_received_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取所有 Gas 代扣记录"""
    df = pd.read_sql_query(
        "SELECT * FROM gas_received ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )
    if not df.empty:
        df["amount_bnb"] = pd.to_numeric(df["amount"]) / 1e18
    return df


def calc_daily_tx_count(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算每日交易笔数"""
    df = get_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "tx_count"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date").size().reset_index(name="tx_count")
    daily.columns = ["date", "tx_count"]

    # 补全日期
    full_dates = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_dates, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()
    daily.columns = ["date", "tx_count"]

    return daily


def calc_daily_volume(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算每日交易量 (BNB)"""
    df = get_eth_transferred_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "volume_bnb"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date")["value_bnb"].sum().reset_index()
    daily.columns = ["date", "volume_bnb"]

    full_dates = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_dates, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()
    daily.columns = ["date", "volume_bnb"]

    return daily


def calc_avg_tx_amount(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算平均单笔交易金额 (BNB)"""
    df = get_eth_transferred_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "avg_amount_bnb"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date")["value_bnb"].mean().reset_index()
    daily.columns = ["date", "avg_amount_bnb"]

    return daily


def calc_daily_gas_cost(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算每日 Gas 代扣总额"""
    df = get_gas_received_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "gas_cost_bnb"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date")["amount_bnb"].sum().reset_index()
    daily.columns = ["date", "gas_cost_bnb"]

    full_dates = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_dates, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()
    daily.columns = ["date", "gas_cost_bnb"]

    return daily


def get_top_token_transfers(
    conn: sqlite3.Connection, limit: int = 20
) -> pd.DataFrame:
    """获取 Top 代币转账排行 (从 Transfer 事件)"""
    df = pd.read_sql_query(
        "SELECT token_address, COUNT(*) as count, SUM(CAST(value AS REAL)) as total_value "
        "FROM transfers GROUP BY token_address ORDER BY count DESC LIMIT ?",
        conn,
        params=(limit,),
    )
    return df
