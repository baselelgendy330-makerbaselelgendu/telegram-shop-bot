#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIX Store Bot - Complete Single File
=====================================
Shop bot for selling CDK ChatGPT codes with Binance Pay auto-verification.

Env vars:
    BOT_TOKEN           - from @BotFather
    DATABASE_URL        - SQLite file path (default: aix_store.db)
    BINANCE_API_KEY     - from binance.com API Management
    BINANCE_API_SECRET  - from binance.com API Management

Install: pip install aiogram==3.12.0 aiosqlite==0.20.0 aiohttp==3.9.5
Run:     python bot.py
"""


################################################################################
# CONFIG
################################################################################

"""
AIX Store Bot - Configuration
=============================
All centralized configuration settings.
"""
import os

# ═══════════════════════════════════════════════════════════
# Bot Core Settings
# ═══════════════════════════════════════════════════════════
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "aix_store.db")
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"
SUPPORT = "@VNV_I"

# ═══════════════════════════════════════════════════════════
# Admin Settings
# ═══════════════════════════════════════════════════════════
ADMIN_IDS = [6728595587, 7469507752]

# ═══════════════════════════════════════════════════════════
# Channel & Bot Links
# ═══════════════════════════════════════════════════════════
CHANNEL_USERNAME = "@CDKK12_CHATGPT"
BOT_USERNAME = "Shop_chatgptplus_bot"

# ═══════════════════════════════════════════════════════════
# Payment Settings
# ═══════════════════════════════════════════════════════════
BINANCE_ID = "381880403"
BEP20_ADDRESS = "0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa"

# Binance Regular Account API (for auto-verification of Pay transfers)
# Create from: https://www.binance.com/en/my/settings/api-management
# Required permissions: "Enable Reading" (for transaction history)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Cryptomus Payment API
CRYPTOMUS_API_KEY = os.getenv("CRYPTOMUS_API_KEY")
CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID")
CRYPTOMUS_WEBHOOK_SECRET = os.getenv("CRYPTOMUS_WEBHOOK_SECRET")

# Referral Settings
REFERRAL_REWARD_AMOUNT = 0.50  # USDT per 10 referrals
REFERRAL_THRESHOLD = 10

# ═══════════════════════════════════════════════════════════
# Media Assets
# ═══════════════════════════════════════════════════════════
AIX_HEADER_IMAGE = os.getenv(
    "AIX_HEADER_IMAGE",
    "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png",
)
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")
CDK_IMAGE_FILE = "https://i.postimg.cc/dQ7m0g1R/IMG-20260620-151545-816.jpg"

# ═══════════════════════════════════════════════════════════
# Product Definitions
# ═══════════════════════════════════════════════════════════
CDK_DESC = (
    "✅ ChatGPT K12 Edu 2-year package.\nFull of latest languages like Plus\n"
    "✅ Can activate any account owner. ⚠️ Applies to <b>Gmail ONLY</b>. "
    "(We are not responsible if you use other emails)\n"
    "✅ After ordering, you will receive a code\n✅ Account is on free plan\n"
    "✅ Recommended to use an account without an active subscription or a newly created account to register.\n"
    "✅ Web upgrade CDK: https://oaiteam.azx.us/\n"
    "Step 1: Get https://chatgpt.com/api/auth/session Paste into JSon\n"
    "Step 2: Paste the CDK\nStep 3: Upgrade, guys."
)

CDK_SINGLE_DESC = CDK_DESC + "\n\n⚠️ <b>NOTE:</b> This product is sold with <b>NO WARRANTY</b>."

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title": "CDK GPT Plus (K12 - EDU) 2 years",
        "image": CDK_IMAGE_FILE,
        "usd": 4.0,
        "type": "stock",
        "min_qty": 10,
        "desc": CDK_DESC,
    },
    "cdk_chatgpt_single": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title": "CDK (K12) FOR SINGLE",
        "image": CDK_IMAGE_FILE,
        "usd": 5.5,
        "type": "stock",
        "min_qty": 1,
        "desc": CDK_SINGLE_DESC,
    },
}

# ═══════════════════════════════════════════════════════════
# Emoji Mapping (Custom + Fallback)
# ═══════════════════════════════════════════════════════════
EMOJI = {
    "cart": "5312361253610475399",
    "back": "6181245923708903693",
    "wallet": "6088990159334808217",
    "binance": "5354924237779909158",
    "share": "6089193719309801680",
    "support": "6181322172263308706",
    "checkout": "5352662091390008496",
    "quantity": "5411271889421086677",
    "price": "5879991085001871624",
    "pencil": "5395444784611480792",
    "loading": "5341715473882955310",
    "user": "6183624639806185325",
    "camera": "5976761770537129878",
    "success": "5976395560150636003",
    "error": "6181467651395558500",
    "chatgpt": "5359726582447487916",
    "refresh": "5386367538735104399",
    "store": "5859297284029681680",
    "vip": "6088920147072915408",
    "verified": "5976653524476368012",
    "stock": "5397916757333654639",
    "sold": "5429651785352501917",
    "announcement": "5395695537687123235",
    "heart": "5364201435858744869",
    "support_msg": "5443038326535759644",
    "telegram": "6089099509202164251",
    "arrow_right": "6181684276661066306",
    "users_group": "4942888689131848546",
    "money_fly": "5816492162488995555",
    "link_pin": "5332724926216428039",
    "quotes": "5460795800101594035",
    "search": "5231012545799666522",
    "hourglass": "5386367538735104399",
    "check_anim": "6276090299232031662",
    "user_link": "5440410042773824003",
    "usdt": "5879991085001871624",
    # Group Emojis (Sales)
    "buy_cart": "5312361253610475399",
    "sparkles_pay": "5409048419211682843",
    "diamond_arrow": "5416117059207572332",
    "secure_shield": "5251203410396458957",
    "user_new": "5262742999678329061",
    # Group Emojis (Referrals)
    "ref_trend": "5244837092042750681",
    "ref_check": "5206607081334906820",
    "ref_hourglass": "5386367538735104399",
}

SAFE_EMOJI_FALLBACK = {
    "cart": "🛒",
    "back": "🔙",
    "wallet": "💰",
    "binance": "🟡",
    "share": "🎁",
    "support": "🎧",
    "checkout": "💳",
    "quantity": "📦",
    "price": "💵",
    "pencil": "✏️",
    "loading": "⏳",
    "user": "👤",
    "camera": "📸",
    "success": "✅",
    "error": "❌",
    "chatgpt": "🤖",
    "refresh": "🔄",
    "store": "🛍",
    "stock": "➕",
    "sold": "↗️",
    "support_msg": "💬",
    "telegram": "⚡",
    "arrow_right": "➡️",
    "users_group": "👥",
    "money_fly": "💸",
    "link_pin": "📇",
    "quotes": "🗣️",
    "search": "🔍",
    "hourglass": "⌛",
    "announcement": "🚨",
    "check_anim": "✅",
    "user_link": "🔗",
    "usdt": "💵",
    "buy_cart": "🛒",
    "sparkles_pay": "💵",
    "diamond_arrow": "➡️",
    "secure_shield": "🛡",
    "user_new": "👤",
    "ref_trend": "📈",
    "ref_check": "✔️",
    "ref_hourglass": "⌛",
}


################################################################################
# UTILS
################################################################################

"""
AIX Store Bot - Utilities
=========================
Helper functions for emoji formatting, safe messaging, etc.
"""
import html
import re
import os

from aiogram.types import Message, URLInputFile, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from config import EMOJI, SAFE_EMOJI_FALLBACK, AIX_HEADER_IMAGE, AIX_HEADER_FILE


def ce(key: str, fallback: str = "") -> str:
    """Get custom emoji with safe fallback."""
    emoji_id = EMOJI.get(key)
    safe_fallback = SAFE_EMOJI_FALLBACK.get(key, fallback or "✅")
    if not emoji_id or not str(emoji_id).isdigit():
        return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'


def esc(value) -> str:
    """Escape HTML characters."""
    return html.escape(str(value), quote=False)


def strip_custom_emoji(text: str) -> str:
    """Strip custom emoji tags, leaving only fallback emoji."""
    return re.sub(
        r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r"\1", text
    )


def format_amount(amount) -> str:
    """Format numeric amount cleanly."""
    try:
        return (
            str(int(amount))
            if float(amount).is_integer()
            else str(amount).rstrip("0").rstrip(".")
        )
    except Exception:
        return str(amount)


async def safe_answer(message: Message, text: str, reply_markup=None):
    """Safely answer a message with emoji fallback on error."""
    try:
        return await message.answer(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )
    except TelegramBadRequest:
        return await message.answer(
            strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML"
        )


async def safe_edit_or_answer(message, text: str, reply_markup=None):
    """Safely edit text or answer if media message."""
    try:
        if (
            getattr(message, "photo", None)
            or getattr(message, "video", None)
            or getattr(message, "document", None)
        ):
            try:
                await message.delete()
            except Exception:
                pass
            return await message.answer(
                text, reply_markup=reply_markup, parse_mode="HTML"
            )
        return await message.edit_text(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return message
        try:
            return await message.edit_text(
                strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML"
            )
        except Exception:
            return await message.answer(
                strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML"
            )
    except Exception:
        return await safe_answer(message, text, reply_markup)


async def safe_answer_photo(message: Message, caption: str, reply_markup=None):
    """Safely send photo with caption, falling back to text on error."""
    try:
        if os.path.exists(AIX_HEADER_FILE):
            return await message.answer_photo(
                photo=FSInputFile(AIX_HEADER_FILE),
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        return await message.answer_photo(
            photo=URLInputFile(AIX_HEADER_IMAGE),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        try:
            if os.path.exists(AIX_HEADER_FILE):
                return await message.answer_photo(
                    photo=FSInputFile(AIX_HEADER_FILE),
                    caption=strip_custom_emoji(caption),
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            return await message.answer_photo(
                photo=URLInputFile(AIX_HEADER_IMAGE),
                caption=strip_custom_emoji(caption),
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        except Exception:
            return await message.answer(
                strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML"
            )
    except Exception:
        return await message.answer(
            strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML"
        )


################################################################################
# DATABASE
################################################################################

"""
AIX Store Bot - Database Layer (SQLite)
========================================
All database operations centralized using aiosqlite.
"""
import aiosqlite
from typing import Optional

from config import DATABASE_URL

_db: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """Get or create database connection."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DATABASE_URL)
        _db.row_factory = aiosqlite.Row
    return _db


async def close_db():
    """Close database connection."""
    global _db
    if _db:
        await _db.close()
        _db = None


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    # Users table
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance_usdt REAL DEFAULT 0,
            referred_by INTEGER,
            total_ref INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            ref_counted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Deposits/Orders table
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            method TEXT,
            amount REAL,
            currency TEXT,
            product_key TEXT DEFAULT 'cdk_chatgpt',
            status TEXT DEFAULT 'pending',
            quantity INTEGER DEFAULT 1,
            txid TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Stock table
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            item_data TEXT NOT NULL,
            sold INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Payments table
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            order_id TEXT UNIQUE NOT NULL,
            cryptomus_uuid TEXT,
            product_key TEXT,
            quantity INTEGER DEFAULT 1,
            amount REAL,
            currency TEXT DEFAULT 'USDT',
            method TEXT DEFAULT 'cryptomus',
            status TEXT DEFAULT 'pending',
            txid TEXT,
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    await db.commit()


# ═══════════════════════════════════════════════════════════
# User Operations
# ═══════════════════════════════════════════════════════════


