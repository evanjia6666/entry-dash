# UxuySmartEntry 数据可视化看板

基于 BSC 链上 `UxuySmartEntry` 合约事件的交互式数据可视化看板。

## 📊 功能特性

- **用户增长分析** — 新增钱包数、活跃用户数、累计用户曲线
- **交易量统计** — 每日交易笔数、交易量 (BNB)、平均交易金额
- **用户行为分析** — 留存率、交易频率、首次激活时间
- **排行与分布** — 活跃钱包排行、目标合约交互排行、时段分布
- **平台健康度** — 管理员操作占比、配置变更日志

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 (可选)

复制 `.env.example` 并填写自定义配置：

```bash
cp .env.example .env
```

默认使用公共 BSC RPC 节点，如需加速可配置自己的节点。

### 3. 运行应用

```bash
streamlit run app.py
```

首次运行会自动从链上拉取数据并缓存到本地 SQLite。

## 📁 项目结构

```
entry-dash/
├── app.py                 # Streamlit 主应用
├── config.py              # 合约地址、RPC、ABI 配置
├── data/
│   ├── fetcher.py         # 链上事件抓取器
│   ├── models.py          # 数据模型定义
│   └── cache.py           # 数据缓存管理
├── analytics/
│   ├── user_metrics.py    # 用户增长/留存计算
│   ├── volume_metrics.py  # 交易量统计
│   ├── behavior_metrics.py # 用户行为分析
│   └── ranking_metrics.py # 排行统计
├── charts/
│   ├── user_charts.py     # 用户相关图表
│   ├── volume_charts.py   # 交易量图表
│   ├── behavior_charts.py # 行为分析图表
│   └── ranking_charts.py # 排行图表
├── utils/
│   └── helpers.py         # 通用工具函数
├── requirements.txt       # 依赖
└── README.md
```

## 🔧 技术栈

- **Streamlit** — 快速构建数据看板
- **Plotly** — 交互式图表
- **web3.py** — 链上事件读取
- **Pandas** — 数据处理
- **SQLite** — 本地数据缓存

## 📈 20 个核心图表

1. 每日/周/月新增钱包数
2. 活跃钱包数 (DAU/WAU/MAU)
3. 累计钱包用户数
4. 新增 vs 活跃对比
5. 每日交易笔数
6. 每日交易量 (BNB)
7. 平均单笔交易金额
8. Top 20 代币转账排行
9. 每日 Gas 代扣总额
10. 用户留存率 (7日/30日)
11. 交易频率分布
12. 每用户平均交易次数
13. 首次交易时间分布
14. Top 10 活跃钱包排行
15. Top 10 交易量钱包排行
16. 交易时段分布 (小时级)
17. 目标合约交互排行
18. 管理员 vs 用户操作占比
19. 管理员变更历史
20. 合约升级/配置变更日志
