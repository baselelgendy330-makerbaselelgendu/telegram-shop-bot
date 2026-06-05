import asyncio
import os
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    URLInputFile,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
VODAFONE_CASH = "01063467929"
INSTAPAY = "mahmoud2662000"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

CHATGPT_IMAGE = "https://i.postimg.cc/g0GQwy2V/f413a409aabc9c298e8b6b461affaa99.jpg"
GEMINI_IMAGE = "https://i.postimg.cc/0Qfr71mh/images-(1).jpg"

CHATGPT_PRODUCT = "ChatGPT Plus"
GEMINI_READY_PRODUCT = "Gemini Ready"
GEMINI_EMAIL_PRODUCT = "Gemini Email Activation"
WALLET_DEPOSIT_KEY = "wallet_deposit"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

# users waiting to type a wallet deposit amount
deposit_waiting = {}

menu_ar = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 المنتجات"), KeyboardButton(text="💬 الدعم")],
        [KeyboardButton(text="👛 المحفظة"), KeyboardButton(text="💳 إيداع")],
        [KeyboardButton(text="🌐 اللغة")],
    ],
    resize_keyboard=True,
)

menu_en = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="💬 Support")],
        [KeyboardButton(text="👛 Wallet"), KeyboardButton(text="💳 Deposit")],
        [KeyboardButton(text="🌐 Language")],
    ],
    resize_keyboard=True,
)

