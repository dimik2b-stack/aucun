import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Set
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

TELEGRAM_BOT_TOKEN = "8543416837:AAFc49U9V1xQE3ofuxSOjzvgmqKS8x3KOXA"
CONFIG_FILE = "whale_config_binance.json"
USER_SETTINGS_DIR = "user_settings"
PORT = int(os.environ.get("PORT", 8080))  # Pour Railway/Render/Heroku

# ================= COMPLETE TOKENS LIST =================
COMPLETE_TOKENS = {
    # ========== TOP 10 BY MARKET CAP ==========
    "BTC": {
        "mint": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",  # Wrapped Bitcoin (WBTC) on Solana
        "decimals": 8,
        "threshold_usd": 1000000,  # $1M threshold
        "category": "layer1"
    },
    "ETH": {
        "mint": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",  # Wrapped Ether (WETH) on Solana
        "decimals": 8,
        "threshold_usd": 500000,  # $500K threshold
        "category": "layer1"
    },
    "USDT": {
        "mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "decimals": 6,
        "threshold_usd": 500000,
        "category": "stablecoin"
    },
    "BNB": {
        "mint": "EPeUFDgHRxs9xxEPVaL6kfGQvCon7jmAWKVUHuux1Tpz",  # Wrapped BNB on Solana
        "decimals": 8,
        "threshold_usd": 300000,
        "category": "layer1"
    },
    "SOL": {
        "mint": "So11111111111111111111111111111111111111112",  # Native SOL
        "decimals": 9,
        "threshold_usd": 200000,
        "category": "layer1"
    },
    "XRP": {
        "mint": "H6aZ8C9Mh7Z8hL7wS1S9X1L1S9C1Z8L1S9C1Z8L1S9C1",  # Placeholder - need real mint
        "decimals": 6,
        "threshold_usd": 250000,
        "category": "payment"
    },
    "USDC": {
        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "decimals": 6,
        "threshold_usd": 500000,
        "category": "stablecoin"
    },
    "ADA": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",  # Placeholder
        "decimals": 6,
        "threshold_usd": 150000,
        "category": "layer1"
    },
    "AVAX": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",  # Placeholder
        "decimals": 8,
        "threshold_usd": 150000,
        "category": "layer1"
    },
    "DOGE": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",  # Placeholder
        "decimals": 8,
        "threshold_usd": 100000,
        "category": "memecoin"
    },
    
    # ========== ADDITIONAL MAJOR TOKENS ==========
    "DOT": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 10,
        "threshold_usd": 100000,
        "category": "layer0"
    },
    "TRX": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 6,
        "threshold_usd": 100000,
        "category": "layer1"
    },
    "LINK": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 8,
        "threshold_usd": 100000,
        "category": "oracle"
    },
    "MATIC": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 8,
        "threshold_usd": 100000,
        "category": "layer2"
    },
    "TON": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 9,
        "threshold_usd": 100000,
        "category": "layer1"
    },
    "DAI": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 8,
        "threshold_usd": 200000,
        "category": "stablecoin"
    },
    "SHIB": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 50000,
        "category": "memecoin"
    },
    "LTC": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 8,
        "threshold_usd": 75000,
        "category": "payment"
    },
    "BCH": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 8,
        "threshold_usd": 75000,
        "category": "payment"
    },
    "UNI": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 75000,
        "category": "defi"
    },
    "ATOM": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 6,
        "threshold_usd": 50000,
        "category": "layer0"
    },
    "XLM": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 7,
        "threshold_usd": 50000,
        "category": "payment"
    },
    
    # ========== POPULAR DEFI TOKENS ==========
    "AAVE": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 50000,
        "category": "defi"
    },
    "MKR": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 50000,
        "category": "defi"
    },
    "CRV": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 30000,
        "category": "defi"
    },
    "COMP": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 30000,
        "category": "defi"
    },
    "SNX": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 30000,
        "category": "defi"
    },
    
    # ========== MEME COINS ==========
    "PEPE": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 18,
        "threshold_usd": 25000,
        "category": "memecoin"
    },
    "FLOKI": {
        "mint": "A8L5aN8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
        "decimals": 9,
        "threshold_usd": 25000,
        "category": "memecoin"
    },
    "BONK": {
        "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "decimals": 5,
        "threshold_usd": 20000,
        "category": "memecoin"
    },
    "WIF": {
        "mint": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "decimals": 6,
        "threshold_usd": 20000,
        "category": "memecoin"
    },
    
    # ========== SOLANA ECOSYSTEM ==========
    "RAY": {
        "mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "decimals": 6,
        "threshold_usd": 30000,
        "category": "defi"
    },
    "ORCA": {
        "mint": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
        "decimals": 6,
        "threshold_usd": 30000,
        "category": "defi"
    },
    "JUP": {
        "mint": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        "decimals": 6,
        "threshold_usd": 30000,
        "category": "defi"
    },
    "PYTH": {
        "mint": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
        "decimals": 6,
        "threshold_usd": 30000,
        "category": "oracle"
    }
}