async def get_user(user_id: int) -> Optional[aiosqlite.Row]:
    """Get user by Telegram ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    return await cursor.fetchone()


async def create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    referrer_id: Optional[int] = None,
):
    """Create a new user."""
    db = await get_db()
    existing = await get_user(user_id)
    if existing:
        return
    
    if referrer_id and referrer_id != user_id:
        ref_exists = await db.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?", (referrer_id,)
        )
        if await ref_exists.fetchone():
            await db.execute(
                """
                INSERT INTO users (telegram_id, username, first_name, referred_by, ref_counted)
                VALUES (?, ?, ?, ?, 0)
                """,
                (user_id, username, first_name, referrer_id),
            )
            await db.commit()
            return
    
    await db.execute(
        "INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
        (user_id, username, first_name),
    )
    await db.commit()


async def update_user_info(user_id: int, username: str, first_name: str):
    """Update user's username and first_name."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET username = ?, first_name = ? WHERE telegram_id = ?",
        (username, first_name, user_id),
    )
    await db.commit()


async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT is_banned FROM users WHERE telegram_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return bool(row and row["is_banned"])


async def set_ban_status(user_id: int, banned: bool):
    """Ban or unban a user."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET is_banned = ? WHERE telegram_id = ?",
        (1 if banned else 0, user_id),
    )
    await db.commit()


async def get_user_stats(user_id: int) -> Optional[aiosqlite.Row]:
    """Get user stats (balance, total_ref)."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT balance_usdt, total_ref FROM users WHERE telegram_id = ?", (user_id,)
    )
    return await cursor.fetchone()


async def get_balance(user_id: int) -> float:
    """Get user's wallet balance."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT balance_usdt FROM users WHERE telegram_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return float(row["balance_usdt"]) if row and row["balance_usdt"] else 0.0


async def add_balance(user_id: int, amount: float):
    """Add (or deduct if negative) balance from user."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET balance_usdt = balance_usdt + ? WHERE telegram_id = ?",
        (amount, user_id),
    )
    await db.commit()


async def deduct_balance(user_id: int, amount: float):
    """Deduct balance from user."""
    await add_balance(user_id, -amount)


# ═══════════════════════════════════════════════════════════
# Referral Operations
# ═══════════════════════════════════════════════════════════


async def process_referral_reward(user_id: int) -> dict:
    """Process pending referral reward."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT referred_by, ref_counted FROM users WHERE telegram_id = ?", (user_id,)
    )
    user = await cursor.fetchone()
    
    if not user or not user["referred_by"] or user["ref_counted"]:
        return {"processed": False}

    referrer_id = user["referred_by"]

    # Activate referral
    await db.execute(
        "UPDATE users SET ref_counted = 1 WHERE telegram_id = ?", (user_id,)
    )
    # Increment referrer's count
    await db.execute(
        "UPDATE users SET total_ref = total_ref + 1 WHERE telegram_id = ?",
        (referrer_id,),
    )
    await db.commit()

    # Get new total
    cursor = await db.execute(
        "SELECT total_ref FROM users WHERE telegram_id = ?", (referrer_id,)
    )
    ref_row = await cursor.fetchone()
    new_total_ref = ref_row["total_ref"] if ref_row else 0

    from config import REFERRAL_REWARD_AMOUNT, REFERRAL_THRESHOLD

    reward_earned = new_total_ref > 0 and new_total_ref % REFERRAL_THRESHOLD == 0
    if reward_earned:
        await db.execute(
            "UPDATE users SET balance_usdt = balance_usdt + ? WHERE telegram_id = ?",
            (REFERRAL_REWARD_AMOUNT, referrer_id),
        )
        await db.commit()

    more_to_earn = REFERRAL_THRESHOLD - (new_total_ref % REFERRAL_THRESHOLD)

    return {
        "processed": True,
        "referrer_id": referrer_id,
        "new_total_ref": new_total_ref,
        "reward_earned": reward_earned,
        "more_to_earn": more_to_earn,
    }


# ═══════════════════════════════════════════════════════════
# Stock Operations
# ═══════════════════════════════════════════════════════════


async def get_stock_count(product_key: str = "cdk_chatgpt") -> int:
    """Get available stock count for a product."""
    from config import PRODUCTS
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) FROM stock WHERE product = ? AND sold = 0",
        (product["stock_name"],),
    )
    row = await cursor.fetchone()
    return row[0] or 0


async def get_total_sold(product_name: str) -> int:
    """Get total sold count for a product."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) FROM stock WHERE product = ? AND sold = 1", (product_name,)
    )
    row = await cursor.fetchone()
    return row[0] or 0


async def reserve_stock(product_name: str, qty: int):
    """Reserve stock items (mark as sold). Returns list of items."""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT id, item_data FROM stock
        WHERE product = ? AND sold = 0
        ORDER BY id ASC LIMIT ?
        """,
        (product_name, qty),
    )
    items = await cursor.fetchall()
    if len(items) < qty:
        return None
    
    ids = [i["id"] for i in items]
    placeholders = ",".join(["?"] * len(ids))
    await db.execute(
        f"UPDATE stock SET sold = 1 WHERE id IN ({placeholders})",
        ids,
    )
    await db.commit()
    return items


async def add_stock_items(product_name: str, items: list[str]) -> int:
    """Add stock items. Returns count added."""
    db = await get_db()
    for item in items:
        await db.execute(
            "INSERT INTO stock (product, item_data) VALUES (?, ?)",
            (product_name, item),
        )
    await db.commit()
    return len(items)


async def pull_stock_items(product_name: str, qty: int):
    """Pull stock items for admin. Returns list of items or None."""
    return await reserve_stock(product_name, qty)


async def get_available_stock(product_name: str) -> int:
    """Get available stock count."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) FROM stock WHERE product = ? AND sold = 0",
        (product_name,),
    )
    row = await cursor.fetchone()
    return row[0] or 0


# ═══════════════════════════════════════════════════════════
# Order/Deposit Operations
# ═══════════════════════════════════════════════════════════


async def create_order(
    user_id: int,
    method: str,
    amount: float,
    currency: str,
    product_key: str,
    qty: int,
    txid: str,
    status: str = "pending",
):
    """Create a new order/deposit record."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO deposits (telegram_id, method, amount, currency, product_key, status, quantity, txid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, method, amount, currency, product_key, status, qty, txid),
    )
    await db.commit()


async def get_all_users() -> list:
    """Get all users for broadcast."""
    db = await get_db()
    cursor = await db.execute("SELECT telegram_id FROM users")
    return await cursor.fetchall()


# ═══════════════════════════════════════════════════════════
# Payment Operations (Binance Auto-Pay)
# ═══════════════════════════════════════════════════════════


async def create_binance_order_record(
    user_id: int,
    order_id: str,
    product_key: str,
    qty: int,
    amount: float,
    binance_merchant_trade_no: str = None,
) -> None:
    """Create a Binance Pay order record."""
    db = await get_db()
    await db.execute(
        """
        INSERT OR IGNORE INTO payments (telegram_id, order_id, product_key, quantity, amount, currency, method, status, txid)
        VALUES (?, ?, ?, ?, ?, 'USDT', 'binance_auto', 'awaiting_payment', ?)
        """,
        (user_id, order_id, product_key, qty, amount, binance_merchant_trade_no),
    )
    await db.commit()


async def update_binance_order_txid(order_id: str, txid: str) -> None:
    """Update order with user's submitted TXID."""
    db = await get_db()
    await db.execute(
        """
        UPDATE payments SET txid = ?, status = 'verifying'
        WHERE order_id = ? AND status = 'awaiting_payment'
        """,
        (txid, order_id),
    )
    await db.commit()


async def get_payment_by_order(order_id: str) -> Optional[aiosqlite.Row]:
    """Get payment record by order_id."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,))
    return await cursor.fetchone()


async def get_binance_order_by_txid(txid: str) -> Optional[aiosqlite.Row]:
    """Get order by TXID."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM payments WHERE txid = ? ORDER BY created_at DESC LIMIT 1",
        (txid,),
    )
    return await cursor.fetchone()


async def mark_binance_order_delivered(order_id: str) -> None:
    """Mark Binance order as delivered."""
    db = await get_db()
    await db.execute(
        "UPDATE payments SET status = 'delivered', paid_at = CURRENT_TIMESTAMP WHERE order_id = ?",
        (order_id,),
    )
    await db.commit()


async def update_payment_status(order_id: str, status: str) -> None:
    """Update payment status."""
    db = await get_db()
    if status in ("paid", "paid_over"):
        await db.execute(
            "UPDATE payments SET status = ?, paid_at = CURRENT_TIMESTAMP WHERE order_id = ?",
            (status, order_id),
        )
    else:
        await db.execute(
            "UPDATE payments SET status = ? WHERE order_id = ?",
            (status, order_id),
        )
    await db.commit()


################################################################################
# KEYBOARDS
################################################################################

"""
AIX Store Bot - Keyboards
=========================
All inline and reply keyboard definitions.
"""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import EMOJI, PRODUCTS
from utils import format_amount, ce


def home_keyboard() -> InlineKeyboardMarkup:
    """Main menu inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Browse Products",
                    callback_data="home_shop",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Deposit",
                    callback_data="home_deposit",
                ),
                InlineKeyboardButton(
                    text="Wallet / Profile",
                    callback_data="home_wallet",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Support",
                    callback_data="home_support",
                ),
                InlineKeyboardButton(
                    text="Share & Earn",
                    callback_data="home_share",
                ),
            ],
        ]
    )


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Products"), KeyboardButton(text="🎧 Support")],
            [KeyboardButton(text="💰 Wallet"), KeyboardButton(text="🎁 Share & Earn")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def back_home_keyboard() -> InlineKeyboardMarkup:
    """Back to main menu button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Main Menu",
                    callback_data="home_main",
                )
            ]
        ]
    )


def product_buttons(stock_count: int) -> InlineKeyboardMarkup:
    """Product listing buttons."""
    chatgpt_icon = EMOJI.get("chatgpt", "🤖")
    error_icon = EMOJI.get("error", "❌")
    refresh_icon = EMOJI.get("refresh", "🔄")
    back_icon = EMOJI.get("back", "🔙")

    btn_1 = InlineKeyboardButton(
        text=f"CDK GPT Plus (10+) | $4.00 | Stock: {stock_count}",
        callback_data="product_cdk_chatgpt",
    )
    btn_2 = InlineKeyboardButton(
        text=f"CDK (K12) FOR SINGLE | $5.50 | Stock: {stock_count}",
        callback_data="product_cdk_chatgpt_single",
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_1],
            [btn_2],
            [
                InlineKeyboardButton(
                    text="🔄 Refresh Stock",
                    callback_data="refresh_products",
                ),
                InlineKeyboardButton(
                    text="◀️ Back",
                    callback_data="home_main",
                ),
            ],
        ]
    )


def product_details_buttons(product_key: str) -> InlineKeyboardMarkup:
    """Product details with Buy button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ce('cart')} Buy Now",
                    callback_data=f"buy_{product_key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('back')} Back to Shop",
                    callback_data="home_shop",
                )
            ],
        ]
    )


def checkout_payment_buttons(product_key: str, qty: int) -> InlineKeyboardMarkup:
    """Payment method selection for checkout."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ce('wallet')} Pay from Wallet",
                    callback_data=f"pay_wallet_{product_key}_{qty}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"⚡ Binance Pay (Auto)",
                    callback_data=f"pay_binance_auto_{product_key}_{qty}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('binance')} Binance Pay (Manual)",
                    callback_data=f"pay_binance_{product_key}_{qty}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('usdt')} USDT (BEP20) Pay",
                    callback_data=f"pay_bep20_{product_key}_{qty}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('back')} Back",
                    callback_data=f"back_to_prod_{product_key}",
                )
            ],
        ]
    )


