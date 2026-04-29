"""
行为分析图表 - 使用 Plotly 绘制
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_tx_frequency_chart(freq_df: pd.DataFrame) -> go.Figure:
    """
    图表11: 交易频率分布 (直方图)
    """
    if freq_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="📊 交易频率分布 (暂无数据)",
            template="plotly_dark",
            height=350,
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=freq_df["bucket"],
        y=freq_df["user_count"],
        marker_color="#2ca02c",
        opacity=0.8,
    ))

    fig.update_layout(
        title="📊 交易频率分布",
        xaxis_title="交易次数区间",
        yaxis_title="用户数",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_avg_tx_per_user_chart(avg_df: pd.DataFrame) -> go.Figure:
    """
    图表12: 每用户平均交易次数 (折线图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=avg_df["date"],
        y=avg_df["avg_tx_per_user"],
        mode="lines+markers",
        name="平均交易次数/用户",
        line=dict(color="#9467bd", width=2),
        marker=dict(size=4),
    ))

    fig.update_layout(
        title="👤 每用户平均交易次数",
        xaxis_title="日期",
        yaxis_title="平均交易次数",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_hourly_heatmap(hourly_df: pd.DataFrame) -> go.Figure:
    """
    图表16: 交易时段分布 (小时级) (热力图/柱状图)
    """
    if hourly_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="🕐 交易时段分布 (暂无数据)",
            template="plotly_dark",
            height=350,
        )
        return fig

    fig = go.Figure()

    # 使用柱状图展示 24 小时分布
    fig.add_trace(go.Bar(
        x=hourly_df["hour"],
        y=hourly_df["tx_count"],
        marker_color=hourly_df["tx_count"],
        colorscale="YlOrRd",
        opacity=0.8,
    ))

    fig.update_layout(
        title="🕐 交易时段分布 (小时级)",
        xaxis_title="小时 (UTC)",
        yaxis_title="交易数量",
        template="plotly_dark",
        height=350,
        xaxis=dict(tickmode="linear", tick0=0, dtick=2),
    )

    return fig


def create_executor_pie_chart(dist_df: pd.DataFrame) -> go.Figure:
    """
    图表18: 管理员 vs 用户操作占比 (饼图)
    """
    if dist_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="🥧 操作类型占比 (暂无数据)",
            template="plotly_dark",
            height=350,
        )
        return fig

    labels_map = {
        "owner": "用户自操作",
        "admin": "管理员代操作",
        "entry": "入口合约代理",
    }

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=[labels_map.get(t, t) for t in dist_df["executor_type"]],
        values=dist_df["count"],
        hole=0.3,
        marker=dict(colors=["#636efa", "#ff7f0e", "#2ca02c"]),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} 笔<br>占比: %{percent}<extra></extra>",
    ))

    fig.update_layout(
        title="🥧 管理员 vs 用户操作占比",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_top_active_wallets_chart(top_df: pd.DataFrame) -> go.Figure:
    """
    图表14: Top 10 活跃钱包排行 (条形图)
    """
    if top_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="🏆 Top 活跃钱包 (暂无数据)",
            template="plotly_dark",
            height=400,
        )
        return fig

    # 简化地址显示
    top_df = top_df.copy()
    top_df["short_addr"] = top_df["owner"].apply(
        lambda x: f"{x[:6]}...{x[-4:]}"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_df["short_addr"],
        x=top_df["tx_count"],
        orientation="h",
        marker_color="#1f77b4",
        opacity=0.8,
    ))

    fig.update_layout(
        title="🏆 Top 10 活跃钱包排行",
        xaxis_title="交易次数",
        yaxis_title="钱包地址",
        template="plotly_dark",
        height=400,
        yaxis=dict(autorange="reversed"),
    )

    return fig


def create_top_volume_wallets_chart(top_df: pd.DataFrame) -> go.Figure:
    """
    图表15: Top 10 交易量钱包排行 (条形图)
    """
    if top_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="💰 Top 交易量钱包 (暂无数据)",
            template="plotly_dark",
            height=400,
        )
        return fig

    top_df = top_df.copy()
    top_df["short_addr"] = top_df["target"].apply(
        lambda x: f"{x[:6]}...{x[-4:]}"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_df["short_addr"],
        x=top_df["total_value"],
        orientation="h",
        marker_color="#ff7f0e",
        opacity=0.8,
    ))

    fig.update_layout(
        title="💰 Top 10 交易量钱包排行",
        xaxis_title="交易量 (BNB)",
        yaxis_title="钱包地址",
        template="plotly_dark",
        height=400,
        yaxis=dict(autorange="reversed"),
    )

    return fig


def create_target_contracts_chart(target_df: pd.DataFrame) -> go.Figure:
    """
    图表17: 目标合约交互排行 (饼图/条形图)
    """
    if target_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="🎯 目标合约交互排行 (暂无数据)",
            template="plotly_dark",
            height=400,
        )
        return fig

    target_df = target_df.copy()
    target_df["short_addr"] = target_df["target"].apply(
        lambda x: f"{x[:6]}...{x[-4:]}"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=target_df["short_addr"],
        x=target_df["count"],
        orientation="h",
        marker_color="#2ca02c",
        opacity=0.8,
    ))

    fig.update_layout(
        title="🎯 Top 目标合约交互排行",
        xaxis_title="交互次数",
        yaxis_title="合约地址",
        template="plotly_dark",
        height=400,
        yaxis=dict(autorange="reversed"),
    )

    return fig