# ================= USER MANAGER =================
class UserManager:
    def __init__(self):
        self.settings_dir = USER_SETTINGS_DIR
        os.makedirs(self.settings_dir, exist_ok=True)
        self.active_users = {}  # chat_id -> UserSettings
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
        
        # Default settings for new user - enable all tokens by default
        default_settings = {
            "chat_id": chat_id,
            "enabled_tokens": list(COMPLETE_TOKENS.keys()),  # Enable ALL tokens by default
            "language": "fr",
            "alert_levels": {
                "mega": True,
                "huge": True,
                "large": True,
                "whale": True,
                "significant": True
            },
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        
        # Save default settings
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Created default settings for new user {chat_id}")
        except Exception as e:
            logger.error(f"Error saving default settings for {chat_id}: {e}")
            # Fallback to basic settings
            default_settings["enabled_tokens"] = ["BTC", "ETH", "USDT", "SOL"]
        
        return default_settings
    
    def save_user_settings(self, chat_id: str, settings: dict):
        """Save user settings"""
        settings_path = self.get_user_settings_path(chat_id)
        settings["last_active"] = datetime.now().isoformat()
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved settings for user {chat_id}")
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

# ================= CONFIG MANAGER (MULTI-USER) =================
class AutoConfig:
    def __init__(self, user_manager: UserManager):
        self.config_file = CONFIG_FILE
        self.last_modified = 0
        self.user_manager = user_manager
        self.config = self.load_config()
        logger.info("Configuration manager initialized")
    
    def load_config(self):
        """Load or create configuration with ALL tokens"""
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
        
        # Create new config with ALL tokens
        logger.info("Creating new config with all tokens...")
        default_config = {
            "tokens": COMPLETE_TOKENS,
            "created_at": datetime.now().isoformat(),
            "version": "4.0",
            "total_tokens": len(COMPLETE_TOKENS)
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

# ================= TELEGRAM BOT (MULTI-USER) =================
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
        
        # Language dictionaries
        self.texts = {
            "fr": {
                "welcome": "🤖 *WHALE RADAR BOT*\n\nBienvenue! Surveillez les grosses transactions en temps réel.",
                "menu": "📱 *MENU PRINCIPAL*",
                "add_token": "➕ Ajouter Token",
                "manage_tokens": "⚙️ Gérer Tokens",
                "settings": "⚙️ Paramètres",
                "stats": "📊 Mes Statistiques",
                "list_tokens": "📋 Mes Tokens",
                "threshold": "🎯 Modifier Seuil",
                "alert_levels": "🔔 Niveaux d'Alerte",
                "language": "🌍 Langue",
                "back": "⬅️ Retour",
                "save": "💾 Sauvegarder",
                "enabled": "✅ Activé",
                "disabled": "❌ Désactivé",
                "enable_all": "✅ Tout Activer",
                "disable_all": "❌ Tout Désactiver",
                "admin": "👑 Admin"
            },
            "en": {
                "welcome": "🤖 *WHALE RADAR BOT*\n\nWelcome! Monitor large transactions in real time.",
                "menu": "📱 *MAIN MENU*",
                "add_token": "➕ Add Token",
                "manage_tokens": "⚙️ Manage Tokens",
                "settings": "⚙️ Settings",
                "stats": "📊 My Statistics",
                "list_tokens": "📋 My Tokens",
                "threshold": "🎯 Change Threshold",
                "alert_levels": "🔔 Alert Levels",
                "language": "🌍 Language",
                "back": "⬅️ Back",
                "save": "💾 Save",
                "enabled": "✅ Enabled",
                "disabled": "❌ Disabled",
                "enable_all": "✅ Enable All",
                "disable_all": "❌ Disable All",
                "admin": "👑 Admin"
            }
        }
        
        # Admin users (add your chat IDs here)
        self.admin_users = ["7546736501"]  # Your original chat ID
        logger.info("Telegram Bot initialized")
    
    def get_text(self, key: str, lang: str = "fr") -> str:
        return self.texts.get(lang, {}).get(key, key)
    
    def get_user_lang(self, chat_id: str) -> str:
        user_settings = self.user_manager.get_user(chat_id)
        return user_settings.get("language", "fr")
    
    async def send(self, chat_id: str, text: str, reply_markup=None):
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
        user_tokens = self.config.get_tokens_for_user(chat_id)
        all_tokens = self.config.get_all_tokens()
        user_lang = self.get_user_lang(chat_id)
        
        menu_text = f"{self.get_text('welcome', user_lang)}\n\n"
        menu_text += f"👤 *Utilisateur:* {chat_id[:8]}...\n"
        menu_text += f"📊 *STATUS:* {len(user_tokens)}/{len(all_tokens)} tokens activés\n"
        menu_text += f"🌍 *LANGUE:* {'Français' if user_lang == 'fr' else 'English'}\n\n"
        menu_text += f"{self.get_text('menu', user_lang)}:"
        
        keyboard_buttons = [
            [{"text": self.get_text("add_token", user_lang), "callback_data": "add_token"}],
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
        
        # Add tokens for current page
        for symbol, info in sorted_tokens[start_idx:end_idx]:
            status = "✅" if symbol in enabled_tokens else "❌"
            threshold = info.get('threshold_usd', 0)
            btn_text = f"{status} {symbol} (${threshold:,})"
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
        
        text = f"🔔 *GESTION DES TOKENS*\n\n"
        text += f"Page {page+1}/{total_pages} - {len(sorted_tokens)} tokens au total\n"
        text += f"Cliquez pour activer/désactiver:\n✅ = Activé | ❌ = Désactivé"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_settings_menu(self, chat_id: str):
        """Send settings menu"""
        user_lang = self.get_user_lang(chat_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": self.get_text("alert_levels", user_lang), "callback_data": "alert_levels"}],
                [{"text": self.get_text("language", user_lang), "callback_data": "language_menu"}],
                [{"text": self.get_text("threshold", user_lang), "callback_data": "change_threshold"}],
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        text = f"⚙️ *PARAMÈTRES*\n\n"
        text += f"🌍 Langue: {'Français' if user_lang == 'fr' else 'English'}\n\n"
        text += f"Sélectionnez une option:"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_alert_levels_menu(self, chat_id: str):
        """Send alert levels configuration menu"""
        user_settings = self.user_manager.get_user(chat_id)
        alert_levels = user_settings.get("alert_levels", {})
        user_lang = self.get_user_lang(chat_id)
        
        keyboard_buttons = []
        levels = [
            ("mega", "🐋 MÉGA WHALE (20x+)"),
            ("huge", "🐳 WHALE ÉNORME (10-20x)"),
            ("large", "🐬 GROSSE WHALE (5-10x)"),
            ("whale", "🐟 WHALE (2-5x)"),
            ("significant", "🦈 GROSSE ACTIVITÉ (1-2x)")
        ]
        
        for level_id, level_name in levels:
            status = "✅" if alert_levels.get(level_id, True) else "❌"
            btn_text = f"{status} {level_name}"
            keyboard_buttons.append([
                {"text": btn_text, "callback_data": f"alert_{level_id}"}
            ])
        
        # Enable/Disable all alerts
        keyboard_buttons.append([
            {"text": "✅ Tout Activer", "callback_data": "enable_all_alerts"},
            {"text": "❌ Tout Désactiver", "callback_data": "disable_all_alerts"}
        ])
        
        keyboard_buttons.append([{"text": self.get_text("back", user_lang), "callback_data": "settings"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
        
        text = "🔔 *NIVEAUX D'ALERTE*\n\n"
        text += "Configurez les niveaux d'alerte à recevoir:\n"
        text += "(x = multiple du seuil)"
        
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
        
        text = "🌍 *LANGUE*\n\nSélectionnez votre langue:"
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
            btn_text = f"{symbol}: ${threshold:,}"
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
        
        text = f"🎯 *MODIFIER LES SEUILS*\n\n"
        text += f"Page {page+1}/{total_pages}\n"
        text += f"Sélectionnez un token pour modifier son seuil:"
        
        await self.send(chat_id, text, keyboard)
    
    async def send_admin_menu(self, chat_id: str):
        """Send admin menu"""
        user_lang = self.get_user_lang(chat_id)
        all_users = self.user_manager.get_all_users()
        
        text = f"👑 *MENU ADMIN*\n\n"
        text += f"👥 Utilisateurs totaux: {len(all_users)}\n"
        text += f"📊 Tokens configurés: {len(self.config.get_all_tokens())}\n\n"
        text += "Options d'administration:"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 Stats Globales", "callback_data": "admin_stats"}],
                [{"text": "👥 Liste Utilisateurs", "callback_data": "admin_users"}],
                [{"text": "🔄 Forcer Re-scan", "callback_data": "admin_rescan"}],
                [{"text": self.get_text("back", user_lang), "callback_data": "main_menu"}]
            ]
        }
        
        await self.send(chat_id, text, keyboard)
    
    async def process_callback(self, chat_id: str, callback_data: str):
        """Process callback queries from inline keyboards"""
        logger.info(f"Processing callback from {chat_id}: {callback_data}")
        self.bot_stats["commands_processed"] += 1
        
        user_lang = self.get_user_lang(chat_id)
        
        if callback_data == "main_menu":
            await self.send_main_menu(chat_id)
        
        elif callback_data == "add_token":
            await self.send_add_token_instructions(chat_id)
        
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
                    status = "❌ Désactivé"
                else:
                    # Enable token
                    enabled_tokens.append(symbol)
                    status = "✅ Activé"
                
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
            await self.answer_callback(chat_id, "✅ Tous les tokens activés")
            await self.send_token_management(chat_id)
        
        elif callback_data == "disable_all":
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["enabled_tokens"] = []
            self.user_manager.update_user(chat_id, user_settings)
            await self.answer_callback(chat_id, "❌ Tous les tokens désactivés")
            await self.send_token_management(chat_id)
        
        elif callback_data.startswith("alert_"):
            level = callback_data[6:]
            user_settings = self.user_manager.get_user(chat_id)
            alert_levels = user_settings.get("alert_levels", {})
            current_state = alert_levels.get(level, True)
            
            alert_levels[level] = not current_state
            user_settings["alert_levels"] = alert_levels
            self.user_manager.update_user(chat_id, user_settings)
            
            await self.answer_callback(chat_id, f"Level {level}: {'enabled' if not current_state else 'disabled'}")
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
            await self.answer_callback(chat_id, "✅ Tous les niveaux activés")
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
            await self.answer_callback(chat_id, "❌ Tous les niveaux désactivés")
            await self.send_alert_levels_menu(chat_id)
        
        elif callback_data.startswith("lang_"):
            lang = callback_data[5:]
            user_settings = self.user_manager.get_user(chat_id)
            user_settings["language"] = lang
            self.user_manager.update_user(chat_id, user_settings)
            
            lang_name = "Français" if lang == "fr" else "English"
            await self.answer_callback(chat_id, f"🌍 Langue: {lang_name}")
            await self.send_settings_menu(chat_id)
        
        elif callback_data.startswith("thresh_"):
            symbol = callback_data[7:]
            await self.ask_for_new_threshold(chat_id, symbol)
        
        elif callback_data == "admin_menu":
            if chat_id in self.admin_users:
                await self.send_admin_menu(chat_id)
        
        elif callback_data == "noop":
            # Do nothing for placeholder buttons
            pass
    
    async def ask_for_new_threshold(self, chat_id: str, symbol: str):
        """Ask user for new threshold value"""
        tokens = self.config.get_all_tokens()
        if symbol in tokens:
            current = tokens[symbol]['threshold_usd']
            self.waiting_for_threshold[chat_id] = symbol
            
            user_lang = self.get_user_lang(chat_id)
            
            text = f"🎯 *MODIFIER SEUIL - {symbol}*\n\n"
            text += f"Seuil actuel: **${current:,}**\n\n"
            text += "Envoyez le nouveau seuil en USD:\n"
            text += "Exemple: `100000` pour $100,000\n\n"
            text += "📝 *Minimum:* $10,000"
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🚫 Annuler", "callback_data": "change_threshold"}]
                ]
            }
            
            await self.send(chat_id, text, keyboard)
    
    async def answer_callback(self, chat_id: str, text: str):
        """Answer callback query with notification"""
        try:
            await self.send(chat_id, f"📱 {text}")
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
        
        # Group by category
        categories = {}
        for symbol, info in user_tokens.items():
            cat = info.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        text = f"📊 *MES STATISTIQUES*\n\n"
        text += f"👤 Utilisateur: {chat_id[:8]}...\n"
        text += f"📈 Tokens activés: **{enabled_count}/{total_count}**\n"
        text += f"💰 Total seuil: **${total_threshold:,}**\n"
        text += f"📊 Moyenne seuil: **${avg_threshold:,.0f}**\n"
        text += f"🌍 Langue: **{'Français' if user_lang == 'fr' else 'English'}**\n\n"
        
        text += "*📋 PAR CATÉGORIE:*\n"
        for cat, count in sorted(categories.items()):
            text += f"• {cat}: {count} tokens\n"
        
        # Show top 5 highest thresholds
        if user_tokens:
            top_tokens = sorted(user_tokens.items(), key=lambda x: x[1].get('threshold_usd', 0), reverse=True)[:5]
            text += f"\n*🏆 TOP 5 SEUILS:*\n"
            for i, (symbol, info) in enumerate(top_tokens, 1):
                threshold = info.get('threshold_usd', 0)
                text += f"{i}. **{symbol}**: ${threshold:,}\n"
        
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
            text += "Allez dans 'Gérer Tokens' pour activer des tokens."
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "⚙️ Gérer Tokens", "callback_data": "manage_tokens"}],
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
        
        text = f"📋 *MES TOKENS ACTIVÉS*\n\n"
        text += f"Page {page+1}/{total_pages} - {len(user_tokens)} tokens\n\n"
        
        # Group by category for current page
        page_tokens = sorted_tokens[start_idx:end_idx]
        by_category = {}
        
        for symbol, info in page_tokens:
            category = info.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((symbol, info))
        
        for category, token_list in sorted(by_category.items()):
            text += f"*{category.upper()}* ({len(token_list)})\n"
            
            for symbol, info in token_list:
                threshold = info.get('threshold_usd', 0)
                text += f"• **{symbol}**: ${threshold:,}\n"
            
            text += "\n"
        
        # Add pagination buttons if needed
        keyboard_buttons = []
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append({"text": "◀️ Précédent", "callback_data": f"list_page_{page-1}"})
            
            nav_buttons.append({"text": f"{page+1}/{total_pages}", "callback_data": "noop"})
            
            if page < total_pages - 1:
                nav_buttons.append({"text": "Suivant ▶️", "callback_data": f"list_page_{page+1}"})
            
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
        text += "`/add ADRESSE_MINT SEUIL_USD`\n\n"
        text += "2. Exemple:\n"
        text += "`/add EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 50000`\n\n"
        text += "3. Le bot détectera automatiquement:\n"
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
    
    async def handle_add_token(self, chat_id: str, mint: str, threshold_str: str):
        """Handle token addition"""
        try:
            threshold = int(threshold_str)
            
            if threshold < 10000:
                await self.send(chat_id, "⚠️ *Seuil minimum:* $10,000")
                return
            
            await self.send(chat_id, "🔍 *Analyse du token en cours...*")
            
            token_info = await self.get_token_info(mint)
            if not token_info["valid"]:
                await self.send(chat_id, "❌ *Token non trouvé sur DexScreener*")
                return
            
            symbol = token_info["symbol"]
            
            # Check if token already exists
            all_tokens = self.config.get_all_tokens()
            if symbol in all_tokens:
                await self.send(chat_id, f"⚠️ *{symbol} existe déjà!*\n"
                              f"Seuil actuel: ${all_tokens[symbol]['threshold_usd']:,}")
                return
            
            # Add to config
            new_token_info = {
                "mint": mint,
                "decimals": token_info["decimals"],
                "threshold_usd": threshold,
                "category": token_info.get("category", "other")
            }
            
            self.config.add_token(symbol, new_token_info)
            
            # Enable for this user
            user_settings = self.user_manager.get_user(chat_id)
            enabled_tokens = user_settings.get("enabled_tokens", [])
            if symbol not in enabled_tokens:
                enabled_tokens.append(symbol)
                user_settings["enabled_tokens"] = enabled_tokens
                self.user_manager.update_user(chat_id, user_settings)
            
            await self.send(chat_id, f"✅ *TOKEN AJOUTÉ*\n\n"
                          f"📛 **{symbol}**\n"
                          f"🎯 Seuil: **${threshold:,}**\n"
                          f"🔢 Décimales: {token_info['decimals']}\n"
                          f"📊 Catégorie: {token_info.get('category', 'other')}\n"
                          f"✅ Activé automatiquement")
            
            await self.send_main_menu(chat_id)
            
        except ValueError:
            await self.send(chat_id, "❌ Format invalide\nExemple: `/add ADRESSE 50000`")
    
    async def get_token_info(self, mint: str):
        """Fetch token information from DexScreener"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("pairs"):
                            pair = data["pairs"][0]
                            base_token = pair.get("baseToken", {})
                            
                            symbol = base_token.get("symbol", "UNKNOWN").upper()
                            decimals = base_token.get("decimals", 9)
                            price = float(pair.get("priceUsd", 0))
                            
                            # Detect category
                            category = self.detect_category(symbol, price)
                            
                            return {
                                "symbol": symbol,
                                "decimals": int(decimals),
                                "price": price,
                                "category": category,
                                "valid": True
                            }
        except Exception as e:
            logger.error(f"Error fetching token info: {e}")
        
        return {"valid": False}
    
    def detect_category(self, symbol: str, price: float) -> str:
        """Detect token category"""
        symbol_lower = symbol.lower()
        
        if symbol_lower in ['usdc', 'usdt', 'dai', 'busd', 'tusd', 'usdp']:
            return "stablecoin"
        
        if symbol_lower in ['btc', 'wbtc', 'eth', 'weth', 'sol', 'bnb', 'avax', 'dot', 'ada', 'matic', 'atom', 'apt', 'near', 'algo', 'xtz', 'eos', 'etc']:
            return "layer1"
        
        if price < 0.01 or symbol_lower in ['shib', 'doge', 'pepe', 'floki', 'bonk', 'wif']:
            return "memecoin"
        
        if symbol_lower in ['uni', 'aave', 'comp', 'mkr', 'jup', 'ray', 'orca', 'crv', 'snx']:
            return "defi"
        
        if symbol_lower in ['link', 'pyth']:
            return "oracle"
        
        if symbol_lower in ['xrp', 'ltc', 'bch', 'xlm']:
            return "payment"
        
        if symbol_lower in ['sand', 'mana', 'axs', 'gala']:
            return "gaming"
        
        if symbol_lower in ['fil', 'vet', 'icp']:
            return "enterprise"
        
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
                self.user_manager.get_user(chat_id)  # This creates user if doesn't exist
                await self.send_main_menu(chat_id)
            
            elif command == "/add" and len(parts) >= 3:
                await self.handle_add_token(chat_id, parts[1], parts[2])
            
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
            
            # ========== NOUVELLES COMMANDES TEXTUELLES ==========
            elif command == "/gérer" or command == "/manage":
                await self.send_token_management(chat_id)
            
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
                self.user_manager.update_user(chat_id, user_settings)
                await self.send(chat_id, f"✅ Tous les tokens activés ({len(all_tokens)} tokens)")
            
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
                    await self.send(chat_id, f"📊 *INFORMATIONS SUR {symbol}*\n\n"
                                  f"🎯 Seuil: **${info['threshold_usd']:,}**\n"
                                  f"🔢 Décimales: {info['decimals']}\n"
                                  f"📊 Catégorie: {info.get('category', 'unknown')}\n"
                                  f"🔗 Mint: `{info['mint'][:20]}...`")
                else:
                    await self.send(chat_id, f"❌ Token {symbol} non trouvé")
            
            elif command == "/search" and len(parts) >= 2:
                search_term = parts[1].upper()
                all_tokens = self.config.get_all_tokens()
                matches = [sym for sym in all_tokens.keys() if search_term in sym]
                if matches:
                    text = f"🔍 *RECHERCHE: '{search_term}'*\n\n"
                    text += f"Résultats trouvés: {len(matches)}\n\n"
                    for symbol in matches[:10]:  # Show first 10
                        info = all_tokens[symbol]
                        text += f"• **{symbol}** - ${info['threshold_usd']:,}\n"
                    if len(matches) > 10:
                        text += f"\n... et {len(matches)-10} autres"
                    await self.send(chat_id, text)
                else:
                    await self.send(chat_id, f"❌ Aucun token trouvé pour '{search_term}'")
            
            elif command == "/catégories" or command == "/categories":
                all_tokens = self.config.get_all_tokens()
                categories = {}
                for symbol, info in all_tokens.items():
                    cat = info.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                text = "📊 *CATÉGORIES DE TOKENS*\n\n"
                for cat, count in sorted(categories.items()):
                    text += f"• **{cat}**: {count} tokens\n"
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
        
        else:
            # Si c'est un message normal, envoyer le menu principal
            await self.send_main_menu(chat_id)
    
    async def show_global_stats(self, chat_id: str):
        """Show global bot statistics"""
        total_users = self.user_manager.get_user_count()
        total_tokens = len(self.config.get_all_tokens())
        uptime = datetime.now() - datetime.fromisoformat(self.bot_stats["start_time"])
        
        text = f"📊 *STATISTIQUES GLOBALES DU BOT*\n\n"
        text += f"🤖 *Bot:* Whale Radar v4.0\n"
        text += f"⏰ *Uptime:* {uptime.days} jours, {uptime.seconds//3600} heures\n"
        text += f"👥 *Utilisateurs:* {total_users}\n"
        text += f"📈 *Tokens configurés:* {total_tokens}\n"
        text += f"📨 *Messages reçus:* {self.bot_stats['messages_received']}\n"
        text += f"📤 *Messages envoyés:* {self.bot_stats['messages_sent']}\n"
        text += f"⚡ *Commandes traitées:* {self.bot_stats['commands_processed']}\n"
        text += f"🚨 *Alertes envoyées:* {self.bot_stats['alerts_sent']}\n\n"
        text += f"🔄 *Dernier scan:* {datetime.now().strftime('%H:%M:%S')}"
        
        await self.send(chat_id, text)
    
    async def send_help(self, chat_id: str):
        """Send help message"""
        user_lang = self.get_user_lang(chat_id)
        
        if user_lang == "fr":
            text = """
🤖 *WHALE RADAR BOT - AIDE COMPLÈTE*

📱 *MENU INTERACTIF:*
• Utilisez `/menu` pour le menu principal
• Cliquez sur les boutons pour naviguer

🔧 *COMMANDES PRINCIPALES:*
• `/menu` - Menu principal
• `/gérer` - Gérer les tokens
• `/paramètres` - Paramètres
• `/statistiques` - Mes statistiques
• `/tokens` - Liste mes tokens
• `/alertes` - Niveaux d'alerte
• `/langue` - Changer langue
• `/seuils` - Modifier seuils
• `/status` - Status du bot
• `/aide` - Cette aide

➕ *AJOUTER/SUPPRIMER:*
• `/add ADRESSE SEUIL` - Ajouter token
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

📊 *SCANNING:*
• Scan automatique toutes les 30 secondes
• Alertes uniquement pour tokens activés
• Volume calculé sur 5 minutes

🌍 *LANGUES:*
• Français: `/langue` puis 🇫🇷
• English: `/language` puis 🇬🇧

👑 *COMMANDES ADMIN:*
• `/admin` - Menu admin
• `/users` - Liste utilisateurs
• `/broadcast MESSAGE` - Envoyer à tous

💡 *ASTUCES:*
• Les menus disparaissent après 24h
• Utilisez les commandes textuelles si besoin
• Vous pouvez taper simplement "menu" pour réafficher

📞 *SUPPORT:*
Pour tout problème, contactez l'administrateur.
"""
        else:
            text = """
🤖 *WHALE RADAR BOT - COMPLETE HELP*

📱 *INTERACTIVE MENU:*
• Use `/menu` for main menu
• Click buttons to navigate

🔧 *MAIN COMMANDS:*
• `/menu` - Main menu
• `/manage` - Manage tokens
• `/settings` - Settings
• `/stats` - My statistics
• `/tokens` - List my tokens
• `/alerts` - Alert levels
• `/language` - Change language
• `/thresholds` - Modify thresholds
• `/status` - Bot status
• `/help` - This help

➕ *ADD/REMOVE:*
• `/add ADDRESS THRESHOLD` - Add token
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

📊 *SCANNING:*
• Auto scan every 30 seconds
• Alerts only for enabled tokens
• Volume calculated over 5 minutes

🌍 *LANGUAGES:*
• Français: `/language` then 🇫🇷
• English: `/language` then 🇬🇧

👑 *ADMIN COMMANDS:*
• `/admin` - Admin menu
• `/users` - User list
• `/broadcast MESSAGE` - Send to all

💡 *TIPS:*
• Menus disappear after 24h
• Use text commands if needed
• You can just type "menu" to show again

📞 *SUPPORT:*
For any issues, contact administrator.
"""
        await self.send(chat_id, text)

# ================= SCANNER (MULTI-USER) =================
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
            data = await self.get_token_data(token_info["mint"])
            if not data or not data.get("pairs"):
                return False
            
            pairs = data["pairs"]
            threshold = token_info["threshold_usd"]
            
            # Check first 3 pairs (usually most liquid)
            for pair in pairs[:3]:
                volume_5m = float(pair.get("volume", {}).get("m5", 0))
                
                if volume_5m >= threshold:
                    dex_id = pair.get("dexId", "Unknown")
                    price = float(pair.get("priceUsd", 0))
                    txns_5m = pair.get("txns", {}).get("m5", {})
                    buys = txns_5m.get("buys", 0)
                    sells = txns_5m.get("sells", 0)
                    
                    action = "BUY" if buys > sells else "SELL"
                    tx_count = buys if action == "BUY" else sells
                    
                    # Check alert level
                    ratio = volume_5m / threshold
                    level = self.get_alert_level(ratio)
                    
                    # Check if this level is enabled for user
                    user_settings = self.user_manager.get_user(chat_id)
                    alert_levels = user_settings.get("alert_levels", {})
                    if not alert_levels.get(level, True):
                        continue
                    
                    token_amount = volume_5m / price if price > 0 else 0
                    
                    await self.send_whale_alert(
                        chat_id=chat_id,
                        symbol=symbol,
                        token_info=token_info,
                        volume_usd=volume_5m,
                        price=price,
                        token_amount=token_amount,
                        action=action,
                        ratio=ratio,
                        level=level,
                        dex=dex_id,
                        pair_address=pair.get("pairAddress", "")
                    )
                    
                    self.telegram.bot_stats["alerts_sent"] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Scan error for {symbol} (user {chat_id}): {e}")
            return False
    
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
            "SELL": {"fr": "VENTE", "en": "SELL"}
        }
        
        whale_type = alert_texts.get(level, {}).get(user_lang, level)
        action_text = action_texts.get(action, {}).get(user_lang, action)
        action_emoji = "🟢" if action == "BUY" else "🔴"
        
        formatted_amount = self.format_number(token_amount, token_info["decimals"])
        formatted_volume = self.format_currency(volume_usd)
        threshold = token_info["threshold_usd"]
        category = token_info.get("category", "unknown").upper()
        
        if user_lang == "fr":
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

🏷️ *Token:* **{symbol}** ({category})
💰 *Montant:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Ratio seuil:* {ratio:.1f}x
🏷️  *Prix:* ${price:.6f}

📊 *Transactions:* {action_text} (5min)
🏦 *DEX:* {dex}
🔗 *Pair:* `{pair_address[:10]}...`

🎯 *Seuil config:* ${threshold:,}
📅 *Date:* {datetime.now().strftime('%d/%m/%Y')}
⏰ *Heure:* {datetime.now().strftime('%H:%M:%S')}

#WhaleAlert #{symbol} #{action} #{category} #{level}
"""
        else:
            message = f"""
{action_emoji} *{whale_type} {action_text}* 🚨

🏷️ *Token:* **{symbol}** ({category})
💰 *Amount:* {formatted_amount} {symbol}
💵 *Volume:* **{formatted_volume}**
📈 *Threshold ratio:* {ratio:.1f}x
🏷️ *Price:* ${price:.6f}

📊 *Transactions:* {action_text} (5min)
🏦 *DEX:* {dex}
🔗 *Pair:* `{pair_address[:10]}...`

🎯 *Config threshold:* ${threshold:,}
📅 *Date:* {datetime.now().strftime('%m/%d/%Y')}
⏰ *Time:* {datetime.now().strftime('%H:%M:%S')}

#WhaleAlert #{symbol} #{action} #{category} #{level}
"""
        
        await self.telegram.send(chat_id, message)
        self.alert_count += 1
        
        logger.info(f"🚨 ALERT for {chat_id}: {symbol} {action} {formatted_volume}")
    
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
    
    async def get_token_data(self, mint: str):
        """Fetch token data from DexScreener"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Error fetching token data: {e}")
        return None
    
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
                logger.info(f"🔍 SCAN #{self.scan_counter} - Scanning for {len(active_users)} active users")
                
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
                    logger.info(f"📊 Scan stats: {self.scan_counter} scans, {self.alert_count} total alerts")
            
            self.last_scan_time = current_time

# ================= WEB SERVER (FOR RAILWAY/RENDER/HEROKU) =================
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
                               "👥 Users: Active\n"
                               "🚨 Alerts: Enabled\n\n"
                               "Use /start in Telegram to begin.")
    
    async def handle_health(self, request):
        """Handle health check endpoint"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "Whale Radar",
            "version": "4.0",
            "users": self.bot.user_manager.get_user_count(),
            "tokens": len(self.bot.config.get_all_tokens()),
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
            "uptime": str(datetime.now() - datetime.fromisoformat(self.bot.telegram.bot_stats["start_time"])),
            "last_scan": self.bot.scanner.last_scan_time
        }
        return web.json_response(stats_data)
    
    async def handle_users(self, request):
        """Handle users endpoint (admin only)"""
        # Simple auth check (you can improve this)
        auth_token = request.query.get('token', '')
        if auth_token != "admin123":  # Change this to a secure token
            return web.Response(text="Unauthorized", status=401)
        
        users = self.bot.user_manager.get_all_users()
        return web.json_response({
            "total_users": len(users),
            "users": users[:50]  # Return first 50 users
        })
    
    async def handle_webhook(self, request):
        """Handle Telegram webhook (if configured)"""
        try:
            data = await request.json()
            # Process webhook update
            # This would require setting up webhook with Telegram
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
        logger.info("Whale Radar Bot initialized")
    
    async def run(self):
        """Main bot loop"""
        logger.info("=" * 80)
        logger.info("🤖 WHALE RADAR BOT - MULTI-USER VERSION")
        logger.info("=" * 80)
        
        # Get initial stats
        all_tokens = self.config.get_all_tokens()
        all_users = self.user_manager.get_all_users()
        
        logger.info(f"✅ Configuration loaded")
        logger.info(f"📊 Total tokens: {len(all_tokens)}")
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
                await self.telegram.send(admin_id, "🤖 *WHALE RADAR BOT DÉMARRÉ*\n\nLe bot est maintenant opérationnel 24/7 sur serveur gratuit!")
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
    logger.info("🤖 Initializing WHALE RADAR BOT (Multi-User)...")
    
    bot = WhaleRadarBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Programme terminé")
    except Exception as e:
        logger.error(f"\n❌ Erreur: {e}")