def deposit_currency_buttons() -> InlineKeyboardMarkup:
    """Deposit currency selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ce('price')} USDT Deposit",
                    callback_data="deposit_currency_USDT",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('back')} Back",
                    callback_data="home_main",
                )
            ],
        ]
    )


def deposit_payment_buttons(amount: float, currency: str) -> InlineKeyboardMarkup:
    """Deposit payment method selection."""
    amt_str = format_amount(amount)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ce('binance')} Binance Pay • {amt_str} {currency}",
                    callback_data=f"topup_binance_{amt_str}_{currency}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('usdt')} USDT (BEP20) • {amt_str} {currency}",
                    callback_data=f"topup_bep20_{amt_str}_{currency}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('pencil')} Change Amount",
                    callback_data="deposit_currency_USDT",
                )
            ],
        ]
    )


def wallet_keyboard() -> InlineKeyboardMarkup:
    """Wallet profile keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ce('wallet')} Deposit",
                    callback_data="home_deposit",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{ce('refresh')} Refresh",
                    callback_data="home_wallet",
                ),
                InlineKeyboardButton(
                    text=f"{ce('back')} Main Menu",
                    callback_data="home_main",
                ),
            ],
        ]
    )


def force_subscribe_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Force subscribe keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Join Channel",
                    url=f"https://t.me/{channel_url.replace('@', '')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Check Subscription",
                    callback_data="check_sub",
                )
            ],
        ]
    )


def admin_send_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    """Admin send code to customer keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Send Code to Customer",
                    callback_data=f"sendprod_{target_user_id}",
                )
            ]
        ]
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel keyboard for input states."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Cancel")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def quantity_keyboard(is_single: bool = False) -> ReplyKeyboardMarkup:
    """Quantity selection keyboard."""
    if is_single:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
                [KeyboardButton(text="4"), KeyboardButton(text="5")],
                [KeyboardButton(text="❌ Cancel")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="50")],
                [KeyboardButton(text="100"), KeyboardButton(text="200")],
                [KeyboardButton(text="❌ Cancel")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )


########################################


################################################################################
# BINANCE_PAY_SERVICE
################################################################################

"""
AIX Store Bot - Binance Pay Verification (Regular Account)
===========================================================
Verifies Binance Pay transfers received on a REGULAR Binance account.

Uses Binance API to check recent Pay transactions and match them
with user-submitted Order IDs.

Required env vars:
    BINANCE_API_KEY       - from Binance API Management
    BINANCE_API_SECRET    - from Binance API Management

How to create API keys:
1. Login to Binance.com
2. Go to Profile → API Management
3. Create new API (give name like "bot_verify")
4. Enable ONLY: "Enable Reading" + "Enable Spot & Margin Trading" (for pay history)
5. Restrict to trusted IP (optional but recommended)
"""
import hashlib
import hmac
import time
import urllib.parse
from typing import Optional

import aiohttp

from config import BINANCE_API_KEY, BINANCE_API_SECRET

BASE_URL = "https://api.binance.com"


def _sign_query(params: dict) -> str:
    """
    Binance API signature using HMAC-SHA256.
    """
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(
        BINANCE_API_SECRET.encode(),
        query_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    return signature


async def _get(endpoint: str, params: dict = None, signed: bool = True) -> dict:
    """
    Send a signed GET request to Binance API.
    """
    url = f"{BASE_URL}{endpoint}"
    params = params or {}

    if signed:
        params["timestamp"] = int(time.time() * 1000)
        params["signature"] = _sign_query(params)

    headers = {
        "X-MBX-APIKEY": BINANCE_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            result = await resp.json()
            if resp.status != 200:
                error_msg = result.get("msg", "Unknown Binance error")
                raise RuntimeError(f"Binance API error ({resp.status}): {error_msg}")
            return result


async def get_pay_transactions(
    start_time: int = None,
    end_time: int = None,
    limit: int = 50,
) -> list[dict]:
    """
    Get recent Binance Pay transactions history.

    Returns list of transactions with:
        - orderId: Binance order ID
        - transactionId: transaction ID
        - amount: transfer amount
        - currency: USDT, etc.
        - createTime: timestamp
        - note: the note/remark attached (where user puts Order ID)
        - buyerName: sender name
        - status: SUCCESS, PENDING, etc.
    """
    params = {
        "type": 1,  # 1 = received (incoming payments)
        "limit": limit,
    }
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    result = await _get("/sapi/v1/pay/transactions", params)
    return result.get("data", [])


async def verify_payment_by_txid(
    txid: str,
    expected_amount: float = None,
    expected_order_id: str = None,
) -> dict:
    """
    Verify a Binance Pay transaction by its Order ID (txid).

    Looks through recent Pay transactions to find a match.

    Args:
        txid: The Binance Order ID submitted by user
        expected_amount: Expected payment amount (optional)
        expected_order_id: The store's Order ID to match in note field (optional)

    Returns dict with:
        - found: bool
        - paid: bool
        - amount: actual amount received
        - currency: e.g. USDT
        - buyer_name: sender name
        - transaction_time: when payment was made
        - note: the note attached to payment
    """
    # Look back 24 hours
    now = int(time.time() * 1000)
    day_ms = 24 * 60 * 60 * 1000

    try:
        transactions = await get_pay_transactions(
            start_time=now - (7 * day_ms),  # Last 7 days
            end_time=now,
            limit=100,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transactions: {e}")

    for tx in transactions:
        # Match by Binance orderId or transactionId
        if tx.get("orderId") == txid or tx.get("transactionId") == txid:
            status = tx.get("status", "")
            is_success = status in ("SUCCESS", "SETTLED")
            amount = float(tx.get("amount", 0))
            note = tx.get("note", "") or tx.get("memo", "")

            # If we have an expected store Order ID, check if it's in the note
            if expected_order_id and expected_order_id not in note:
                continue  # Note doesn't match, skip

            # If we have expected amount, verify it matches
            if expected_amount:
                # Allow small tolerance (0.01) for fees
                if abs(amount - expected_amount) > 0.02:
                    return {
                        "found": True,
                        "paid": False,
                        "error": f"Amount mismatch. Expected {expected_amount}, got {amount}",
                        "amount": amount,
                        "currency": tx.get("currency", "USDT"),
                        "note": note,
                    }

            return {
                "found": True,
                "paid": is_success,
                "amount": amount,
                "currency": tx.get("currency", "USDT"),
                "buyer_name": tx.get("buyerName", "Unknown"),
                "transaction_time": tx.get("createTime"),
                "note": note,
                "order_id": tx.get("orderId"),
                "transaction_id": tx.get("transactionId"),
                "status": status,
            }

    return {
        "found": False,
        "paid": False,
        "error": "Transaction not found. Make sure you sent the correct Binance Order ID.",
    }


async def verify_payment_by_note(
    order_id: str,
    expected_amount: float = None,
) -> dict:
    """
    Verify payment by searching for the store Order ID in transaction notes.

    This is more flexible - the user doesn't need to send the Binance Order ID,
    the bot can find the payment by looking for the Order ID in the note field.

    Args:
        order_id: The store's Order ID (e.g. AIX-123456-ABC123)
        expected_amount: Expected payment amount

    Returns same format as verify_payment_by_txid.
    """
    now = int(time.time() * 1000)
    day_ms = 24 * 60 * 60 * 1000

    try:
        transactions = await get_pay_transactions(
            start_time=now - (7 * day_ms),
            end_time=now,
            limit=100,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transactions: {e}")

    for tx in transactions:
        note = tx.get("note", "") or tx.get("memo", "")

        # Check if our order ID appears in the note
        if order_id in note:
            status = tx.get("status", "")
            is_success = status in ("SUCCESS", "SETTLED")
            amount = float(tx.get("amount", 0))

            if expected_amount:
                if abs(amount - expected_amount) > 0.02:
                    return {
                        "found": True,
                        "paid": False,
                        "error": f"Amount mismatch. Expected {expected_amount}, got {amount}",
                        "amount": amount,
                        "currency": tx.get("currency", "USDT"),
                        "note": note,
                    }

            return {
                "found": True,
                "paid": is_success,
                "amount": amount,
                "currency": tx.get("currency", "USDT"),
                "buyer_name": tx.get("buyerName", "Unknown"),
                "transaction_time": tx.get("createTime"),
                "note": note,
                "order_id": tx.get("orderId"),
                "transaction_id": tx.get("transactionId"),
                "status": status,
            }

    return {
        "found": False,
        "paid": False,
        "error": f"No payment found with Order ID '{order_id}' in the note. Make sure you included the Order ID in the payment note.",
    }


################################################################################
# CRYPTOMUS_SERVICE
################################################################################

"""
AIX Store Bot - Cryptomus Payment Service
==========================================
Auto-payment via Cryptomus API. Creates payment links, checks status,
and handles webhooks for automatic order fulfillment.

Required env vars:
    CRYPTOMUS_API_KEY
    CRYPTOMUS_MERCHANT_ID
