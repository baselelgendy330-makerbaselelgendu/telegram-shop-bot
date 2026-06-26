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
from aiogram import BaseMiddleware, Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    URLInputFile, FSInputFile, BotCommand, ReplyKeyboardMarkup, KeyboardButton
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Binance API (set these in Railway Variables)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "381880403")

ADMIN_IDS = [6728595587, 7469507752]
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

CHANNEL_USERNAME = "@CDKK12_CHATGPT"
BOT_USERNAME = "Shop_chatgptplus_bot"

AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")
CDK_IMAGE_FILE = "https://i.postimg.cc/dQ7m0g1R/IMG-20260620-151545-816.jpg"

EMOJI = {
    "cart": "5312361253610475399", "back": "6181245923708903693", "wallet": "6088990159334808217",
    "binance": "5354924237779909158", "share": "6089193719309801680", "support": "6181322172263308706",
    "checkout": "5352662091390008496", "quantity": "5411271889421086677", "price": "5879991085001871624",
    "pencil": "5395444784611480792", "loading": "5341715473882955310", "user": "6183624639806185325",
    "camera": "5976761770537129878", "success": "5976395560150636003", "error": "6181467651395558500",
    "chatgpt": "5359726582447487916", "refresh": "5386367538735104399", "store": "5859297284029681680",
    "vip": "6088920147072915408", "verified": "5976653524476368012", "stock": "5397916757333654639",
    "sold": "5429651785352501917", "announcement": "5395695537687123235", "heart": "5364201435858744869",
    "support_msg": "5443038326535759644", "telegram": "6089099509202164251", "arrow_right": "6181684276661066306",
    "users_group": "4942888689131848546", "money_fly": "5816492162488995555", "link_pin": "5332724926216428039",
    "quotes": "5460795800101594035", "search": "5231012545799666522", "hourglass": "5386367538735104399",
    "check_anim": "6276090299232031662", "user_link": "5440410042773824003", "usdt": "5879991085001871624",
    "buy_cart": "5312361253610475399", "sparkles_pay": "5409048419211682843", "diamond_arrow": "5416117059207572332",
    "secure_shield": "5251203410396458957", "user_new": "5262742999678329061", "ref_trend": "5244837092042750681",
    "ref_check": "5206607081334906820", "ref_hourglass": "5386367538735104399", "arrows_down": "6181684276661066306"
}

SAFE_EMOJI_FALLBACK = {
    "cart": "🛒", "back": "🔙", "wallet": "💰", "binance": "🟡", "share": "🎁", "support": "🎧",
    "checkout": "💳", "quantity": "📦", "price": "💵", "pencil": "✏️", "loading": "⏳",
    "user": "👤", "camera": "📸", "success": "✅", "error": "❌", "chatgpt": "🤖", "refresh": "🔄",
    "store": "🛍", "stock": "➕", "sold": "↗️", "support_msg": "💬", "telegram": "⚡", "arrow_right": "➡️",
    "users_group": "👥", "money_fly": "💸", "link_pin": "📇", "quotes": "🗣️", "search": "🔍",
    "hourglass": "⌛", "announcement": "🚨", "check_anim": "✅", "user_link": "🔗", "usdt": "💵",
    "buy_cart": "🛒", "sparkles_pay": "💵", "diamond_arrow": "➡️", "secure_shield": "🛡",
    "user_new": "👤", "ref_trend": "📈", "ref_check": "✔️", "ref_hourglass": "⌛", "arrows_down": "⬇️"
}

def ce(key: str, fallback: str = "") -> str:
    emoji_id = EMOJI.get(key)
    safe_fallback = SAFE_EMOJI_FALLBACK.get(key, fallback or "✅")
    if not emoji_id or not str(emoji_id).isdigit(): return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'

def esc(value) -> str: 
    return html.escape(str(value), quote=False)

def strip_custom_emoji(text: str) -> str: 
    return re.sub(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r'\1', text)

# ============ Binance Pay Verification ============
async def verify_binance_payment(order_id: str, expected_amount: float):
    """يتأكد من تحويل Binance Pay عن طريق الـ Order ID."""
    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        return False, "Binance API not configured"

    base_url = "https://api.binance.com"
    endpoint = "/sapi/v1/pay/transactions"
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}&recvWindow=60000"
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{endpoint}?{query}&signature={signature}"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=20) as resp:
                data = await resp.json()
    except Exception as e:
        return False, f"Connection error: {e}"

    if not isinstance(data, dict) or data.get("code") != "000000":
        return False, "Could not read transactions from Binance"

    for tx in data.get("data", []):
        if str(tx.get("orderId")) == str(order_id):
            if str(tx.get("transactionType")) != "0":
                return False, "This is not an incoming payment"
            if tx.get("currency") != "USDT":
                return False, f"Wrong currency: {tx.get('currency')}"
            paid = abs(float(tx.get("amount", 0)))
            if paid + 0.02 < expected_amount:
                return False, f"Amount too low. Paid {paid}, required {expected_amount}"
            return True, "OK"

    return False, "Order ID not found. Make sure you paid and the ID is correct."

# ============ Safe Message Helpers ============
async def safe_answer(message: Message, text: str, reply_markup=None):
    try: 
        return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest: 
        return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")

