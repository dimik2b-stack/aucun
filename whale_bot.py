import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Set, Optional
import logging
from aiohttp import web
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whale_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8547895751:AAFupdZqD0yVDhmdZ2AgIqnzhvDfdfXU7Ns"
CONFIG_FILE = "whale_config_multi_chain.json"
USER_SETTINGS_DIR = "user_settings"
PORT = int(os.environ.get("PORT", 8080))

# ================= COMPLETE TOKENS LIST (MULTI-CHAIN) =================
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
    
    # ========== CHAINLINK (MULTI-CHAIN) ==========
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
    "LINK-POLY": {
        "network": "polygon",
        "address": "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
        "threshold_usd": 100000,
        "category": "oracle",
        "decimals": 18,
        "api_source": "polygonscan",
        "display_name": "Chainlink (Polygon)"
    },
    "LINK-ARB": {
        "network": "arbitrum",
        "address": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
        "threshold_usd": 100000,
        "category": "oracle",
        "decimals": 18,
        "api_source": "arbiscan",
        "display_name": "Chainlink (Arbitrum)"
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
    
    # ========== SHIBA INU (MULTI-CHAIN) ==========
    "SHIB-ETH": {
        "network": "ethereum",
        "address": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
        "threshold_usd": 50000,
        "category": "memecoin",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Shiba Inu (Ethereum)"
    },
    "SHIB-BSC": {
        "network": "bsc",
        "address": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
        "threshold_usd": 50000,
        "category": "memecoin",
        "decimals": 18,
        "api_source": "bscscan",
        "display_name": "Shiba Inu (BSC)"
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
    
    # ========== WRAPPED BITCOIN (MULTI-CHAIN) ==========
    "WBTC-ETH": {
        "network": "ethereum",
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "threshold_usd": 500000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "ethplorer",
        "display_name": "Wrapped Bitcoin (Ethereum)"
    },
    "WBTC-ARB": {
        "network": "arbitrum",
        "address": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        "threshold_usd": 500000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "arbiscan",
        "display_name": "Wrapped Bitcoin (Arbitrum)"
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
    
    # ========== RENDER (MULTI-CHAIN) ==========
    "RNDR-ETH": {
        "network": "ethereum",
        "address": "0x6De037ef9aD2725EB40118Bb1702EBb27e4Aeb24",
        "threshold_usd": 30000,
        "category": "ai",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Render (Ethereum)"
    },
    "RNDR-SOL": {
        "network": "solana",
        "address": "7pjgo5NqZyZb6gQpN96CB2muBgqsSVqSogn8CA9D2R",
        "threshold_usd": 30000,
        "category": "ai",
        "decimals": 9,
        "api_source": "birdeye",
        "display_name": "Render (Solana)"
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
    
    # ========== GALA (MULTI-CHAIN) ==========
    "GALA-ETH": {
        "network": "ethereum",
        "address": "0xd1d2Eb1B1e90B638588728b4130137D262C87cae",
        "threshold_usd": 20000,
        "category": "gaming",
        "decimals": 8,
        "api_source": "ethplorer",
        "display_name": "Gala (Ethereum)"
    },
    "GALA-BSC": {
        "network": "bsc",
        "address": "0x7ddee176f665cd201f93eede625770e2fd911990",
        "threshold_usd": 20000,
        "category": "gaming",
        "decimals": 8,
        "api_source": "bscscan",
        "display_name": "Gala (BSC)"
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
    
    # ========== CELSIUS ==========
    "CEL": {
        "network": "ethereum",
        "address": "0xd8912C10681D8B21Fd3742244f44658dBA12264E",
        "threshold_usd": 20000,
        "category": "lending",
        "decimals": 8,
        "api_source": "ethplorer",
        "display_name": "Celsius"
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
    
    # ========== ICON ==========
    "ICX": {
        "network": "icon",
        "address": "",
        "threshold_usd": 15000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "ICON"
    },
    
    # ========== NANO ==========
    "NANO": {
        "network": "nano",
        "address": "",
        "threshold_usd": 10000,
        "category": "payment",
        "decimals": 6,
        "api_source": "coingecko",
        "display_name": "Nano"
    },
    
    # ========== RAVENCOIN ==========
    "RVN": {
        "network": "ravencoin",
        "address": "",
        "threshold_usd": 10000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Ravencoin"
    },
    
    # ========== ONTOLOGY ==========
    "ONT": {
        "network": "ontology",
        "address": "",
        "threshold_usd": 10000,
        "category": "layer1",
        "decimals": 8,
        "api_source": "coingecko",
        "display_name": "Ontology"
    },
    
    # ========== HARMONY ==========
    "HARMONY": {
        "network": "harmony",
        "address": "",
        "threshold_usd": 10000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Harmony"
    },
    
    # ========== REN ==========
    "REN": {
        "network": "ethereum",
        "address": "0x408e41876cCCDC0F92210600ef50372656052a38",
        "threshold_usd": 15000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Ren"
    },
    
    # ========== 0X PROTOCOL ==========
    "0X": {
        "network": "ethereum",
        "address": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
        "threshold_usd": 15000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "0x Protocol"
    },
    
    # ========== ENJIN ==========
    "ENJ": {
        "network": "ethereum",
        "address": "0xF629cBd94d3791C9250152BD8dFbDF380E2a3B9c",
        "threshold_usd": 15000,
        "category": "gaming",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Enjin Coin"
    },
    
    # ========== CHILIZ ==========
    "CHZ": {
        "network": "ethereum",
        "address": "0x3506424f91fd33084466f402D5C8C09A0E5c4B91",
        "threshold_usd": 15000,
        "category": "sports",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Chiliz"
    },
    
    # ========== STORJ ==========
    "STORJ": {
        "network": "ethereum",
        "address": "0xB64ef51C888972c908CFacf59B47C1AfBC0Ab8aC",
        "threshold_usd": 10000,
        "category": "storage",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Storj"
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
    
    # ========== KUSAMA ==========
    "KSM": {
        "network": "kusama",
        "address": "",
        "threshold_usd": 15000,
        "category": "layer0",
        "decimals": 12,
        "api_source": "coingecko",
        "display_name": "Kusama"
    },
    
    # ========== CELO ==========
    "CELO": {
        "network": "celo",
        "address": "",
        "threshold_usd": 15000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Celo"
    },
    
    # ========== NERVOS ==========
    "NERVOS": {
        "network": "nervos",
        "address": "",
        "threshold_usd": 10000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Nervos Network"
    },
    
    # ========== KYBER NETWORK ==========
    "KNC": {
        "network": "ethereum",
        "address": "0xdefa4e8a7bcba345f687a2f1456f5edd9ce97202",
        "threshold_usd": 10000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Kyber Network"
    },
    
    # ========== ARAGON ==========
    "ANT": {
        "network": "ethereum",
        "address": "0x960b236A07cf122663c4303350609A66A7B288C0",
        "threshold_usd": 10000,
        "category": "governance",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Aragon"
    },
    
    # ========== QTUM ==========
    "QTUM": {
        "network": "qtum",
        "address": "",
        "threshold_usd": 15000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Qtum"
    },
    
    # ========== COMPOUND ==========
    "COMP": {
        "network": "ethereum",
        "address": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Compound"
    },
    
    # ========== AXIE INFINITY ==========
    "AXS": {
        "network": "ethereum",
        "address": "0xf5b0f3c0a2f8ee1be2c4e0f9f9a3f3f1d3c0c0c0",
        "threshold_usd": 20000,
        "category": "gaming",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Axie Infinity"
    },
    
    # ========== FLOW ==========
    "FLOW": {
        "network": "flow",
        "address": "",
        "threshold_usd": 20000,
        "category": "layer1",
        "decimals": 18,
        "api_source": "coingecko",
        "display_name": "Flow"
    },
    
    # ========== SYNTHETIX ==========
    "SNX": {
        "network": "ethereum",
        "address": "0xC011A72400E58ecD99Ee497CF89E3775d4bd732F",
        "threshold_usd": 30000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Synthetix"
    },
    
    # ========== BALANCER ==========
    "BAL": {
        "network": "ethereum",
        "address": "0xba100000625a3754423978a60c9317c58a424e3D",
        "threshold_usd": 15000,
        "category": "defi",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Balancer"
    },
    
    # ========== ORCHID ==========
    "OXT": {
        "network": "ethereum",
        "address": "0x4575f41308ec1483f3d399aa9a2826d74da13deb",
        "threshold_usd": 10000,
        "category": "privacy",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "Orchid"
    },
    
    # ========== OMG NETWORK ==========
    "OMG": {
        "network": "ethereum",
        "address": "0xd26114cd6EE289AccF82350c8d8487fedB8A0C07",
        "threshold_usd": 15000,
        "category": "layer2",
        "decimals": 18,
        "api_source": "ethplorer",
        "display_name": "OMG Network"
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
    "icon": {
        "name": "ICON",
        "explorer": "https://tracker.icon.community",
        "api_base": "https://api.icon.community",
        "volume_metric": "large_transactions"
    },
    "nano": {
        "name": "Nano",
        "explorer": "https://nanocrawler.cc",
        "api_base": "https://api.nanocrawler.cc",
        "volume_metric": "large_transactions"
    },
    "ravencoin": {
        "name": "Ravencoin",
        "explorer": "https://ravencoin.network",
        "api_base": "https://api.ravencoin.org",
        "volume_metric": "large_transactions"
    },
    "ontology": {
        "name": "Ontology",
        "explorer": "https://explorer.ont.io",
        "api_base": "https://explorer.ont.io/api",
        "volume_metric": "large_transactions"
    },
    "harmony": {
        "name": "Harmony",
        "explorer": "https://explorer.harmony.one",
        "api_base": "https://api.harmony.one",
        "volume_metric": "large_transactions"
    },
    "arweave": {
        "name": "Arweave",
        "explorer": "https://viewblock.io/arweave",
        "api_base": "https://arweave.net",
        "volume_metric": "large_transactions"
    },
    "kusama": {
        "name": "Kusama",
        "explorer": "https://kusama.subscan.io",
        "api_base": "https://kusama.api.subscan.io",
        "volume_metric": "large_transfers"
    },
    "celo": {
        "name": "Celo",
        "explorer": "https://explorer.celo.org",
        "api_base": "https://explorer.celo.org/api",
        "volume_metric": "large_transfers"
    },
    "nervos": {
        "name": "Nervos",
        "explorer": "https://explorer.nervos.org",
        "api_base": "https://api.explorer.nervos.org",
        "volume_metric": "large_transactions"
    },
    "qtum": {
        "name": "Qtum",
        "explorer": "https://qtum.info",
        "api_base": "https://qtum.info/api",
        "volume_metric": "large_transactions"
    },
    "flow": {
        "name": "Flow",
        "explorer": "https://flowscan.org",
        "api_base": "https://api.flowscan.org",
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
        
        # DEFAULT: No tokens enabled initially - user must select
        default_settings = {
            "chat_id": chat_id,
            "enabled_tokens": [],  # Empty by default - user must select
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
            "onboarding_complete": False  # New users need to select tokens first
        }
        
        # Save default settings
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
                chat_id = filename[5:-5]  # Remove 'user_' and '.json'
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
        
        # Create new config
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
        
        # Convert sets to lists for JSON serialization
        for network in stats:
            stats[network]["categories"] = list(stats[network]["categories"])
        
        return stats
    
    def add_token(self, symbol: str, token_info: dict):
        """Add a new token to configuration"""
        if "tokens" not in self.config:
            self.config["tokens"] = {}
        
        self.config["tokens"][symbol] = token_info
        self.save_config()
        logger.info(f"Token {symbol} added to config")
    
    def update_token_threshold(self, symbol: str, threshold: int):
        """Update token threshold"""
        if "tokens" in self.config and symbol in self.config["tokens"]:
            self.config["tokens"][symbol]["threshold_usd"] = threshold
            self.save_config()
            logger.info(f"Threshold for {symbol} updated to ${threshold:,}")
            return True
        return False
    
    def remove_token(self, symbol: str):
        """Remove a token from configuration"""
        if "tokens" in self.config and symbol in self.config["tokens"]:
            del self.config["tokens"][symbol]
            self.save_config()
            logger.info(f"Token {symbol} removed from config")
            return True
        return False

# ================= TELEGRAM BOT =================
class TelegramBot:
    def __init__(self, config_manager: AutoConfig, user_manager: UserManager):
        self.token = TELEGRAM_BOT_TOKEN
        self.url = f"https://api.telegram.org/bot{self.token}"
        self.config = config_manager
        self.user_manager = user_manager
        self.last_update_id = 0
        self.waiting_for_threshold = {}  # chat_id -> symbol
        self.bot_stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "commands_processed": 0,
            "alerts_sent": 0,
            "users_growth": [],
            "start_time": datetime.now().isoformat()
        }
        
        # Dictionnaire pour suivre les derniers messages avec menus
        self.last_menu_message_id = {}  # chat_id -> message_id
        self.last_alert_message_id = {}  # chat_id -> message_id (pour les alertes)
        
        # Network icons
        self.network_icons = {
            "bitcoin": "₿",
            "ethereum": "Ξ",
            "xrp": "✕",
            "cardano": "₳",
            "avalanche": "❄",
            "dogecoin": "Ð",
            "tron": "₮",
            "ton": "₸",
            "bsc": "ⓑ",
            "polygon": "⬡",
            "solana": "◎",
            "arbitrum": "⟁",
            "optimism": "Ⓞ",
            "polkadot": "●",
            "cosmos": "⚛",
            "near": "Ⓝ",
            "aptos": "Ⓐ",
            "injective": "ⓘ",
            "internet_computer": "ⓘ",
            "ethereum_classic": "ξ",
            "litecoin": "Ł",
            "bitcoin_cash": "Ƀ",
            "stellar": "✶",
            "filecoin": "⨎",
            "hedera": "ℏ",
            "vechain": "Ⓥ",
            "algorand": "ⓐ",
            "fantom": "ⓕ",
            "theta": "θ",
            "zilliqa": "Ⓩ",
            "icon": "ⓘ",
            "nano": "ⓝ",
            "ravencoin": "ⓡ",
            "ontology": "ⓞ",
            "harmony": "ⓗ",
            "arweave": "ⓐ",
            "kusama": "ⓚ",
            "celo": "ⓒ",
            "nervos": "ⓝ",
            "qtum": "ⓠ",
            "flow": "ⓕ",
            "base": "🅱",
            "other": "🔗"
        }
        
        # Network names in different languages
        self.network_names = {
            "fr": {
                "bitcoin": "Bitcoin",
                "ethereum": "Ethereum",
                "xrp": "XRP",
                "cardano": "Cardano",
                "avalanche": "Avalanche",
                "dogecoin": "Dogecoin",
                "tron": "Tron",
                "ton": "Toncoin",
                "bsc": "Binance Smart Chain",
                "polygon": "Polygon",
                "solana": "Solana",
                "arbitrum": "Arbitrum",
                "optimism": "Optimism",
                "polkadot": "Polkadot",
                "cosmos": "Cosmos",
                "near": "Near Protocol",
                "aptos": "Aptos",
                "injective": "Injective",
                "internet_computer": "Internet Computer",
                "ethereum_classic": "Ethereum Classic",
                "litecoin": "Litecoin",
                "bitcoin_cash": "Bitcoin Cash",
                "stellar": "Stellar",
                "filecoin": "Filecoin",
                "hedera": "Hedera",
                "vechain": "VeChain",
                "algorand": "Algorand",
                "fantom": "Fantom",
                "theta": "Theta Network",
                "zilliqa": "Zilliqa",
                "icon": "ICON",
                "nano": "Nano",
                "ravencoin": "Ravencoin",
                "ontology": "Ontology",
                "harmony": "Harmony",
                "arweave": "Arweave",
                "kusama": "Kusama",
                "celo": "Celo",
                "nervos": "Nervos",
                "qtum": "Qtum",
                "flow": "Flow",
                "base": "Base",
                "other": "Autre"
            },
            "en": {
                "bitcoin": "Bitcoin",
                "ethereum": "Ethereum",
                "xrp": "XRP",
                "cardano": "Cardano",
                "avalanche": "Avalanche",
                "dogecoin": "Dogecoin",
                "tron": "Tron",
                "ton": "Toncoin",
                "bsc": "Binance Smart Chain",
                "polygon": "Polygon",
                "solana": "Solana",
                "arbitrum": "Arbitrum",
                "optimism": "Optimism",
                "polkadot": "Polkadot",
                "cosmos": "Cosmos",
                "near": "Near Protocol",
                "aptos": "Aptos",
                "injective": "Injective",
                "internet_computer": "Internet Computer",
                "ethereum_classic": "Ethereum Classic",
                "litecoin": "Litecoin",
                "bitcoin_cash": "Bitcoin Cash",
                "stellar": "Stellar",
                "filecoin": "Filecoin",
                "hedera": "Hedera",
                "vechain": "VeChain",
                "algorand": "Algorand",
                "fantom": "Fantom",
                "theta": "Theta Network",
                "zilliqa": "Zilliqa",
                "icon": "ICON",
                "nano": "Nano",
                "ravencoin": "Ravencoin",
                "ontology": "Ontology",
                "harmony": "Harmony",
                "arweave": "Arweave",
                "kusama": "Kusama",
                "celo": "Celo",
                "nervos": "Nervos",
                "qtum": "Qtum",
                "flow": "Flow",
                "base": "Base",
                "other": "Other"
            }
        }
        
        # Language dictionaries - COMPLETE TRANSLATION
        self.texts = {
            "fr": {
                # Main menu
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
                "user": "Utilisateur",
                "configure_alert_levels": "Configurez les niveaux d'alerte à recevoir",
                "threshold_multiple": "multiple du seuil",
                "select_language": "Sélectionnez votre langue",
                "select_option": "Sélectionnez une option",
                "current_threshold": "Seuil actuel",
                "send_new_threshold": "Envoyez le nouveau seuil en USD",
                "example": "Exemple",
                "minimum": "Minimum",
                "by_network": "Par réseau",
                "by_category": "Par catégorie",
                "total_threshold": "Total seuil",
                "average_threshold": "Moyenne seuil",
                "top_5_thresholds": "Top 5 seuils",
                "tokens": "tokens",
                "select_token_change_threshold": "Sélectionnez un token pour modifier son seuil",
                "global_stats": "Statistiques globales",
                "user_list": "Liste utilisateurs",
                "force_rescan": "Forcer re-scan",
                "broadcast": "Diffuser message",
                "admin_options": "Options d'administration",
                "total_users": "Utilisateurs totaux",
                "tokens_configured": "Tokens configurés",
                
                # Onboarding
                "onboarding_welcome": "🎉 *BIENVENUE SUR WHALE RADAR!*\n\nSélectionnez les tokens que vous souhaitez surveiller:",
                "onboarding_instructions": "Cliquez sur les tokens pour les activer/désactiver.\n✅ = Activé | ❌ = Désactivé",
                "onboarding_complete": "✅ *CONFIGURATION TERMINÉE!*\n\nVous surveillez maintenant {count} tokens.\nVous recevrez des alertes pour les grosses transactions.\n\nUtilisez /menu pour accéder aux autres options.",
                "onboarding_continue": "Continuez la sélection ou cliquez sur Terminer pour commencer.",
                "finish": "🚀 Terminer",
                
                # Token management
                "token_selection": "🎯 *SÉLECTION DES TOKENS*\n\nChoisissez les tokens à surveiller:",
                "tokens_enabled": "✅ {count} tokens activés",
                "tokens_disabled": "❌ {count} tokens désactivés",
                "filter_by_network": "🔗 Filtrer par réseau",
                "filter_by_category": "📊 Filtrer par catégorie",
                
                # Networks
                "networks_menu": "🔗 *SÉLECTION DES RÉSEAUX*\n\nChoisissez les réseaux à surveiller:",
                "network_enabled": "✅ {network} activé",
                "network_disabled": "❌ {network} désactivé",
                "select_network_view": "Sélectionnez un réseau pour voir ses tokens:",
                
                # Categories
                "categories": {
                    "layer1": "🏗️ Layer 1",
                    "layer2": "🔷 Layer 2",
                    "layer0": "🌐 Layer 0",
                    "stablecoin": "💵 Stablecoin",
                    "defi": "🔄 DeFi",
                    "memecoin": "🐸 Memecoin",
                    "oracle": "🔮 Oracle",
                    "payment": "💳 Payment",
                    "gaming": "🎮 Gaming",
                    "ai": "🤖 AI",
                    "storage": "💾 Storage",
                    "lending": "🏦 Lending",
                    "governance": "🏛️ Governance",
                    "sports": "⚽ Sports",
                    "privacy": "🕵️ Privacy",
                    "other": "📦 Autre"
                },
                
                # Stats
                "user_stats": "👤 Statistiques Utilisateur",
                "total_tokens": "Tokens totaux",
                "enabled_tokens": "Tokens activés",
                "active_networks": "Réseaux actifs",
                "total_alerts": "Alertes reçues",
                
                # Alerts
                "alert_mega": "🐋 MÉGA WHALE (20x+)",
                "alert_huge": "🐳 WHALE ÉNORME (10-20x)",
                "alert_large": "🐬 GROSSE WHALE (5-10x)",
                "alert_whale": "🐟 WHALE (2-5x)",
                "alert_significant": "🦈 GROSSE ACTIVITÉ (1-2x)",
                
                # Settings
                "change_language": "Changer la langue",
                "toggle_network_icons": "Afficher les icônes réseau",
                "reset_settings": "Réinitialiser les paramètres",
                
                # Messages
                "no_tokens_selected": "⚠️ *AUCUN TOKEN SÉLECTIONNÉ*\n\nVous devez sélectionner au moins un token pour recevoir des alertes.\n\nUtilisez 'Sélectionner Tokens' pour choisir vos tokens.",
                "scan_started": "🔍 Scan démarré pour {count} tokens",
                "alert_received": "🚨 Nouvelle alerte reçue",
                "token_added": "✅ Token ajouté",
                "token_removed": "❌ Token supprimé",
                "settings_saved": "✅ Paramètres sauvegardés"
            },
            "en": {
                # Main menu
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
                "user": "User",
                "configure_alert_levels": "Configure alert levels to receive",
                "threshold_multiple": "threshold multiple",
                "select_language": "Select your language",
                "select_option": "Select an option",
                "current_threshold": "Current threshold",
                "send_new_threshold": "Send the new threshold in USD",
                "example": "Example",
                "minimum": "Minimum",
                "by_network": "By network",
                "by_category": "By category",
                "total_threshold": "Total threshold",
                "average_threshold": "Average threshold",
                "top_5_thresholds": "Top 5 thresholds",
                "tokens": "tokens",
                "select_token_change_threshold": "Select a token to change its threshold",
                "global_stats": "Global statistics",
                "user_list": "User list",
                "force_rescan": "Force re-scan",
                "broadcast": "Broadcast message",
                "admin_options": "Admin options",
                "total_users": "Total users",
                "tokens_configured": "Tokens configured",
                
                # Onboarding
                "onboarding_welcome": "🎉 *WELCOME TO WHALE RADAR!*\n\nSelect the tokens you want to monitor:",
                "onboarding_instructions": "Click on tokens to enable/disable them.\n✅ = Enabled | ❌ = Disabled",
                "onboarding_complete": "✅ *SETUP COMPLETE!*\n\nYou are now monitoring {count} tokens.\nYou will receive alerts for large transactions.\n\nUse /menu to access other options.",
                "onboarding_continue": "Continue selecting or click Finish to start.",
                "finish": "🚀 Finish",
                
                # Token management
                "token_selection": "🎯 *TOKEN SELECTION*\n\nChoose tokens to monitor:",
                "tokens_enabled": "✅ {count} tokens enabled",
                "tokens_disabled": "❌ {count} tokens disabled",
                "filter_by_network": "🔗 Filter by network",
                "filter_by_category": "📊 Filter by category",
                
                # Networks
                "networks_menu": "🔗 *NETWORK SELECTION*\n\nChoose networks to monitor:",
                "network_enabled": "✅ {network} enabled",
                "network_disabled": "❌ {network} disabled",
                "select_network_view": "Select a network to view its tokens:",
                
                # Categories
                "categories": {
                    "layer1": "🏗️ Layer 1",
                    "layer2": "🔷 Layer 2",
                    "layer0": "🌐 Layer 0",
                    "stablecoin": "💵 Stablecoin",
                    "defi": "🔄 DeFi",
                    "memecoin": "🐸 Memecoin",
                    "oracle": "🔮 Oracle",
                    "payment": "💳 Payment",
                    "gaming": "🎮 Gaming",
                    "ai": "🤖 AI",
                    "storage": "💾 Storage",
                    "lending": "🏦 Lending",
                    "governance": "🏛️ Governance",
                    "sports": "⚽ Sports",
                    "privacy": "🕵️ Privacy",
                    "other": "📦 Other"
                },
                
                # Stats
                "user_stats": "👤 User Statistics",
                "total_tokens": "Total tokens",
                "enabled_tokens": "Enabled tokens",
                "active_networks": "Active networks",
                "total_alerts": "Alerts received",
                
                # Alerts
                "alert_mega": "🐋 MEGA WHALE (20x+)",
                "alert_huge": "🐳 HUGE WHALE (10-20x)",
                "alert_large": "🐬 LARGE WHALE (5-10x)",
                "alert_whale": "🐟 WHALE (2-5x)",
                "alert_significant": "🦈 BIG ACTIVITY (1-2x)",
                
                # Settings
                "change_language": "Change language",
                "toggle_network_icons": "Show network icons",
                "reset_settings": "Reset settings",
                
                # Messages
                "no_tokens_selected": "⚠️ *NO TOKENS SELECTED*\n\nYou need to select at least one token to receive alerts.\n\nUse 'Select Tokens' to choose your tokens.",
                "scan_started": "🔍 Scan started for {count} tokens",
                "alert_received": "🚨 New alert received",
                "token_added": "✅ Token added",
                "token_removed": "❌ Token removed",
                "settings_saved": "✅ Settings saved"
            }
        }
        
        # Admin users
        self.admin_users = ["7546736501"]
        logger.info("Telegram Bot initialized")
    
    def get_text(self, key: str, lang: str = "fr") -> str:
        """Get translated text"""
        if key in self.texts.get(lang, {}):
            return self.texts[lang][key]
        elif key in self.texts.get("fr", {}):
            return self.texts["fr"][key]
        return key
    
    def get_category_text(self, category: str, lang: str = "fr") -> str:
        """Get translated category name"""
        categories = self.texts.get(lang, {}).get("categories", {})
        return categories.get(category, category.capitalize())
    
    def get_network_icon(self, network: str) -> str:
        """Get network icon"""
        return self.network_icons.get(network, self.network_icons["other"])
    
    def get_network_name(self, network: str, lang: str = "fr") -> str:
        """Get translated network name"""
        return self.network_names.get(lang, {}).get(network, network.capitalize())
    
    def get_user_lang(self, chat_id: str) -> str:
        """Get user language"""
        user_settings = self.user_manager.get_user(chat_id)
        return user_settings.get("language", "fr")
    
    async def send(self, chat_id: str, text: str, reply_markup=None, edit_menu: bool = True, is_alert: bool = False):
        """Send or edit message to Telegram"""
        try:
            # Pour les alertes, on garde tous les messages
            if is_alert:
                self.last_alert_message_id[chat_id] = time.time()
                return await self._send_new_message(chat_id, text, reply_markup)
            
            # Pour les menus, on édite le dernier message si possible
            if edit_menu and chat_id in self.last_menu_message_id:
                message_id = self.last_menu_message_id[chat_id]
                
                payload = {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }
                if reply_markup:
                    payload["reply_markup"] = reply_markup
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.url}/editMessageText", json=payload, timeout=10) as resp:
                        if resp.status == 200:
                            self.bot_stats["messages_sent"] += 1
                            return True
                        else:
                            # Si l'édition échoue, on envoie un nouveau message
                            error_text = await resp.text()
                            logger.warning(f"Edit failed for {chat_id}: {error_text}, sending new message")
                            return await self._send_new_message(chat_id, text, reply_markup)
            
            # Sinon, envoyer un nouveau message
            return await self._send_new_message(chat_id, text, reply_markup)
            
        except Exception as e:
            logger.error(f"Telegram send error for {chat_id}: {e}")
            return False
    
    async def _send_new_message(self, chat_id: str, text: str, reply_markup=None):
        """Send new message to Telegram"""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.url}/sendMessage", json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        if "result" in response_data and "message_id" in response_data["result"]:
                            self.last_menu_message_id[chat_id] = response_data["result"]["message_id"]
                        
                        self.bot_stats["messages_sent"] += 1
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"Telegram API error: {resp.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Telegram send error for {chat_id}: {e}")
            return False
    
    async def send_main_menu(self, chat_id: str):
        """Send main menu to user"""
        user_settings = self.user_manager.get_user(chat_id)
        user_tokens = self.config.get_tokens_for_user(chat_id)
        user_lang = self.get_user_lang(chat_id)
        
        # Check if user needs to select tokens first
        if not user_settings.get("onboarding_complete", False) or len(user_tokens) == 0:
            await self.send_onboarding_menu(chat_id, first_time=True)
            return
        
        menu_text = f"{self.get_text('welcome', user_lang)}\n\n"
        menu_text += f"👤 *{self.get_text('user', user_lang)}:* {chat_id[:8]}...\n"
        menu_text += f"📊 *STATUS:* {len(user_tokens)} {self.get_text('enabled_tokens', user_lang).lower()}\n"
        menu_text += f"🌍 *LANGUAGE:* {'Français' if user_lang == 'fr' else 'English'}\n"
        
        # Show active networks
        active_networks = set()
        for token_info in user_tokens.values():
            active_networks.add(token_info.get("network", "other"))
        
        if active_networks:
            menu_text += f"🔗 *{self.get_text('active_networks', user_lang)}:* {len(active_networks)}\n"
        
        menu_text += f"\n{self.get_text('menu', user_lang)}:"
        
        keyboard_buttons = [
            [{"text": self.get_text("select_tokens", user_lang), "callback_data": "select_tokens"}],
            [{"text": self.get_text("manage_tokens", user_lang), "callback_data": "manage_tokens"}],
            [{"text": self.get_text("settings", user_lang), "callback_data": "settings"}],
            [{"text": self.get_text("stats", user_lang), "callback_data": "stats"}],
            [{"text": self.get_text("list_tokens", user_lang), "callback_data": "list_tokens"}]
        ]
        
        # Add admin button for admin users
        if chat_id in self.admin_users:
            keyboard_buttons.append([{"text": self.get_text("admin", user_lang), "callback_data": "admin_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, menu_text, keyboard)
    
    async def send_onboarding_menu(self, chat_id: str, first_time: bool = False, page: int = 0):
        """Send onboarding/token selection menu"""
        user_lang = self.get_user_lang(chat_id)
        user_settings = self.user_manager.get_user(chat_id)
        enabled_tokens = user_settings.get("enabled_tokens", [])
        
        if first_time:
            text = f"{self.get_text('onboarding_welcome', user_lang)}\n\n"
        else:
            text = f"{self.get_text('token_selection', user_lang)}\n\n"
        
        text += f"{self.get_text('onboarding_instructions', user_lang)}\n\n"
        
        # Get all tokens grouped by network
        all_tokens = self.config.get_all_tokens()
        networks = {}
        for symbol, info in all_tokens.items():
            network = info.get("network", "other")
            if network not in networks:
                networks[network] = []
            networks[network].append((symbol, info))
        
        # Sort networks by name
        sorted_networks = sorted(networks.items(), key=lambda x: x[0])
        
        # Pagination: show 2 networks per page
        networks_per_page = 2
        total_pages = (len(sorted_networks) + networks_per_page - 1) // networks_per_page
        start_idx = page * networks_per_page
        end_idx = min(start_idx + networks_per_page, len(sorted_networks))
        
        # Display networks for current page
        for network, tokens in sorted_networks[start_idx:end_idx]:
            network_name = self.get_network_name(network, user_lang)
            network_icon = self.get_network_icon(network)
            
            text += f"\n{network_icon} *{network_name}* ({len(tokens)} tokens)\n"
            
            # Sort tokens alphabetically
            sorted_tokens = sorted(tokens, key=lambda x: x[0])
            
            for symbol, info in sorted_tokens:
                status = "✅" if symbol in enabled_tokens else "❌"
                threshold = info.get('threshold_usd', 0)
                display_name = info.get('display_name', symbol)
                
                text += f"{status} **{display_name}** - ${threshold:,}\n"
        
        text += f"\n📊 Page {page+1}/{total_pages}"
        text += f"\n✅ {len(enabled_tokens)} tokens sélectionnés"
        
        # Create keyboard
        keyboard_buttons = []
        
        # Token toggles (grouped by 2)
        current_network_tokens = []
        for network, tokens in sorted_networks[start_idx:end_idx]:
            current_network_tokens.extend(tokens)
        
        # Sort and create buttons
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
        
        # Bulk actions
        keyboard_buttons.append([
            {"text": self.get_text("select_all", user_lang), "callback_data": "onboarding_select_all"},
            {"text": self.get_text("deselect_all", user_lang), "callback_data": "onboarding_deselect_all"}
        ])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append({"text": self.get_text("previous", user_lang), "callback_data": f"onboarding_page_{page-1}"})
        
        nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
        
        if page < total_pages - 1:
            nav_buttons.append({"text": self.get_text("next", user_lang), "callback_data": f"onboarding_page_{page+1}"})
        
        if nav_buttons:
            keyboard_buttons.append(nav_buttons)
        
        # Finish button (only if tokens selected)
        if len(enabled_tokens) > 0:
            keyboard_buttons.append([{"text": self.get_text("finish", user_lang), "callback_data": "onboarding_finish"}])
        else:
            text += "\n\n⚠️ " + self.get_text("no_tokens_selected", user_lang)
        
        # Back button (only if not first time)
        if not first_time:
            keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, text, keyboard)
    
    async def send_token_management(self, chat_id: str, page: int = 0):
        """Send token management menu with pagination"""
        all_tokens = self.config.get_all_tokens()
        user_settings = self.user_manager.get_user(chat_id)
        enabled_tokens = user_settings.get("enabled_tokens", [])
        user_lang = self.get_user_lang(chat_id)
        
        # Sort tokens alphabetically
        sorted_tokens = sorted(all_tokens.items(), key=lambda x: x[0])
        
        # Pagination
        tokens_per_page = 15
        total_pages = (len(sorted_tokens) + tokens_per_page - 1) // tokens_per_page
        start_idx = page * tokens_per_page
        end_idx = min(start_idx + tokens_per_page, len(sorted_tokens))
        
        keyboard_buttons = []
        
        # Add tokens for current page with network icons
        for symbol, info in sorted_tokens[start_idx:end_idx]:
            status = "✅" if symbol in enabled_tokens else "❌"
            threshold = info.get('threshold_usd', 0)
            network_icon = self.get_network_icon(info.get("network", "other"))
            display_name = info.get('display_name', symbol)
            
            btn_text = f"{status} {network_icon} {display_name}"
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"toggle_{symbol}"}
            ])
        
        # Add pagination buttons if needed
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append({"text": "◀️", "callback_data": f"page_{page-1}"})
            
            nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
            
            if page < total_pages - 1:
                nav_buttons.append({"text": "▶️", "callback_data": f"page_{page+1}"})
            
            keyboard_buttons.append(nav_buttons)
        
        # Add bulk actions
        keyboard_buttons.append([
            {"text": self.get_text("enable_all", user_lang), "callback_data": "enable_all"},
            {"text": self.get_text("disable_all", user_lang), "callback_data": "disable_all"}
        ])
        
        # Add back button
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        text = f"🔔 *{self.get_text('manage_tokens', user_lang).upper()}*\n\n"
        text += f"Page {page+1}/{total_pages} - {len(sorted_tokens)} {self.get_text('tokens', user_lang)} total\n"
        text += f"Click to enable/disable:\n✅ = {self.get_text('enabled', user_lang)} | ❌ = {self.get_text('disabled', user_lang)}"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_settings_menu(self, chat_id: str):
        """Send settings menu"""
        user_lang = self.get_user_lang(chat_id)
        user_settings = self.user_manager.get_user(chat_id)
        show_icons = user_settings.get("show_network_icons", True)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": self.get_text("alert_levels", user_lang), "callback_data": "alert_levels"}],
                [{"text": self.get_text("language", user_lang), "callback_data": "language_menu"}],
                [{"text": self.get_text("threshold", user_lang), "callback_data": "change_threshold"}],
                [{"text": f"{'✅' if show_icons else '❌'} {self.get_text('toggle_network_icons', user_lang)}", 
                  "callback_data": "toggle_network_icons"}],
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        text = f"⚙️ *{self.get_text('settings', user_lang).upper()}*\n\n"
        text += f"🌍 {self.get_text('language', user_lang)}: {'Français' if user_lang == 'fr' else 'English'}\n"
        text += f"🔗 {self.get_text('toggle_network_icons', user_lang)}: {'✅ On' if show_icons else '❌ Off'}\n\n"
        text += f"{self.get_text('select_option', user_lang)}:"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_alert_levels_menu(self, chat_id: str):
        """Send alert levels configuration menu"""
        user_settings = self.user_manager.get_user(chat_id)
        alert_levels = user_settings.get("alert_levels", {})
        user_lang = self.get_user_lang(chat_id)
        
        keyboard_buttons = []
        levels = [
            ("mega", self.get_text("alert_mega", user_lang)),
            ("huge", self.get_text("alert_huge", user_lang)),
            ("large", self.get_text("alert_large", user_lang)),
            ("whale", self.get_text("alert_whale", user_lang)),
            ("significant", self.get_text("alert_significant", user_lang))
        ]
        
        for level_id, level_name in levels:
            status = "✅" if alert_levels.get(level_id, True) else "❌"
            btn_text = f"{status} {level_name}"
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"alert_{level_id}"}
            ])
        
        # Enable/Disable all alerts
        keyboard_buttons.append([
            {"text": f"✅ {self.get_text('enable_all', user_lang)}", "callback_data": "enable_all_alerts"},
            {"text": f"❌ {self.get_text('disable_all', user_lang)}", "callback_data": "disable_all_alerts"}
        ])
        
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "settings"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        text = f"🔔 *{self.get_text('alert_levels', user_lang).upper()}*\n\n"
        text += f"{self.get_text('configure_alert_levels', user_lang)}:\n"
        text += f"(x = {self.get_text('threshold_multiple', user_lang)})"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_language_menu(self, chat_id: str):
        """Send language selection menu"""
        user_lang = self.get_user_lang(chat_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🇫🇷 Français", "callback_data": "lang_fr"}],
                [{"text": "🇬🇧 English", "callback_data": "lang_en"}],
                [{"text": self.get_text("back", user_lang), "callback_data": "settings"}]
            ]
        }
        
        text = f"🌍 *{self.get_text('language', user_lang).upper()}*\n\n"
        text += f"{self.get_text('select_language', user_lang)}:"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_change_threshold_menu(self, chat_id: str, page: int = 0):
        """Send threshold change menu with pagination"""
        all_tokens = self.config.get_all_tokens()
        user_lang = self.get_user_lang(chat_id)
        
        # Sort tokens alphabetically
        sorted_tokens = sorted(all_tokens.items(), key=lambda x: x[0])
        
        # Pagination
        tokens_per_page = 15
        total_pages = (len(sorted_tokens) + tokens_per_page - 1) // tokens_per_page
        start_idx = page * tokens_per_page
        end_idx = min(start_idx + tokens_per_page, len(sorted_tokens))
        
        keyboard_buttons = []
        
        # Add tokens for current page
        for symbol, info in sorted_tokens[start_idx:end_idx]:
            threshold = info.get('threshold_usd', 0)
            network_icon = self.get_network_icon(info.get("network", "other"))
            display_name = info.get('display_name', symbol)
            
            btn_text = f"{network_icon} {display_name}: ${threshold:,}"
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"thresh_{symbol}"}
            ])
        
        # Add pagination buttons if needed
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append({"text": "◀️", "callback_data": f"thresh_page_{page-1}"})
            
            nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
            
            if page < total_pages - 1:
                nav_buttons.append({"text": "▶️", "callback_data": f"thresh_page_{page+1}"})
            
            keyboard_buttons.append(nav_buttons)
        
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "settings"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        text = f"🎯 *{self.get_text('threshold', user_lang).upper()}*\n\n"
        text += f"Page {page+1}/{total_pages}\n"
        text += f"{self.get_text('select_token_change_threshold', user_lang)}:"
        
        await self.send(chat_id, text, keyboard)
    
    async def process_callback(self, chat_id: str, callback_data: str):
        """Process callback queries from inline keyboards"""
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
                    # Disable token
                    enabled_tokens.remove(symbol)
                    status = self.get_text("disabled", user_lang)
                else:
                    # Enable token
                    enabled_tokens.append(symbol)
                    status = self.get_text("enabled", user_lang)
                
                # Update user settings
                user_settings["enabled_tokens"] = enabled_tokens
                self.user_manager.update_user(chat_id, user_settings)
                
                # Get current page from user settings or message
                # For now, just refresh the same view
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
                
                text = self.get_text("onboarding_complete", user_lang).format(count=len(enabled_tokens))
                await self.send(chat_id, text, edit_menu=False)
                await self.send_main_menu(chat_id)
            else:
                await self.send(chat_id, self.get_text("no_tokens_selected", user_lang))
        
        elif callback_data == "manage_tokens":
            await self.send_token_management(chat_id)
        
        elif callback_data.startswith("page_"):
            page = int(callback_data[5:])
            await self.send_token_management(chat_id, page)
        
        elif callback_data == "settings":
            await self.send_settings_menu(chat_id)
        
        elif callback_data == "stats":
            await self.show_stats(chat_id)
        
        elif callback_data == "list_tokens":
            await self.show_token_list(chat_id)
        
        elif callback_data == "alert_levels":
            await self.send_alert_levels_menu(chat_id)
        
        elif callback_data == "language_menu":
            await self.send_language_menu(chat_id)
        
        elif callback_data == "change_threshold":
            await self.send_change_threshold_menu(chat_id)
        
        elif callback_data.startswith("thresh_page_"):
            page = int(callback_data[12:])
            await self.send_change_threshold_menu(chat_id, page)
        
        elif callback_data.startswith("toggle_"):
            symbol = callback_data[7:]
            all_tokens = self.config.get_all_tokens()
            user_settings = self.user_manager.get_user(chat_id)
            enabled_tokens = user_settings.get("enabled_tokens", [])
            
            if symbol in all_tokens:
                if symbol in enabled_tokens:
                    # Disable token
                    enabled_tokens.remove(symbol)
                    status = f"❌ {self.get_text('disabled', user_lang)}"
                else:
                    # Enable token
                    enabled_tokens.append(symbol)
                    status = f"✅ {self.get_text('enabled', user_lang)}"
                
                # Update user settings
                user_settings["enabled_tokens"] = enabled_tokens
                self.user_manager.update_user(chat_id, user_settings)
                
                # Show notification
                await self.answer_callback(chat_id, f"{symbol} {status}")
                # Refresh current page
                await self.send_token_management(chat_id)
        
        elif callback_data == "enable_all":
            all_tokens = self.config.get_all_tokens()
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["enabled_tokens"] = list(all_tokens.keys())
            self.user_manager.update_user(chat_id, user_settings)
            await self.answer_callback(chat_id, f"✅ {self.get_text('enable_all', user_lang)}")
            await self.send_token_management(chat_id)
        
        elif callback_data == "disable_all":
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["enabled_tokens"] = []
            self.user_manager.update_user(chat_id, user_settings)
            await self.answer_callback(chat_id, f"❌ {self.get_text('disable_all', user_lang)}")
            await self.send_token_management(chat_id)
        
        elif callback_data.startswith("alert_"):
            level = callback_data[6:]
            user_settings = self.user_manager.get_user(chat_id)
            alert_levels = user_settings.get("alert_levels", {})
            current_state = alert_levels.get(level, True)
            
            alert_levels[level] = not current_state
            user_settings["alert_levels"] = alert_levels
            self.user_manager.update_user(chat_id, user_settings)
            
            status = self.get_text("enabled", user_lang) if not current_state else self.get_text("disabled", user_lang)
            await self.answer_callback(chat_id, f"Level {level}: {status}")
            await self.send_alert_levels_menu(chat_id)
        
        elif callback_data == "enable_all_alerts":
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["alert_levels"] = {
                "mega": True,
                "huge": True,
                "large": True,
                "whale": True,
                "significant": True
            }
            self.user_manager.update_user(chat_id, user_settings)
            await self.answer_callback(chat_id, f"✅ {self.get_text('enable_all', user_lang)}")
            await self.send_alert_levels_menu(chat_id)
        
        elif callback_data == "disable_all_alerts":
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["alert_levels"] = {
                "mega": False,
                "huge": False,
                "large": False,
                "whale": False,
                "significant": False
            }
            self.user_manager.update_user(chat_id, user_settings)
            await self.answer_callback(chat_id, f"❌ {self.get_text('disable_all', user_lang)}")
            await self.send_alert_levels_menu(chat_id)
        
        elif callback_data.startswith("lang_"):
            lang = callback_data[5:]
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["language"] = lang
            self.user_manager.update_user(chat_id, user_settings)
            
            lang_name = "Français" if lang == "fr" else "English"
            await self.answer_callback(chat_id, f"🌍 {self.get_text('language', lang)}: {lang_name}")
            await self.send_settings_menu(chat_id)
        
        elif callback_data == "toggle_network_icons":
            user_settings = self.user_manager.get_user(chat_id)
            current = user_settings.get("show_network_icons", True)
            user_settings["show_network_icons"] = not current
            self.user_manager.update_user(chat_id, user_settings)
            
            status = f"✅ {self.get_text('enabled', user_lang)}" if not current else f"❌ {self.get_text('disabled', user_lang)}"
            await self.answer_callback(chat_id, f"🔗 Network icons: {status}")
            await self.send_settings_menu(chat_id)
        
        elif callback_data.startswith("thresh_"):
            symbol = callback_data[7:]
            await self.ask_for_new_threshold(chat_id, symbol)
        
        elif callback_data == "admin_menu":
            if chat_id in self.admin_users:
                await self.send_admin_menu(chat_id)
        
        elif callback_data == "noop":
            pass
        
        else:
            logger.warning(f"Unknown callback data: {callback_data}")
    
    async def ask_for_new_threshold(self, chat_id: str, symbol: str):
        """Ask user for new threshold value"""
        tokens = self.config.get_all_tokens()
        if symbol in tokens:
            current = tokens[symbol]['threshold_usd']
            self.waiting_for_threshold[chat_id] = symbol
            
            user_lang = self.get_user_lang(chat_id)
            
            text = f"🎯 *{self.get_text('threshold', user_lang).upper()} - {symbol}*\n\n"
            text += f"{self.get_text('current_threshold', user_lang)}: **${current:,}**\n\n"
            text += f"{self.get_text('send_new_threshold', user_lang)}:\n"
            text += f"{self.get_text('example', user_lang)}: `100000` for $100,000\n\n"
            text += f"📝 *{self.get_text('minimum', user_lang)}:* $10,000"
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🚫 Cancel", "callback_data": "change_threshold"}]
                ]
            }
            
            await self.send(chat_id, text, keyboard)
    
    async def answer_callback(self, chat_id: str, text: str):
        """Answer callback query with notification"""
        try:
            await self.send(chat_id, f"📱 {text}", edit_menu=False)
        except Exception as e:
            logger.error(f"Error answering callback for {chat_id}: {e}")
    
    async def show_stats(self, chat_id: str):
        """Show statistics for user"""
        user_tokens = self.config.get_tokens_for_user(chat_id)
        all_tokens = self.config.get_all_tokens()
        enabled_count = len(user_tokens)
        total_count = len(all_tokens)
        
        user_lang = self.get_user_lang(chat_id)
        
        # Calculate thresholds
        total_threshold = sum(t.get('threshold_usd', 0) for t in user_tokens.values())
        avg_threshold = total_threshold / enabled_count if enabled_count > 0 else 0
        
        # Group by network
        networks = {}
        for symbol, info in user_tokens.items():
            network = info.get('network', 'other')
            networks[network] = networks.get(network, 0) + 1
        
        # Group by category
        categories = {}
        for symbol, info in user_tokens.items():
            cat = info.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        text = f"📊 *{self.get_text('user_stats', user_lang).upper()}*\n\n"
        text += f"👤 {self.get_text('user', user_lang)}: {chat_id[:8]}...\n"
        text += f"📈 {self.get_text('enabled_tokens', user_lang)}: **{enabled_count}/{total_count}**\n"
        text += f"💰 {self.get_text('total_threshold', user_lang)}: **${total_threshold:,}**\n"
        text += f"📊 {self.get_text('average_threshold', user_lang)}: **${avg_threshold:,.0f}**\n"
        text += f"🌍 {self.get_text('language', user_lang)}: **{'Français' if user_lang == 'fr' else 'English'}**\n"
        text += f"🔗 {self.get_text('active_networks', user_lang)}: **{len(networks)}**\n\n"
        
        text += f"*🔗 {self.get_text('by_network', user_lang).upper()}:*\n"
        for network, count in sorted(networks.items()):
            network_name = self.get_network_name(network, user_lang)
            text += f"• {self.get_network_icon(network)} {network_name}: {count} tokens\n"
        
        text += f"\n*📊 {self.get_text('by_category', user_lang).upper()}:*\n"
        for cat, count in sorted(categories.items()):
            cat_name = self.get_category_text(cat, user_lang)
            text += f"• {cat_name}: {count} tokens\n"
        
        # Show top 5 highest thresholds
        if user_tokens:
            top_tokens = sorted(user_tokens.items(), key=lambda x: x[1].get('threshold_usd', 0), reverse=True)[:5]
            text += f"\n*🏆 {self.get_text('top_5_thresholds', user_lang).upper()}:*\n"
            for i, (symbol, info) in enumerate(top_tokens, 1):
                threshold = info.get('threshold_usd', 0)
                network_icon = self.get_network_icon(info.get("network", "other"))
                text += f"{i}. {network_icon} **{symbol}**: ${threshold:,}\n"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def show_token_list(self, chat_id: str, page: int = 0):
        """Show list of enabled tokens with pagination"""
        user_tokens = self.config.get_tokens_for_user(chat_id)
        user_lang = self.get_user_lang(chat_id)
        
        if not user_tokens:
            text = "📭 *AUCUN TOKEN ACTIVÉ*\n\n"
            text += self.get_text("no_tokens_selected", user_lang)
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎯 " + self.get_text("select_tokens", user_lang), "callback_data": "select_tokens"}],
                    [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
                ]
            }
            
            await self.send(chat_id, text, keyboard)
            return
        
        # Sort tokens alphabetically
        sorted_tokens = sorted(user_tokens.items(), key=lambda x: x[0])
        
        # Pagination
        tokens_per_page = 20
        total_pages = (len(sorted_tokens) + tokens_per_page - 1) // tokens_per_page
        start_idx = page * tokens_per_page
        end_idx = min(start_idx + tokens_per_page, len(sorted_tokens))
        
        text = f"📋 *{self.get_text('list_tokens', user_lang).upper()}*\n\n"
        text += f"Page {page+1}/{total_pages} - {len(user_tokens)} {self.get_text('tokens', user_lang)}\n\n"
        
        # Group by network for current page
        page_tokens = sorted_tokens[start_idx:end_idx]
        by_network = {}
        
        for symbol, info in page_tokens:
            network = info.get('network', 'other')
            if network not in by_network:
                by_network[network] = []
            by_network[network].append((symbol, info))
        
        for network, token_list in sorted(by_network.items()):
            network_name = self.get_network_name(network, user_lang)
            network_icon = self.get_network_icon(network)
            text += f"*{network_icon} {network_name}* ({len(token_list)})\n"
            
            for symbol, info in token_list:
                threshold = info.get('threshold_usd', 0)
                display_name = info.get('display_name', symbol)
                category = self.get_category_text(info.get('category', 'other'), user_lang)
                
                text += f"• **{display_name}**: ${threshold:,} ({category})\n"
            
            text += "\n"
        
        # Add pagination buttons if needed
        keyboard_buttons = []
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append({"text": "◀️ " + self.get_text("previous", user_lang), "callback_data": f"list_page_{page-1}"})
            
            nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
            
            if page < total_pages - 1:
                nav_buttons.append({"text": self.get_text("next", user_lang) + " ▶️", "callback_data": f"list_page_{page+1}"})
            
            keyboard_buttons.append(nav_buttons)
        
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, text, keyboard)
    
    async def send_add_token_instructions(self, chat_id: str):
        """Send instructions for adding a token"""
        user_lang = self.get_user_lang(chat_id)
        
        text = "➕ *AJOUTER UN TOKEN*\n\n"
        text += "Pour ajouter un nouveau token:\n\n"
        text += "1. Envoyez la commande:\n"
        text += "`/add RÉSEAU ADRESSE SEUIL_USD`\n\n"
        text += "2. Exemple pour Ethereum:\n"
        text += "`/add ethereum 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 50000`\n\n"
        text += "3. Réseaux supportés: bitcoin, ethereum, xrp, cardano, avalanche, solana, bsc, polygon, arbitrum, optimism, etc.\n\n"
        text += "4. Le bot détectera automatiquement:\n"
        text += "   • Symbole\n"
        text += "   • Nombre de décimales\n"
        text += "   • Catégorie\n\n"
        text += "📝 *Note:* Le token sera automatiquement activé pour vous."
        
        keyboard = {
            "inline_keyboard": [
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def handle_add_token(self, chat_id: str, network: str, address: str, threshold_str: str):
        """Handle token addition"""
        try:
            threshold = int(threshold_str)
            
            if threshold < 10000:
                await self.send(chat_id, "⚠️ *Seuil minimum:* $10,000")
                return
            
            if network not in NETWORK_CONFIGS:
                await self.send(chat_id, f"❌ *Réseau non supporté:* {network}\n\nRéseaux supportés: {', '.join(NETWORK_CONFIGS.keys())}")
                return
            
            await self.send(chat_id, f"🔍 *Analyse du token sur {network}...*")
            
            token_info = await self.get_token_info(network, address)
            if not token_info["valid"]:
                await self.send(chat_id, f"❌ *Token non trouvé sur le réseau {network}*")
                return
            
            symbol = token_info["symbol"]
            
            # Check if token already exists
            all_tokens = self.config.get_all_tokens()
            existing_symbol = None
            for existing_sym, existing_info in all_tokens.items():
                if existing_info.get("address") == address and existing_info.get("network") == network:
                    existing_symbol = existing_sym
                    break
            
            if existing_symbol:
                await self.send(chat_id, f"⚠️ *{existing_symbol} existe déjà!*\n"
                              f"Seuil actuel: ${all_tokens[existing_symbol]['threshold_usd']:,}")
                return
            
            # Create unique symbol if needed
            base_symbol = token_info["symbol"]
            final_symbol = base_symbol
            counter = 1
            while final_symbol in all_tokens:
                final_symbol = f"{base_symbol}-{counter}"
                counter += 1
            
            # Add to config
            new_token_info = {
                "network": network,
                "address": address,
                "threshold_usd": threshold,
                "decimals": token_info["decimals"],
                "category": token_info.get("category", "other"),
                "api_source": token_info.get("api_source", "coingecko"),
                "display_name": token_info.get("name", final_symbol)
            }
            
            self.config.add_token(final_symbol, new_token_info)
            
            # Enable for this user
            user_settings = self.user_manager.get_user(chat_id)
            enabled_tokens = user_settings.get("enabled_tokens", [])
            if final_symbol not in enabled_tokens:
                enabled_tokens.append(final_symbol)
                user_settings["enabled_tokens"] = enabled_tokens
                self.user_manager.update_user(chat_id, user_settings)
            
            await self.send(chat_id, f"✅ *TOKEN AJOUTÉ*\n\n"
                          f"📛 **{final_symbol}**\n"
                          f"🔗 Réseau: **{NETWORK_CONFIGS[network]['name']}**\n"
                          f"🎯 Seuil: **${threshold:,}**\n"
                          f"🔢 Décimales: {token_info['decimals']}\n"
                          f"📊 Catégorie: {token_info.get('category', 'other')}\n"
                          f"✅ Activé automatiquement")
            
            await self.send_main_menu(chat_id)
            
        except ValueError:
            await self.send(chat_id, "❌ Format invalide\nExemple: `/add ethereum ADRESSE 50000`")
    
    async def get_token_info(self, network: str, address: str):
        """Fetch token information based on network"""
        try:
            if network == "bitcoin":
                return {
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "decimals": 8,
                    "category": "layer1",
                    "api_source": "coingecko",
                    "valid": True
                }
            
            elif network == "ethereum":
                return await self.get_ethereum_token_info(address)
            
            elif network == "solana":
                return await self.get_solana_token_info(address)
            
            elif network in ["bsc", "polygon", "avalanche", "arbitrum", "optimism", "base", "fantom"]:
                # Use CoinGecko for EVM chains
                return await self.get_coingecko_token_info(address, network)
            
            else:
                # For other chains, try generic approach
                return await self.get_generic_token_info(network, address)
                
        except Exception as e:
            logger.error(f"Error fetching token info for {network}: {e}")
            return {"valid": False}
    
    async def get_ethereum_token_info(self, address: str):
        """Get Ethereum token info from Ethplorer"""
        try:
            api_key = os.environ.get("ETHPLORER_API_KEY", "freekey")
            async with aiohttp.ClientSession() as session:
                url = f"https://api.ethplorer.io/getTokenInfo/{address}?apiKey={api_key}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "error" not in data:
                            return {
                                "symbol": data.get("symbol", "UNKNOWN").upper(),
                                "name": data.get("name", "Unknown Token"),
                                "decimals": int(data.get("decimals", 18)),
                                "category": self.detect_category(data.get("symbol", "").upper()),
                                "api_source": "ethplorer",
                                "valid": True
                            }
        except Exception as e:
            logger.error(f"Error fetching Ethereum token info: {e}")
        
        return {"valid": False}
    
    async def get_solana_token_info(self, address: str):
        """Get Solana token info from Birdeye"""
        try:
            api_key = os.environ.get("BIRDEYE_API_KEY", "")
            headers = {"X-API-KEY": api_key} if api_key else {}
            
            async with aiohttp.ClientSession() as session:
                url = f"https://public-api.birdeye.so/defi/token_overview?address={address}"
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success"):
                            token_data = data.get("data", {})
                            return {
                                "symbol": token_data.get("symbol", "UNKNOWN").upper(),
                                "name": token_data.get("name", "Unknown Token"),
                                "decimals": int(token_data.get("decimals", 9)),
                                "category": self.detect_category(token_data.get("symbol", "").upper()),
                                "api_source": "birdeye",
                                "valid": True
                            }
        except Exception as e:
            logger.error(f"Error fetching Solana token info: {e}")
        
        return {"valid": False}
    
    async def get_coingecko_token_info(self, address: str, network: str):
        """Get token info from CoinGecko"""
        try:
            network_map = {
                "ethereum": "ethereum",
                "bsc": "binance-smart-chain",
                "polygon": "polygon-pos",
                "avalanche": "avalanche",
                "arbitrum": "arbitrum-one",
                "optimism": "optimistic-ethereum",
                "base": "base",
                "fantom": "fantom"
            }
            
            cg_network = network_map.get(network)
            if not cg_network:
                return {"valid": False}
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/coins/{cg_network}/contract/{address}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "symbol": data.get("symbol", "UNKNOWN").upper(),
                            "name": data.get("name", "Unknown Token"),
                            "decimals": data.get("detail_platforms", {}).get(cg_network, {}).get("decimal_place", 18),
                            "category": self.detect_category(data.get("symbol", "").upper()),
                            "api_source": "coingecko",
                            "valid": True
                        }
        except Exception as e:
            logger.error(f"Error fetching CoinGecko token info: {e}")
        
        return {"valid": False}
    
    async def get_generic_token_info(self, network: str, address: str):
        """Get generic token info for unsupported chains"""
        try:
            # Try to get info from CoinGecko by symbol
            if not address or address == "":
                # Native token
                network_name = NETWORK_CONFIGS.get(network, {}).get("name", network)
                return {
                    "symbol": network.upper(),
                    "name": network_name,
                    "decimals": 18,  # Default
                    "category": "layer1",
                    "api_source": "coingecko",
                    "valid": True
                }
            
            # For tokens with addresses, we need more complex logic
            # This is a simplified version
            return {
                "symbol": "UNKNOWN",
                "name": f"Token on {network}",
                "decimals": 18,
                "category": "other",
                "api_source": "generic",
                "valid": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching generic token info: {e}")
            return {"valid": False}
    
    def detect_category(self, symbol: str) -> str:
        """Detect token category"""
        symbol_lower = symbol.lower()
        
        if symbol_lower in ['usdc', 'usdt', 'dai', 'busd', 'tusd', 'usdp']:
            return "stablecoin"
        
        if symbol_lower in ['btc', 'wbtc', 'eth', 'weth', 'sol', 'bnb', 'avax', 'dot', 'ada', 'matic', 'atom', 'apt', 'near', 'algo', 'xtz', 'eos', 'etc']:
            return "layer1"
        
        if symbol_lower in ['arb', 'op', 'base', 'matic']:
            return "layer2"
        
        if symbol_lower in ['shib', 'doge', 'pepe', 'floki', 'bonk', 'wif'] or 'meme' in symbol_lower:
            return "memecoin"
        
        if symbol_lower in ['uni', 'aave', 'comp', 'mkr', 'jup', 'ray', 'orca', 'crv', 'snx', 'cake', 'sushi', 'bal']:
            return "defi"
        
        if symbol_lower in ['link', 'pyth', 'band', 'api3', 'grt']:
            return "oracle"
        
        if symbol_lower in ['xrp', 'ltc', 'bch', 'xlm']:
            return "payment"
        
        if symbol_lower in ['sand', 'mana', 'axs', 'gala', 'enj']:
            return "gaming"
        
        if symbol_lower in ['fil', 'vet', 'icp', 'theta', 'hbar']:
            return "enterprise"
        
        if symbol_lower in ['rndr', 'fet']:
            return "ai"
        
        if symbol_lower in ['ar', 'storj', 'fil']:
            return "storage"
        
        if symbol_lower in ['cel', 'aave', 'comp']:
            return "lending"
        
        if symbol_lower in ['ant', 'uni']:
            return "governance"
        
        if symbol_lower in ['chz']:
            return "sports"
        
        if symbol_lower in ['oxt']:
            return "privacy"
        
        return "other"
    
    async def process_updates(self):
        """Process Telegram updates for all users"""
        try:
            url = f"{self.url}/getUpdates?offset={self.last_update_id + 1}&timeout=2"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok") and data.get("result"):
                            for update in data["result"]:
                                await self.handle_update(update)
                                self.last_update_id = update["update_id"]
        except Exception as e:
            logger.error(f"Error processing updates: {e}")
    
    async def handle_update(self, update):
        """Handle Telegram updates"""
        # Check for callback queries first
        if "callback_query" in update:
            callback = update["callback_query"]
            callback_data = callback.get("data", "")
            chat_id = str(callback["message"]["chat"]["id"])
            await self.process_callback(chat_id, callback_data)
            return
        
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id"))
        
        if not chat_id:
            return
        
        logger.info(f"Message from {chat_id}: {text[:50]}...")
        self.bot_stats["messages_received"] += 1
        
        # Check if waiting for threshold input
        if chat_id in self.waiting_for_threshold and text.isdigit():
            symbol = self.waiting_for_threshold[chat_id]
            try:
                threshold = int(text)
                
                if threshold < 10000:
                    await self.send(chat_id, "⚠️ *Seuil minimum:* $10,000")
                    return
                
                if self.config.update_token_threshold(symbol, threshold):
                    await self.send(chat_id, f"✅ *SEUIL MODIFIÉ*\n\n"
                                  f"📛 **{symbol}**\n"
                                  f"Nouveau seuil: **${threshold:,}**")
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
                # Register new user or load existing
                user_settings = self.user_manager.get_user(chat_id)
                
                # Check if user needs to select tokens first
                if not user_settings.get("onboarding_complete", False) or len(user_settings.get("enabled_tokens", [])) == 0:
                    await self.send_onboarding_menu(chat_id, first_time=True)
                else:
                    await self.send_main_menu(chat_id)
            
            elif command == "/add" and len(parts) >= 4:
                network = parts[1].lower()
                address = parts[2]
                threshold = parts[3]
                await self.handle_add_token(chat_id, network, address, threshold)
            
            elif command == "/threshold" and len(parts) >= 3:
                symbol = parts[1].upper()
                try:
                    threshold = int(parts[2])
                    if self.config.update_token_threshold(symbol, threshold):
                        await self.send(chat_id, f"✅ Seuil de {symbol} modifié: ${threshold:,}")
                    else:
                        await self.send(chat_id, f"❌ Token {symbol} non trouvé")
                except ValueError:
                    await self.send(chat_id, "❌ Format invalide. Utilisez: `/threshold SYMBOLE MONTANT`")
            
            elif command == "/remove" and len(parts) >= 2:
                symbol = parts[1].upper()
                if self.config.remove_token(symbol):
                    # Disable for all users
                    for user_id in self.user_manager.get_all_users():
                        user_settings = self.user_manager.get_user(user_id)
                        if symbol in user_settings.get("enabled_tokens", []):
                            user_settings["enabled_tokens"].remove(symbol)
                            self.user_manager.update_user(user_id, user_settings)
                    await self.send(chat_id, f"✅ Token {symbol} supprimé pour tous les utilisateurs")
                else:
                    await self.send(chat_id, f"❌ Token {symbol} non trouvé")
            
            elif command == "/list":
                await self.show_token_list(chat_id)
            
            elif command == "/help":
                await self.send_help(chat_id)
            
            elif command == "/enable" and len(parts) >= 2:
                symbol = parts[1].upper()
                user_settings = self.user_manager.get_user(chat_id)
                enabled_tokens = user_settings.get("enabled_tokens", [])
                if symbol not in enabled_tokens:
                    enabled_tokens.append(symbol)
                    user_settings["enabled_tokens"] = enabled_tokens
                    self.user_manager.update_user(chat_id, user_settings)
                    await self.send(chat_id, f"✅ Token {symbol} activé")
                else:
                    await self.send(chat_id, f"ℹ️ Token {symbol} était déjà activé")
            
            elif command == "/disable" and len(parts) >= 2:
                symbol = parts[1].upper()
                user_settings = self.user_manager.get_user(chat_id)
                enabled_tokens = user_settings.get("enabled_tokens", [])
                if symbol in enabled_tokens:
                    enabled_tokens.remove(symbol)
                    user_settings["enabled_tokens"] = enabled_tokens
                    self.user_manager.update_user(chat_id, user_settings)
                    await self.send(chat_id, f"✅ Token {symbol} désactivé")
                else:
                    await self.send(chat_id, f"ℹ️ Token {symbol} était déjà désactivé")
            
            elif command == "/select":
                await self.send_onboarding_menu(chat_id, first_time=False)
            
            elif command == "/networks":
                await self.show_networks_menu(chat_id)
            
            elif command == "/users" and chat_id in self.admin_users:
                users = self.user_manager.get_all_users()
                text = f"👥 *UTILISATEURS INSCRITS:* {len(users)}\n\n"
                for i, user_id in enumerate(users[:20], 1):
                    text += f"{i}. `{user_id}`\n"
                if len(users) > 20:
                    text += f"\n... et {len(users)-20} autres"
                await self.send(chat_id, text)
            
            elif command == "/broadcast" and chat_id in self.admin_users and len(parts) >= 2:
                message = " ".join(parts[1:])
                users = self.user_manager.get_all_users()
                sent = 0
                for user_id in users:
                    try:
                        await self.send(user_id, f"📢 *ANNONCE ADMIN:*\n\n{message}")
                        sent += 1
                    except:
                        pass
                await self.send(chat_id, f"✅ Message envoyé à {sent}/{len(users)} utilisateurs")
            
            # Commandes textuelles avec traduction
            elif command == "/gérer" or command == "/manage":
                await self.send_token_management(chat_id)
            
            elif command == "/sélectionner" or command == "/select":
                await self.send_onboarding_menu(chat_id, first_time=False)
            
            elif command == "/paramètres" or command == "/settings":
                await self.send_settings_menu(chat_id)
            
            elif command == "/statistiques" or command == "/stats":
                await self.show_stats(chat_id)
            
            elif command == "/tokens":
                await self.show_token_list(chat_id)
            
            elif command == "/alertes" or command == "/alerts":
                await self.send_alert_levels_menu(chat_id)
            
            elif command == "/langue" or command == "/language":
                await self.send_language_menu(chat_id)
            
            elif command == "/seuils" or command == "/thresholds":
                await self.send_change_threshold_menu(chat_id)
            
            elif command == "/réseaux" or command == "/networks":
                await self.show_networks_menu(chat_id)
            
            elif command == "/activer" and len(parts) >= 2:
                symbol = parts[1].upper()
                user_settings = self.user_manager.get_user(chat_id)
                enabled_tokens = user_settings.get("enabled_tokens", [])
                if symbol not in enabled_tokens:
                    enabled_tokens.append(symbol)
                    user_settings["enabled_tokens"] = enabled_tokens
                    self.user_manager.update_user(chat_id, user_settings)
                    await self.send(chat_id, f"✅ Token {symbol} activé")
                else:
                    await self.send(chat_id, f"ℹ️ Token {symbol} était déjà activé")
            
            elif command == "/désactiver" and len(parts) >= 2:
                symbol = parts[1].upper()
                user_settings = self.user_manager.get_user(chat_id)
                enabled_tokens = user_settings.get("enabled_tokens", [])
                if symbol in enabled_tokens:
                    enabled_tokens.remove(symbol)
                    user_settings["enabled_tokens"] = enabled_tokens
                    self.user_manager.update_user(chat_id, user_settings)
                    await self.send(chat_id, f"✅ Token {symbol} désactivé")
                else:
                    await self.send(chat_id, f"ℹ️ Token {symbol} était déjà désactivé")
            
            elif command == "/activer_tous" or command == "/enable_all":
                all_tokens = self.config.get_all_tokens()
                user_settings = self.user_manager.get_user(chat_id)
                user_settings["enabled_tokens"] = list(all_tokens.keys())
                user_settings["onboarding_complete"] = True
                self.user_manager.update_user(chat_id, user_settings)
                await self.send(chat_id, f"✅ Tous les tokens activés ({len(all_tokens)} tokens)")
                await self.send_main_menu(chat_id)
            
            elif command == "/désactiver_tous" or command == "/disable_all":
                user_settings = self.user_manager.get_user(chat_id)
                user_settings["enabled_tokens"] = []
                self.user_manager.update_user(chat_id, user_settings)
                await self.send(chat_id, "❌ Tous les tokens désactivés")
            
            elif command == "/info" and len(parts) >= 2:
                symbol = parts[1].upper()
                all_tokens = self.config.get_all_tokens()
                if symbol in all_tokens:
                    info = all_tokens[symbol]
                    network_name = self.get_network_name(info.get("network", "other"), self.get_user_lang(chat_id))
                    
                    await self.send(chat_id, f"📊 *INFORMATIONS SUR {symbol}*\n\n"
                                  f"🎯 Seuil: **${info['threshold_usd']:,}**\n"
                                  f"🔗 Réseau: **{network_name}**\n"
                                  f"📛 Nom: {info.get('display_name', symbol)}\n"
                                  f"🔢 Décimales: {info.get('decimals', 'N/A')}\n"
                                  f"📊 Catégorie: {self.get_category_text(info.get('category', 'other'), self.get_user_lang(chat_id))}\n"
                                  f"🔗 Adresse: `{info.get('address', 'Native token')[:20]}...`")
                else:
                    await self.send(chat_id, f"❌ Token {symbol} non trouvé")
            
            elif command == "/search" and len(parts) >= 2:
                search_term = parts[1].upper()
                all_tokens = self.config.get_all_tokens()
                matches = [sym for sym in all_tokens.keys() if search_term in sym.upper()]
                if matches:
                    text = f"🔍 *RECHERCHE: '{search_term}'*\n\n"
                    text += f"Résultats trouvés: {len(matches)}\n\n"
                    for symbol in matches[:10]:  # Show first 10
                        info = all_tokens[symbol]
                        text += f"• **{symbol}** - ${info['threshold_usd']:,} ({info.get('network', 'other')})\n"
                    if len(matches) > 10:
                        text += f"\n... et {len(matches)-10} autres"
                    await self.send(chat_id, text)
                else:
                    await self.send(chat_id, f"❌ Aucun token trouvé pour '{search_term}'")
            
            elif command == "/catégories" or command == "/categories":
                all_tokens = self.config.get_all_tokens()
                categories = {}
                for symbol, info in all_tokens.items():
                    cat = info.get('category', 'other')
                    categories[cat] = categories.get(cat, 0) + 1
                
                user_lang = self.get_user_lang(chat_id)
                text = "📊 *CATÉGORIES DE TOKENS*\n\n"
                for cat, count in sorted(categories.items()):
                    cat_name = self.get_category_text(cat, user_lang)
                    text += f"• **{cat_name}**: {count} tokens\n"
                text += f"\n📈 Total: {len(all_tokens)} tokens"
                await self.send(chat_id, text)
            
            elif command == "/status" or command == "/état":
                user_tokens = self.config.get_tokens_for_user(chat_id)
                all_tokens = self.config.get_all_tokens()
                user_lang = self.get_user_lang(chat_id)
                
                text = f"📊 *STATUS DU BOT*\n\n"
                text += f"👤 Utilisateur: {chat_id[:8]}...\n"
                text += f"📈 Tokens activés: **{len(user_tokens)}/{len(all_tokens)}**\n"
                text += f"🌍 Langue: **{'Français' if user_lang == 'fr' else 'English'}**\n"
                text += f"⏰ Dernière activité: {datetime.now().strftime('%H:%M:%S')}\n\n"
                
                # Alert levels status
                user_settings = self.user_manager.get_user(chat_id)
                alert_levels = user_settings.get("alert_levels", {})
                text += "*🔔 NIVEAUX D'ALERTE:*\n"
                for level_id, level_name in [("mega", "🐋 MÉGA WHALE"), ("huge", "🐳 WHALE ÉNORME"), 
                                            ("large", "🐬 GROSSE WHALE"), ("whale", "🐟 WHALE"), 
                                            ("significant", "🦈 GROSSE ACTIVITÉ")]:
                    status = "✅" if alert_levels.get(level_id, True) else "❌"
                    text += f"{status} {level_name}\n"
                
                await self.send(chat_id, text)
            
            elif command == "/admin" and chat_id in self.admin_users:
                await self.send_admin_menu(chat_id)
            
            elif command == "/aide" or command == "/help":
                await self.send_help(chat_id)
            
            elif command == "/ping":
                await self.send(chat_id, "🏓 Pong! Le bot est en ligne et fonctionnel.")
            
            elif command == "/uptime":
                uptime = datetime.now() - datetime.fromisoformat(self.bot_stats["start_time"])
                days = uptime.days
                hours, remainder = divmod(uptime.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                await self.send(chat_id, f"⏰ *UPTIME*\n\nLe bot fonctionne depuis:\n{days} jours, {hours} heures, {minutes} minutes, {seconds} secondes")
            
            elif command == "/stats_global":
                if chat_id in self.admin_users:
                    await self.show_global_stats(chat_id)
            
            else:
                # Si la commande n'est pas reconnue, envoyer le menu principal
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
        
        else:
            # Si c'est un message normal, envoyer le menu principal
            await self.send_main_menu(chat_id)
    
    async def show_networks_menu(self, chat_id: str):
        """Show networks selection menu"""
        user_lang = self.get_user_lang(chat_id)
        user_tokens = self.config.get_tokens_for_user(chat_id)
        
        # Get networks with tokens
        networks_with_tokens = set()
        for token_info in user_tokens.values():
            networks_with_tokens.add(token_info.get("network", "other"))
        
        text = f"🔗 *{self.get_text('networks', user_lang).upper()}*\n\n"
        text += f"{self.get_text('active_networks', user_lang)}: {len(networks_with_tokens)}\n\n"
        text += f"{self.get_text('select_network_view', user_lang)}:\n"
        
        keyboard_buttons = []
        
        for network_id, network_config in NETWORK_CONFIGS.items():
            network_name = self.get_network_name(network_id, user_lang)
            network_icon = self.get_network_icon(network_id)
            token_count = len(self.config.get_tokens_by_network(network_id))
            
            status = "✅" if network_id in networks_with_tokens else "🔘"
            btn_text = f"{status} {network_icon} {network_name} ({token_count})"
            
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"network_{network_id}"}
            ])
        
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        await self.send(chat_id, text, keyboard)
    
    async def show_global_stats(self, chat_id: str):
        """Show global bot statistics"""
        total_users = self.user_manager.get_user_count()
        total_tokens = len(self.config.get_all_tokens())
        uptime = datetime.now() - datetime.fromisoformat(self.bot_stats["start_time"])
        
        # Network stats
        network_stats = self.config.get_network_stats()
        
        text = f"📊 *STATISTIQUES GLOBALES DU BOT*\n\n"
        text += f"🤖 *Bot:* Whale Radar (Multi-Chain)\n"
        text += f"⏰ *Uptime:* {uptime.days} jours, {uptime.seconds//3600} heures\n"
        text += f"👥 *Utilisateurs:* {total_users}\n"
        text += f"📈 *Tokens configurés:* {total_tokens}\n"
        text += f"📨 *Messages reçus:* {self.bot_stats['messages_received']}\n"
        text += f"📤 *Messages envoyés:* {self.bot_stats['messages_sent']}\n"
        text += f"⚡ *Commandes traitées:* {self.bot_stats['commands_processed']}\n"
        text += f"🚨 *Alertes envoyées:* {self.bot_stats['alerts_sent']}\n\n"
        
        text += f"🔗 *RÉSEAUX:*\n"
        for network, stats in network_stats.items():
            network_name = self.get_network_name(network, "fr")
            text += f"• {self.get_network_icon(network)} {network_name}: {stats['count']} tokens\n"
        
        text += f"\n🔄 *Dernier scan:* {datetime.now().strftime('%H:%M:%S')}"
        
        await self.send(chat_id, text)
    
    async def send_help(self, chat_id: str):
        """Send help message"""
        user_lang = self.get_user_lang(chat_id)
        
        if user_lang == "fr":
            text = """
🤖 *WHALE RADAR BOT - AIDE COMPLÈTE (MULTI-CHAÎNE)*

📱 *MENU INTERACTIF:*
• Utilisez `/menu` pour le menu principal
• Cliquez sur les boutons pour naviguer
• Nouveaux utilisateurs: Sélectionnez vos tokens d'abord!

🔧 *COMMANDES PRINCIPALES:*
• `/menu` - Menu principal
• `/sélectionner` - Sélectionner tokens (important!)
• `/gérer` - Gérer les tokens
• `/paramètres` - Paramètres
• `/statistiques` - Mes statistiques
• `/tokens` - Liste mes tokens
• `/réseaux` - Voir réseaux
• `/alertes` - Niveaux d'alerte
• `/langue` - Changer langue
• `/seuils` - Modifier seuils
• `/status` - Status du bot
• `/aide` - Cette aide

➕ *AJOUTER/SUPPRIMER:*
• `/add RÉSEAU ADRESSE SEUIL` - Ajouter token
• `/remove SYMBOLE` - Supprimer token
• `/info SYMBOLE` - Info token

⚙️ *ACTIVER/DÉSACTIVER:*
• `/activer SYMBOLE` - Activer token
• `/désactiver SYMBOLE` - Désactiver token
• `/activer_tous` - Tout activer
• `/désactiver_tous` - Tout désactiver

🔍 *RECHERCHE:*
• `/search TERME` - Rechercher token
• `/catégories` - Voir catégories

🎯 *SEUILS:*
• `/threshold SYMBOLE MONTANT` - Modifier seuil
Exemple: `/threshold BTC 1000000`

🔔 *NIVEAUX D'ALERTE:*
1. 🐋 MÉGA WHALE (20x+ du seuil)
2. 🐳 WHALE ÉNORME (10-20x)
3. 🐬 GROSSE WHALE (5-10x)
4. 🐟 WHALE (2-5x)
5. 🦈 GROSSE ACTIVITÉ (1-2x)

🔗 *RÉSEAUX SUPPORTÉS:*
• ₿ Bitcoin (BTC)
• Ξ Ethereum (ETH, USDC, USDT, etc.)
• ✕ XRP (Ripple)
• ₳ Cardano (ADA)
• ❄ Avalanche (AVAX)
• Ð Dogecoin (DOGE)
• ₮ Tron (TRX)
• ₸ Toncoin (TON)
• ⓑ Binance Smart Chain (BNB, CAKE, etc.)
• ◎ Solana (SOL, BONK, JUP, WIF, etc.)
• ⬡ Polygon (MATIC, USDC)
• ⟁ Arbitrum (ARB, WBTC)
• Ⓞ Optimism (OP)
• ● Polkadot (DOT)
• ⚛ Cosmos (ATOM)
• Ⓝ Near Protocol (NEAR)
• Ⓐ Aptos (APT)
• 🅱 Base Network

📊 *SCANNING:*
• Scan automatique toutes les 30 secondes
• Alertes uniquement pour tokens activés
• Surveillance multi-chaîne simultanée

🌍 *LANGUES:*
• Français: `/langue` puis 🇫🇷
• English: `/language` puis 🇬🇧

👑 *COMMANDES ADMIN:*
• `/admin` - Menu admin
• `/users` - Liste utilisateurs
• `/broadcast MESSAGE` - Envoyer à tous
• `/stats_global` - Statistiques globales

💡 *ASTUCES:*
1. **Sélectionnez d'abord vos tokens** après /start
2. Commencez avec 2-3 tokens principaux
3. Ajustez les seuils selon votre budget
4. Utilisez les commandes textuelles si les menus disparaissent

📞 *SUPPORT:*
Pour tout problème, contactez l'administrateur.
"""
        else:
            text = """
🤖 *WHALE RADAR BOT - COMPLETE HELP (MULTI-CHAIN)*

📱 *INTERACTIVE MENU:*
• Use `/menu` for main menu
• Click buttons to navigate
• New users: Select your tokens first!

🔧 *MAIN COMMANDS:*
• `/menu` - Main menu
• `/select` - Select tokens (important!)
• `/manage` - Manage tokens
• `/settings` - Settings
• `/stats` - My statistics
• `/tokens` - List my tokens
• `/networks` - View networks
• `/alerts` - Alert levels
• `/language` - Change language
• `/thresholds` - Modify thresholds
• `/status` - Bot status
• `/help` - This help

➕ *ADD/REMOVE:*
• `/add NETWORK ADDRESS THRESHOLD` - Add token
• `/remove SYMBOL` - Remove token
• `/info SYMBOL` - Token info

⚙️ *ENABLE/DISABLE:*
• `/enable SYMBOL` - Enable token
• `/disable SYMBOL` - Disable token
• `/enable_all` - Enable all
• `/disable_all` - Disable all

🔍 *SEARCH:*
• `/search TERM` - Search token
• `/categories` - View categories

🎯 *THRESHOLDS:*
• `/threshold SYMBOL AMOUNT` - Change threshold
Example: `/threshold BTC 1000000`

🔔 *ALERT LEVELS:*
1. 🐋 MEGA WHALE (20x+ threshold)
2. 🐳 HUGE WHALE (10-20x)
3. 🐬 LARGE WHALE (5-10x)
4. 🐟 WHALE (2-5x)
5. 🦈 BIG ACTIVITY (1-2x)

🔗 *SUPPORTED NETWORKS:*
• ₿ Bitcoin (BTC)
• Ξ Ethereum (ETH, USDC, USDT, etc.)
• ✕ XRP (Ripple)
• ₳ Cardano (ADA)
• ❄ Avalanche (AVAX)
• Ð Dogecoin (DOGE)
• ₮ Tron (TRX)
• ₸ Toncoin (TON)
• ⓑ Binance Smart Chain (BNB, CAKE, etc.)
• ◎ Solana (SOL, BONK, JUP, WIF, etc.)
• ⬡ Polygon (MATIC, USDC)
• ⟁ Arbitrum (ARB, WBTC)
• Ⓞ Optimism (OP)
• ● Polkadot (DOT)
• ⚛ Cosmos (ATOM)
• Ⓝ Near Protocol (NEAR)
• Ⓐ Aptos (APT)
• 🅱 Base Network

📊 *SCANNING:*
• Auto scan every 30 seconds
• Alerts only for enabled tokens
• Multi-chain monitoring simultaneously

🌍 *LANGUES:*
• Français: `/language` then 🇫🇷
• English: `/language` then 🇬🇧

👑 *ADMIN COMMANDS:*
• `/admin` - Admin menu
• `/users` - User list
• `/broadcast MESSAGE` - Send to all
• `/stats_global` - Global statistics

💡 *TIPS:*
1. **Select your tokens first** after /start
2. Start with 2-3 main tokens
3. Adjust thresholds according to your budget
4. Use text commands if menus disappear

📞 *SUPPORT:*
For any issues, contact administrator.
"""
        await self.send(chat_id, text)
    
    async def send_admin_menu(self, chat_id: str):
        """Send admin menu"""
        user_lang = self.get_user_lang(chat_id)
        all_users = self.user_manager.get_all_users()
        network_stats = self.config.get_network_stats()
        
        text = f"👑 *{self.get_text('admin', user_lang).upper()}*\n\n"
        text += f"👥 {self.get_text('total_users', user_lang)}: {len(all_users)}\n"
        text += f"📊 {self.get_text('tokens_configured', user_lang)}: {len(self.config.get_all_tokens())}\n\n"
        
        text += f"🔗 {self.get_text('networks', user_lang)}:\n"
        for network, stats in network_stats.items():
            network_name = self.get_network_name(network, user_lang)
            text += f"• {self.get_network_icon(network)} {network_name}: {stats['count']} tokens\n"
        
        text += f"\n{self.get_text('admin_options', user_lang)}:"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 " + self.get_text("global_stats", user_lang), "callback_data": "admin_stats"}],
                [{"text": "👥 " + self.get_text("user_list", user_lang), "callback_data": "admin_users"}],
                [{"text": "🔄 " + self.get_text("force_rescan", user_lang), "callback_data": "admin_rescan"}],
                [{"text": "📢 " + self.get_text("broadcast", user_lang), "callback_data": "admin_broadcast"}],
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)

