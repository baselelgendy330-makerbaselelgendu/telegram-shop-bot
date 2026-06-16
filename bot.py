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
    "loading": "6089327236958132324",     # إيموجي التحميل
    "num1": "5197397670724912036",        # رقم 1
    "num2": "5197250993296785376",        # رقم 2
    "num3": "5195203805725084605",        # رقم 3
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
    text = f"{ce('loading', '⏳')} <b>Loading...</b>" if lang == "en" else f"{ce('loading', '⏳')} <b>جاري التحميل...</b>"
    msg = None
    try:
        if getattr(message, "from_user", None) and message.from_user.is_bot:
            msg = await message.edit_text(text, parse_mode="HTML")
        else:
            msg = await message.answer(text, parse_mode="HTML")
    except Exception:
        msg = await message.answer(text, parse_mode="HTML")
    
    await asyncio.sleep(0.3)
    return msg or message

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
            [InlineKeyboardButton(text=f"CDK Activation Chatgpt 1Y | $9 | Stock {counts['cdk_chatgpt']}", callback_data="product_cdk_chatgpt")],
            [InlineKeyboardButton(text="Refresh", callback_data="refresh_products"), InlineKeyboardButton(text="Back", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"CDK Activation Chatgpt 1Y | 9$ | المتاح {counts['cdk_chatgpt']}", callback_data="product_cdk_chatgpt")],
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
            [InlineKeyboardButton(text="Back", callback_data=f"product_{product_key}")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="رجوع", callback_data=f"product_{product_key}")],
    ])

def deposit_currency_buttons(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="USDT Deposit", callback_data="deposit_currency_USDT")],
            [InlineKeyboardButton(text="Back", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إيداع بالدولار USDT", callback_data="deposit_currency_USDT")],
        [InlineKeyboardButton(text="رجوع", callback_data="home_main")],
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str):
    amount_txt = format_amount(amount)
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🟡 Binance UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
            [InlineKeyboardButton(text="Change Amount", callback_data="deposit_currency_USDT")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🟡 بينانس UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
        [InlineKeyboardButton(text="تغيير المبلغ", callback_data="deposit_currency_USDT")],
    ])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])

def wallet_kb(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Deposit", callback_data="home_deposit")],
            [InlineKeyboardButton(text="Refresh", callback_data="home_wallet")],
            [InlineKeyboardButton(text="Main Menu", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="تحديث", callback_data="home_wallet")],
        [InlineKeyboardButton(text="الرئيسية", callback_data="home_main")],
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
        f"{ce('support','🎧')} <b>الدعم</b> — مساعدة في أي وقت\n\n"
        f"{ce('lightning','⚡')} تفعيل سريع • دفع آمن • خدمة موثوقة"
    )

