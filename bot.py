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
    ReplyKeyboardRemove,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"
REFERRAL_REWARD = 0.10  

AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

# ━━━━━ قواميس الإيموجيات المعتمدة ━━━━━
EMOJI = {
    "announcement": "5424818078833715060",  
    "vip": "6088920147072915408",           
    "verified": "5976653524476368012",       
    "lightning": "5440621591387980068",      
    "heart": "5364201435858744869",          
    "wallet": "6088990159334808217",         
    "telegram": "6089099509202164251",       
    "arrows_down": "5443038326535759644",    
    "pencil": "5395444784611480792",         
    "quotes": "6181467651395558500", # إيموجي علامتي التنصيص المتحرك للديسكربشن
    "store": "5859297284029681680", "support": "6181322172263308706",
    "language": "5447410659077661506", "home": "5195140682590722632",
    "chatgpt": "5864127571754489150", "stock": "6089247294731852091", 
    "shield": "5251203410396458957", "link": "5282843764451195532", 
    "step": "5397782960512444700", "rocket": "6181682949516173646",
    "success": "5976653524476368012", "refresh": "5341715473882955310", 
    "payment": "5352662091390008496", "binance": "6222208096257712941", 
    "fire": "6266887773454603583", "stock_add": "5397916757333654639", 
    "trash": "5445267414562389170", "error": "6181467651395558500", 
    "arrows_up": "5449683594425410231", "bell": "5458603043203327669", 
    "hundred": "6181303849932823189", "loading": "6089327236958132324",
}

SAFE_EMOJI_FALLBACK = {
    "store": "🛍", "wallet": "💰", "support": "🎧", "telegram": "✈️",
    "language": "🌐", "home": "🏠", "chatgpt": "🤖", "stock": "📦",
    "shield": "🛡", "link": "🔗", "step": "🔹", "rocket": "🚀",
    "success": "✅", "refresh": "🔄", "lightning": "⚡", "payment": "💳",
    "binance": "🟡", "fire": "🔥", "announcement": "📢", "stock_add": "➕",
    "trash": "🗑", "error": "❌", "arrows_up": "⬆️", "arrows_down": "⬇️",
    "bell": "🔔", "hundred": "💯", "vip": "⭐", "verified": "☑️", "heart": "❤️",
    "loading": "⏳", "pencil": "✍️", "quotes": "💬"
}

def ce(key: str, fallback: str = "") -> str:
    emoji_id = EMOJI.get(key)
    safe_fallback = SAFE_EMOJI_FALLBACK.get(key, fallback or "✅")
    if not emoji_id or not str(emoji_id).isdigit(): return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'

def esc(value) -> str: return html.escape(str(value), quote=False)
def strip_custom_emoji(text: str) -> str: return re.sub(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r'\1', text)

async def safe_answer(message: Message, text: str, reply_markup=None):
    try: return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest: return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")

