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
import base64
from aiogram import BaseMiddleware, Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    URLInputFile, FSInputFile, BotCommand, ReplyKeyboardMarkup, KeyboardButton
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"
REFERRAL_REWARD = 0.10

# مفاتيح Cryptomus (متروكة كمتغيرات لعدم حدوث خطأ في الخادم)
CRYPTOMUS_API_KEY = os.getenv("CRYPTOMUS_API_KEY")
CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID")

AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")
CDK_IMAGE_FILE = "https://i.postimg.cc/dQ7m0g1R/IMG-20260620-151545-816.jpg"

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
    "hourglass": "5386367538735104399",
    "check_anim": "6276090299232031662",
    "user_link": "5440410042773824003",
    "usdt": "5879991085001871624"
}

SAFE_EMOJI_FALLBACK = {
    "cart": "🛒", "back": "🔙", "wallet": "💰", "binance": "🟡", "share": "🎁", "support": "🎧", 
    "language": "🌐", "checkout": "💳", "quantity": "📦", "price": "💵", "pencil": "✏️", "loading": "⏳",
    "user": "👤", "camera": "📸", "success": "✅", "error": "❌", "chatgpt": "🤖", "refresh": "🔄", 
    "store": "🛍", "stock": "➕", "sold": "↗️", "support_msg": "💬", "telegram": "⚡", "arrow_right": "➡️",
    "users_group": "👥", "money_fly": "💸", "link_pin": "📇", "quotes": "🗣️", "search": "🔍", "hourglass": "⌛", "announcement": "🚨",
    "check_anim": "✅",
    "user_link": "🔗",
    "usdt": "💵"
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
    try: 
        if getattr(message, "photo", None) or getattr(message, "video", None) or getattr(message, "document", None):
            try: await message.delete()
            except: pass
            return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
            
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

# قوائم الانتظار في البوت
deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}
admin_reply_waiting: dict[int, int] = {} 

CDK_DESC_EN = (
    "✅ ChatGPT K12 Edu 2-year package.\nFull of latest languages like Plus\n"
    "✅ Can activate any account owner. ⚠️ Applies to **Gmail ONLY**. (We are not responsible if you use other emails)\n"
    "✅ After ordering, you will receive a code\n✅ Account is on free plan\n"
    "✅ Recommended to use an account without an active subscription or a newly created account to register.\n"
    "✅ Web upgrade CDK: https://oaiteam.azx.us/\n"
    "Step 1: Get https://chatgpt.com/api/auth/session Paste into JSon\n"
    "Step 2: Paste the CDK\nStep 3: Upgrade, guys."
)

CDK_DESC_AR = (
    "✅ باقة ChatGPT K12 المخصصة للتعليم لمدة سنتين.\nتحتوي على أحدث المميزات واللغات مثل حسابات بلس تماماً.\n"
    "✅ تقبل التفعيل على إيميلات <b>جيميل (Gmail) فقط</b>. (نحن غير مسؤولين عن أي خطأ إذا تم استخدام إيميل آخر)\n"
    "✅ بعد الطلب والدفع، ستتلقى كود التفعيل فوراً.\n✅ الحساب يجب أن يكون على الخطة المجانية الحالية.\n"
    "✅ يوصى باستخدام حساب ليس به اشتراك نشط أو حساب جديد تماماً للتسجيل.\n"
    "✅ موقع ترقية وتفعيل الكود: https://oaiteam.azx.us/\n"
    "Step 1: Get https://chatgpt.com/api/auth/session Paste into JSon\n"
    "Step 2: Paste the CDK\nStep 3: Upgrade, guys."
)

