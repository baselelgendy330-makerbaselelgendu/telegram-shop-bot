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
VODAFONE_CASH = "01063467929"
INSTAPAY = "mahmoud2662000"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

# ضع رابط صورة الهيدر الخضراء هنا أو في Environment باسم AIX_HEADER_IMAGE
AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

EMOJI = {
    "chatgpt": "5359726582447487916",
    "store": "5373261557700509032",
    "verified": "5370941588165893740",
    "binance": "5319236736042149889",
    "vodafone": "5352562482508481505",
    "instapay": "5845899541571706084",
    "payment": "5364036341610858181",
    "gemini": "5875095634033250205",
    "wallet": "6267013757730296733",
    "cart": "5859297284029681680",
    "support": "6181322172263308706",
    "telegram": "6089099509202164251",
    "fire": "6179353385024626225",
    "announcement": "6181594486074777254",
    "rocket": "6181682949516173646",
    "shield": "6179259084722675328",
    "lightning": "6179411633371095707",
    "home": "5195140682590722632",
    "refresh": "5292226786229236118",
    "stock": "6181284483925286789",
    "success": "6179298314953956852",
    "error": "6181467651395558500",
    "vip": "6181731641560407212",
    "language": "6181573608238751317",
    "stock_add": "5397916757333654639",
}

SAFE_EMOJI_FALLBACK = {
    "chatgpt": "🤖",
    "store": "🛍",
    "verified": "✅",
    "binance": "🟡",
    "vodafone": "🔴",
    "instapay": "🟣",
    "payment": "💳",
    "gemini": "💎",
    "wallet": "💰",
    "cart": "🛒",
    "support": "🎧",
    "telegram": "✈️",
    "fire": "🔥",
    "announcement": "📢",
    "rocket": "🚀",
    "shield": "🛡",
    "lightning": "⚡",
    "home": "🏠",
    "refresh": "🔄",
    "stock": "📦",
    "success": "✅",
    "error": "❌",
    "vip": "⭐",
    "language": "🌐",
    "stock_add": "➕",
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
    # الأفضل: ضع ملف aix_header.jpg في نفس مجلد bot.py على GitHub.
    # لو مش موجود، سيحاول رابط AIX_HEADER_IMAGE، ولو فشل يرسل الرسالة بدون صورة.
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


CHATGPT_IMAGE = "https://i.postimg.cc/g0GQwy2V/f413a409aabc9c298e8b6b461affaa99.jpg"
GEMINI_IMAGE = "https://i.postimg.cc/0Qfr71mh/images-(1).jpg"

CHATGPT_PRODUCT = "ChatGPT Plus Ready Account"
CHATGPT_EMAIL_PRODUCT = "ChatGPT Email Activation"
GEMINI_READY_PRODUCT = "Gemini Pro Ready Account"
GEMINI_EMAIL_PRODUCT = "Gemini Email Activation"
WALLET_DEPOSIT_KEY = "wallet_deposit"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

deposit_waiting: dict[int, str] = {}

PRODUCTS = {
    "chatgpt": {
        "stock_name": CHATGPT_PRODUCT,
        "title_en": "ChatGPT Plus Ready Account",
        "title_ar": "ChatGPT Plus حساب جاهز",
        "image": CHATGPT_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "stock",
        "warranty_ar": "15 يوم",
        "warranty_en": "15 days",
    },
    "chatgpt_email": {
        "stock_name": CHATGPT_EMAIL_PRODUCT,
        "title_en": "ChatGPT Plus 1M On Your Email",
        "title_ar": "ChatGPT Plus 1M تفعيل على إيميلك",
        "image": CHATGPT_IMAGE,
        "usd": 5,
        "egp": 250,
        "type": "activation",
        "warranty_ar": "15 يوم",
        "warranty_en": "15 days",
    },
    "gemini_ready": {
        "stock_name": GEMINI_READY_PRODUCT,
        "title_en": "Gemini Pro 12 Month Ready Account",
        "title_ar": "Gemini Pro 12 شهر حساب جاهز",
        "image": GEMINI_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "stock",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    },
    "gemini_email": {
        "stock_name": GEMINI_EMAIL_PRODUCT,
        "title_en": "Gemini Pro 12M On Your Email",
        "title_ar": "Gemini Pro 12M تفعيل على إيميلك",
        "image": GEMINI_IMAGE,
        "usd": 4,
        "egp": 200,
        "type": "activation",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    },
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
            balance_egp NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_egp NUMERIC DEFAULT 0;")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            method TEXT,
            amount NUMERIC,
            currency TEXT,
            product_key TEXT DEFAULT 'chatgpt',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS product_key TEXT DEFAULT 'chatgpt';")
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
            "SELECT balance_usdt, balance_egp FROM users WHERE telegram_id=$1",
            user_id,
        )
    if not row:
        return 0, 0
    return row["balance_usdt"] or 0, row["balance_egp"] or 0

async def get_stock_count(product_key: str = "chatgpt"):
    product = PRODUCTS[product_key]
    if product["type"] == "activation":
        return "∞"
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            product["stock_name"],
        )

