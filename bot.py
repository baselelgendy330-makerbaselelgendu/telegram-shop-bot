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

AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

EMOJI = {
    "store": "5859297284029681680", "wallet": "6088990159334808217", "support": "6181322172263308706",
    "telegram": "6089099509202164251", "language": "5447410659077661506", "home": "5195140682590722632",
    "chatgpt": "5864127571754489150", "stock": "6089247294731852091", "shield": "5251203410396458957",
    "link": "5282843764451195532", "step": "5397782960512444700", "rocket": "6181682949516173646",
    "success": "6179298314953956852", "refresh": "5341715473882955310", "lightning": "6181421841274379029",
    "payment": "5352662091390008496", "binance": "6222208096257712941", "fire": "6266887773454603583",
    "announcement": "6181594486074777254", "stock_add": "5397916757333654639", "trash": "5445267414562389170",
    "error": "6181467651395558500", "arrows_up": "5449683594425410231", "arrows_down": "5447183459602669338",
    "bell": "5458603043203327669", "hundred": "6181303849932823189", "vip": "6181731641560407212",
    "verified": "5370941588165893740", "loading": "6089327236958132324",
    "num1": "5197397670724912036", "num2": "5197250993296785376", "num3": "5195203805725084605",
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
            return await message.answer_photo(photo=FSInputFile(AIX_HEADER_FILE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
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

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, lang TEXT DEFAULT 'ar', balance_usdt NUMERIC DEFAULT 0, created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id SERIAL PRIMARY KEY, telegram_id BIGINT, method TEXT, amount NUMERIC, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS product_key TEXT DEFAULT 'cdk_chatgpt';")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id SERIAL PRIMARY KEY, product TEXT NOT NULL, item_data TEXT NOT NULL, sold BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW()
        );
        """)

async def ensure_user_by_id(user_id: int, username: str | None = None, first_name: str | None = None):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO users(telegram_id, username, first_name) VALUES($1, $2, $3) ON CONFLICT (telegram_id) DO UPDATE SET username=$2, first_name=$3", user_id, username, first_name)

async def ensure_user(message: Message):
    await ensure_user_by_id(message.from_user.id, message.from_user.username, message.from_user.first_name)

async def get_lang(user_id: int) -> str:
    async with db_pool.acquire() as conn:
        lang = await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id)
    return lang or "ar"

async def get_wallet_balance(user_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance_usdt FROM users WHERE telegram_id=$1", user_id)
    return row["balance_usdt"] if row and row["balance_usdt"] else 0

async def get_stock_count(product_key: str = "cdk_chatgpt"):
    product = PRODUCTS.get(product_key, {"stock_name": "CDK Activation Chatgpt 1Y"})
    async with db_pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", product["stock_name"])

async def product_counts():
    return {"cdk_chatgpt": await get_stock_count("cdk_chatgpt")}

def user_display_name(user) -> str:
    return user.first_name or user.username or "User"

def format_amount(amount):
    try:
        amount = float(amount)
        return str(int(amount)) if amount.is_integer() else str(amount).rstrip("0").rstrip(".")
    except Exception:
        return str(amount)

def resolve_stock_product(product_type: str):
    if product_type.lower() in ["chatgpt", "cdk", "cdk_chatgpt"]:
        return "cdk_chatgpt", PRODUCTS["cdk_chatgpt"]["stock_name"]
    return None, None

def product_label(product_key: str):
    return "CDK Activation Chatgpt For 1 year" if product_key == "cdk_chatgpt" else product_key

async def edit_or_answer(message, text: str, reply_markup=None):
    return await safe_edit_or_answer(message, text, reply_markup)

async def animate_message(message: Message, lang: str):
    text = f"{ce('loading', '⏳')} <b>Loading...</b>" if lang == "en" else f"{ce('loading', '⏳')} <b>جاري التحميل...</b>"
    try:
        if getattr(message, "from_user", None) and message.from_user.is_bot:
            msg = await message.edit_text(text, parse_mode="HTML")
        else:
            msg = await message.answer(text, parse_mode="HTML")
    except Exception:
        msg = await message.answer(text, parse_mode="HTML")
    await asyncio.sleep(0.3)
    return msg or message

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
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Main Menu" if lang == "en" else "القائمة الرئيسية", callback_data="home_main")]])

def product_buttons(lang: str, counts: dict):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"CDK Activation Chatgpt 1Y | $9 | Stock {counts.get('cdk_chatgpt', 0)}", callback_data="product_cdk_chatgpt")],
            [InlineKeyboardButton(text="Refresh", callback_data="refresh_products"), InlineKeyboardButton(text="Back", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"CDK Activation Chatgpt 1Y | 9$ | المتاح {counts.get('cdk_chatgpt', 0)}", callback_data="product_cdk_chatgpt")],
        [InlineKeyboardButton(text="تحديث", callback_data="refresh_products"), InlineKeyboardButton(text="رجوع", callback_data="home_main")],
    ])

def product_details_buttons(lang: str, product_key: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy Now" if lang == "en" else "شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="Back to Shop" if lang == "en" else "رجوع للمتجر", callback_data="home_shop")],
    ])

def payment_buttons(lang: str, product_key: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 Binance UID" if lang == "en" else "🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="Back" if lang == "en" else "رجوع", callback_data=f"product_{product_key}")],
    ])

def deposit_currency_buttons(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Deposit" if lang == "en" else "إيداع بالدولار USDT", callback_data="deposit_currency_USDT")],
        [InlineKeyboardButton(text="Back" if lang == "en" else "رجوع", callback_data="home_main")],
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str):
    amount_txt = format_amount(amount)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🟡 Binance UID • {amount_txt} USDT" if lang == "en" else f"🟡 بينانس UID • {amount_txt} USDT", callback_data=f"topup_binance_{amount_txt}_USDT")],
        [InlineKeyboardButton(text="Change Amount" if lang == "en" else "تغيير المبلغ", callback_data="deposit_currency_USDT")],
    ])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")], [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]])

def wallet_kb(lang: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Deposit", callback_data="home_deposit")],
            [InlineKeyboardButton(text="Refresh", callback_data="home_wallet"), InlineKeyboardButton(text="Main Menu", callback_data="home_main")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إيداع", callback_data="home_deposit")],
        [InlineKeyboardButton(text="تحديث", callback_data="home_wallet"), InlineKeyboardButton(text="الرئيسية", callback_data="home_main")],
    ])

def main_reply_keyboard(lang: str):
    if lang == "en":
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛍 Products"), KeyboardButton(text="🎧 Support")], [KeyboardButton(text="💰 Wallet"), KeyboardButton(text="🌐 Language")]], resize_keyboard=True, is_persistent=True)
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛍 المنتجات"), KeyboardButton(text="🎧 الدعم")], [KeyboardButton(text="💰 المحفظة"), KeyboardButton(text="🌐 اللغة")]], resize_keyboard=True, is_persistent=True)

MENU_TEXTS = {"🛍 Products", "Products", "🛍 المنتجات", "المنتجات", "🎧 Support", "Support", "🎧 الدعم", "الدعم", "💰 Wallet", "Wallet", "💰 المحفظة", "المحفظة", "🌐 Language", "Language", "🌐 اللغة", "اللغة", "🏠 Home", "Home", "🏠 الرئيسية", "الرئيسية"}

def home_text(lang: str, name: str):
    name = esc(name)
    if lang == "en":
        return f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{name}</b>\nWelcome to your premium AI subscriptions store.\n\n{ce('store','🛍')} <b>Shop</b> — Browse & buy products\n{ce('wallet','💰')} <b>Deposit</b> — Add funds to your wallet\n{ce('support','🎧')} <b>Support</b> — Get help anytime\n\n{ce('lightning','⚡')} Fast activation • Secure payments • Trusted service"
    return f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n━━━━━━━━━━━━━━━━━━\n\nأهلاً، <b>{name}</b>\nنورت متجر اشتراكات الذكاء الاصطناعي المميزة.\n\n{ce('store','🛍')} <b>المتجر</b> — تصفح واشتري المنتجات\n{ce('wallet','💰')} <b>إيداع</b> — إضافة رصيد للمحفظة\n{ce('support','🎧')} <b>الدعم</b> — مساعدة في أي وقت\n\n{ce('lightning','⚡')} تفعيل سريع • دفع آمن • خدمة موثوقة"

def product_list_text(lang: str):
    if lang == "en":
        return f"{ce('store','🛍')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\nPrice: $9 | Subscription: 1 Year, no warranty {ce('error','❌')}\n\n{ce('arrows_down','⬇️')} Choose a product below:"
    return f"{ce('store','🛍')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\nالسعر: 9$ | الاشتراك سنه ، no warranty {ce('error','❌')}\n\n{ce('arrows_down','⬇️')} اختار المنتج من الأزرار:"

def deposit_intro_text(lang: str):
    if lang == "en":
        return f"{ce('wallet','💰')} <b>Deposit Balance</b>\n━━━━━━━━━━━━━━━━━━\n\nChoose the currency you want to deposit.\n\nUSDT: minimum 5 USDT"
    return f"{ce('wallet','💰')} <b>إيداع رصيد</b>\n━━━━━━━━━━━━━━━━━━\n\nاختار العملة اللي عايز تعمل بيها إيداع.\n\nالدولار USDT: أقل مبلغ 5 USDT"

async def send_home(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    name = user_display_name(message.from_user)
    await safe_answer_photo(message, home_text(lang, name), reply_markup=home_keyboard(lang))
    await message.answer("Main Menu" if lang == "en" else "القائمة الرئيسية", reply_markup=main_reply_keyboard(lang))

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
    await edit_or_answer(msg, f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\nUSDT Balance: {balance_usdt} USDT" if lang == "en" else f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\nرصيد الدولار: {balance_usdt} USDT", reply_markup=wallet_kb(lang))

@dp.message(Command("support"))
async def support_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await message.answer(f"{ce('support','🎧')} <b>Support Center</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}" if lang == "en" else f"{ce('support','🎧')} <b>مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}", reply_markup=back_home_keyboard(lang), parse_mode="HTML")

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
    await call.message.answer(f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:", reply_markup=language_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.message(Command("language"))
async def language_command(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await message.answer(f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:", reply_markup=language_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    await ensure_user_by_id(call.from_user.id, call.from_user.username, call.from_user.first_name)
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await call.message.answer(f"{ce('success','✅')} Language changed to English" if lang == "en" else f"{ce('success','✅')} تم تغيير اللغة للعربية", reply_markup=home_keyboard(lang), parse_mode="HTML")
    await call.answer()

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
        f"{ce('chatgpt','🤖')} <b>CDK Activation Chatgpt For 1 year</b>\n━━━━━━━━━━━━━━\n\n{ce('wallet','💰')} Price: $9\n{ce('stock','📦')} Stock: {count}\n{ce('shield','🛡')} Subscription: 1 Year, no warranty {ce('error','❌')}\n\n{ce('fire','🔥')} <b>K-12 Offer Activation for your personal account!</b>\n\n{ce('link','🔗')} <b>Redemption Link:</b> http://gpt.ddfafa.com\n\n{ce('bell','🔔')} <b>How to activate:</b>\n{ce('num1','1️⃣')} Put the CDK code in the first field.\n{ce('num2','2️⃣')} Click 'Open AuthSession Page', copy the full Access Token, and paste it in the second field.\n{ce('num3','3️⃣')} Click 'Activate Now' and you are done!\n\n{ce('lightning','⚡')} Instant delivery after payment."
        if lang == "en" else
        f"{ce('chatgpt','🤖')} <b>CDK Activation Chatgpt For 1 year</b>\n━━━━━━━━━━━━━━\n\n{ce('wallet','💰')} السعر: 9$\n{ce('stock','📦')} المتوفر: {count}\n{ce('shield','🛡')} الاشتراك سنه ، no warranty {ce('error','❌')}\n\n{ce('fire','🔥')} <b>تفعيل عرض K-12 على حسابك الشخصي!</b>\n\n{ce('link','🔗')} <b>موقع التفعيل:</b> http://gpt.ddfafa.com\n\n{ce('bell','🔔')} <b>طريقة التفعيل:</b>\n{ce('num1','1️⃣')} حط الكود (CDK) في الخانة الأولى.\n{ce('num2','2️⃣')} افتح 'Open AuthSession Page'، انسخ الاكسيس توكن بالكامل، واللصقه في الخانة التانية.\n{ce('num3','3️⃣')} دوس 'Activate Now' وبس كدا!\n\n{ce('lightning','⚡')} تسليم فوري للكود بعد الدفع."
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
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    if product["type"] == "stock" and await get_stock_count(product_key) <= 0:
        await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
        return
    msg = await animate_message(call.message, lang)
    await edit_or_answer(msg, f"{ce('payment','💳')} Checkout\n━━━━━━━━━━━━━━\n\n💰 Price: ${product['usd']}\n\n{ce('arrows_down','⬇️')} Choose payment method:" if lang == "en" else f"{ce('payment','💳')} إتمام الشراء\n━━━━━━━━━━━━━━\n\n💰 السعر: {product['usd']}$\n\n{ce('arrows_down','⬇️')} اختار طريقة الدفع:", reply_markup=payment_buttons(lang, product_key))
    await call.answer()

@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    balance_usdt = await get_wallet_balance(call.from_user.id)
    msg = await animate_message(call.message, lang)
    await edit_or_answer(msg, f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 USDT Balance: {balance_usdt} USDT\n\n{ce('payment','💳')} Deposit funds anytime.\n⚠️ Minimum: 5 USDT" if lang == "en" else f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 رصيد الدولار: {balance_usdt} USDT\n\n{ce('payment','💳')} تقدر تضيف رصيد في أي وقت.\n⚠️ أقل إيداع: 5 USDT", reply_markup=wallet_kb(lang))
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet", "💰 المحفظة", "💰 Wallet"]))
async def wallet_message(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    msg = await animate_message(message, lang)
    balance_usdt = await get_wallet_balance(message.from_user.id)
    await safe_edit_or_answer(msg, f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 USDT Balance: {balance_usdt} USDT" if lang == "en" else f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\n💵 رصيد الدولار: {balance_usdt} USDT", reply_markup=wallet_kb(lang))

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
    await edit_or_answer(msg, f"{ce('binance','🟡')} USDT Deposit\n━━━━━━━━━━━━━━\n\nType the amount you want to add in USDT.\nMinimum: 5 USDT\n\nExample: 5 or 10" if lang == "en" else f"{ce('binance','🟡')} إيداع بالدولار USDT\n━━━━━━━━━━━━━━\n\nاكتب المبلغ اللي عايز تضيفه بالدولار.\nأقل مبلغ: 5 USDT\n\nمثال: 5 أو 10", reply_markup=back_home_keyboard(lang))
    await call.answer()

async def route_main_keyboard_actions(message: Message, text_value: str):
    if "Product" in text_value or "منتجات" in text_value or text_value == "المنتجات":
        lang = await get_lang(message.from_user.id)
        msg = await animate_message(message, lang)
        counts = await product_counts()
        await edit_or_answer(msg, product_list_text(lang), reply_markup=product_buttons(lang, counts))
    elif "Support" in text_value or "دعم" in text_value or text_value == "الدعم":
        lang = await get_lang(message.from_user.id)
        await message.answer(f"{ce('support','🎧')} <b>Support Center</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}" if lang == "en" else f"{ce('support','🎧')} <b>مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('telegram','✈️')} {SUPPORT}", reply_markup=back_home_keyboard(lang), parse_mode="HTML")
    elif "Wallet" in text_value or "محفظ" in text_value or text_value == "المحفظة":
        lang = await get_lang(message.from_user.id)
        balance_usdt = await get_wallet_balance(message.from_user.id)
        msg = await animate_message(message, lang)
        await edit_or_answer(msg, f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\nUSDT Balance: {balance_usdt} USDT" if lang == "en" else f"{ce('wallet','💰')} <b>AIX WALLET</b>\n━━━━━━━━━━━━━━\n\nرصيد الدولار: {balance_usdt} USDT", reply_markup=wallet_kb(lang))
    elif "Language" in text_value or "لغة" in text_value or text_value == "اللغة":
        lang = await get_lang(message.from_user.id)
        await message.answer(f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:", reply_markup=language_keyboard(), parse_mode="HTML")
    else:
        await send_home(message)

@dp.message(F.text.in_(MENU_TEXTS))
async def route_main_reply_keyboard(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    await route_main_keyboard_actions(message, (message.text or "").strip())

@dp.message(lambda message: message.from_user and message.from_user.id in deposit_waiting)
async def receive_deposit_amount(message: Message):
    await ensure_user(message)
    if not message.text or message.text.startswith("/"): return
    lang = await get_lang(message.from_user.id)
    currency = deposit_waiting.get(message.from_user.id)
    try:
        amount = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer(f"{ce('error','❌')} Numbers only" if lang == "en" else f"{ce('error','❌')} اكتب رقم فقط")
        return
    if currency == "USDT" and amount < 5:
        await message.answer(f"{ce('error','❌')} Minimum is 5 USDT" if lang == "en" else f"{ce('error','❌')} أقل إيداع 5 USDT.")
        return
    deposit_waiting.pop(message.from_user.id, None)
    msg = await animate_message(message, lang)
    amount_txt = format_amount(amount)
    text = (
        f"{ce('payment','💳')} Deposit Selected\n━━━━━━━━━━━━━━\n\n💰 Amount: {amount_txt} {currency}\n\n{ce('binance','🟡')} <b>Binance UID</b>\n<code>{BINANCE_UID}</code>"
        if lang == "en" else
        f"{ce('payment','💳')} تم تحديد مبلغ الإيداع\n━━━━━━━━━━━━━━\n\n💰 المبلغ: {amount_txt} {currency}\n\n{ce('binance','🟡')} <b>بينانس UID</b>\n<code>{BINANCE_UID}</code>"
    )
    await edit_or_answer(msg, text, reply_markup=deposit_amount_payment_buttons(lang, amount, currency))

@dp.callback_query(F.data.startswith("topup_"))
async def create_wallet_topup(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    parts = call.data.split("_")
    method, amount, currency = parts[1], float(parts[2]), parts[3].upper()
    msg = await animate_message(call.message, lang)
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("INSERT INTO deposits (telegram_id, method, amount, currency, product_key) VALUES($1,$2,$3,$4,$5) RETURNING id", call.from_user.id, method, amount, currency, WALLET_DEPOSIT_KEY)
    await bot.send_message(ADMIN_ID, f"💳 Wallet Deposit Request #{dep_id}\nUser: @{call.from_user.username}\nID: {call.from_user.id}\nAmount: {format_amount(amount)} {currency}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]]))
    await edit_or_answer(msg, f"🟡 UID: <code>{BINANCE_UID}</code>\n💰 Amount: {format_amount(amount)} USDT\n📸 Send screenshot proof here. ID: #{dep_id}" if lang == "en" else f"🟡 بينانس UID: <code>{BINANCE_UID}</code>\n💰 المبلغ: {format_amount(amount)} USDT\n📸 ابعت صورة الإثبات هنا. رقم: #{dep_id}")
    await call.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")
    method, product_key = parts[1], "_".join(parts[2:])
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    msg = await animate_message(call.message, lang)
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("INSERT INTO deposits (telegram_id, method, amount, currency, product_key) VALUES($1,$2,$3,$4,$5) RETURNING id", call.from_user.id, method, product["usd"], "USDT", product_key)
    await bot.send_message(ADMIN_ID, f"🛒 Order #{dep_id}\nUser: @{call.from_user.username}\nProduct: {product['title_en']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]]))
    await edit_or_answer(msg, f"🟡 UID: <code>{BINANCE_UID}</code>\n💰 Amount: {product['usd']} USDT\n📸 Send screenshot proof here. ID: #{dep_id}" if lang == "en" else f"🟡 بينانس UID: <code>{BINANCE_UID}</code>\n💰 المبلغ: {product['usd']} USDT\n📸 ابعت صورة الإثبات هنا. رقم الطلب: #{dep_id}")
    await call.answer()

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
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
            await bot.send_message(dep["telegram_id"], f"✅ Deposit approved! Added {dep['amount']} USDT" if user_lang == "en" else f"✅ تم قبول الإيداع! وإضافة {dep['amount']} USDT", parse_mode="HTML")
            await call.message.edit_text(f"✅ Wallet Deposit #{dep_id} Approved", parse_mode="HTML")
            return
        product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
        item = await conn.fetchrow("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT 1", product["stock_name"])
        if not item:
            await call.message.edit_text("❌ لا يوجد مخزون", parse_mode="HTML")
            await bot.send_message(dep["telegram_id"], "❌ Out of stock. Contact support.", parse_mode="HTML")
            return
        await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
        deliver_text = f"✅ Payment Confirmed\n📦 Your CDK Code:\n<code>{item['item_data']}</code>\n🔗 Link: http://gpt.ddfafa.com" if user_lang == "en" else f"✅ تم تأكيد الدفع\n📦 الكود الخاص بك:\n<code>{item['item_data']}</code>\n🔗 رابط التفعيل: http://gpt.ddfafa.com"
        await bot.send_message(dep["telegram_id"], deliver_text, parse_mode="HTML")
    await call.message.edit_text(f"✅ Order #{dep_id} Approved", parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            user_lang = await get_lang(dep["telegram_id"])
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], "❌ Order rejected." if user_lang == "en" else "❌ تم رفض الطلب.", parse_mode="HTML")
    await call.message.edit_text(f"❌ Order #{dep_id} Rejected", parse_mode="HTML")
    await call.answer()

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID: return
    lang = await get_lang(message.from_user.id)
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer("📤 Sent for review." if lang == "en" else "📤 تم إرسال الإثبات للمراجعة.")

@dp.callback_query(F.data == "home_support")
async def support_inline(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
    await edit_or_answer(msg, f"🎧 Support: {SUPPORT}", reply_markup=back_home_keyboard(lang))
    await call.answer()

@dp.message(F.text.in_(["💬 الدعم", "💬 Support"]))
async def support_message(message: Message):
    await message.answer(f"🎧 Support: {SUPPORT}", parse_mode="HTML")

@dp.message(Command("getemoji"))
async def get_emoji_id(message: Message):
    if message.from_user.id != ADMIN_ID: return
    target = message.reply_to_message
    if not target:
        await message.answer("Reply to animated emoji and send /getemoji")
        return
    entities = (target.entities or []) + (target.caption_entities or [])
    result = [f"Emoji ID:\n<code>{e.custom_emoji_id}</code>" for e in entities if e.type == "custom_emoji" and e.custom_emoji_id]
    await message.answer("\n\n".join(result) if result else "❌ No animated emoji found.", parse_mode="HTML")

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(f"📦 Stock: {await get_stock_count('cdk_chatgpt')}\n\n/addstock cdk\nCODE")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/addstock", "").strip()
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if len(lines) < 2:
        await message.answer("Use:\n/addstock cdk\nCODE")
        return
    product_key, stock_name = resolve_stock_product(lines[0])
    items = lines[1:]
    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"✅ Added {len(items)} items. Total: {total}")

@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/broadcast", "").strip()
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id FROM users")
    sent = 0
    for user in users:
        try:
            await bot.send_message(user["telegram_id"], f"📢 {esc(text)}", parse_mode="HTML")
            sent += 1
        except Exception: pass
    await message.answer(f"✅ Sent to {sent} users.")

async def setup_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Start"),
        BotCommand(command="menu", description="Menu"),
        BotCommand(command="products", description="Products"),
        BotCommand(command="wallet", description="Wallet"),
        BotCommand(command="support", description="Support"),
        BotCommand(command="language", description="Language"),
    ])

async def main():
    await init_db()
    await setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