PRODUCTS = {
    "chatgpt": {
        "stock_name": CHATGPT_PRODUCT,
        "title_en": "ChatGPT Plus 1M",
        "title_ar": "ChatGPT Plus 1M",
        "image": CHATGPT_IMAGE,
        "usd": 5,
        "egp": 250,
        "type": "stock",
        "warranty_ar": "15 يوم",
        "warranty_en": "15 days",
    },
    "gemini_ready": {
        "stock_name": GEMINI_READY_PRODUCT,
        "title_en": "Gemini Pro 12M Ready Account",
        "title_ar": "Gemini Pro 12M حساب جاهز",
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

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            lang TEXT DEFAULT 'ar',
            balance_usdt NUMERIC DEFAULT 0,
            balance_egp NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
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

async def ensure_user_by_id(user_id: int, username: str | None = None):
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users(telegram_id, username)
            VALUES($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE SET username=$2
            """,
            user_id,
            username,
        )

async def ensure_user(message: Message):
    await ensure_user_by_id(message.from_user.id, message.from_user.username)

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

def resolve_stock_product(product_type: str):
    aliases = {
        "chatgpt": "chatgpt",
        "chat": "chatgpt",
        "gpt": "chatgpt",
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
        return "ChatGPT Plus"
    if product_key == "gemini_ready":
        return "Gemini Ready"
    if product_key == "gemini_email":
        return "Gemini Email Activation"
    return product_key

async def broadcast_stock_added(product_key: str, quantity: int, total: int):
    product = PRODUCTS[product_key]
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id, lang FROM users")

    for user in users:
        user_id = user["telegram_id"]
        lang = user["lang"] or "ar"
        if lang == "en":
            text = (
                f"🚀 𝗡𝗘𝗪 𝗦𝗧𝗢𝗖𝗞 𝗔𝗗𝗗𝗘𝗗!\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"✨ {product['title_en']} is now available.\n"
                f"📦 New Stock: +{quantity}\n"
                f"🔥 Available Now: {total}\n\n"
                f"💎 Premium quality • Fast delivery • Trusted service\n\n"
                f"🛍 Open Products and order before stock runs out!"
            )
        else:
            text = (
                f"🚀 𝗡𝗘𝗪 𝗦𝗧𝗢𝗖𝗞 𝗔𝗗𝗗𝗘𝗗!\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"✨ تم إضافة مخزون جديد من {product['title_ar']}\n"
                f"📦 الكمية المضافة: +{quantity}\n"
                f"🔥 المتوفر الآن: {total}\n\n"
                f"💎 جودة بريميوم • تسليم سريع • خدمة موثوقة\n\n"
                f"🛍 افتح المنتجات واطلب قبل نفاد الكمية!"
            )
        try:
            await bot.send_message(user_id, text)
        except Exception:
            pass

async def loading_bar(message: Message, title: str):
    msg = await message.answer(f"{title}\n\n▱▱▱▱▱▱▱▱▱▱ 0%")
    frames = [
        ("▰▰▰▱▱▱▱▱▱▱", 30),
        ("▰▰▰▰▰▰▱▱▱▱", 60),
        ("▰▰▰▰▰▰▰▰▰▱", 90),
        ("▰▰▰▰▰▰▰▰▰▰", 100),
    ]
    for bar, percent in frames:
        await asyncio.sleep(0.16)
        try:
            await msg.edit_text(f"{title}\n\n{bar} {percent}%")
        except Exception:
            pass
    return msg

async def premium_transition(message: Message, title: str):
    msg = await message.answer(f"{title}\n\n▱▱▱▱▱▱▱▱▱▱ 0%")
    frames = [
        ("▰▰▰▱▱▱▱▱▱▱", 30),
        ("▰▰▰▰▰▰▱▱▱▱", 60),
        ("▰▰▰▰▰▰▰▰▰▱", 90),
        ("▰▰▰▰▰▰▰▰▰▰", 100),
    ]
    for bar, percent in frames:
        await asyncio.sleep(0.16)
        try:
            await msg.edit_text(f"{title}\n\n{bar} {percent}%")
        except Exception:
            pass
    await asyncio.sleep(0.12)
    try:
        await msg.delete()
    except Exception:
        pass

async def wallet_transition(message: Message, lang: str):
    title = "👛 Opening secure wallet..." if lang == "en" else "👛 فتح المحفظة الآمنة..."
    msg = await message.answer(f"{title}\n\n◇◇◇◇◇ 0%")
    frames = [
        ("◆◇◇◇◇", 20, "🔐 Securing session..." if lang == "en" else "🔐 تأمين الجلسة..."),
        ("◆◆◇◇◇", 40, "💵 Reading balances..." if lang == "en" else "💵 قراءة الأرصدة..."),
        ("◆◆◆◇◇", 60, "🧾 Syncing wallet..." if lang == "en" else "🧾 مزامنة المحفظة..."),
        ("◆◆◆◆◇", 80, "✨ Finalizing..." if lang == "en" else "✨ التجهيز النهائي..."),
        ("◆◆◆◆◆", 100, "✅ Wallet ready" if lang == "en" else "✅ المحفظة جاهزة"),
    ]
    for bar, percent, step in frames:
        await asyncio.sleep(0.18)
        try:
            await msg.edit_text(f"{title}\n{step}\n\n{bar} {percent}%")
        except Exception:
            pass
    await asyncio.sleep(0.15)
    try:
        await msg.delete()
    except Exception:
        pass

async def deposit_transition(message: Message, lang: str):
    title = "💳 Preparing premium deposit..." if lang == "en" else "💳 تجهيز الإيداع البريميوم..."
    msg = await message.answer(f"{title}\n\n⬡⬡⬡⬡⬡ 0%")
    frames = [
        ("⬢⬡⬡⬡⬡", 20, "🔎 Checking limits..." if lang == "en" else "🔎 فحص حدود الإيداع..."),
        ("⬢⬢⬡⬡⬡", 40, "💱 Loading currency options..." if lang == "en" else "💱 تجهيز العملات..."),
        ("⬢⬢⬢⬡⬡", 60, "🏦 Preparing methods..." if lang == "en" else "🏦 تجهيز طرق الدفع..."),
        ("⬢⬢⬢⬢⬡", 80, "🔐 Securing payment..." if lang == "en" else "🔐 تأمين الدفع..."),
        ("⬢⬢⬢⬢⬢", 100, "✅ Ready" if lang == "en" else "✅ جاهز"),
    ]
    for bar, percent, step in frames:
        await asyncio.sleep(0.18)
        try:
            await msg.edit_text(f"{title}\n{step}\n\n{bar} {percent}%")
        except Exception:
            pass
    await asyncio.sleep(0.15)
    try:
        await msg.delete()
    except Exception:
        pass

def product_buttons(lang: str, counts: dict):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | $5 | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | $6 | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
            [InlineKeyboardButton(text="👑 Gemini On Your Email | $4", callback_data="product_gemini_email")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_products")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | 250 جنيه | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | 300 جنيه | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
        [InlineKeyboardButton(text="👑 تفعيل Gemini على إيميلك | 200 جنيه", callback_data="product_gemini_email")],
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_products")],
    ])

def product_details_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Now", callback_data=f"buy_{product_key}")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="refresh_products")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="refresh_products")],
    ])

def payment_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data=f"pay_binance_{product_key}")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data=f"pay_vodafone_{product_key}")],
            [InlineKeyboardButton(text="🟣 InstaPay", callback_data=f"pay_instapay_{product_key}")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data=f"pay_vodafone_{product_key}")],
        [InlineKeyboardButton(text="🟣 انستا باي", callback_data=f"pay_instapay_{product_key}")],
    ])

def wallet_deposit_buttons(lang: str):
    # old helper kept for compatibility
    return deposit_currency_buttons(lang)

def deposit_currency_buttons(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇪🇬 Deposit EGP", callback_data="deposit_currency_EGP")],
            [InlineKeyboardButton(text="🟡 Deposit USDT", callback_data="deposit_currency_USDT")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 إيداع بالمصري", callback_data="deposit_currency_EGP")],
        [InlineKeyboardButton(text="🟡 إيداع بالدولار USDT", callback_data="deposit_currency_USDT")],
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str):
    amount_txt = format_amount(amount)
    currency = currency.upper()

    if currency == "USDT":
        if lang == "en":
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🟡 Binance UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
                [InlineKeyboardButton(text="🔙 Change Amount", callback_data="deposit_currency_USDT")],
            ])
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🟡 بينانس UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
            [InlineKeyboardButton(text="🔙 تغيير المبلغ", callback_data="deposit_currency_USDT")],
        ])

    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🔴 Vodafone Cash • {amount_txt} EGP", callback_data=f"topup_vodafone_{amount_txt}_EGP")],
            [InlineKeyboardButton(text=f"🟣 InstaPay • {amount_txt} EGP", callback_data=f"topup_instapay_{amount_txt}_EGP")],
            [InlineKeyboardButton(text="🔙 Change Amount", callback_data="deposit_currency_EGP")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔴 فودافون كاش • {amount_txt} جنيه", callback_data=f"topup_vodafone_{amount_txt}_EGP")],
        [InlineKeyboardButton(text=f"🟣 انستا باي • {amount_txt} جنيه", callback_data=f"topup_instapay_{amount_txt}_EGP")],
        [InlineKeyboardButton(text="🔙 تغيير المبلغ", callback_data="deposit_currency_EGP")],
    ])

def format_amount(amount):
    try:
        amount = float(amount)
        if amount.is_integer():
            return str(int(amount))
        return str(amount).rstrip("0").rstrip(".")
    except Exception:
        return str(amount)

def parse_deposit_amount(text: str):
    raw = text.strip().lower().replace(",", ".")
    currency = None

    if any(x in raw for x in ["usdt", "usd", "$", "دولار"]):
        currency = "USDT"
    elif any(x in raw for x in ["egp", "جنيه", "جنية", "مصري", "ج "]):
        currency = "EGP"

    cleaned = raw
    for token in ["usdt", "usd", "$", "دولار", "egp", "جنيه", "جنية", "مصري", "ج"]:
        cleaned = cleaned.replace(token, " ")

    number = None
    for part in cleaned.split():
        try:
            number = float(part)
            break
        except ValueError:
            continue

    if number is None:
        try:
            number = float(cleaned.strip())
        except Exception:
            return None, None

    if currency is None:
        # If the user writes only 250 or more, treat it as EGP.
        # If the user writes 5 to 249, treat it as USDT.
        currency = "EGP" if number >= 250 else "USDT"

    return number, currency

async def product_counts():
    return {
        "chatgpt": await get_stock_count("chatgpt"),
        "gemini_ready": await get_stock_count("gemini_ready"),
        "gemini_email": "∞",
    }

def product_list_text(lang: str):
    if lang == "en":
        return (
            "🛍 Available Products\n━━━━━━━━━━━━━━\n\n"
            "🤖 ChatGPT Plus 1M\n💰 $5 | 🛡 15 days\n\n"
            "💎 Gemini Pro 12M\n💰 $6 | 🛡 1 Year\n\n"
            "👑 Gemini On Your Email\n💰 $4 | 🛡 1 Year\n\n"
            "Choose a product below:"
        )
    return (
        "🛍 المنتجات المتاحة\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 250 جنيه | 🛡 15 يوم\n\n"
        "💎 Gemini Pro 12M\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "👑 تفعيل Gemini على إيميلك\n💰 200 جنيه | 🛡 سنة كاملة\n\n"
        "اختار المنتج:"
    )

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    caption = (
        f"{BOT_NAME}\n\nPremium AI Subscriptions\nFast • Secure • Trusted"
        if lang == "en"
        else f"{BOT_NAME}\n\nاشتراكات الذكاء الاصطناعي المميزة\nسريع • آمن • موثوق"
    )
    await message.answer_photo(
        photo=URLInputFile(CHATGPT_IMAGE),
        caption=caption,
        reply_markup=menu_en if lang == "en" else menu_ar,
    )

@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
async def language(message: Message):
    await ensure_user(message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])
    await message.answer("🌐 اختر اللغة / Choose language:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    await ensure_user_by_id(call.from_user.id, call.from_user.username)
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await call.message.answer(
        "✅ Language changed to English" if lang == "en" else "✅ تم تغيير اللغة للعربية",
        reply_markup=menu_en if lang == "en" else menu_ar,
    )
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet"]))
async def wallet(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(message.from_user.id)
    await wallet_transition(message, lang)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Deposit / إيداع", callback_data="choose_deposit_currency")],
        [InlineKeyboardButton(text="🔄 Refresh Balance / تحديث الرصيد", callback_data="refresh_wallet")],
    ])

    text = (
        f"👛 YOUR WALLET\n━━━━━━━━━━━━━━\n\n"
        f"💵 USDT Balance: {balance_usdt} USDT\n"
        f"🇪🇬 EGP Balance: {balance_egp} EGP\n\n"
        f"💳 Press Deposit to add balance.\n"
        f"⚠️ Minimum deposit: 5 USDT or 250 EGP"
        if lang == "en"
        else
        f"👛 المحفظة\n━━━━━━━━━━━━━━\n\n"
        f"💵 رصيد الدولار: {balance_usdt} USDT\n"
        f"🇪🇬 رصيد المصري: {balance_egp} جنيه\n\n"
        f"💳 اضغط إيداع لإضافة رصيد.\n"
        f"⚠️ أقل إيداع: 5 USDT أو 250 جنيه"
    )
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "refresh_wallet")
async def refresh_wallet(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    balance_usdt, balance_egp = await get_wallet_balance(call.from_user.id)
    await wallet_transition(call.message, lang)
    text = (
        f"👛 YOUR WALLET\n━━━━━━━━━━━━━━\n\n"
        f"💵 USDT Balance: {balance_usdt} USDT\n"
        f"🇪🇬 EGP Balance: {balance_egp} EGP"
        if lang == "en"
        else
        f"👛 المحفظة\n━━━━━━━━━━━━━━\n\n"
        f"💵 رصيد الدولار: {balance_usdt} USDT\n"
        f"🇪🇬 رصيد المصري: {balance_egp} جنيه"
    )
    await call.message.answer(text)
    await call.answer()

@dp.message(F.text.in_(["💳 إيداع", "💳 Deposit"]))
async def deposit_menu(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await deposit_transition(message, lang)
    text = (
        f"💳 ADD BALANCE\n━━━━━━━━━━━━━━\n\n"
        f"Choose the currency you want to deposit.\n\n"
        f"🇪🇬 EGP: minimum 250 EGP\n"
        f"🟡 USDT: minimum 5 USDT"
        if lang == "en"
        else
        f"💳 إضافة رصيد\n━━━━━━━━━━━━━━\n\n"
        f"اختار العملة اللي عايز تعمل بيها إيداع.\n\n"
        f"🇪🇬 المصري: أقل مبلغ 250 جنيه\n"
        f"🟡 الدولار USDT: أقل مبلغ 5 USDT"
    )
    await message.answer(text, reply_markup=deposit_currency_buttons(lang))

@dp.callback_query(F.data == "choose_deposit_currency")
@dp.callback_query(F.data == "start_deposit_amount")
async def choose_deposit_currency(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await deposit_transition(call.message, lang)
    text = (
        "💳 Choose deposit currency\n━━━━━━━━━━━━━━\n\n"
        "🇪🇬 EGP: minimum 250 EGP\n"
        "🟡 USDT: minimum 5 USDT"
        if lang == "en"
        else
        "💳 اختار عملة الإيداع\n━━━━━━━━━━━━━━\n\n"
        "🇪🇬 المصري: أقل مبلغ 250 جنيه\n"
        "🟡 الدولار USDT: أقل مبلغ 5 USDT"
    )
    await call.message.answer(text, reply_markup=deposit_currency_buttons(lang))
    await call.answer()

@dp.callback_query(F.data.startswith("deposit_currency_"))
async def deposit_currency_selected(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    currency = call.data.replace("deposit_currency_", "").upper()

    if currency not in ["EGP", "USDT"]:
        await call.answer("Invalid currency", show_alert=True)
        return

    deposit_waiting[call.from_user.id] = currency
    await deposit_transition(call.message, lang)

    if currency == "EGP":
        text = (
            "🇪🇬 EGP Deposit\n━━━━━━━━━━━━━━\n\n"
            "Type the amount you want to add in EGP.\n"
            "Minimum: 250 EGP\n\n"
            "Example: `250` or `500`"
            if lang == "en"
            else
            "🇪🇬 إيداع بالمصري\n━━━━━━━━━━━━━━\n\n"
            "اكتب المبلغ اللي عايز تضيفه بالجنيه.\n"
            "أقل مبلغ: 250 جنيه\n\n"
            "مثال: `250` أو `500`"
        )
    else:
        text = (
            "🟡 USDT Deposit\n━━━━━━━━━━━━━━\n\n"
            "Type the amount you want to add in USDT.\n"
            "Minimum: 5 USDT\n\n"
            "Example: `5` or `10`"
            if lang == "en"
            else
            "🟡 إيداع بالدولار USDT\n━━━━━━━━━━━━━━\n\n"
            "اكتب المبلغ اللي عايز تضيفه بالدولار.\n"
            "أقل مبلغ: 5 USDT\n\n"
            "مثال: `5` أو `10`"
        )

    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.message(lambda message: message.from_user and message.from_user.id in deposit_waiting)
async def receive_deposit_amount(message: Message):
    await ensure_user(message)

    if not message.text or message.text.startswith("/"):
        return

    lang = await get_lang(message.from_user.id)
    selected_currency = deposit_waiting.get(message.from_user.id)
    amount, parsed_currency = parse_deposit_amount(message.text)
    currency = selected_currency if selected_currency in ["EGP", "USDT"] else parsed_currency

    if amount is None:
        await message.answer(
            "❌ اكتب المبلغ رقم فقط مثل: `250` أو `5`",
            parse_mode="Markdown",
        )
        return

    if currency == "USDT" and amount < 5:
        await message.answer(
            "❌ أقل إيداع للدولار هو 5 USDT.\nاكتب مبلغ 5 USDT أو أكثر."
            if lang != "en"
            else "❌ Minimum USD deposit is 5 USDT.\nPlease enter 5 USDT or more."
        )
        return

    if currency == "EGP" and amount < 250:
        await message.answer(
            "❌ أقل إيداع بالمصري هو 250 جنيه.\nاكتب مبلغ 250 جنيه أو أكثر."
            if lang != "en"
            else "❌ Minimum EGP deposit is 250 EGP.\nPlease enter 250 EGP or more."
        )
        return

    deposit_waiting.pop(message.from_user.id, None)
    await deposit_transition(message, lang)

    amount_txt = format_amount(amount)
    text = (
        f"💳 Deposit Amount Selected\n━━━━━━━━━━━━━━\n\n"
        f"💰 Amount: {amount_txt} {currency}\n\n"
        f"Choose payment method below:"
        if lang == "en"
        else
        f"💳 تم تحديد مبلغ الإيداع\n━━━━━━━━━━━━━━\n\n"
        f"💰 المبلغ: {amount_txt} {currency}\n\n"
        f"اختار طريقة الدفع من الأزرار:"
    )
    await message.answer(text, reply_markup=deposit_amount_payment_buttons(lang, amount, currency))

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

    await deposit_transition(call.message, lang)

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
        [
            InlineKeyboardButton(text="✅ Approve Deposit", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}"),
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"💳 Wallet Deposit Request #{dep_id}\n"
        f"User: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"Method: {method}\n"
        f"Amount: {format_amount(amount)} {currency}\n\n"
        f"بعد التأكد اضغط Approve Deposit.",
        reply_markup=kb,
    )

    if method == "binance":
        pay_text = f"🟡 Binance UID Deposit\n━━━━━━━━━━━━━━\n\n🆔 UID:\n`{BINANCE_UID}`\n\n💰 Amount: {format_amount(amount)} USDT"
    elif method == "vodafone":
        pay_text = f"🔴 Vodafone Cash Deposit\n━━━━━━━━━━━━━━\n\n📱 Number:\n`{VODAFONE_CASH}`\n\n💰 Amount: {format_amount(amount)} EGP"
    else:
        pay_text = f"🟣 InstaPay Deposit\n━━━━━━━━━━━━━━\n\n🏦 InstaPay:\n`{INSTAPAY}`\n\n💰 Amount: {format_amount(amount)} EGP"

    await call.message.answer(
        f"{pay_text}\n\n"
        f"📸 بعد الدفع ابعت صورة إثبات الدفع هنا.\n"
        f"🧾 Deposit ID: #{dep_id}",
        parse_mode="Markdown",
    )
    await call.answer()

@dp.message(Command("deposit"))
async def manual_deposit(message: Message):
    await ensure_user(message)
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer(
            "استخدم الأمر كده:\n"
            "/deposit binance 5 usdt\n"
            "/deposit vodafone 250 egp\n"
            "/deposit instapay 250 egp"
        )
        return
    method = parts[1].lower()
    currency = parts[3].upper()
    if method not in ["binance", "vodafone", "instapay"] or currency not in ["USDT", "EGP"]:
        await message.answer("❌ طريقة الدفع أو العملة غير صحيحة")
        return
    try:
        amount = float(parts[2])
    except ValueError:
        await message.answer("❌ المبلغ غير صحيح")
        return

    if currency == "USDT" and amount < 5:
        await message.answer("❌ أقل إيداع للدولار هو 5 USDT")
        return
    if currency == "EGP" and amount < 250:
        await message.answer("❌ أقل إيداع بالمصري هو 250 جنيه")
        return

    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval(
            """
            INSERT INTO deposits (telegram_id, method, amount, currency, product_key)
            VALUES($1,$2,$3,$4,$5)
            RETURNING id
            """,
            message.from_user.id,
            method,
            amount,
            currency,
            WALLET_DEPOSIT_KEY,
        )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve Deposit", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}"),
        ]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"💳 Wallet Deposit Request #{dep_id}\n"
        f"User: @{message.from_user.username}\n"
        f"ID: {message.from_user.id}\n"
        f"Method: {method}\n"
        f"Amount: {format_amount(amount)} {currency}\n\n"
        f"بعد التأكد اضغط Approve Deposit.",
        reply_markup=kb,
    )
    await message.answer("✅ تم تسجيل طلب الإيداع. ابعت صورة إثبات الدفع الآن.")

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await premium_transition(message, "🛍 Loading products..." if lang == "en" else "🛍 جاري تحميل المنتجات...")
    counts = await product_counts()
    await message.answer(product_list_text(lang), reply_markup=product_buttons(lang, counts))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    counts = await product_counts()
    await premium_transition(call.message, "🔄 Updating products..." if lang == "en" else "🔄 جاري تحديث المنتجات...")
    try:
        await call.message.edit_text(product_list_text(lang), reply_markup=product_buttons(lang, counts))
    except Exception:
        await call.message.answer(product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer("Updated ✅")

@dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await premium_transition(call.message, "🤖 Preparing product..." if lang == "en" else "🤖 جاري تجهيز المنتج...")
    count = await get_stock_count("chatgpt")
    caption = (
        f"🤖 CHATGPT PLUS 1M\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $5\n📦 Stock: {count}\n🛡 Warranty: 15 Days\n\n"
        f"📌 Private Account\n📌 1 Month Subscription\n📌 Instant Delivery"
        if lang == "en"
        else
        f"🤖 ChatGPT Plus 1M\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 250 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: 15 يوم\n\n"
        f"📌 حساب خاص\n📌 اشتراك شهر\n📌 تسليم فوري"
    )
    await call.message.answer_photo(URLInputFile(CHATGPT_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "chatgpt"))
    await call.answer()

@dp.callback_query(F.data == "product_gemini_ready")
async def product_gemini_ready(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await premium_transition(call.message, "💎 Preparing product..." if lang == "en" else "💎 جاري تجهيز المنتج...")
    count = await get_stock_count("gemini_ready")
    caption = (
        f"💎 Gemini Pro 12M\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $6\n📦 Stock: {count}\n🛡 Warranty: 1 Year\n\n"
        f"☁️ 5TB Storage\n🤖 Gemini Advanced\n⚡ Ready Account"
        if lang == "en"
        else
        f"💎 Gemini Pro 12M\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 300 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: سنة كاملة\n\n"
        f"☁️ مساحة 5 تيرا بايت\n🤖 Gemini Advanced\n⚡ حساب جاهز"
    )
    await call.message.answer_photo(URLInputFile(GEMINI_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "gemini_ready"))
    await call.answer()

@dp.callback_query(F.data == "product_gemini_email")
async def product_gemini_email(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await premium_transition(call.message, "👑 Preparing product..." if lang == "en" else "👑 جاري تجهيز المنتج...")
    caption = (
        f"👑 Gemini Pro On Your Email\n━━━━━━━━━━━━━━\n\n"
        f"💰 Price: $4\n🛡 Warranty: 1 Year\n\n"
        f"☁️ 5TB Storage\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 Monthly Credits\n"
        f"👥 Add 5 Family Members\n🔑 You Become The Owner\n\n"
        f"📧 Activated On Your Personal Email"
        if lang == "en"
        else
        f"👑 Gemini على إيميلك الشخصي\n━━━━━━━━━━━━━━\n\n"
        f"💰 السعر: 200 جنيه\n🛡 الضمان: سنة كاملة\n\n"
        f"☁️ مساحة 5 تيرا بايت\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 كريديت شهري\n"
        f"👥 إضافة 5 أشخاص\n🔑 تصبح المالك الأساسي\n\n"
        f"📧 التفعيل على إيميلك الشخصي"
    )
    await call.message.answer_photo(URLInputFile(GEMINI_IMAGE), caption=caption, reply_markup=product_details_buttons(lang, "gemini_email"))
    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    await premium_transition(call.message, "🛒 Preparing checkout..." if lang == "en" else "🛒 جاري تجهيز الدفع...")
    if product["type"] == "stock":
        count = await get_stock_count(product_key)
        if count <= 0:
            await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
            return
    text = (
        f"🛒 Checkout\n━━━━━━━━━━━━━━\n\n💰 Price: ${product['usd']} / {product['egp']} EGP\n\nChoose payment method:"
        if lang == "en"
        else f"🛒 إتمام الشراء\n━━━━━━━━━━━━━━\n\n💰 السعر: {product['egp']} جنيه / {product['usd']} USDT\n\nاختار طريقة الدفع:"
    )
    await call.message.answer(text, reply_markup=payment_buttons(lang, product_key))
    await call.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")
    method = parts[1]
    product_key = "_".join(parts[2:])
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    await premium_transition(call.message, "🔐 Securing payment details..." if lang == "en" else "🔐 جاري تجهيز بيانات الدفع...")
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
        [
            InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}"),
        ]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"🛒 New Order #{dep_id}\n"
        f"User: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"Product: {product['title_en']}\n"
        f"Method: {method}\n"
        f"Amount: {amount} {currency}",
        reply_markup=kb,
    )
    if method == "binance":
        pay_text = f"🟡 Binance UID:\n`{BINANCE_UID}`\n\n💰 Amount: {amount} USDT"
    elif method == "vodafone":
        pay_text = f"🔴 Vodafone Cash:\n`{VODAFONE_CASH}`\n\n💰 Amount: {amount} EGP"
    else:
        pay_text = f"🟣 InstaPay:\n`{INSTAPAY}`\n\n💰 Amount: {amount} EGP"
    await call.message.answer(
        f"{pay_text}\n\n📸 بعد الدفع ابعت صورة إثبات الدفع هنا.\n🧾 Order ID: #{dep_id}",
        parse_mode="Markdown",
    )
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
                await conn.execute(
                    "UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2",
                    dep["amount"],
                    dep["telegram_id"],
                )
            else:
                await conn.execute(
                    "UPDATE users SET balance_egp = balance_egp + $1 WHERE telegram_id=$2",
                    dep["amount"],
                    dep["telegram_id"],
                )
            await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
            await bot.send_message(
                dep["telegram_id"],
                f"✅ تم قبول الإيداع وإضافة الرصيد\n━━━━━━━━━━━━━━\n\n💰 Amount: {dep['amount']} {dep['currency']}\n\nشكراً لثقتك ❤️",
            )
            await call.message.edit_text(f"✅ Wallet Deposit #{dep_id} Approved")
            await call.answer()
            return
        product = PRODUCTS[product_key]
        if product["type"] == "activation":
            await bot.send_message(
                dep["telegram_id"],
                f"✅ تم تأكيد الدفع بنجاح\n━━━━━━━━━━━━━━\n\n"
                f"📧 تفعيل Gemini على إيميلك الشخصي\n\n"
                f"يرجى التواصل مع الأدمن لإتمام التفعيل:\n{SUPPORT}\n\nشكراً لثقتك ❤️",
            )
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
            remaining = await conn.fetchval(
                "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
                product["stock_name"],
            )
            await bot.send_message(
                dep["telegram_id"],
                f"✅ تم تأكيد الدفع\n━━━━━━━━━━━━━━\n\n📦 بيانات الحساب:\n\n{item['item_data']}\n\nشكراً لشرائك ❤️",
            )
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

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    chatgpt = await get_stock_count("chatgpt")
    gemini = await get_stock_count("gemini_ready")
    await message.answer(
        f"📦 Stock Report\n\n"
        f"🤖 ChatGPT Stock: {chatgpt}\n"
        f"💎 Gemini Ready Stock: {gemini}\n\n"
        f"الأوامر:\n"
        f"/liststock chatgpt\n/liststock gemini\n"
        f"/delstock chatgpt ID\n/delstock gemini ID\n"
        f"/clearstock chatgpt\n/clearstock gemini"
    )

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/addstock", "").strip()
    if not text:
        await message.answer(
            "📦 إضافة استوك:\n\n"
            "/addstock chatgpt\nemail1:pass1\nemail2:pass2\n\n"
            "/addstock gemini\nemail1:pass1\nemail2:pass2\n\n"
            "ملاحظة: منتج Gemini على الإيميل الشخصي لا يحتاج استوك."
        )
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
    await bot.send_message(
        ADMIN_ID,
        f"📦 Stock Added\n\nProduct: {label}\nQuantity Added: {len(items)}\nCurrent Stock: {total}",
    )
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
        rows = await conn.fetch(
            """
            SELECT id, item_data FROM stock
            WHERE product=$1 AND sold=false
            ORDER BY id ASC
            LIMIT 50
            """,
            stock_name,
        )
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
        row = await conn.fetchrow("SELECT id, item_data FROM stock WHERE id=$1 AND product=$2 AND sold=false", item_id, stock_name)
        if not row:
            await message.answer("❌ العنصر غير موجود أو مباع بالفعل")
            return
        await conn.execute("DELETE FROM stock WHERE id=$1", item_id)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    label = product_label(product_key)
    await message.answer(f"🗑 تم حذف العنصر ID {item_id} من {label}\n📦 المتبقي: {total}")

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
    label = product_label(product_key)
    await message.answer(f"🗑 تم مسح {deleted} عنصر من استوك {label}")

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
            await bot.send_message(user["telegram_id"], f"📢 إشعار من {BOT_NAME}\n\n{text}")
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

@dp.message(F.text.in_(["💬 الدعم", "💬 Support"]))
async def support(message: Message):
    await message.answer(f"💬 {SUPPORT}")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