async def safe_edit_or_answer(message, text: str, reply_markup=None):
    try: return await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest:
        try: return await message.edit_text(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
        except Exception: return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
    except Exception: return await safe_answer(message, text, reply_markup)

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

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title_en": "CDK GPT Plus (K12 - EDU) 1 year No warranty",
        "title_ar": "CDK GPT Plus (K12 - EDU) 1 year No warranty",
        "image": CDK_IMAGE_FILE,
        "usd": 9,
        "type": "stock",
        "desc_en": "✅ ChatGPT K12 Edu 1 year package.\nFull of latest languages like Plus\n✅ Can activate any account owner. Only applies to Gmail or hotmail, outlook\n✅ After ordering, you will receive a code\n✅ Account is on free plan\n✅ Recommended to use an account without an active subscription or a newly created account to register.\n✅ Web upgrade CDK: http://gpt.ddfafa.com",
        "desc_ar": "✅ باقة ChatGPT K12 المخصصة للتعليم لمدة سنة كاملة.\nتحتوي على أحدث المميزات واللغات مثل حسابات بلس تماماً.\n✅ تقبل التفعيل على أي حساب، وتطبق على إيميلات جيمل، هوتميل، وأوتلوك.\n✅ بعد الطلب والدفع، ستتلقى كود التفعيل فوراً.\n✅ الحساب يجب أن يكون على الخطة المجانية الحالية.\n✅ يوصى باستخدام حساب ليس به اشتراك نشط أو حساب جديد تماماً للتسجيل.\n✅ موقع ترقية وتفعيل الكود: http://gpt.ddfafa.com"
    }
}

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
        await conn.execute("CREATE TABLE IF NOT EXISTS deposits (id SERIAL PRIMARY KEY, telegram_id BIGINT, method TEXT, amount NUMERIC, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', quantity INT DEFAULT 1, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS quantity INT DEFAULT 1;")
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
                    try: await bot.send_message(referrer_id, f"🎁 <b>New Referral!</b>\n━━━━━━━━━━━━━━\nSomeone joined via your link! <b>+{REFERRAL_REWARD} USDT</b> has been added to your wallet.", parse_mode="HTML")
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
        return f"""{ce('verified','✅')} <b>Payment Confirmed Successfully!</b>\n━━━━━━━━━━━━━━━━━━━━━\n{ce('vip','👑')} <b>{product['title_en']}</b>\n\n📦 <b>Quantity:</b> {qty}\n\n{ce('announcement','📢')} <b>How to receive your codes:</b>\nPlease contact the admin directly to receive your keys instantly! Send a screenshot of this message to the admin below.\n💬 <b>Contact Admin:</b> {support}\n\n━━━━━━━━━━━━━━━━━━━━━\n{ce('heart','❤️')} <b>Thank you for trusting AIX Store!</b>"""
    else:
        return f"""{ce('verified','✅')} <b>تم تأكيد الدفع وتسليم طلبك بنجاح!</b>\n━━━━━━━━━━━━━━━━━━━━━\n{ce('vip','👑')} <b>{product['title_ar']}</b>\n\n📦 <b>الكمية المطلوبة:</b> {qty}\n\n{ce('announcement','📢')} <b>لاستلام الأكواد الخاصة بك:</b>\nبرجاء التواصل مع الإدارة لاستلام الأكواد فوراً. يرجى إرسال سكرين شوت لهذه الرسالة كإثبات لطلبك!\n💬 <b>تواصل مع الإدارة:</b> {support}\n\n━━━━━━━━━━━━━━━━━━━━━\n{ce('heart','❤️')} <b>شكراً لثقتك في AIX Store!</b>"""

# ━━━━━ كيبورد الأرقام اللي بيظهر تحت في الكمية بديل للإنلاين ━━━━━
def reply_quantity_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5")],
        [KeyboardButton(text="❌ Cancel / إلغاء")]
    ], resize_keyboard=True, one_time_keyboard=True)

def home_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Browse Products" if lang=="en" else "تصفح المنتجات", callback_data="home_shop")],
        [InlineKeyboardButton(text="Deposit" if lang=="en" else "إيداع", callback_data="home_deposit"), InlineKeyboardButton(text="Wallet / Profile" if lang=="en" else "المحفظة والحساب", callback_data="home_wallet")],
        [InlineKeyboardButton(text="Support" if lang=="en" else "الدعم", callback_data="home_support"), InlineKeyboardButton(text="🎁 Share & Earn" if lang=="en" else "🎁 نشر وبناء أرباح", callback_data="home_share")],
        [InlineKeyboardButton(text="Language" if lang=="en" else "اللغة", callback_data="home_language")]
    ])

def back_home_keyboard(lang: str): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Main Menu" if lang == "en" else "القائمة الرئيسية", callback_data="home_main")]])

def product_buttons(lang: str, counts: dict):
    if lang == "en": return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"CDK GPT Plus 1Y | $9 | Stock {counts.get('cdk_chatgpt', 0)}", callback_data="product_cdk_chatgpt")], [InlineKeyboardButton(text="Refresh", callback_data="refresh_products"), InlineKeyboardButton(text="Back", callback_data="home_main")]])
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"CDK GPT Plus 1Y | 9$ | المتاح {counts.get('cdk_chatgpt', 0)}", callback_data="product_cdk_chatgpt")], [InlineKeyboardButton(text="تحديث", callback_data="refresh_products"), InlineKeyboardButton(text="رجوع", callback_data="home_main")]])

