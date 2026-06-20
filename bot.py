import asyncio
import os
import html
import re
import json
import asyncpg
import hmac
import hashlib
import time
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    URLInputFile, FSInputFile, BotCommand, ReplyKeyboardMarkup, KeyboardButton
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587
BINANCE_UID = "381880403"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"
REFERRAL_REWARD = 0.10

# مفاتيح بينانس من السيرفر
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

EMOJI = {
    "cart": "5312361253610475399",
    "back": "6181245923708903693",
    "wallet": "6088990159334808217",
    "binance": "5354924237779909158",
    "share": "6089193719309801680",
    "support": "6181322172263308706",
    "language": "5447410659077661506",
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
    "hourglass": "5386367538735104399"
}

SAFE_EMOJI_FALLBACK = {
    "cart": "🛒", "back": "🔙", "wallet": "💰", "binance": "🟡", "share": "🎁", "support": "🎧", 
    "language": "🌐", "checkout": "💳", "quantity": "📦", "price": "💵", "pencil": "✏️", "loading": "⏳",
    "user": "👤", "camera": "📸", "success": "✅", "error": "❌", "chatgpt": "🤖", "refresh": "🔄", 
    "store": "🛍", "stock": "➕", "sold": "↗️", "support_msg": "💬", "telegram": "⚡", "arrow_right": "➡️",
    "users_group": "👥", "money_fly": "💸", "link_pin": "📇", "quotes": "🗣️", "search": "🔍", "hourglass": "⌛", "announcement": "🚨"
}

def ce(key: str, fallback: str = "") -> str:
    emoji_id = EMOJI.get(key)
    safe_fallback = SAFE_EMOJI_FALLBACK.get(key, fallback or "✅")
    if not emoji_id or not str(emoji_id).isdigit(): return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'

def esc(value) -> str: return html.escape(str(value), quote=False)
def strip_custom_emoji(text: str) -> str: return re.sub(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r'\1', text)

# ━━━━━ دالة الأمان المعدلة ━━━━━
async def safe_answer(message: Message, text: str, reply_markup=None):
    try: return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest: return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")