async def product_counts():
    return {
        "chatgpt": await get_stock_count("chatgpt"),
        "chatgpt_email": "∞",
        "gemini_ready": await get_stock_count("gemini_ready"),
        "gemini_email": "∞",
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
    aliases = {
        "chatgpt": "chatgpt",
        "chat": "chatgpt",
        "gpt": "chatgpt",
        "chatgpt_ready": "chatgpt",
        "chatgpt-ready": "chatgpt",
        "gemini": "gemini_ready",
        "gemini_ready": "gemini_ready",
        "gemini-ready": "gemini_ready",
    }
    product_key = aliases.get(product_type.lower())
    if not product_key:
        return None, None
    return product_key, PRODUCTS[product_key]["stock_name"]

def product_label(product_key: str):
    if product_key == "chatgpt":
        return "ChatGPT Plus Ready Account"
    if product_key == "chatgpt_email":
        return "ChatGPT Email Activation"
    if product_key == "gemini_ready":
        return "Gemini Pro Ready Account"
    if product_key == "gemini_email":
        return "Gemini Email Activation"
    return product_key

# ---------------- Animations ----------------
async def edit_or_answer(message, text: str, reply_markup=None):
    return await safe_edit_or_answer(message, text, reply_markup)

async def animate_message(message, title: str, style: str = "default"):
    frames_map = {
        "default": [
            "▱▱▱▱▱▱▱▱▱▱ 0%",
            "▰▰▱▱▱▱▱▱▱▱ 20%",
            "▰▰▰▰▱▱▱▱▱▱ 40%",
            "▰▰▰▰▰▰▱▱▱▱ 60%",
            "▰▰▰▰▰▰▰▰▱▱ 80%",
            "▰▰▰▰▰▰▰▰▰▰ 100%",
        ],
        "wallet": [
            "◇◇◇◇◇◇◇◇◇◇ 0%",
            "◆◆◇◇◇◇◇◇◇◇ 20%",
            "◆◆◆◆◇◇◇◇◇◇ 40%",
            "◆◆◆◆◆◆◇◇◇◇ 60%",
            "◆◆◆◆◆◆◆◆◇◇ 80%",
            "◆◆◆◆◆◆◆◆◆◆ 100%",
        ],
        "deposit": [
            "⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡ 0%",
            "⬢⬢⬡⬡⬡⬡⬡⬡⬡⬡ 20%",
            "⬢⬢⬢⬢⬡⬡⬡⬡⬡⬡ 40%",
            "⬢⬢⬢⬢⬢⬢⬡⬡⬡⬡ 60%",
            "⬢⬢⬢⬢⬢⬢⬢⬢⬡⬡ 80%",
            "⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢ 100%",
        ],
        "checkout": [
            "▰▱▱▱▱ 20%",
            "▰▰▱▱▱ 40%",
            "▰▰▰▱▱ 60%",
            "▰▰▰▰▱ 80%",
            "▰▰▰▰▰ 100%",
        ],
    }
    frames = frames_map.get(style, frames_map["default"])
    try:
        await message.edit_text(f"{title}\n\n{frames[0]}", parse_mode="HTML")
        msg = message
    except Exception:
        msg = await message.answer(f"{title}\n\n{frames[0]}", parse_mode="HTML")
    for frame in frames[1:]:
        await asyncio.sleep(0.12)
        try:
            await msg.edit_text(f"{title}\n\n{frame}", parse_mode="HTML")
        except Exception:
            pass
    await asyncio.sleep(0.08)
    return msg

# ---------------- Keyboards ----------------
def home_keyboard(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Browse Products", callback_data="home_shop")],
            [InlineKeyboardButton(text="Deposit", callback_data="home_deposit"), InlineKeyboardButton(text="Wallet", callback_data="home_wallet")],
            [InlineKeyboardButton(text="Support", callback_data="home_support")],
            [InlineKeyboardButton(text="Language", callback_data="home_language")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="تصفح المنتجات", callback_data="home_shop")],
        [InlineKeyboardButton(text="إيداع", callback_data="home_deposit"), InlineKeyboardButton(text="المحفظة", callback_data="home_wallet")],
        [InlineKeyboardButton(text="الدعم", callback_data="home_support")],
        [InlineKeyboardButton(text="اللغة", callback_data="home_language")],
    ])

def back_home_keyboard(lang: str):
    text = "Main Menu" if lang == "en" else "القائمة الرئيسية"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data="home_main")]])

def product_buttons(lang: str, counts: dict):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"ChatGPT Plus Ready Account | $6 | Stock {counts['chatgpt']}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text="ChatGPT On Your Email | $5", callback_data="product_chatgpt_email")],
            [InlineKeyboardButton(text=f"Gemini Pro Ready Account | $6 | Stock {counts['gemini_ready']}", callback_data="product_gemini_ready")],
            [InlineKeyboardButton(text="Gemini On Your Email | $4", callback_data="product_gemini_email")],
            [InlineKeyboardButton(text="Refresh", callback_data="refresh_products"), InlineKeyboardButton(text="Back", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"ChatGPT Plus Ready Account | 300 جنيه | المتاح {counts['chatgpt']}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text="ChatGPT على إيميلك | 250 جنيه", callback_data="product_chatgpt_email")],
        [InlineKeyboardButton(text=f"Gemini Pro Ready Account | 300 جنيه | المتاح {counts['gemini_ready']}", callback_data="product_gemini_ready")],
        [InlineKeyboardButton(text="Gemini على إيميلك | 200 جنيه", callback_data="product_gemini_email")],
        [InlineKeyboardButton(text="تحديث", callback_data="refresh_products"), InlineKeyboardButton(text="رجوع", callback_data="home_main")],
    ])

def product_details_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}")],
            [InlineKeyboardButton(text="Back to Shop", callback_data="home_shop")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="رجوع للمتجر", callback_data="home_shop")],
    ])

def payment_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data=f"pay_binance_{product_key}")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data=f"pay_vodafone_{product_key}")],
            [InlineKeyboardButton(text="🟣 InstaPay", callback_data=f"pay_instapay_{product_key}")],
            [InlineKeyboardButton(text="Back", callback_data=f"product_{product_key}")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data=f"pay_vodafone_{product_key}")],
        [InlineKeyboardButton(text="🟣 انستا باي", callback_data=f"pay_instapay_{product_key}")],
        [InlineKeyboardButton(text="رجوع", callback_data=f"product_{product_key}")],
    ])

def deposit_currency_buttons(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="EGP Deposit", callback_data="deposit_currency_EGP")],
            [InlineKeyboardButton(text="USDT Deposit", callback_data="deposit_currency_USDT")],
            [InlineKeyboardButton(text="Back", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إيداع بالمصري", callback_data="deposit_currency_EGP")],
        [InlineKeyboardButton(text="إيداع بالدولار USDT", callback_data="deposit_currency_USDT")],
        [InlineKeyboardButton(text="رجوع", callback_data="home_main")],
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str):
    amount_txt = format_amount(amount)
    currency = currency.upper()
    if currency == "USDT":
        if lang == "en":
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🟡 Binance UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
                [InlineKeyboardButton(text="Change Amount", callback_data="deposit_currency_USDT")],
            ])
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🟡 بينانس UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
            [InlineKeyboardButton(text="تغيير المبلغ", callback_data="deposit_currency_USDT")],
        ])
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🔴 Vodafone Cash • {amount_txt} EGP", callback_data=f"topup_vodafone_{amount_txt}_EGP")],
            [InlineKeyboardButton(text=f"🟣 InstaPay • {amount_txt} EGP", callback_data=f"topup_instapay_{amount_txt}_EGP")],
            [InlineKeyboardButton(text="Change Amount", callback_data="deposit_currency_EGP")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔴 فودافون كاش • {amount_txt} جنيه", callback_data=f"topup_vodafone_{amount_txt}_EGP")],
        [InlineKeyboardButton(text=f"🟣 انستا باي • {amount_txt} جنيه", callback_data=f"topup_instapay_{amount_txt}_EGP")],
        [InlineKeyboardButton(text="تغيير المبلغ", callback_data="deposit_currency_EGP")],
    ])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])