def product_details_buttons(lang: str, product_key: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy Now" if lang == "en" else "شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="Back to Shop" if lang == "en" else "رجوع للمتجر", callback_data="home_shop")]
    ])

def checkout_payment_buttons(lang: str, product_key: str, qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pay from Wallet" if lang=="en" else "💰 الدفع من المحفظة", callback_data=f"pay_wallet_{product_key}_{qty}")],
        [InlineKeyboardButton(text="🟡 Pay via Binance UID" if lang=="en" else "🟡 الدفع عبر بينانس UID", callback_data=f"pay_binance_{product_key}_{qty}")],
        [InlineKeyboardButton(text="Back" if lang=="en" else "رجوع", callback_data=f"back_to_prod_{product_key}")]
    ])

def deposit_currency_buttons(lang: str): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="USDT Deposit" if lang == "en" else "إيداع بالدولار USDT", callback_data="deposit_currency_USDT")], [InlineKeyboardButton(text="Back" if lang == "en" else "رجوع", callback_data="home_main")]])
def deposit_amount_payment_buttons(lang: str, amount: float, currency: str): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🟡 Binance UID • {format_amount(amount)} USDT", callback_data=f"topup_binance_{format_amount(amount)}_USDT")], [InlineKeyboardButton(text="Change Amount" if lang == "en" else "تغيير المبلغ", callback_data="deposit_currency_USDT")]])
def language_keyboard(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")], [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]])
def wallet_kb(lang: str): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="إيداع" if lang=="ar" else "Deposit", callback_data="home_deposit")], [InlineKeyboardButton(text="تحديث" if lang=="ar" else "Refresh", callback_data="home_wallet"), InlineKeyboardButton(text="الرئيسية" if lang=="ar" else "Main Menu", callback_data="home_main")]])

def main_reply_keyboard(lang: str):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Products" if lang=="en" else "🛍 المنتجات"), KeyboardButton(text="🎧 Support" if lang=="en" else "🎧 الدعم")], 
        [KeyboardButton(text="💰 Wallet" if lang=="en" else "💰 المحفظة"), KeyboardButton(text="🎁 Share & Earn" if lang=="en" else "🎁 الإحالات")],
        [KeyboardButton(text="🌐 Language" if lang=="en" else "🌐 اللغة")]
    ], resize_keyboard=True, is_persistent=True)

MENU_TEXTS = {"🛍 Products", "Products", "🛍 المنتجات", "المنتجات", "🎧 Support", "Support", "🎧 الدعم", "الدعم", "💰 Wallet", "Wallet", "💰 المحفظة", "المحفظة", "🌐 Language", "Language", "🌐 اللغة", "اللغة", "🎁 Share & Earn", "🎁 الإحالات"}

def home_text(lang: str, name: str):
    if lang == "en": return f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{esc(name)}</b>\nWelcome to your premium AI subscriptions store.\n\n{ce('store','🛍')} <b>Shop</b> — Browse & buy products\n{ce('wallet','💰')} <b>Deposit</b> — Add funds to your wallet\n{ce('support','🎧')} <b>Support</b> — Get help anytime\n\n{ce('lightning','⚡')} Fast activation • Secure payments • Trusted service"
    return f"{ce('vip','⭐')} <b>AIX Store</b> {ce('verified','✅')}\n━━━━━━━━━━━━━━━━━━\n\nأهلاً، <b>{esc(name)}</b>\nنورت متجر اشتراكات الذكاء الاصطناعي المميزة.\n\n{ce('store','🛍')} <b>المتجر</b> — تصفح واشتري المنتجات\n{ce('wallet','💰')} <b>إيداع</b> — إضافة رصيد للمحفظة\n{ce('support','🎧')} <b>الدعم</b> — مساعدة في أي وقت\n\n{ce('lightning','⚡')} تفعيل سريع • دفع آمن • خدمة موثوقة"