"""
import json
import base64
import hmac
import hashlib
import uuid
import time

import aiohttp

from config import CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID

BASE_URL = "https://api.cryptomus.com/v1"


def _sign(payload_json: str) -> str:
    """
    Cryptomus signature:
    base64( HMAC_SHA512( base64(payload) + API_KEY ) )
    """
    b64_payload = base64.b64encode(payload_json.encode()).decode()
    signature = hmac.new(
        CRYPTOMUS_API_KEY.encode(),
        (b64_payload + CRYPTOMUS_API_KEY).encode(),
        hashlib.sha512,
    ).digest()
    return base64.b64encode(signature).decode()


async def _request(method: str, endpoint: str, payload: dict = None) -> dict:
    """Send a signed request to Cryptomus API."""
    url = f"{BASE_URL}{endpoint}"
    payload = payload or {}
    payload_json = json.dumps(payload)

    headers = {
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": _sign(payload_json),
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method, url, headers=headers, data=payload_json
        ) as resp:
            result = await resp.json()
            if not result.get("state"):
                error_msg = result.get("message", "Unknown Cryptomus error")
                raise RuntimeError(f"Cryptomus API error: {error_msg}")
            return result.get("result", {})


async def create_payment(
    amount: float,
    currency: str = "USDT",
    order_id: str = None,
    description: str = "AIX Store Purchase",
    user_id: int = None,
) -> dict:
    """
    Create a Cryptomus payment invoice.

    Returns dict with:
        - url: Payment link to send user
        - uuid: Payment UUID for checking status
        - order_id: Your order ID
    """
    order_id = order_id or f"aix_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    payload = {
        "amount": str(amount),
        "currency": currency,
        "order_id": order_id,
        "network": "TRC20",  # Fast & cheap USDT
        "url_return": f"https://t.me/Shop_chatgptplus_bot",
        "url_callback": f"https://your-railway-url.up.railway.app/webhook/cryptomus",
        "is_payment_multiple": False,
        "lifetime": 3600,  # 1 hour expiry
        "additional_data": description,
    }

    result = await _request("POST", "/payment", payload)
    return {
        "url": result.get("url"),
        "uuid": result.get("uuid"),
        "order_id": order_id,
        "address": result.get("address"),
        "status": result.get("payment_status", "check"),
    }


async def get_payment_status(payment_uuid: str = None, order_id: str = None) -> dict:
    """
    Check payment status by uuid or order_id.

    Returns dict with:
        - status: payment_status (check, wrong_amount, confirm, paid, etc.)
        - is_final: True if payment is complete
        - amount: actual amount paid
        - payer_amount: amount paid by user
    """
    payload = {}
    if payment_uuid:
        payload["uuid"] = payment_uuid
    elif order_id:
        payload["order_id"] = order_id
    else:
        raise ValueError("Need payment_uuid or order_id")

    result = await _request("POST", "/payment/info", payload)
    status = result.get("payment_status", "unknown")

    # Final states: paid, paid_over, wrong_amount (if acceptable)
    is_final = status in ("paid", "paid_over")

    return {
        "status": status,
        "is_final": is_final,
        "amount": result.get("amount"),
        "payer_amount": result.get("payer_amount"),
        "uuid": result.get("uuid"),
        "order_id": result.get("order_id"),
        "currency": result.get("currency"),
        "network": result.get("network"),
    }


def verify_webhook(payload: dict, received_sign: str) -> bool:
    """
    Verify webhook signature from Cryptomus.
    Returns True if the webhook is authentic.
    """
    if not CRYPTOMUS_API_KEY:
        return False

    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    expected_sign = _sign(payload_json)
    return hmac.compare_digest(expected_sign, received_sign)


# ═══════════════════════════════════════════════════════════
# Shortcuts
# ═══════════════════════════════════════════════════════════


async def create_product_payment(
    product_key: str,
    qty: int,
    user_id: int,
) -> dict:
    """
    Create a payment for a product purchase.
    Returns payment info including the payment URL.
    """
    from config import PRODUCTS

    product = PRODUCTS[product_key]
    total = float(product["usd"]) * qty
    desc = f"{product['title']} x{qty}"

    return await create_payment(
        amount=total,
        currency="USDT",
        description=desc,
        user_id=user_id,
    )


########################################


################################################################################
# WEBHOOK
################################################################################

"""
AIX Store Bot - Webhook Handler
===============================
Handles Cryptomus payment webhooks for automatic order fulfillment.
Also provides HTTP endpoints for Railway health checks.
"""
import json
import logging

from aiohttp import web

from services.cryptomus import verify_webhook, get_payment_status
from database import (
    get_payment_by_order,
    update_payment_status,
    reserve_stock,
    create_order,
)
from config import PRODUCTS, CHANNEL_USERNAME
from utils import ce
from loader import bot

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


# ═══════════════════════════════════════════════════════════
# Health Check (Railway requires this)
# ═══════════════════════════════════════════════════════════


@routes.get("/")
async def health_check(request):
    """Health check endpoint for Railway."""
    return web.json_response({"status": "ok", "bot": "AIX Store"})


@routes.get("/health")
async def health(request):
    """Health check."""
    return web.json_response({"status": "alive"})


# ═══════════════════════════════════════════════════════════
# Cryptomus Webhook
# ═══════════════════════════════════════════════════════════


@routes.post("/webhook/cryptomus")
async def cryptomus_webhook(request):
    """
    Handle Cryptomus payment webhook.

    Cryptomus sends a POST request when payment status changes.
    We verify the signature, check the status, and auto-deliver if paid.
    """
    try:
        body = await request.json()
    except Exception:
        logger.warning("Cryptomus webhook: invalid JSON body")
        return web.json_response({"error": "invalid json"}, status=400)

    # Verify webhook signature
    received_sign = request.headers.get("Sign", "")
    if not verify_webhook(body, received_sign):
        logger.warning("Cryptomus webhook: invalid signature")
        return web.json_response({"error": "invalid signature"}, status=403)

    order_id = body.get("order_id", "")
    status = body.get("status", "")
    uuid = body.get("uuid", "")

    logger.info(f"Cryptomus webhook: order_id={order_id}, status={status}")

    if not order_id:
        return web.json_response({"error": "missing order_id"}, status=400)

    # Get local payment record
    payment_record = await get_payment_by_order(order_id)
    if not payment_record:
        logger.warning(f"Cryptomus webhook: unknown order_id {order_id}")
        return web.json_response({"status": "unknown order"})

    # Update status
    await update_payment_status(order_id, status)

    # If already delivered, ignore
    if payment_record["status"] == "delivered":
        return web.json_response({"status": "already delivered"})

    # Check if payment is final (paid or paid_over)
    if status in ("paid", "paid_over"):
        product_key = payment_record["product_key"]
        qty = payment_record["quantity"]
        user_id = payment_record["telegram_id"]
        product = PRODUCTS.get(product_key)

        if not product:
            logger.error(f"Unknown product_key: {product_key}")
            return web.json_response({"status": "unknown product"})

        # Reserve stock
        items = await reserve_stock(product["stock_name"], qty)
        if items is None:
            logger.error(f"Out of stock for order {order_id}")
            # Notify user
            try:
                await bot.send_message(
                    user_id,
                    f"{ce('error')} <b>Payment received but out of stock!</b>\n"
                    f"Order ID: <code>{order_id}</code>\n\n"
                    f"Admins have been notified. Please contact support.",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            # Notify admins
            await _notify_admins_out_of_stock(user_id, product, qty, order_id)
            return web.json_response({"status": "out of stock"})

        # Mark as delivered
        await update_payment_status(order_id, "delivered")

        # Create order record
        await create_order(
            user_id,
            "cryptomus",
            float(payment_record["amount"]),
            payment_record["currency"],
            product_key,
            qty,
            f"cryptomus_{uuid}",
            "approved",
        )

        # Send codes to user
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        delivery_text = (
            f"{ce('success')} <b>Payment Confirmed & Auto-Delivered!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('vip')} <b>{product['title']}</b>\n"
            f"{ce('quantity')} Quantity: <b>{qty}</b>\n"
            f"{ce('checkout')} Order ID: <code>{order_id}</code>\n\n"
            f"🔑 <b>Your Codes:</b>\n{codes_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
        )
        try:
            await bot.send_message(user_id, delivery_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to send delivery to {user_id}: {e}")

        # Notify admins
        await _notify_admins_auto_delivery(user_id, product, qty, order_id, items)

        # Post to channel
        if CHANNEL_USERNAME != "@YourChannelUsername":
            group_msg = (
                f"{ce('buy_cart')} <b>New Auto-Purchase!</b>\n\n"
                f"{ce('diamond_arrow')} <b>Product:</b> {product['title']}\n"
                f"{ce('sparkles_pay')} <b>QTY:</b> {qty}\n"
                f"{ce('checkout')} <b>Order:</b> <code>{order_id[:20]}...</code>\n\n"
                f"<i>Paid via Cryptomus Auto-Pay</i> {ce('secure_shield')}"
            )
            try:
                await bot.send_message(
                    chat_id=CHANNEL_USERNAME,
                    text=group_msg,
                    parse_mode="HTML",
                )
            except Exception:
                pass

        logger.info(f"Auto-delivered order {order_id} to user {user_id}")
        return web.json_response({"status": "delivered"})

    return web.json_response({"status": f"received: {status}"})


# ═══════════════════════════════════════════════════════════
# Notification Helpers
# ═══════════════════════════════════════════════════════════


async def _notify_admins_auto_delivery(user_id, product, qty, order_id, items):
    """Notify admins about auto-delivery."""
    from config import ADMIN_IDS

    codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
    admin_msg = (
        f"✅ <b>Auto-Delivery Completed!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n\n"
        f"🔑 <b>Codes Delivered:</b>\n{codes_str}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass


async def _notify_admins_out_of_stock(user_id, product, qty, order_id):
    """Notify admins when payment received but out of stock."""
    from config import ADMIN_IDS

    admin_msg = (
        f"🚨 <b>PAID BUT OUT OF STOCK!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n\n"
        f"<b>Add stock ASAP!</b>"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# App Factory
# ═══════════════════════════════════════════════════════════


def create_web_app():
    """Create aiohttp app for webhook server."""
    app = web.Application()
    app.add_routes(routes)
    return app


################################################################################
# ADMIN_HANDLERS
################################################################################

"""
AIX Store Bot - Admin Handlers
==============================
All admin-only handlers: ban, unban, addstock, pull, addbalance, send, broadcast.
"""
import asyncio
import time

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from config import ADMIN_IDS, CHANNEL_USERNAME, PRODUCTS, BOT_USERNAME
from database import (
    set_ban_status,
    add_balance,
    add_stock_items,
    pull_stock_items,
    get_available_stock,
    get_all_users,
    create_order,
)
from utils import ce, format_amount

router = Router()

# Admin state: admin_id -> target_user_id
admin_reply_waiting: dict[int, int] = {}


# ═══════════════════════════════════════════════════════════
# Admin Notification Helpers
# ═══════════════════════════════════════════════════════════


async def notify_admins_wallet_purchase(user, product, qty, total_price, items):
    """Notify all admins about a successful wallet purchase."""
    codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
    admin_msg = (
        f"🛒 <b>Successful purchase from Wallet!</b>\n"
        f"User: @{user.username or 'N/A'}\n"
        f"ID: <code>{user.id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n"
        f"Deducted Amount: {total_price} USDT\n\n"
        f"<b>🔑 Codes pulled from stock:</b>\n{codes_str}"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Send Code to Customer",
                    callback_data=f"sendprod_{user.id}",
                )
            ]
        ]
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass


async def notify_admins_manual_payment(method, user, product, qty, total_price):
    """Notify admins about a manual payment request."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Message / Send Code",
                    callback_data=f"sendprod_{user.id}",
                )
            ]
        ]
    )
    admin_msg = (
        f"🟡 <b>Manual {method} Payment Request!</b>\n"
        f"User: @{user.username or 'N/A'}\n"
        f"ID: <code>{user.id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n"
        f"Required Amount: {total_price} USDT\n\n"
        f"<i>(After verifying the transfer, use the command <code>/pull {qty}</code> to pull codes and send them to the customer)</i>"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass


async def notify_admins_auto_delivery(user_id, product, qty, order_id, items):
    """Notify admins about an auto-delivery (Binance Pay Auto)."""
    codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
    admin_msg = (
        f"✅ <b>Auto-Delivery Completed!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n\n"
        f"🔑 <b>Codes Delivered:</b>\n{codes_str}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass


async def notify_admins_out_of_stock(user_id, product, qty, order_id):
    """Notify admins when Binance payment received but out of stock."""
    admin_msg = (
        f"🚨 <b>PAID BUT OUT OF STOCK!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Order ID: <code>{order_id}</code>\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Product: {product['title']}\n"
        f"Quantity: {qty}\n\n"
        f"<b>Add stock ASAP!</b>"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass


async def notify_admins_deposit_request(method, user, amount, currency):
    """Notify admins about a deposit request."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Message Customer",
                    callback_data=f"sendprod_{user.id}",
                )
            ]
        ]
    )
    admin_msg = (
        f"🟡 <b>Manual Top-up Request ({method})!</b>\n"
        f"User: @{user.username or 'N/A'}\n"
        f"ID: <code>{user.id}</code>\n"
        f"Requested Amount: {amount} {currency}\n\n"
        f"<i>(Customer will send the screenshot, you can use the <code>/addbalance</code> command directly)</i>"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# Admin Command Handlers
# ═══════════════════════════════════════════════════════════


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    """Ban a user. Usage: /ban user_id"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            f"{ce('error')} <b>Correct usage:</b>\n<code>/ban user_id</code>",
            parse_mode="HTML",
        )
        return
    try:
        target_id = int(parts[1])
        await set_ban_status(target_id, True)
        await message.answer(
            f"{ce('success')} <b>Successfully banned user (ID: {target_id})!</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    """Unban a user. Usage: /unban user_id"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            f"{ce('error')} <b>Correct usage:</b>\n<code>/unban user_id</code>",
            parse_mode="HTML",
        )
        return
    try:
        target_id = int(parts[1])
        await set_ban_status(target_id, False)
        await message.answer(
            f"{ce('success')} <b>Successfully unbanned user (ID: {target_id})!</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")


@router.message(Command("addbalance"))
async def cmd_addbalance(message: Message):
    """Add/deduct balance. Usage: /addbalance user_id amount"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            f"{ce('error')} <b>Usage:</b>\n"
            f"Adding: <code>/addbalance user_id 10</code>\n"
            f"Deducting: <code>/addbalance user_id -10</code>",
            parse_mode="HTML",
        )
        return
    try:
        target_id = int(parts[1])
        amount = float(parts[2])
        await add_balance(target_id, amount)

        if amount >= 0:
            await message.answer(
                f"{ce('success')} <b>Successfully added ${amount} to user (ID: {target_id})!</b>",
                parse_mode="HTML",
            )
            user_msg = (
                f"{ce('wallet')} <b>Balance Added!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>{amount} USDT</b> has been added to your wallet by the admin.\n"
                f"You can now browse products and purchase easily."
            )
        else:
            abs_amount = abs(amount)
            await message.answer(
                f"{ce('success')} <b>Successfully deducted ${abs_amount} from user (ID: {target_id})!</b>",
                parse_mode="HTML",
            )
            user_msg = (
                f"{ce('wallet')} <b>Balance Deducted!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>{abs_amount} USDT</b> has been deducted from your wallet by the admin."
            )

        try:
            await bot.send_message(target_id, user_msg, parse_mode="HTML")
        except Exception:
            pass
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")


@router.message(Command("send"))
async def cmd_send(message: Message):
    """Send message to user. Usage: /send user_id message"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.html_text.split(" ", 2)
    if len(parts) < 3:
        await message.answer(
            f"{ce('error')} <b>Error! Correct usage:</b>\n"
            f"<code>/send user_id your_message_here</code>",
            parse_mode="HTML",
        )
        return
    try:
        target_id = int(parts[1])
        text_to_send = parts[2]
        user_msg = (
            f"{ce('support_msg')} <b>Message from Admin:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n{text_to_send}"
        )
        await bot.send_message(target_id, user_msg, parse_mode="HTML")
        await message.answer(
            f"{ce('success')} <b>Message sent to the customer successfully!</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error sending message:</b>\n{e}", parse_mode="HTML")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """Broadcast message to all users. Usage: /broadcast message"""
    if message.from_user.id not in ADMIN_IDS:
        return
    text_to_send = message.html_text.replace("/broadcast", "", 1).strip()
    if not text_to_send:
        await message.answer(
            f"{ce('error')} <b>Error! Please write the message after the command.</b>",
            parse_mode="HTML",
        )
        return

    loading_msg = await message.answer(
        f"{ce('loading')} <b>Sending broadcast to all users...</b>", parse_mode="HTML"
    )
    sent_count = 0
    users = await get_all_users()
    for u in users:
        try:
            await bot.send_message(u["telegram_id"], text_to_send, parse_mode="HTML")
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await loading_msg.edit_text(
        f"{ce('success')} <b>Broadcast sent successfully to {sent_count} users!</b>",
        parse_mode="HTML",
    )


@router.message(Command("pull"))
async def cmd_pull(message: Message):
    """Pull stock items for manual delivery. Usage: /pull qty"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(
            f"{ce('error')} <b>Correct usage:</b>\n<code>/pull 10</code> (to pull 10 codes)",
            parse_mode="HTML",
        )
        return

    qty = int(parts[1])
    if qty < 1:
        return

    product_name = PRODUCTS["cdk_chatgpt"]["stock_name"]
    items = await pull_stock_items(product_name, qty)

    if items is None:
        await message.answer(
            f"{ce('error')} <b>Insufficient stock!</b>",
            parse_mode="HTML",
        )
        return

    codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
    await message.answer(
        f"{ce('success')} <b>Successfully pulled {qty} codes and deducted them from stock!</b>\n\n"
        f"{codes_str}\n\n"
        f"<i>You can now copy and send them to the customer.</i>",
        parse_mode="HTML",
    )


@router.message(Command("addstock"))
async def cmd_addstock(message: Message):
    """Add stock items. Usage: /addstock product_name (newline) code1 (newline) code2..."""
    if message.from_user.id not in ADMIN_IDS:
        return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2:
        await message.answer(
            f"{ce('error')} <b>Error! Use this format (in a single message):</b>\n\n"
            f"<code>/addstock CDK</code>\n<code>Code_1</code>",
            parse_mode="HTML",
        )
        return

    product_name = PRODUCTS["cdk_chatgpt"]["stock_name"]
    items = lines[1:]

    added_count = await add_stock_items(product_name, items)
    total = await get_available_stock(product_name)
    product_info = PRODUCTS["cdk_chatgpt"]

    # 1. Notify all users about new stock
    broadcast_text = (
        f"{ce('announcement')} <b>Stock Alert!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 New keys have been added for: <b>{product_info['title']}</b>\n\n"
        f"{ce('quantity')} Available Stock: <b>{total}</b>\n"
        f"⚡ Hurry up and grab yours now before it runs out!"
    )
    buy_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Buy Now",
                    callback_data="buy_cdk_chatgpt",
                )
            ]
        ]
    )

    users = await get_all_users()
    sent_count = 0
    for u in users:
        try:
            await bot.send_message(
                u["telegram_id"], broadcast_text, parse_mode="HTML", reply_markup=buy_kb
            )
            sent_count += 1
        except Exception:
            pass

    # 2. Post to channel
    if CHANNEL_USERNAME != "@YourChannelUsername":
        group_text = (
            f"{ce('announcement')} <b>STOCK ALERT!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 New keys have been added for: <b>{product_info['title']}</b>\n\n"
            f"{ce('quantity')} Available Stock: <b>{total}</b>\n"
            f"⚡ Hurry up and grab yours now before it runs out!\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=group_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🛒 Buy Now",
                                url=f"https://t.me/{BOT_USERNAME}?start=shop",
                            )
                        ]
                    ]
                ),
            )
        except Exception as e:
            await message.answer(
                f"{ce('error')} <b>Failed to post to channel:</b> {e}",
                parse_mode="HTML",
            )

    await message.answer(
        f"{ce('success')} <b>Successfully added {added_count} codes!</b>\n"
        f"Total stock: {total}\n"
        f"Notification sent to {sent_count} users and the channel.",
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════
# Admin Send Code to Customer
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data.startswith("sendprod_"))
async def cb_sendprod(call: CallbackQuery):
    """Initiate send code to customer flow."""
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("Unauthorized!", show_alert=True)

    target_user = int(call.data.split("_")[1])
    admin_reply_waiting[call.from_user.id] = target_user

    await call.message.reply(
        f"{ce('pencil')} <b>Alright, please send the code or message now to be forwarded to the customer "
        f"(ID: <code>{target_user}</code>):</b>\n"
        f"<i>(You can send text, photo, or file)\nTo cancel, send: ❌ Cancel</i>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(F.photo | F.document)
async def handle_admin_media(message: Message):
    """Handle admin sending media (photo/document) to customer."""
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_reply_waiting:
        return

    target_id = admin_reply_waiting.pop(user_id)
    try:
        original_caption = message.html_text or ""
        new_caption = (
            f"🎁 <b>Your order is ready!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{original_caption}\n\n"
            f"{ce('heart')} <b>Thank you for trusting our store!</b>"
        )
        await message.copy_to(target_id, caption=new_caption, parse_mode="HTML")
        await message.answer(
            f"{ce('success')} <b>File/Photo sent to the customer (ID: {target_id}) successfully! ✅</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(
            f"{ce('error')} <b>Error occurred during sending! Maybe the user blocked the bot.</b>\n"
            f"Error: {e}",
            parse_mode="HTML",
        )


@router.message(F.text)
async def handle_admin_text(message: Message):
    """Handle admin sending text message to customer."""
    user_id = message.from_user.id
    text = message.text.strip()

    # Handle cancel
    if text in ["❌ Cancel", "Cancel"]:
        if user_id in admin_reply_waiting:
            admin_reply_waiting.pop(user_id)
            from keyboards import main_reply_keyboard
            from utils import safe_answer_photo
            from handlers.user import home_text, home_keyboard

            await message.answer(
                f"{ce('error')} <b>Cancelled.</b>",
                reply_markup=main_reply_keyboard(),
                parse_mode="HTML",
            )
            await safe_answer_photo(
                message,
                home_text(message.from_user.first_name or "Admin"),
                reply_markup=home_keyboard(),
            )
        return

    if user_id not in ADMIN_IDS or user_id not in admin_reply_waiting:
        return

    target_id = admin_reply_waiting.pop(user_id)
    try:
        user_msg = (
            f"🎁 <b>Your order is ready!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{message.html_text}\n\n"
            f"{ce('heart')} <b>Thank you for trusting our store!</b>"
        )
        await bot.send_message(target_id, user_msg, parse_mode="HTML")
        await message.answer(
            f"{ce('success')} <b>Code sent to the customer successfully! ✅</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(
            f"{ce('error')} <b>Error occurred during sending! Maybe the user blocked the bot.</b>\n"
            f"Error: {e}",
            parse_mode="HTML",
        )


################################################################################
# USER_HANDLERS
################################################################################

"""
AIX Store Bot - User Handlers
=============================
All user-facing handlers: start, shop, products, deposit, wallet, support, referral.
"""
import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, URLInputFile

from loader import bot
from config import BOT_NAME, SUPPORT, CHANNEL_USERNAME, PRODUCTS, CDK_IMAGE_FILE, BINANCE_ID
from database import (
    get_user_stats,
    get_stock_count,
    get_total_sold,
    create_order,
    get_balance,
    deduct_balance,
    reserve_stock,
    process_referral_reward,
    get_payment_by_order,
    get_binance_order_by_txid,
    create_binance_order_record,
    update_binance_order_txid,
    mark_binance_order_delivered,
    update_payment_status,
)
from keyboards import (
    home_keyboard,
    main_reply_keyboard,
    back_home_keyboard,
    product_buttons,
    product_details_buttons,
    checkout_payment_buttons,
    deposit_currency_buttons,
    deposit_payment_buttons,
    wallet_keyboard,
    quantity_keyboard,
    cancel_keyboard,
)
from utils import (
    ce,
    esc,
    format_amount,
    safe_answer,
    safe_edit_or_answer,
    safe_answer_photo,
    strip_custom_emoji,
)

router = Router()

# ═══════════════════════════════════════════════════════════
# State Management (In-Memory)
# ═══════════════════════════════════════════════════════════
deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}


# ═══════════════════════════════════════════════════════════
# Text Builders
# ═══════════════════════════════════════════════════════════


def home_text(name: str) -> str:
    return (
        f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"Hey, <b>{esc(name)}</b> {ce('user_link')}\n"
        f"Welcome to your premium AI subscriptions store.\n\n"
        f"{ce('store')} <b>Shop</b> — Browse & buy products\n"
        f"{ce('wallet')} <b>Deposit</b> — Add funds to your wallet\n"
        f"{ce('support')} <b>Support</b> — Get help anytime\n\n"
        f"{ce('check_anim')} Fast activation  "
        f"{ce('check_anim')} Secure payments  "
        f"{ce('check_anim')} Trusted service"
    )


def product_list_text() -> str:
    return (
        f"{ce('store')} <b>Available Products</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('chatgpt')} <b>CDK Activation ChatGPT 2 Year</b>\n"
        f"Price (10+): $4.00 | Single: $5.50\n\n"
        f"{ce('arrow_right')} Choose a product below:"
    )


def get_delivery_text(product: dict, qty: int) -> str:
    return (
        f"{ce('success')} <b>Payment Confirmed Successfully!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('vip')} <b>{product['title']}</b>\n\n"
        f"{ce('quantity')} <b>Quantity:</b> {qty}\n\n"
        f"{ce('announcement')} <b>Delivery Status:</b>\n"
        f"Please wait... The admin has been notified and will send your codes directly here in this chat shortly!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
    )


async def animate_message(message: Message):
    """Show loading animation."""
    text = f"{ce('loading')} <b>Loading...</b>"
    try:
        if getattr(message, "from_user", None) and message.from_user.is_bot:
            if getattr(message, "photo", None):
                msg = await message.answer(text, parse_mode="HTML")
            else:
                msg = await message.edit_text(text, parse_mode="HTML")
        else:
            msg = await message.answer(text, parse_mode="HTML")
    except Exception:
        msg = await message.answer(text, parse_mode="HTML")
    await asyncio.sleep(0.3)
    return msg or message


async def send_home(message: Message):
    """Send home screen with photo and keyboard."""
    await safe_answer_photo(
        message, home_text(message.from_user.first_name or "User"), reply_markup=home_keyboard()
    )
    await message.answer("Main Menu", reply_markup=main_reply_keyboard())


# ═══════════════════════════════════════════════════════════
# Command Handlers
# ═══════════════════════════════════════════════════════════


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    deposit_waiting.pop(message.from_user.id, None)
    buy_waiting.pop(message.from_user.id, None)
    await send_home(message)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Handle /menu command."""
    await cmd_start(message)


# ═══════════════════════════════════════════════════════════
# Navigation Callbacks
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data == "home_main")
async def cb_home_main(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message)
    await safe_edit_or_answer(msg, home_text(call.from_user.first_name or "User"), reply_markup=home_keyboard())


@router.callback_query(F.data == "home_shop")
async def cb_home_shop(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message)
    await handle_shop_action(msg)


@router.callback_query(F.data == "refresh_products")
async def cb_refresh_products(call: CallbackQuery):
    await cb_home_shop(call)


async def handle_shop_action(target_message: Message):
    """Display product listing."""
    count = await get_stock_count("cdk_chatgpt")
    await safe_edit_or_answer(target_message, product_list_text(), reply_markup=product_buttons(count))


@router.callback_query(F.data == "home_deposit")
async def cb_home_deposit(call: CallbackQuery):
    await call.answer()
    text = "💰 <b>Deposit Funds</b>\nSelect currency:"
    await safe_edit_or_answer(call.message, text, reply_markup=deposit_currency_buttons())


@router.callback_query(F.data == "home_support")
async def cb_home_support(call: CallbackQuery):
    await call.answer()
    text = (
        f"{ce('support_msg')} <b>Quick support:</b>\n\n"
        f"{ce('telegram')} <b>Telegram:</b> {ce('arrow_right')} {SUPPORT}"
    )
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())