def main_reply_keyboard(lang: str):
    if lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛍 Products"), KeyboardButton(text="🎧 Support")],
                [KeyboardButton(text="💰 Wallet"), KeyboardButton(text="🌐 Language")],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 المنتجات"), KeyboardButton(text="🎧 الدعم")],
            [KeyboardButton(text="💰 المحفظة"), KeyboardButton(text="🌐 اللغة")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

MENU_TEXTS = {
    "🛍 Products", "Products", "🛍 المنتجات", "المنتجات",
    "🎧 Support", "Support", "🎧 الدعم", "الدعم",
    "💰 Wallet", "Wallet", "💰 المحفظة", "المحفظة",
    "🌐 Language", "Language", "🌐 اللغة", "اللغة",
    "🏠 Home", "Home", "🏠 الرئيسية", "الرئيسية",
}

# ---------------- Texts ----------------
def home_text(lang: str, name: str):
    name = esc(name)
    if lang == "en":
        return (
            f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Hey, <b>{name}</b>\n"
            f"Welcome to your premium AI subscriptions store.\n\n"
            f"{ce('store','🛍')} <b>Shop</b> — Browse & buy products\n"
            f"{ce('wallet','💰')} <b>Deposit</b> — Add funds to your wallet\n"
            f"{ce('cart','🛒')} <b>Orders</b> — Fast digital delivery\n"
            f"{ce('support','🎧')} <b>Support</b> — Get help anytime\n\n"
            f"{ce('lightning','⚡')} Fast activation • Secure payments • Trusted service"
        )
    return (
        f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"أهلاً، <b>{name}</b>\n"
        f"نورت متجر اشتراكات الذكاء الاصطناعي المميزة.\n\n"
        f"{ce('store','🛍')} <b>المتجر</b> — تصفح واشتري المنتجات\n"
        f"{ce('wallet','💰')} <b>إيداع</b> — إضافة رصيد للمحفظة\n"
        f"{ce('cart','🛒')} <b>الطلبات</b> — تسليم رقمي سريع\n"
        f"{ce('support','🎧')} <b>الدعم</b> — مساعدة في أي وقت\n\n"
        f"{ce('lightning','⚡')} تفعيل سريع • دفع آمن • خدمة موثوقة"
    )

def product_list_text(lang: str):
    if lang == "en":
        return (
            f"{ce('store','🛍')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            f"{ce('chatgpt','🤖')} <b>ChatGPT Plus Ready Account</b>\n"
            f"Price: $6 / 300 EGP | Warranty: 15 days\n\n"
            f"{ce('chatgpt','🤖')} <b>ChatGPT Plus On Your Email</b>\n"
            f"Price: $5 / 250 EGP | Warranty: 15 days\n\n"
            f"{ce('gemini','🟢')} <b>Gemini Pro Ready Account</b>\n"
            f"Price: $6 / 300 EGP | Warranty: 1 Year\n\n"
            f"{ce('gemini','🟢')} <b>Gemini Pro On Your Email</b>\n"
            f"Price: $4 / 200 EGP | Warranty: 1 Year\n\n"
            f"Choose a product below:"
        )
    return (
        f"{ce('store','🛍')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('chatgpt','🤖')} <b>ChatGPT Plus Ready Account</b>\n"
        f"السعر: 300 جنيه / $6 | الضمان: 15 يوم\n\n"
        f"{ce('chatgpt','🤖')} <b>ChatGPT Plus على إيميلك</b>\n"
        f"السعر: 250 جنيه / $5 | الضمان: 15 يوم\n\n"
        f"{ce('gemini','🟢')} <b>Gemini Pro Ready Account</b>\n"
        f"السعر: 300 جنيه / $6 | الضمان: سنة كاملة\n\n"
        f"{ce('gemini','🟢')} <b>Gemini Pro على إيميلك</b>\n"
        f"السعر: 200 جنيه / $4 | الضمان: سنة كاملة\n\n"
        f"اختار المنتج من الأزرار:"
    )

def deposit_intro_text(lang: str):
    if lang == "en":
        return (
            f"{ce('wallet','💰')} <b>Deposit Balance</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            f"Choose the currency you want to deposit.\n\n"
            f"EGP: minimum 250 EGP\n"
            f"USDT: minimum 5 USDT"
        )
    return (
        f"{ce('wallet','💰')} <b>إيداع رصيد</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"اختار العملة اللي عايز تعمل بيها إيداع.\n\n"
        f"المصري: أقل مبلغ 250 جنيه\n"
        f"الدولار USDT: أقل مبلغ 5 USDT"
    )

# ---------------- Home/UI Handlers ----------------
async def send_home(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    name = user_display_name(message.from_user)

    await safe_answer_photo(
        message,
        home_text(lang, name),
        reply_markup=home_keyboard(lang),
    )

    await message.answer(
        "Main Menu" if lang == "en" else "القائمة الرئيسية",
        reply_markup=main_reply_keyboard(lang),
    )

@dp.message(CommandStart())
async def start(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    await send_home(message)


@dp.message(Command("menu"))
async def menu_command(message: Message):
    await start(message)

@dp.message(Command("products"))
async def products_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, f"{ce('store','🛍')} Loading products..." if lang == "en" else f"{ce('store','🛍')} جاري تحميل المنتجات...", "default")
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

@dp.message(Command("wallet"))
async def wallet_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(message.from_user.id)
    msg = await animate_message(message, f"{ce('wallet','💰')} Syncing Wallet..." if lang == "en" else f"{ce('wallet','💰')} مزامنة المحفظة...", "wallet")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Deposit / إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="Main Menu / الرئيسية", callback_data="home_main")],
    ])
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\nUSDT Balance: {balance_usdt} USDT\nEGP Balance: {balance_egp} EGP"
        if lang == "en" else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\nرصيد الدولار: {balance_usdt} USDT\nرصيد المصري: {balance_egp} جنيه"
    )
    await edit_or_answer(msg, text, reply_markup=kb)

@dp.message(Command("support"))
async def support_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    text = (
        f"{ce('support','🎧')} <b>Support Center</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}"
        if lang == "en" else
        f"{ce('support','🎧')} <b>مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}"
    )
    await message.answer(text, reply_markup=back_home_keyboard(lang), parse_mode="HTML")

@dp.callback_query(F.data == "home_main")
async def home_main(call: CallbackQuery):
    await ensure_user_by_id(call.from_user.id, call.from_user.username, call.from_user.first_name)
    lang = await get_lang(call.from_user.id)
    name = user_display_name(call.from_user)
    msg = await animate_message(call.message, f"{ce('lightning','⚡')} Loading AIX Store..." if lang == "en" else f"{ce('lightning','⚡')} جاري فتح AIX Store...", "default")
    await edit_or_answer(msg, home_text(lang, name), reply_markup=home_keyboard(lang))
    await call.answer()