async def safe_edit_or_answer(message, text: str, reply_markup=None):
    try: 
        if getattr(message, "photo", None) or getattr(message, "video", None) or getattr(message, "document", None):
            try: 
                await message.delete()
            except: 
                pass
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
        if os.path.exists(AIX_HEADER_FILE): 
            return await message.answer_photo(photo=FSInputFile(AIX_HEADER_FILE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest:
        try:
            if os.path.exists(AIX_HEADER_FILE): 
                return await message.answer_photo(photo=FSInputFile(AIX_HEADER_FILE), caption=strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
            return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
        except Exception: 
            return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")
    except Exception: 
        return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

# Waiting states
deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}
admin_reply_waiting: dict[int, int] = {}
binance_payment_waiting: dict[int, dict] = {}  # NEW: stores {product_key, qty, amount}

CDK_DESC_EN = (
    "✅ ChatGPT K12 Edu 2-year package.\nFull of latest languages like Plus\n"
    "✅ Can activate any account owner. ⚠️ Applies to <b>Gmail ONLY</b>. (We are not responsible if you use other emails)\n"
    "✅ After ordering, you will receive a code\n✅ Account is on free plan\n"
    "✅ Recommended to use an account without an active subscription or a newly created account to register.\n"
    "✅ Web upgrade CDK: https://oaiteam.azx.us/\n"
    "Step 1: Get https://chatgpt.com/api/auth/session Paste into JSon\n"
    "Step 2: Paste the CDK\nStep 3: Upgrade, guys."
)

CDK_SINGLE_DESC_EN = CDK_DESC_EN + "\n\n⚠️ <b>NOTE:</b> This product is sold with <b>NO WARRANTY</b>."

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title": "CDK GPT Plus (K12 - EDU) 2 years",
        "image": CDK_IMAGE_FILE,
        "usd": 4.0,
        "type": "stock",
        "desc": CDK_DESC_EN
    },
    "cdk_chatgpt_single": {
        "stock_name": "CDK Activation Chatgpt 1Y",
        "title": "CDK (K12) FOR SINGLE",
        "image": CDK_IMAGE_FILE,
        "usd": 5.5,
        "type": "stock",
        "desc": CDK_SINGLE_DESC_EN
    }
}

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, balance_usdt NUMERIC DEFAULT 0, referred_by BIGINT, total_ref INT DEFAULT 0, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_ref INT DEFAULT 0;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance_usdt NUMERIC DEFAULT 0;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS ref_counted BOOLEAN DEFAULT FALSE;")
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
                    await conn.execute("INSERT INTO users(telegram_id, username, first_name, referred_by, ref_counted) VALUES($1, $2, $3, $4, FALSE)", user_id, username, first_name, referrer_id)
                else:
                    await conn.execute("INSERT INTO users(telegram_id, username, first_name) VALUES($1, $2, $3) ON CONFLICT (telegram_id) DO NOTHING", user_id, username, first_name)
            else:
                await conn.execute("INSERT INTO users(telegram_id, username, first_name) VALUES($1, $2, $3) ON CONFLICT (telegram_id) DO NOTHING", user_id, username, first_name)
        else:
            await conn.execute("UPDATE users SET username=$1, first_name=$2 WHERE telegram_id=$3", username, first_name, user_id)

async def process_referral_reward(user_id: int):
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT referred_by, ref_counted FROM users WHERE telegram_id=$1", user_id)
        if user and user["referred_by"] and not user["ref_counted"]:
            referrer_id = user["referred_by"]
            await conn.execute("UPDATE users SET ref_counted = TRUE WHERE telegram_id=$1", user_id)
            await conn.execute("UPDATE users SET total_ref = total_ref + 1 WHERE telegram_id=$1", referrer_id)
            new_total_ref = await conn.fetchval("SELECT total_ref FROM users WHERE telegram_id=$1", referrer_id)
            reward_earned = False
            if new_total_ref > 0 and new_total_ref % 10 == 0:
                await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", 0.50, referrer_id)
                reward_earned = True
            more_to_earn = 10 - (new_total_ref % 10)
            if reward_earned:
                try: 
                    await bot.send_message(referrer_id, f"{ce('share')} <b>Congratulations!</b>\n━━━━━━━━━━━━━━\nYou reached {new_total_ref} active referrals! <b>+0.50 USDT</b> has been added to your wallet.", parse_mode="HTML")
                except Exception: 
                    pass
            else:
                try: 
                    await bot.send_message(referrer_id, f"{ce('share')} <b>New Active Referral!</b>\n━━━━━━━━━━━━━━\nSomeone joined via your link and subscribed! You now have {new_total_ref} active referrals. Invite {more_to_earn} more friends to get $0.50 USDT.", parse_mode="HTML")
                except Exception: 
                    pass
            if CHANNEL_USERNAME != "@YourChannelUsername":
                group_ref_msg = (
                    f"{ce('ref_trend')} <b>New Active Referral!</b>\n\n"
                    f"{ce('user_new')} <b>Referrer:</b> **\n"
                    f"{ce('ref_check')} <b>Active Referrals:</b> {new_total_ref}\n"
                    f"{ce('ref_hourglass')} <b>{more_to_earn} more to earn $0.50</b>"
                )
                try: 
                    await bot.send_message(chat_id=CHANNEL_USERNAME, text=group_ref_msg, parse_mode="HTML")
                except Exception: 
                    pass

class SecurityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat = data.get("event_chat")
        if chat and chat.type in ["group", "supergroup"]:
            return
        user = data.get("event_from_user")
        referrer_id = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start "):
            args = event.text.split()
            if len(args) > 1 and args[1].isdigit():
                referrer_id = int(args[1])
        if user:
            await ensure_user_by_id(user.id, user.username, user.first_name, referrer_id)
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)
        if user and user.id not in ADMIN_IDS:
            if db_pool:
                async with db_pool.acquire() as conn:
                    try:
                        is_banned = await conn.fetchval("SELECT is_banned FROM users WHERE telegram_id=$1", user.id)
                        if is_banned:
                            return
                    except Exception:
                        pass
            if CHANNEL_USERNAME != "@YourChannelUsername":
                try:
                    member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
                    if member.status not in ["member", "administrator", "creator"]:
                        text = f"{ce('error')} <b>Access Denied!</b>\n━━━━━━━━━━━━━━━━━━━━━\nYou must join our group to use this bot.\n\n{ce('arrow_right')} Please join {CHANNEL_USERNAME} first."
                        kb = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="📢 Join Group", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                            [InlineKeyboardButton(text="🔄 Check Subscription", callback_data="check_sub")]
                        ])
                        if isinstance(event, Message):
                            await event.answer(text, reply_markup=kb, parse_mode="HTML")
                        elif isinstance(event, CallbackQuery):
                            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
                            await event.answer()
                        return
                    else:
                        await process_referral_reward(user.id)
                except Exception:
                    pass
        else:
            if user: 
                await process_referral_reward(user.id)
        return await handler(event, data)