@router.callback_query(F.data == "home_wallet")
async def cb_home_wallet(call: CallbackQuery):
    await call.answer()
    stats = await get_user_stats(call.from_user.id)
    balance = stats["balance_usdt"] if stats else 0.0
    total_ref = stats["total_ref"] if stats else 0
    earnings = (total_ref // 10) * 0.50

    msg = await animate_message(call.message)
    text = (
        f"{ce('wallet')} <b>AIX USER PROFILE & WALLET</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('user')} Name: <b>{esc(call.from_user.first_name)}</b> {ce('user_link')}\n"
        f"{ce('price')} Wallet Balance: <b>{balance} USDT</b>\n\n"
        f"{ce('users_group')} Total Invited Users: <b>{total_ref} friends</b>\n"
        f"{ce('money_fly')} Referral Earnings: <b>{format_amount(earnings)} USDT</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('checkout')} You can deposit funds or use your referral balance to purchase instantly."
    )
    await safe_edit_or_answer(msg, text, reply_markup=wallet_keyboard())


@router.callback_query(F.data == "home_share")
async def cb_home_share(call: CallbackQuery):
    await call.answer()
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={call.from_user.id}"
    stats = await get_user_stats(call.from_user.id)
    total_ref = stats["total_ref"] if stats else 0
    earnings = (total_ref // 10) * 0.50

    text = (
        f"{ce('share')} <b>Share & Earn Free USDT!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Invite <b>10 friends</b> to use the bot and earn <b>$0.50 USDT</b> instantly inside your wallet!\n\n"
        f"{ce('users_group')} Your Total Invites: <b>{total_ref} users</b>\n"
        f"{ce('money_fly')} Total Earned: <b>{format_amount(earnings)} USDT</b>\n\n"
        f"{ce('link_pin')} <b>Your Exclusive Referral Link:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"<i>Copy the link and share it in groups to start earning!</i>"
    )
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())


# ═══════════════════════════════════════════════════════════
# Product & Purchase Handlers
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data.startswith("product_"))
async def cb_product(call: CallbackQuery):
    """Show product details."""
    await call.answer()
    product_key = call.data.replace("product_", "")

    if product_key not in PRODUCTS:
        await call.answer("Product not found!", show_alert=True)
        return

    count = await get_stock_count("cdk_chatgpt")
    if count <= 0:
        await call.answer("Out of stock! Please check back later.", show_alert=True)
        return

    sold_count = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    product = PRODUCTS[product_key]
    desc = product["desc"].replace("✅", ce("success"))

    caption = (
        f"{ce('chatgpt')} <b>{product['title']}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Price: <b>${float(product['usd']):.2f}</b>\n"
        f"{ce('stock')} Stock: <b>{count} accounts</b>\n"
        f"{ce('sold')} Sold: <b>{sold_count} accounts</b>\n\n"
        f"<b>Description:</b>\n<blockquote>{desc}</blockquote>"
    )

    try:
        await call.message.delete()
    except Exception:
        pass

    try:
        await call.message.answer_photo(
            URLInputFile(CDK_IMAGE_FILE),
            caption=caption,
            reply_markup=product_details_buttons(product_key),
            parse_mode="HTML",
        )
    except Exception:
        await call.message.answer(caption, reply_markup=product_details_buttons(product_key), parse_mode="HTML")