# ================= SCANNER (MULTI-CHAIN) =================
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
        logger.info("Whale Scanner initialized (Multi-Chain)")
    
    async def scan_for_user(self, chat_id: str):
        """Scan tokens for a specific user"""
        user_tokens = self.config.get_tokens_for_user(chat_id)
        
        if not user_tokens:
            return 0
        
        alerts = 0
        for symbol, info in user_tokens.items():
            alerted = await self.scan_token_volume(chat_id, symbol, info)
            if alerted:
                alerts += 1
        
        return alerts
    
    async def scan_token_volume(self, chat_id: str, symbol: str, token_info: dict):
        """Scan token volume for whale activity"""
        try:
            network = token_info.get("network", "other")
            api_source = token_info.get("api_source", "coingecko")
            
            # Get token data based on network
            data = await self.get_token_data(network, token_info.get("address", ""), symbol)
            if not data:
                return False
            
            threshold = token_info["threshold_usd"]
            
            # Process data based on network
            if network == "bitcoin":
                return await self.process_bitcoin_data(chat_id, symbol, token_info, data, threshold)
            elif network == "ethereum":
                return await self.process_ethereum_data(chat_id, symbol, token_info, data, threshold)
            elif network == "solana":
                return await self.process_solana_data(chat_id, symbol, token_info, data, threshold)
            elif network == "xrp":
                return await self.process_xrp_data(chat_id, symbol, token_info, data, threshold)
            elif network == "cardano":
                return await self.process_cardano_data(chat_id, symbol, token_info, data, threshold)
            elif network == "avalanche":
                return await self.process_avalanche_data(chat_id, symbol, token_info, data, threshold)
            else:
                # For other chains, use generic processor
                return await self.process_generic_data(chat_id, symbol, token_info, data, threshold, network)
            
        except Exception as e:
            logger.error(f"Scan error for {symbol} on {token_info.get('network', 'other')} (user {chat_id}): {e}")
            return False
    
    async def get_token_data(self, network: str, address: str, symbol: str):
        """Fetch token data based on network"""
        try:
            if network == "bitcoin":
                # Use mempool.space for Bitcoin large transactions
                async with aiohttp.ClientSession() as session:
                    url = "https://mempool.space/api/v1/transactions"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.json()
            
            elif network == "ethereum":
                # Use Etherscan or alternative API
                api_key = os.environ.get("ETHERSCAN_API_KEY", "")
                if address:  # Token
                    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
                else:  # ETH
                    url = f"https://api.etherscan.io/api?module=account&action=txlist&address=0x0000000000000000000000000000000000000000&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("result", [])
            
            elif network == "solana":
                # Use Birdeye for Solana
                api_key = os.environ.get("BIRDEYE_API_KEY", "")
                headers = {"X-API-KEY": api_key} if api_key else {}
                
                if address:
                    url = f"https://public-api.birdeye.so/defi/txs_token?address={address}"
                else:
                    url = "https://public-api.birdeye.so/defi/txs_token?address=So11111111111111111111111111111111111111112"  # SOL
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.json()
            
            elif network == "xrp":
                # Use XRP Ledger API
                async with aiohttp.ClientSession() as session:
                    url = "https://data.ripple.com/v2/transactions?limit=20"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.json()
            
            elif network == "cardano":
                # Use Cardano Blockchain Explorer
                async with aiohttp.ClientSession() as session:
                    url = "https://cardano-mainnet.blockfrost.io/api/v0/blocks/latest/transactions"
                    headers = {"project_id": os.environ.get("BLOCKFROST_API_KEY", "")}
                    async with session.get(url, headers=headers, timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.json()
            
            elif network == "avalanche":
                # Use Snowtrace API
                api_key = os.environ.get("SNOWTRACE_API_KEY", "")
                if address:
                    url = f"https://api.snowtrace.io/api?module=account&action=tokentx&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
                else:
                    url = f"https://api.snowtrace.io/api?module=account&action=txlist&address=0x0000000000000000000000000000000000000000&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("result", [])
            
            else:
                # For other chains, try to get price from CoinGecko
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.json()
        
        except Exception as e:
            logger.error(f"Error fetching {network} data: {e}")
        
        return None
    
    async def process_bitcoin_data(self, chat_id: str, symbol: str, token_info: dict, data: dict, threshold: float):
        """Process Bitcoin transactions"""
        try:
            # Bitcoin transactions from mempool.space
            if isinstance(data, list):
                for tx in data[:10]:  # Check recent transactions
                    fee = tx.get("fee", 0)
                    vsize = tx.get("vsize", 0)
                    
                    # Estimate value (simplified)
                    # In reality, need to check outputs for large amounts
                    if fee > 0.001 * 1e8:  # Fee > 0.001 BTC
                        # Get BTC price
                        price = await self.get_token_price("bitcoin")
                        if price > 0:
                            volume_usd = (fee / 1e8) * price
                            
                            if volume_usd >= threshold:
                                ratio = volume_usd / threshold
                                level = self.get_alert_level(ratio)
                                
                                # Check if this level is enabled for user
                                user_settings = self.user_manager.get_user(chat_id)
                                alert_levels = user_settings.get("alert_levels", {})
                                if not alert_levels.get(level, True):
                                    continue
                                
                                await self.send_whale_alert(
                                    chat_id=chat_id,
                                    symbol=symbol,
                                    token_info=token_info,
                                    volume_usd=volume_usd,
                                    price=price,
                                    token_amount=fee / 1e8,
                                    action="TRANSFER",
                                    ratio=ratio,
                                    level=level,
                                    dex="Bitcoin Network",
                                    pair_address=""
                                )
                                
                                self.telegram.bot_stats["alerts_sent"] += 1
                                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Bitcoin data: {e}")
            return False
    
    async def process_ethereum_data(self, chat_id: str, symbol: str, token_info: dict, data: list, threshold: float):
        """Process Ethereum transactions"""
        try:
            price = await self.get_token_price("ethereum" if symbol == "ETH" else symbol.lower())
            if price <= 0:
                return False
            
            # Check recent transactions
            for tx in data[:20]:
                value = int(tx.get("value", 0))
                
                # Convert from wei to ETH/tokens
                decimals = token_info.get("decimals", 18)
                token_amount = value / (10 ** decimals)
                volume_usd = token_amount * price
                
                if volume_usd >= threshold:
                    ratio = volume_usd / threshold
                    level = self.get_alert_level(ratio)
                    
                    # Check if this level is enabled for user
                    user_settings = self.user_manager.get_user(chat_id)
                    alert_levels = user_settings.get("alert_levels", {})
                    if not alert_levels.get(level, True):
                        continue
                    
                    action = "IN" if tx.get("to", "") == token_info.get("address", "") else "OUT"
                    
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
                        pair_address=tx.get("hash", "")[:20]
                    )
                    
                    self.telegram.bot_stats["alerts_sent"] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Ethereum data: {e}")
            return False
    
    async def process_solana_data(self, chat_id: str, symbol: str, token_info: dict, data: dict, threshold: float):
        """Process Solana transactions"""
        try:
            price = await self.get_token_price("solana" if symbol == "SOL" else symbol.lower())
            if price <= 0:
                return False
            
            if data.get("success"):
                items = data.get("data", {}).get("items", [])
                for item in items[:20]:
                    volume = float(item.get("volume", 0))
                    
                    if volume >= threshold:
                        ratio = volume / threshold
                        level = self.get_alert_level(ratio)
                        
                        # Check if this level is enabled for user
                        user_settings = self.user_manager.get_user(chat_id)
                        alert_levels = user_settings.get("alert_levels", {})
                        if not alert_levels.get(level, True):
                            continue
                        
                        token_amount = volume / price if price > 0 else 0
                        action = "BUY" if item.get("side") == "buy" else "SELL"
                        
                        await self.send_whale_alert(
                            chat_id=chat_id,
                            symbol=symbol,
                            token_info=token_info,
                            volume_usd=volume,
                            price=price,
                            token_amount=token_amount,
                            action=action,
                            ratio=ratio,
                            level=level,
                            dex="Solana DEX",
                            pair_address=item.get("tx_id", "")[:20]
                        )
                        
                        self.telegram.bot_stats["alerts_sent"] += 1
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Solana data: {e}")
            return False
    
    async def process_xrp_data(self, chat_id: str, symbol: str, token_info: dict, data: dict, threshold: float):
        """Process XRP transactions"""
        try:
            price = await self.get_token_price("ripple")
            if price <= 0:
                return False
            
            if data.get("transactions"):
                for tx in data["transactions"][:10]:
                    amount = float(tx.get("Amount", 0))
                    
                    # XRP amounts are in drops (1 XRP = 1,000,000 drops)
                    if amount > 1000000:  # More than 1 XRP
                        xrp_amount = amount / 1000000
                        volume_usd = xrp_amount * price
                        
                        if volume_usd >= threshold:
                            ratio = volume_usd / threshold
                            level = self.get_alert_level(ratio)
                            
                            # Check if this level is enabled for user
                            user_settings = self.user_manager.get_user(chat_id)
                            alert_levels = user_settings.get("alert_levels", {})
                            if not alert_levels.get(level, True):
                                continue
                            
                            await self.send_whale_alert(
                                chat_id=chat_id,
                                symbol=symbol,
                                token_info=token_info,
                                volume_usd=volume_usd,
                                price=price,
                                token_amount=xrp_amount,
                                action="TRANSFER",
                                ratio=ratio,
                                level=level,
                                dex="XRP Ledger",
                                pair_address=tx.get("hash", "")[:20]
                            )
                            
                            self.telegram.bot_stats["alerts_sent"] += 1
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing XRP data: {e}")
            return False
    
    async def process_cardano_data(self, chat_id: str, symbol: str, token_info: dict, data: dict, threshold: float):
        """Process Cardano transactions"""
        try:
            price = await self.get_token_price("cardano")
            if price <= 0:
                return False
            
            if isinstance(data, list):
                for tx in data[:10]:
                    # Cardano transactions have outputs with amounts
                    # This is simplified - real implementation would parse outputs
                    volume_usd = 100000  # Placeholder
                    
                    if volume_usd >= threshold:
                        ratio = volume_usd / threshold
                        level = self.get_alert_level(ratio)
                        
                        # Check if this level is enabled for user
                        user_settings = self.user_manager.get_user(chat_id)
                        alert_levels = user_settings.get("alert_levels", {})
                        if not alert_levels.get(level, True):
                            continue
                        
                        token_amount = volume_usd / price if price > 0 else 0
                        
                        await self.send_whale_alert(
                            chat_id=chat_id,
                            symbol=symbol,
                            token_info=token_info,
                            volume_usd=volume_usd,
                            price=price,
                            token_amount=token_amount,
                            action="TRANSFER",
                            ratio=ratio,
                            level=level,
                            dex="Cardano Network",
                            pair_address=tx.get("hash", "")[:20] if isinstance(tx, dict) else ""
                        )
                        
                        self.telegram.bot_stats["alerts_sent"] += 1
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Cardano data: {e}")
            return False
    
    async def process_avalanche_data(self, chat_id: str, symbol: str, token_info: dict, data: list, threshold: float):
        """Process Avalanche transactions"""
        try:
            price = await self.get_token_price("avalanche-2" if symbol == "AVAX" else symbol.lower())
            if price <= 0:
                return False
            
            # Similar to Ethereum processing
            for tx in data[:20]:
                value = int(tx.get("value", 0))
                
                # Convert from wei to tokens
                decimals = token_info.get("decimals", 18)
                token_amount = value / (10 ** decimals)
                volume_usd = token_amount * price
                
                if volume_usd >= threshold:
                    ratio = volume_usd / threshold
                    level = self.get_alert_level(ratio)
                    
                    # Check if this level is enabled for user
                    user_settings = self.user_manager.get_user(chat_id)
                    alert_levels = user_settings.get("alert_levels", {})
                    if not alert_levels.get(level, True):
                        continue
                    
                    action = "IN" if tx.get("to", "") == token_info.get("address", "") else "OUT"
                    
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
                        dex="Avalanche Network",
                        pair_address=tx.get("hash", "")[:20]
                    )
                    
                    self.telegram.bot_stats["alerts_sent"] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing Avalanche data: {e}")
            return False
    
    async def process_generic_data(self, chat_id: str, symbol: str, token_info: dict, data: dict, threshold: float, network: str):
        """Process other chain data"""
        try:
            price = await self.get_token_price(symbol.lower())
            if price <= 0:
                return False
            
            # Simplified check - in reality would need chain-specific API
            # For now, simulate based on price movements
            import random
            if random.random() < 0.05:  # 5% chance for demo
                volume_usd = threshold * random.uniform(1.5, 25)
                
                if volume_usd >= threshold:
                    ratio = volume_usd / threshold
                    level = self.get_alert_level(ratio)
                    
                    # Check if this level is enabled for user
                    user_settings = self.user_manager.get_user(chat_id)
                    alert_levels = user_settings.get("alert_levels", {})
                    if not alert_levels.get(level, True):
                        return False
                    
                    token_amount = volume_usd / price if price > 0 else 0
                    action = random.choice(["BUY", "SELL", "TRANSFER"])
                    network_name = NETWORK_CONFIGS.get(network, {}).get("name", network)
                    
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
                        dex=f"{network_name} Network",
                        pair_address=f"0x{random.getrandbits(160):040x}"[:20]
                    )
                    
                    self.telegram.bot_stats["alerts_sent"] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {network} data: {e}")
            return False
    
    async def get_token_price(self, symbol: str) -> float:
        """Get token price from cache or API"""
        cache_key = symbol.lower()
        
        # Check cache (5 minutes)
        if cache_key in self.price_cache:
            price, timestamp = self.price_cache[cache_key]
            if time.time() - timestamp < 300:  # 5 minutes
                return price
        
        try:
            # Use CoinGecko API
            async with aiohttp.ClientSession() as session:
                # Map symbol to CoinGecko ID
                symbol_map = {
                    "btc": "bitcoin",
                    "eth": "ethereum",
                    "xrp": "ripple",
                    "ada": "cardano",
                    "avax": "avalanche-2",
                    "doge": "dogecoin",
                    "trx": "tron",
                    "ton": "the-open-network",
                    "matic": "polygon",
                    "dot": "polkadot",
                    "atom": "cosmos",
                    "near": "near",
                    "apt": "aptos",
                    "op": "optimism",
                    "arb": "arbitrum",
                    "inj": "injective-protocol",
                    "rndr": "render-token",
                    "imx": "immutable-x",
                    "gala": "gala",
                    "fet": "fetch-ai",
                    "pepe": "pepe",
                    "bonk": "bonk",
                    "jup": "jupiter-exchange-solana",
                    "wif": "dogwifhat",
                    "bnb": "binancecoin",
                    "cake": "pancakeswap-token",
                    "icp": "internet-computer",
                    "etc": "ethereum-classic",
                    "ltc": "litecoin",
                    "bch": "bitcoin-cash",
                    "xlm": "stellar",
                    "fil": "filecoin",
                    "hbar": "hedera",
                    "vet": "vechain",
                    "algo": "algorand",
                    "ftm": "fantom",
                    "mkr": "maker",
                    "aave": "aave",
                    "uni": "uniswap",
                    "sushi": "sushi",
                    "crv": "curve-dao-token",
                    "grt": "the-graph",
                    "ldo": "lido-dao",
                    "theta": "theta-token",
                    "cel": "celsius-network-token",
                    "zil": "zilliqa",
                    "icx": "icon",
                    "nano": "nano",
                    "rvn": "ravencoin",
                    "ont": "ontology",
                    "harmony": "harmony",
                    "ren": "republic-protocol",
                    "0x": "0x",
                    "enj": "enjincoin",
                    "chz": "chiliz",
                    "storj": "storj",
                    "ar": "arweave",
                    "ksm": "kusama",
                    "celo": "celo",
                    "nervos": "nervos-network",
                    "knc": "kyber-network",
                    "ant": "aragon",
                    "qtum": "qtum",
                    "comp": "compound-governance-token",
                    "axs": "axie-infinity",
                    "flow": "flow",
                    "snx": "havven",
                    "bal": "balancer",
                    "oxt": "orchid",
                    "omg": "omisego",
                    "base": "base",
                    "sol": "solana",
                    "usdc": "usd-coin",
                    "usdt": "tether",
                    "dai": "dai",
                    "shib": "shiba-inu",
                    "wbtc": "wrapped-bitcoin",
                    "link": "chainlink",
                    "wax": "wax",
                    "lrc": "loopring",
                    "sys": "syscoin",
                    "pivx": "pivx",
                    "nkn": "nkn",
                    "bts": "bitshares",
                    "fun": "funfair",
                    "etn": "electroneum",
                    "wtc": "waltonchain",
                    "ark": "ark",
                    "dcr": "decred",
                    "dgx": "digixdao",
                    "byt": "bytom",
                    "lsk": "lisk",
                    "bcn": "bytecoin",
                    "steem": "steem",
                    "via": "viacoin",
                    "ftc": "feathercoin",
                    "nxs": "nexus",
                    "nxm": "nexus-mutual",
                    "fct": "factom",
                    "maid": "maidsafecoin",
                    "nmc": "namecoin",
                    "scx": "siacoin",
                    "hed": "hedera-hashgraph",
                    "arw": "arweave",
                    "luna": "terra-luna",
                    "luna2": "terra-luna-2",
                    "anc": "anchor-protocol",
                    "bcha": "bitcoin-cash-abc",
                    "bsv": "bitcoin-sv",
                    "elr": "elrond-egld",
                    "rad": "radicle",
                    "nexo": "nexo",
                    "zcoin": "firo",
                    "gamecredits": "game-credits",
                }
                
                cg_id = symbol_map.get(symbol.lower(), symbol.lower())
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
                
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if cg_id in data:
                            price = float(data[cg_id]["usd"])
                            self.price_cache[cache_key] = (price, time.time())
                            return price
            
            # Try alternative approach for native tokens
            if symbol.lower() in ["bitcoin", "btc"]:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if "bitcoin" in data:
                                price = float(data["bitcoin"]["usd"])
                                self.price_cache["bitcoin"] = (price, time.time())
                                return price
            
            elif symbol.lower() in ["ethereum", "eth"]:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if "ethereum" in data:
                                price = float(data["ethereum"]["usd"])
                                self.price_cache["ethereum"] = (price, time.time())
                                return price
        
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
        
        return 0.0
    
    def get_alert_level(self, ratio: float) -> str:
        """Determine alert level based on ratio"""
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
        """Send whale alert to specific user"""
        
        # Get user language
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
            "SELL": {"fr": "VENTE", "en": "SELL"},
            "IN": {"fr": "ENTRÉE", "en": "INFLOW"},
            "OUT": {"fr": "SORTIE", "en": "OUTFLOW"},
            "TRANSFER": {"fr": "TRANSFERT", "en": "TRANSFER"}
        }
        
        whale_type = alert_texts.get(level, {}).get(user_lang, level)
        action_text = action_texts.get(action, {}).get(user_lang, action)
        action_emoji = "🟢" if action in ["BUY", "IN"] else "🔴"
        
        formatted_amount = self.format_number(token_amount, token_info.get("decimals", 9))
        formatted_volume = self.format_currency(volume_usd)
        threshold = token_info["threshold_usd"]
        category = self.telegram.get_category_text(token_info.get("category", "other"), user_lang)
        network = token_info.get("network", "other")
        network_icon = self.telegram.get_network_icon(network)
        network_name = self.telegram.get_network_name(network, user_lang)
        
        if user_lang == "fr":
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

