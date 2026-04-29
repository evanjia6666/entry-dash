"""
用户增长与留存指标计算
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def get_wallet_created_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取所有钱包创建记录"""
    return pd.read_sql_query(
        "SELECT * FROM wallet_created ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )


def get_transaction_executed_df(conn: sqlite3.Connection) -> pd.DataFrame:
    """获取所有交易执行记录"""
    return pd.read_sql_query(
        "SELECT * FROM transaction_executed ORDER BY timestamp",
        conn,
        parse_dates=["timestamp"],
    )


def calc_daily_new_wallets(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算每日新增钱包数"""
    df = get_wallet_created_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "count"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date").size().reset_index(name="count")
    daily.columns = ["date", "count"]

    # 补全缺失日期
    full_dates = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_dates, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()
    daily.columns = ["date", "count"]

    return daily


def calc_cumulative_wallets(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算累计钱包用户数"""
    df = get_wallet_created_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "cumulative"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date").size().reset_index(name="count")
    daily.columns = ["date", "count"]

    full_dates = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_dates, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()
    daily.columns = ["date", "count"]

    daily["cumulative"] = daily["count"].cumsum()
    return daily[["date", "cumulative"]]


def calc_active_wallets(
    conn: sqlite3.Connection, window: str = "daily", days: int = 30
) -> pd.DataFrame:
    """
    计算活跃钱包数
    window: "daily" | "weekly" | "monthly"
    """
    df = get_transaction_executed_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["date", "active_wallets"])

    cutoff = df["timestamp"].max() - timedelta(days=days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["date"] = df["timestamp"].dt.date

    if window == "daily":
        active = df.groupby("date")["owner"].nunique().reset_index()
    elif window == "weekly":
        active = df.groupby("date")["owner"].nunique().reset_index()
        # 计算7日滚动活跃用户
        active["active_wallets"] = active["owner"].rolling(7, min_periods=1).sum()
    elif window == "monthly":
        active = df.groupby("date")["owner"].nunique().reset_index()
        active["active_wallets"] = active["owner"].rolling(30, min_periods=1).sum()
    else:
        active = df.groupby("date")["owner"].nunique().reset_index()

    active.columns = ["date", "active_wallets"]
    return active


def calc_new_vs_active(conn: sqlite3.Connection, days: int = 30) -> pd.DataFrame:
    """计算新增 vs 活跃钱包对比"""
    new_df = calc_daily_new_wallets(conn, days)
    active_df = calc_active_wallets(conn, "daily", days)

    merged = pd.merge(new_df, active_df, on="date", how="outer").fillna(0)
    return merged.sort_values("date")


def calc_retention_rate(
    conn: sqlite3.Connection, retention_days: int = 7, max_days: int = 60
) -> pd.DataFrame:
    """
    计算用户留存率
    返回每个注册日期的用户在 N 天后的留存比例
    """
    df = get_wallet_created_df(conn)
    if df.empty:
        return pd.DataFrame(columns=["cohort_date", "retention_day", "retention_rate"])

    tx_df = get_transaction_executed_df(conn)

    cohorts = []
    cutoff = df["timestamp"].max() - timedelta(days=max_days)
    df = df[df["timestamp"] >= cutoff].copy()
    df["cohort_date"] = df["timestamp"].dt.date

    for cohort_date, cohort_df in df.groupby("cohort_date"):
        cohort_owners = set(cohort_df["owner"].unique())
        if not cohort_owners:
            continue

        # 检查 N 天后是否有交易
        future_date = cohort_date + timedelta(days=retention_days)
        future_tx = tx_df[
            (tx_df["timestamp"].dt.date == future_date)
            & (tx_df["owner"].isin(cohort_owners))
        ]

        retained = future_tx["owner"].nunique()
        total = len(cohort_owners)

        cohorts.append({
            "cohort_date": cohort_date,
            "retention_day": retention_days,
            "retained_users": retained,
            "total_users": total,
            "retention_rate": retained / total if total > 0 else 0,
        })

    result = pd.DataFrame(cohorts)
    return result


def calc_first_tx_time_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """计算首次交易时间分布 (从创建钱包到首次交易的天数)"""
    wallet_df = get_wallet_created_df(conn)
    tx_df = get_transaction_executed_df(conn)

    if wallet_df.empty or tx_df.empty:
        return pd.DataFrame(columns=["owner", "days_to_first_tx"])

    # 每个用户的首次交易时间
    first_tx = tx_df.groupby("owner")["timestamp"].min().reset_index()
    first_tx.columns = ["owner", "first_tx_time"]

    # 钱包创建时间
    wallet_first = wallet_df.groupby("owner")["timestamp"].min().reset_index()
    wallet_first.columns = ["owner", "wallet_created_time"]

    # 合并计算时间差
    merged = pd.merge(wallet_first, first_tx, on="owner", how="inner")
    merged["days_to_first_tx"] = (
        (merged["first_tx_time"] - merged["wallet_created_time"]).dt.total_seconds() / 86400
    ).round(1)

    return merged[["owner", "days_to_first_tx"]]