# 🟢 إضافة منتجين (جملة ومفرد) مرتبطين بنفس المخزون
PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title_en": "CDK GPT Plus (K12 - EDU) 2 years",
        "title_ar": "CDK GPT Plus (K12 - EDU) 2 years",
        "image": CDK_IMAGE_FILE,
        "usd": 4.0,  
        "type": "stock",
        "desc_en": CDK_DESC_EN,
        "desc_ar": CDK_DESC_AR
    },
    "cdk_chatgpt_single": {
        "stock_name": "CDK Activation Chatgpt 1Y", # نفس المخزون!
        "title_en": "CDK (K12) FOR SINGLE",
        "title_ar": "CDK (K12) للمفرد",
        "image": CDK_IMAGE_FILE,
        "usd": 5.5,  # السعر الجديد 5.5
        "type": "stock",
        "desc_en": CDK_DESC_EN,
        "desc_ar": CDK_DESC_AR
    }
}

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, lang TEXT DEFAULT 'ar', balance_usdt NUMERIC DEFAULT 0, referred_by BIGINT, total_ref INT DEFAULT 0, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_ref INT DEFAULT 0;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        # إضافة عمود الحظر
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;")
        await conn.execute("CREATE TABLE IF NOT EXISTS deposits (id SERIAL PRIMARY KEY, telegram_id BIGINT, method TEXT, amount NUMERIC, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', quantity INT DEFAULT 1, txid TEXT UNIQUE, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("ALTER TABLE deposits ADD COLUMN IF NOT EXISTS txid TEXT UNIQUE;")
        await conn.execute("CREATE TABLE IF NOT EXISTS stock (id SERIAL PRIMARY KEY, product TEXT NOT NULL, item_data TEXT NOT NULL, sold BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW());")

# 🟢 نظام الأمان للتحقق من المحظورين (Ban Middleware)
class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user and user.id != ADMIN_ID:
            if db_pool:
                async with db_pool.acquire() as conn:
                    try:
                        is_banned = await conn.fetchval("SELECT is_banned FROM users WHERE telegram_id=$1", user.id)
                        if is_banned:
                            return  # تجاهل العميل المحظور تماماً
                    except Exception:
                        pass
        return await handler(event, data)

dp.message.middleware(BanMiddleware())
dp.callback_query.middleware(BanMiddleware())

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
    if product_type.lower() in ["chatgpt", "cdk", "cdk_chatgpt", "cdk_chatgpt_single"]: return "cdk_chatgpt", PRODUCTS["cdk_chatgpt"]["stock_name"]
    return None, None

async def handle_shop_action(target_message: Message, lang: str):
    counts = await product_counts()
    await safe_edit_or_answer(target_message, product_list_text(lang), reply_markup=product_buttons(lang, counts))

def get_delivery_text(lang: str, product: dict, qty: int, support: str):
    if lang == "en":
        return (
            f"{ce('success')} <b>Payment Confirmed Successfully!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('vip')} <b>{product['title_en']}</b>\n\n{ce('quantity')} <b>Quantity:</b> {qty}\n\n"
            f"{ce('announcement')} <b>Delivery Status:</b>\n"
            f"Please wait... The admin has been notified and will send your codes directly here in this chat shortly!\n\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
        )
    else:
        return (
            f"{ce('success')} <b>تم تأكيد الدفع وتسليم طلب بنجاح!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('vip')} <b>{product['title_ar']}</b>\n\n{ce('quantity')} <b>الكمية المطلوبة:</b> {qty}\n\n"
            f"{ce('announcement')} <b>حالة التسليم:</b>\n"
            f"برجاء الانتظار... تم إشعار الإدارة وجاري إرسال الأكواد لك في هذا الشات مباشرةً! لا داعي للمغادرة.\n\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('heart')} <b>شكراً لثقتك في AIX Store!</b>"
        )

# 🟢 كيبورد الكمية ديناميكي
def reply_quantity_keyboard(lang: str, is_single: bool = False):
    cancel_text = "❌ Cancel" if lang == "en" else "❌ إلغاء"
    if is_single:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
            [KeyboardButton(text="4"), KeyboardButton(text="5")],
            [KeyboardButton(text=cancel_text)]
        ], resize_keyboard=True, one_time_keyboard=True)
    else:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="50")],
            [KeyboardButton(text="100"), KeyboardButton(text="200")],
            [KeyboardButton(text=cancel_text)]
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