def product_list_text(lang: str):
    if lang == "en": return f"{ce('store','🛍')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\nPrice: $9 | Subscription: 1 Year, no warranty {ce('error','❌')}\n\n{ce('arrows_down','⬇️')} Choose a product below:"
    return f"{ce('store','🛍')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('hundred','💯')} <b>CDK Activation Chatgpt For 1 year</b>\nالسعر: 9$ | الاشتراك سنه ، no warranty {ce('error','❌')}\n\n{ce('arrows_down','⬇️')} اختار المنتج من الأزرار:"

async def animate_message(message: Message, lang: str):
    text = f"{ce('loading', '⏳')} <b>Loading...</b>" if lang == "en" else f"{ce('loading', '⏳')} <b>جاري التحميل...</b>"
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
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit(): referrer_id = int(args[1])
    await ensure_user_by_id(message.from_user.id, message.from_user.username, message.from_user.first_name, referrer_id)
    await send_home(message)

@dp.message(Command("menu"))
async def menu_command(message: Message): await start(message)

# ━━━━━ 🚀 أوامر الإدارة من الشات مباشرة 🚀 ━━━━━
@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID: return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2: 
        await message.answer("❌ <b>خطأ! استخدم الصيغة دي (في رسالة واحدة):</b>\n\n<code>/addstock CDK</code>\n<code>الكود_الأول</code>\n<code>الكود_الثاني</code>", parse_mode="HTML")
        return
        
    product_key, stock_name = resolve_stock_product(lines[0])
    if not stock_name:
        await message.answer("❌ الكود غير معروف. استخدم `CDK`.", parse_mode="HTML")
        return

    added_count = 0
    items = lines[1:]
    
    async with db_pool.acquire() as conn:
        for item in items: 
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
            added_count += 1
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
        
        product_info = PRODUCTS[product_key]
        broadcast_text = f"📢 <b>Stock Alert!</b>\n━━━━━━━━━━━━━━━━━━━━━\n🔥 New keys have been added for: <b>{product_info['title_en']}</b>\n\n📦 Available Stock: <b>{total}</b>\n⚡ Hurry up and grab yours now before it runs out!"
        
        users = await conn.fetch("SELECT telegram_id FROM users")
        sent_count = 0
        for u in users:
            try:
                await bot.send_message(
                    u["telegram_id"], 
                    broadcast_text, 
                    parse_mode="HTML", 
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}")]])
                )
                sent_count += 1
            except Exception: pass

    await message.answer(f"✅ <b>تمت إضافة {added_count} أكواد!</b>\nالمخزون الكلي: {total}\nتم إرسال إشعار لـ {sent_count} مستخدم.", parse_mode="HTML")

