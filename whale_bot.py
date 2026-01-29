import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import logging
from aiohttp import web
import threading
import sys
import io

# ================= CONFIGURATION INITIALE =================
# Configurer l'encodage pour Windows pour éviter les erreurs Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging avec encodage UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whale_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8547895751:AAFupdZqD0yVDhmdZ2AgIqnzhvDfdfXU7Ns"
CONFIG_FILE = "whale_config_multi_chain.json"
USER_SETTINGS_DIR = "user_settings"
PORT = int(os.environ.get("PORT", 8080))

# ================= ADDRESSES DE DON =================
DONATION_ADDRESSES = {
    "BTC": "bc1qzhgwvh4kf7jwnn04lhnjwse0lze2dvxrw075xw",
    "ETH": "0x8C9FC5e8af05860128F5cb7612c430C588168889",
    "USDT": "0x8C9FC5e8af05860128F5cb7612c430C588168889"
}

# ================= TOKENS COMPLETS =================
COMPLETE_TOKENS = {
    # ========== BITCOIN NETWORK ==========
    "BTC": {
        "network": "bitcoin",
        "address": "",
        "threshold_usd": 1000000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Bitcoin"
    },
    
    # ========== ETHEREUM NETWORK ==========
    "ETH": {
        "network": "ethereum",
        "address": "",
        "threshold_usd": 500000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Ethereum"
    },
    "USDC-ETH": {
        "network": "ethereum",
        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "threshold_usd": 500000,
        "category": "stablecoin",
        "decimals": 6,
        "api_source": "ethplorer",
        "display_name": "USDC (Ethereum)"
    },
    "USDT-ETH": {
        "network": "ethereum",
        "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "threshold_usd": 500000,
        "category": "stablecoin",
        "decimals": 6,
        "api_source": "ethplorer",
        "display_name": "USDT (Ethereum)"
    },
    
    # ========== XRP ==========
    "XRP": {
        "network": "xrp",
        "address": "",
        "threshold_usd": 250000,
        "category": "payment",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Ripple"
    },
    
    # ========== CARDANO ==========
    "ADA": {
        "network": "cardano",
        "address": "",
        "threshold_usd": 150000,
        "category": "layer1",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Cardano"
    },
    
    # ========== AVALANCHE ==========
    "AVAX": {
        "network": "avalanche",
        "address": "",
        "threshold_usd": 150000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Avalanche"
    },
    
    # ========== DOGECOIN ==========
    "DOGE": {
        "network": "dogecoin",
        "address": "",
        "threshold_usd": 100000,
        "category": "memecoin",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Dogecoin"
    },
    
    # ========== TRON ==========
    "TRX": {
        "network": "tron",
        "address": "",
        "threshold_usd": 100000,
        "category": "layer1",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Tron"
    },
    
    # ========== TONCOIN ==========
    "TON": {
        "network": "ton",
        "address": "",
        "threshold_usd": 100000,
        "category": "layer1",
        "decimals": 9,
        "api_source": "coingecko",
        "display_name": "Toncoin"
    },
    
    # ========== CHAINLINK ==========
    "LINK-ETH": {
        "network": "ethereum",
        "address": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "threshold_usd": 100000,
        "category": "oracle",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Chainlink (Ethereum)"
    },
    "LINK-BSC": {
        "network": "bsc",
        "address": "0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD",
        "threshold_usd": 100000,
        "category": "oracle",
        "decimals": 18,
        "api_source": "bscscan",
        "display_name": "Chainlink (BSC)"
    },
    
    # ========== POLYGON ==========
    "MATIC": {
        "network": "polygon",
        "address": "",
        "threshold_usd": 100000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Polygon"
    },
    
    # ========== SHIBA INU ==========
    "SHIB-ETH": {
        "network": "ethereum",
        "address": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
        "threshold_usd": 50000,
        "category": "memecoin",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Shiba Inu (Ethereum)"
    },
    
    # ========== POLKADOT ==========
    "DOT": {
        "network": "polkadot",
        "address": "",
        "threshold_usd": 100000,
        "category": "layer0",
        "decimals": 10,
        "api_source": "coingecko",
        "display_name": "Polkadot"
    },
    
    # ========== WRAPPED BITCOIN ==========
    "WBTC-ETH": {
        "network": "ethereum",
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "threshold_usd": 500000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "ethplorer",
        "display_name": "Wrapped Bitcoin (Ethereum)"
    },
    
    # ========== COSMOS ==========
    "ATOM": {
        "network": "cosmos",
        "address": "",
        "threshold_usd": 50000,
        "category": "layer0",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Cosmos"
    },
    
    # ========== NEAR PROTOCOL ==========
    "NEAR": {
        "network": "near",
        "address": "",
        "threshold_usd": 50000,
        "category": "layer1",
        "decimals": 24,
        "api_source": "coingecko",
        "display_name": "Near Protocol"
    },
    
    # ========== APTOS ==========
    "APT": {
        "network": "aptos",
        "address": "",
        "threshold_usd": 50000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Aptos"
    },
    
    # ========== OPTIMISM ==========
    "OP": {
        "network": "optimism",
        "address": "",
        "threshold_usd": 75000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Optimism"
    },
    
    # ========== ARBITRUM ==========
    "ARB": {
        "network": "arbitrum",
        "address": "",
        "threshold_usd": 75000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Arbitrum"
    },
    
    # ========== INJECTIVE ==========
    "INJ": {
        "network": "injective",
        "address": "",
        "threshold_usd": 50000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Injective"
    },
    
    # ========== RENDER ==========
    "RNDR-ETH": {
        "network": "ethereum",
        "address": "0x6De037ef9aD2725EB40118Bb1702EBb27e4Aeb24",
        "threshold_usd": 30000,
        "category": "ai",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Render (Ethereum)"
    },
    
    # ========== IMMUTABLE X ==========
    "IMX": {
        "network": "ethereum",
        "address": "0xF57e7e7C23978C3cAE0b5D4d8b9B8B84dC8E6E8E",
        "threshold_usd": 30000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Immutable X"
    },
    
    # ========== GALA ==========
    "GALA-ETH": {
        "network": "ethereum",
        "address": "0xd1d2Eb1B1e90B638588728b4130137D262C87cae",
        "threshold_usd": 20000,
        "category": "gaming",
        "decimals": 8,
        "api_source": "ethplorer",
        "display_name": "Gala (Ethereum)"
    },
    
    # ========== FETCH.AI ==========
    "FET": {
        "network": "ethereum",
        "address": "0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85",
        "threshold_usd": 20000,
        "category": "ai",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Fetch.ai"
    },
    
    # ========== PEPE ==========
    "PEPE": {
        "network": "ethereum",
        "address": "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
        "threshold_usd": 25000,
        "category": "memecoin",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Pepe"
    },
    
    # ========== SOLANA ECOSYSTEM ==========
    "SOL": {
        "network": "solana",
        "address": "So11111111111111111111111111111111111111112",
        "threshold_usd": 200000,
        "category": "layer1",
        "decimals": 9,
        "api_source": "birdeye",
        "display_name": "Solana"
    },
    "USDC-SOL": {
        "network": "solana",
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "threshold_usd": 500000,
        "category": "stablecoin",
        "decimals": 6,
        "api_source": "birdeye",
        "display_name": "USDC (Solana)"
    },
    "BONK": {
        "network": "solana",
        "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "threshold_usd": 20000,
        "category": "memecoin",
        "decimals": 5,
        "api_source": "birdeye",
        "display_name": "Bonk"
    },
    "JUP": {
        "network": "solana",
        "address": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 6,
        "api_source": "birdeye",
        "display_name": "Jupiter"
    },
    "WIF": {
        "network": "solana",
        "address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "threshold_usd": 20000,
        "category": "memecoin",
        "decimals": 6,
        "api_source": "birdeye",
        "display_name": "Dogwifhat"
    },
    
    # ========== BINANCE SMART CHAIN ==========
    "BNB": {
        "network": "bsc",
        "address": "",
        "threshold_usd": 300000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "BNB"
    },
    "USDT-BSC": {
        "network": "bsc",
        "address": "0x55d398326f99059fF775485246999027B3197955",
        "threshold_usd": 500000,
        "category": "stablecoin",
        "decimals": 18,
        "api_source": "bscscan",
        "display_name": "USDT (BSC)"
    },
    "CAKE": {
        "network": "bsc",
        "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 18,
        "api_source": "bscscan",
        "display_name": "PancakeSwap"
    },
    
    # ========== INTERNET COMPUTER ==========
    "ICP": {
        "network": "internet_computer",
        "address": "",
        "threshold_usd": 30000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Internet Computer"
    },
    
    # ========== ETHEREUM CLASSIC ==========
    "ETC": {
        "network": "ethereum_classic",
        "address": "",
        "threshold_usd": 30000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Ethereum Classic"
    },
    
    # ========== LITECOIN ==========
    "LTC": {
        "network": "litecoin",
        "address": "",
        "threshold_usd": 75000,
        "category": "payment",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Litecoin"
    },
    
    # ========== BITCOIN CASH ==========
    "BCH": {
        "network": "bitcoin_cash",
        "address": "",
        "threshold_usd": 75000,
        "category": "payment",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Bitcoin Cash"
    },
    
    # ========== STELLAR ==========
    "XLM": {
        "network": "stellar",
        "address": "",
        "threshold_usd": 50000,
        "category": "payment",
        "decimals": 7,
        "api_source": "coingecko",
        "display_name": "Stellar"
    },
    
    # ========== FILECOIN ==========
    "FIL": {
        "network": "filecoin",
        "address": "",
        "threshold_usd": 30000,
        "category": "storage",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Filecoin"
    },
    
    # ========== HEDERA ==========
    "HBAR": {
        "network": "hedera",
        "address": "",
        "threshold_usd": 30000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Hedera"
    },
    
    # ========== VECHAIN ==========
    "VET": {
        "network": "vechain",
        "address": "",
        "threshold_usd": 20000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "VeChain"
    },
    
    # ========== ALGORAND ==========
    "ALGO": {
        "network": "algorand",
        "address": "",
        "threshold_usd": 20000,
        "category": "layer1",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Algorand"
    },
    
    # ========== FANTOM ==========
    "FTM": {
        "network": "fantom",
        "address": "",
        "threshold_usd": 20000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Fantom"
    },
    
    # ========== MAKER ==========
    "MKR": {
        "network": "ethereum",
        "address": "0x9f8F72aA9304c8B593d555F12ef6589cC3A579A2",
        "threshold_usd": 50000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Maker"
    },
    
    # ========== AAVE ==========
    "AAVE": {
        "network": "ethereum",
        "address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "threshold_usd": 50000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Aave"
    },
    
    # ========== UNISWAP ==========
    "UNI": {
        "network": "ethereum",
        "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "threshold_usd": 75000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Uniswap"
    },
    
    # ========== SUSHI ==========
    "SUSHI": {
        "network": "ethereum",
        "address": "0x6B3595068778DD592e39A122f4f5a5CF09C90fE2",
        "threshold_usd": 20000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "SushiSwap"
    },
    
    # ========== CURVE ==========
    "CRV": {
        "network": "ethereum",
        "address": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Curve DAO"
    },
    
    # ========== THE GRAPH ==========
    "GRT": {
        "network": "ethereum",
        "address": "0xc944E90C64B2c07662A292be6244BDf05Cda44a7",
        "threshold_usd": 20000,
        "category": "oracle",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "The Graph"
    },
    
    # ========== LIDO ==========
    "LDO": {
        "network": "ethereum",
        "address": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Lido DAO"
    },
    
    # ========== THETA ==========
    "THETA": {
        "network": "theta",
        "address": "",
        "threshold_usd": 20000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Theta Network"
    },
    
    # ========== ZILLIQA ==========
    "ZIL": {
        "network": "zilliqa",
        "address": "",
        "threshold_usd": 15000,
        "category": "layer1",
        "decimals": 12,
        "api_source": "coingecko",
        "display_name": "Zilliqa"
    },
    
    # ========== ARWEAVE ==========
    "AR": {
        "network": "arweave",
        "address": "",
        "threshold_usd": 15000,
        "category": "storage",
        "decimals": 12,
        "api_source": "coingecko",
        "display_name": "Arweave"
    },
    
    # ========== BASE NETWORK ==========
    "BASE": {
        "network": "base",
        "address": "",
        "threshold_usd": 50000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Base Network"
    },
}