@dp.callback_query(F.data == "home_language")
async def home_language(call: CallbackQuery):
    await call.message.answer(f"{ce('language','🌐')} اختر اللغة / Choose language:", reply_markup=language_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.message(Command("language"))
async def language_command(message: Message):
    await ensure_user(message)
    await message.answer(f"{ce('language','🌐')} اختر اللغة / Choose language:", reply_markup=language_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    await ensure_user_by_id(call.from_user.id, call.from_user.username, call.from_user.first_name)
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await call.message.answer(
        f"{ce('success','✅')} Language changed to English" if lang == "en" else f"{ce('success','✅')} تم تغيير اللغة للعربية",
        reply_markup=home_keyboard(lang),
        parse_mode="HTML",
    )
    await call.answer()

# ---------------- Shop ----------------
@dp.callback_query(F.data == "home_shop")
async def shop_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, f"{ce('store','🛍')} Loading products..." if lang == "en" else f"{ce('store','🛍')} جاري تحميل المنتجات...", "default")
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer()

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, f"{ce('store','🛍')} Loading products..." if lang == "en" else f"{ce('store','🛍')} جاري تحميل المنتجات...", "default")
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, f"{ce('refresh','🔄')} Updating products..." if lang == "en" else f"{ce('refresh','🔄')} جاري تحديث المنتجات...", "default")
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer("Updated ✅")

@dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await animate_message(call.message, f"{ce('chatgpt','🤖')} Preparing product..." if lang == "en" else f"{ce('chatgpt','🤖')} جاري تجهيز المنتج...", "checkout")
    count = await get_stock_count("chatgpt")
    caption = (
        f"{ce('chatgpt','🤖')} <b>ChatGPT Plus Ready Account</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $6\n📦 Stock: {count}\n🛡 Warranty: 15 Days\n\n"
        f"📦 Product Type: Ready Account\n"
        f"🔐 Delivery Type: Email + Password\n"
        f"⏳ Subscription: 1 Month ChatGPT Plus\n"
        f"⚡ Delivery after payment approval\n"
        f"💎 Premium account ready to login and use immediately"
        if lang == "en"
        else
        f"{ce('chatgpt','🤖')} <b>ChatGPT Plus Ready Account</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 300 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: 15 يوم\n\n"
        f"📦 نوع المنتج: حساب جاهز\n"
        f"🔐 نوع التسليم: إيميل + باسورد\n"
        f"⏳ الاشتراك: ChatGPT Plus لمدة شهر\n"
        f"⚡ التسليم بعد تأكيد الدفع\n"
        f"💎 حساب بريميوم جاهز لتسجيل الدخول والاستخدام مباشرة"
    )
    await call.message.answer_photo(URLInputFile(CHATGPT_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "chatgpt"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "product_chatgpt_email")
async def product_chatgpt_email(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await animate_message(call.message, f"{ce('vip','⭐')} Preparing product..." if lang == "en" else f"{ce('vip','⭐')} جاري تجهيز المنتج...", "checkout")
    caption = (
        f"{ce('chatgpt','🤖')} <b>ChatGPT Plus On Your Email</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $5\n🛡 Warranty: 15 Days\n\n"
        f"📧 Activation on your personal email\n"
        f"🔐 Your email stays with you\n"
        f"💬 After payment confirmation, contact admin to complete activation."
        if lang == "en"
        else
        f"✨ ChatGPT Plus على إيميلك\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 250 جنيه\n🛡 الضمان: 15 يوم\n\n"
        f"📧 التفعيل على إيميلك الشخصي\n"
        f"🔐 الإيميل يفضل معاك\n"
        f"💬 بعد تأكيد الدفع، تواصل مع الأدمن لإتمام التفعيل."
    )
    await call.message.answer_photo(URLInputFile(CHATGPT_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "chatgpt_email"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "product_gemini_ready")
async def product_gemini_ready(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await animate_message(call.message, f"{ce('gemini','🟢')} Preparing product..." if lang == "en" else f"{ce('gemini','🟢')} جاري تجهيز المنتج...", "checkout")
    count = await get_stock_count("gemini_ready")
    caption = (
        f"{ce('gemini','🟢')} <b>Gemini Pro Ready Account</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $6\n📦 Stock: {count}\n🛡 Warranty: Full 12 Months\n\n"
        f"📦 Product Type: Ready Gemini Pro Account\n"
        f"🔐 Delivery Type: Email + Password + 2FA\n"
        f"⏳ Subscription: 12 Months\n"
        f"☁️ 5TB Storage\n"
        f"🤖 Gemini Advanced Included\n"
        f"⚡ Ready to login and use after delivery"
        if lang == "en"
        else
        f"{ce('gemini','🟢')} <b>Gemini Pro Ready Account</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 300 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: كامل لمدة 12 شهر\n\n"
        f"📦 نوع المنتج: حساب جيميناي برو جاهز\n"
        f"🔐 نوع التسليم: إيميل + باسورد + 2FA\n"
        f"⏳ مدة الاشتراك: 12 شهر\n"
        f"☁️ مساحة 5 تيرا بايت\n"
        f"🤖 Gemini Advanced مفعّل\n"
        f"⚡ جاهز لتسجيل الدخول والاستخدام بعد التسليم"
    )
    await call.message.answer_photo(URLInputFile(GEMINI_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "gemini_ready"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "product_gemini_email")
async def product_gemini_email(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await animate_message(call.message, f"{ce('gemini','🟢')} Preparing product..." if lang == "en" else f"{ce('gemini','🟢')} جاري تجهيز المنتج...", "checkout")
    caption = (
        f"{ce('gemini','🟢')} <b>Gemini Pro On Your Email</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $4\n🛡 Warranty: 1 Year\n\n"
        f"☁️ 5TB Storage\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 Monthly Credits\n"
        f"👥 Add 5 Family Members\n🔑 You Become The Owner\n\n"
        f"📧 Activated On Your Personal Email"
        if lang == "en"
        else
        f"{ce('gemini','🟢')} <b>Gemini على إيميلك الشخصي</b>\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 200 جنيه\n🛡 الضمان: سنة كاملة\n\n"
        f"☁️ مساحة 5 تيرا بايت\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 كريديت شهري\n"
        f"👥 إضافة 5 أشخاص\n🔑 تصبح المالك الأساسي\n\n"
        f"📧 التفعيل على إيميلك الشخصي"
    )
    await call.message.answer_photo(URLInputFile(GEMINI_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "gemini_email"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    if product["type"] == "stock":
        count = await get_stock_count(product_key)
        if count <= 0:
            await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
            return
    msg = await animate_message(call.message, f"{ce('rocket','🚀')} Preparing checkout..." if lang == "en" else f"{ce('rocket','🚀')} جاري تجهيز الدفع...", "checkout")
    text = (
        f"🛒 Checkout\n━━━━━━━━━━━━━━\n\n💰 Price: ${product['usd']} / {product['egp']} EGP\n\nChoose payment method:"
        if lang == "en"
        else f"🛒 إتمام الشراء\n━━━━━━━━━━━━━━\n\n💰 السعر: {product['egp']} جنيه / {product['usd']} USDT\n\nاختار طريقة الدفع:"
    )
    await edit_or_answer(msg, text, reply_markup=payment_buttons(lang, product_key))
    await call.answer()

# ---------------- Wallet / Deposit ----------------
@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(call.from_user.id)
    msg = await animate_message(call.message, f"{ce('wallet','💰')} Syncing Wallet..." if lang == "en" else f"{ce('wallet','💰')} مزامنة المحفظة...", "wallet")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Deposit / إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="🔄 Refresh / تحديث", callback_data="home_wallet")],
        [InlineKeyboardButton(text="⬅️ Main Menu / الرئيسية", callback_data="home_main")],
    ])
    text = (
        f"👛 AIX WALLET\n━━━━━━━━━━━━━━\n\n"
        f"💵 USDT Balance: {balance_usdt} USDT\n"
        f"🇪🇬 EGP Balance: {balance_egp} EGP\n\n"
        f"💳 Deposit funds anytime.\n"
        f"⚠️ Minimum: 5 USDT or 250 EGP"
        if lang == "en"
        else
        f"👛 AIX WALLET\n━━━━━━━━━━━━━━\n\n"
        f"💵 رصيد الدولار: {balance_usdt} USDT\n"
        f"🇪🇬 رصيد المصري: {balance_egp} جنيه\n\n"
        f"💳 تقدر تضيف رصيد في أي وقت.\n"
        f"⚠️ أقل إيداع: 5 USDT أو 250 جنيه"
    )
    await edit_or_answer(msg, text, reply_markup=kb)
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet"]))
async def wallet_message(message: Message):
    await ensure_user(message)
    fake = await message.answer("...")
    class Obj: pass
    # simpler: send new wallet with same function logic
    lang = await get_lang(message.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(message.from_user.id)
    await fake.edit_text("💳 Syncing Wallet...\n\n◉◉◉◉◉ 100%")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Deposit / إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="⬅️ Main Menu / الرئيسية", callback_data="home_main")],
    ])
    text = (
        f"👛 AIX WALLET\n━━━━━━━━━━━━━━\n\n💵 USDT Balance: {balance_usdt} USDT\n🇪🇬 EGP Balance: {balance_egp} EGP"
        if lang == "en" else
        f"👛 AIX WALLET\n━━━━━━━━━━━━━━\n\n💵 رصيد الدولار: {balance_usdt} USDT\n🇪🇬 رصيد المصري: {balance_egp} جنيه"
    )
    await fake.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "home_deposit")
