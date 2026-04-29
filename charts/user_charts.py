"""
用户相关图表 - 使用 Plotly 绘制
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import config


def create_daily_new_wallets_chart(daily_df: pd.DataFrame) -> go.Figure:
    """
    图表1: 每日新增钱包数 (折线图 + 柱状图)
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=daily_df["date"],
        y=daily_df["count"],
        name="新增钱包数",
        marker_color="#636efa",
        opacity=0.7,
    ))

    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=daily_df["count"],
        name="趋势",
        line=dict(color="#00cc96", width=2),
        mode="lines",
    ))

    fig.update_layout(
        title="📈 每日新增钱包数",
        xaxis_title="日期",
        yaxis_title="钱包数量",
        template="plotly_dark",
        height=350,
        showlegend=True,
    )

    return fig


def create_cumulative_wallets_chart(cumulative_df: pd.DataFrame) -> go.Figure:
    """
    图表3: 累计钱包用户数 (面积图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=cumulative_df["date"],
        y=cumulative_df["cumulative"],
        fill="tozeroy",
        name="累计用户",
        line=dict(color="#ff7f0e", width=2),
        fillcolor="rgba(255, 127, 14, 0.3)",
    ))

    fig.update_layout(
        title="📊 累计钱包用户数",
        xaxis_title="日期",
        yaxis_title="累计用户数",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_active_wallets_chart(active_df: pd.DataFrame) -> go.Figure:
    """
    图表2: 活跃钱包数 (折线图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=active_df["date"],
        y=active_df["active_wallets"],
        mode="lines+markers",
        name="活跃钱包",
        line=dict(color="#2ca02c", width=2),
        marker=dict(size=4),
    ))

    fig.update_layout(
        title="🔄 活跃钱包数",
        xaxis_title="日期",
        yaxis_title="活跃钱包数",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_new_vs_active_chart(merged_df: pd.DataFrame) -> go.Figure:
    """
    图表4: 新增 vs 活跃钱包对比 (双轴图)
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=merged_df["date"],
            y=merged_df["count"],
            name="新增",
            marker_color="#636efa",
            opacity=0.7,
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=merged_df["date"],
            y=merged_df["active_wallets"],
            name="活跃",
            line=dict(color="#ff7f0e", width=2),
            mode="lines+markers",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="📊 新增 vs 活跃钱包对比",
        xaxis_title="日期",
        template="plotly_dark",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig.update_yaxes(title_text="新增数量", secondary_y=False)
    fig.update_yaxes(title_text="活跃数量", secondary_y=True)

    return fig


def create_retention_heatmap(retention_df: pd.DataFrame) -> go.Figure:
    """
    图表10: 用户留存率 (热力图)
    """
    if retention_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="📋 用户留存率 (暂无数据)",
            template="plotly_dark",
            height=400,
        )
        return fig

    # 构建透视表
    pivot = retention_df.pivot_table(
        values="retention_rate",
        index="cohort_date",
        columns="retention_day",
    )

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="YlGnBu",
        text=(pivot.values * 100).round(1),
        texttemplate="%{text}%",
        hovertemplate="留存率: %{text}%<extra></extra>",
    ))

    fig.update_layout(
        title="📋 用户留存率热力图",
        xaxis_title="留存天数",
        yaxis_title=" cohort 日期",
        template="plotly_dark",
        height=400,
    )

    return fig


def create_first_tx_distribution(first_tx_df: pd.DataFrame) -> go.Figure:
    """
    图表13: 首次交易时间分布 (柱状图)
    """
    if first_tx_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="⏱️ 首次交易时间分布 (暂无数据)",
            template="plotly_dark",
            height=350,
        )
        return fig

    # 分桶
    bins = [0, 1, 3, 7, 14, 30, 60, float("inf")]
    labels = ["当天", "1-3天", "3-7天", "7-14天", "14-30天", "30-60天", "60天+"]
    first_tx_df = first_tx_df.copy()
    first_tx_df["bucket"] = pd.cut(
        first_tx_df["days_to_first_tx"], bins=bins, labels=labels
    )

    bucket_counts = first_tx_df["bucket"].value_counts().sort_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=bucket_counts.index,
        y=bucket_counts.values,
        marker_color="#1f77b4",
        opacity=0.8,
    ))

    fig.update_layout(
        title="⏱️ 首次交易时间分布",
        xaxis_title="时间区间",
        yaxis_title="用户数",
        template="plotly_dark",
        height=350,
    )

    return fig
