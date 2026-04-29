"""
项目配置文件 - 合约地址、RPC、ABI 等配置
"""

# BSC 合约地址
CONTRACT_ADDRESS = "0x743CB7d6D8fBBF93806DeC9B7700743a2641dae2"

# BSC RPC 节点 (可替换为其他节点如 Ankr, QuickNode 等)
BSC_RPC_URL = "https://bsc-dataseed.binance.org"

# BSC Chain ID
BSC_CHAIN_ID = 56

# 合约 ABI (核心事件)
CONTRACT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "scw", "type": "address"},
            {"indexed": True, "name": "admin", "type": "address"},
        ],
        "name": "WalletCreated",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "scw", "type": "address"},
            {"indexed": True, "name": "admin", "type": "address"},
            {"indexed": False, "name": "created", "type": "bool"},
        ],
        "name": "TransactionExecuted",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "target", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256[]"},
            {"indexed": False, "name": "data", "type": "bytes[]"},
        ],
        "name": "Executed",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "target", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256[]"},
            {"indexed": False, "name": "data", "type": "bytes[]"},
        ],
        "name": "ExecutedByAdmin",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "target", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256[]"},
            {"indexed": False, "name": "data", "type": "bytes[]"},
        ],
        "name": "ExecutedByEntry",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "target", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "EthTransfered",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "token", "type": "uint256"},
            {"indexed": False, "name": "amount", "type": "uint256"},
        ],
        "name": "GasReceived",
        "type": "event",
    },
    # ERC-20 标准 Transfer 事件 (需要从代币合约获取)
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
]

# 缓存配置
CACHE_DIR = ".cache"
CACHE_DB_PATH = f"{CACHE_DIR}/events.db"

# 图表默认时间范围 (天)
DEFAULT_DAYS = 30

# BSC 区块时间 (秒)
BLOCK_TIME_SECONDS = 3

# 已知代币地址映射 (可后续扩展)
KNOWN_TOKENS = {
    "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c": "WBNB",
    "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": "BUSD",
    "0x55d398326f99059fF775485246999027B3197955": "USDT",
    "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d": "USDC",
}

# 图表主题
CHART_THEME = {
    "background_color": "#0e1117",
    "paper_bgcolor": "#0e1117",
    "plot_bgcolor": "#0e1117",
    "font_color": "#fafafa",
    "grid_color": "#262730",
    "line_color": "#636efa",
}