async def deposit_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, f"{ce('wallet','💰')} Opening Deposit Gateway..." if lang == "en" else f"{ce('wallet','💰')} فتح بوابة الإيداع...", "deposit")
    await edit_or_answer(msg, deposit_intro_text(lang), reply_markup=deposit_currency_buttons(lang))
    await call.answer()

@dp.message(F.text.in_(["💳 إيداع", "💳 Deposit"]))
async def deposit_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, f"{ce('wallet','💰')} Opening Deposit Gateway..." if lang == "en" else f"{ce('wallet','💰')} فتح بوابة الإيداع...", "deposit")
    await edit_or_answer(msg, deposit_intro_text(lang), reply_markup=deposit_currency_buttons(lang))

@dp.callback_query(F.data.startswith("deposit_currency_"))
async def deposit_currency_selected(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    currency = call.data.replace("deposit_currency_", "").upper()
    if currency not in ["EGP", "USDT"]:
        await call.answer("Invalid currency", show_alert=True)
        return
    deposit_waiting[call.from_user.id] = currency
    msg = await animate_message(call.message, f"{ce('lightning','⚡')} Preparing amount input..." if lang == "en" else f"{ce('lightning','⚡')} تجهيز إدخال المبلغ...", "deposit")
    if currency == "EGP":
        text = (
            "🇪🇬 EGP Deposit\n━━━━━━━━━━━━━━\n\n"
            "Type the amount you want to add in EGP.\n"
            "Minimum: 250 EGP\n\n"
            "Example: 250 or 500"
            if lang == "en" else
            "🇪🇬 إيداع بالمصري\n━━━━━━━━━━━━━━\n\n"
            "اكتب المبلغ اللي عايز تضيفه بالجنيه.\n"
            "أقل مبلغ: 250 جنيه\n\n"
            "مثال: 250 أو 500"
        )
    else:
        text = (
            f"{ce('binance','🟡')} USDT Deposit\n━━━━━━━━━━━━━━\n\n"
            "Type the amount you want to add in USDT.\n"
            "Minimum: 5 USDT\n\n"
            "Example: 5 or 10"
            if lang == "en" else
            f"{ce('binance','🟡')} إيداع بالدولار USDT\n━━━━━━━━━━━━━━\n\n"
            "اكتب المبلغ اللي عايز تضيفه بالدولار.\n"
            "أقل مبلغ: 5 USDT\n\n"
            "مثال: 5 أو 10"
        )
    await edit_or_answer(msg, text, reply_markup=back_home_keyboard(lang))
    await call.answer()


async def open_products_screen(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, f"{ce('store','🛍')} Loading products..." if lang == "en" else f"{ce('store','🛍')} جاري تحميل المنتجات...", "default")
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

async def open_wallet_screen(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(message.from_user.id)
    msg = await animate_message(message, f"{ce('wallet','💰')} Syncing Wallet..." if lang == "en" else f"{ce('wallet','💰')} مزامنة المحفظة...", "wallet")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Deposit / إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="Refresh / تحديث", callback_data="home_wallet")],
        [InlineKeyboardButton(text="Main Menu / الرئيسية", callback_data="home_main")],
    ])
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"USDT Balance: <b>{balance_usdt}</b> USDT\n"
        f"EGP Balance: <b>{balance_egp}</b> EGP\n\n"
        f"{ce('payment','💳')} Deposit funds anytime.\n"
        f"{ce('lightning','⚡')} Minimum: 5 USDT or 250 EGP"
        if lang == "en" else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"رصيد الدولار: <b>{balance_usdt}</b> USDT\n"
        f"رصيد المصري: <b>{balance_egp}</b> جنيه\n\n"
        f"{ce('payment','💳')} تقدر تضيف رصيد في أي وقت.\n"
        f"{ce('lightning','⚡')} أقل إيداع: 5 USDT أو 250 جنيه"
    )
    await edit_or_answer(msg, text, reply_markup=kb)