def product_list_text(lang: str):
    if lang == "en":
        return (
            f"{ce('store','🛍')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            f"{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\n"
            f"Price: $9 | Subscription: 1 Year, no warranty {ce('error','❌')}\n\n"
            f"{ce('arrows_down','⬇️')} Choose a product below:"
        )
    return (
        f"{ce('store','🛍')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\n"
        f"السعر: 9$ | الاشتراك سنه ، no warranty {ce('error','❌')}\n\n"
        f"{ce('arrows_down','⬇️')} اختار المنتج من الأزرار:"
    )

def deposit_intro_text(lang: str):
    if lang == "en":
        return (
            f"{ce('wallet','💰')} <b>Deposit Balance</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            f"Choose the currency you want to deposit.\n\n"
            f"USDT: minimum 5 USDT"
        )
    return (
        f"{ce('wallet','💰')} <b>إيداع رصيد</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"اختار العملة اللي عايز تعمل بيها إيداع.\n\n"
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
    msg = await animate_message(message, lang)
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

@dp.message(Command("wallet"))
async def wallet_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    balance_usdt = await get_wallet_balance(message.from_user.id)
    msg = await animate_message(message, lang)
    kb = wallet_kb(lang)
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\nUSDT Balance: {balance_usdt} USDT"
        if lang == "en" else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\nرصيد الدولار: {balance_usdt} USDT"
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
    msg = await animate_message(call.message, lang)
    await edit_or_answer(msg, home_text(lang, name), reply_markup=home_keyboard(lang))
    await call.answer()

@dp.callback_query(F.data == "home_language")
async def home_language(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    text = f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:"
    await call.message.answer(text, reply_markup=language_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.message(Command("language"))
async def language_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    text = f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:"
    await message.answer(text, reply_markup=language_keyboard(), parse_mode="HTML")

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
    msg = await animate_message(call.message, lang)
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer()

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, lang)
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer("Updated ✅" if lang == "en" else "تم التحديث ✅")

@dp.callback_query(F.data == "product_cdk_chatgpt")
async def product_cdk_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await animate_message(call.message, lang)
    count = await get_stock_count("cdk_chatgpt")
    
    caption = (
        f"{ce('chatgpt','🤖')} <b>CDK Activation Chatgpt For 1 year</b>\n━━━━━━━━━━━━━━\n\n"
        f"{ce('wallet','💰')} Price: $9\n"
        f"{ce('stock','📦')} Stock: {count}\n"
        f"{ce('shield','🛡')} Subscription: 1 Year, no warranty {ce('error','❌')}\n\n"
        f"{ce('fire','🔥')} <b>K-12 Offer Activation for your personal account!</b>\n\n"
        f"{ce('link','🔗')} <b>Redemption Link:</b> http://gpt.ddfafa.com\n\n"
        f"{ce('bell','🔔')} <b>How to activate:</b>\n"
        f"{ce('num1','1️⃣')} Put the CDK code in the first field.\n"
        f"{ce('num2','2️⃣')} Click 'Open AuthSession Page', copy the full Access Token, and paste it in the second field.\n"
        f"{ce('num3','3️⃣')} Click 'Activate Now' and you are done!\n\n"
        f"{ce('lightning','⚡')} Instant delivery after payment."
        if lang == "en"
        else
        f"{ce('chatgpt','🤖')} <b>CDK Activation Chatgpt For 1 year</b>\n━━━━━━━━━━━━━━\n\n"
        f"{ce('wallet','💰')} السعر: 9$\n"
        f"{ce('stock','📦')} المتوفر: {count}\n"
        f"{ce('shield','🛡')} الاشتراك سنه ، no warranty {ce('error','❌')}\n\n"
        f"{ce('fire','🔥')} <b>تفعيل عرض K-12 على حسابك الشخصي!</b>\n\n"
        f"{ce('link','🔗')} <b>موقع التفعيل:</b> http://gpt.ddfafa.com\n\n"
        f"{ce('bell','🔔')} <b>طريقة التفعيل:</b>\n"
        f"{ce('num1','1️⃣')} حط الكود (CDK) في الخانة الأولى.\n"
        f"{ce('num2','2️⃣')} افتح 'Open AuthSession Page'، انسخ الاكسيس توكن بالكامل، واللصقه في الخانة التانية.\n"
        f"{ce('num3','3️⃣')} دوس 'Activate Now' وبس كدا!\n\n"
        f"{ce('lightning','⚡')} تسليم فوري للكود بعد الدفع."
    )
    
    try:
        await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")
    except Exception:
        await call.message.answer(caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")
        
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
    msg = await animate_message(call.message, lang)
    text = (
        f"{ce('payment','💳')} Checkout\n━━━━━━━━━━━━━━\n\n💰 Price: ${product['usd']}\n\n{ce('arrows_down','⬇️')} Choose payment method:"
        if lang == "en"
        else f"{ce('payment','💳')} إتمام الشراء\n━━━━━━━━━━━━━━\n\n💰 السعر: {product['usd']}$\n\n{ce('arrows_down','⬇️')} اختار طريقة الدفع:"
    )
    await edit_or_answer(msg, text, reply_markup=payment_buttons(lang, product_key))
    await call.answer()

# ---------------- Wallet / Deposit ----------------
@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    balance_usdt = await get_wallet_balance(call.from_user.id)
    msg = await animate_message(call.message, lang)
    kb = wallet_kb(lang)
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n"
        f"💵 USDT Balance: {balance_usdt} USDT\n\n"
        f"{ce('payment','💳')} Deposit funds anytime.\n"
        f"⚠️ Minimum: 5 USDT"
        if lang == "en"
        else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n"
        f"💵 رصيد الدولار: {balance_usdt} USDT\n\n"
        f"{ce('payment','💳')} تقدر تضيف رصيد في أي وقت.\n"
        f"⚠️ أقل إيداع: 5 USDT"
    )
    await edit_or_answer(msg, text, reply_markup=kb)
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet", "💰 المحفظة", "💰 Wallet"]))
async def wallet_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, lang)
    balance_usdt = await get_wallet_balance(message.from_user.id)
    kb = wallet_kb(lang)
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 USDT Balance: {balance_usdt} USDT"
        if lang == "en" else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 رصيد الدولار: {balance_usdt} USDT"
    )
    await safe_edit_or_answer(msg, text, reply_markup=kb)

@dp.callback_query(F.data == "home_deposit")
async def deposit_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
    await edit_or_answer(msg, deposit_intro_text(lang), reply_markup=deposit_currency_buttons(lang))
    await call.answer()

@dp.message(F.text.in_(["💳 إيداع", "💳 Deposit"]))
async def deposit_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, lang)
    await edit_or_answer(msg, deposit_intro_text(lang), reply_markup=deposit_currency_buttons(lang))