@router.callback_query(F.data.startswith("back_to_prod_"))
async def cb_back_to_product(call: CallbackQuery):
    """Navigate back to product from checkout."""
    await call.answer()
    product_key = call.data.replace("back_to_prod_", "")

    if product_key not in PRODUCTS:
        await cb_home_shop(call)
        return

    count = await get_stock_count("cdk_chatgpt")
    sold_count = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    product = PRODUCTS[product_key]
    desc = product["desc"].replace("✅", ce("success"))

    caption = (
        f"{ce('chatgpt')} <b>{product['title']}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Price: <b>${float(product['usd']):.2f}</b>\n"
        f"{ce('stock')} Stock: <b>{count} accounts</b>\n"
        f"{ce('sold')} Sold: <b>{sold_count} accounts</b>\n\n"
        f"<b>Description:</b>\n<blockquote>{desc}</blockquote>"
    )
    await safe_edit_or_answer(call.message, caption, reply_markup=product_details_buttons(product_key))


@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(call: CallbackQuery):
    """Initiate purchase flow - ask for quantity."""
    await call.answer()
    product_key = call.data.replace("buy_", "")
    buy_waiting[call.from_user.id] = product_key

    is_single = product_key == "cdk_chatgpt_single"
    if is_single:
        text = f"{ce('pencil')} Enter quantity to buy:"
    else:
        text = f"{ce('pencil')} Enter quantity to buy (Minimum 10):"

    await call.message.answer(text, reply_markup=quantity_keyboard(is_single), parse_mode="HTML")


async def receive_quantity(message: Message):
    """Process quantity input from user."""
    user_id = message.from_user.id
    product_key = buy_waiting.get(user_id)
    if not product_key:
        return

    is_single = product_key == "cdk_chatgpt_single"
    min_qty = PRODUCTS[product_key]["min_qty"]

    try:
        qty = int(message.text.strip())
        if qty < min_qty:
            error_text = (
                f"{ce('error')} <b>Order Cannot Be Processed!</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<blockquote>{ce('announcement')} <b>The minimum order quantity is {min_qty}.</b>\n"
                f"Please enter {min_qty} or more to continue.</blockquote>"
            )
            await message.answer(error_text, parse_mode="HTML")
            return
    except ValueError:
        await message.answer(f"{ce('error')} <b>Enter a valid number!</b>", parse_mode="HTML")
        return

    buy_waiting.pop(user_id, None)
    await proceed_to_checkout(message, product_key, qty)


async def proceed_to_checkout(message: Message, product_key: str, qty: int):
    """Show checkout screen with payment options."""
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = (
        f"{ce('checkout')} <b>Checkout</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{ce('quantity')} Quantity: <b>{qty}</b>\n"
        f"{ce('price')} Total Price: <b>${total_price:.2f}</b>\n\n"
        f"Choose payment method:"
    )
    await message.answer(text, reply_markup=checkout_payment_buttons(product_key, qty), parse_mode="HTML")


