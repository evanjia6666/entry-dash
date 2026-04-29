"""
交易量图表 - 使用 Plotly 绘制
"""

import plotly.graph_objects as go
import pandas as pd


def create_daily_tx_count_chart(daily_df: pd.DataFrame) -> go.Figure:
    """
    图表5: 每日交易笔数 (柱状图)
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=daily_df["date"],
        y=daily_df["tx_count"],
        name="交易笔数",
        marker_color="#636efa",
        opacity=0.8,
    ))

    fig.update_layout(
        title="💰 每日交易笔数",
        xaxis_title="日期",
        yaxis_title="交易数量",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_daily_volume_chart(volume_df: pd.DataFrame) -> go.Figure:
    """
    图表6: 每日交易量 (BNB) (面积图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=volume_df["date"],
        y=volume_df["volume_bnb"],
        fill="tozeroy",
        name="交易量 (BNB)",
        line=dict(color="#00cc96", width=2),
        fillcolor="rgba(0, 204, 150, 0.3)",
        mode="lines",
    ))

    fig.update_layout(
        title="💎 每日交易量 (BNB)",
        xaxis_title="日期",
        yaxis_title="交易量 (BNB)",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_avg_tx_amount_chart(avg_df: pd.DataFrame) -> go.Figure:
    """
    图表7: 平均单笔交易金额 (折线图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=avg_df["date"],
        y=avg_df["avg_amount_bnb"],
        mode="lines+markers",
        name="平均交易金额",
        line=dict(color="#ff7f0e", width=2),
        marker=dict(size=4),
    ))

    fig.update_layout(
        title="📏 平均单笔交易金额 (BNB)",
        xaxis_title="日期",
        yaxis_title="平均金额 (BNB)",
        template="plotly_dark",
        height=350,
    )

    return fig


def create_token_transfer_ranking(top_df: pd.DataFrame) -> go.Figure:
    """
    图表8: Top 20 代币转账排行 (横向柱状图)
    """
    if top_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="🏷️ Top 代币转账 (暂无数据)",
            template="plotly_dark",
            height=400,
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_df["token_address"],
        x=top_df["count"],
        orientation="h",
        marker_color="#1f77b4",
        opacity=0.8,
    ))

    fig.update_layout(
        title="🏷️ Top 20 代币转账排行",
        xaxis_title="转账次数",
        yaxis_title="代币地址",
        template="plotly_dark",
        height=400,
        yaxis=dict(autorange="reversed"),
    )

    return fig


def create_daily_gas_cost_chart(gas_df: pd.DataFrame) -> go.Figure:
    """
    图表9: 每日 Gas 代扣总额 (折线图)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=gas_df["date"],
        y=gas_df["gas_cost_bnb"],
        mode="lines+markers",
        name="Gas 代扣",
        line=dict(color="#d62728", width=2),
        marker=dict(size=4),
    ))

    fig.update_layout(
        title="⛽ 每日 Gas 代扣总额 (BNB)",
        xaxis_title="日期",
        yaxis_title="Gas 总额 (BNB)",
        template="plotly_dark",
        height=350,
    )

    return fig