@dp.callback_query(F.data.startswith("deposit_currency_"))
async def deposit_currency_selected(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    currency = call.data.replace("deposit_currency_", "").upper()
    if currency != "USDT":
        await call.answer("Invalid currency" if lang == "en" else "عملة غير صحيحة", show_alert=True)
        return
    deposit_waiting[call.from_user.id] = currency
    msg = await animate_message(call.message, lang)
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
    msg = await animate_message(message, lang)
    counts = await product_counts()
    await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))

async def open_wallet_screen(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    balance_usdt = await get_wallet_balance(message.from_user.id)
    msg = await animate_message(message, lang)
    kb = wallet_kb(lang)
    text = (
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"USDT Balance: <b>{balance_usdt}</b> USDT\n\n"
        f"{ce('payment','💳')} Deposit funds anytime.\n"
        f"{ce('lightning','⚡')} Minimum: 5 USDT"
        if lang == "en" else
        f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"رصيد الدولار: <b>{balance_usdt}</b> USDT\n\n"
        f"{ce('payment','💳')} تقدر تضيف رصيد في أي وقت.\n"
        f"{ce('lightning','⚡')} أقل إيداع: 5 USDT"
    )
    await safe_edit_or_answer(msg, text, reply_markup=kb)

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
    lang = await get_lang(message.from_user.id)
    text = f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:"
    await message.answer(text, reply_markup=language_keyboard(), parse_mode="HTML")

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
        await message.answer(f"{ce('error','❌')} Please write numbers only like: 5 or 10" if lang == "en" else f"{ce('error','❌')} اكتب المبلغ رقم فقط مثل: 5 أو 10")
        return
    if currency == "USDT" and amount < 5:
        await message.answer(f"{ce('error','❌')} Minimum USDT deposit is 5 USDT." if lang == "en" else f"{ce('error','❌')} أقل إيداع للدولار هو 5 USDT.")
        return
    deposit_waiting.pop(message.from_user.id, None)
    msg = await animate_message(message, lang)
    amount_txt = format_amount(amount)
    
    text = (
        f"{ce('payment','💳')} Deposit Amount Selected\n━━━━━━━━━━━━━━\n\n"
        f"💰 Amount: {amount_txt} {currency}\n\n"
        f"{ce('binance','🟡')} <b>Binance UID</b>\n"
        f"<code>{BINANCE_UID}</code>\n\n"
        f"{ce('arrows_down','⬇️')} Choose payment method below:"
        if lang == "en" else
        f"{ce('payment','💳')} تم تحديد مبلغ الإيداع\n━━━━━━━━━━━━━━\n\n"
        f"💰 المبلغ: {amount_txt} {currency}\n\n"
        f"{ce('binance','🟡')} <b>بينانس UID</b>\n"
        f"<code>{BINANCE_UID}</code>\n\n"
        f"{ce('arrows_down','⬇️')} اختار طريقة الدفع من الأزرار:"
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
        await call.answer("Invalid amount" if lang == "en" else "مبلغ غير صحيح", show_alert=True)
        return
    currency = parts[3].upper()
    if currency == "USDT" and amount < 5:
        await call.answer("Minimum is 5 USDT" if lang == "en" else "أقل مبلغ هو 5 USDT", show_alert=True)
        return
        
    msg = await animate_message(call.message, lang)
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
    
    if lang == "en":
        pay_text = f"{ce('binance','🟡')} Binance UID Deposit\n━━━━━━━━━━━━━━\n\n🆔 UID:\n<code>{BINANCE_UID}</code>\n\n💰 Amount: {format_amount(amount)} USDT"
        proof_text = "📸 After payment, please send the payment proof screenshot here."
        dep_id_text = f"🧾 Deposit ID: #{dep_id}"
    else:
        pay_text = f"{ce('binance','🟡')} إيداع بينانس UID\n━━━━━━━━━━━━━━\n\n🆔 UID:\n<code>{BINANCE_UID}</code>\n\n💰 المبلغ: {format_amount(amount)} USDT"
        proof_text = "📸 بعد الدفع ابعت صورة إثبات الدفع هنا."
        dep_id_text = f"🧾 رقم الإيداع: #{dep_id}"

    await edit_or_answer(msg, f"{pay_text}\n\n{proof_text}\n{dep_id_text}")
    await call.answer()

# ---------------- Payment / Orders ----------------
@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")
    method = parts[1]
    product_key = "_".join(parts[2:])
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    msg = await animate_message(call.message, lang)
    currency = "USDT"
    amount = product["usd"]
    
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
    
    if lang == "en":
        pay_text = f"{ce('binance','🟡')} Binance UID:\n<code>{BINANCE_UID}</code>\n\n💰 Amount: {amount} USDT"
        proof_text = "📸 After payment, please send the payment proof screenshot here."
        order_id_text = f"🧾 Order ID: #{dep_id}"
    else:
        pay_text = f"{ce('binance','🟡')} بينانس UID:\n<code>{BINANCE_UID}</code>\n\n💰 المبلغ: {amount} USDT"
        proof_text = "📸 بعد الدفع ابعت صورة إثبات الدفع هنا."
        order_id_text = f"🧾 رقم الطلب: #{dep_id}"

    await edit_or_answer(msg, f"{pay_text}\n\n{proof_text}\n{order_id_text}")
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
        
        user_lang = await get_lang(dep["telegram_id"])
        product_key = dep["product_key"]
        if product_key == WALLET_DEPOSIT_KEY:
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", dep["amount"], dep["telegram_id"])
            await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
            
            success_text = f"{ce('success','✅')} Deposit approved and balance added\n━━━━━━━━━━━━━━\n\n💰 Amount: {dep['amount']} {dep['currency']}\n\nThank you for trusting us ❤️" if user_lang == "en" else f"{ce('success','✅')} تم قبول الإيداع وإضافة الرصيد\n━━━━━━━━━━━━━━\n\n💰 المبلغ: {dep['amount']} {dep['currency']}\n\nشكراً لثقتك ❤️"
            await bot.send_message(dep["telegram_id"], success_text)
            await call.message.edit_text(f"{ce('success','✅')} Wallet Deposit #{dep_id} Approved")
            await call.answer()
            return
            
        product = PRODUCTS[product_key]
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
            await call.message.edit_text(f"{ce('error','❌')} لا يوجد مخزون متاح حاليًا")
            no_stock_text = f"{ce('error','❌')} No stock available right now. Contact support." if user_lang == "en" else f"{ce('error','❌')} لا يوجد مخزون حاليًا. تواصل مع الدعم."
            await bot.send_message(dep["telegram_id"], no_stock_text)
            return
        await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
        remaining = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", product["stock_name"])
        
        deliver_text = f"{ce('success','✅')} Payment Confirmed\n━━━━━━━━━━━━━━\n\n📦 Your CDK Code:\n\n<code>{item['item_data']}</code>\n\n{ce('link','🔗')} Redemption Link: http://gpt.ddfafa.com\n\nThank you for your purchase ❤️" if user_lang == "en" else f"{ce('success','✅')} تم تأكيد الدفع\n━━━━━━━━━━━━━━\n\n📦 الكود الخاص بك (CDK):\n\n<code>{item['item_data']}</code>\n\n{ce('link','🔗')} رابط التفعيل: http://gpt.ddfafa.com\n\nشكراً لشرائك ❤️"
        await bot.send_message(dep["telegram_id"], deliver_text)
        
        if remaining == 0:
            await bot.send_message(ADMIN_ID, f"🚨 OUT OF STOCK\n\nProduct: {product['stock_name']}")
        elif remaining <= 3:
            await bot.send_message(ADMIN_ID, f"⚠️ Low Stock Alert\n\nProduct: {product['stock_name']}\nRemaining: {remaining}")
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
    await call.message.edit_text(f"{ce('success','✅')} Order #{dep_id} Approved")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            user_lang = await get_lang(dep["telegram_id"])
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)
            reject_text = f"{ce('error','❌')} Order rejected. Contact support." if user_lang == "en" else f"{ce('error','❌')} تم رفض الطلب. تواصل مع الدعم."
            await bot.send_message(dep["telegram_id"], reject_text)
    await call.message.edit_text(f"{ce('error','❌')} Order #{dep_id} Rejected")
    await call.answer()

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    lang = await get_lang(message.from_user.id)
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    success_text = "📤 Payment proof sent for review." if lang == "en" else "📤 تم إرسال الإثبات للمراجعة."
    await message.answer(success_text)

# ---------------- Support / Admin commands ----------------
@dp.callback_query(F.data == "home_support")
async def support_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
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
    product = PRODUCTS[product_key]

    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id, lang FROM users")

    product_name = product["title_en"]
    product_icon = ce("chatgpt", "🤖")

    for user in users:
        lang = user["lang"] or "ar"

        if lang == "en":
            text = (
                f"{ce('fire','🔥')} <b>New CDK stock available now!</b>\n"
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
                f"{ce('fire','🔥')} <b>وصل مخزون جديد من أكواد التفعيل!</b>\n"
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
            f"{ce('error','❌')} مفيش Custom Emoji في الرسالة دي.\n\n"
            "لازم تبعت إيموجي بريميوم/متحرك من تليجرام، وبعدين تعمل Reply عليه وتكتب /getemoji"
        )
        return

    await message.answer(
        f"{ce('success','✅')} Custom Emoji IDs Found:\n\n" + "\n\n".join(result),
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
    cdk = await get_stock_count("cdk_chatgpt")
    await message.answer(
        f"{ce('stock','📦')} Stock Report\n\n{ce('chatgpt','🤖')} CDK Activation Chatgpt Stock: {cdk}\n\n"
        f"/liststock cdk\n/delstock cdk ID\n/clearstock cdk"
    )

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/addstock", "").strip()
    if not text:
        await message.answer(f"{ce('stock_add','➕')} إضافة استوك لكود التفعيل:\n\n/addstock cdk\nCODE1\nCODE2\nCODE3")
        return
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    product_key, stock_name = resolve_stock_product(lines[0])
    if not product_key:
        await message.answer(f"{ce('error','❌')} نوع المنتج غير صحيح. استخدم cdk")
        return
    items = lines[1:]
    if not items:
        await message.answer(f"{ce('error','❌')} اكتب الأكواد تحت اسم المنتج، كل كود في سطر.")
        return
    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    label = product_label(product_key)
    await message.answer(f"{ce('success','✅')} تم إضافة {len(items)} كود إلى {label}\n{ce('stock','📦')} المخزون الحالي: {total}")
    await bot.send_message(ADMIN_ID, f"{ce('stock','📦')} Stock Added\n\nProduct: {label}\nQuantity Added: {len(items)}\nCurrent Stock: {total}")
    await broadcast_stock_added(product_key, len(items), total)

@dp.message(Command("liststock"))
async def list_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("استخدم:\n/liststock cdk")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer(f"{ce('error','❌')} استخدم cdk")
        return
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT 50", stock_name)
    label = product_label(product_key)
    if not rows:
        await message.answer(f"📭 لا يوجد استوك متاح في {label}")
        return
    lines = [f"{ce('stock','📦')} {label} Stock", "━━━━━━━━━━━━━━"]
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
        await message.answer("استخدم:\n/delstock cdk 5")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer(f"{ce('error','❌')} استخدم cdk")
        return
    try:
        item_id = int(parts[2])
    except ValueError:
        await message.answer(f"{ce('error','❌')} رقم ID غير صحيح")
        return
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM stock WHERE id=$1 AND product=$2 AND sold=false", item_id, stock_name)
        if not row:
            await message.answer(f"{ce('error','❌')} العنصر غير موجود أو مباع بالفعل")
            return
        await conn.execute("DELETE FROM stock WHERE id=$1", item_id)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"{ce('trash','🗑')} تم حذف العنصر ID {item_id} من {product_label(product_key)}\n{ce('stock','📦')} المتبقي: {total}")

@dp.message(Command("clearstock"))
async def clear_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("استخدم:\n/clearstock cdk")
        return
    product_key, stock_name = resolve_stock_product(parts[1])
    if not product_key:
        await message.answer(f"{ce('error','❌')} استخدم cdk")
        return
    async with db_pool.acquire() as conn:
        deleted = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
        await conn.execute("DELETE FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"{ce('trash','🗑')} تم مسح {deleted} كود من استوك {product_label(product_key)}")

@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer(f"استخدم:\n/broadcast رسالتك")
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
    await message.answer(f"{ce('success','✅')} تم الإرسال إلى {sent} مستخدم")

@dp.message(Command("broadcastphoto"))
async def broadcast_photo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer(f"اعمل Reply على الصورة واكتب /broadcastphoto")
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
    await message.answer(f"{ce('success','✅')} تم إرسال الصورة إلى {sent} مستخدم")

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