async def open_support_screen(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    text = (
        f"{ce('support','🎧')} <b>Support Center</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('telegram','✈️')} {SUPPORT}\n\n"
        f"{ce('success','✅')} Fast response\n"
        f"{ce('verified','✅')} Trusted support"
        if lang == "en" else
        f"{ce('support','🎧')} <b>مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('telegram','✈️')} {SUPPORT}\n\n"
        f"{ce('success','✅')} رد سريع\n"
        f"{ce('verified','✅')} دعم موثوق"
    )
    await message.answer(text, reply_markup=back_home_keyboard(lang), parse_mode="HTML")

async def open_language_screen(message: Message):
    await ensure_user(message)
    await message.answer(f"{ce('language','🌐')} اختر اللغة / Choose language:", reply_markup=language_keyboard(), parse_mode="HTML")

@dp.message(F.text.in_(MENU_TEXTS))
async def route_main_reply_keyboard(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    text_value = (message.text or "").strip()

    if "Product" in text_value or "منتجات" in text_value or text_value == "المنتجات":
        await open_products_screen(message)
    elif "Support" in text_value or "دعم" in text_value or text_value == "الدعم":
        await open_support_screen(message)
    elif "Wallet" in text_value or "محفظ" in text_value or text_value == "المحفظة":
        await open_wallet_screen(message)
    elif "Language" in text_value or "لغة" in text_value or text_value == "اللغة":
        await open_language_screen(message)
    else:
        await send_home(message)

@dp.message(lambda message: message.from_user and message.from_user.id in deposit_waiting)
async def receive_deposit_amount(message: Message):
    await ensure_user(message)
    if not message.text or message.text.startswith("/"):
        return
    lang = await get_lang(message.from_user.id)
    currency = deposit_waiting.get(message.from_user.id)
    try:
        amount = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer("❌ اكتب المبلغ رقم فقط مثل: 250 أو 5")
        return
    if currency == "USDT" and amount < 5:
        await message.answer("❌ أقل إيداع للدولار هو 5 USDT." if lang != "en" else "❌ Minimum USDT deposit is 5 USDT.")
        return
    if currency == "EGP" and amount < 250:
        await message.answer("❌ أقل إيداع بالمصري هو 250 جنيه." if lang != "en" else "❌ Minimum EGP deposit is 250 EGP.")
        return
    deposit_waiting.pop(message.from_user.id, None)
    msg = await animate_message(message, f"{ce('payment','💳')} Loading payment methods..." if lang == "en" else f"{ce('payment','💳')} جاري تجهيز طرق الدفع...", "deposit")
    amount_txt = format_amount(amount)
    if currency == "USDT":
        text = (
            f"💳 Deposit Amount Selected\n━━━━━━━━━━━━━━\n\n"
            f"💰 Amount: {amount_txt} {currency}\n\n"
            f"{ce('binance','🟡')} <b>Binance UID</b>\n"
            f"<code>{BINANCE_UID}</code>\n\n"
            f"Choose payment method below:"
            if lang == "en" else
            f"💳 تم تحديد مبلغ الإيداع\n━━━━━━━━━━━━━━\n\n"
            f"💰 المبلغ: {amount_txt} {currency}\n\n"
            f"{ce('binance','🟡')} <b>بينانس UID</b>\n"
            f"<code>{BINANCE_UID}</code>\n\n"
            f"اختار طريقة الدفع من الأزرار:"
        )
    else:
        text = (
            f"💳 Deposit Amount Selected\n━━━━━━━━━━━━━━\n\n"
            f"💰 Amount: {amount_txt} {currency}\n\n"
            f"{ce('vodafone','🔴')} <b>Vodafone Cash</b>\n"
            f"<code>{VODAFONE_CASH}</code>\n\n"
            f"{ce('instapay','🟣')} <b>InstaPay</b>\n"
            f"<code>{INSTAPAY}</code>\n\n"
            f"Choose payment method below:"
            if lang == "en" else
            f"💳 تم تحديد مبلغ الإيداع\n━━━━━━━━━━━━━━\n\n"
            f"💰 المبلغ: {amount_txt} {currency}\n\n"
            f"{ce('vodafone','🔴')} <b>فودافون كاش</b>\n"
            f"<code>{VODAFONE_CASH}</code>\n\n"
            f"{ce('instapay','🟣')} <b>انستا باي</b>\n"
            f"<code>{INSTAPAY}</code>\n\n"
            f"اختار طريقة الدفع من الأزرار:"
        )
    await edit_or_answer(msg, text, reply_markup=deposit_amount_payment_buttons(lang, amount, currency))

@dp.callback_query(F.data.startswith("topup_"))
async def create_wallet_topup(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    parts = call.data.split("_")
    if len(parts) != 4:
        await call.answer("Error", show_alert=True)
        return
    method = parts[1]
    try:
        amount = float(parts[2])
    except ValueError:
        await call.answer("Invalid amount", show_alert=True)
        return
    currency = parts[3].upper()
    if currency == "USDT" and amount < 5:
        await call.answer("Minimum is 5 USDT", show_alert=True)
        return
    if currency == "EGP" and amount < 250:
        await call.answer("Minimum is 250 EGP", show_alert=True)
        return
    msg = await animate_message(call.message, f"{ce('payment','💳')} Preparing secure payment..." if lang == "en" else f"{ce('payment','💳')} جاري تجهيز بيانات الدفع...", "deposit")
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval(
            """
            INSERT INTO deposits (telegram_id, method, amount, currency, product_key)
            VALUES($1,$2,$3,$4,$5)
            RETURNING id
            """,
            call.from_user.id,
            method,
            amount,
            currency,
            WALLET_DEPOSIT_KEY,
        )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve Deposit", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"💳 Wallet Deposit Request #{dep_id}\nUser: @{call.from_user.username}\nID: {call.from_user.id}\nMethod: {method}\nAmount: {format_amount(amount)} {currency}\n\nبعد التأكد اضغط Approve Deposit.",
        reply_markup=kb,
    )
    if method == "binance":
        pay_text = f"{ce('binance','🟡')} Binance UID Deposit\n━━━━━━━━━━━━━━\n\n🆔 UID:\n<code>{BINANCE_UID}</code>\n\n💰 Amount: {format_amount(amount)} USDT"
    elif method == "vodafone":
        pay_text = f"{ce('vodafone','🔴')} Vodafone Cash Deposit\n━━━━━━━━━━━━━━\n\n📱 Number:\n<code>{VODAFONE_CASH}</code>\n\n💰 Amount: {format_amount(amount)} EGP"
    else:
        pay_text = f"{ce('instapay','🟣')} InstaPay Deposit\n━━━━━━━━━━━━━━\n\n🏦 InstaPay:\n<code>{INSTAPAY}</code>\n\n💰 Amount: {format_amount(amount)} EGP"
    await edit_or_answer(msg, f"{pay_text}\n\n📸 بعد الدفع ابعت صورة إثبات الدفع هنا.\n🧾 Deposit ID: #{dep_id}")
    await call.answer()

# ---------------- Payment / Orders ----------------
@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")
    method = parts[1]
    product_key = "_".join(parts[2:])
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    msg = await animate_message(call.message, f"{ce('payment','💳')} Securing payment details..." if lang == "en" else f"{ce('payment','💳')} جاري تجهيز بيانات الدفع...", "deposit")
    currency = "USDT" if method == "binance" else "EGP"
    amount = product["usd"] if method == "binance" else product["egp"]
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval(
            """
            INSERT INTO deposits (telegram_id, method, amount, currency, product_key)
            VALUES($1,$2,$3,$4,$5)
            RETURNING id
            """,
            call.from_user.id,
            method,
            amount,
            currency,
            product_key,
        )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"🛒 New Order #{dep_id}\nUser: @{call.from_user.username}\nID: {call.from_user.id}\nProduct: {product['title_en']}\nMethod: {method}\nAmount: {amount} {currency}",
        reply_markup=kb,
    )
    if method == "binance":
        pay_text = f"{ce('binance','🟡')} Binance UID:\n<code>{BINANCE_UID}</code>\n\n💰 Amount: {amount} USDT"
    elif method == "vodafone":
        pay_text = f"{ce('vodafone','🔴')} Vodafone Cash:\n<code>{VODAFONE_CASH}</code>\n\n💰 Amount: {amount} EGP"
    else:
        pay_text = f"{ce('instapay','🟣')} InstaPay:\n<code>{INSTAPAY}</code>\n\n💰 Amount: {amount} EGP"
    await edit_or_answer(msg, f"{pay_text}\n\n📸 بعد الدفع ابعت صورة إثبات الدفع هنا.\n🧾 Order ID: #{dep_id}")
    await call.answer()

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if not dep or dep["status"] != "pending":
            await call.answer("Already handled")
            return
        product_key = dep["product_key"]
        if product_key == WALLET_DEPOSIT_KEY:
            if str(dep["currency"]).upper() == "USDT":
                await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", dep["amount"], dep["telegram_id"])
            else:
                await conn.execute("UPDATE users SET balance_egp = balance_egp + $1 WHERE telegram_id=$2", dep["amount"], dep["telegram_id"])
            await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], f"✅ تم قبول الإيداع وإضافة الرصيد\n━━━━━━━━━━━━━━\n\n💰 Amount: {dep['amount']} {dep['currency']}\n\nشكراً لثقتك ❤️")
            await call.message.edit_text(f"✅ Wallet Deposit #{dep_id} Approved")
            await call.answer()
            return
        product = PRODUCTS[product_key]
        if product["type"] == "activation":
            if product_key == "chatgpt_email":
                activation_text = (
                    f"✅ تم تأكيد الدفع بنجاح\n━━━━━━━━━━━━━━\n\n"
                    f"✨ تفعيل ChatGPT Plus على إيميلك الشخصي\n\n"
                    f"يرجى التواصل مع الأدمن لإتمام التفعيل:\n{SUPPORT}\n\n"
                    f"شكراً لثقتك ❤️"
                )
            else:
                activation_text = (
                    f"✅ تم تأكيد الدفع بنجاح\n━━━━━━━━━━━━━━\n\n"
                    f"📧 تفعيل Gemini Pro على إيميلك الشخصي\n\n"
                    f"يرجى التواصل مع الأدمن لإتمام التفعيل:\n{SUPPORT}\n\n"
                    f"شكراً لثقتك ❤️"
                )
            await bot.send_message(dep["telegram_id"], activation_text)
        else:
            item = await conn.fetchrow(
                """
                SELECT id, item_data FROM stock
                WHERE product=$1 AND sold=false
                ORDER BY id ASC
                LIMIT 1
                """,
                product["stock_name"],
            )
            if not item:
                await call.message.edit_text("❌ لا يوجد مخزون متاح حاليًا")
                await bot.send_message(dep["telegram_id"], "❌ لا يوجد مخزون حاليًا. تواصل مع الدعم.")
                return
            await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
            remaining = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", product["stock_name"])
            await bot.send_message(dep["telegram_id"], f"✅ تم تأكيد الدفع\n━━━━━━━━━━━━━━\n\n📦 بيانات الحساب:\n\n{item['item_data']}\n\nشكراً لشرائك ❤️")
            if remaining == 0:
                await bot.send_message(ADMIN_ID, f"🚨 OUT OF STOCK\n\nProduct: {product['stock_name']}")
            elif remaining <= 3:
                await bot.send_message(ADMIN_ID, f"⚠️ Low Stock Alert\n\nProduct: {product['stock_name']}\nRemaining: {remaining}")
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
    await call.message.edit_text(f"✅ Order #{dep_id} Approved")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], "❌ تم رفض الطلب. تواصل مع الدعم.")
    await call.message.edit_text(f"❌ Order #{dep_id} Rejected")
    await call.answer()

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer("📤 تم إرسال الإثبات للمراجعة.")