@dp.message(Command("liststock"))
async def list_stock(message: Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/liststock CDK`", parse_mode="Markdown")
    product_key, stock_name = resolve_stock_product(args[1])
    if not stock_name: return await message.answer("❌ Unknown product.")
    async with db_pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
    await message.answer(f"📦 المتاح لـ {stock_name}: <b>{total}</b> كود", parse_mode="HTML")

@dp.message(Command("clearstock"))
async def clear_stock(message: Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/clearstock CDK`", parse_mode="Markdown")
    product_key, stock_name = resolve_stock_product(args[1])
    if not stock_name: return await message.answer("❌ Unknown product.")
    async with db_pool.acquire() as conn:
        deleted = await conn.execute("DELETE FROM stock WHERE product=$1 AND sold=false", stock_name)
        try: n = int(deleted.split()[-1])
        except: n = deleted
    await message.answer(f"🗑 تم مسح {n} أكواد غير مباعة من {stock_name}.", parse_mode="HTML")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/broadcast", "", 1).strip()
    if not text: return await message.answer("Usage: `/broadcast رسالتك هنا`", parse_mode="Markdown")
    async with db_pool.acquire() as conn: users = await conn.fetch("SELECT telegram_id FROM users")
    sent = 0
    for u in users:
        try:
            await bot.send_message(u["telegram_id"], f"📢 <b>تنبيه من الإدارة:</b>\n\n{esc(text)}", parse_mode="HTML")
            sent += 1
        except Exception: pass
    await message.answer(f"✅ تم إرسال الرسالة إلى {sent} مستخدم.")

@dp.message(Command("broadcastphoto"))
async def cmd_broadcastphoto(message: Message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.answer("❌ لازم تعمل **Reply** على رسالة فيها صورة وتكتب `/broadcastphoto`")
    caption = message.text.replace("/broadcastphoto", "", 1).strip()
    if not caption: caption = message.reply_to_message.caption or ""
    photo_id = message.reply_to_message.photo[-1].file_id
    async with db_pool.acquire() as conn: users = await conn.fetch("SELECT telegram_id FROM users")
    sent = 0
    for u in users:
        try:
            await bot.send_photo(u["telegram_id"], photo=photo_id, caption=caption, parse_mode="HTML")
            sent += 1
        except Exception: pass
    await message.answer(f"✅ تم إرسال الصورة إلى {sent} مستخدم.")

# ━━━━━ عرض المنتج بتنسيق كوبي بيست بوكس الاقتباس والإيموجي المتحرك ━━━━━
@dp.callback_query(F.data == "product_cdk_chatgpt")
@dp.callback_query(F.data.startswith("back_to_prod_"))
async def product_cdk_chatgpt_callback(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("cdk_chatgpt")
    product = PRODUCTS["cdk_chatgpt"]
    desc = product["desc_en"] if lang == "en" else product["desc_ar"]
    
    caption = (
        f"🤖 <b>{product['title_en']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Price: <b>${product['usd']}.00</b>\n"
        f"🔋 Stock: <b>{count} accounts</b>\n"
        f"📊 Sold: <b>176 accounts</b>\n\n"
        f"{ce('quotes', '💬')} <b>Description:</b>\n"
        f"<blockquote>{desc}</blockquote>"
    )
    try: await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")
    except Exception: await call.message.answer(caption, reply_markup=product_details_buttons(lang, "cdk_chatgpt"), parse_mode="HTML")

# ━━━━━ طلب الكمية بالكيبورد السفلي ━━━━━
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
        await message.answer("❌ Cancelled / تم الإلغاء", reply_markup=main_reply_keyboard(lang))
        await send_home(message)
        return
        
    try:
        qty = int(message.text.strip())
        if qty <= 0: raise ValueError
    except ValueError:
        await message.answer("❌ اكتب رقم صحيح أو اختر من الأزرار!")
        return
        
    buy_waiting.pop(user_id, None)
    await message.answer("🔄 Processing Checkout..." if lang=="en" else "🔄 جاري تجهيز الفاتورة...", reply_markup=main_reply_keyboard(lang))
    await proceed_to_checkout(message, product_key, qty)

async def proceed_to_checkout(call_obj, product_key: str, qty: int):
    lang = await get_lang(call_obj.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = (f"💳 <b>Checkout</b>\n━━━━━━━━━━━━━━\n\n📦 Quantity: <b>{qty}</b>\n💰 Total Price: <b>${total_price}</b>\n\nChoose payment method:" if lang == "en" else f"💳 <b>إتمام الشراء</b>\n━━━━━━━━━━━━━━\n\n📦 الكمية: <b>{qty}</b>\n💰 الإجمالي: <b>{total_price}$</b>\n\nاختار طريقة الدفع:")
    
    if isinstance(call_obj, Message):
        await call_obj.answer(text, reply_markup=checkout_payment_buttons(lang, product_key, qty), parse_mode="HTML")
    else:
        await safe_edit_or_answer(call_obj.message, text, reply_markup=checkout_payment_buttons(lang, product_key, qty))

# ━━━━━ الدفع الفوري من المحفظة (خصم المخزون والتحويل للأدمن) ━━━━━
@dp.callback_query(F.data.startswith("pay_wallet_"))
async def pay_wallet_product(call: CallbackQuery):
    await call.answer()
    product_key, qty = call.data.replace("pay_wallet_", "").rsplit("_", 1)
    qty, lang = int(qty), await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty

    async with db_pool.acquire() as conn:
        balance = await get_wallet_balance(call.from_user.id)
        if balance < total_price:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Deposit Now" if lang=="en" else "إيداع الآن", callback_data="home_deposit")], [InlineKeyboardButton(text="Back", callback_data=f"back_to_prod_{product_key}")]])
            await safe_edit_or_answer(call.message, f"❌ <b>Insufficient Balance!</b>\nRequired: {total_price} USDT\nYour Balance: {balance} USDT" if lang=="en" else f"❌ <b>رصيدك غير كافي!</b>\nالمطلوب: {total_price} USDT\nرصيدك: {balance} USDT", reply_markup=kb)
            return
        
        items = await conn.fetch("SELECT id FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
        if len(items) < qty: 
            await safe_edit_or_answer(call.message, "Out of stock ❌" if lang == "en" else "المخزون نفذ أو غير كافي ❌")
            return
            
        await conn.execute("UPDATE users SET balance_usdt = balance_usdt - $1 WHERE telegram_id=$2", total_price, call.from_user.id)
        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        
        await safe_edit_or_answer(call.message, get_delivery_text(lang, product, qty, SUPPORT))
        await bot.send_message(ADMIN_ID, f"🛒 <b>Wallet Sale!</b>\nUser: @{call.from_user.username}\nProduct: {product['title_en']}\nQty: {qty}\nTotal: {total_price} USDT\n\n⚠️ العميل دفع بنجاح وهيراسل لك خاص للاستلام الكود الفوري.", parse_mode="HTML")

@dp.callback_query(F.data.startswith("pay_binance_"))
async def pay_binance_product(call: CallbackQuery):
    await call.answer()
    product_key, qty = call.data.replace("pay_binance_", "").rsplit("_", 1)
    qty, lang = int(qty), await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    async with db_pool.acquire() as conn: dep_id = await conn.fetchval("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, quantity) VALUES($1,$2,$3,$4,$5,$6) RETURNING id", call.from_user.id, "binance", total_price, "USDT", product_key, qty)
    await bot.send_message(ADMIN_ID, f"🛒 Order #{dep_id}\nUser: @{call.from_user.username}\nQty: {qty}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]]))
    await safe_edit_or_answer(call.message, f"🟡 Binance UID: <code>{BINANCE_UID}</code>\n💰 Amount: {total_price} USDT\n📸 Send screenshot proof here. ID: #{dep_id}" if lang=="en" else f"🟡 بينانس UID: <code>{BINANCE_UID}</code>\n💰 المبلغ: {total_price} USDT\n📸 ابعت صورة الإثبات هنا. رقم الطلب: #{dep_id}")

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    await call.answer()
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if not dep or dep["status"] != "pending": return await safe_edit_or_answer(call.message, "Already handled")
        user_lang = await get_lang(dep["telegram_id"])
        product_key = dep["product_key"]
        if product_key == WALLET_DEPOSIT_KEY:
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", dep["amount"], dep["telegram_id"])
            await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], f"✅ Deposit approved! Added {dep['amount']} USDT." if user_lang=="en" else f"✅ تم قبول الإيداع وإضافة {dep['amount']} USDT.", parse_mode="HTML")
            await safe_edit_or_answer(call.message, f"✅ Wallet Deposit #{dep_id} Approved")
            return
        
        product = PRODUCTS[product_key]
        qty = dep["quantity"]
        items = await conn.fetch("SELECT id FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
        if len(items) < qty: return await safe_edit_or_answer(call.message, "❌ لا يوجد مخزون كافي")
        
        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
        await bot.send_message(dep["telegram_id"], get_delivery_text(user_lang, product, qty, SUPPORT), parse_mode="HTML")
    await safe_edit_or_answer(call.message, f"✅ Order #{dep_id} Approved")

# ━━━━━ باقي الخدمات المساعدة ━━━━━
@dp.callback_query(F.data == "home_deposit")
async def deposit_inline_screen(call: CallbackQuery):
    await call.answer()
    await safe_edit_or_answer(call.message, deposit_intro_text(await get_lang(call.from_user.id)), reply_markup=deposit_currency_buttons(await get_lang(call.from_user.id)))

@dp.callback_query(F.data == "deposit_currency_USDT")
async def deposit_usdt(call: CallbackQuery):
    await call.answer()
    deposit_waiting[call.from_user.id] = "USDT"
    await safe_edit_or_answer(call.message, "Type deposit amount in USDT (Min: 5):" if await get_lang(call.from_user.id)=="en" else "اكتب مبلغ الإيداع بالدولار (أقل شيء 5):", reply_markup=back_home_keyboard(await get_lang(call.from_user.id)))

async def receive_deposit_amount(message: Message):
    lang = await get_lang(message.from_user.id)
    try:
        amount = float(message.text.strip())
        if amount < 5: raise ValueError
    except ValueError:
        await message.answer("❌ اكتب رقم صحيح أكبر من أو يساوي 5!")
        return
    deposit_waiting.pop(message.from_user.id, None)
    await message.answer(f"🟡 Binance UID: <code>{BINANCE_UID}</code>\n💰 Amount: {amount} USDT" if lang=="en" else f"🟡 بينانس UID: <code>{BINANCE_UID}</code>\n💰 المبلغ: {amount} USDT", reply_markup=deposit_amount_payment_buttons(lang, amount, "USDT"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("topup_"))
async def topup_wallet(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    async with db_pool.acquire() as conn: dep_id = await conn.fetchval("INSERT INTO deposits (telegram_id, method, amount, currency, product_key) VALUES($1,$2,$3,$4,$5) RETURNING id", call.from_user.id, "binance", amount, "USDT", WALLET_DEPOSIT_KEY)
    await bot.send_message(ADMIN_ID, f"💳 Wallet Deposit #{dep_id}\nAmount: {amount} USDT", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{dep_id}"), InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")]]))
    await safe_edit_or_answer(call.message, f"📸 Send proof for Deposit #{dep_id}" if await get_lang(call.from_user.id)=="en" else f"📸 ابعت صورة الإثبات لرقم الشحن #{dep_id}")

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
        text = f"""🎁 <b>Share & Earn Free USDT!</b>\n━━━━━━━━━━━━━━━━━━━━━\nInvite your friends to use the bot and earn <b>{REFERRAL_REWARD} USDT</b> instantly inside your wallet for every successful invite!\n\n👥 Your Total Invites: <b>{total_ref} users</b>\n💰 Total Earned: <b>{format_amount(earnings)} USDT</b>\n\n🔗 <b>Your Exclusive Referral Link:</b>\n<code>{ref_link}</code>\n\n<i>Copy the link and share it in groups to start earning!</i>"""
    else:
        text = f"""🎁 <b>انشر البوت وابني أرباح مجانية!</b>\n━━━━━━━━━━━━━━━━━━━━━\nانسخ رابط الإحالة الخاص بك وانشره؛ لكل شخص يدخل البوت عن طريقك هتكسب <b>{REFERRAL_REWARD} USDT</b> فوراً جوه محفظتك تقدر تشتري بيها أي منتج!\n\n👥 عدد إحالاتك الحالي: <b>{total_ref} عضو</b>\n💰 إجمالي ما كسبته: <b>{format_amount(earnings)} USDT</b>\n\n🔗 <b>رابط الإحالة الحصري الخاص بك:</b>\n<code>{ref_link}</code>\n\n<i>اضغط على الرابط لنسخه وانشره في الجروبات لتبدأ الأرباح!</i>"""
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
        text = f"""{ce('wallet','💰')} <b>AIX USER PROFILE & WALLET</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 Name: <b>{esc(call.from_user.first_name)}</b>\n💵 Wallet Balance: <b>{balance} USDT</b>\n\n👥 Total Invited Users: <b>{total_ref} friends</b>\n🎁 Referral Earnings: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('payment','💳')} You can deposit funds or use your referral balance to purchase instantly."""
    else:
        text = f"""{ce('wallet','💰')} <b>ملف الحساب ومحفظة AIX</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 الحساب: <b>{esc(call.from_user.first_name)}</b>\n💵 رصيد المحفظة الحالي: <b>{balance} USDT</b>\n\n👥 إجمالي الإحالات الخاصة بك: <b>{total_ref} عضو</b>\n🎁 أرباحك من الإحالات: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('payment','💳')} تقدر تشحن محفظتك يدوياً أو تستخدم أرباح إحالاتك للشراء الفوري مباشرةً."""
    await safe_edit_or_answer(msg, text, reply_markup=wallet_kb(lang))

@dp.callback_query(F.data == "home_main")
async def home_main(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    msg = await animate_message(call.message, lang)
    await safe_edit_or_answer(msg, home_text(lang, call.from_user.first_name or "User"), reply_markup=home_keyboard(lang))

@dp.callback_query(F.data == "home_language")
async def home_language(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    await safe_edit_or_answer(call.message, f"{ce('language','🌐')} Choose language:" if lang == "en" else f"{ce('language','🌐')} اختر اللغة:", reply_markup=language_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    await call.answer()
    lang = call.data.replace("lang_", "")
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await safe_edit_or_answer(call.message, f"{ce('verified','✅')} Language changed to English" if lang == "en" else f"{ce('verified','✅')} تم تغيير اللغة للعربية", reply_markup=home_keyboard(lang))

@dp.callback_query(F.data == "home_shop")
async def shop_inline_callback(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message, await get_lang(call.from_user.id))
    await handle_shop_action(msg, await get_lang(call.from_user.id))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    await call.answer("Updated ✅")
    msg = await animate_message(call.message, await get_lang(call.from_user.id))
    await handle_shop_action(msg, await get_lang(call.from_user.id))

@dp.callback_query(F.data.startswith("reject_"))
async def reject_order(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    await call.answer()
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], "❌ Order rejected." if await get_lang(dep["telegram_id"])=="en" else "❌ تم رفض طلبك.")
    await safe_edit_or_answer(call.message, f"❌ Order #{dep_id} Rejected")

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID: return
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer("📤 Sent for review." if await get_lang(message.from_user.id)=="en" else "📤 تم إرسال الإثبات للمراجعة.")

@dp.callback_query()
async def catch_all_callbacks(call: CallbackQuery): await call.answer()

# ━━━━━ مستقبل الرسايل النصية العامة والزراير ━━━━━
@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id
    
    if user_id in buy_waiting:
        await receive_custom_quantity(message)
        return
        
    if user_id in deposit_waiting:
        await receive_deposit_amount(message)
        return
        
    text_value = message.text.strip()
    if text_value in ["🛍 Products", "🛍 المنتجات"]:
        lang = await get_lang(user_id)
        msg = await animate_message(message, lang)
        await handle_shop_action(msg, lang)
    elif text_value in ["🎧 Support", "🎧 الدعم"]:
        lang = await get_lang(user_id)
        await message.answer(f"{ce('support','🎧')} <b>Support Center / مركز الدعم</b>\n━━━━━━━━━━━━━━━━━━━━━\n{ce('telegram','✈️')} {SUPPORT}", reply_markup=back_home_keyboard(lang), parse_mode="HTML")
    elif text_value in ["💰 Wallet", "💰 المحفظة"]:
        class FakeCall:
            def __init__(self, message, from_user): self.message, self.from_user = message, from_user
            async def answer(self, *args, **kwargs): pass
        await wallet_inline(FakeCall(message, message.from_user))
    elif text_value in ["🌐 Language", "🌐 اللغة"]:
        await message.answer(f"{ce('language','🌐')} Choose language / اختر اللغة:", reply_markup=language_keyboard(), parse_mode="HTML")
    elif text_value in ["🎁 Share & Earn", "🎁 الإحالات"]:
        class FakeCall:
            def __init__(self, message, from_user): self.message, self.from_user = message, from_user
            async def answer(self, *args, **kwargs): pass
        await referral_screen(FakeCall(message, message.from_user))
    else:
        await send_home(message)

async def setup_bot_commands(): await bot.set_my_commands([BotCommand(command="start", description="Start"), BotCommand(command="menu", description="Menu")])
async def main():
    await init_db()
    await setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
