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
    if not emoji_id or not str(emoji_id).isdigit(): 
        return safe_fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{safe_fallback}</tg-emoji>'

def esc(value) -> str: 
    return html.escape(str(value), quote=False)

def strip_custom_emoji(text: str) -> str: 
    return re.sub(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', r'\1', text)

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

deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}
admin_reply_waiting: dict[int, int] = {}
binance_payment_waiting: dict[int, dict] = {}

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
    ch
