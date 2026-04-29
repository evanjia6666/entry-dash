"""
UxuySmartEntry 数据可视化看板 - Streamlit 主应用
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import config
from data.cache import init_db
from data.fetcher import ensure_data_sync
from analytics.user_metrics import (
    calc_daily_new_wallets,
    calc_cumulative_wallets,
    calc_active_wallets,
    calc_new_vs_active,
    calc_retention_rate,
    calc_first_tx_time_distribution,
)
from analytics.volume_metrics import (
    calc_daily_tx_count,
    calc_daily_volume,
    calc_avg_tx_amount,
    calc_daily_gas_cost,
    get_top_token_transfers,
)
from analytics.behavior_metrics import (
    calc_tx_frequency_distribution,
    calc_avg_tx_per_user,
    calc_executor_type_distribution,
    calc_hourly_distribution,
    calc_top_target_contracts,
    calc_top_active_wallets,
    calc_top_volume_wallets,
)
from charts.user_charts import (
    create_daily_new_wallets_chart,
    create_cumulative_wallets_chart,
    create_active_wallets_chart,
    create_new_vs_active_chart,
    create_retention_heatmap,
    create_first_tx_distribution,
)
from charts.volume_charts import (
    create_daily_tx_count_chart,
    create_daily_volume_chart,
    create_avg_tx_amount_chart,
    create_token_transfer_ranking,
    create_daily_gas_cost_chart,
)
from charts.behavior_charts import (
    create_tx_frequency_chart,
    create_avg_tx_per_user_chart,
    create_hourly_heatmap,
    create_executor_pie_chart,
    create_top_active_wallets_chart,
    create_top_volume_wallets_chart,
    create_target_contracts_chart,
)
from utils.helpers import get_db_connection, get_data_summary, format_number


# 页面配置
st.set_page_config(
    page_title="UxuySmartEntry 数据看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #fafafa;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #262730;
    }
    .chart-container {
        background-color: #0e1117;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #262730;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600)
def sync_data():
    """同步链上数据 (带缓存)"""
    return ensure_data_sync(verbose=False)


def show_sidebar():
    """侧边栏配置"""
    st.sidebar.title("⚙️ 配置")

    # 时间范围选择
    days = st.sidebar.selectbox(
        "📅 时间范围",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"最近 {x} 天",
    )

    # 数据同步按钮
    if st.sidebar.button("🔄 同步链上数据"):
        with st.spinner("正在同步链上数据..."):
            result = sync_data()
            if result.get("synced"):
                st.sidebar.success("✅ 数据同步完成")
                st.sidebar.json(result)
            else:
                st.sidebar.info(f"ℹ️ {result.get('message', '未知状态')}")

    # 数据摘要
    conn = get_db_connection()
    summary = get_data_summary(conn)
    conn.close()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 数据摘要")
    for label, count in summary.items():
        if label != "latest_data_time":
            st.sidebar.metric(label, format_number(count) if isinstance(count, (int, float)) else count)

    return days


def show_header():
    """显示页面头部"""
    st.markdown('<div class="main-header">📊 UxuySmartEntry 数据看板</div>', unsafe_allow_html=True)
    st.markdown("基于 BSC 链上合约事件的实时数据分析")
    st.markdown("---")


def render_user_growth_page(days: int):
    """用户增长页面"""
    st.header("📈 用户增长分析")

    conn = get_db_connection()

    col1, col2 = st.columns(2)

    with col1:
        daily_new = calc_daily_new_wallets(conn, days)
        if not daily_new.empty:
            st.plotly_chart(create_daily_new_wallets_chart(daily_new), use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        cumulative = calc_cumulative_wallets(conn, days)
        if not cumulative.empty:
            st.plotly_chart(create_cumulative_wallets_chart(cumulative), use_container_width=True)
        else:
            st.info("暂无数据")

    col1, col2 = st.columns(2)

    with col1:
        active = calc_active_wallets(conn, "daily", days)
        if not active.empty:
            st.plotly_chart(create_active_wallets_chart(active), use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        new_vs_active = calc_new_vs_active(conn, days)
        if not new_vs_active.empty:
            st.plotly_chart(create_new_vs_active_chart(new_vs_active), use_container_width=True)
        else:
            st.info("暂无数据")

    # 留存率
    st.subheader("📋 用户留存率")
    retention = calc_retention_rate(conn, retention_days=7, max_days=days)
    st.plotly_chart(create_retention_heatmap(retention), use_container_width=True)

    # 首次交易分布
    st.subheader("⏱️ 首次交易时间分布")
    first_tx = calc_first_tx_time_distribution(conn)
    st.plotly_chart(create_first_tx_distribution(first_tx), use_container_width=True)

    conn.close()


def render_volume_analysis_page(days: int):
    """交易量分析页面"""
    st.header("💰 交易量分析")

    conn = get_db_connection()

    col1, col2 = st.columns(2)

    with col1:
        daily_tx = calc_daily_tx_count(conn, days)
        if not daily_tx.empty:
            st.plotly_chart(create_daily_tx_count_chart(daily_tx), use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        daily_vol = calc_daily_volume(conn, days)
        if not daily_vol.empty:
            st.plotly_chart(create_daily_volume_chart(daily_vol), use_container_width=True)
        else:
            st.info("暂无数据")

    col1, col2 = st.columns(2)

    with col1:
        avg_amount = calc_avg_tx_amount(conn, days)
        if not avg_amount.empty:
            st.plotly_chart(create_avg_tx_amount_chart(avg_amount), use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        gas_cost = calc_daily_gas_cost(conn, days)
        if not gas_cost.empty:
            st.plotly_chart(create_daily_gas_cost_chart(gas_cost), use_container_width=True)
        else:
            st.info("暂无数据")

    # Top 代币转账
    st.subheader("🏷️ Top 20 代币转账排行")
    top_tokens = get_top_token_transfers(conn)
    st.plotly_chart(create_token_transfer_ranking(top_tokens), use_container_width=True)

    conn.close()


def render_behavior_analysis_page(days: int):
    """用户行为分析页面"""
    st.header("🎯 用户行为分析")

    conn = get_db_connection()

    col1, col2 = st.columns(2)

    with col1:
        freq_dist = calc_tx_frequency_distribution(conn)
        st.plotly_chart(create_tx_frequency_chart(freq_dist), use_container_width=True)

    with col2:
        avg_tx = calc_avg_tx_per_user(conn, days)
        st.plotly_chart(create_avg_tx_per_user_chart(avg_tx), use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        executor_dist = calc_executor_type_distribution(conn)
        st.plotly_chart(create_executor_pie_chart(executor_dist), use_container_width=True)

    with col2:
        hourly_dist = calc_hourly_distribution(conn)
        st.plotly_chart(create_hourly_heatmap(hourly_dist), use_container_width=True)

    # 排行
    st.subheader("🏆 排行榜")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Top 10 活跃钱包**")
        top_active = calc_top_active_wallets(conn)
        st.plotly_chart(create_top_active_wallets_chart(top_active), use_container_width=True)

    with col2:
        st.markdown("**Top 10 交易量钱包**")
        top_volume = calc_top_volume_wallets(conn)
        st.plotly_chart(create_top_volume_wallets_chart(top_volume), use_container_width=True)

    with col3:
        st.markdown("**Top 目标合约交互**")
        top_targets = calc_top_target_contracts(conn)
        st.plotly_chart(create_target_contracts_chart(top_targets), use_container_width=True)

    conn.close()


def render_platform_health_page():
    """平台健康度页面"""
    st.header("🏥 平台健康度")

    conn = get_db_connection()

    # 管理员 vs 用户操作占比
    st.subheader("🥧 管理员 vs 用户操作占比")
    from analytics.behavior_metrics import calc_executor_type_distribution

    executor_dist = calc_executor_type_distribution(conn)
    from charts.behavior_charts import create_executor_pie_chart

    st.plotly_chart(create_executor_pie_chart(executor_dist), use_container_width=True)

    # 配置变更历史 (需要从链上获取更多事件)
    st.subheader("📋 配置变更日志")
    st.info(
        "⚠️ 合约升级和管理员变更事件需要通过更复杂的链上查询获取，"
        "当前版本主要关注核心交易数据。"
    )

    # 数据摘要表格
    st.subheader("📊 数据摘要")
    summary = get_data_summary(conn)

    summary_df = pd.DataFrame(
        [{"指标": k, "数值": format_number(v) if isinstance(v, (int, float)) else v}
         for k, v in summary.items() if k != "latest_data_time"]
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    conn.close()


def main():
    """主函数"""
    # 侧边栏
    days = show_sidebar()

    # 头部
    show_header()

    # 页面导航
    page = st.selectbox(
        "📑 选择页面",
        [
            "📈 用户增长",
            "💰 交易量分析",
            "🎯 用户行为分析",
            "🏥 平台健康度",
        ],
    )

    # 根据选择渲染不同页面
    if "用户增长" in page:
        render_user_growth_page(days)
    elif "交易量" in page:
        render_volume_analysis_page(days)
    elif "用户行为" in page:
        render_behavior_analysis_page(days)
    else:
        render_platform_health_page()

    # 底部
    st.markdown("---")
    st.caption(
        f"数据源: BSC Chain | 合约: `{config.CONTRACT_ADDRESS}` | "
        f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