{network_icon} *Réseau:* **{network_name}**
🏷️ *Token:* **{symbol}** ({category})
💰 *Montant:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Ratio seuil:* {ratio:.1f}x
🏷️ *Prix:* ${price:.6f}

📊 *Type:* {action_text} (Dernières transactions)
🏦 *Plateforme:* {dex}
🔗 *Transaction:* `{pair_address[:10]}...`

🎯 *Seuil config:* ${threshold:,}
📅 *Date:* {datetime.now().strftime('%d/%m/%Y')}
⏰ *Heure:* {datetime.now().strftime('%H:%M:%S')}

#WhaleAlert #{symbol} #{action} #{network} #{level}
"""
        else:
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

{network_icon} *Network:* **{network_name}**
🏷️ *Token:* **{symbol}** ({category})
💰 *Amount:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Threshold ratio:* {ratio:.1f}x
🏷️ *Price:* ${price:.6f}

📊 *Type:* {action_text} (Recent transactions)
🏦 *Platform:* {dex}
🔗 *Transaction:* `{pair_address[:10]}...`

🎯 *Config threshold:* ${threshold:,}
📅 *Date:* {datetime.now().strftime('%m/%d/%Y')}
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
            
            # Get all active users
            all_users = self.user_manager.get_all_users()
            active_users = []
            
            for user_id in all_users:
                user_settings = self.user_manager.get_user(user_id)
                user_tokens = self.config.get_tokens_for_user(user_id)
                if user_tokens:  # Only scan for users with enabled tokens
                    active_users.append(user_id)
            
            if active_users:
                logger.info(f"🔍 SCAN #{self.scan_counter} - Scanning for {len(active_users)} active users across {len(set([t['network'] for t in self.config.get_all_tokens().values()]))} networks")
                
                total_alerts = 0
                
                # Scan for each active user
                for user_id in active_users:
                    alerts = await self.scan_for_user(user_id)
                    total_alerts += alerts
                
                self.scan_stats["total_scans"] += 1
                
                if total_alerts > 0:
                    logger.info(f"🚨 Total alerts this scan: {total_alerts}")
                
                # Log stats every 10 scans
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
        self.app.router.add_get('/users', self.handle_users)
        self.app.router.add_post('/webhook', self.handle_webhook)
    
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
    
    async def handle_users(self, request):
        """Handle users endpoint (admin only)"""
        auth_token = request.query.get('token', '')
        if auth_token != "admin123":
            return web.Response(text="Unauthorized", status=401)
        
        users = self.bot.user_manager.get_all_users()
        return web.json_response({
            "total_users": len(users),
            "users": users[:50]
        })
    
    async def handle_webhook(self, request):
        """Handle Telegram webhook"""
        try:
            data = await request.json()
            return web.Response(text="OK")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.Response(text="Error", status=500)
    
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
        logger.info("Whale Radar Bot (Multi-Chain) initialized with 150+ tokens")
    
    async def run(self):
        """Main bot loop"""
        logger.info("=" * 80)
        logger.info("🤖 WHALE RADAR BOT - MULTI-CHAIN VERSION")
        logger.info("=" * 80)
        
        # Get initial stats
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
        
        # Start web server
        web_runner = await self.web_server.start()
        
        # Start keep-alive thread for free hosting
        self.start_keep_alive()
        
        # Send welcome to admin users
        for admin_id in self.telegram.admin_users:
            try:
                await self.telegram.send(admin_id, "🤖 *WHALE RADAR BOT DÉMARRÉ*\n\nVersion Multi-Chain avec 150+ tokens sur 35+ réseaux!")
                await self.telegram.send_main_menu(admin_id)
            except Exception as e:
                logger.error(f"Error sending to admin {admin_id}: {e}")
        
        # Log web server URL for Railway/Render
        logger.info(f"🔗 Health check URL: http://0.0.0.0:{PORT}/health")
        logger.info(f"📊 Stats URL: http://0.0.0.0:{PORT}/stats")
        
        while True:
            try:
                # Process Telegram updates
                await self.telegram.process_updates()
                
                # Run scans
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
                
                # Notify admin users
                for admin_id in self.telegram.admin_users:
                    try:
                        await self.telegram.send(admin_id, end_message)
                    except:
                        pass
                
                # Stop web server
                await web_runner.cleanup()
                
                logger.info("👋 Au revoir!")
                break
                
            except Exception as e:
                logger.error(f"Erreur: {e}")
                await asyncio.sleep(10)
    
    def start_keep_alive(self):
        """Start keep-alive thread to prevent free hosting from sleeping"""
        def keep_alive():
            import requests
            import time
            while True:
                try:
                    # Self-ping to keep alive
                    requests.get(f"http://0.0.0.0:{PORT}/health", timeout=5)
                    time.sleep(300)  # Ping every 5 minutes
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
