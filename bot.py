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
# 🔴 Multi-Admin List
ADMIN_IDS = [6728595587, 7469507752]
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

# 🔴 Linked Channel & Bot
CHANNEL_USERNAME = "@CDKK12_CHATGPT" 
BOT_USERNAME = "Shop_chatgptplus_bot"

# Binance Auto API Keys
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "381880403")

# Cryptomus Keys (Optional/Alternative)
CRYPTOMUS_API_KEY = os.getenv("CRYPTOMUS_API_KEY")
CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID")

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
    "usdt": "5879991085001871624", "buy_cart": "5312361253610475399", "sparkles_pay": "5409048419211682843",
    "diamond_arrow": "5416117059207572332", "secure_shield": "5251203410396458957", "user_new": "5262742999678329061",
    "ref_trend": "5244837092042750681", "ref_check": "5206607081334906820", "ref_hourglass": "5386367538735104399"
}

SAFE_EMOJI_FALLBACK = {
    "cart": "🛒", "back": "🔙", "wallet": "💰", "binance": "🟡", "share": "🎁", "support": "🎧", 
    "checkout": "💳", "quantity": "📦", "price": "💵", "pencil": "✏️", "loading": "⏳",
    "user": "👤", "success": "✅", "error": "❌", "chatgpt": "🤖", "refresh": "🔄", 
    "store": "🛍", "stock": "➕", "sold": "↗️", "support_msg": "💬", "telegram": "⚡", "arrow_right": "➡️",
    "users_group": "👥", "money_fly": "💸", "link_pin": "📇", "usdt": "💵", "buy_cart": "🛒",
    "sparkles_pay": "💵", "diamond_arrow": "➡️", "secure_shield": "🛡", "user_new": "👤",
    "ref_trend": "📈", "ref_check": "✔️", "ref_hourglass": "⌛"
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
        if "message is not modified" in str(e).lower(): return message
        try: return await message.edit_text(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
        except Exception: return await message.answer(strip_custom_emoji(text), reply_markup=reply_markup, parse_mode="HTML")
    except Exception: return await safe_answer(message, text, reply_markup)

async def safe_answer_photo(message: Message, caption: str, reply_markup=None):
    try:
        return await message.answer_photo(photo=URLInputFile(AIX_HEADER_IMAGE), caption=caption, reply_markup=reply_markup, parse_mode="HTML")
    except Exception: return await message.answer(strip_custom_emoji(caption), reply_markup=reply_markup, parse_mode="HTML")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

# Waiting states
deposit_waiting: dict[int, str] = {}
buy_waiting: dict[int, str] = {}
admin_reply_waiting: dict[int, int] = {} 
binance_verification_waiting: dict[int, dict] = {} # 🔴 New: State for Binance Auto Check

CDK_DESC_EN = (
    "✅ ChatGPT K12 Edu 2-year package.\nFull of latest languages like Plus\n"
    "✅ Can activate any account owner. ⚠️ Applies to <b>Gmail ONLY</b>.\n"
    "✅ After ordering, you will receive a code\n✅ Account is on free plan\n"
    "✅ Web upgrade CDK: https://oaiteam.azx.us/\n"
)

PRODUCTS = {
    "cdk_chatgpt": {
        "stock_name": "CDK Activation Chatgpt 1Y", "title": "CDK GPT Plus (K12 - EDU) 2 years",
        "image": CDK_IMAGE_FILE, "usd": 4.0, "type": "stock", "desc": CDK_DESC_EN
    },
    "cdk_chatgpt_single": {
        "stock_name": "CDK Activation Chatgpt 1Y", "title": "CDK (K12) FOR SINGLE",
        "image": CDK_IMAGE_FILE, "usd": 5.5, "type": "stock", "desc": CDK_DESC_EN + "\n\n⚠️ <b>NO WARRANTY</b>."
    }
}

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, balance_usdt NUMERIC DEFAULT 0, referred_by BIGINT, total_ref INT DEFAULT 0, ref_counted BOOLEAN DEFAULT FALSE, is_banned BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("CREATE TABLE IF NOT EXISTS deposits (id SERIAL PRIMARY KEY, telegram_id BIGINT, method TEXT, amount NUMERIC, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', quantity INT DEFAULT 1, txid TEXT UNIQUE, created_at TIMESTAMP DEFAULT NOW());")
        await conn.execute("CREATE TABLE IF NOT EXISTS stock (id SERIAL PRIMARY KEY, product TEXT NOT NULL, item_data TEXT NOT NULL, sold BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW());")

# 🟢 Binance Auto API Verification Function
async def verify_binance_transaction(order_id: str, expected_amount: float) -> bool:
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        print("Binance API Keys not configured!")
        return False
        
    try:
        timestamp = int(time.time() * 1000)
        params = f"timestamp={timestamp}"
        signature = hmac.new(BINANCE_API_SECRET.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        url = f"https://api.binance.com/sapi/v1/pay/transactions?{params}&signature={signature}"
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "000000" and "data" in data:
                        for tx in data["data"]:
                            tx_id = str(tx.get("orderId", ""))
                            tx_ref = str(tx.get("transactionId", ""))
                            # Check if the provided Order ID matches the transaction
                            if order_id == tx_id or order_id == tx_ref:
                                amount = float(tx.get("amount", 0))
                                if amount >= expected_amount:
                                    return True
    except Exception as e:
        print(f"Error checking Binance API: {e}")
    return False

# 🟢 Security Middleware
class SecurityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat = data.get("event_chat")
        if chat and chat.type in ["group", "supergroup"]: return
        user = data.get("event_from_user")
        
        referrer_id = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start "):
            args = event.text.split()
            if len(args) > 1 and args[1].isdigit(): referrer_id = int(args[1])
        
        if user:
            async with db_pool.acquire() as conn:
                u = await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", user.id)
                if not u:
                    await conn.execute("INSERT INTO users(telegram_id, username, first_name, referred_by) VALUES($1, $2, $3, $4) ON CONFLICT DO NOTHING", user.id, user.username, user.first_name, referrer_id)
                else:
                    await conn.execute("UPDATE users SET username=$1, first_name=$2 WHERE telegram_id=$3", user.username, user.first_name, user.id)
                    if u["is_banned"]: return

            if CHANNEL_USERNAME != "@YourChannelUsername" and user.id not in ADMIN_IDS:
                if isinstance(event, CallbackQuery) and event.data == "check_sub": pass
                else:
                    try:
                        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
                        if member.status not in ["member", "administrator", "creator"]:
                            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Join Group", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")], [InlineKeyboardButton(text="🔄 Check Subscription", callback_data="check_sub")]])
                            msg_text = f"{ce('error')} <b>Access Denied!</b>\nYou must join our group to use this bot."
                            if isinstance(event, Message): await event.answer(msg_text, reply_markup=kb, parse_mode="HTML")
                            elif isinstance(event, CallbackQuery): 
                                await event.message.answer(msg_text, reply_markup=kb, parse_mode="HTML")
                                await event.answer()
                            return
                        else: await process_referral_reward(user.id)
                    except Exception: pass 
            else: await process_referral_reward(user.id)
        return await handler(event, data)