# ═══════════════════════════════════════════════════════════
# Payment Handlers
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data.startswith("pay_wallet_"))
async def cb_pay_wallet(call: CallbackQuery):
    """Process wallet payment."""
    await call.answer()
    parts = call.data.replace("pay_wallet_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id

    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty

    # Check balance
    balance = await get_balance(user_id)
    if balance < total_price:
        await call.message.answer(
            f"{ce('error')} <b>Not enough balance!</b> You have {balance} USDT. Please top up.",
            parse_mode="HTML",
        )
        return

    # Reserve stock
    items = await reserve_stock(product["stock_name"], qty)
    if items is None:
        await call.message.answer(
            f"{ce('error')} <b>Out of stock!</b> Not enough items available.",
            parse_mode="HTML",
        )
        return

    # Deduct balance and create order
    await deduct_balance(user_id, total_price)
    await create_order(
        user_id, "wallet", total_price, "USDT", product_key, qty,
        f"wallet_{int(__import__('time').time())}", "approved",
    )

    # Send delivery message to user
    await call.message.answer(get_delivery_text(product, qty), parse_mode="HTML")

    # Notify admins
    from .admin import notify_admins_wallet_purchase
    await notify_admins_wallet_purchase(call.from_user, product, qty, total_price, items)

    # Notify group
    if CHANNEL_USERNAME != "@YourChannelUsername":
        group_msg = (
            f"{ce('buy_cart')} <b>New Purchase!</b>\n\n"
            f"{ce('diamond_arrow')} <b>Product:</b> {product['title']}\n"
            f"{ce('sparkles_pay')} <b>QTY:</b> {qty}\n\n"
            f"<i>Thank you for choosing us</i> {ce('secure_shield')}"
        )
        try:
            await bot.send_message(chat_id=CHANNEL_USERNAME, text=group_msg, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data.startswith("pay_cryptomus_"))
async def cb_pay_cryptomus(call: CallbackQuery):
    """Create Cryptomus auto-payment invoice."""
    await call.answer()
    parts = call.data.replace("pay_cryptomus_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id

    from services.cryptomus import create_product_payment, get_payment_status
    from database import create_payment_record

    # Create Cryptomus payment
    try:
        payment = await create_product_payment(product_key, qty, user_id)
    except Exception as e:
        await call.message.answer(
            f"{ce('error')} <b>Payment Error:</b> Could not create payment link.\n"
            f"<code>{str(e)}</code>\n\n"
            f"Please try again or contact support.",
            parse_mode="HTML",
        )
        return

    # Save payment record
    await create_payment_record(
        user_id=user_id,
        order_id=payment["order_id"],
        cryptomus_uuid=payment["uuid"],
        product_key=product_key,
        qty=qty,
        amount=float(PRODUCTS[product_key]["usd"]) * qty,
    )

    total_price = float(PRODUCTS[product_key]["usd"]) * qty

    text = (
        f"{ce('binance')} <b>Binance Pay (Auto)</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Amount to pay: <b>{total_price:.2f} USDT</b>\n\n"
        f"{ce('loading')} Click the button below to pay automatically:\n\n"
        f"⚠️ <b>Your Order ID:</b> <code>{payment['order_id']}</code>\n"
        f"<i>Save this ID to check your payment status.</i>\n\n"
        f"⏳ <b>Payment expires in 1 hour.</b>\n"
        f"✅ Once confirmed, codes are delivered automatically!"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pay Now (Cryptomus)", url=payment["url"])],
            [
                InlineKeyboardButton(
                    text="🔄 Check Status",
                    callback_data=f"check_cryptomus_{payment['order_id']}",
                )
            ],
            [InlineKeyboardButton(text="◀️ Back", callback_data=f"back_to_prod_{product_key}")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)


@router.callback_query(F.data.startswith("check_cryptomus_"))
async def cb_check_cryptomus(call: CallbackQuery):
    """Check Cryptomus payment status manually."""
    await call.answer()
    order_id = call.data.replace("check_cryptomus_", "")

    from services.cryptomus import get_payment_status
    from database import get_payment_by_order, update_payment_status, reserve_stock, deduct_balance

    # Get local payment record
    payment_record = await get_payment_by_order(order_id)
    if not payment_record:
        await call.message.answer(
            f"{ce('error')} Order not found. Please contact support.",
            parse_mode="HTML",
        )
        return

    # Check status from Cryptomus
    try:
        status_info = await get_payment_status(order_id=order_id)
    except Exception as e:
        await call.message.answer(
            f"{ce('error')} Could not check payment: <code>{str(e)}</code>",
            parse_mode="HTML",
        )
        return

    status = status_info["status"]
    is_final = status_info["is_final"]

    # Update status in DB
    await update_payment_status(order_id, status)

    if is_final:
        # Payment confirmed → auto-deliver
        product_key = payment_record["product_key"]
        qty = payment_record["quantity"]
        user_id = payment_record["telegram_id"]
        product = PRODUCTS[product_key]

        # Reserve stock
        items = await reserve_stock(product["stock_name"], qty)
        if items is None:
            await call.message.answer(
                f"{ce('error')} Payment received but out of stock! Admins have been notified.",
                parse_mode="HTML",
            )
            from .admin import notify_admins_out_of_stock
            await notify_admins_out_of_stock(user_id, product, qty, order_id)
            return

        # Mark as delivered
        await update_payment_status(order_id, "delivered")

        # Send delivery to user
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        delivery_text = (
            f"{ce('success')} <b>Payment Confirmed & Auto-Delivered!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('vip')} <b>{product['title']}</b>\n"
            f"{ce('quantity')} Quantity: <b>{qty}</b>\n"
            f"{ce('checkout')} Order ID: <code>{order_id}</code>\n\n"
            f"🔑 <b>Your Codes:</b>\n{codes_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
        )
        await call.message.answer(delivery_text, parse_mode="HTML")

        # Notify admins
        from .admin import notify_admins_auto_delivery
        await notify_admins_auto_delivery(user_id, product, qty, order_id, items)
    else:
        status_emoji = "⏳" if status in ("check", "wrong_amount") else "🔄"
        await call.message.answer(
            f"{status_emoji} <b>Payment Status:</b> <code>{status}</code>\n\n"
            f"Your payment is being processed.\n"
            f"Order ID: <code>{order_id}</code>\n\n"
            f"Click 'Check Status' again in a few minutes.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔄 Check Again",
                            callback_data=f"check_cryptomus_{order_id}",
                        )
                    ],
                ]
            ),
        )