# ---------------- Support / Admin commands ----------------
@dp.callback_query(F.data == "home_support")
async def support_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, f"{ce('support','🎧')} Opening Support..." if lang == "en" else f"{ce('support','🎧')} فتح الدعم...", "default")
    text = (
        f"{ce('support','🎧')} <b>Support Center</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}\n\n{ce('success','✅')} Fast response\n{ce('verified','✅')} Trusted support"
        if lang == "en" else
        f"{ce('support','🎧')} <b>مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}\n\n{ce('success','✅')} رد سريع\n{ce('verified','✅')} دعم موثوق"
    )
    await edit_or_answer(msg, text, reply_markup=back_home_keyboard(lang))
    await call.answer()

@dp.message(F.text.in_(["💬 الدعم", "💬 Support"]))
async def support_message(message: Message):
    await message.answer(f"{ce('support','🎧')} {ce('telegram','✈️')} {SUPPORT}", parse_mode="HTML")

async def broadcast_stock_added(product_key: str, quantity: int, total: int):
    # إشعار تلقائي لكل المستخدمين عند إضافة مخزون جديد للحسابات الجاهزة
    product = PRODUCTS[product_key]

    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id, lang FROM users")

    if product_key == "chatgpt":
        product_name = "ChatGPT Plus — Ready Accounts"
        product_icon = ce("chatgpt", "🤖")
    elif product_key == "gemini_ready":
        product_name = "Gemini Pro — Ready Accounts"
        product_icon = ce("gemini", "🟢")
    else:
        product_name = product["title_en"]
        product_icon = ce("store", "🛍")

    for user in users:
        lang = user["lang"] or "ar"

        if lang == "en":
            text = (
                f"{ce('fire','🔥')} <b>New stock available now!</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"{product_icon} <b>{product_name}</b>\n"
                f"{ce('stock_add','+')} Added: <b>{quantity}</b>\n"
                f"{ce('stock','📦')} Current stock: <b>{total}</b>\n\n"
                f"{ce('lightning','⚡')} Limited quantity — order now before it runs out!"
            )
            btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Buy now", callback_data="refresh_products")]
            ])
        else:
            text = (
                f"{ce('fire','🔥')} <b>وصل مخزون جديد الآن!</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"{product_icon} <b>{product_name}</b>\n"
                f"{ce('stock_add','+')} تمت إضافة: <b>{quantity}</b>\n"
                f"{ce('stock','📦')} المخزون الحالي: <b>{total}</b>\n\n"
                f"{ce('lightning','⚡')} الكمية محدودة — اطلب الآن قبل النفاد!"
            )
            btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="اطلب الآن", callback_data="refresh_products")]
            ])

        try:
            await bot.send_message(user["telegram_id"], text, reply_markup=btn, parse_mode="HTML")
        except Exception:
            pass