dp.message.middleware(SecurityMiddleware())
dp.callback_query.middleware(SecurityMiddleware())

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=call.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await process_referral_reward(call.from_user.id)
            await call.message.delete()
            await call.answer("✅ Thank you for subscribing!", show_alert=True)
            await send_home(call.message)
        else: await call.answer("❌ You haven't joined yet!", show_alert=True)
    except Exception: await call.answer("Error checking subscription.", show_alert=True)

async def process_referral_reward(user_id: int):
    async with db_pool.acquire() as conn:
        u = await conn.fetchrow("SELECT referred_by, ref_counted FROM users WHERE telegram_id=$1", user_id)
        if u and u["referred_by"] and not u["ref_counted"]:
            await conn.execute("UPDATE users SET ref_counted = TRUE WHERE telegram_id=$1", user_id)
            await conn.execute("UPDATE users SET total_ref = total_ref + 1 WHERE telegram_id=$1", u["referred_by"])
            new_ref = await conn.fetchval("SELECT total_ref FROM users WHERE telegram_id=$1", u["referred_by"])
            if new_ref % 10 == 0:
                await conn.execute("UPDATE users SET balance_usdt = balance_usdt + 0.50 WHERE telegram_id=$1", u["referred_by"])
                try: await bot.send_message(u["referred_by"], f"{ce('share')} <b>Congratulations! +0.50 USDT added!</b>", parse_mode="HTML")
                except: pass

