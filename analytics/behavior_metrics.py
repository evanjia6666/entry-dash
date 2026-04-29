"""
用户行为分析指标计算
"""

import sqlite3
from datetime import timedelta

import pandas as pd


def get_transaction_executed_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取交易执行记录"""
    return pd.read_sql_query(
        "SELECT * FROM transaction_executed ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )


def get_executed_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取执行记录"""
    return pd.read_sql_query(
        "SELECT * FROM executed ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )


def calc_tx_frequency_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    计算交易频率分布 (用户分桶)
    返回每个用户总交易次数分布
    """
    df = get_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["owner", "tx_count"])

    # 每个用户的交易次数
    owner_counts = df.groupby("target").size().reset_index(name="tx_count")
    # 注意: executed 表没有 owner 字段，用 target 代替分析

    # 从 transaction_executed 获取 owner 维度
    tx_df = get_transaction_executed_df(conn)
    if not tx_df.empty:
        owner_counts = tx_df.groupby("owner").size().reset_index(name="tx_count")

    # 分桶
    if not owner_counts.empty:
        bins = [0, 1, 5, 10, 50, 100, 500, 1000, float("inf")]
        labels = ["1", "2-5", "6-10", "11-50", "51-100", "101-500", "501-1000", "1000+"]
        owner_counts["bucket"] = pd.cut(
            owner_counts["tx_count"], bins=bins, labels=labels
        )

        bucket_counts = owner_counts.groupby("bucket", observed=False).size().reset_index(
            name="user_count"
        )
        return bucket_counts

    return pd.DataFrame(columns=["bucket", "user_count"])


def calc_avg_tx_per_user(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算每用户平均交易次数 (按日)"""
    df = get_transaction_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "avg_tx_per_user"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily_users = df.groupby("date")["owner"].nunique().reset_index()
    daily_users.columns = ["date", "unique_users"]

    daily_tx = df.groupby("date").size().reset_index(name="tx_count")
    daily_tx.columns = ["date", "tx_count"]

    merged = pd.merge(daily_users, daily_tx, on="date")
    merged["avg_tx_per_user"] = (merged["tx_count"] / merged["unique_users"]).round(2)

    return merged[["date", "avg_tx_per_user"]]


def calc_executor_type_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """计算管理员 vs 用户操作占比"""
    df = get_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["executor_type", "count"])

    dist = df.groupby("executor_type").size().reset_index(name="count")
    return dist


def calc_hourly_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """计算交易时段分布 (小时级)"""
    df = get_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["hour", "tx_count"])

    df["hour"] = df["timestamp"].dt.hour

    hourly = df.groupby("hour").size().reset_index(name="tx_count")
    return hourly


def calc_top_target_contracts(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    """计算目标合约交互排行"""
    df = get_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["target", "count"])

    top = df.groupby("target").size().reset_index(name="count")
    top = top.sort_values("count", ascending=False).head(limit)
    return top


def calc_top_active_wallets(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    """计算 Top 活跃钱包排行 (按交易次数)"""
    df = get_transaction_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["owner", "tx_count"])

    top = df.groupby("owner").size().reset_index(name="tx_count")
    top = top.sort_values("tx_count", ascending=False).head(limit)
    return top


def calc_top_volume_wallets(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    """计算 Top 交易量钱包排行"""
    eth_df = pd.read_sql_query(
        "SELECT target, SUM(CAST(value AS REAL)) as total_value "
        "FROM eth_transferred GROUP BY target ORDER BY total_value DESC LIMIT ?",
        conn,
        params=(limit,),
    )
    return eth_df