# 🟢 زرارين للمنتج (بالسعر الجديد 5.5)
def product_buttons(lang: str, counts: dict):
    stock_count = counts.get('cdk_chatgpt', 0)
    chatgpt_icon_id = "5359726582447487916" 
    refresh_icon_id = "5386367538735104399"
    
    if lang == "en": 
        btn_text_wholesale = f"CDK GPT Plus (10+) | $4.00 | {stock_count}" if stock_count > 0 else f"CDK GPT Plus (10+) | $4.00 | 0"
        btn_1 = InlineKeyboardButton(text=btn_text_wholesale, callback_data="product_cdk_chatgpt", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
        
        btn_text_single = f"CDK (K12) FOR SINGLE | $5.50 | {stock_count}" if stock_count > 0 else f"CDK (K12) FOR SINGLE | $5.50 | 0"
        btn_2 = InlineKeyboardButton(text=btn_text_single, callback_data="product_cdk_chatgpt_single", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [btn_1], 
            [btn_2],
            [InlineKeyboardButton(text="Refresh products", callback_data="refresh_products", icon_custom_emoji_id=refresh_icon_id), InlineKeyboardButton(text="Back", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
        ])
    else:
        btn_text_wholesale = f"CDK GPT Plus (10+) | 4.00$ | {stock_count}" if stock_count > 0 else f"CDK GPT Plus (10+) | 4.00$ | 0"
        btn_1 = InlineKeyboardButton(text=btn_text_wholesale, callback_data="product_cdk_chatgpt", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
        
        btn_text_single = f"CDK (K12) FOR SINGLE | 5.50$ | {stock_count}" if stock_count > 0 else f"CDK (K12) FOR SINGLE | 5.50$ | 0"
        btn_2 = InlineKeyboardButton(text=btn_text_single, callback_data="product_cdk_chatgpt_single", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [btn_1], 
            [btn_2],
            [InlineKeyboardButton(text="تحديث المنتجات", callback_data="refresh_products", icon_custom_emoji_id=refresh_icon_id), InlineKeyboardButton(text="رجوع", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
        ])

def product_details_buttons(lang: str, product_key: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy Now" if lang == "en" else "شراء الآن", callback_data=f"buy_{product_key}", icon_custom_emoji_id=EMOJI["cart"])],
        [InlineKeyboardButton(text="Back to Shop" if lang == "en" else "رجوع للمتجر", callback_data="home_shop", icon_custom_emoji_id=EMOJI["back"])]
    ])

# 🟢 أزرار الدفع
def checkout_payment_buttons(lang: str, product_key: str, qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Pay from Wallet" if lang=="en" else "الدفع من المحفظة", callback_data=f"pay_wallet_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["wallet"])],
        [InlineKeyboardButton(text="Binance Pay (ID)" if lang=="en" else "دفع بينانس (ID)", callback_data=f"pay_binmanual_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["binance"])],
        [InlineKeyboardButton(text="USDT (BEP20) Pay" if lang=="en" else "دفع USDT (BEP20)", callback_data=f"pay_bep20_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["usdt"])],
        [InlineKeyboardButton(text="Back" if lang=="en" else "رجوع", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_currency_buttons(lang: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Deposit" if lang == "en" else "إيداع بالدولار USDT", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["price"])], 
        [InlineKeyboardButton(text="Back" if lang == "en" else "رجوع", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_amount_payment_buttons(lang: str, amount: float, currency: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Binance Pay • {format_amount(amount)} USDT" if lang == "en" else f"دفع بينانس (ID) • {format_amount(amount)} USDT", callback_data=f"topup_binmanual_{format_amount(amount)}_{currency}", icon_custom_emoji_id=EMOJI["binance"])], 
        [InlineKeyboardButton(text=f"USDT (BEP20) • {format_amount(amount)} USDT" if lang == "en" else f"دفع USDT (BEP20) • {format_amount(amount)} USDT", callback_data=f"topup_bep20_{format_amount(amount)}_{currency}", icon_custom_emoji_id=EMOJI["usdt"])], 
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
    chk = ce('check_anim')
    ulink = ce('user_link')
    if lang == "en": 
        return f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{esc(name)}</b> {ulink}\nWelcome to your premium AI subscriptions store.\n\n{ce('store')} <b>Shop</b> — Browse & buy products\n{ce('wallet')} <b>Deposit</b> — Add funds to your wallet\n{ce('support')} <b>Support</b> — Get help anytime\n\n{chk} Fast activation  {chk} Secure payments  {chk} Trusted service"
    return f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nأهلاً، <b>{esc(name)}</b> {ulink}\nنورت متجر اشتراكات الذكاء الاصطناعي المميزة.\n\n{ce('store')} <b>المتجر</b> — تصفح واشتري المنتجات\n{ce('wallet')} <b>إيداع</b> — إضافة رصيد للمحفظة\n{ce('support')} <b>الدعم</b> — مساعدة في أي وقت\n\n{chk} تفعيل سريع  {chk} دفع آمن  {chk} خدمة موثوقة"

# 🟢 تم تعديل السعر لـ 5.50 هنا بشكل نهائي
def product_list_text(lang: str):
    if lang == "en": return f"{ce('store')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('chatgpt')} <b>CDK Activation Chatgpt 2 Year</b>\nPrice (10+): $4.00 | Single: $5.50\n\n{ce('arrows_down')} Choose a product below:"
    return f"{ce('store')} <b>المنتجات المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('chatgpt')} <b>CDK Activation Chatgpt 2 Year</b>\nسعر الجملة (10+): 4.00$ | المفرد: 5.50$\n\n{ce('arrows_down')} اختار المنتج من الأزرار:"

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
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit(): referrer_id = int(args[1])
    await ensure_user_by_id(message.from_user.id, message.from_user.username, message.from_user.first_name, referrer_id)
    await send_home(message)

@dp.message(Command("menu"))
async def menu_command(message: Message): await start(message)

# 🟢 أمر الحظر
@dp.message(Command("ban"))
async def ban_user_command(message: Message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(f"{ce('error')} <b>الاستخدام الصحيح:</b>\n<code>/ban user_id</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET is_banned = TRUE WHERE telegram_id=$1", target_id)
        await message.answer(f"{ce('success')} <b>تم حظر المستخدم (ID: {target_id}) بنجاح! ولن يستطيع استخدام البوت.</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>خطأ:</b> {e}", parse_mode="HTML")

# 🟢 أمر فك الحظر
@dp.message(Command("unban"))
async def unban_user_command(message: Message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(f"{ce('error')} <b>الاستخدام الصحيح:</b>\n<code>/unban user_id</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET is_banned = FALSE WHERE telegram_id=$1", target_id)
        await message.answer(f"{ce('success')} <b>تم فك الحظر عن المستخدم (ID: {target_id}) بنجاح!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>خطأ:</b> {e}", parse_mode="HTML")

@dp.message(Command("addbalance"))
async def add_balance_command(message: Message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(f"{ce('error')} <b>الاستخدام الصحيح:</b>\n<code>/addbalance user_id amount</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        amount = float(parts[2])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", amount, target_id)
        await message.answer(f"{ce('success')} <b>تم شحن محفظة العميل (ID: {target_id}) بمبلغ {amount}$ بنجاح!</b>", parse_mode="HTML")
        
        target_lang = await get_lang(target_id)
        if target_lang == "en":
            user_msg = f"{ce('wallet')} <b>Balance Added!</b>\n━━━━━━━━━━━━━━━━━━━━━\n<b>{amount} USDT</b> has been added to your wallet by the admin.\nYou can now browse products and purchase easily."
        else:
            user_msg = f"{ce('wallet')} <b>تم شحن رصيدك!</b>\n━━━━━━━━━━━━━━━━━━━━━\nتمت إضافة <b>{amount} USDT</b> إلى محفظتك من قِبل الإدارة.\nيمكنك الآن تصفح المنتجات والشراء بسهولة."
            
        await bot.send_message(target_id, user_msg, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>خطأ:</b> {e}", parse_mode="HTML")

@dp.message(Command("send"))
async def send_to_user_command(message: Message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.html_text.split(" ", 2)
    if len(parts) < 3:
        await message.answer(f"{ce('error')} <b>خطأ! استخدم الأمر هكذا:</b>\n<code>/send user_id رسالتك هنا</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        text_to_send = parts[2]
        target_lang = await get_lang(target_id)
        
        if target_lang == "en":
            user_msg = f"{ce('support_msg')} <b>Message from Admin:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{text_to_send}"
        else:
            user_msg = f"{ce('support_msg')} <b>رسالة من الإدارة:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{text_to_send}"
            
        await bot.send_message(target_id, user_msg, parse_mode="HTML")
        await message.answer(f"{ce('success')} <b>تم إرسال الرسالة للعميل بنجاح!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>خطأ أثناء الإرسال:</b>\n{e}", parse_mode="HTML")

@dp.message(Command("broadcast"))
async def broadcast_message(message: Message):
    if message.from_user.id != ADMIN_ID: return
    text_to_send = message.html_text.replace("/broadcast", "", 1).strip()
    if not text_to_send:
        await message.answer(f"{ce('error')} <b>خطأ! برجاء كتابة الرسالة بعد الأمر.</b>", parse_mode="HTML")
        return

    loading_msg = await message.answer(f"{ce('loading')} <b>جاري إرسال الإذاعة لجميع المستخدمين...</b>", parse_mode="HTML")
    sent_count = 0
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id FROM users")
        for u in users:
            try:
                await bot.send_message(u["telegram_id"], text_to_send, parse_mode="HTML")
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
    await loading_msg.edit_text(f"{ce('success')} <b>تم إرسال رسالة الإذاعة بنجاح لـ {sent_count} مستخدم!</b>", parse_mode="HTML")

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

# 🟢 معالجة المنتجين (الجملة والمفرد) وإظهار التفاصيل وحماية المخزون
@dp.callback_query(F.data.in_(["product_cdk_chatgpt", "product_cdk_chatgpt_single"]))
@dp.callback_query(F.data.startswith("back_to_prod_"))
async def product_callback(call: CallbackQuery):
    await call.answer()
    
    if call.data.startswith("product_"):
        product_key = call.data.replace("product_", "")
    else:
        product_key = call.data.replace("back_to_prod_", "")
        
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("cdk_chatgpt") # المخزون واحد للمنتجين
    
    if count <= 0:
        msg = "Out of stock! Please check back later." if lang == "en" else "عذراً، هذا المنتج نفذ من المخزون حالياً!"
        await call.answer(msg, show_alert=True)
        return
        
    sold_count = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    product = PRODUCTS[product_key]
    desc = product["desc_en"].replace("✅", ce("success")) if lang == "en" else product["desc_ar"].replace("✅", ce("success"))
    
    caption = (
        f"{ce('chatgpt')} <b>{product['title_en'] if lang == 'en' else product['title_ar']}</b>\n━━━━━━━━━━━━━━\n"
        f"{ce('price')} Price: <b>${float(product['usd']):.2f}</b>\n"
        f"{ce('stock')} Stock: <b>{count} accounts</b>\n"
        f"{ce('sold')} Sold: <b>{sold_count} accounts</b>\n\n"
        f"<b>Description:</b>\n<blockquote>{desc}</blockquote>"
    )
    try: await call.message.delete()
    except: pass
    try: await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=product_details_buttons(lang, product_key), parse_mode="HTML")
    except Exception: await call.message.answer(caption, reply_markup=product_details_buttons(lang, product_key), parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    await call.answer()
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)
    buy_waiting[call.from_user.id] = product_key
    
    is_single = product_key == "cdk_chatgpt_single"
    if is_single:
        text = f"{ce('pencil')} Enter quantity to buy:" if lang == "en" else f"{ce('pencil')} أدخل الكمية المراد شراؤها:"
    else:
        text = f"{ce('pencil')} Enter quantity to buy (Minimum 10):" if lang == "en" else f"{ce('pencil')} أدخل الكمية المراد شراؤها (أقل كمية 10):"
        
    await call.message.answer(text, reply_markup=reply_quantity_keyboard(lang, is_single), parse_mode="HTML")

async def receive_custom_quantity(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    product_key = buy_waiting.get(user_id)
    
    is_single = product_key == "cdk_chatgpt_single"
    min_qty = 1 if is_single else 10
    
    try:
        qty = int(message.text.strip())
        if qty < min_qty:
            if lang == "ar":
                error_text = f"{ce('error')} <b>عذراً، لا يمكن إتمام الطلب!</b>\n━━━━━━━━━━━━━━━━━━\n<blockquote>{ce('announcement')} <b>الحد الأدنى لشراء هذا المنتج هو {min_qty}.</b>\nيرجى كتابة رقم {min_qty} أو أكثر للاستمرار.</blockquote>"
            else:
                error_text = f"{ce('error')} <b>Order Cannot Be Processed!</b>\n━━━━━━━━━━━━━━━━━━\n<blockquote>{ce('announcement')} <b>The minimum order quantity is {min_qty}.</b>\nPlease enter {min_qty} or more to continue.</blockquote>"
            await message.answer(error_text, parse_mode="HTML")
            return
    except ValueError:
        await message.answer(f"{ce('error')} <b>اكتب رقم صحيح! / Enter a valid number!</b>", parse_mode="HTML")
        return
        
    buy_waiting.pop(user_id, None)
    await proceed_to_checkout(message, product_key, qty)

async def proceed_to_checkout(call_obj, product_key: str, qty: int):
    lang = await get_lang(call_obj.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = (f"{ce('checkout')} <b>Checkout</b>\n━━━━━━━━━━━━━━\n\n{ce('quantity')} Quantity: <b>{qty}</b>\n{ce('price')} Total Price: <b>${total_price:.2f}</b>\n\nChoose payment method:" if lang == "en" else f"{ce('checkout')} <b>إتمام الشراء</b>\n━━━━━━━━━━━━━━\n\n{ce('quantity')} الكمية: <b>{qty}</b>\n{ce('price')} الإجمالي: <b>{total_price:.2f}$</b>\n\nاختار طريقة الدفع:")
    if isinstance(call_obj, Message): await call_obj.answer(text, reply_markup=checkout_payment_buttons(lang, product_key, qty), parse_mode="HTML")
    else: await safe_edit_or_answer(call_obj.message, text, reply_markup=checkout_payment_buttons(lang, product_key, qty))

@dp.callback_query(F.data.startswith("pay_wallet_"))
async def pay_wallet_product(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_wallet_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id
    lang = await get_lang(user_id)

    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT balance_usdt FROM users WHERE telegram_id=$1", user_id)
        balance = float(user["balance_usdt"]) if user and user["balance_usdt"] else 0.0

        if balance < total_price:
            await call.message.answer(f"{ce('error')} <b>Not enough balance!</b> Please top up." if lang == "en" else f"{ce('error')} <b>رصيد محفظتك غير كافٍ!</b> يرجى إيداع أموال.", parse_mode="HTML")
            return

        items = await conn.fetch("SELECT id FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
        if len(items) < qty:
            await call.message.answer(f"{ce('error')} <b>Out of stock!</b>" if lang == "en" else f"{ce('error')} <b>نفذت الكمية من المخزون حالياً!</b>", parse_mode="HTML")
            return

        await conn.execute("UPDATE users SET balance_usdt = balance_usdt - $1 WHERE telegram_id=$2", total_price, user_id)
        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        await conn.execute("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, quantity, txid, status) VALUES($1,$2,$3,$4,$5,$6,$7,'approved')", user_id, "wallet", total_price, "USDT", product_key, qty, f"wallet_{int(time.time())}")

        await call.message.answer(get_delivery_text(lang, product, qty, SUPPORT), parse_mode="HTML")
        
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✉️ إرسال الكود للعميل", callback_data=f"sendprod_{user_id}")]
        ])
        await bot.send_message(ADMIN_ID, f"🛒 <b>شراء ناجح من المحفظة!</b>\nالمستخدم: @{call.from_user.username}\nالـ ID: <code>{user_id}</code>\nالمنتج: {product['title_ar']}\nالكمية: {qty}\nالمبلغ المخصوم: {total_price} USDT", parse_mode="HTML", reply_markup=admin_kb)

@dp.callback_query(F.data.startswith("pay_binmanual_"))
async def pay_binmanual_product(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_binmanual_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    
    total_price = float(PRODUCTS[product_key]["usd"]) * qty
    
    if lang == "en":
        text = (
            f"{ce('binance')} <b>Manual Binance Payment</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} Amount to pay: <b>{total_price:.2f} USDT</b>\n\n"
            f"{ce('loading')} Please transfer the exact amount to the following Binance ID:\n\n"
            f"{ce('arrow_right')} <code>381880403</code>\n\n"
            f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team for approval and order processing:\n"
            f"{ce('support')} {SUPPORT}"
        )
    else:
        text = (
            f"{ce('binance')} <b>الدفع اليدوي عبر بينانس</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} المبلغ المطلوب تحويله: <b>{total_price:.2f} USDT</b>\n\n"
            f"{ce('loading')} برجاء تحويل المبلغ بالكامل إلى معرف بينانس (Binance ID) التالي:\n\n"
            f"{ce('arrow_right')} <code>381880403</code>\n\n"
            f"{ce('support_msg')} بعد إتمام التحويل، يرجى أخذ لقطة شاشة (سكرين شوت) وإرسالها للإدارة لتأكيد الدفع وتسليم طلبك فوراً:\n"
            f"{ce('support')} {SUPPORT}"
        )
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Contact Support" if lang=="en" else "تواصل مع الإدارة", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
        [InlineKeyboardButton(text="Back" if lang=="en" else "رجوع", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])
    await safe_edit_or_answer(call.message, text, reply_markup=kb)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ مراسلة / إرسال الكود", callback_data=f"sendprod_{user_id}")]
    ])
    await bot.send_message(ADMIN_ID, f"🟡 <b>طلب دفع (بينانس ID)!</b>\nالمستخدم: @{call.from_user.username}\nالـ ID: <code>{user_id}</code>\nالمنتج: {PRODUCTS[product_key]['title_ar']}\nالكمية: {qty}\nالمبلغ المطلوب: {total_price} USDT\n\n<i>(العميل سيقوم بمراسلتك بالسكرين شوت، يمكنك الرد عليه وإرسال الكود من هنا)</i>", parse_mode="HTML", reply_markup=admin_kb)

@dp.callback_query(F.data.startswith("pay_bep20_"))
async def pay_bep20_product(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_bep20_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    
    total_price = float(PRODUCTS[product_key]["usd"]) * qty
    
    if lang == "en":
        text = (
            f"{ce('usdt')} <b>USDT (BEP20) Payment</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} Amount to pay: <b>{total_price:.2f} USDT</b>\n\n"
            f"{ce('loading')} Please transfer the amount to the following Address (BEP20):\n\n"
            f"<code>0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa</code>\n\n"
            f"⚠️ <b>IMPORTANT:</b> Please transfer the EXACT amount ({total_price:.2f} USDT) <i>net</i> after network fees. We are not responsible for any deductions caused by network fees.\n\n"
            f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team for approval:\n"
            f"{ce('support')} {SUPPORT}"
        )
    else:
        text = (
            f"{ce('usdt')} <b>الدفع عبر USDT (BEP20)</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} المبلغ المطلوب تحويله: <b>{total_price:.2f} USDT</b>\n\n"
            f"{ce('loading')} برجاء تحويل المبلغ إلى عنوان المحفظة (BEP20) التالي:\n\n"
            f"<code>0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa</code>\n\n"
            f"⚠️ <b>تنبيه هام:</b> يرجى تحويل المبلغ بالكامل ({total_price:.2f} USDT) <i>صافي</i> بعد خصم عمولة الشبكة. الإدارة غير مسؤولة عن نقص المبلغ بسبب عمولة التحويل.\n\n"
            f"{ce('support_msg')} بعد إتمام التحويل، يرجى أخذ لقطة شاشة (سكرين شوت) وإرسالها للإدارة لتأكيد الدفع:\n"
            f"{ce('support')} {SUPPORT}"
        )
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Contact Support" if lang=="en" else "تواصل مع الإدارة", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
        [InlineKeyboardButton(text="Back" if lang=="en" else "رجوع", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])
    await safe_edit_or_answer(call.message, text, reply_markup=kb)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ مراسلة / إرسال الكود", callback_data=f"sendprod_{user_id}")]
    ])
    await bot.send_message(ADMIN_ID, f"🟡 <b>طلب دفع (USDT BEP20)!</b>\nالمستخدم: @{call.from_user.username}\nالـ ID: <code>{user_id}</code>\nالمنتج: {PRODUCTS[product_key]['title_ar']}\nالكمية: {qty}\nالمبلغ المطلوب: {total_price} USDT\n\n<i>(العميل سيقوم بمراسلتك بالسكرين شوت، يمكنك الرد عليه وإرسال الكود من هنا)</i>", parse_mode="HTML", reply_markup=admin_kb)

@dp.callback_query(F.data == "deposit_currency_USDT")
async def deposit_currency_chosen(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    deposit_waiting[call.from_user.id] = "USDT"
    text = "💰 <b>Enter amount to deposit (e.g., 10 or 5.5):</b>" if lang == "en" else "💰 <b>أدخل المبلغ المراد إيداعه (مثلاً 10 أو 5.5):</b>"
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard(lang))

async def receive_deposit_amount(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    currency = deposit_waiting.get(user_id, "USDT")

    try:
        amount = float(message.text.strip())
        if amount < 1: raise ValueError
    except ValueError:
        await message.answer(f"{ce('error')} Please enter a valid number greater than 1." if lang == "en" else f"{ce('error')} يرجى كتابة رقم صحيح أكبر من 1.", parse_mode="HTML")
        return

    deposit_waiting.pop(user_id, None)
    text = f"💳 <b>Deposit via Crypto</b>\n\nAmount: <b>{amount} {currency}</b>" if lang == "en" else f"💳 <b>إيداع عبر الكريبتو</b>\n\nالمبلغ: <b>{amount} {currency}</b>"
    await message.answer(text, reply_markup=deposit_amount_payment_buttons(lang, amount, currency), parse_mode="HTML")

@dp.callback_query(F.data.startswith("topup_binmanual_"))
async def topup_binmanual_callback(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    currency = parts[3]
    user_id = call.from_user.id
    lang = await get_lang(user_id)

    if lang == "en":
        text = (
            f"{ce('binance')} <b>Manual Binance Deposit</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} Amount to transfer: <b>{amount} {currency}</b>\n\n"
            f"{ce('loading')} Please transfer the exact amount to the following Binance ID:\n\n"
            f"{ce('arrow_right')} <code>381880403</code>\n\n"
            f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team to add the balance to your wallet:\n"
            f"{ce('support')} {SUPPORT}"
        )
    else:
        text = (
            f"{ce('binance')} <b>إيداع يدوي عبر بينانس</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} المبلغ المطلوب تحويله: <b>{amount} {currency}</b>\n\n"
            f"{ce('loading')} برجاء تحويل المبلغ بالكامل إلى معرف بينانس (Binance ID) التالي:\n\n"
            f"{ce('arrow_right')} <code>381880403</code>\n\n"
            f"{ce('support_msg')} بعد إتمام التحويل، يرجى أخذ لقطة شاشة (سكرين شوت) وإرسالها للإدارة لشحن رصيد محفظتك فوراً:\n"
            f"{ce('support')} {SUPPORT}"
        )
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Contact Support" if lang=="en" else "تواصل مع الإدارة", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
        [InlineKeyboardButton(text="Main Menu" if lang=="en" else "القائمة الرئيسية", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])
    await safe_edit_or_answer(call.message, text, reply_markup=kb)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ مراسلة العميل", callback_data=f"sendprod_{user_id}")]
    ])
    await bot.send_message(ADMIN_ID, f"🟡 <b>طلب شحن يدوي (بينانس)!</b>\nالمستخدم: @{call.from_user.username}\nالـ ID: <code>{user_id}</code>\nالمبلغ المطلوب: {amount} {currency}\n\n<i>(العميل سيقوم بمراسلتك بالسكرين شوت، يمكنك استخدام أمر الشحن /addbalance مباشرة)</i>", parse_mode="HTML", reply_markup=admin_kb)

@dp.callback_query(F.data.startswith("topup_bep20_"))
async def topup_bep20_callback(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    currency = parts[3]
    user_id = call.from_user.id
    lang = await get_lang(user_id)

    if lang == "en":
        text = (
            f"{ce('usdt')} <b>USDT (BEP20 Deposit)</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} Amount to transfer: <b>{amount} {currency}</b>\n\n"
            f"{ce('loading')} Please transfer the amount to the following Address (BEP20):\n\n"
            f"<code>0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa</code>\n\n"
            f"⚠️ <b>IMPORTANT:</b> Please transfer the EXACT amount ({amount} {currency}) <i>net</i> after network fees. We are not responsible for any deductions caused by network fees.\n\n"
            f"{ce('support_msg')} After successful transfer, take a screenshot and send it to our support team to add the balance to your wallet:\n"
            f"{ce('support')} {SUPPORT}"
        )
    else:
        text = (
            f"{ce('usdt')} <b>شحن عبر USDT (BEP20)</b>\n━━━━━━━━━━━━━━\n"
            f"{ce('price')} المبلغ المطلوب تحويله: <b>{amount} {currency}</b>\n\n"
            f"{ce('loading')} برجاء تحويل المبلغ إلى عنوان المحفظة (BEP20) التالي:\n\n"
            f"<code>0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa</code>\n\n"
            f"⚠️ <b>تنبيه هام:</b> يرجى تحويل المبلغ بالكامل ({amount} {currency}) <i>صافي</i> بعد خصم عمولة الشبكة. الإدارة غير مسؤولة عن نقص المبلغ بسبب عمولة التحويل.\n\n"
            f"{ce('support_msg')} بعد إتمام التحويل، يرجى أخذ لقطة شاشة (سكرين شوت) وإرسالها للإدارة لشحن رصيد محفظتك فوراً:\n"
            f"{ce('support')} {SUPPORT}"
        )
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Contact Support" if lang=="en" else "تواصل مع الإدارة", url=f"https://t.me/{SUPPORT.replace('@', '')}")],
        [InlineKeyboardButton(text="Main Menu" if lang=="en" else "القائمة الرئيسية", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])
    await safe_edit_or_answer(call.message, text, reply_markup=kb)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ مراسلة العميل", callback_data=f"sendprod_{user_id}")]
    ])
    await bot.send_message(ADMIN_ID, f"🟡 <b>طلب شحن يدوي (USDT BEP20)!</b>\nالمستخدم: @{call.from_user.username}\nالـ ID: <code>{user_id}</code>\nالمبلغ المطلوب: {amount} {currency}\n\n<i>(العميل سيقوم بمراسلتك بالسكرين شوت، يمكنك استخدام أمر الشحن /addbalance مباشرة)</i>", parse_mode="HTML", reply_markup=admin_kb)

@dp.callback_query(F.data.startswith("sendprod_"))
async def admin_send_product_prompt(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return await call.answer("غير مصرح لك!", show_alert=True)
        
    target_user = int(call.data.split("_")[1])
    admin_reply_waiting[ADMIN_ID] = target_user
    
    await call.message.reply(f"{ce('pencil')} <b>حسناً يا غالي، أرسل الكود أو الرسالة الآن ليتم تحويلها للعميل (ID: <code>{target_user}</code>):</b>\n<i>(يمكنك إرسال نص، صورة، أو ملف)\nلإلغاء العملية أرسل: ❌ إلغاء</i>", parse_mode="HTML")
    await call.answer()

async def show_support(message_or_call):
    lang = await get_lang(message_or_call.from_user.id)
    text = (f"{ce('support_msg')} <b>Quick support:</b>\n\n{ce('telegram')} <b>Telegram:</b> {ce('arrow_right')} {SUPPORT}" 
            if lang == "en" else 
            f"{ce('support_msg')} <b>الدعم السريع:</b>\n\n{ce('telegram')} <b>تليجرام:</b> {ce('arrow_right')} {SUPPORT}")
    
    if isinstance(message_or_call, CallbackQuery):
        await safe_edit_or_answer(message_or_call.message, text, reply_markup=back_home_keyboard(lang))
    else:
        await message_or_call.answer(text, reply_markup=back_home_keyboard(lang), parse_mode="HTML")

@dp.callback_query(F.data == "home_support")
async def support_callback(call: CallbackQuery):
    await call.answer()
    await show_support(call)

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
    lang = await get_lang(call.from_user.id)
    text = "💰 <b>Deposit Funds</b>\nSelect currency:" if lang == "en" else "💰 <b>إيداع الأموال</b>\nاختر العملة:"
    await safe_edit_or_answer(call.message, text, reply_markup=deposit_currency_buttons(lang))

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
        text = (
            f"{ce('share')} <b>Share & Earn Free USDT!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"Invite your friends to use the bot and earn <b>{REFERRAL_REWARD} USDT</b> instantly inside your wallet for every successful invite!\n\n"
            f"{ce('users_group')} Your Total Invites: <b>{total_ref} users</b>\n"
            f"{ce('money_fly')} Total Earned: <b>{format_amount(earnings)} USDT</b>\n\n"
            f"{ce('link_pin')} <b>Your Exclusive Referral Link:</b>\n"
            f"<code>{ref_link}</code>\n\n<i>Copy the link and share it in groups to start earning!</i>"
        )
    else:
        text = (
            f"{ce('share')} <b>انشر البوت وابني أرباح مجانية!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"انسخ رابط الإحالة الخاص بك وانشره؛ لكل شخص يدخل البوت عن طريقك هتكسب <b>{REFERRAL_REWARD} USDT</b> فوراً جوه محفظتك تقدر تشتري بيها أي منتج!\n\n"
            f"{ce('users_group')} عدد إحالاتك الحالي: <b>{total_ref} عضو</b>\n"
            f"{ce('money_fly')} إجمالي ما كسبته: <b>{format_amount(earnings)} USDT</b>\n\n"
            f"{ce('link_pin')} <b>رابط الإحالة الحصري الخاص بك:</b>\n"
            f"<code>{ref_link}</code>\n\n<i>اضغط على الرابط لنسخه وانشره في الجروبات لتبدأ الأرباح!</i>"
        )
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard(lang))

@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    await call.answer()
    lang = await get_lang(call.from_user.id)
    stats = await get_user_stats(call.from_user.id)
    balance = stats["balance_usdt"] if stats else 0.0
    total_ref = stats["total_ref"] if stats else 0
    msg = await animate_message(call.message, lang)
    ulink = ce('user_link')
    
    if lang == "en":
        text = (
            f"{ce('wallet')} <b>AIX USER PROFILE & WALLET</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('user')} Name: <b>{esc(call.from_user.first_name)}</b> {ulink}\n"
            f"{ce('price')} Wallet Balance: <b>{balance} USDT</b>\n\n"
            f"{ce('users_group')} Total Invited Users: <b>{total_ref} friends</b>\n"
            f"{ce('money_fly')} Referral Earnings: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('checkout')} You can deposit funds or use your referral balance to purchase instantly."
        )
    else:
        text = (
            f"{ce('wallet')} <b>ملف الحساب ومحفظة AIX</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ce('user')} الحساب: <b>{esc(call.from_user.first_name)}</b> {ulink}\n"
            f"{ce('price')} رصيد المحفظة الحالي: <b>{balance} USDT</b>\n\n"
            f"{ce('users_group')} إجمالي الإحالات الخاصة بك: <b>{total_ref} عضو</b>\n"
            f"{ce('money_fly')} أرباحك من الإحالات: <b>{format_amount(total_ref * REFERRAL_REWARD)} USDT</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('checkout')} تقدر تشحن محفظتك يدوياً أو تستخدم أرباح إحالاتك للشراء الفوري مباشرةً."
        )
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

@dp.callback_query(F.data == "refresh_products")
async def refresh_products_callback(call: CallbackQuery):
    await shop_inline_callback(call)

@dp.message(F.photo | F.document)
async def handle_admin_media(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and user_id in admin_reply_waiting:
        target_id = admin_reply_waiting.pop(ADMIN_ID)
        try:
            original_caption = message.html_text or ""
            target_lang = await get_lang(target_id)
            if target_lang == "en":
                new_caption = f"🎁 <b>Your order is ready!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{original_caption}\n\n{ce('heart')} <b>Thank you for trusting our store!</b>"
            else:
                new_caption = f"🎁 <b>طلبك جاهز يا غالي!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{original_caption}\n\n{ce('heart')} <b>شكراً لشرائك وثقتك في متجرنا!</b>"
                
            await message.copy_to(target_id, caption=new_caption, parse_mode="HTML")
            await message.answer(f"{ce('success')} <b>تم إرسال الملف/الصورة للعميل (ID: {target_id}) بنجاح! ✅</b>", parse_mode="HTML")
        except Exception as e:
            await message.answer(f"{ce('error')} <b>حدث خطأ أثناء الإرسال! ربما العميل حظر البوت.</b>\nالخطأ: {e}", parse_mode="HTML")
        return

@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id
    text_value = message.text.strip()
    lang = await get_lang(user_id)

    if text_value in ["❌ Cancel", "❌ إلغاء", "Cancel", "إلغاء", "❌ Cancel / إلغاء"]:
        buy_waiting.pop(user_id, None)
        deposit_waiting.pop(user_id, None)
        if user_id == ADMIN_ID:
            admin_reply_waiting.pop(ADMIN_ID, None)
        cancel_msg = "<b>Cancelled. Returning to main menu...</b>" if lang == "en" else "<b>تم الإلغاء. جاري العودة للقائمة الرئيسية...</b>"
        await message.answer(f"{ce('error')} {cancel_msg}", reply_markup=main_reply_keyboard(lang), parse_mode="HTML")
        await send_home(message)
        return

    if text_value.startswith("/"): return
    
    if user_id == ADMIN_ID and user_id in admin_reply_waiting:
        target_id = admin_reply_waiting.pop(ADMIN_ID)
        try:
            target_lang = await get_lang(target_id)
            if target_lang == "en":
                user_msg = f"🎁 <b>Your order is ready!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{message.html_text}\n\n{ce('heart')} <b>Thank you for trusting our store!</b>"
            else:
                user_msg = f"🎁 <b>طلبك جاهز يا غالي!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{message.html_text}\n\n{ce('heart')} <b>شكراً لشرائك وثقتك في متجرنا!</b>"
                
            await bot.send_message(target_id, user_msg, parse_mode="HTML")
            await message.answer(f"{ce('success')} <b>تم إرسال الكود للعميل بنجاح! ✅</b>", parse_mode="HTML")
        except Exception as e:
            await message.answer(f"{ce('error')} <b>حدث خطأ أثناء الإرسال! ربما العميل حظر البوت.</b>\nالخطأ: {e}", parse_mode="HTML")
        return

    if user_id in buy_waiting:
        await receive_custom_quantity(message)
        return
    if user_id in deposit_waiting:
        await receive_deposit_amount(message)
        return

    if text_value in ["🛍 Products", "🛍 المنتجات"]:
        msg = await animate_message(message, lang)
        await handle_shop_action(msg, lang)
    elif text_value in ["🎧 Support", "🎧 الدعم"]:
        await show_support(message)
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
    elif text_value in ["🌐 Language", "🌐 اللغة"]:
        await message.answer("🌐 <b>Choose your language / اختر لغتك:</b>", reply_markup=language
