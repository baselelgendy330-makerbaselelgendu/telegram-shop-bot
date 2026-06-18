import asyncio
import os
import html
import re
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    URLInputFile,
    FSInputFile,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

# رابط صورة الهيدر الخضراء
AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

# --- قائمة الإيموجيات المتحركة ---
EMOJI = {
    "store": "5859297284029681680",
    "wallet": "6088990159334808217",
    "support": "6181322172263308706",
    "telegram": "6089099509202164251",
    "language": "5447410659077661506",
    "home": "5195140682590722632",
    "chatgpt": "5864127571754489150",
    "stock": "6089247294731852091",
    "shield": "5251203410396458957",
    "link": "5282843764451195532",
    "step": "5397782960512444700",
    "rocket": "6181682949516173646",
    "success": "6179298314953956852",
    "refresh": "5341715473882955310",
    "lightning": "6181421841274379029",
    "payment": "5352662091390008496",
    "binance": "6222208096257712941",
    "fire": "6266887773454603583",
    "announcement": "6181594486074777254",
    "stock_add": "5397916757333654639",
    "trash": "5445267414562389170",
    "error": "6181467651395558500",
    "arrows_up": "5449683594425410231",
    "arrows_down": "5447183459602669338",
    "bell": "5458603043203327669",
    "hundred": "6181303849932823189",
    "vip": "6181731641560407212",
    "verified": "5370941588165893740",
    "loading": "6089327236958132324",
    "num1": "5197397670724912036",
    "num2": "5197250993296785376",
    "num3": "5195203805725084605",
}

SAFE_EMOJI_FALLBACK = {
    "store": "🛍", "wallet": "💰", "support": "🎧", "telegram": "✈️",
    "language": "🌐", "home": "🏠", "chatgpt": "🤖", "stock": "📦",
    "shield": "🛡", "link": "🔗", "step": "🔹", "rocket": "🚀",
    "success": "✅", "refresh": "🔄", "lightning": "⚡", "payment": "💳",
    "binance": "🟡", "fire": "🔥", "announcement": "📢", "stock_add": "➕",
    "trash": "🗑", "error": "❌", "arrows_up": "⬆️", "arrows_down": "⬇️",
    "bell": "🔔", "hundred": "💯", "vip": "⭐", "verified": "☑️",
    "loading": "⏳", "num1": "1️⃣", "num2": "2️⃣", "num3": "3️⃣",
}

def ce(key: str, fallback: str = "") -> str:
    emoji_id = EMOJI.get(key)
    safe_fallback = SAFE_EMOJI_FALLBACK.get(key, fallback or "✅")
    if not emoji_id or not str(emoji_id).isdigit():
        return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'

def esc(value) -> str:
    return html.escape(str(value), quote=False)

def strip_custom_emoji(text: str) -> str:
    return re.sub(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r'\1', text)

async def safe_answer(message: Message, text: str, reply_markup=None):
    try:
        return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest:
        return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup)

async def safe_edit_or_answer(message, text: str, reply_markup=None):
    try:
        return await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest:
        try:
            return await message.edit_text(strip_custom_emoji(text), reply_markup=reply_markup)
        except Exception:
            return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup)
    except Exception:
        return await safe_answer(message, text, reply_markup)

async def safe_answer_photo(message: Message, caption: str, reply_markup=None):
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
                )
            return await message.answer_photo(
                photo=URLInputFile(AIX_HEADER_IMAGE),
                caption=strip_custom_emoji(caption),
                reply_markup=reply_markup,
            )
        except Exception:
            return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup)
    except Exception:
        return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup)

CDK_IMAGE_FILE = "https://i.postimg.cc/Twx17x9S/IMG-20260616-190321.jpg"
WALLET_DEPOSIT_KEY = "wallet_deposit"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

deposit_waiting: dict[int, str] = {}

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title_en": "CDK Activation Chatgpt For 1 year",
        "title_ar": "CDK Activation Chatgpt For 1 year",
        "image": CDK_IMAGE_FILE,
        "usd": 9,
        "type": "stock",
    }
}

# ---------------- Database ----------------
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            lang TEXT DEFAULT 'ar',
            balance_usdt NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            method TEXT,
            amount NUMERIC,
            currency TEXT,
            product_key TEXT DEFAULT 'cdk_chatgpt',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS product_key TEXT DEFAULT 'cdk_chatgpt';")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id SERIAL PRIMARY KEY,
            product TEXT NOT NULL,
            item_data TEXT NOT NULL,
            sold BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

async def ensure_user_by_id(user_id: int, username: str | None = None, first_name: str | None = None):
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users(telegram_id, username, first_name)
            VALUES($1, $2, $3)
            ON CONFLICT (telegram_id) DO UPDATE SET username=$2, first_name=$3
            """,
            user_id,
            username,
            first_name,
        )

async def ensure_user(message: Message):
    await ensure_user_by_id(message.from_user.id, message.from_user.username, message.from_user.first_name)

async def get_lang(user_id: int) -> str:
    async with db_pool.acquire() as conn:
        lang = await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id)
    return lang or "ar"

async def get_wallet_balance(user_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance_usdt FROM users WHERE telegram_id=$1",
            user_id,
        )
    if not row:
        return 0
    return row["balance_usdt"] or 0

async def get_stock_count(product_key: str = "cdk_chatgpt"):
    product = PRODUCTS[product_key]
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            product["stock_name"],
        )

async def product_counts():
    return {
        "cdk_chatgpt": await get_stock_count("cdk_chatgpt"),
    }

# ---------------- Helpers ----------------
def user_display_name(user) -> str:
    return user.first_name or user.username or "User"

def format_amount(amount):
    try:
        amount = float(amount)
        if amount.is_integer():
            return str(int(amount))
        return str(amount).rstrip("0").rstrip(".")
    except Exception:
        return str(amount)

def resolve_stock_product(product_type: str):
    if product_type.lower() in ["chatgpt", "cdk", "cdk_chatgpt"]:
        return "cdk_chatgpt", PRODUCTS["cdk_chatgpt"]["stock_name"]
    return None, None

def product_label(product_key: str):
    if product_key == "cdk_chatgpt":
        return "CDK Activation Chatgpt For 1 year"
    return product_key

# ---------------- Animations ----------------
async def edit_or_answer(message, text: str, reply_markup=None):
    return await safe_edit_or_answer(message, text, reply_markup)

async def animate_message(message: Message, lang: str):
    text = f"{ce('loading', '⏳')} <b>Loading...</b>" if lang == "en"