@router.callback_query(F.data.startswith("pay_binance_"))
async def cb_pay_binance(call: CallbackQuery):
    """Show Binance Pay MANUAL payment instructions (fallback)."""
    await call.answer()
    parts = call.data.replace("pay_binance_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id

    from config import BINANCE_ID

    total_price = float(PRODUCTS[product_key]["usd"]) * qty

    text = (
        f"{ce('binance')} <b>Manual Binance Payment</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Amount to pay: <b>{total_price:.2f} USDT</b>\n\n"
        f"{ce('loading')} Please transfer the exact amount to the following Binance ID:\n\n"
        f"{ce('arrow_right')} <code>{BINANCE_ID}</code>\n\n"
        f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team:\n"
        f"{ce('support')} {SUPPORT}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
            [InlineKeyboardButton(text="◀️ Back", callback_data=f"back_to_prod_{product_key}")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

    # Notify admins
    from .admin import notify_admins_manual_payment
    await notify_admins_manual_payment("Binance", call.from_user, PRODUCTS[product_key], qty, total_price)


@router.callback_query(F.data.startswith("pay_bep20_"))
async def cb_pay_bep20(call: CallbackQuery):
    """Show USDT BEP20 payment instructions."""
    await call.answer()
    parts = call.data.replace("pay_bep20_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id

    from config import BEP20_ADDRESS

    total_price = float(PRODUCTS[product_key]["usd"]) * qty

    text = (
        f"{ce('usdt')} <b>USDT (BEP20) Payment</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Amount to pay: <b>{total_price:.2f} USDT</b>\n\n"
        f"{ce('loading')} Please transfer the amount to the following Address (BEP20):\n\n"
        f"<code>{BEP20_ADDRESS}</code>\n\n"
        f"⚠️ <b>IMPORTANT:</b> Please transfer the EXACT amount ({total_price:.2f} USDT) "
        f"<i>net</i> after network fees. We are not responsible for any deductions caused by network fees.\n\n"
        f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team:\n"
        f"{ce('support')} {SUPPORT}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
            [InlineKeyboardButton(text="◀️ Back", callback_data=f"back_to_prod_{product_key}")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

    # Notify admins
    from .admin import notify_admins_manual_payment
    await notify_admins_manual_payment("USDT BEP20", call.from_user, PRODUCTS[product_key], qty, total_price)


# ═══════════════════════════════════════════════════════════
# Binance Pay Auto (TXID Verification)
# ═══════════════════════════════════════════════════════════

binance_txid_waiting: dict[int, str] = {}  # user_id -> order_id


@router.callback_query(F.data.startswith("pay_binance_auto_"))
async def cb_pay_binance_auto(call: CallbackQuery):
    """
    Generate order ID for Binance Pay Auto.
    User pays via Binance Pay ID, then sends TXID for auto verification.
    """
    await call.answer()
    parts = call.data.replace("pay_binance_auto_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id

    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty

    # Generate unique order ID
    import time, uuid
    order_id = f"AIX-{user_id}-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"

    # Save order in DB
    await create_binance_order_record(
        user_id=user_id,
        order_id=order_id,
        product_key=product_key,
        qty=qty,
        amount=total_price,
    )

    # Store in memory that user needs to send TXID
    binance_txid_waiting[user_id] = order_id

    text = (
        f"⚡ <b>Binance Pay (Auto Verification)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('price')} <b>Amount:</b> <code>{total_price:.2f} USDT</code>\n"
        f"{ce('quantity')} <b>Quantity:</b> {qty}x {product['title']}\n\n"
        f"📋 <b>Your Order ID:</b>\n"
        f"<code>{order_id}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Follow these steps:</b>\n\n"
        f"1️⃣ Open <b>Binance App</b> → Pay → Send\n"
        f"2️⃣ Enter this <b>Binance ID</b>:\n"
        f"<code>{BINANCE_ID}</code>\n\n"
        f"3️⃣ Enter exact amount: <b>{total_price:.2f} USDT</b>\n"
        f"4️⃣ In <b>Note/Comment</b> write your Order ID:\n"
        f"<code>{order_id}</code>\n\n"
        f"5️⃣ Complete the transfer\n"
        f"6️⃣ <b>Copy the Binance Order ID</b> from your payment receipt\n"
        f"7️⃣ <b>Send it here</b> in this chat ↓\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ Once confirmed, your codes will be delivered <b>automatically!</b>\n\n"
        f"{ce('error')} <b>Do NOT send the Order ID above as the TXID.</b>\n"
        f"Send the Binance Order ID from your payment receipt."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Cancel", callback_data=f"back_to_prod_{product_key}")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)


async def receive_binance_txid(message: Message):
    """
    Receive TXID from user and verify payment via Binance Pay API.
    Auto-deliver if payment is confirmed.
    """
    user_id = message.from_user.id
    txid = message.text.strip()

    # Check if user is in TXID waiting state
    if user_id not in binance_txid_waiting:
        # Try to find order by TXID directly
        pass
    else:
        order_id = binance_txid_waiting.pop(user_id)
        # Update order with submitted TXID
        await update_binance_order_txid(order_id, txid)

    # Verify payment via Binance Pay API (regular account)
    verifying_msg = await message.answer(
        f"{ce('loading')} <b>Verifying payment...</b>\n"
        f"TXID: <code>{txid}</code>\n"
        f"Please wait a moment...",
        parse_mode="HTML",
    )

    try:
        from services.binance_pay import verify_payment_by_txid

        result = await verify_payment_by_txid(
            txid=txid,
            expected_order_id=order_id,
        )

        if not result["found"]:
            await verifying_msg.edit_text(
                f"{ce('error')} <b>{result.get('error', 'Transaction not found')}</b>\n\n"
                f"Make sure you:\n"
                f"1. Copied the correct <b>Binance Order ID</b> from your payment receipt\n"
                f"2. Included the Order ID <code>{order_id}</code> in the payment note\n"
                f"3. Wait 1-2 minutes after payment and try again\n\n"
                f"Need help? Contact {SUPPORT}",
                parse_mode="HTML",
            )
            return

        if not result["paid"]:
            await verifying_msg.edit_text(
                f"{ce('error')} <b>Payment not completed!</b>\n"
                f"Status: <code>{result.get('status', 'unknown')}</code>\n\n"
                f"TXID: <code>{txid}</code>\n"
                f"Amount: {result.get('amount')} {result.get('currency')}\n\n"
                f"Your payment may still be processing. Wait 1-2 minutes and try again.",
                parse_mode="HTML",
            )
            return

        if result.get("error"):
            # Found but has error (e.g. amount mismatch)
            await verifying_msg.edit_text(
                f"{ce('error')} <b>{result['error']}</b>\n\n"
                f"TXID: <code>{txid}</code>\n"
                f"Found Amount: {result.get('amount')} {result.get('currency')}\n"
                f"Note: {result.get('note', 'N/A')}\n\n"
                f"Contact {SUPPORT} if you need help.",
                parse_mode="HTML",
            )
            return

        # Payment confirmed - auto deliver!
        paid_amount = result["amount"]
        order_record = await get_payment_by_order(order_id)
        if not order_record:
            await verifying_msg.edit_text(
                f"{ce('error')} Internal error: Order not found. Contact support.",
                parse_mode="HTML",
            )
            return

        product_key = order_record["product_key"]
        qty = order_record["quantity"]
        product = PRODUCTS[product_key]

        # Check if already delivered
        if order_record["status"] == "delivered":
            await verifying_msg.edit_text(
                f"{ce('success')} <b>Already delivered!</b>\n"
                f"Check your chat history for the codes.",
                parse_mode="HTML",
            )
            return

        # Reserve stock
        items = await reserve_stock(product["stock_name"], qty)
        if items is None:
            await verifying_msg.edit_text(
                f"{ce('error')} <b>Payment confirmed but out of stock!</b>\n"
                f"Admins have been notified. Please contact support.",
                parse_mode="HTML",
            )
            from .admin import notify_admins_out_of_stock
            await notify_admins_out_of_stock(user_id, product, qty, order_id)
            return

        # Mark as delivered
        await mark_binance_order_delivered(order_id)

        # Send codes to user
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        delivery_text = (
            f"{ce('success')} <b>Payment Verified & Auto-Delivered!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('vip')} <b>{product['title']}</b>\n"
            f"{ce('quantity')} Quantity: <b>{qty}</b>\n"
            f"{ce('checkout')} Order ID: <code>{order_id}</code>\n"
            f"💰 Paid: <b>{paid_amount} USDT</b>\n\n"
            f"🔑 <b>Your Codes:</b>\n{codes_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
        )
        await verifying_msg.delete()
        await message.answer(delivery_text, parse_mode="HTML")

        # Notify admins
        from .admin import notify_admins_auto_delivery
        await notify_admins_auto_delivery(user_id, product, qty, order_id, items)

        # Post to channel
        if CHANNEL_USERNAME != "@YourChannelUsername":
            group_msg = (
                f"{ce('buy_cart')} <b>New Auto-Purchase!</b>\n\n"
                f"{ce('diamond_arrow')} <b>Product:</b> {product['title']}\n"
                f"{ce('sparkles_pay')} <b>QTY:</b> {qty}\n"
                f"{ce('checkout')} <b>Order:</b> <code>{order_id[:20]}...</code>\n\n"
                f"<i>Paid via Binance Pay Auto</i> {ce('secure_shield')}"
            )
            try:
                await bot.send_message(
                    chat_id=CHANNEL_USERNAME,
                    text=group_msg,
                    parse_mode="HTML",
                )
            except Exception:
                pass

    except RuntimeError as e:
        await verifying_msg.edit_text(
            f"{ce('error')} <b>Verification Error:</b>\n"
            f"<code>{str(e)}</code>\n\n"
            f"Make sure you sent the <b>Binance Order ID</b> from your payment receipt.\n"
            f"Contact {SUPPORT} if you need help.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"Binance TXID verification error: {e}")
        await verifying_msg.edit_text(
            f"{ce('error')} <b>Could not verify payment.</b>\n"
            f"Please try again later or contact {SUPPORT}",
            parse_mode="HTML",
        )


# ═══════════════════════════════════════════════════════════
# Deposit Handlers
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data == "deposit_currency_USDT")
async def cb_deposit_currency(call: CallbackQuery):
    await call.answer()
    deposit_waiting[call.from_user.id] = "USDT"
    text = "💰 <b>Enter amount to deposit (e.g., 10 or 5.5):</b>"
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())


async def receive_deposit_amount(message: Message):
    """Process deposit amount input."""
    user_id = message.from_user.id
    currency = deposit_waiting.get(user_id, "USDT")

    try:
        amount = float(message.text.strip())
        if amount < 1:
            raise ValueError
    except ValueError:
        await message.answer(
            f"{ce('error')} Please enter a valid number greater than 1.", parse_mode="HTML"
        )
        return

    deposit_waiting.pop(user_id, None)
    text = f"💳 <b>Deposit via Crypto</b>\n\nAmount: <b>{amount} {currency}</b>"
    await message.answer(text, reply_markup=deposit_payment_buttons(amount, currency), parse_mode="HTML")


@router.callback_query(F.data.startswith("topup_binance_"))
async def cb_topup_binance(call: CallbackQuery):
    """Show Binance deposit instructions."""
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    currency = parts[3]
    user_id = call.from_user.id

    from config import BINANCE_ID

    text = (
        f"{ce('binance')} <b>Manual Binance Deposit</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Amount to transfer: <b>{amount} {currency}</b>\n\n"
        f"{ce('loading')} Please transfer the exact amount to the following Binance ID:\n\n"
        f"{ce('arrow_right')} <code>{BINANCE_ID}</code>\n\n"
        f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team:\n"
        f"{ce('support')} {SUPPORT}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="home_main")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

    # Notify admins
    from .admin import notify_admins_deposit_request
    await notify_admins_deposit_request("Binance", call.from_user, amount, currency)


@router.callback_query(F.data.startswith("topup_bep20_"))
async def cb_topup_bep20(call: CallbackQuery):
    """Show USDT BEP20 deposit instructions."""
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    currency = parts[3]
    user_id = call.from_user.id

    from config import BEP20_ADDRESS

    text = (
        f"{ce('usdt')} <b>USDT (BEP20) Deposit</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{ce('price')} Amount to transfer: <b>{amount} {currency}</b>\n\n"
        f"{ce('loading')} Please transfer the amount to the following Address (BEP20):\n\n"
        f"<code>{BEP20_ADDRESS}</code>\n\n"
        f"⚠️ <b>IMPORTANT:</b> Please transfer the EXACT amount ({amount} {currency}) "
        f"<i>net</i> after network fees.\n\n"
        f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team:\n"
        f"{ce('support')} {SUPPORT}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="home_main")],
        ]
    )
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

    # Notify admins
    from .admin import notify_admins_deposit_request
    await notify_admins_deposit_request("USDT BEP20", call.from_user, amount, currency)


# ═══════════════════════════════════════════════════════════
# Force Subscribe Check
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery):
    """Handle subscription check callback."""
    if CHANNEL_USERNAME == "@YourChannelUsername":
        await call.answer("Channel is not configured yet.", show_alert=True)
        return

    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_USERNAME, user_id=call.from_user.id
        )
        if member.status in ["member", "administrator", "creator"]:
            await process_referral_reward(call.from_user.id)
            await call.message.delete()
            await call.answer(
                "✅ Thank you for subscribing! You can now use the bot.", show_alert=True
            )
            await send_home(call.message)
        else:
            await call.answer("❌ You haven't joined yet!", show_alert=True)
    except Exception:
        await call.answer("Error checking subscription.", show_alert=True)


# ═══════════════════════════════════════════════════════════
# Text Message Router
# ═══════════════════════════════════════════════════════════


@router.message(F.text)
async def handle_text(message: Message):
    """Route text messages to appropriate handlers."""
    user_id = message.from_user.id
    text = message.text.strip()

    # Cancel handling
    if text in ["❌ Cancel", "Cancel"]:
        buy_waiting.pop(user_id, None)
        deposit_waiting.pop(user_id, None)
        await message.answer(
            f"{ce('error')} <b>Cancelled. Returning to main menu...</b>",
            reply_markup=main_reply_keyboard(),
            parse_mode="HTML",
        )
        await send_home(message)
        return

    # Ignore commands
    if text.startswith("/"):
        return

    # Route quantity input
    if user_id in buy_waiting:
        await receive_quantity(message)
        return

    # Route deposit amount input
    if user_id in deposit_waiting:
        await receive_deposit_amount(message)
        return

    # Route Binance TXID verification
    if user_id in binance_txid_waiting:
        await receive_binance_txid(message)
        return

    # Also allow checking any TXID that looks like a Binance order ID
    # Format: starts with numbers/letters, typical Binance Pay TXID format
    if len(text) >= 10 and text.isalnum() and not text.startswith("AIX-"):
        # Check if this TXID exists in our DB
        order_record = await get_binance_order_by_txid(text)
        if order_record:
            await receive_binance_txid(message)
            return

    # Reply keyboard navigation
    if text == "🛍 Products":
        msg = await animate_message(message)
        await handle_shop_action(msg)
    elif text == "🎧 Support":
        support_text = (
            f"{ce('support_msg')} <b>Quick support:</b>\n\n"
            f"{ce('telegram')} <b>Telegram:</b> {ce('arrow_right')} {SUPPORT}"
        )
        await message.answer(support_text, reply_markup=back_home_keyboard(), parse_mode="HTML")
    elif text == "💰 Wallet":
        # Build fake call object
        class FakeCall:
            def __init__(self, msg, user):
                self.message = msg
                self.from_user = user
            async def answer(self, *args, **kwargs):
                pass
        await cb_home_wallet(FakeCall(message, message.from_user))
    elif text == "🎁 Share & Earn":
        class FakeCall:
            def __init__(self, msg, user):
                self.message = msg
                self.from_user = user
            async def answer(self, *args, **kwargs):
                pass
        await cb_home_share(FakeCall(message, message.from_user))
    else:
        await send_home(message)


################################################################################
# MIDDLEWARE
################################################################################

"""
AIX Store Bot - Middleware
==========================
Security middleware: Ban check, Force Subscribe, Referral processing.
"""
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS, CHANNEL_USERNAME
from database import (
    create_user,
    update_user_info,
    is_user_banned,
    process_referral_reward,
)
from keyboards import force_subscribe_keyboard
from utils import ce


class SecurityMiddleware(BaseMiddleware):
    """
    Handles:
    1. User registration/updates
    2. Ban check
    3. Force channel subscription
    4. Referral reward processing
    """

    async def __call__(self, handler, event, data):
        # Skip group messages
        chat = data.get("event_chat")
        if chat and chat.type in ["group", "supergroup"]:
            return

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # ── 1. Extract referrer from /start command ──
        referrer_id = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start "):
            args = event.text.split()
            if len(args) > 1 and args[1].isdigit():
                referrer_id = int(args[1])

        # ── 2. Register/update user ──
        await create_user(user.id, user.username, user.first_name, referrer_id)
        # Update profile info on every interaction
        await update_user_info(user.id, user.username, user.first_name)

        # ── 3. Allow check_sub callback to pass through ──
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        # ── 4. Admin bypass ──
        if user.id in ADMIN_IDS:
            await process_referral_reward(user.id)
            return await handler(event, data)

        # ── 5. Ban check ──
        try:
            if await is_user_banned(user.id):
                return  # Silently ignore banned users
        except Exception:
            pass

        # ── 6. Force subscribe check ──
        if CHANNEL_USERNAME != "@YourChannelUsername":
            try:
                from loader import bot

                member = await bot.get_chat_member(
                    chat_id=CHANNEL_USERNAME, user_id=user.id
                )
                if member.status not in ["member", "administrator", "creator"]:
                    text = (
                        f"{ce('error')} <b>Access Denied!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"You must join our channel to use this bot.\n\n"
                        f"{ce('arrow_right')} Please join {CHANNEL_USERNAME} first."
                    )
                    kb = force_subscribe_keyboard(CHANNEL_USERNAME)
                    if isinstance(event, Message):
                        await event.answer(text, reply_markup=kb, parse_mode="HTML")
                    elif isinstance(event, CallbackQuery):
                        await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
                        await event.answer()
                    return
                else:
                    # User is subscribed → process any pending referral
                    await process_referral_reward(user.id)
            except Exception:
                pass
        else:
            # No channel configured → process referral directly
            await process_referral_reward(user.id)

        return await handler(event, data)


################################################################################
# LOADER
################################################################################

"""
AIX Store Bot - Loader
======================
Bot and Dispatcher instances.
"""
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


################################################################################
# MAIN
################################################################################

"""
AIX Store Bot - Main Entry Point
================================
Initialize and run the bot with proper lifecycle management.
"""
import asyncio
import logging
import sys

from aiogram.types import BotCommand

from loader import bot, dp
from database import init_db, close_pool
from middleware import SecurityMiddleware
from handlers import user, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def on_startup():
    """Initialize bot on startup."""
    logger.info("Starting AIX Store Bot...")
    await init_db()
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="menu", description="Return to main menu"),
    ])
    logger.info("Bot is ready!")


async def on_shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down AIX Store Bot...")
    await close_pool()
    await bot.session.close()
    logger.info("Bot stopped.")


def main():
    """Main entry point."""
    # Register middleware
    dp.message.middleware(SecurityMiddleware())
    dp.callback_query.middleware(SecurityMiddleware())

    # Register routers (admin first to catch admin commands)
    dp.include_router(admin.router)
    dp.include_router(user.router)

    # Register lifecycle hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start polling
    try:
        dp.run_polling(bot, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