@dp.message(Command("getemoji"))
async def get_emoji_id(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    target = message.reply_to_message
    if not target:
        await message.answer(
            "اعمل Reply على رسالة فيها الإيموجي المتحرك واكتب:\n\n/getemoji\n\n"
            "Send or forward the animated/custom emoji, reply to it, then type /getemoji"
        )
        return

    entities = []
    if target.entities:
        entities.extend(target.entities)
    if target.caption_entities:
        entities.extend(target.caption_entities)

    result = []
    for entity in entities:
        if entity.type == "custom_emoji" and entity.custom_emoji_id:
            emoji_text = ""
            try:
                source_text = target.text or target.caption or ""
                emoji_text = source_text[entity.offset: entity.offset + entity.length]
            except Exception:
                emoji_text = ""
            result.append(
                f"{emoji_text} Emoji ID:\n<code>{entity.custom_emoji_id}</code>"
            )

    if not result:
        await message.answer(
            "❌ مفيش Custom Emoji في الرسالة دي.\n\n"
            "لازم تبعت إيموجي بريميوم/متحرك من تليجرام، وبعدين تعمل Reply عليه وتكتب /getemoji"
        )
        return

    await message.answer(
        "✅ Custom Emoji IDs Found:\n\n" + "\n\n".join(result),
        parse_mode="HTML"
    )

@dp.message(Command("emojihelp"))
async def emoji_help(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "طريقة استخراج ID الإيموجي المتحرك:\n\n"
        "1) ابعت الإيموجي المتحرك في شات البوت.\n"
        "2) اعمل Reply على رسالة الإيموجي.\n"
        "3) اكتب /getemoji\n\n"
        "بعدها ابعتلي الـ IDs وأنا أبدّل كل إيموجي عادي في البوت بإيموجي متحرك."
    )

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    chatgpt = await get_stock_count("chatgpt")
    gemini = await get_stock_count("gemini_ready")
    await message.answer(
        f"📦 Stock Report\n\n🤖 ChatGPT Plus Ready Account Stock: {chatgpt}\n💎 Gemini Pro Ready Account Stock: {gemini}\n\n"
        f"/liststock chatgpt\n/liststock gemini\n/delstock chatgpt ID\n/delstock gemini ID\n/clearstock chatgpt\n/clearstock gemini"
    )

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/addstock", "").strip()
    if not text:
        await message.answer("📦 إضافة استوك:\n\n/addstock chatgpt\nemail1:pass1\nemail2:pass2\n\n/addstock gemini\nemail1:pass1\nemail2:pass2")
        return
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    product_key, stock_name = resolve_stock_product(lines[0])
    if not product_key:
        await message.answer("❌ نوع المنتج غير صحيح. استخدم chatgpt أو gemini")
        return
    items = lines[1:]
    if not items:
        await message.answer("❌ اكتب الحسابات تحت اسم المنتج، كل حساب في سطر.")
        return
    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    label = product_label(product_key)
    await message.answer(f"✅ تم إضافة {len(items)} حساب إلى {label}\n📦 المخزون الحالي: {total}")
    await bot.send_message(ADMIN_ID, f"📦 Stock Added\n\nProduct: {label}\nQuantity Added: {len(items)}\nCurrent Stock: {total}")
    await broadcast_stock_added(product_key, len(items), total)

@dp.message(Command("liststock"))
async def list_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("استخدم:\n/liststock chatgpt\n/liststock gemini")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer("❌ استخدم chatgpt أو gemini")
        return
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT 50", stock_name)
    label = product_label(product_key)
    if not rows:
        await message.answer(f"📭 لا يوجد استوك متاح في {label}")
        return
    lines = [f"📦 {label} Stock", "━━━━━━━━━━━━━━"]
    for row in rows:
        item = row["item_data"]
        if len(item) > 80:
            item = item[:80] + "..."
        lines.append(f"ID {row['id']} - {item}")
    await message.answer("\n".join(lines))

@dp.message(Command("delstock"))
async def delete_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("استخدم:\n/delstock chatgpt 5\n/delstock gemini 7")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer("❌ استخدم chatgpt أو gemini")
        return
    try:
        item_id = int(parts[2])
    except ValueError:
        await message.answer("❌ رقم ID غير صحيح")
        return
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM stock WHERE id=$1 AND product=$2 AND sold=false", item_id, stock_name)
        if not row:
            await message.answer("❌ العنصر غير موجود أو مباع بالفعل")
            return
        await conn.execute("DELETE FROM stock WHERE id=$1", item_id)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"🗑 تم حذف العنصر ID {item_id} من {product_label(product_key)}\n📦 المتبقي: {total}")

@dp.message(Command("clearstock"))
async def clear_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("استخدم:\n/clearstock chatgpt\n/clearstock gemini")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer("❌ استخدم chatgpt أو gemini")
        return
    async with db_pool.acquire() as conn:
        deleted = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
        await conn.execute("DELETE FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"🗑 تم مسح {deleted} عنصر من استوك {product_label(product_key)}")

@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("استخدم:\n/broadcast رسالتك")
        return
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id FROM users")
    sent = 0
    for user in users:
        try:
            await bot.send_message(user["telegram_id"], f"{ce('announcement','📢')} إشعار من {BOT_NAME}\n\n{esc(text)}", parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ تم الإرسال إلى {sent} مستخدم")

@dp.message(Command("broadcastphoto"))
async def broadcast_photo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer("اعمل Reply على الصورة واكتب /broadcastphoto")
        return
    photo = message.reply_to_message.photo[-1].file_id
    caption = message.reply_to_message.caption or ""
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id FROM users")
    sent = 0
    for user in users:
        try:
            await bot.send_photo(user["telegram_id"], photo, caption=caption)
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ تم إرسال الصورة إلى {sent} مستخدم")

async def setup_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Start and open the menu"),
        BotCommand(command="menu", description="Open the main menu"),
        BotCommand(command="products", description="Show products"),
        BotCommand(command="wallet", description="Open wallet"),
        BotCommand(command="support", description="Open support"),
        BotCommand(command="language", description="Change language"),
    ])

async def main():
    await init_db()
    await setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