async def safe_edit_or_answer(message, text: str, reply_markup=None):
    try: 
        return await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return message
        try: 
            return await message.edit_text(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
        except Exception: 
            return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
    except Exception: 
        return await safe_answer(message, text, reply_markup)

async def safe_answer_photo(message: Message, caption: str, reply_markup=None):
    try:
        if os.path.exists(AIX_HEADER_FILE): return await message.answer_photo(photo=FSInputFile(AIX_HEADER_FILE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest:
        try:
            if os.path.exists(AIX_HEADER_FILE): return await message.answer_photo(photo=FSInputFile(AIX_HEADER_FILE), caption=strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
            return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
        except Exception: return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
    except Exception: return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")

CDK_IMAGE_FILE = "https://i.postimg.cc/Twx17x9S/IMG-20260616-190321.jpg"
WALLET_DEPOSIT_KEY = "wallet_deposit"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}
binance_waiting: dict[int, dict] = {} 

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title_en": "CDK GPT Plus (K12 - EDU) 1 year No warranty",
        "title_ar": "CDK GPT Plus (K12 - EDU) 1 year No warranty",
        "image": CDK_IMAGE_FILE,
        "usd": 6,  
        "type": "stock",
        "desc_en": "✅ ChatGPT K12 Edu 1 year package.\nFull of latest languages like Plus\n✅ Can activate any account owner. Only applies to Gmail or hotmail, outlook\n✅ After ordering, you will receive a code\n✅ Account is on free plan\n✅ Recommended to use an account without an active subscription or a newly created account to register.\n✅ Web upgrade CDK: http://gpt.ddfafa.com",
        "desc_ar": "✅ باقة ChatGPT K12 المخصصة للتعليم لمدة سنة كاملة.\nتحتوي على أحدث المميزات واللغات مثل حسابات بلس تماماً.\n✅ تقبل التفعيل على أي حساب، وتطبق على إيميلات جيمل، هوتميل، وأوتلوك.\n✅ بعد الطلب والدفع، ستتلقى كود التفعيل فوراً.\n✅ الحساب يجب أن يكون على الخطة المجانية الحالية.\n✅ يوصى باستخدام حساب ليس به اشتراك نشط أو حساب جديد تماماً للتسجيل.\n✅ موقع ترقية وتفعيل الكود: http://gpt.ddfafa.com"
    }
}

# ━━━━━ 🟡 لوجيك فحص بينانس الذكي والآمن 🟡 ━━━━━
async def check_binance_payment_via_api(pay_id: str, expected_amount: float) -> bool:
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        print("⚠️ Binance API Keys are missing in variables!")
        return False
    
    url = "https://api.binance.com/sapi/v1/pay/transactions"
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(BINANCE_API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    headers = {
        "X-MBX-APIKEY": BINANCE_API_KEY
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}?{query_string}&signature={signature}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    transactions = data.get("data", [])
                    for tx in transactions:
                        if str(tx.get("orderId")) == str(pay_id) or str(tx.get("transactionId")) == str(pay_id):
                            amount = float(tx.get("amount", 0))
                            status = tx.get("status") 
                            if status == "SUCCESS" and abs(amount - expected_amount) < 0.01:
                                return True
                else:
                    print(f"Binance API Error Status: {resp.status}")
        return False
    except Exception as e:
        print(f"Binance API Connection Error: {e}")
        return False

# ━━━━━ دالات قاعدة البيانات ━━━━━
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, lang TEXT DEFAULT 'ar', 
            balance_usdt NUMERIC DEFAULT 0, referred_by BIGINT, total_ref INT DEFAULT 0, created_at TIMESTAMP DEFAULT NOW()
        );""")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_ref INT DEFAULT 0;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        await conn.execute("CREATE TABLE IF NOT EXISTS deposits (id SERIAL PRIMARY KEY, telegram_id BIGINT, method TEXT, amount NUMERIC, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', quantity INT DEFAULT 1, txid TEXT UNIQUE, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS txid TEXT UNIQUE;")
        await conn.execute("CREATE TABLE IF NOT EXISTS stock (id SERIAL PRIMARY KEY, product TEXT NOT NULL, item_data TEXT NOT NULL, sold BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW());")

async def ensure_user_by_id(user_id: int, username: str | None = None, first_name: str | None = None, referrer_id: int | None = None):
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", user_id)
        if not user:
            if referrer_id and referrer_id != user_id:
                ref_exists = await conn.fetchval("SELECT telegram_id FROM users WHERE telegram_id=$1", referrer_id)
                if ref_exists:
                    await conn.execute("INSERT INTO users(telegram_id, username, first_name, referred_by) VALUES($1, $2, $3, $4)", user_id, username, first_name, referrer_id)
                    await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1, total_ref = total_ref + 1 WHERE telegram_id=$2", REFERRAL_REWARD, referrer_id)
                    try: await bot.send_message(referrer_id, f"{ce('share')} <b>New Referral!</b>\n━━━━━━━━━━━━━━\nSomeone joined via your link! <b>+{REFERRAL_REWARD} USDT</b> has been added to your wallet.", parse_mode="HTML")
                    except Exception: pass
            if not referrer_id or referrer_id == user_id:
                await conn.execute("INSERT INTO users(telegram_id, username, first_name) VALUES($1, $2, $3) ON CONFLICT (telegram_id) DO NOTHING", user_id, username, first_name)
        else:
            await conn.execute("UPDATE users SET username=$1, first_name=$2 WHERE telegram_id=$3", username, first_name, user_id)

async def get_lang(user_id: int) -> str:
    async with db_pool.acquire() as conn: return await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id) or "ar"

async def get_user_stats(user_id: int):
    async with db_pool.acquire() as conn: return await conn.fetchrow("SELECT balance_usdt, total_ref FROM users WHERE telegram_id=$1", user_id)

async def get_stock_count(product_key: str = "cdk_chatgpt"):
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    async with db_pool.acquire() as conn: return await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", product["stock_name"])

async def get_total_sold(product_name):
    return await db_pool.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=true", product_name)

async def product_counts(): return {"cdk_chatgpt": await get_stock_count("cdk_chatgpt")}

def format_amount(amount):
    try: return str(int(amount)) if float(amount).is_integer() else str(amount).rstrip("0").rstrip(".")
    except Exception: return str(amount)

def resolve_stock_product(product_type: str):
    if product_type.lower() in ["chatgpt", "cdk", "cdk_chatgpt"]: return "cdk_chatgpt", PRODUCTS["cdk_chatgpt"]["stock_name"]
    return None, None

async def handle_shop_action(target_message: Message, lang: str):
    counts = await product_counts()
    await safe_edit_or_answer(target_message, product_list_text(lang), reply_markup=product_buttons(lang, counts))

def get_delivery_text(lang: str, product: dict, qty: int, support: str):
    if lang == "en":
        return f"""{ce('success')} <b>Payment Confirmed Successfully!</b>\n━━━━━━━━━━━━━━━━━━━━━\n{ce('vip')} <b>{product['title_en']}</b>\n\n{ce('quantity')} <b>Quantity:</b> {qty}\n\n{ce('announcement')} <b>How to receive your codes:</b>\nPlease contact the admin directly to receive your keys instantly! Send a screenshot of this message to the admin below.\n{ce('support')} <b>Contact Admin:</b> {support}\n\n━━━━━━━━━━━━━━━━━━━━━\n{ce('heart')} <b>Thank you for trusting AIX Store!</b>"""
    else:
        return f"""{ce('success')} <b>تم تأكيد الدفع وتسليم طلب بنجاح!</b>\n━━━━━━━━━━━━━━━━━━━━━\n{ce('vip')} <b>{product['title_ar']}</b>\n\n{ce('quantity')} <b>الكمية المطلوبة:</b> {qty}\n\n{ce('announcement')} <b>لاستلام الأكواد الخاصة بك:</b>\nبرجاء التواصل مع الإدارة لاستلام الأكواد فوراً. يرجى إرسال سكرين شوت لهذه الرسالة كإثبات لطلبك!\n{ce('support')} <b>تواصل مع الإدارة:</b> {support}\n\n━━━━━━━━━━━━━━━━━━━━━\n{ce('heart')} <b>شكراً لثقتك في AIX Store!</b>"""

def reply_quantity_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5")],
        [KeyboardButton(text="❌ Cancel / إلغاء")]
    ], resize_keyboard=True, one_time_keyboard=True)

def home_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Browse Products" if lang=="en" else "تصفح المنتجات", callback_data="home_shop", icon_custom_emoji_id=EMOJI["store"])],
        [InlineKeyboardButton(text="Deposit" if lang=="en" else "إيداع", callback_data="home_deposit", icon_custom_emoji_id=EMOJI["wallet"]), InlineKeyboardButton(text="Wallet / Profile" if lang=="en" else "المحفظة والحساب", callback_data="home_wallet", icon_custom_emoji_id=EMOJI["user"])],
        [InlineKeyboardButton(text="Support" if lang=="en" else "الدعم", callback_data="home_support", icon_custom_emoji_id=EMOJI["support"]), InlineKeyboardButton(text="Share & Earn" if lang=="en" else "نشر وبناء أرباح", callback_data="home_share", icon_custom_emoji_id=EMOJI["share"])],
        [InlineKeyboardButton(text="Language" if lang=="en" else "اللغة", callback_data="home_language", icon_custom_emoji_id=EMOJI["language"])]
    ])

def back_home_keyboard(lang: str): 
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Main Menu" if lang == "en" else "القائمة الرئيسية", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]])

def product_buttons(lang: str, counts: dict):
    stock_count = counts.get('cdk_chatgpt', 0)
    chatgpt_icon_id = "5359726582447487916" 
    refresh_icon_id = "5386367538735104399"
    if lang == "en": 
        if stock_count == 0:
            btn_product = InlineKeyboardButton(text=f"CDK GPT Plus 1Y | $6.00 | 0", callback_data="product_cdk_chatgpt", icon_custom_emoji_id=EMOJI["error"])
        else:
            btn_product = InlineKeyboardButton(text=f"CDK GPT Plus 1Y | $6.00 | {stock_count}", callback_data="product_cdk_chatgpt", icon_custom_emoji_id=chatgpt_icon_id)
        return InlineKeyboardMarkup(inline_keyboard=[
            [btn_product], 
            [InlineKeyboardButton(text="Refresh products", callback_data="refresh_products", icon_custom_emoji_id=refresh_icon_id), InlineKeyboardButton(text="Back", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
        ])
    else:
        if stock_count == 0:
            btn_product = InlineKeyboardButton(text=f"CDK GPT Plus 1Y | 6.00$ | 0", callback_data="product_cdk_chatgpt", icon_custom_emoji_id=EMOJI["error"])
        else:
            btn_product = InlineKeyboardButton(text=f"CDK GPT Plus 1Y | 6.00$ | {stock_count}", callback_data="product_cdk_chatgpt", icon_custom_emoji_id=chatgpt_icon_id)
        return InlineKeyboardMarkup(inline_keyboard=[
            [btn_product], 
            [InlineKeyboardButton(text="تحديث المنتجات", callback_data="refresh_products", icon_custom_emoji_id=refresh_icon_id), InlineKeyboardButton(text="رجوع", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
        ])

def product_details_buttons(lang: str, product_key: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy Now" if lang == "en" else "شراء الآن", callback_data=f"buy_{product_key}", icon_custom_emoji_id=EMOJI["cart"])],
        [InlineKeyboardButton(text="Back to Shop" if lang == "en" else "رجوع للمتجر", callback_data="home_shop", icon_custom_emoji_id=EMOJI["back"])]
    ])

def checkout_payment_buttons(lang: str, product_key: str, qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Pay from Wallet" if lang=="en" else "الدفع من المحفظة", callback_data=f"pay_wallet_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["wallet"])],
        [InlineKeyboardButton(text="Pay via Binance UID" if lang=="en" else "الدفع عبر بينانس UID", callback_data=f"pay_binance_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["binance"])],
        [InlineKeyboardButton(text="Back" if lang=="en" else "رجوع", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_currency_buttons(lang: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Deposit" if lang == "en" else "إيداع بالدولار USDT", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["price"])], 
        [InlineKeyboardButton(text="Back" if lang == "en" else "رجوع", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Binance UID • {format_amount(amount)} USDT", callback_data=f"topup_binance_{format_amount(amount)}_USDT", icon_custom_emoji_id=EMOJI["binance"])], 
        [InlineKeyboardButton(text="Change Amount" if lang == "en" else "تغيير المبلغ", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["pencil"])]
    ])

def language_keyboard(): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")], 
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

def wallet_kb(lang: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="إيداع" if lang=="ar" else "Deposit", callback_data="home_deposit", icon_custom_emoji_id=EMOJI["wallet"])], 
        [InlineKeyboardButton(text="تحديث" if lang=="ar" else "Refresh", callback_data="home_wallet", icon_custom_emoji_id=EMOJI["refresh"]), InlineKeyboardButton(text="الرئيسية" if lang=="ar" else "Main Menu", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def main_reply_keyboard(lang: str):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Products" if lang=="en" else "🛍 المنتجات"), KeyboardButton(text="🎧 Support" if lang=="en" else "🎧 الدعم")], 
        [KeyboardButton(text="💰 Wallet" if lang=="en" else "💰 المحفظة"), KeyboardButton(text="🎁 Share & Earn" if lang=="en" else "🎁 الإحالات")],
        [KeyboardButton(text="🌐 Language" if lang=="en" else "🌐 اللغة")]
    ], resize_keyboard=True, is_persistent=True)

def home_text(lang: str, name: str):
    if lang == "en": return f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{esc(name)}</b>\nWelcome to your premium AI subscriptions store.\n\n{ce('store')} <b>Shop</b> — Browse & buy products\n{ce('wallet')} <b>Deposit</b> — Add funds to your wallet\n{ce('support')} <b>Support</b> — Get help anytime\n\n{ce('lightning')} Fast activation • Secure payments • Trusted service"
    return f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nأهلاً، <b>{esc(name)}</b>\nنورت متجر اشتراكات الذكاء الاصطناعي المميزة.\n\n{ce('store')} <b>المتجر</b> — تصفح واشتري المنتجات\n{ce('wallet')} <b>إيداع</b> — إضافة رصيد للمحفظة\n{ce('support')} <b>الدعم</b> — مساعدة في أي وقت\n\n{ce('lightning')} تفعيل سريع • دفع آمن • خدمة موثوقة"

def product_list_text(lang: str):
    if lang == "en": return f"{ce('store')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('chatgpt')} <b>CDK Activation Chatgpt For 1 year</b>\nPrice: $6 | Subscription: 1 Year, no warranty {ce('error')}\n\n{ce('arrows_down')} Choose a product below:"
    return f"{ce('store')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('chatgpt')} <b>CDK Activation Chatgpt For 1 year</b>\nالسعر: 6$ | الاشتراك سنه ، no warranty {ce('error')}\n\n{ce('arrows_down')} اختار المنتج من الأزرار:"

async def animate_message(message: Message, lang: str):
    text = f"{ce('loading')} <b>Loading...</b>" if lang == "en" else f"{ce('loading')} <b>جاري التحميل...</b>"
    try:
        if getattr(message, "from_user", None) and message.from_user.is_bot:
            if getattr(message, "photo", None): msg = await message.answer(text, parse_mode="HTML")
            else: msg = await message.edit_text(text, parse_mode="HTML")
        else: msg = await message.answer(text, parse_mode="HTML")
    except Exception: msg = await message.answer(text, parse_mode="HTML")
    await asyncio.sleep(0.3)
    return msg or message

async def send_home(message: Message):
    lang = await get_lang(message.from_user.id)
    await safe_answer_photo(message, home_text(lang, message.from_user.first_name or "User"), reply_markup=home_keyboard(lang))
    await message.answer("Main Menu" if lang == "en" else "القائمة الرئيسية", reply_markup=main_reply_keyboard(lang))

@dp.message(CommandStart())
async def start(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    buy_waiting.pop(message.from_user.id, None)
    binance_waiting.pop(message.from_user.id, None)
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit(): referrer_id = int(args[1])
    await ensure_user_by_id(message.from_user.id, message.from_user.username, message.from_user.first_name, referrer_id)
    await send_home(message)

@dp.message(Command("menu"))
async def menu_command(message: Message): await start(message)

# ━━━━━ أوامر الإدارة ━━━━━
@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID: return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2: 
        await message.answer(f"{ce('error')} <b>خطأ! استخدم الصيغة دي (في رسالة واحدة):</b>\n\n<code>/addstock CDK</code>\n<code>الكود_الأول</code>", parse_mode="HTML")
        return
    product_key, stock_name = resolve_stock_product(lines[0])
    if not stock_name: return await message.answer(f"{ce('error')} الكود غير معروف. استخدم CDK.", parse_mode="HTML")
    added_count = 0
    items = lines[1:]
    async with db_pool.acquire() as conn:
        for item in items: 
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
            added_count += 1
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
        product_info = PRODUCTS[product_key]
        broadcast_text = f"{ce('announcement')} <b>Stock Alert!</b>\n━━━━━━━━━━━━━━━━━━━━━\n🔥 New keys have been added for: <b>{product_info['title_en']}</b>\n\n{ce('quantity')} Available Stock: <b>{total}</b>\n⚡ Hurry up and grab yours now before it runs out!"
        users = await conn.fetch("SELECT telegram_id FROM users")
        sent_count = 0
        for u in users:
            try:
                await bot.send_message(u["telegram_id"], broadcast_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}", icon_custom_emoji_id=EMOJI["cart"])]]))
                sent_count += 1
            except Exception: pass
    await message.answer(f"{ce('success')} <b>تمت إضافة {added_count} أكواد!</b>\nالمخزون الكلي: {total}\nتم إرسال إشعار لـ {sent_count} مستخدم.", parse_mode="HTML")

# ━━━━━ 🚀 صفحة منتج ChatGPT 🚀 ━━━━━
@dp.callback_query(F.data == "product_cdk_chatgpt")
@dp.callback_query(F.data.startswith("back_to_prod_"))
async def product_cdk_chatgpt_callback(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("cdk_chatgpt")
    sold_count = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    product = PRODUCTS["cdk_chatgpt"]
    desc = product["desc_en"].replace("✅", ce("success")) if lang == "en" else product["desc_ar"].replace("✅", ce("success"))
    caption = (
        f"{ce('chatgpt')} <b>{product['title_en']}</b>\n━━━━━━━━━━━━━━\n"
        f"{ce('price')} Price: <b>${product['usd']}.00</b>\n"
        f"{ce('stock')} Stock: <b>{count} accounts</b>\n"
        f"{ce('sold')} Sold: <b>{sold_count} accounts</b>\n\n"
        f"<b>Description:</b>\n<blockquote>{ce('quotes')} {desc}</blockquote>"
    )
    try: await call.message.delete()
    except: pass
    try: await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")
    except Exception: await call.message.answer(caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    await call.answer()
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)
    buy_waiting[call.from_user.id] = product_key
    text = f"{ce('pencil')} Enter quantity to buy (1-5):" if lang == "en" else f"{ce('pencil')} أدخل الكمية المراد شراؤها (1-5):"
    await call.message.answer(text, reply_markup=reply_quantity_keyboard(), parse_mode="HTML")

async def receive_custom_quantity(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    product_key = buy_waiting.get(user_id)
    if message.text and ("Cancel" in message.text or "إلغاء" in message.text):
        buy_waiting.pop(user_id, None)
        await message.answer(f"{ce('error')} <b>Cancelled / تم الإلغاء</b>", reply_markup=main_reply_keyboard(lang), parse_mode="HTML")
        await send_home(message)
        return
    try:
        qty = int(message.text.strip())
        if qty <= 0 or qty > 5: raise ValueError
    except ValueError:
        await message.answer(f"{ce('error')} <b>اكتب رقم صحيح بين 1 و 5!</b>", parse_mode="HTML")
        return
    buy_waiting.pop(user_id, None)
    await proceed_to_checkout(message, product_key, qty)

async def proceed_to_checkout(call_obj, product_key: str, qty: int):
    lang = await get_lang(call_obj.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = (f"{ce('checkout')} <b>Checkout</b>\n━━━━━━━━━━━━━━\n\n{ce('quantity')} Quantity: <b>{qty}</b>\n{ce('price')} Total Price: <b>${total_price}</b>\n\nChoose payment method:" if lang == "en" else f"{ce('checkout')} <b>إتمام الشراء</b>\n━━━━━━━━━━━━━━\n\n{ce('quantity')} الكمية: <b>{qty}</b>\n{ce('price')} الإجمالي: <b>{total_price}$</b>\n\nاختار طريقة الدفع:")
    if isinstance(call_obj, Message): await call_obj.answer(text, reply_markup=checkout_payment_buttons(lang, product_key, qty), parse_mode="HTML")
    else: await safe_edit_or_answer(call_obj.message, text, reply_markup=checkout_payment_buttons(lang, product_key, qty))

# ━━━━━ 🚀 الدفع والتحقق التلقائي المحدث 🚀 ━━━━━
@dp.callback_query(F.data.startswith("pay_binance_"))
async def pay_binance_product(call: CallbackQuery):
    await call.answer()
    product_key, qty = call.data.replace("pay_binance_", "").rsplit("_", 1)
    qty, lang = int(qty), await get_lang(call.from_user.id)
    total_price = float(PRODUCTS[product_key]["usd"]) * qty
    
    binance_waiting[call.from_user.id] = {"product_key": product_key, "qty": qty, "amount": total_price}
    
    if lang == "en":
        text = (
            f"Binance ID (tap to copy): <code>{BINANCE_UID}</code>\n"
            f"Amount to transfer: <b>${total_price}</b>\n"
            f"Please send the order ID or off-chain transaction reference after payment for verification."
        )
        btn_text = "Back to main menu"
    else:
        text = (
            f"معرف بينانس (اضغط للنسخ): <code>{BINANCE_UID}</code>\n"
            f"المبلغ المطلوب تحويله: <b>${total_price}</b>\n"
            f"يرجى إرسال رقم المعاملة (Pay ID) أو مرجع المعاملة (Off-chain) بعد الدفع للتحقق."
        )
        btn_text = "العودة للقائمة الرئيسية"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="home_main", icon_custom_emoji_id="5332455502917949981")]
    ])

    await call.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def receive_binance_pay_id(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    info = binance_waiting.get(user_id)
    pay_id = message.text.strip()
    
    if not pay_id.isdigit() or len(pay_id) < 6:
        await message.answer(f"{ce('error')} <b>معرف غير صحيح، يرجى كتابة أرقام الـ Pay ID فقط!</b>", parse_mode="HTML")
        return
        
    loading_msg = await message.answer(f"{ce('loading')} <b>جاري فحص المعاملة تلقائياً عبر بينانس...</b>" if lang=="ar" else f"{ce('loading')} <b>Verifying transaction via Binance...</b>", parse_mode="HTML")
    
    async with db_pool.acquire() as conn:
        duplicate = await conn.fetchval("SELECT id FROM deposits WHERE txid=$1", pay_id)
        if duplicate:
            await loading_msg.edit_text(f"{ce('error')} <b>معذرةً، تم استخدام معرف المعاملة هذا مسبقاً!</b>", parse_mode="HTML")
            return
            
        success = await check_binance_payment_via_api(pay_id, info["amount"])
        
        if success:
            product = PRODUCTS[info["product_key"]]
            qty = info["qty"]
            items = await conn.fetch("SELECT id FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
            
            if len(items) < qty:
                await loading_msg.edit_text(f"{ce('error')} <b>نفذت الكمية من المخزون حالياً، يرجى مراسلة الدعم لشحن حسابك يدوياً!</b>", parse_mode="HTML")
                return
                
            await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
            await conn.execute("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, quantity, txid, status) VALUES($1,$2,$3,$4,$5,$6,$7,'approved')", user_id, "binance_auto", info["amount"], "USDT", info["product_key"], qty, pay_id)
            
            binance_waiting.pop(user_id, None)
            await loading_msg.delete()
            await message.answer(get_delivery_text(lang, product, qty, SUPPORT), parse_mode="HTML")
            
            await bot.send_message(ADMIN_ID, f"⚡ <b>بيع تلقائي ناجح عبر الـ API!</b>\nالمستخدم: @{message.from_user.username}\nالمنتج: {product['title_en']}\nالكمية: {qty}\nالمبلغ: {info['amount']} USDT\nرقم المعاملة: <code>{pay_id}</code>", parse_mode="HTML")
        else:
            if lang == "ar":
                error_text = (
                    f"{ce('error')} <b>لم نجد المعاملة بعد</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"<blockquote>{ce('quotes')} {ce('search')} <b>عذراً، لم نتمكن من العثور على أي تحويل بهذا المعرف في حسابنا حتى الآن.</b></blockquote>\n\n"
                    f"{ce('announcement')} <b>يرجى التأكد من الآتي:</b>\n"
                    f"{ce('arrow_right')} هل كتبت رقم الـ Pay ID بشكل صحيح؟\n"
                    f"{ce('arrow_right')} هل قمت بتحويل المبلغ المطلوب بالكامل؟\n\n"
                    f"{ce('hourglass')} <i>فضلاً انتظر دقيقة ثم أرسل رقم المعاملة مرة أخرى للمحاولة.</i>"
                )
                btn_text = "العودة للقائمة الرئيسية"
            else:
                error_text = (
                    f"{ce('error')} <b>Payment Not Found</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"<blockquote>{ce('quotes')} {ce('search')} <b>We haven't received any transfer with this ID in our system just yet.</b></blockquote>\n\n"
                    f"{ce('announcement')} <b>Please double check:</b>\n"
                    f"{ce('arrow_right')} Did you copy the exact correct Pay ID?\n"
                    f"{ce('arrow_right')} Did you send the full required amount?\n\n"
                    f"{ce('hourglass')} <i>Kindly wait a minute and submit the ID again to re-verify.</i>"
                )
                btn_text = "Back to main menu"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=btn_text, callback_data="home_main", icon_custom_emoji_id="5332455502917949981")]
            ])
            
            await loading_msg.edit_text(error_text, reply_markup=keyboard, parse_mode="HTML")

# ━━━━━ باقي قنوات العرض ━━━━━

# 🟢 إضافة زرار اللغة هنا 🟢
@dp.callback_query(F.data == "home_language")
async def language_screen_callback(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    text = "🌐 <b>Choose your language:</b>" if lang == "en" else "🌐 <b>اختر لغتك المفضلة:</b>"
    await safe_edit_or_answer(call.message, text, reply_markup=language_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_language_callback(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await call.answer("Language changed successfully!" if lang == "en" else "تم تغيير اللغة بنجاح!")
    
    msg = await animate_message(call.message, lang)
    await safe_edit_or_answer(msg, home_text(lang, call.from_user.first_name or "User"), reply_markup=home_keyboard(lang))
    await call.message.answer("Main Menu" if lang == "en" else "القائمة الرئيسية", reply_markup=main_reply_keyboard(lang))

@dp.callback_query(F.data == "home_deposit")
async def deposit_inline_screen(call: CallbackQuery):
    await call.answer()
    await safe_edit_or_answer(call.message, f"{ce('wallet')} <b>إيداع الأموال</b>\nاختر العملة:", reply_markup=deposit_currency_buttons(await get_lang(call.from_user.id)))

@dp.callback_query(F.data == "home_share")
async def referral_screen(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={call.from_user.id}"
    stats = await get_user_stats(call.from_user.id)
    total_ref = stats["total_ref"] if stats else 0
    earnings = total_ref * REFERRAL_REWARD
    if lang == "en":
        text = f"""{ce('share')} <b>Share & Earn Free USDT!</b>\n━━━━━━━━━━━━━━━━━━━━━\nInvite your friends to use the bot and earn <b>{REFERRAL_REWARD} USDT</b> instantly inside your wallet for every successful invite!\n\n{ce('users_group')} Your Total Invites: <b>{total_ref} users</b>\n{ce('money_fly')} Total Earned: <b>{format_amount(earnings)} USDT</b>\n\n{ce('link_pin')} <b>Your Exclusive Referral Link:</b>\n<code>{ref_link}</code>\n\n<i>Copy the link and share it in groups to start earning!</i>"""
    else:
        text = f"""{ce('share')} <b>انشر البوت وابني أرباح مجانية!</b>\n━━━━━━━━━━━━━━━━━━━━━\nانسخ رابط الإحالة الخاص بك وانشره؛ لكل شخص يدخل البوت عن طريقك هتكسب <b>{REFERRAL_REWARD} USDT</b> فوراً جوه محفظتك تقدر تشتري بيها أي منتج!\n\n{ce('users_group')} عدد إحالاتك الحالي: <b>{total_ref} عضو</b>\n{ce('money_fly')} إجمالي ما كسبته: <b>{format_amount(earnings)} USDT</b>\n\n{ce('link_pin')} <b>رابط الإحالة الحصري الخاص بك:</b>\n<code>{ref_link}</code>\n\n<i>اضغط على الرابط لنسخه وانشره في الجروبات لتبدأ الأرباح!</i>"""
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard(lang))

@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    stats = await get_user_stats(call.from_user.id)
    balance = stats["balance_usdt"] if stats else 0.0
    total_ref = stats["total_ref"] if stats else 0
    msg = await animate_message(call.message, lang)
    if lang == "en":
        text = f"""{ce('wallet')} <b>AIX USER PROFILE & WALLET</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('user')} Name: <b>{esc(call.from_user.first_name)}</b>\n{ce('price')} Wallet Balance: <b>{balance} USDT</b>\n\n{ce('users_group')} Total Invited Users: <b>{total_ref} friends</b>\n{ce('money_fly')} Referral Earnings: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('checkout')} You can deposit funds or use your referral balance to purchase instantly."""
    else:
        text = f"""{ce('wallet')} <b>ملف الحساب ومحفظة AIX</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('user')} الحساب: <b>{esc(call.from_user.first_name)}</b>\n{ce('price')} رصيد المحفظة الحالي: <b>{balance} USDT</b>\n\n{ce('users_group')} إجمالي الإحالات الخاصة بك: <b>{total_ref} عضو</b>\n{ce('money_fly')} أرباحك من الإحالات: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('checkout')} تقدر تشحن محفظتك يدوياً أو تستخدم أرباح إحالاتك للشراء الفوري مباشرةً."""
    await safe_edit_or_answer(msg, text, reply_markup=wallet_kb(lang))

@dp.callback_query(F.data == "home_main")
async def home_main(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
    await safe_edit_or_answer(msg, home_text(lang, call.from_user.first_name or "User"), reply_markup=home_keyboard(lang))

@dp.callback_query(F.data == "home_shop")
async def shop_inline_callback(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message, await get_lang(call.from_user.id))
    await handle_shop_action(msg, await get_lang(call.from_user.id))

@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id
    
    if user_id in binance_waiting:
        await receive_binance_pay_id(message)
        return
    if user_id in buy_waiting:
        await receive_custom_quantity(message)
        return
        
    text_value = message.text.strip()
    if text_value.startswith("/"): return

    if text_value in ["🛍 Products", "🛍 المنتجات"]:
        lang = await get_lang(user_id)
        msg = await animate_message(message, lang)
        await handle_shop_action(msg, lang)
    elif text_value in ["🎧 Support", "🎧 الدعم"]:
        lang = await get_lang(user_id)
        support_text = f"{ce('support_msg')} <b>الدعم السريع:</b>\n\n{ce('telegram')} <b>تليجرام:</b> {ce('arrow_right')} {SUPPORT}\n\nتواصل معنا للحصول على مساعدة أسرع وحل المشاكل." if lang == "ar" else f"{ce('support_msg')} <b>Quick support:</b>\n\n{ce('telegram')} <b>Telegram:</b> {ce('arrow_right')} {SUPPORT}\n\nContact us for faster help and issue handling."
        await message.answer(support_text, reply_markup=back_home_keyboard(lang), parse_mode="HTML")
    elif text_value in ["💰 Wallet", "💰 المحفظة"]:
        class FakeCall:
            def __init__(self, message, from_user): self.message, self.from_user = message, from_user 
            async def answer(self, *args, **kwargs): pass
        await wallet_inline(FakeCall(message, message.from_user))
    elif text_value in ["🎁 Share & Earn", "🎁 الإحالات"]:
        class FakeCall:
            def __init__(self, message, from_user): self.message, self.from_user = message, from_user 
            async def answer(self, *args, **kwargs): pass
        await referral_screen(FakeCall(message, message.from_user))
    else:
        await send_home(message)

async def main():
    await init_db()
    await bot.set_my_commands([BotCommand(command="start", description="Start"), BotCommand(command="menu", description="Menu")])
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())