dp.message.middleware(SecurityMiddleware())
dp.callback_query.middleware(SecurityMiddleware())

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery):
    if CHANNEL_USERNAME == "@YourChannelUsername":
        await call.answer("Channel is not configured yet.", show_alert=True)
        return
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=call.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await process_referral_reward(call.from_user.id)
            await call.message.delete()
            await call.answer("✅ Thank you for subscribing! You can now use the bot.", show_alert=True)
            await send_home(call.message)
        else:
            await call.answer("❌ You haven't joined yet!", show_alert=True)
    except Exception:
        await call.answer("Error checking subscription.", show_alert=True)

async def get_user_stats(user_id: int):
    async with db_pool.acquire() as conn: 
        return await conn.fetchrow("SELECT balance_usdt, total_ref FROM users WHERE telegram_id=$1", user_id)

async def get_stock_count(product_key: str = "cdk_chatgpt"):
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    async with db_pool.acquire() as conn: 
        return await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", product["stock_name"])

async def get_total_sold(product_name):
    return await db_pool.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=true", product_name)

async def product_counts(): 
    return {"cdk_chatgpt": await get_stock_count("cdk_chatgpt")}

def format_amount(amount):
    try: 
        return str(int(amount)) if float(amount).is_integer() else str(amount).rstrip("0").rstrip(".")
    except Exception: 
        return str(amount)

def resolve_stock_product(product_type: str):
    if product_type.lower() in ["chatgpt", "cdk", "cdk_chatgpt", "cdk_chatgpt_single"]: 
        return "cdk_chatgpt", PRODUCTS["cdk_chatgpt"]["stock_name"]
    return None, None

async def handle_shop_action(target_message: Message):
    counts = await product_counts()
    await safe_edit_or_answer(target_message, product_list_text(), reply_markup=product_buttons(counts))

def get_delivery_text(product: dict, qty: int):
    return (
        f"{ce('success')} <b>Payment Confirmed Successfully!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('vip')} <b>{product['title']}</b>\n\n{ce('quantity')} <b>Quantity:</b> {qty}\n\n"
        f"{ce('announcement')} <b>Delivery Status:</b>\n"
        f"Please wait... The admin has been notified and will send your codes directly here in this chat shortly!\n\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('heart')} <b>Thank you for trusting AIX Store!</b>"
    )

def reply_quantity_keyboard(is_single: bool = False):
    cancel_text = "❌ Cancel"
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

def home_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Browse Products", callback_data="home_shop", icon_custom_emoji_id=EMOJI["store"])],
        [InlineKeyboardButton(text="Deposit", callback_data="home_deposit", icon_custom_emoji_id=EMOJI["wallet"]), InlineKeyboardButton(text="Wallet / Profile", callback_data="home_wallet", icon_custom_emoji_id=EMOJI["user"])],
        [InlineKeyboardButton(text="Support", callback_data="home_support", icon_custom_emoji_id=EMOJI["support"]), InlineKeyboardButton(text="Share & Earn", callback_data="home_share", icon_custom_emoji_id=EMOJI["share"])]
    ])

def back_home_keyboard(): 
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Main Menu", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]])