# ================= DEPLOYMENT FILES =================

"""
Fichiers nécessaires pour déploiement sur serveur gratuit:

1. requirements.txt
aiohttp==3.9.1
asyncio==3.4.3

2. railway.json (pour Railway.app)
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python whale_bot.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE"
  }
}

3. render.yaml (pour Render.com)
services:
  - type: web
    name: whale-radar-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python whale_bot.py
    envVars:
      - key: PORT
        value: 8080
    healthCheckPath: /health

4. Procfile (pour Heroku)
web: python whale_bot.py

5. runtime.txt (pour Heroku)
python-3.11.0

Instructions de déploiement:

1. Railway.app (RECOMMANDÉ - Gratuit):
   - Créez un compte sur railway.app
   - Créez un nouveau projet
   - Importez depuis GitHub ou upload les fichiers
   - Ajoutez la variable d'environnement PORT
   - Le bot sera déployé automatiquement

2. Render.com (Gratuit):
   - Créez un compte sur render.com
   - Créez un nouveau "Web Service"
   - Connectez votre dépôt GitHub
   - Utilisez les configurations ci-dessus
   - Déployez

3. Heroku (Gratuit avec limitations):
   - Installez Heroku CLI
   - `heroku create`
   - `git push heroku main`
   - Le bot sera déployé

Le bot sera maintenant en ligne 24/7 !
"""