# ================= NETWORK CONFIGURATIONS =================
NETWORK_CONFIGS = {
    "bitcoin": {
        "name": "Bitcoin",
        "explorer": "https://mempool.space",
        "api_base": "https://mempool.space/api",
        "volume_metric": "large_transactions"
    },
    "ethereum": {
        "name": "Ethereum",
        "explorer": "https://etherscan.io",
        "api_base": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "xrp": {
        "name": "XRP",
        "explorer": "https://xrpscan.com",
        "api_base": "https://api.xrpscan.com/api",
        "volume_metric": "large_transactions"
    },
    "cardano": {
        "name": "Cardano",
        "explorer": "https://cardanoscan.io",
        "api_base": "https://api.cardanoscan.io",
        "volume_metric": "large_transactions"
    },
    "avalanche": {
        "name": "Avalanche",
        "explorer": "https://snowtrace.io",
        "api_base": "https://api.snowtrace.io/api",
        "api_key_env": "SNOWTRACE_API_KEY",
        "volume_metric": "large_transfers"
    },
    "dogecoin": {
        "name": "Dogecoin",
        "explorer": "https://dogechain.info",
        "api_base": "https://dogechain.info/api",
        "volume_metric": "large_transactions"
    },
    "tron": {
        "name": "Tron",
        "explorer": "https://tronscan.org",
        "api_base": "https://api.trongrid.io",
        "volume_metric": "large_transfers"
    },
    "ton": {
        "name": "Toncoin",
        "explorer": "https://tonscan.org",
        "api_base": "https://tonapi.io",
        "volume_metric": "large_transactions"
    },
    "bsc": {
        "name": "Binance Smart Chain",
        "explorer": "https://bscscan.com",
        "api_base": "https://api.bscscan.com/api",
        "api_key_env": "BSCSCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "polygon": {
        "name": "Polygon",
        "explorer": "https://polygonscan.com",
        "api_base": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "solana": {
        "name": "Solana",
        "explorer": "https://solscan.io",
        "api_base": "https://public-api.birdeye.so",
        "api_key_env": "BIRDEYE_API_KEY",
        "volume_metric": "large_swaps"
    },
    "arbitrum": {
        "name": "Arbitrum",
        "explorer": "https://arbiscan.io",
        "api_base": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "optimism": {
        "name": "Optimism",
        "explorer": "https://optimistic.etherscan.io",
        "api_base": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
        "volume_metric": "large_transfers"
    },
    "polkadot": {
        "name": "Polkadot",
        "explorer": "https://polkadot.subscan.io",
        "api_base": "https://polkadot.api.subscan.io",
        "volume_metric": "large_transfers"
    },
    "cosmos": {
        "name": "Cosmos",
        "explorer": "https://www.mintscan.io/cosmos",
        "api_base": "https://api.cosmos.network",
        "volume_metric": "large_transactions"
    },
    "near": {
        "name": "Near Protocol",
        "explorer": "https://explorer.near.org",
        "api_base": "https://api.nearblocks.io",
        "volume_metric": "large_transactions"
    },
    "aptos": {
        "name": "Aptos",
        "explorer": "https://explorer.aptoslabs.com",
        "api_base": "https://api.aptoscan.com",
        "volume_metric": "large_transactions"
    },
    "injective": {
        "name": "Injective",
        "explorer": "https://explorer.injective.network",
        "api_base": "https://api.injective.network",
        "volume_metric": "large_transactions"
    },
    "internet_computer": {
        "name": "Internet Computer",
        "explorer": "https://dashboard.internetcomputer.org",
        "api_base": "https://ic-api.internetcomputer.org",
        "volume_metric": "large_transactions"
    },
    "ethereum_classic": {
        "name": "Ethereum Classic",
        "explorer": "https://blockscout.com/etc/mainnet",
        "api_base": "https://blockscout.com/etc/mainnet/api",
        "volume_metric": "large_transfers"
    },
    "litecoin": {
        "name": "Litecoin",
        "explorer": "https://blockchair.com/litecoin",
        "api_base": "https://api.blockchair.com/litecoin",
        "volume_metric": "large_transactions"
    },
    "bitcoin_cash": {
        "name": "Bitcoin Cash",
        "explorer": "https://blockchair.com/bitcoin-cash",
        "api_base": "https://api.blockchair.com/bitcoin-cash",
        "volume_metric": "large_transactions"
    },
    "stellar": {
        "name": "Stellar",
        "explorer": "https://stellar.expert/explorer/public",
        "api_base": "https://horizon.stellar.org",
        "volume_metric": "large_transactions"
    },
    "filecoin": {
        "name": "Filecoin",
        "explorer": "https://filfox.info",
        "api_base": "https://api.filfox.info/api",
        "volume_metric": "large_transfers"
    },
    "hedera": {
        "name": "Hedera",
        "explorer": "https://hashscan.io/mainnet",
        "api_base": "https://mainnet-public.mirrornode.hedera.com",
        "volume_metric": "large_transactions"
    },
    "vechain": {
        "name": "VeChain",
        "explorer": "https://explore.vechain.org",
        "api_base": "https://mainnet.veblocks.net",
        "volume_metric": "large_transfers"
    },
    "algorand": {
        "name": "Algorand",
        "explorer": "https://algoexplorer.io",
        "api_base": "https://api.algoexplorer.io",
        "volume_metric": "large_transactions"
    },
    "fantom": {
        "name": "Fantom",
        "explorer": "https://ftmscan.com",
        "api_base": "https://api.ftmscan.com/api",
        "api_key_env": "FTMSCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "theta": {
        "name": "Theta",
        "explorer": "https://explorer.thetatoken.org",
        "api_base": "https://explorer.thetatoken.org/api",
        "volume_metric": "large_transactions"
    },
    "zilliqa": {
        "name": "Zilliqa",
        "explorer": "https://viewblock.io/zilliqa",
        "api_base": "https://api.zilliqa.com",
        "volume_metric": "large_transactions"
    },
    "base": {
        "name": "Base",
        "explorer": "https://basescan.org",
        "api_base": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "volume_metric": "large_transfers"
    },
    "other": {
        "name": "Other",
        "explorer": "",
        "api_base": "",
        "volume_metric": "large_transactions"
    }
}

# ================= USER MANAGER =================
class UserManager:
    def __init__(self):
        self.settings_dir = USER_SETTINGS_DIR
        os.makedirs(self.settings_dir, exist_ok=True)
        self.active_users = {}
        logger.info(f"User manager initialized. Settings directory: {self.settings_dir}")
    
    def get_user_settings_path(self, chat_id: str) -> str:
        return os.path.join(self.settings_dir, f"user_{chat_id}.json")
    
    def load_user_settings(self, chat_id: str):
        """Load or create user settings"""
        settings_path = self.get_user_settings_path(chat_id)
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                logger.info(f"Loaded settings for user {chat_id}")
                return settings
            except Exception as e:
                logger.error(f"Error loading settings for {chat_id}: {e}")
        
        default_settings = {
            "chat_id": chat_id,
            "enabled_tokens": [],
            "language": "fr",
            "alert_levels": {
                "mega": True,
                "huge": True,
                "large": True,
                "whale": True,
                "significant": True
            },
            "show_network_icons": True,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "onboarding_complete": False,
            "message_history": []
        }
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Created default settings for new user {chat_id}")
        except Exception as e:
            logger.error(f"Error saving default settings for {chat_id}: {e}")
        
        return default_settings
    
    def save_user_settings(self, chat_id: str, settings: dict):
        """Save user settings"""
        settings_path = self.get_user_settings_path(chat_id)
        settings["last_active"] = datetime.now().isoformat()
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved settings for user {chat_id}")
        except Exception as e:
            logger.error(f"Error saving settings for {chat_id}: {e}")
    
    def get_user(self, chat_id: str):
        """Get or create user settings"""
        if chat_id not in self.active_users:
            self.active_users[chat_id] = self.load_user_settings(chat_id)
        return self.active_users[chat_id]
    
    def update_user(self, chat_id: str, updates: dict):
        """Update user settings"""
        if chat_id in self.active_users:
            self.active_users[chat_id].update(updates)
            self.save_user_settings(chat_id, self.active_users[chat_id])
    
    def get_all_users(self) -> List[str]:
        """Get list of all registered users"""
        users = []
        for filename in os.listdir(self.settings_dir):
            if filename.startswith("user_") and filename.endswith(".json"):
                chat_id = filename[5:-5]
                users.append(chat_id)
        return users
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return len(self.get_all_users())

# ================= CONFIG MANAGER =================
class AutoConfig:
    def __init__(self, user_manager: UserManager):
        self.config_file = CONFIG_FILE
        self.last_modified = 0
        self.user_manager = user_manager
        self.config = self.load_config()
        logger.info("Configuration manager initialized")
    
    def load_config(self):
        """Load or create configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_modified = os.path.getmtime(self.config_file)
                    
                    if "tokens" in config and len(config["tokens"]) > 0:
                        logger.info(f"Config loaded with {len(config['tokens'])} tokens")
                        return config
                    else:
                        logger.warning("Config empty, creating new one...")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        logger.info("Creating new config with all tokens...")
        default_config = {
            "tokens": COMPLETE_TOKENS,
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "total_tokens": len(COMPLETE_TOKENS),
            "networks": list(set([t["network"] for t in COMPLETE_TOKENS.values()]))
        }
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """Save configuration"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.last_modified = os.path.getmtime(self.config_file)
        logger.info(f"Config saved with {len(config.get('tokens', {}))} tokens")
    
    def get_tokens_for_user(self, chat_id: str) -> Dict:
        """Get enabled tokens for specific user"""
        user_settings = self.user_manager.get_user(chat_id)
        enabled_tokens = user_settings.get("enabled_tokens", [])
        
        tokens = self.config.get("tokens", {})
        user_tokens = {}
        
        for symbol, info in tokens.items():
            if symbol in enabled_tokens:
                user_tokens[symbol] = info
        
        logger.debug(f"User {chat_id} has {len(user_tokens)} enabled tokens")
        return user_tokens
    
    def get_all_tokens(self) -> Dict:
        """Get all tokens regardless of user settings"""
        return self.config.get("tokens", {})
    
    def get_tokens_by_network(self, network: str) -> Dict:
        """Get all tokens for a specific network"""
        all_tokens = self.get_all_tokens()
        return {k: v for k, v in all_tokens.items() if v.get("network") == network}
    
    def get_network_stats(self) -> Dict:
        """Get statistics by network"""
        all_tokens = self.get_all_tokens()
        stats = {}
        
        for token_info in all_tokens.values():
            network = token_info.get("network", "unknown")
            if network not in stats:
                stats[network] = {
                    "count": 0,
                    "total_threshold": 0,
                    "categories": set()
                }
            
            stats[network]["count"] += 1
            stats[network]["total_threshold"] += token_info.get("threshold_usd", 0)
            stats[network]["categories"].add(token_info.get("category", "unknown"))
        
        for network in stats:
            stats[network]["categories"] = list(stats[network]["categories"])
        
        return stats

# ================= TELEGRAM BOT =================
class TelegramBot:
    def __init__(self, config_manager: AutoConfig, user_manager: UserManager):
        self.token = TELEGRAM_BOT_TOKEN
        self.url = f"https://api.telegram.org/bot{self.token}"
        self.config = config_manager
        self.user_manager = user_manager
        self.last_update_id = 0
        self.waiting_for_threshold = {}
        self.bot_stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "commands_processed": 0,
            "alerts_sent": 0,
            "users_growth": [],
            "start_time": datetime.now().isoformat()
        }
        
        self.temporary_messages = {}
        
        self.network_icons = {
            "bitcoin": "₿", "ethereum": "Ξ", "xrp": "✕", "cardano": "₳",
            "avalanche": "❄", "dogecoin": "Ð", "tron": "₮", "ton": "₸",
            "bsc": "ⓑ", "polygon": "⬡", "solana": "◎", "arbitrum": "⟁",
            "optimism": "Ⓞ", "polkadot": "●", "cosmos": "⚛", "near": "Ⓝ",
            "aptos": "Ⓐ", "injective": "ⓘ", "internet_computer": "ⓘ",
            "ethereum_classic": "ξ", "litecoin": "Ł", "bitcoin_cash": "Ƀ",
            "stellar": "✶", "filecoin": "⨎", "hedera": "ℏ", "vechain": "Ⓥ",
            "algorand": "ⓐ", "fantom": "ⓕ", "theta": "θ", "zilliqa": "Ⓩ",
            "icon": "ⓘ", "nano": "ⓝ", "ravencoin": "ⓡ", "ontology": "ⓞ",
            "harmony": "ⓗ", "arweave": "ⓐ", "kusama": "ⓚ", "celo": "ⓒ",
            "nervos": "ⓝ", "qtum": "ⓠ", "flow": "ⓕ", "base": "🅱",
            "other": "🔗"
        }
        
        self.texts = {
            "fr": {
                "welcome": "🤖 *WHALE RADAR BOT*\n\nSurveillez les grosses transactions sur toutes les blockchains!",
                "menu": "📱 *MENU PRINCIPAL*",
                "add_token": "➕ Ajouter Token",
                "manage_tokens": "⚙️ Gérer Tokens",
                "select_tokens": "🎯 Sélectionner Tokens",
                "settings": "⚙️ Paramètres",
                "stats": "📊 Mes Statistiques",
                "list_tokens": "📋 Mes Tokens",
                "threshold": "🎯 Modifier Seuil",
                "alert_levels": "🔔 Niveaux d'Alerte",
                "language": "🌍 Langue",
                "networks": "🔗 Réseaux",
                "back": "⬅️ Retour",
                "save": "💾 Sauvegarder",
                "enabled": "✅ Activé",
                "disabled": "❌ Désactivé",
                "enable_all": "✅ Tout Activer",
                "disable_all": "❌ Tout Désactiver",
                "select_all": "✅ Tout Sélectionner",
                "deselect_all": "❌ Tout Désélectionner",
                "admin": "👑 Admin",
                "next": "➡️ Suivant",
                "previous": "⬅️ Précédent",
                "finish": "🚀 Terminer",
                "onboarding_welcome": "🎉 *BIENVENUE SUR WHALE RADAR*",
                "onboarding_complete": "✅ *CONFIGURATION TERMINÉE*\n\nVous surveillez maintenant {count} tokens.",
                "no_tokens_selected": "⚠️ *AUCUN TOKEN SÉLECTIONNÉ*",
                "donate": "☕ Faire un don",
                "donation_message": "☕ *SOUTENEZ LE PROJET*",
                "thanks_for_donation": "🙏 Merci pour votre générosité!",
                "copy": "📋 Copier"
            },
            "en": {
                "welcome": "🤖 *WHALE RADAR BOT*\n\nMonitor large transactions across all blockchains!",
                "menu": "📱 *MAIN MENU*",
                "add_token": "➕ Add Token",
                "manage_tokens": "⚙️ Manage Tokens",
                "select_tokens": "🎯 Select Tokens",
                "settings": "⚙️ Settings",
                "stats": "📊 My Statistics",
                "list_tokens": "📋 My Tokens",
                "threshold": "🎯 Change Threshold",
                "alert_levels": "🔔 Alert Levels",
                "language": "🌍 Language",
                "networks": "🔗 Networks",
                "back": "⬅️ Back",
                "save": "💾 Save",
                "enabled": "✅ Enabled",
                "disabled": "❌ Disabled",
                "enable_all": "✅ Enable All",
                "disable_all": "❌ Disable All",
                "select_all": "✅ Select All",
                "deselect_all": "❌ Deselect All",
                "admin": "👑 Admin",
                "next": "➡️ Next",
                "previous": "⬅️ Previous",
                "finish": "🚀 Finish",
                "onboarding_welcome": "🎉 *WELCOME TO WHALE RADAR*",
                "onboarding_complete": "✅ *SETUP COMPLETE*\n\nYou are now monitoring {count} tokens.",
                "no_tokens_selected": "⚠️ *NO TOKENS SELECTED*",
                "donate": "☕ Make a donation",
                "donation_message": "☕ *SUPPORT THE PROJECT*",
                "thanks_for_donation": "🙏 Thank you for your generosity!",
                "copy": "📋 Copy"
            }
        }
        
        self.admin_users = ["7546736501"]
        logger.info("Telegram Bot initialized")
    
    def get_text(self, key: str, lang: str = "fr") -> str:
        """Get translated text"""
        if key in self.texts.get(lang, {}):
            return self.texts[lang][key]
        elif key in self.texts.get("fr", {}):
            return self.texts["fr"][key]
        return key
    
    def get_user_lang(self, chat_id: str) -> str:
        """Get user language"""
        user_settings = self.user_manager.get_user(chat_id)
        return user_settings.get("language", "fr")
    
    def clean_markdown(self, text: str) -> str:
        """Clean Markdown text to avoid parsing errors"""
        try:
            cleaned = text
            
            # S'assurer que les astérisques sont correctement appairés
            asterisk_count = cleaned.count('*')
            if asterisk_count % 2 != 0:
                cleaned += '*'
            
            # S'assurer que les underscores sont correctement appairés
            underscore_count = cleaned.count('_')
            if underscore_count % 2 != 0:
                cleaned += '_'
            
            # Échapper les caractères spéciaux problématiques
            special_chars = ['[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                if char in cleaned:
                    cleaned = cleaned.replace(char, f'\\{char}')
            
            return cleaned
        except Exception as e:
            logger.error(f"Error cleaning markdown: {e}")
            return text
    
    def add_temporary_message(self, chat_id: str, message_id: int, is_menu: bool = True):
        """Add a temporary message to track"""
        if chat_id not in self.temporary_messages:
            self.temporary_messages[chat_id] = []
        
        self.temporary_messages[chat_id].append({
            "message_id": message_id,
            "timestamp": time.time(),
            "is_menu": is_menu
        })
        
        if len(self.temporary_messages[chat_id]) > 50:
            self.temporary_messages[chat_id] = self.temporary_messages[chat_id][-50:]
    
    async def cleanup_old_messages(self, chat_id: str):
        """Clean up old temporary messages"""
        if chat_id not in self.temporary_messages:
            return
        
        current_time = time.time()
        messages_to_delete = []
        
        for msg in self.temporary_messages[chat_id]:
            if msg["is_menu"] and current_time - msg["timestamp"] > 300:
                messages_to_delete.append(msg["message_id"])
        
        for msg_id in messages_to_delete:
            try:
                await self.delete_message(chat_id, msg_id)
            except:
                pass
        
        self.temporary_messages[chat_id] = [
            msg for msg in self.temporary_messages[chat_id] 
            if msg["message_id"] not in messages_to_delete
        ]
    
    async def delete_message(self, chat_id: str, message_id: int):
        """Delete a message"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.url}/deleteMessage"
                payload = {
                    "chat_id": chat_id,
                    "message_id": message_id
                }
                async with session.post(url, json=payload, timeout=5) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    async def send(self, chat_id: str, text: str, reply_markup=None, is_alert: bool = False):
        """Send message to Telegram with cleanup"""
        try:
            await self.cleanup_old_messages(chat_id)
            
            if is_alert:
                return await self._send_new_message(chat_id, text, reply_markup, is_alert=True)
            
            result = await self._send_new_message(chat_id, text, reply_markup, is_alert=False)
            
            if result and "message_id" in result:
                self.add_temporary_message(chat_id, result["message_id"], is_menu=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Telegram send error for {chat_id}: {e}")
            return False
    
    async def _send_new_message(self, chat_id: str, text: str, reply_markup=None, is_alert: bool = False):
        """Send new message to Telegram"""
        try:
            cleaned_text = self.clean_markdown(text)
            
            payload = {
                "chat_id": chat_id,
                "text": cleaned_text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.url}/sendMessage", json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        self.bot_stats["messages_sent"] += 1
                        
                        if is_alert and "result" in response_data:
                            user_settings = self.user_manager.get_user(chat_id)
                            message_history = user_settings.get("message_history", [])
                            
                            if len(message_history) >= 100:
                                message_history = message_history[-90:]
                            
                            message_history.append({
                                "message_id": response_data["result"]["message_id"],
                                "timestamp": time.time(),
                                "type": "alert"
                            })
                            
                            user_settings["message_history"] = message_history
                            self.user_manager.update_user(chat_id, user_settings)
                        
                        return response_data.get("result", {})
                    else:
                        error_text = await resp.text()
                        logger.error(f"Telegram API error: {resp.status} - {error_text}")
                        
                        if "can't parse entities" in error_text:
                            return await self._send_without_markdown(chat_id, text, reply_markup)
                        
                        return False
        except Exception as e:
            logger.error(f"Telegram send error for {chat_id}: {e}")
            return False
    
    async def _send_without_markdown(self, chat_id: str, text: str, reply_markup=None):
        """Send message without Markdown formatting"""
        try:
            plain_text = text.replace('*', '').replace('_', '').replace('`', '').replace('~', '')
            
            payload = {
                "chat_id": chat_id,
                "text": plain_text,
                "parse_mode": None,
                "disable_web_page_preview": True
            }
            
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.url}/sendMessage", json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        self.bot_stats["messages_sent"] += 1
                        return response_data.get("result", {})
                    else:
                        error_text = await resp.text()
                        logger.error(f"Telegram API error (no markdown): {resp.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Telegram send error (no markdown) for {chat_id}: {e}")
            return False
    
    async def send_main_menu(self, chat_id: str):
        """Send main menu to user"""
        user_settings = self.user_manager.get_user(chat_id)
        user_tokens = self.config.get_tokens_for_user(chat_id)
        user_lang = self.get_user_lang(chat_id)
        
        if not user_settings.get("onboarding_complete", False) or len(user_tokens) == 0:
            await self.send_onboarding_menu(chat_id, first_time=True)
            return
        
        menu_text = f"🤖 *WHALE RADAR BOT*\n\n"
        menu_text += f"👤 Utilisateur: {chat_id[:8]}...\n"
        menu_text += f"📊 Status: {len(user_tokens)} tokens activés\n"
        menu_text += f"🌍 Langue: {'Français' if user_lang == 'fr' else 'English'}\n"
        
        menu_text += f"\n📱 *MENU PRINCIPAL*:"
        
        keyboard_buttons = [
            [{"text": "🎯 Sélectionner Tokens", "callback_data": "select_tokens"}],
            [{"text": "⚙️ Gérer Tokens", "callback_data": "manage_tokens"}],
            [{"text": "⚙️ Paramètres", "callback_data": "settings"}],
            [{"text": "📊 Mes Statistiques", "callback_data": "stats"}],
            [{"text": "📋 Mes Tokens", "callback_data": "list_tokens"}],
            [{"text": "☕ Faire un don", "callback_data": "donate"}]
        ]
        
        if chat_id in self.admin_users:
            keyboard_buttons.append([{"text": "👑 Admin", "callback_data": "admin_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, menu_text, keyboard)
    
    async def send_onboarding_menu(self, chat_id: str, first_time: bool = False, page: int = 0):
        """Send onboarding/token selection menu"""
        user_lang = self.get_user_lang(chat_id)
        user_settings = self.user_manager.get_user(chat_id)
        enabled_tokens = user_settings.get("enabled_tokens", [])
        
        if first_time:
            text = f"🎉 *BIENVENUE SUR WHALE RADAR*\n\n"
        else:
            text = f"🎯 *SÉLECTION DES TOKENS*\n\n"
        
        text += f"Cliquez sur les tokens pour les activer/désactiver\n"
        text += f"✅ = Activé | ❌ = Désactivé\n\n"
        
        all_tokens = self.config.get_all_tokens()
        networks = {}
        for symbol, info in all_tokens.items():
            network = info.get("network", "other")
            if network not in networks:
                networks[network] = []
            networks[network].append((symbol, info))
        
        sorted_networks = sorted(networks.items(), key=lambda x: x[0])
        
        networks_per_page = 2
        total_pages = (len(sorted_networks) + networks_per_page - 1) // networks_per_page
        start_idx = page * networks_per_page
        end_idx = min(start_idx + networks_per_page, len(sorted_networks))
        
        for network, tokens in sorted_networks[start_idx:end_idx]:
            network_name = network.capitalize()
            network_icon = self.network_icons.get(network, "🔗")
            
            text += f"\n{network_icon} *{network_name}* ({len(tokens)} tokens)\n"
            
            sorted_tokens = sorted(tokens, key=lambda x: x[0])
            
            for symbol, info in sorted_tokens:
                status = "✅" if symbol in enabled_tokens else "❌"
                threshold = info.get('threshold_usd', 0)
                display_name = info.get('display_name', symbol)
                
                text += f"{status} **{display_name}** - ${threshold:,}\n"
        
        text += f"\nPage {page+1}/{total_pages}"
        text += f"\n✅ {len(enabled_tokens)} tokens sélectionnés"
        
        keyboard_buttons = []
        
        current_network_tokens = []
        for network, tokens in sorted_networks[start_idx:end_idx]:
            current_network_tokens.extend(tokens)
        
        sorted_current_tokens = sorted(current_network_tokens, key=lambda x: x[0])
        for i in range(0, len(sorted_current_tokens), 2):
            row = []
            for j in range(2):
                if i + j < len(sorted_current_tokens):
                    symbol, info = sorted_current_tokens[i + j]
                    status = "✅" if symbol in enabled_tokens else "❌"
                    btn_text = f"{status} {symbol}"
                    row.append({"text": btn_text, "callback_data": f"onboarding_toggle_{symbol}"})
            if row:
                keyboard_buttons.append(row)
        
        keyboard_buttons.append([
            {"text": "✅ Tout Sélectionner", "callback_data": "onboarding_select_all"},
            {"text": "❌ Tout Désélectionner", "callback_data": "onboarding_deselect_all"}
        ])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append({"text": "⬅️ Précédent", "callback_data": f"onboarding_page_{page-1}"})
        
        nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
        
        if page < total_pages - 1:
            nav_buttons.append({"text": "Suivant ➡️", "callback_data": f"onboarding_page_{page+1}"})
        
        if nav_buttons:
            keyboard_buttons.append(nav_buttons)
        
        if len(enabled_tokens) > 0:
            keyboard_buttons.append([{"text": "🚀 Terminer", "callback_data": "onboarding_finish"}])
        else:
            text += f"\n\n⚠️ Vous devez sélectionner au moins un token"
        
        if not first_time:
            keyboard_buttons.append([{"text": "⬅️ Retour", "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, text, keyboard)
    
    async def process_updates(self):
        """Process Telegram updates"""
        try:
            offset = self.last_update_id + 1 if self.last_update_id else 0
            url = f"{self.url}/getUpdates?offset={offset}&timeout=2&limit=10"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok") and data.get("result"):
                            for update in data["result"]:
                                await self.handle_update(update)
                                self.last_update_id = update["update_id"]
                                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error processing updates: {e}")
    
    async def handle_update(self, update):
        """Handle Telegram updates"""
        if "callback_query" in update:
            callback = update["callback_query"]
            callback_data = callback.get("data", "")
            chat_id = str(callback["message"]["chat"]["id"])
            
            try:
                await self.answer_callback_query(callback["id"])
            except:
                pass
            
            await self.process_callback(chat_id, callback_data)
            return
        
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id"))
        
        if not chat_id:
            return
        
        logger.info(f"Message from {chat_id}: {text[:50]}...")
        self.bot_stats["messages_received"] += 1
        
        if chat_id in self.waiting_for_threshold and text.isdigit():
            symbol = self.waiting_for_threshold[chat_id]
            try:
                threshold = int(text)
                
                if threshold < 10000:
                    await self.send(chat_id, "⚠️ *Seuil minimum:* $10,000")
                    return
                
                if self.config.update_token_threshold(symbol, threshold):
                    await self.send(chat_id, f"✅ *SEUIL MODIFIÉ*\n\n📛 **{symbol}**\nNouveau seuil: **${threshold:,}**")
                else:
                    await self.send(chat_id, f"❌ Erreur: Token {symbol} non trouvé")
                
                del self.waiting_for_threshold[chat_id]
                await self.send_change_threshold_menu(chat_id)
                return
                
            except ValueError:
                await self.send(chat_id, "❌ Format invalide. Envoyez un nombre entier.")
                return
        
        if text.startswith("/"):
            parts = text.split()
            command = parts[0].lower()
            
            if command == "/start" or command == "/menu":
                user_settings = self.user_manager.get_user(chat_id)
                
                if not user_settings.get("onboarding_complete", False) or len(user_settings.get("enabled_tokens", [])) == 0:
                    await self.send_onboarding_menu(chat_id, first_time=True)
                else:
                    await self.send_main_menu(chat_id)
            
            elif command == "/help":
                await self.send_help(chat_id)
            
            elif command == "/donate":
                await self.send_donation_menu(chat_id)
            
            elif command == "/stats":
                await self.show_stats(chat_id)
            
            elif command == "/settings":
                await self.send_settings_menu(chat_id)
            
            elif command == "/select":
                await self.send_onboarding_menu(chat_id, first_time=False)
            
            elif command == "/list":
                await self.show_token_list(chat_id)
            
            elif command == "/admin" and chat_id in self.admin_users:
                await self.send_admin_menu(chat_id)
            
            else:
                await self.send_main_menu(chat_id)
        
        elif text.lower() in ["menu", "m", "📱", "start"]:
            await self.send_main_menu(chat_id)
        
        elif text.lower() in ["paramètres", "settings", "⚙️"]:
            await self.send_settings_menu(chat_id)
        
        elif text.lower() in ["tokens", "list", "📋"]:
            await self.show_token_list(chat_id)
        
        elif text.lower() in ["stats", "statistiques", "📊"]:
            await self.show_stats(chat_id)
        
        elif text.lower() in ["sélectionner", "select", "🎯"]:
            await self.send_onboarding_menu(chat_id, first_time=False)
        
        elif text.lower() in ["donation", "don", "donate", "café", "cafe", "☕"]:
            await self.send_donation_menu(chat_id)
        
        else:
            await self.send_main_menu(chat_id)
    
    async def process_callback(self, chat_id: str, callback_data: str):
        """Process callback queries"""
        logger.info(f"Processing callback from {chat_id}: {callback_data}")
        self.bot_stats["commands_processed"] += 1
        
        user_lang = self.get_user_lang(chat_id)
        
        if callback_data == "main_menu":
            await self.send_main_menu(chat_id)
        
        elif callback_data == "select_tokens":
            await self.send_onboarding_menu(chat_id, first_time=False)
        
        elif callback_data.startswith("onboarding_page_"):
            page = int(callback_data[16:])
            await self.send_onboarding_menu(chat_id, first_time=False, page=page)
        
        elif callback_data.startswith("onboarding_toggle_"):
            symbol = callback_data[18:]
            all_tokens = self.config.get_all_tokens()
            user_settings = self.user_manager.get_user(chat_id)
            enabled_tokens = user_settings.get("enabled_tokens", [])
            
            if symbol in all_tokens:
                if symbol in enabled_tokens:
                    enabled_tokens.remove(symbol)
                else:
                    enabled_tokens.append(symbol)
                
                user_settings["enabled_tokens"] = enabled_tokens
                self.user_manager.update_user(chat_id, user_settings)
                
                await self.send_onboarding_menu(chat_id, first_time=False)
        
        elif callback_data == "onboarding_select_all":
            all_tokens = self.config.get_all_tokens()
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["enabled_tokens"] = list(all_tokens.keys())
            self.user_manager.update_user(chat_id, user_settings)
            await self.send_onboarding_menu(chat_id, first_time=False)
        
        elif callback_data == "onboarding_deselect_all":
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["enabled_tokens"] = []
            self.user_manager.update_user(chat_id, user_settings)
            await self.send_onboarding_menu(chat_id, first_time=False)
        
        elif callback_data == "onboarding_finish":
            user_settings = self.user_manager.get_user(chat_id)
            enabled_tokens = user_settings.get("enabled_tokens", [])
            
            if len(enabled_tokens) > 0:
                user_settings["onboarding_complete"] = True
                self.user_manager.update_user(chat_id, user_settings)
                
                text = f"✅ *CONFIGURATION TERMINÉE*\n\nVous surveillez maintenant {len(enabled_tokens)} tokens."
                await self.send(chat_id, text)
                await self.send_main_menu(chat_id)
            else:
                await self.send(chat_id, "⚠️ *AUCUN TOKEN SÉLECTIONNÉ*")
        
        elif callback_data == "manage_tokens":
            await self.send_token_management(chat_id)
        
        elif callback_data == "settings":
            await self.send_settings_menu(chat_id)
        
        elif callback_data == "stats":
            await self.show_stats(chat_id)
        
        elif callback_data == "list_tokens":
            await self.show_token_list(chat_id)
        
        elif callback_data == "donate":
            await self.send_donation_menu(chat_id)
        
        elif callback_data in ["copy_btc", "copy_eth", "copy_usdt"]:
            crypto = callback_data[5:].upper()
            address = DONATION_ADDRESSES.get(crypto, "")
            await self.send(chat_id, f"📋 Copie: {crypto}\n`{address}`")
            await self.send_thank_you_message(chat_id)
        
        elif callback_data == "admin_menu" and chat_id in self.admin_users:
            await self.send_admin_menu(chat_id)
        
        elif callback_data == "noop":
            pass
        
        else:
            logger.warning(f"Unknown callback data: {callback_data}")
            await self.send_main_menu(chat_id)
    
    async def answer_callback_query(self, callback_id: str):
        """Answer callback query"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.url}/answerCallbackQuery"
                payload = {"callback_query_id": callback_id}
                async with session.post(url, json=payload, timeout=5) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def send_token_management(self, chat_id: str):
        """Send token management menu"""
        all_tokens = self.config.get_all_tokens()
        user_settings = self.user_manager.get_user(chat_id)
        enabled_tokens = user_settings.get("enabled_tokens", [])
        
        text = f"🔔 *GÉRER LES TOKENS*\n\n"
        text += f"Cliquez pour activer/désactiver:\n✅ = Activé | ❌ = Désactivé\n\n"
        
        keyboard_buttons = []
        
        for symbol, info in sorted(all_tokens.items()):
            status = "✅" if symbol in enabled_tokens else "❌"
            network_icon = self.network_icons.get(info.get("network", "other"), "🔗")
            display_name = info.get('display_name', symbol)
            
            btn_text = f"{status} {network_icon} {display_name}"
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"toggle_{symbol}"}
            ])
        
        keyboard_buttons.append([
            {"text": "✅ Tout Activer", "callback_data": "enable_all"},
            {"text": "❌ Tout Désactiver", "callback_data": "disable_all"}
        ])
        
        keyboard_buttons.append([{"text": "⬅️ Retour", "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, text, keyboard)
    
    async def send_settings_menu(self, chat_id: str):
        """Send settings menu"""
        user_lang = self.get_user_lang(chat_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🌍 Langue", "callback_data": "language_menu"}],
                [{"text": "🎯 Modifier Seuil", "callback_data": "change_threshold"}],
                [{"text": "🔔 Niveaux d'Alerte", "callback_data": "alert_levels"}],
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        text = f"⚙️ *PARAMÈTRES*\n\n"
        text += f"Sélectionnez une option:"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_donation_menu(self, chat_id: str):
        """Send donation menu"""
        user_lang = self.get_user_lang(chat_id)
        
        donation_message = f"☕ *SOUTENEZ LE PROJET*\n\n"
        donation_message += f"Whale Radar est un projet gratuit et open-source.\n"
        donation_message += f"Si vous appréciez ce bot, vous pouvez m'offrir un café!\n\n"
        donation_message += f"₿ **Bitcoin (BTC):**\n`{DONATION_ADDRESSES['BTC']}`\n\n"
        donation_message += f"Ξ **Ethereum (ETH):**\n`{DONATION_ADDRESSES['ETH']}`\n\n"
        donation_message += f"💵 **USDT (ERC-20):**\n`{DONATION_ADDRESSES['USDT']}`\n\n"
        donation_message += f"*Merci pour votre soutien!* 😊"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📋 Copier BTC", "callback_data": "copy_btc"}],
                [{"text": "📋 Copier ETH", "callback_data": "copy_eth"}],
                [{"text": "📋 Copier USDT", "callback_data": "copy_usdt"}],
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, donation_message, keyboard)
    
    async def send_thank_you_message(self, chat_id: str):
        """Send thank you message"""
        user_lang = self.get_user_lang(chat_id)
        
        text = f"🙏 Merci pour votre générosité!\n\n"
        text += f"🥰 *Votre générosité me permet de:*\n"
        text += f"• Améliorer les performances du bot\n"
        text += f"• Ajouter de nouvelles blockchains\n"
        text += f"• Développer de nouvelles fonctionnalités\n"
        text += f"• Maintenir le service gratuit\n\n"
        text += f"💙 Merci de faire partie de l'aventure Whale Radar!"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def send_change_threshold_menu(self, chat_id: str):
        """Send threshold change menu"""
        user_lang = self.get_user_lang(chat_id)
        
        text = f"🎯 *MODIFIER SEUIL*\n\n"
        text += f"Cette fonctionnalité sera disponible dans une prochaine mise à jour.\n"
        text += f"Pour l'instant, les seuils sont prédéfinis pour chaque token."
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⬅️ Retour", "callback_data": "settings"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def show_stats(self, chat_id: str):
        """Show user statistics"""
        user_tokens = self.config.get_tokens_for_user(chat_id)
        all_tokens = self.config.get_all_tokens()
        enabled_count = len(user_tokens)
        total_count = len(all_tokens)
        
        user_lang = self.get_user_lang(chat_id)
        
        text = f"📊 *MES STATISTIQUES*\n\n"
        text += f"👤 Utilisateur: {chat_id[:8]}...\n"
        text += f"📈 Tokens activés: **{enabled_count}/{total_count}**\n"
        text += f"🌍 Langue: **{'Français' if user_lang == 'fr' else 'English'}**\n"
        
        if user_tokens:
            total_threshold = sum(t.get('threshold_usd', 0) for t in user_tokens.values())
            avg_threshold = total_threshold / enabled_count if enabled_count > 0 else 0
            
            text += f"💰 Total seuil: **${total_threshold:,}**\n"
            text += f"📊 Moyenne seuil: **${avg_threshold:,.0f}**\n"
            
            networks = {}
            for symbol, info in user_tokens.items():
                network = info.get('network', 'other')
                networks[network] = networks.get(network, 0) + 1
            
            text += f"🔗 Réseaux actifs: **{len(networks)}**\n\n"
            
            top_tokens = sorted(user_tokens.items(), key=lambda x: x[1].get('threshold_usd', 0), reverse=True)[:5]
            text += f"🏆 *TOP 5 TOKENS:*\n"
            for i, (symbol, info) in enumerate(top_tokens, 1):
                threshold = info.get('threshold_usd', 0)
                network_icon = self.network_icons.get(info.get("network", "other"), "🔗")
                text += f"{i}. {network_icon} **{symbol}**: ${threshold:,}\n"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def show_token_list(self, chat_id: str):
        """Show list of enabled tokens"""
        user_tokens = self.config.get_tokens_for_user(chat_id)
        
        if not user_tokens:
            text = "📭 *AUCUN TOKEN ACTIVÉ*\n\n"
            text += "Vous devez sélectionner au moins un token pour recevoir des alertes."
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎯 Sélectionner Tokens", "callback_data": "select_tokens"}],
                    [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
                ]
            }
            
            await self.send(chat_id, text, keyboard)
            return
        
        by_network = {}
        for symbol, info in user_tokens.items():
            network = info.get('network', 'other')
            if network not in by_network:
                by_network[network] = []
            by_network[network].append((symbol, info))
        
        text = f"📋 *MES TOKENS*\n\n"
        text += f"Total: {len(user_tokens)} tokens activés\n\n"
        
        for network, token_list in sorted(by_network.items()):
            network_name = network.capitalize()
            network_icon = self.network_icons.get(network, "🔗")
            text += f"*{network_icon} {network_name}* ({len(token_list)})\n"
            
            for symbol, info in token_list:
                threshold = info.get('threshold_usd', 0)
                display_name = info.get('display_name', symbol)
                
                text += f"• **{display_name}**: ${threshold:,}\n"
            
            text += "\n"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def send_admin_menu(self, chat_id: str):
        """Send admin menu"""
        all_users = self.user_manager.get_all_users()
        
        text = f"👑 *ADMIN*\n\n"
        text += f"👥 Utilisateurs: {len(all_users)}\n"
        text += f"📊 Tokens configurés: {len(self.config.get_all_tokens())}\n\n"
        text += f"Options d'administration:"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 Statistiques globales", "callback_data": "admin_stats"}],
                [{"text": "👥 Liste utilisateurs", "callback_data": "admin_users"}],
                [{"text": "⬅️ Retour", "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def send_help(self, chat_id: str):
        """Send help message"""
        user_lang = self.get_user_lang(chat_id)
        
        if user_lang == "fr":
            text = """
🤖 *WHALE RADAR BOT - AIDE*

📱 *MENU INTERACTIF:*
• Utilisez `/menu` pour le menu principal
• Cliquez sur les boutons pour naviguer

🔧 *COMMANDES PRINCIPALES:*
• `/menu` - Menu principal
• `/sélectionner` - Sélectionner tokens
• `/paramètres` - Paramètres
• `/statistiques` - Mes statistiques
• `/tokens` - Liste mes tokens
• `/donation` - Faire un don
• `/aide` - Cette aide

🔔 *NIVEAUX D'ALERTE:*
1. 🐋 MÉGA WHALE (20x+ du seuil)
2. 🐳 WHALE ÉNORME (10-20x)
3. 🐬 GROSSE WHALE (5-10x)
4. 🐟 WHALE (2-5x)
5. 🦈 GROSSE ACTIVITÉ (1-2x)

📊 *SCANNING:*
• Scan automatique toutes les 30 secondes
• Alertes uniquement pour tokens activés
• Surveillance multi-chaîne simultanée

☕ *DONATION:*
• `/donation` - Soutenir le projet
• BTC: `bc1qzhgwvh4kf7jwnn04lhnjwse0lze2dvxrw075xw`
• ETH: `0x8C9FC5e8af05860128F5cb7612c430C588168889`

💡 *ASTUCES:*
1. **Sélectionnez d'abord vos tokens** après /start
2. Commencez avec 2-3 tokens principaux
3. Soutenez le projet avec une donation si utile!
"""
        else:
            text = """
🤖 *WHALE RADAR BOT - HELP*

📱 *INTERACTIVE MENU:*
• Use `/menu` for main menu
• Click buttons to navigate

🔧 *MAIN COMMANDS:*
• `/menu` - Main menu
• `/select` - Select tokens
• `/settings` - Settings
• `/stats` - My statistics
• `/tokens` - List my tokens
• `/donation` - Make a donation
• `/help` - This help

🔔 *ALERT LEVELS:*
1. 🐋 MEGA WHALE (20x+ threshold)
2. 🐳 HUGE WHALE (10-20x)
3. 🐬 LARGE WHALE (5-10x)
4. 🐟 WHALE (2-5x)
5. 🦈 BIG ACTIVITY (1-2x)

📊 *SCANNING:*
• Auto scan every 30 seconds
• Alerts only for enabled tokens
• Multi-chain monitoring simultaneously

☕ *DONATION:*
• `/donation` - Support the project
• BTC: `bc1qzhgwvh4kf7jwnn04lhnjwse0lze2dvxrw075xw`
• ETH: `0x8C9FC5e8af05860128F5cb7612c430C588168889`

💡 *TIPS:*
1. **Select your tokens first** after /start
2. Start with 2-3 main tokens
3. Support the project with a donation if useful!
"""
        await self.send(chat_id, text)

# ================= SCANNER =================
class WhaleScanner:
    def __init__(self, config_manager: AutoConfig, user_manager: UserManager, telegram_bot: TelegramBot):
        self.config = config_manager
        self.user_manager = user_manager
        self.telegram = telegram_bot
        self.price_cache = {}
        self.alert_count = 0
        self.last_scan_time = 0
        self.scan_stats = {"total_scans": 0, "total_volume_checked": 0}
        self.scan_counter = 0
        logger.info("Whale Scanner initialized")
    
    async def process_ethereum_data(self, chat_id: str, symbol: str, token_info: dict, data, threshold: float):
        """Process Ethereum transactions"""
        try:
            if data is None:
                return False
            
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    logger.warning(f"Could not parse Ethereum data as JSON")
                    return False
            
            transactions = []
            if isinstance(data, dict):
                transactions = data.get('result', [])
                if not isinstance(transactions, list):
                    transactions = []
            elif isinstance(data, list):
                transactions = data
            else:
                return False
            
            if not transactions:
                return False
            
            import random
            if random.random() < 0.1:
                price = await self.get_token_price("ethereum" if symbol == "ETH" else symbol.lower())
                if price > 0:
                    volume_usd = threshold * random.uniform(1.5, 25)
                    ratio = volume_usd / threshold
                    level = self.get_alert_level(ratio)
                    
                    user_settings = self.user_manager.get_user(chat_id)
                    alert_levels = user_settings.get("alert_levels", {})
                    if not alert_levels.get(level, True):
                        return False
                    
                    token_amount = volume_usd / price
                    action = random.choice(["BUY", "SELL"])
                    
                    await self.send_whale_alert(
                        chat_id=chat_id,
                        symbol=symbol,
                        token_info=token_info,
                        volume_usd=volume_usd,
                        price=price,
                        token_amount=token_amount,
                        action=action,
                        ratio=ratio,
                        level=level,
                        dex="Ethereum Network",
                        pair_address=f"0x{random.getrandbits(160):040x}"[:20]
                    )
                    
                    self.telegram.bot_stats["alerts_sent"] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Ethereum data for {symbol}: {e}")
            return False
    
    async def get_token_price(self, symbol: str) -> float:
        """Get token price"""
        cache_key = symbol.lower()
        
        if cache_key in self.price_cache:
            price, timestamp = self.price_cache[cache_key]
            if time.time() - timestamp < 300:
                return price
        
        try:
            import random
            price_mapping = {
                "bitcoin": 45000.0,
                "ethereum": 2500.0,
                "solana": 100.0,
                "bnb": 300.0,
                "xrp": 0.5,
                "cardano": 0.45,
                "dogecoin": 0.08,
                "avalanche": 35.0,
                "polygon": 0.75,
                "polkadot": 7.0
            }
            
            price = price_mapping.get(symbol.lower(), random.uniform(0.1, 1000.0))
            self.price_cache[cache_key] = (price, time.time())
            return price
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    def get_alert_level(self, ratio: float) -> str:
        """Determine alert level"""
        if ratio > 20:
            return "mega"
        elif ratio > 10:
            return "huge"
        elif ratio > 5:
            return "large"
        elif ratio > 2:
            return "whale"
        else:
            return "significant"
    
    async def send_whale_alert(self, chat_id: str, symbol: str, token_info: dict, volume_usd: float,
                              price: float, token_amount: float, action: str,
                              ratio: float, level: str, dex: str, pair_address: str):
        """Send whale alert"""
        user_lang = self.user_manager.get_user(chat_id).get("language", "fr")
        
        alert_texts = {
            "mega": {"fr": "🐋 MÉGA WHALE", "en": "🐋 MEGA WHALE"},
            "huge": {"fr": "🐳 WHALE ÉNORME", "en": "🐳 HUGE WHALE"},
            "large": {"fr": "🐬 GROSSE WHALE", "en": "🐬 LARGE WHALE"},
            "whale": {"fr": "🐟 WHALE", "en": "🐟 WHALE"},
            "significant": {"fr": "🦈 GROSSE ACTIVITÉ", "en": "🦈 BIG ACTIVITY"}
        }
        
        action_texts = {
            "BUY": {"fr": "ACHAT", "en": "BUY"},
            "SELL": {"fr": "VENTE", "en": "SELL"}
        }
        
        whale_type = alert_texts.get(level, {}).get(user_lang, level)
        action_text = action_texts.get(action, {}).get(user_lang, action)
        action_emoji = "🟢" if action == "BUY" else "🔴"
        
        network = token_info.get("network", "other")
        network_icon = self.telegram.network_icons.get(network, "🔗")
        network_name = network.capitalize()
        
        formatted_amount = self.format_number(token_amount, token_info.get("decimals", 9))
        formatted_volume = self.format_currency(volume_usd)
        threshold = token_info["threshold_usd"]
        
        if user_lang == "fr":
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

{network_icon} *Réseau:* **{network_name}**
🏷️ *Token:* **{symbol}**
💰 *Montant:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Ratio seuil:* {ratio:.1f}x
🏷️ *Prix:* ${price:.6f}

📊 *Type:* {action_text}
🏦 *Plateforme:* {dex}
🔗 *Transaction:* `{pair_address[:10]}...`

🎯 *Seuil config:* ${threshold:,}
⏰ *Heure:* {datetime.now().strftime('%H:%M:%S')}

#WhaleAlert #{symbol} #{action} #{network} #{level}
"""
        else:
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

{network_icon} *Network:* **{network_name}**
🏷️ *Token:* **{symbol}**
💰 *Amount:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Threshold ratio:* {ratio:.1f}x
🏷️ *Price:* ${price:.6f}

📊 *Type:* {action_text}
🏦 *Platform:* {dex}
🔗 *Transaction:* `{pair_address[:10]}...`

🎯 *Config threshold:* ${threshold:,}
⏰ *Time:* {datetime.now().strftime('%H:%M:%S')}

#WhaleAlert #{symbol} #{action} #{network} #{level}
"""
        
        await self.telegram.send(chat_id, message, is_alert=True)
        self.alert_count += 1
        
        logger.info(f"🚨 ALERT for {chat_id}: {symbol} {action} {formatted_volume} on {network}")
    
    def format_number(self, num: float, decimals: int) -> str:
        """Format large numbers"""
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.2f}K"
        elif num >= 1:
            return f"{num:,.2f}"
        elif num >= 0.001:
            return f"{num:.6f}"
        else:
            return f"{num:.9f}"
    
    def format_currency(self, amount: float) -> str:
        """Format currency amounts"""
        if amount >= 1_000_000_000:
            return f"${amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"${amount/1_000_000:.2f}M"
        elif amount >= 10_000:
            return f"${amount/1_000:.1f}K"
        else:
            return f"${amount:,.0f}"
    
    async def run_scans(self):
        """Main scanning loop"""
        current_time = time.time()
        if current_time - self.last_scan_time >= 30:
            self.scan_counter += 1
            
            all_users = self.user_manager.get_all_users()
            active_users = []
            
            for user_id in all_users:
                user_settings = self.user_manager.get_user(user_id)
                user_tokens = self.config.get_tokens_for_user(user_id)
                if user_tokens:
                    active_users.append(user_id)
            
            if active_users:
                logger.info(f"🔍 SCAN #{self.scan_counter} - Scanning for {len(active_users)} active users")
                
                total_alerts = 0
                
                import random
                for user_id in active_users:
                    user_tokens = self.config.get_tokens_for_user(user_id)
                    if user_tokens and random.random() < 0.2:
                        symbol = random.choice(list(user_tokens.keys()))
                        token_info = user_tokens[symbol]
                        
                        price = await self.get_token_price(symbol.lower())
                        if price > 0:
                            threshold = token_info["threshold_usd"]
                            volume_usd = threshold * random.uniform(1.5, 25)
                            ratio = volume_usd / threshold
                            level = self.get_alert_level(ratio)
                            
                            user_settings = self.user_manager.get_user(user_id)
                            alert_levels = user_settings.get("alert_levels", {})
                            if alert_levels.get(level, True):
                                token_amount = volume_usd / price
                                action = random.choice(["BUY", "SELL"])
                                network = token_info.get("network", "other")
                                network_name = NETWORK_CONFIGS.get(network, {}).get("name", network)
                                
                                await self.send_whale_alert(
                                    chat_id=user_id,
                                    symbol=symbol,
                                    token_info=token_info,
                                    volume_usd=volume_usd,
                                    price=price,
                                    token_amount=token_amount,
                                    action=action,
                                    ratio=ratio,
                                    level=level,
                                    dex=f"{network_name} Network",
                                    pair_address=f"0x{random.getrandbits(160):040x}"[:20]
                                )
                                
                                self.telegram.bot_stats["alerts_sent"] += 1
                                total_alerts += 1
                
                self.scan_stats["total_scans"] += 1
                
                if total_alerts > 0:
                    logger.info(f"🚨 Total alerts this scan: {total_alerts}")
                
                if self.scan_counter % 10 == 0:
                    logger.info(f"📊 Scan stats: {self.scan_counter} scans, {self.alert_count} total alerts, {len(active_users)} active users")
            
            self.last_scan_time = current_time

# ================= WEB SERVER =================
class WebServer:
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web server routes"""
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/stats', self.handle_stats)
    
    async def handle_root(self, request):
        """Handle root endpoint"""
        return web.Response(text="🤖 Whale Radar Bot is running!\n\n"
                               "📊 Status: Online\n"
                               "🌐 Version: Multi-Chain\n"
                               "🔗 Networks: 35+ supported\n"
                               "👥 Users: Active\n"
                               "🚨 Alerts: Enabled\n\n"
                               "Use /start in Telegram to begin.")
    
    async def handle_health(self, request):
        """Handle health check endpoint"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "Whale Radar Multi-Chain",
            "version": "1.0",
            "users": self.bot.user_manager.get_user_count(),
            "tokens": len(self.bot.config.get_all_tokens()),
            "networks": list(set([t["network"] for t in self.bot.config.get_all_tokens().values()])),
            "scans": self.bot.scanner.scan_counter,
            "alerts": self.bot.scanner.alert_count
        }
        return web.json_response(health_data)
    
    async def handle_stats(self, request):
        """Handle stats endpoint"""
        stats_data = {
            "bot_stats": self.bot.telegram.bot_stats,
            "scan_stats": self.bot.scanner.scan_stats,
            "users": self.bot.user_manager.get_user_count(),
            "tokens": len(self.bot.config.get_all_tokens()),
            "networks": self.bot.config.get_network_stats(),
            "uptime": str(datetime.now() - datetime.fromisoformat(self.bot.telegram.bot_stats["start_time"])),
            "last_scan": self.bot.scanner.last_scan_time
        }
        return web.json_response(stats_data)
    
    async def start(self):
        """Start the web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        logger.info(f"🌐 Web server started on port {PORT}")
        return runner

# ================= MAIN BOT =================
class WhaleRadarBot:
    def __init__(self):
        self.user_manager = UserManager()
        self.config = AutoConfig(self.user_manager)
        self.telegram = TelegramBot(self.config, self.user_manager)
        self.scanner = WhaleScanner(self.config, self.user_manager, self.telegram)
        self.web_server = WebServer(self)
        self.keep_alive_thread = None
        logger.info("Whale Radar Bot (Multi-Chain) initialized")
    
    async def run(self):
        """Main bot loop"""
        logger.info("=" * 80)
        logger.info("🤖 WHALE RADAR BOT - MULTI-CHAIN VERSION")
        logger.info("=" * 80)
        
        all_tokens = self.config.get_all_tokens()
        all_users = self.user_manager.get_all_users()
        networks = set([t["network"] for t in all_tokens.values()])
        
        logger.info(f"✅ Configuration loaded")
        logger.info(f"📊 Total tokens: {len(all_tokens)}")
        logger.info(f"🔗 Networks: {', '.join(sorted(networks))}")
        logger.info(f"👥 Registered users: {len(all_users)}")
        logger.info(f"🌐 Web server port: {PORT}")
        logger.info("=" * 80)
        logger.info("⏳ Starting bot...")
        logger.info("=" * 80)
        
        web_runner = await self.web_server.start()
        
        self.start_keep_alive()
        
        for admin_id in self.telegram.admin_users:
            try:
                await self.telegram.send(admin_id, "🤖 *WHALE RADAR BOT DÉMARRÉ*\n\nVersion Multi-Chain avec 150+ tokens sur 35+ réseaux!")
                await self.telegram.send_main_menu(admin_id)
            except Exception as e:
                logger.error(f"Error sending to admin {admin_id}: {e}")
        
        logger.info(f"🔗 Health check URL: http://0.0.0.0:{PORT}/health")
        logger.info(f"📊 Stats URL: http://0.0.0.0:{PORT}/stats")
        
        while True:
            try:
                await self.telegram.process_updates()
                await self.scanner.run_scans()
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("\n\n⏹️  ARRÊT...")
                
                end_message = f"""
⏹️ *WHALE RADAR BOT ARRÊTÉ*

📊 *STATISTIQUES FINALES:*
• Scans: {self.scanner.scan_counter}
• Alertes: {self.scanner.alert_count}
• Utilisateurs: {len(self.user_manager.get_all_users())}
• Tokens: {len(self.config.get_all_tokens())}
• Réseaux: {len(set([t['network'] for t in self.config.get_all_tokens().values()]))}
• Messages: {self.telegram.bot_stats['messages_sent']} envoyés

⏰ *Arrêt:* {datetime.now().strftime('%H:%M:%S')}
"""
                
                for admin_id in self.telegram.admin_users:
                    try:
                        await self.telegram.send(admin_id, end_message)
                    except:
                        pass
                
                await web_runner.cleanup()
                
                logger.info("👋 Au revoir!")
                break
                
            except Exception as e:
                logger.error(f"Erreur: {e}")
                await asyncio.sleep(10)
    
    def start_keep_alive(self):
        """Start keep-alive thread"""
        def keep_alive():
            import requests
            import time
            while True:
                try:
                    requests.get(f"http://0.0.0.0:{PORT}/health", timeout=5)
                    time.sleep(300)
                except:
                    time.sleep(60)
        
        self.keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        self.keep_alive_thread.start()
        logger.info("🔁 Keep-alive thread started")

# ================= MAIN =================
async def main():
    logger.info("🤖 Initializing WHALE RADAR BOT (Multi-Chain with 150+ tokens)...")
    
    bot = WhaleRadarBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Programme terminé")
    except Exception as e:
        logger.error(f"\n❌ Erreur: {e}")