def product_buttons(counts: dict):
    stock_count = counts.get('cdk_chatgpt', 0)
    chatgpt_icon_id = "5359726582447487916"
    refresh_icon_id = "5386367538735104399"
    btn_text_wholesale = f"CDK GPT Plus (10+) | $4.00 | {stock_count}" if stock_count > 0 else f"CDK GPT Plus (10+) | $4.00 | 0"
    btn_1 = InlineKeyboardButton(text=btn_text_wholesale, callback_data="product_cdk_chatgpt", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
    btn_text_single = f"CDK (K12) FOR SINGLE | $5.50 | {stock_count}" if stock_count > 0 else f"CDK (K12) FOR SINGLE | $5.50 | 0"
    btn_2 = InlineKeyboardButton(text=btn_text_single, callback_data="product_cdk_chatgpt_single", icon_custom_emoji_id=chatgpt_icon_id if stock_count > 0 else EMOJI["error"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_1], 
        [btn_2],
        [InlineKeyboardButton(text="Refresh products", callback_data="refresh_products", icon_custom_emoji_id=refresh_icon_id), InlineKeyboardButton(text="Back", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def product_details_buttons(product_key: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}", icon_custom_emoji_id=EMOJI["cart"])],
        [InlineKeyboardButton(text="Back to Shop", callback_data="home_shop", icon_custom_emoji_id=EMOJI["back"])]
    ])

def checkout_payment_buttons(product_key: str, qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Pay from Wallet", callback_data=f"pay_wallet_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["wallet"])],
        [InlineKeyboardButton(text="Binance Pay (Auto)", callback_data=f"pay_binance_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["binance"])],
        [InlineKeyboardButton(text="Back", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_currency_buttons(): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Deposit", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["price"])], 
        [InlineKeyboardButton(text="Back", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_amount_payment_buttons(amount: float, currency: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Binance Pay • {format_amount(amount)} USDT", callback_data=f"topup_binance_{format_amount(amount)}_{currency}", icon_custom_emoji_id=EMOJI["binance"])], 
        [InlineKeyboardButton(text="Change Amount", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["pencil"])]
    ])

def wallet_kb(): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Deposit", callback_data="home_deposit", icon_custom_emoji_id=EMOJI["wallet"])], 
        [InlineKeyboardButton(text="Refresh", callback_data="home_wallet", icon_custom_emoji_id=EMOJI["refresh"]), InlineKeyboardButton(text="Main Menu", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]
    ])

def main_reply_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="🎧 Support")],
                [KeyboardButton(text="💰 Wallet"), KeyboardButton(text="🎁 Share & Earn")]
    ], resize_keyboard=True, is_persistent=True)

def home_text(name: str):
    chk = ce('check_anim')
    ulink = ce('user_link')
    return f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{esc(name)}</b> {ulink}\nWelcome to your premium AI subscriptions store.\n\n{ce('store')} <b>Shop</b> — Browse & buy products\n{ce('wallet')} <b>Deposit</b> — Add funds to your wallet\n{ce('support')} <b>Support</b> — Get help anytime\n\n{chk} Fast activation  {chk} Secure payments  {chk} Trusted service"

def product_list_text():
    return f"{ce('store')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━\n\n{ce('chatgpt')} <b>CDK Activation Chatgpt 2 Year</b>\nPrice (10+): $4.00 | Single: $5.50\n\n{ce('arrows_down')} Choose a product below:"

async def animate_message(message: Message):
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
    await safe_answer_photo(message, home_text(message.from_user.first_name or "User"), reply_markup=home_keyboard())
    await message.answer("Main Menu", reply_markup=main_reply_keyboard())

@dp.message(CommandStart())
async def start(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    buy_waiting.pop(message.from_user.id, None)
    binance_payment_waiting.pop(message.from_user.id, None)
    await send_home(message)

@dp.message(Command("menu"))
async def menu_command(message: Message): 
    await start(message)

@dp.message(Command("ban"))
async def ban_user_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(f"{ce('error')} <b>Correct usage:</b>\n<code>/ban user_id</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET is_banned = TRUE WHERE telegram_id=$1", target_id)
        await message.answer(f"{ce('success')} <b>Successfully banned user (ID: {target_id})! They can no longer use the bot.</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")

@dp.message(Command("unban"))
async def unban_user_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(f"{ce('error')} <b>Correct usage:</b>\n<code>/unban user_id</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET is_banned = FALSE WHERE telegram_id=$1", target_id)
        await message.answer(f"{ce('success')} <b>Successfully unbanned user (ID: {target_id})!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")

@dp.message(Command("pull"))
async def pull_stock_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(f"{ce('error')} <b>Correct usage:</b>\n<code>/pull 10</code> (to pull 10 codes)", parse_mode="HTML")
        return
    qty = int(parts[1])
    if qty < 1: 
        return
    async with db_pool.acquire() as conn:
        product_name = PRODUCTS["cdk_chatgpt"]["stock_name"]
        items = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product_name, qty)
        if len(items) < qty:
            await message.answer(f"{ce('error')} <b>Insufficient stock! Currently available: {len(items)}</b>", parse_mode="HTML")
            return
        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        await message.answer(f"{ce('success')} <b>Successfully pulled {qty} codes and deducted them from stock!</b>\n\n{codes_str}\n\n<i>You can now copy and send them to the customer.</i>", parse_mode="HTML")

@dp.message(Command("addbalance"))
async def add_balance_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(f"{ce('error')} <b>Usage:</b>\n<code>/addbalance user_id 10</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        amount = float(parts[2])
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", amount, target_id)
        if amount >= 0:
            await message.answer(f"{ce('success')} <b>Successfully added ${amount} to user (ID: {target_id})!</b>", parse_mode="HTML")
            user_msg = f"{ce('wallet')} <b>Balance Added!</b>\n━━━━━━━━━━━━━━━━━━━━━\n<b>{amount} USDT</b> has been added to your wallet by the admin.\nYou can now browse products and purchase easily."
        else:
            abs_amount = abs(amount)
            await message.answer(f"{ce('success')} <b>Successfully deducted ${abs_amount} from user (ID: {target_id})!</b>", parse_mode="HTML")
            user_msg = f"{ce('wallet')} <b>Balance Deducted!</b>\n━━━━━━━━━━━━━━━━━━━━━\n<b>{abs_amount} USDT</b> has been deducted from your wallet by the admin."
        try: 
            await bot.send_message(target_id, user_msg, parse_mode="HTML")
        except Exception: 
            pass
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error:</b> {e}", parse_mode="HTML")

@dp.message(Command("send"))
async def send_to_user_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    parts = message.html_text.split(" ", 2)
    if len(parts) < 3:
        await message.answer(f"{ce('error')} <b>Error! Correct usage:</b>\n<code>/send user_id your_message_here</code>", parse_mode="HTML")
        return
    try:
        target_id = int(parts[1])
        text_to_send = parts[2]
        user_msg = f"{ce('support_msg')} <b>Message from Admin:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{text_to_send}"
        await bot.send_message(target_id, user_msg, parse_mode="HTML")
        await message.answer(f"{ce('success')} <b>Message sent to the customer successfully!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{ce('error')} <b>Error sending message:</b>\n{e}", parse_mode="HTML")

@dp.message(Command("broadcast"))
async def broadcast_message(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    text_to_send = message.html_text.replace("/broadcast", "", 1).strip()
    if not text_to_send:
        await message.answer(f"{ce('error')} <b>Error! Please write the message after the command.</b>", parse_mode="HTML")
        return
    loading_msg = await message.answer(f"{ce('loading')} <b>Sending broadcast to all users...</b>", parse_mode="HTML")
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
    await loading_msg.edit_text(f"{ce('success')} <b>Broadcast sent successfully to {sent_count} users!</b>", parse_mode="HTML")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id not in ADMIN_IDS: 
        return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2: 
        await message.answer(f"{ce('error')} <b>Error! Use this format (in a single message):</b>\n\n<code>/addstock CDK</code>\n<code>Code_1</code>", parse_mode="HTML")
        return
    product_key, stock_name = resolve_stock_product(lines[0])
    if not stock_name: 
        return await message.answer(f"{ce('error')} Unknown code. Use CDK.", parse_mode="HTML")
    added_count = 0
    items = lines[1:]
    async with db_pool.acquire() as conn:
        for item in items: 
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
            added_count += 1
        total = await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", stock_name)
        product_info = PRODUCTS[product_key]
        broadcast_text = f"{ce('announcement')} <b>Stock Alert!</b>\n━━━━━━━━━━━━━━━━━━━━━\n🔥 New keys have been added for: <b>{product_info['title']}</b>\n\n{ce('quantity')} Available Stock: <b>{total}</b>\n⚡ Hurry up and grab yours now before it runs out!"
        users = await conn.fetch("SELECT telegram_id FROM users")
        sent_count = 0
        for u in users:
            try:
                await bot.send_message(u["telegram_id"], broadcast_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}", icon_custom_emoji_id=EMOJI["cart"])]]))
                sent_count += 1
            except Exception: 
                pass
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
                await bot.send_message(chat_id=CHANNEL_USERNAME, text=group_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛒 Buy Now", url=f"https://t.me/{BOT_USERNAME}?start=shop")]]))
            except Exception as e:
                await message.answer(f"{ce('error')} <b>Failed to post to group:</b> {e}", parse_mode="HTML")
    await message.answer(f"{ce('success')} <b>Successfully added {added_count} codes!</b>\nTotal stock: {total}\nNotification sent to {sent_count} users and the Group.", parse_mode="HTML")

@dp.callback_query(F.data.in_(["product_cdk_chatgpt", "product_cdk_chatgpt_single"]))
@dp.callback_query(F.data.startswith("back_to_prod_"))
async def product_callback(call: CallbackQuery):
    await call.answer()
    if call.data.startswith("product_"):
        product_key = call.data.replace("product_", "")
    else:
        product_key = call.data.replace("back_to_prod_", "")
    count = await get_stock_count("cdk_chatgpt") 
    if count <= 0:
        await call.answer("Out of stock! Please check back later.", show_alert=True)
        return
    sold_count = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    product = PRODUCTS[product_key]
    desc = product["desc"].replace("✅", ce("success"))
    caption = (
        f"{ce('chatgpt')} <b>{product['title']}</b>\n━━━━━━━━━━━━━━\n"
        f"{ce('price')} Price: <b>${float(product['usd']):.2f}</b>\n"
        f"{ce('stock')} Stock: <b>{count} accounts</b>\n"
        f"{ce('sold')} Sold: <b>{sold_count} accounts</b>\n\n"
        f"<b>Description:</b>\n<blockquote>{desc}</blockquote>"
    )
    try: 
        await call.message.delete()
    except: 
        pass
    try: 
        await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=product_details_buttons(product_key), parse_mode="HTML")
    except Exception: 
        await call.message.answer(caption, reply_markup=product_details_buttons(product_key), parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    await call.answer()
    product_key = call.data.replace("buy_", "")
    buy_waiting[call.from_user.id] = product_key
    is_single = product_key == "cdk_chatgpt_single"
    text = f"{ce('pencil')} Enter quantity to buy:" if is_single else f"{ce('pencil')} Enter quantity to buy (Minimum 10):"
    await call.message.answer(text, reply_markup=reply_quantity_keyboard(is_single), parse_mode="HTML")

async def receive_custom_quantity(message: Message):
    user_id = message.from_user.id
    product_key = buy_waiting.get(user_id)
    is_single = product_key == "cdk_chatgpt_single"
    min_qty = 1 if is_single else 10
    try:
        qty = int(message.text.strip())
        if qty < min_qty:
            error_text = f"{ce('error')} <b>Order Cannot Be Processed!</b>\n━━━━━━━━━━━━━━━━━━\n<blockquote>{ce('announcement')} <b>The minimum order quantity is {min_qty}.</b>\nPlease enter {min_qty} or more to continue.</blockquote>"
            await message.answer(error_text, parse_mode="HTML")
            return
    except ValueError:
        await message.answer(f"{ce('error')} <b>Enter a valid number!</b>", parse_mode="HTML")
        return
    buy_waiting.pop(user_id, None)
    await proceed_to_checkout(message, product_key, qty)

async def proceed_to_checkout(call_obj, product_key: str, qty: int):
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = f"{ce('checkout')} <b>Checkout</b>\n━━━━━━━━━━━━━━\n\n{ce('quantity')} Quantity: <b>{qty}</b>\n{ce('price')} Total Price: <b>${total_price:.2f}</b>\n\nChoose payment method:"
    if isinstance(call_obj, Message): 
        await call_obj.answer(text, reply_markup=checkout_payment_buttons(product_key, qty), parse_mode="HTML")
    else: 
        await safe_edit_or_answer(call_obj.message, text, reply_markup=checkout_payment_buttons(product_key, qty))

@dp.callback_query(F.data.startswith("pay_wallet_"))
async def pay_wallet_product(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_wallet_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT balance_usdt FROM users WHERE telegram_id=$1", user_id)
        balance = float(user["balance_usdt"]) if user and user["balance_usdt"] else 0.0
        if balance < total_price:
            await call.message.answer(f"{ce('error')} <b>Not enough balance!</b> Please top up.", parse_mode="HTML")
            return
        items = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
        if len(items) < qty:
            await call.message.answer(f"{ce('error')} <b>Out of stock!</b>", parse_mode="HTML")
            return
        await conn.execute("UPDATE users SET balance_usdt = balance_usdt - $1 WHERE telegram_id=$2", total_price, user_id)
        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        await conn.execute("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, quantity, txid, status) VALUES($1,$2,$3,$4,$5,$6,$7,'approved')", user_id, "wallet", total_price, "USDT", product_key, qty, f"wallet_{int(time.time())}")
        await call.message.answer(get_delivery_text(product, qty), parse_mode="HTML")
        if CHANNEL_USERNAME != "@YourChannelUsername":
            group_sale_msg = (
                f"{ce('buy_cart')} <b>New Purchase!</b>\n\n"
                f"{ce('user_new')} <b>User:</b> **\n"
                f"{ce('diamond_arrow')} <b>Product:</b> {product['title']}\n"
                f"{ce('sparkles_pay')} <b>QTY:</b> {qty}\n\n"
                f"<i>Thank you for choosing us</i> {ce('secure_shield')}"
            )
            try:
                await bot.send_message(chat_id=CHANNEL_USERNAME, text=group_sale_msg, parse_mode="HTML")
            except Exception:
                pass
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        admin_msg = f"🛒 <b>Successful purchase from Wallet!</b>\nUser: @{call.from_user.username}\nID: <code>{user_id}</code>\nProduct: {product['title']}\nQuantity: {qty}\nDeducted Amount: {total_price} USDT\n\n<b>🔑 Codes pulled from stock:</b>\n{codes_str}"
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✉️ Send Code to Customer", callback_data=f"sendprod_{user_id}")]])
        for admin in ADMIN_IDS:
            try: 
                await bot.send_message(admin, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
            except Exception: 
                pass

# ============ NEW: Binance Pay Auto Payment ============
@dp.callback_query(F.data.startswith("pay_binance_"))
async def pay_binance_product(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_binance_", "").rsplit("_", 1)
    product_key = parts[0]
    qty = int(parts[1])
    user_id = call.from_user.id
    total_price = float(PRODUCTS[product_key]["usd"]) * qty
    
    binance_payment_waiting[user_id] = {
        "product_key": product_key,
        "qty": qty,
        "amount": total_price,
        "type": "purchase"
    }
    
    text = (
        f"{ce('binance')} <b>Binance Pay - Automatic Verification</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('price')} <b>Amount to transfer:</b> {total_price:.2f} USDT\n\n"
        f"<b>Binance ID (tap to copy):</b>\n<code>{BINANCE_PAY_ID}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📋 Instructions:</b>\n"
        f"1️⃣ Open Binance app\n"
        f"2️⃣ Go to Pay → Transfer\n"
        f"3️⃣ Enter the ID above\n"
        f"4️⃣ Send <b>{total_price:.2f} USDT</b>\n"
        f"5️⃣ Copy the <b>Order ID</b> from transaction details\n"
        f"6️⃣ Send it here to receive your codes instantly\n\n"
        f"{ce('loading')} <b>Waiting for your Order ID...</b>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_binance_pay")]
    ])
    
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

@dp.callback_query(F.data == "cancel_binance_pay")
async def cancel_binance_pay(call: CallbackQuery):
    binance_payment_waiting.pop(call.from_user.id, None)
    await call.answer("Payment cancelled", show_alert=True)
    await send_home(call.message)

async def process_binance_order_id(message: Message, order_id: str):
    user_id = message.from_user.id
    payment_info = binance_payment_waiting.get(user_id)
    
    if not payment_info:
        await message.answer(f"{ce('error')} <b>No pending payment found. Please start a new order.</b>", parse_mode="HTML")
        return
    
    expected_amount = payment_info["amount"]
    product_key = payment_info["product_key"]
    qty = payment_info["qty"]
    payment_type = payment_info.get("type", "purchase")
    
    loading_msg = await message.answer(f"{ce('loading')} <b>Verifying payment with Binance...</b>", parse_mode="HTML")
    
    # Check if Order ID was already used
    async with db_pool.acquire() as conn:
        existing = await conn.fetchval("SELECT id FROM deposits WHERE txid=$1", order_id)
        if existing:
            await loading_msg.edit_text(f"{ce('error')} <b>This Order ID has already been used!</b>\n\nPlease send a new payment or contact {SUPPORT}.", parse_mode="HTML")
            return
    
    # Verify with Binance API
    success, reason = await verify_binance_payment(order_id, expected_amount)
    
    if not success:
        await loading_msg.edit_text(
            f"{ce('error')} <b>Payment Verification Failed!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Reason:</b> {reason}\n\n"
            f"Please check and try again, or contact {SUPPORT}.",
            parse_mode="HTML"
        )
        return
    
    # Payment verified! Process accordingly
    binance_payment_waiting.pop(user_id, None)
    
    if payment_type == "topup":
        # Add to wallet
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", expected_amount, user_id)
            await conn.execute("INSERT INTO deposits (telegram_id, method, amount, currency, txid, status) VALUES($1,$2,$3,$4,$5,'approved')", user_id, "binance_pay", expected_amount, "USDT", order_id)
        
        await loading_msg.edit_text(
            f"{ce('success')} <b>Deposit Confirmed!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{ce('wallet')} <b>{expected_amount} USDT</b> has been added to your wallet.\n\n"
            f"You can now browse products and make purchases!",
            parse_mode="HTML"
        )
        
    else:
        # Process product purchase
        product = PRODUCTS[product_key]
        async with db_pool.acquire() as conn:
            items = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
            
            if len(items) < qty:
                await loading_msg.edit_text(f"{ce('error')} <b>Out of stock! Please contact {SUPPORT} for refund.</b>", parse_mode="HTML")
                return
            
            await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
            await conn.execute("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, quantity, txid, status) VALUES($1,$2,$3,$4,$5,$6,$7,'approved')", user_id, "binance_pay", expected_amount, "USDT", product_key, qty, order_id)
        
        await loading_msg.edit_text(get_delivery_text(product, qty), parse_mode="HTML")
        
        # Notify group
        if CHANNEL_USERNAME != "@YourChannelUsername":
            group_sale_msg = (
                f"{ce('buy_cart')} <b>New Purchase!</b>\n\n"
                f"{ce('user_new')} <b>User:</b> **\n"
                f"{ce('diamond_arrow')} <b>Product:</b> {product['title']}\n"
                f"{ce('sparkles_pay')} <b>QTY:</b> {qty}\n"
                f"{ce('binance')} <b>Binance Pay (Auto)</b>\n\n"
                f"<i>Thank you for choosing us</i> {ce('secure_shield')}"
         mode
            
            try:
                await bot.send_message(chat_id=CHANNEL_USERNAME, text=group_sale_msg, parse_mode="HTML")
            except Exception:
                pass
        
        # Notify admins
        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
        admin_msg = f"🟡 <b>Successful Binance Pay purchase (Auto-verified)!</b>\nUser: @{message.from_user.username}\nID: <code>{user_id}</code>\nProduct: {product['title']}\nQuantity: {qty}\nAmount: {expected_amount} USDT\nOrder ID: <code>{order_id}</code>\n\n<b>🔑 Codes pulled from stock:</b>\n{codes_str}"
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✉️ Send Code to Customer", callback_data=f"sendprod_{user_id}")]])
        for admin in ADMIN_IDS:
            try: 
                await bot.send_message(admin, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
            except Exception: 
                pass

@dp.callback_query(F.data.startswith("sendprod_"))
async def admin_send_product_prompt(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("Unauthorized!", show_alert=True)
    target_user = int(call.data.split("_")[1])
    admin_reply_waiting[call.from_user.id] = target_user
    await call.message.reply(f"{ce('pencil')} <b>Alright, please send the code or message now to be forwarded to the customer (ID: <code>{target_user}</code>):</b>\n<i>(You can send text, photo, or file)\nTo cancel, send: ❌ Cancel</i>", parse_mode
    (call.message.reply(f"{ce('pencil')} <b>Alright, please send the code or message now to be forwarded to the customer (ID: <code>{target_user}</code>):</b>\n<i>(You can send text, photo, or file)\nTo cancel, send: ❌ Cancel</i>", parse_mode="HTML")
    await call.answer()

async def show_support(message_or_call):
    text = f"{ce('support_msg')} <b>Quick support:</b>\n\n{ce('telegram')} <b>Telegram:</b> {ce('arrow_right')} {SUPPORT}" 
    if isinstance(message_or_call, CallbackQuery):
        await safe_edit_or_answer(message_or_call.message, text, reply_markup=back_home_keyboard())
    else:
        await message_or_call.answer(text, reply_markup=back_home_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "home_support")
async def support_callback(call: CallbackQuery):
    await call.answer()
    await show_support(call)

@dp.callback_query(F.data == "home_deposit")
async def deposit_inline_screen(call: CallbackQuery):
    await call.answer()
    text = "💰 <b>Deposit Funds</b>\nSelect currency:"
    await safe_edit_or_answer(call.message, text, reply_markup=deposit_currency_buttons())

@dp.callback_query(F.data == "deposit_currency_USDT")
async def deposit_currency_chosen(call: CallbackQuery):
    await call.answer()
    deposit_waiting[call.from_user.id] = "USDT"
    text = "💰 <b>Enter amount to deposit (e.g., 10 or 5.5):</b>"
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())

async def receive_deposit_amount(message: Message):
    user_id = message.from_user.id
    currency = deposit_waiting.get(user_id, "USDT")
    try:
        amount = float(message.text.strip())
        if amount < 1: 
            raise ValueError
    except ValueError:
        await message.answer(f"{ce('error')} Please enter a valid number greater than 1.", parse_mode="HTML")
        return
    deposit_waiting.pop(user_id, None)
    text = f"💳 <b>Deposit via Crypto</b>\n\nAmount: <b>{amount} {currency}</b>"
    await message.answer(text, reply_markup=deposit_amount_payment_buttons(amount, currency), parse_mode="HTML")

@dp.callback_query(F.data.startswith("topup_binance_"))
async def topup_binance_callback(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amount = float(parts[2])
    currency = parts[3]
    user_id = call.from_user.id
    
    binance_payment_waiting[user_id] = {
        "amount": amount,
        "type": "topup"
    }
    
    text = (
        f"{ce('binance')} <b>Binance Pay - Automatic Verification</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ce('price')} <b>Amount to transfer:</b> {amount:.2f} {currency}\n\n"
        f"<b>Binance ID (tap to copy):</b>\n<code>{BINANCE_PAY_ID}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📋 Instructions:</b>\n"
        f"1️⃣ Open Binance app\n"
        f"2️⃣ Go to Pay → Transfer\n"
        f"3️⃣ Enter the ID above\n"
        f"4️⃣ Send <b>{amount:.2f} {currency}</b>\n"
        f"5️⃣ Copy the <b>Order ID</b> from transaction details\n"
        f"6️⃣ Send it here to add balance to your wallet instantly\n\n"
        f"{ce('loading')} <b>Waiting for your Order ID...</b>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_binance_pay")]
    ])
    
    await safe_edit_or_answer(call.message, text, reply_markup=kb)

@dp.callback_query(F.data == "home_share")
async def referral_screen(call: CallbackQuery):
    await call.answer()
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={call.from_user.id}"
    stats = await get_user_stats(call.from_user.id)
    total_ref = stats["total_ref"] if stats else 0
    earnings = (total_ref // 10) * 0.50
    text = (
        f"{ce('share')} <b>Share & Earn Free USDT!</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"Invite <b>10 friends</b> to use the bot and earn <b>$0.50 USDT</b> instantly inside your wallet!\n\n"
        f"{ce('users_group')} Your Total Invites: <b>{total_ref} users</b>\n"
        f"{ce('money_fly')} Total Earned: <b>{format_amount(earnings)} USDT</b>\n\n"
        f"{ce('link_pin')} <b>Your Exclusive Referral Link:</b>\n"
        f"<code>{ref_link}</code>\n\n<i>Copy the link and share it in groups to start earning!</i>"
    )
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())

@dp.callback_query(F.data == "home_wallet")
async def wallet_inline(call: CallbackQuery):
    await call.answer()
    stats = await get_user_stats(call.from_user.id)
    balance = stats["balance_usdt"] if stats else 0.0
    total_ref = stats["total_ref"] if stats else 0
    earnings = (total_ref // 10) * 0.50
    msg = await animate_message(call.message)
    ulink = ce('user_link')
    text = (
        f"{ce('wallet')} <b>AIX USER PROFILE & WALLET</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{ce('user')} Name: <b>{esc(call.from_user.first_name)}</b> {ulink}\n"
        f"{ce('price')} Wallet Balance: <b>{balance} USDT</b>\n\n"
        f"{ce('users_group')} Total Invited Users: <b>{total_ref} friends</b>\n"
        f"{ce('money_fly')} Referral Earnings: <b>{format_amount(earnings)} USDT</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n{ce('checkout')} You can deposit funds or use your referral balance to purchase instantly."
    )
    await safe_edit_or_answer(msg, text, reply_markup=wallet_kb())

@dp.callback_query(F.data == "home_main")
async def home_main(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message)
    await safe_edit_or_answer(msg, home_text(call.from_user.first_name or "User"), reply_markup=home_keyboard())

@dp.callback_query(F.data == "home_shop")
async def shop_inline_callback(call: CallbackQuery):
    await call.answer()
    msg = await animate_message(call.message)
    await handle_shop_action(msg)

@dp.callback_query(F.data == "refresh_products")
async def refresh_products_callback(call: CallbackQuery):
    await shop_inline_callback(call)

@dp.message(F.photo | F.document)
async def handle_admin_media(message: Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS and user_id in admin_reply_waiting:
        target_id = admin_reply_waiting.pop(user_id)
        try:
            original_caption = message.html_text or ""
            new_caption = f"🎁 <b>Your order is ready!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{original_caption}\n\n{ce('heart')} <b>Thank you for trusting our store!</b>"
            await message.copy_to(target_id, caption=new_caption, parse_mode="HTML")
            await message.answer(f"{ce('success')} <b>File/Photo sent to the customer (ID: {target_id}) successfully! ✅</b>", parse_mode="HTML")
        except Exception as e:
            await message.answer(f"{ce('error')} <b>Error occurred during sending! Maybe the user blocked the bot.</b>\nError: {e}", parse_mode="HTML")
        return

@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id
    text_value = message.text.strip()

    if text_value in ["❌ Cancel", "Cancel"]:
        buy_waiting.pop(user_id, None)
        deposit_waiting.pop(user_id, None)
        binance_payment_waiting.pop(user_id, None)
        if user_id in ADMIN_IDS:
            admin_reply_waiting.pop(user_id, None)
        cancel_msg = "<b>Cancelled. Returning to main menu...</b>"
        await message.answer(f"{ce('error')} {cancel_msg}", reply_markup=main_reply_keyboard(), parse_mode="HTML")
        await send_home(message)
        return

    if text_value.startswith("/"): 
        return
    
    # Check if waiting for Binance Order ID
    if user_id in binance_payment_waiting:
        # User sent Order ID
        order_id = text_value.strip()
        if len(order_id) > 10 and order_id.isdigit():
            await process_binance_order_id(message, order_id)
            return
        else:
            await message.answer(
                f"{ce('error')} <b>Invalid Order ID format!</b>\n\n"
                f"The Order ID should be a long number (18 digits).\n"
                f"Please check and send it again, or tap Cancel.",
                parse_mode="HTML"
            )
            return
    
    if user_id in ADMIN_IDS and user_id in admin_reply_waiting:
        target_id = admin_reply_waiting.pop(user_id)
        try:
            user_msg = f"🎁 <b>Your order is ready!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{message.html_text}\n\n{ce('heart')} <b>Thank you for trusting our store!</b>"
            await bot.send_message(target_id, user_msg, parse_mode="HTML")
            await message.answer(f"{ce('success')} <b>Code sent to the customer successfully! ✅</b>", parse_mode="HTML")
        except Exception as e:
            await message.answer(f"{ce('error')} <b>Error occurred during sending! Maybe the user blocked the bot.</b>\nError: {e}", parse_mode="HTML")
        return

    if user_id in buy_waiting:
        await receive_custom_quantity(message)
        return
        
    if user_id in deposit_waiting:
        await receive_deposit_amount(message)
        return

    if text_value in ["🛍 Products"]:
        msg = await animate_message(message)
        await handle_shop_action(msg)
    elif text_value in ["🎧 Support"]:
        await show_support(message)
    elif text_value in ["💰 Wallet"]:
        class FakeCall:
            def __init__(self, message, from_user): 
                self.message, self.from_user = message, from_user 
            async def answer(self, *args, **kwargs): 
                pass
        await wallet_inline(FakeCall(message, message.from_user))
    elif text_value in ["🎁 Share & Earn"]:
        class FakeCall:
            def __init__(self, message, from_user): 
                self.message, self.from_user = message, from_user 
            async def answer(self, *args, **kwargs): 
                pass
        await referral_screen(FakeCall(message, message.from_user))
    else:
        await send_home(message)

async def main():
    await init_db()
    await bot.set_my_commands([
        BotCommand(command="start", description="Start"), 
        BotCommand(command="menu", description="Menu")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())
    