async def get_user_stats(user_id: int):
    async with db_pool.acquire() as conn: return await conn.fetchrow("SELECT balance_usdt, total_ref FROM users WHERE telegram_id=$1", user_id)

async def get_stock_count(product_key: str = "cdk_chatgpt"):
    async with db_pool.acquire() as conn: return await conn.fetchval("SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false", PRODUCTS[product_key]["stock_name"])

def format_amount(amount):
    return str(int(amount)) if float(amount).is_integer() else str(amount).rstrip("0").rstrip(".")

def home_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Browse Products", callback_data="home_shop", icon_custom_emoji_id=EMOJI["store"])],
        [InlineKeyboardButton(text="Deposit", callback_data="home_deposit", icon_custom_emoji_id=EMOJI["wallet"]), InlineKeyboardButton(text="Wallet / Profile", callback_data="home_wallet", icon_custom_emoji_id=EMOJI["user"])],
        [InlineKeyboardButton(text="Support", callback_data="home_support", icon_custom_emoji_id=EMOJI["support"]), InlineKeyboardButton(text="Share & Earn", callback_data="home_share", icon_custom_emoji_id=EMOJI["share"])]
    ])

def back_home_keyboard(): 
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Main Menu", callback_data="home_main", icon_custom_emoji_id=EMOJI["back"])]])

def checkout_payment_buttons(product_key: str, qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Pay from Wallet", callback_data=f"pay_wallet_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["wallet"])],
        [InlineKeyboardButton(text="Binance Pay (Auto)", callback_data=f"pay_binauto_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["binance"])],
        [InlineKeyboardButton(text="USDT (BEP20)", callback_data=f"pay_bep20_{product_key}_{qty}", icon_custom_emoji_id=EMOJI["usdt"])],
        [InlineKeyboardButton(text="Back", callback_data=f"back_to_prod_{product_key}", icon_custom_emoji_id=EMOJI["back"])]
    ])

def deposit_amount_payment_buttons(amount: float, currency: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Binance Pay (Auto) • {format_amount(amount)} USDT", callback_data=f"topup_binauto_{format_amount(amount)}_{currency}", icon_custom_emoji_id=EMOJI["binance"])], 
        [InlineKeyboardButton(text=f"USDT (BEP20) • {format_amount(amount)} USDT", callback_data=f"topup_bep20_{format_amount(amount)}_{currency}", icon_custom_emoji_id=EMOJI["usdt"])], 
        [InlineKeyboardButton(text="Change Amount", callback_data="deposit_currency_USDT", icon_custom_emoji_id=EMOJI["pencil"])]
    ])

def main_reply_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="🎧 Support")], 
        [KeyboardButton(text="💰 Wallet"), KeyboardButton(text="🎁 Share & Earn")]
    ], resize_keyboard=True, is_persistent=True)

async def send_home(message: Message):
    text = f"{ce('vip')} <b>AIX Store</b> {ce('verified')}\n━━━━━━━━━━━━━━━━━━\n\nHey, <b>{esc(message.from_user.first_name)}</b>\nWelcome to your premium AI store."
    await safe_answer_photo(message, text, reply_markup=home_keyboard())
    await message.answer("Main Menu", reply_markup=main_reply_keyboard())

@dp.message(CommandStart())
async def start(message: Message):
    deposit_waiting.pop(message.from_user.id, None)
    buy_waiting.pop(message.from_user.id, None)
    binance_verification_waiting.pop(message.from_user.id, None)
    await send_home(message)

# ----------- ADMIN COMMANDS -----------
@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2: return await message.answer("Format:\n/addstock CDK\nCode_1")
    stock_name = PRODUCTS["cdk_chatgpt"]["stock_name"]
    added_count = 0
    async with db_pool.acquire() as conn:
        for item in lines[1:]: 
            await conn.execute("INSERT INTO stock(product,item_data) VALUES($1,$2)", stock_name, item)
            added_count += 1
    await message.answer(f"✅ Added {added_count} codes.")

@dp.message(Command("addbalance"))
async def add_balance_command(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.text.split()
    if len(parts) < 3: return
    target_id, amount = int(parts[1]), float(parts[2])
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", amount, target_id)
    await message.answer(f"✅ Modified balance for {target_id} by {amount}")

# ----------- SHOP & PRODUCTS -----------
@dp.callback_query(F.data == "home_shop")
async def shop_inline_callback(call: CallbackQuery):
    await call.answer()
    count = await get_stock_count("cdk_chatgpt")
    btn1 = InlineKeyboardButton(text=f"CDK GPT Plus (10+) | $4.00 | {count}", callback_data="product_cdk_chatgpt")
    btn2 = InlineKeyboardButton(text=f"CDK (K12) FOR SINGLE | $5.50 | {count}", callback_data="product_cdk_chatgpt_single")
    kb = InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [InlineKeyboardButton(text="Back", callback_data="home_main")]])
    await safe_edit_or_answer(call.message, f"{ce('store')} <b>Available Products</b>\n━━━━━━━━━━━━━━━━━━", reply_markup=kb)

@dp.callback_query(F.data.in_(["product_cdk_chatgpt", "product_cdk_chatgpt_single"]))
async def product_callback(call: CallbackQuery):
    await call.answer()
    product_key = call.data.replace("product_", "")
    product = PRODUCTS[product_key]
    count = await get_stock_count(product_key)
    caption = f"{ce('chatgpt')} <b>{product['title']}</b>\nPrice: <b>${product['usd']:.2f}</b>\nStock: <b>{count}</b>\n\n{product['desc']}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Buy Now", callback_data=f"buy_{product_key}")], [InlineKeyboardButton(text="Back", callback_data="home_shop")]])
    try: await call.message.delete()
    except: pass
    await call.message.answer_photo(URLInputFile(CDK_IMAGE_FILE), caption=caption, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    await call.answer()
    product_key = call.data.replace("buy_", "")
    buy_waiting[call.from_user.id] = product_key
    is_single = product_key == "cdk_chatgpt_single"
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2")], [KeyboardButton(text="❌ Cancel")]], resize_keyboard=True) if is_single else ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="10"), KeyboardButton(text="20")], [KeyboardButton(text="❌ Cancel")]], resize_keyboard=True)
    await call.message.answer(f"{ce('pencil')} Enter quantity:", reply_markup=kb, parse_mode="HTML")

# ----------- AUTO BINANCE PAYMENTS -----------
@dp.callback_query(F.data.startswith("pay_binauto_") | F.data.startswith("topup_binauto_"))
async def handle_auto_binance(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    
    if call.data.startswith("pay_binauto_"):
        parts = call.data.replace("pay_binauto_", "").rsplit("_", 1)
        product_key, qty = parts[0], int(parts[1])
        amount = float(PRODUCTS[product_key]["usd"]) * qty
        binance_verification_waiting[user_id] = {"type": "buy", "product_key": product_key, "qty": qty, "amount": amount, "currency": "USDT"}
    else:
        parts = call.data.split("_")
        amount, currency = float(parts[2]), parts[3]
        binance_verification_waiting[user_id] = {"type": "topup", "amount": amount, "currency": currency}

    text = (
        f"🏦 <b>Binance Pay (Auto Verification)</b>\n━━━━━━━━━━━━━━\n"
        f"Binance ID (tap to copy): <code>{BINANCE_PAY_ID}</code>\n"
        f"Amount to transfer: <b>${amount:.2f}</b>\n\n"
        f"{ce('loading')} <b>Please send the order ID or off-chain transaction reference after payment for verification.</b>\n"
        f"<i>(Just paste the Order ID here in the chat)</i>"
    )
    await safe_edit_or_answer(call.message, text, reply_markup=back_home_keyboard())

# ----------- TEXT MESSAGES HANDLER (Includes Auto Verification) -----------
@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text in ["❌ Cancel", "Cancel"]:
        buy_waiting.pop(user_id, None)
        deposit_waiting.pop(user_id, None)
        binance_verification_waiting.pop(user_id, None)
        await message.answer("<b>Cancelled.</b>", reply_markup=main_reply_keyboard(), parse_mode="HTML")
        return await send_home(message)

    # 🔴 BINANCE AUTO VERIFICATION LOGIC
    if user_id in binance_verification_waiting:
        state = binance_verification_waiting.pop(user_id)
        order_id = text
        expected_amount = state["amount"]
        
        verify_msg = await message.answer(f"{ce('loading')} <b>Verifying your transaction, please wait...</b>", parse_mode="HTML")
        
        async with db_pool.acquire() as conn:
            exists = await conn.fetchval("SELECT 1 FROM deposits WHERE txid=$1", order_id)
            if exists:
                await verify_msg.edit_text(f"{ce('error')} <b>This Order ID has already been used!</b>", parse_mode="HTML")
                return
        
        is_valid = await verify_binance_transaction(order_id, expected_amount)
        
        if is_valid:
            async with db_pool.acquire() as conn:
                await conn.execute("INSERT INTO deposits(telegram_id, method, amount, currency, product_key, quantity, txid, status) VALUES($1,$2,$3,$4,$5,$6,$7,'approved')", user_id, "binance_auto", expected_amount, "USDT", state.get("product_key", "topup"), state.get("qty", 1), order_id)
                
                if state["type"] == "topup":
                    await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", expected_amount, user_id)
                    await verify_msg.edit_text(f"{ce('success')} <b>Top-up Successful!</b>\n<b>{expected_amount} USDT</b> added to your wallet.", parse_mode="HTML")
                
                elif state["type"] == "buy":
                    product_key = state["product_key"]
                    qty = state["qty"]
                    product = PRODUCTS[product_key]
                    items = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
                    
                    if len(items) < qty:
                        await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", expected_amount, user_id)
                        await verify_msg.edit_text(f"{ce('error')} <b>Stock ran out!</b>\n<b>{expected_amount} USDT</b> added to your wallet instead.", parse_mode="HTML")
                    else:
                        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
                        codes_str = "\n".join([f"<code>{i['item_data']}</code>" for i in items])
                        await verify_msg.edit_text(f"{ce('success')} <b>Payment Confirmed!</b>\n\n{ce('vip')} <b>{product['title']}</b>\n\n{ce('announcement')} <b>Codes:</b>\n{codes_str}", parse_mode="HTML")
                        
                        if CHANNEL_USERNAME != "@YourChannelUsername":
                            try: await bot.send_message(chat_id=CHANNEL_USERNAME, text=f"🛒 <b>New Auto-Buy!</b>\nProduct: {product['title']}\nQTY: {qty}", parse_mode="HTML")
                            except: pass
        else:
            binance_verification_waiting[user_id] = state # Put back in waiting state
            await verify_msg.edit_text(f"{ce('error')} <b>5 minutes have passed or ID invalid!</b>\nWe haven't received/verified the exact amount for this Order ID. Please check and send it again.", parse_mode="HTML")
        return

    # Normal Buying Logic
    if user_id in buy_waiting:
        product_key = buy_waiting.pop(user_id)
        try:
            qty = int(text)
            if qty < 1: raise ValueError
        except: return await message.answer("Invalid quantity.")
        
        product = PRODUCTS[product_key]
        total = float(product["usd"]) * qty
        await message.answer(f"{ce('checkout')} <b>Checkout</b>\nQty: {qty}\nTotal: ${total:.2f}", reply_markup=checkout_payment_buttons(product_key, qty), parse_mode="HTML")
        return
        
    if text == "🛍 Products":
        count = await get_stock_count("cdk_chatgpt")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"CDK GPT Plus (10+) | $4.00", callback_data="product_cdk_chatgpt")],
            [InlineKeyboardButton(text=f"CDK (K12) FOR SINGLE | $5.50", callback_data="product_cdk_chatgpt_single")]
        ])
        await message.answer(f"{ce('store')} <b>Products</b>", reply_markup=kb, parse_mode="HTML")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())
