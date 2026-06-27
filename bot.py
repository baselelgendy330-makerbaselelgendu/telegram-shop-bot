#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AIX Store Bot - Binance Pay Auto - SQLite"""
import os, asyncio, logging, html, re, time, uuid, base64, hmac, hashlib, json, urllib.parse
from typing import Optional

import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, URLInputFile, FSInputFile, BotCommand
from aiogram.exceptions import TelegramBadRequest

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "aix_store.db")
SUPPORT = "@VNV_I"
ADMIN_IDS = [6728595587, 7469507752]
CHANNEL_USERNAME = "@CDKK12_CHATGPT"
BINANCE_ID = "381880403"
BEP20_ADDRESS = "0x40ae850b17bb209142f70eb75fa6f3c3b0a757aa"
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

CDK_IMAGE = "https://i.postimg.cc/dQ7m0g1R/IMG-20260620-151545-816.jpg"
HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

CDK_DESC = ("ChatGPT K12 Edu 2-year package.\nFull of latest languages like Plus\n"
    "Can activate any account owner. Applies to Gmail ONLY.\n"
    "After ordering, you will receive a code. Account is on free plan.\n"
    "Web upgrade CDK: https://oaiteam.azx.us/")

PRODUCTS = {
    "cdk_chatgpt": {"stock_name": "CDK Activation Chatgpt 1Y", "title": "CDK GPT Plus (K12) 2 years", "image": CDK_IMAGE, "usd": 4.0, "min_qty": 10, "desc": CDK_DESC},
    "cdk_chatgpt_single": {"stock_name": "CDK Activation Chatgpt 1Y", "title": "CDK (K12) FOR SINGLE", "image": CDK_IMAGE, "usd": 5.5, "min_qty": 1, "desc": CDK_DESC + "\n\nNOTE: This product is sold with NO WARRANTY."},
}

SAFE = {"cart":"\U0001f6d2","back":"\U0001f519","wallet":"\U0001f4b0","binance":"\U0001f7e1","share":"\U0001f381","support":"\U0001fa7b","checkout":"\U0001f4b3","quantity":"\U0001f4e6","price":"\U0001f4b5","pencil":"\u270f","loading":"\u23f3","user":"\U0001f464","success":"\u2705","error":"\u274c","chatgpt":"\U0001f916","refresh":"\U0001f504","store":"\U0001f6cd","stock":"\u2795","sold":"\u2197","support_msg":"\U0001f4ac","telegram":"\u26a1","arrow_right":"\u27a1","users_group":"\U0001f465","money_fly":"\U0001f4b8","link_pin":"\U0001f4c7","announcement":"\U0001f6a8","check_anim":"\u2705","user_link":"\U0001f517","usdt":"\U0001f4b5","buy_cart":"\U0001f6d2","sparkles_pay":"\U0001f4b5","diamond_arrow":"\u27a1","secure_shield":"\U0001f6e1","user_new":"\U0001f464","ref_trend":"\U0001f4c8","ref_check":"\u2714","ref_hourglass":"\u231b","heart":"\u2764\ufe0f"}

def ce(k): return SAFE.get(k, "\u2705")
def esc(v): return html.escape(str(v), quote=False)
def fa(a):
    try: return str(int(a)) if float(a).is_integer() else str(a).rstrip("0").rstrip(".")
    except: return str(a)

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DATABASE_URL)
        _db.row_factory = aiosqlite.Row
    return _db

async def init_db():
    db = await get_db()
    await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, balance_usdt REAL DEFAULT 0, referred_by INTEGER, total_ref INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0, ref_counted INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    await db.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, method TEXT, amount REAL, currency TEXT, product_key TEXT DEFAULT 'cdk_chatgpt', status TEXT DEFAULT 'pending', quantity INTEGER DEFAULT 1, txid TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    await db.execute("CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT NOT NULL, item_data TEXT NOT NULL, sold INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    await db.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, order_id TEXT UNIQUE NOT NULL, product_key TEXT, quantity INTEGER DEFAULT 1, amount REAL, currency TEXT DEFAULT 'USDT', method TEXT DEFAULT 'binance_auto', status TEXT DEFAULT 'awaiting_payment', txid TEXT, paid_at TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    await db.commit()

async def get_user(user_id):
    db = await get_db()
    c = await db.execute("SELECT * FROM users WHERE telegram_id=?", (user_id,))
    r = await c.fetchone()
    return dict(r) if r else None

async def create_user(user_id, username=None, first_name=None, referrer_id=None):
    db = await get_db()
    existing = await get_user(user_id)
    if existing: return
    if referrer_id and referrer_id != user_id:
        c = await db.execute("SELECT telegram_id FROM users WHERE telegram_id=?", (referrer_id,))
        if await c.fetchone():
            await db.execute("INSERT INTO users (telegram_id, username, first_name, referred_by, ref_counted) VALUES (?, ?, ?, ?, 0)", (user_id, username, first_name, referrer_id))
            await db.commit()
            return
    await db.execute("INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)", (user_id, username, first_name))
    await db.commit()

async def is_banned(user_id):
    try:
        db = await get_db()
        c = await db.execute("SELECT is_banned FROM users WHERE telegram_id=?", (user_id,))
        r = await c.fetchone()
        return bool(r and r[0])
    except: return False

async def set_ban(user_id, banned):
    db = await get_db()
    await db.execute("UPDATE users SET is_banned=? WHERE telegram_id=?", (1 if banned else 0, user_id))
    await db.commit()

async def get_stats(user_id):
    db = await get_db()
    c = await db.execute("SELECT balance_usdt, total_ref FROM users WHERE telegram_id=?", (user_id,))
    r = await c.fetchone()
    return {"balance_usdt": r[0] or 0, "total_ref": r[1] or 0} if r else {"balance_usdt": 0, "total_ref": 0}

async def get_balance(user_id):
    try:
        db = await get_db()
        c = await db.execute("SELECT balance_usdt FROM users WHERE telegram_id=?", (user_id,))
        r = await c.fetchone()
        return float(r[0]) if r and r[0] else 0.0
    except: return 0.0

async def add_balance(user_id, amount):
    db = await get_db()
    await db.execute("UPDATE users SET balance_usdt=balance_usdt+? WHERE telegram_id=?", (amount, user_id))
    await db.commit()

async def process_ref(user_id):
    db = await get_db()
    c = await db.execute("SELECT referred_by, ref_counted FROM users WHERE telegram_id=?", (user_id,))
    user = await c.fetchone()
    if not user or not user[0] or user[1]: return {"processed": False}
    ref_id = user[0]
    await db.execute("UPDATE users SET ref_counted=1 WHERE telegram_id=?", (user_id,))
    await db.execute("UPDATE users SET total_ref=total_ref+1 WHERE telegram_id=?", (ref_id,))
    await db.commit()
    c = await db.execute("SELECT total_ref FROM users WHERE telegram_id=?", (ref_id,))
    r = await c.fetchone()
    new_total = r[0] if r else 0
    reward = new_total > 0 and new_total % 10 == 0
    if reward:
        await db.execute("UPDATE users SET balance_usdt=balance_usdt+0.5 WHERE telegram_id=?", (ref_id,))
        await db.commit()
    return {"processed": True, "referrer_id": ref_id, "new_total_ref": new_total, "reward_earned": reward, "more_to_earn": 10 - (new_total % 10)}

async def get_stock_count(product_key="cdk_chatgpt"):
    product = PRODUCTS.get(product_key, PRODUCTS["cdk_chatgpt"])
    db = await get_db()
    c = await db.execute("SELECT COUNT(*) FROM stock WHERE product=? AND sold=0", (product["stock_name"],))
    r = await c.fetchone()
    return r[0] or 0

async def get_total_sold(product_name):
    db = await get_db()
    c = await db.execute("SELECT COUNT(*) FROM stock WHERE product=? AND sold=1", (product_name,))
    r = await c.fetchone()
    return r[0] or 0

async def reserve_stock(product_name, qty):
    db = await get_db()
    c = await db.execute("SELECT id, item_data FROM stock WHERE product=? AND sold=0 ORDER BY id ASC LIMIT ?", (product_name, qty))
    items = await c.fetchall()
    if len(items) < qty: return None
    ids = [i[0] for i in items]
    ph = ",".join(["?"]*len(ids))
    await db.execute(f"UPDATE stock SET sold=1 WHERE id IN ({ph})", ids)
    await db.commit()
    return items

async def add_stock_items(product_name, items):
    db = await get_db()
    for item in items: await db.execute("INSERT INTO stock (product, item_data) VALUES (?, ?)", (product_name, item))
    await db.commit()
    return len(items)

async def create_order(user_id, method, amount, currency, product_key, qty, txid, status="pending"):
    db = await get_db()
    await db.execute("INSERT INTO deposits (telegram_id, method, amount, currency, product_key, status, quantity, txid) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, method, amount, currency, product_key, status, qty, txid))
    await db.commit()

async def get_all_users():
    db = await get_db()
    c = await db.execute("SELECT telegram_id FROM users")
    rows = await c.fetchall()
    return rows or []

async def create_bnb_order(user_id, order_id, product_key, qty, amount):
    db = await get_db()
    await db.execute("INSERT OR IGNORE INTO payments (telegram_id, order_id, product_key, quantity, amount, currency, method, status) VALUES (?, ?, ?, ?, ?, 'USDT', 'binance_auto', 'awaiting_payment')", (user_id, order_id, product_key, qty, amount))
    await db.commit()

async def update_bnb_txid(order_id, txid):
    db = await get_db()
    await db.execute("UPDATE payments SET txid=?, status='verifying' WHERE order_id=? AND status='awaiting_payment'", (txid, order_id))
    await db.commit()

async def get_payment_by_order(order_id):
    db = await get_db()
    c = await db.execute("SELECT * FROM payments WHERE order_id=?", (order_id,))
    r = await c.fetchone()
    return dict(r) if r else None

async def get_payment_by_txid(txid):
    db = await get_db()
    c = await db.execute("SELECT * FROM payments WHERE txid=? ORDER BY created_at DESC LIMIT 1", (txid,))
    r = await c.fetchone()
    return dict(r) if r else None

async def mark_delivered(order_id):
    db = await get_db()
    await db.execute("UPDATE payments SET status='delivered', paid_at=CURRENT_TIMESTAMP WHERE order_id=?", (order_id,))
    await db.commit()

# ═══════════════════════════════════════════════════════════
# BINANCE PAY SERVICE
# ═══════════════════════════════════════════════════════════
async def bnb_get(endpoint, params=None):
    url = f"https://api.binance.com{endpoint}"
    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    qs = urllib.parse.urlencode(params)
    sig = hmac.new(BINANCE_API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
    params["signature"] = sig
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, headers=headers) as r:
            data = await r.json()
            if r.status != 200: raise RuntimeError(f"Binance error: {data.get('msg', 'unknown')}")
            return data

async def get_bnb_transactions():
    now = int(time.time() * 1000)
    day = 24 * 60 * 60 * 1000
    result = await bnb_get("/sapi/v1/pay/transactions", {"type": 1, "startTime": now - (7 * day), "endTime": now, "limit": 100})
    return result.get("data", [])

async def verify_bnb_payment(txid, expected_order_id=None):
    try:
        txs = await get_bnb_transactions()
    except Exception as e: return {"found": False, "error": str(e)}
    for tx in txs:
        if tx.get("orderId") == txid or tx.get("transactionId") == txid:
            note = tx.get("note", "") or tx.get("memo", "")
            if expected_order_id and expected_order_id not in note: continue
            status = tx.get("status", "")
            is_paid = status in ("SUCCESS", "SETTLED")
            return {"found": True, "paid": is_paid, "amount": float(tx.get("amount", 0)), "currency": tx.get("currency", "USDT"), "buyer_name": tx.get("buyerName", ""), "note": note, "status": status}
    return {"found": False, "error": "Transaction not found"}

# ═══════════════════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════════════════
def home_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{ce('store')} Browse Products", callback_data="home_shop")],
        [InlineKeyboardButton(text=f"{ce('wallet')} Deposit", callback_data="home_deposit"), InlineKeyboardButton(text=f"{ce('user')} Wallet / Profile", callback_data="home_wallet")],
        [InlineKeyboardButton(text=f"{ce('support')} Support", callback_data="home_support"), InlineKeyboardButton(text=f"{ce('share')} Share & Earn", callback_data="home_share")],
    ])

def main_reply_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="\U0001f6cd Products"), KeyboardButton(text="\U0001fa7b Support")], [KeyboardButton(text="\U0001f4b0 Wallet"), KeyboardButton(text="\U0001f381 Share & Earn")]], resize_keyboard=True, is_persistent=True)

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{ce('back')} Main Menu", callback_data="home_main")]])

def product_kb(count):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"CDK GPT Plus (10+) | $4.00 | Stock: {count}", callback_data="product_cdk_chatgpt")],
        [InlineKeyboardButton(text=f"CDK (K12) FOR SINGLE | $5.50 | Stock: {count}", callback_data="product_cdk_chatgpt_single")],
        [InlineKeyboardButton(text=f"{ce('refresh')} Refresh", callback_data="refresh_products"), InlineKeyboardButton(text=f"{ce('back')} Back", callback_data="home_main")],
    ])

def product_detail_kb(pk):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{ce('cart')} Buy Now", callback_data=f"buy_{pk}")], [InlineKeyboardButton(text=f"{ce('back')} Back to Shop", callback_data="home_shop")]])

def checkout_kb(pk, qty):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{ce('wallet')} Pay from Wallet", callback_data=f"pay_wallet_{pk}_{qty}")],
        [InlineKeyboardButton(text="\u26a1 Binance Pay (Auto)", callback_data=f"pay_bnb_{pk}_{qty}")],
        [InlineKeyboardButton(text=f"{ce('binance')} Binance Pay (Manual)", callback_data=f"pay_binmanual_{pk}_{qty}")],
        [InlineKeyboardButton(text=f"{ce('usdt')} USDT (BEP20)", callback_data=f"pay_bep20_{pk}_{qty}")],
        [InlineKeyboardButton(text=f"{ce('back')} Back", callback_data=f"back_prod_{pk}")],
    ])

def deposit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{ce('price')} USDT Deposit", callback_data="dep_USDT")], [InlineKeyboardButton(text=f"{ce('back')} Back", callback_data="home_main")]])

def wallet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{ce('wallet')} Deposit", callback_data="home_deposit")], [InlineKeyboardButton(text=f"{ce('refresh')} Refresh", callback_data="home_wallet"), InlineKeyboardButton(text=f"{ce('back')} Main Menu", callback_data="home_main")]])

def force_sub_kb():
    url = CHANNEL_USERNAME.replace("@", "")
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="\U0001f4e2 Join Channel", url=f"https://t.me/{url}")], [InlineKeyboardButton(text="\U0001f504 Check Subscription", callback_data="check_sub")]])

def qty_kb(is_single=False):
    if is_single:
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")], [KeyboardButton(text="4"), KeyboardButton(text="5")], [KeyboardButton(text="\u274c Cancel")]], resize_keyboard=True, one_time_keyboard=True)
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="50")], [KeyboardButton(text="100"), KeyboardButton(text="200")], [KeyboardButton(text="\u274c Cancel")]], resize_keyboard=True, one_time_keyboard=True)

def admin_send_kb(target_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="\u2709\ufe0f Send Code to Customer", callback_data=f"sendprod_{target_id}")]])

# ═══════════════════════════════════════════════════════════
# BOT & DISPATCHER
# ═══════════════════════════════════════════════════════════
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_router = Router()
admin_router = Router()

# ═══════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════
class SecMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat = data.get("event_chat")
        if chat and chat.type in ["group", "supergroup"]: return
        user = data.get("event_from_user")
        if not user: return await handler(event, data)
        ref_id = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start "):
            args = event.text.split()
            if len(args) > 1 and args[1].isdigit(): ref_id = int(args[1])
        await create_user(user.id, user.username, user.first_name, ref_id)
        if isinstance(event, CallbackQuery) and event.data == "check_sub": return await handler(event, data)
        if user.id in ADMIN_IDS: return await handler(event, data)
        if await is_banned(user.id): return
        if CHANNEL_USERNAME != "@YourChannelUsername":
            try:
                m = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
                if m.status not in ["member", "administrator", "creator"]:
                    t = f"{ce('error')} Access Denied!\nYou must join {CHANNEL_USERNAME} to use this bot."
                    kb = force_sub_kb()
                    if isinstance(event, Message): await event.answer(t, reply_markup=kb, parse_mode="HTML")
                    elif isinstance(event, CallbackQuery): await event.message.answer(t, reply_markup=kb, parse_mode="HTML"); await event.answer()
                    return
                else: await process_ref(user.id)
            except: pass
        return await handler(event, data)

dp.message.middleware(SecMiddleware())
dp.callback_query.middleware(SecMiddleware())

# ═══════════════════════════════════════════════════════════
# USER HANDLERS
# ═══════════════════════════════════════════════════════════
deposit_wait = {}
buy_wait = {}
bnb_txid_wait = {}
admin_reply_wait = {}

def htext(name): return f"{ce('vip')} <b>AIX Store</b>\nHey, <b>{esc(name)}</b>!\n{ce('store')} Shop - Browse & buy\n{ce('wallet')} Deposit - Add funds\n{ce('support')} Support - Get help"
def plist(): return f"{ce('store')} <b>Available Products</b>\n{ce('chatgpt')} CDK Activation ChatGPT 2 Year\nPrice (10+): $4.00 | Single: $5.50"
def dtxt(product, qty): return f"{ce('success')} <b>Payment Confirmed!</b>\n{ce('vip')} {product['title']}\n{ce('quantity')} Qty: {qty}\nPlease wait... Admin will send your codes shortly!"

async def send_home(message):
    await safe_answer_photo(message, htext(message.from_user.first_name or "User"), reply_markup=home_kb())
    await message.answer("Main Menu", reply_markup=main_reply_kb())

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    deposit_wait.pop(message.from_user.id, None)
    buy_wait.pop(message.from_user.id, None)
    await send_home(message)

@user_router.message(Command("menu"))
async def cmd_menu(message: Message): await cmd_start(message)

@user_router.callback_query(F.data == "home_main")
async def cb_home(call: CallbackQuery):
    await call.answer()
    await safe_edit_or_answer(call.message, htext(call.from_user.first_name or "User"), reply_markup=home_kb())

@user_router.callback_query(F.data == "home_shop")
async def cb_shop(call: CallbackQuery):
    await call.answer()
    count = await get_stock_count("cdk_chatgpt")
    await safe_edit_or_answer(call.message, plist(), reply_markup=product_kb(count))

@user_router.callback_query(F.data == "refresh_products")
async def cb_refresh(call: CallbackQuery): await cb_shop(call)

@user_router.callback_query(F.data.startswith("product_"))
async def cb_product(call: CallbackQuery):
    await call.answer()
    pk = call.data.replace("product_", "")
    if pk not in PRODUCTS: return
    count = await get_stock_count("cdk_chatgpt")
    if count <= 0: await call.answer("Out of stock!", show_alert=True); return
    sold = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    p = PRODUCTS[pk]
    c = f"{ce('chatgpt')} <b>{p['title']}</b>\n{ce('price')} Price: <b>${p['usd']}</b>\n{ce('stock')} Stock: <b>{count}</b>\n{ce('sold')} Sold: <b>{sold}</b>\n\n{p['desc'][:200]}..."
    try: await call.message.delete()
    except: pass
    try: await call.message.answer_photo(URLInputFile(CDK_IMAGE), caption=c, reply_markup=product_detail_kb(pk), parse_mode="HTML")
    except: await call.message.answer(c, reply_markup=product_detail_kb(pk), parse_mode="HTML")

@user_router.callback_query(F.data.startswith("back_prod_"))
async def cb_back_prod(call: CallbackQuery):
    await call.answer()
    pk = call.data.replace("back_prod_", "")
    if pk not in PRODUCTS: return await cb_shop(call)
    count = await get_stock_count("cdk_chatgpt")
    sold = await get_total_sold(PRODUCTS["cdk_chatgpt"]["stock_name"])
    p = PRODUCTS[pk]
    c = f"{ce('chatgpt')} <b>{p['title']}</b>\n{ce('price')} Price: <b>${p['usd']}</b>\n{ce('stock')} Stock: <b>{count}</b>\n{ce('sold')} Sold: <b>{sold}</b>\n\n{p['desc'][:200]}..."
    await safe_edit_or_answer(call.message, c, reply_markup=product_detail_kb(pk))

@user_router.callback_query(F.data.startswith("buy_"))
async def cb_buy(call: CallbackQuery):
    await call.answer()
    pk = call.data.replace("buy_", "")
    buy_wait[call.from_user.id] = pk
    is_s = pk == "cdk_chatgpt_single"
    await call.message.answer(f"{ce('pencil')} Enter quantity to buy:", reply_markup=qty_kb(is_s), parse_mode="HTML")

async def rcv_qty(message):
    uid = message.from_user.id
    pk = buy_wait.pop(uid, None)
    if not pk: return
    is_s = pk == "cdk_chatgpt_single"
    mn = 1 if is_s else 10
    try:
        q = int(message.text.strip())
        if q < mn: await message.answer(f"{ce('error')} Minimum order is {mn}.", parse_mode="HTML"); return
    except: await message.answer(f"{ce('error')} Enter a valid number!", parse_mode="HTML"); return
    p = PRODUCTS[pk]
    total = float(p["usd"]) * q
    txt = f"{ce('checkout')} <b>Checkout</b>\n{ce('quantity')} Qty: <b>{q}</b>\n{ce('price')} Total: <b>${total:.2f}</b>\n\nChoose payment method:"
    await message.answer(txt, reply_markup=checkout_kb(pk, q), parse_mode="HTML")

@user_router.callback_query(F.data.startswith("pay_wallet_"))
async def cb_pay_wallet(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_wallet_", "").rsplit("_", 1)
    pk, qty = parts[0], int(parts[1])
    uid = call.from_user.id
    p = PRODUCTS[pk]
    total = float(p["usd"]) * qty
    bal = await get_balance(uid)
    if bal < total: await call.message.answer(f"{ce('error')} Not enough balance! You have {bal} USDT.", parse_mode="HTML"); return
    items = await reserve_stock(p["stock_name"], qty)
    if items is None: await call.message.answer(f"{ce('error')} Out of stock!", parse_mode="HTML"); return
    await add_balance(uid, -total)
    await create_order(uid, "wallet", total, "USDT", pk, qty, f"wallet_{int(time.time())}", "approved")
    await call.message.answer(dtxt(p, qty), parse_mode="HTML")
    codes = "\n".join([f"<code>{i[1]}</code>" for i in items])
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\U0001f6d2 Wallet Purchase!\nUser: {call.from_user.username or 'N/A'}\nID: <code>{uid}</code>\nProduct: {p['title']}\nQty: {qty}\nAmount: {total} USDT\n\n<b>Codes:</b>\n{codes}", parse_mode="HTML", reply_markup=admin_send_kb(uid))
        except: pass

@user_router.callback_query(F.data.startswith("pay_bnb_"))
async def cb_pay_bnb_auto(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_bnb_", "").rsplit("_", 1)
    pk, qty = parts[0], int(parts[1])
    uid = call.from_user.id
    p = PRODUCTS[pk]
    total = float(p["usd"]) * qty
    oid = f"AIX-{uid}-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    await create_bnb_order(uid, oid, pk, qty, total)
    bnb_txid_wait[uid] = oid
    t = (f"\u26a1 <b>Binance Pay (Auto Verification)</b>\n{ce('price')} Amount: <code>${total:.2f} USDT</code>\n{ce('quantity')} Qty: {qty}x {p['title']}\n\n"
         f"\U0001f4cb <b>Your Order ID:</b>\n<code>{oid}</code>\n\n"
         f"<b>Steps:</b>\n1\ufe0f\u20e3 Open <b>Binance App</b> → Pay → Send\n"
         f"2\ufe0f\u20e3 Enter Binance ID: <code>{BINANCE_ID}</code>\n"
         f"3\ufe0f\u20e3 Amount: <b>${total:.2f} USDT</b>\n"
         f"4\ufe0f\u20e3 In <b>Note</b> write: <code>{oid}</code>\n"
         f"5\ufe0f\u20e3 Complete transfer\n"
         f"6\ufe0f\u20e3 Copy <b>Binance Order ID</b> from receipt\n"
         f"7\ufe0f\u20e3 <b>Send it here</b>\n\n"
         f"\u23f3 Once confirmed, codes delivered <b>automatically!</b>")
    await safe_edit_or_answer(call.message, t, reply_markup=back_kb())

async def rcv_bnb_txid(message):
    uid = message.from_user.id
    txid = message.text.strip()
    oid = bnb_txid_wait.pop(uid, None)
    if not oid:
        order = await get_payment_by_txid(txid)
        if order: oid = order["order_id"]
        else: return
    else:
        await update_bnb_txid(oid, txid)
    vm = await message.answer(f"{ce('loading')} <b>Verifying payment...</b>\nTXID: <code>{txid}</code>\nPlease wait...", parse_mode="HTML")
    try:
        result = await verify_bnb_payment(txid, oid)
    except Exception as e:
        await vm.edit_text(f"{ce('error')} Verification error: {e}\nContact {SUPPORT}", parse_mode="HTML")
        return
    if not result["found"]:
        await vm.edit_text(f"{ce('error')} Transaction not found.\nMake sure you:\n1. Sent correct Binance Order ID\n2. Included Order ID in the note\n3. Wait 1-2 minutes\n\nNeed help? Contact {SUPPORT}", parse_mode="HTML")
        return
    if not result["paid"]:
        await vm.edit_text(f"{ce('error')} Payment not completed. Status: {result.get('status', 'unknown')}\nWait 1-2 minutes and try again.", parse_mode="HTML")
        return
    order = await get_payment_by_order(oid)
    if not order: await vm.edit_text(f"{ce('error')} Internal error. Contact support.", parse_mode="HTML"); return
    if order["status"] == "delivered": await vm.edit_text(f"{ce('success')} Already delivered! Check your chat history.", parse_mode="HTML"); return
    pk = order["product_key"]
    qty = order["quantity"]
    p = PRODUCTS[pk]
    items = await reserve_stock(p["stock_name"], qty)
    if items is None:
        await vm.edit_text(f"{ce('error')} Payment confirmed but out of stock! Admins notified.", parse_mode="HTML")
        for aid in ADMIN_IDS:
            try: await bot.send_message(aid, f"\U0001f6a8 PAID BUT OUT OF STOCK!\nOrder: <code>{oid}</code>\nUser: <code>{uid}</code>\nProduct: {p['title']}\nQty: {qty}", parse_mode="HTML")
            except: pass
        return
    await mark_delivered(oid)
    codes = "\n".join([f"<code>{i[1]}</code>" for i in items])
    dt = (f"{ce('success')} <b>Payment Verified & Auto-Delivered!</b>\n"
          f"{ce('vip')} <b>{p['title']}</b>\n{ce('quantity')} Qty: <b>{qty}</b>\n"
          f"{ce('checkout')} Order ID: <code>{oid}</code>\n"
          f"\U0001f4b0 Paid: <b>{result['amount']} {result['currency']}</b>\n\n"
          f"\U0001f511 <b>Your Codes:</b>\n{codes}\n\n{ce('heart')} Thank you for trusting AIX Store!")
    await vm.delete()
    await message.answer(dt, parse_mode="HTML")
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\u2705 Auto-Delivery!\nOrder: <code>{oid}</code>\nUser: <code>{uid}</code>\nProduct: {p['title']}\nQty: {qty}\n\nCodes:\n{codes}", parse_mode="HTML")
        except: pass

@user_router.callback_query(F.data.startswith("pay_binmanual_"))
async def cb_pay_binmanual(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_binmanual_", "").rsplit("_", 1)
    pk, qty = parts[0], int(parts[1])
    uid = call.from_user.id
    total = float(PRODUCTS[pk]["usd"]) * qty
    t = f"{ce('binance')} <b>Manual Binance Payment</b>\n{ce('price')} Amount: <b>${total:.2f} USDT</b>\n\nTransfer to Binance ID:\n<code>{BINANCE_ID}</code>\n\nAfter transfer, contact: {SUPPORT}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")], [InlineKeyboardButton(text=f"{ce('back')} Back", callback_data=f"back_prod_{pk}")]])
    await safe_edit_or_answer(call.message, t, reply_markup=kb)
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\U0001f7e1 Manual Binance Payment!\nUser: @{call.from_user.username or 'N/A'}\nID: <code>{uid}</code>\nProduct: {PRODUCTS[pk]['title']}\nQty: {qty}\nAmount: ${total} USDT", parse_mode="HTML", reply_markup=admin_send_kb(uid))
        except: pass

@user_router.callback_query(F.data.startswith("pay_bep20_"))
async def cb_pay_bep20(call: CallbackQuery):
    await call.answer()
    parts = call.data.replace("pay_bep20_", "").rsplit("_", 1)
    pk, qty = parts[0], int(parts[1])
    uid = call.from_user.id
    total = float(PRODUCTS[pk]["usd"]) * qty
    t = f"{ce('usdt')} <b>USDT (BEP20) Payment</b>\n{ce('price')} Amount: <b>${total:.2f} USDT</b>\n\nAddress (BEP20):\n<code>{BEP20_ADDRESS}</code>\n\nAfter transfer, contact: {SUPPORT}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")], [InlineKeyboardButton(text=f"{ce('back')} Back", callback_data=f"back_prod_{pk}")]])
    await safe_edit_or_answer(call.message, t, reply_markup=kb)
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\U0001f4b5 USDT BEP20 Payment!\nUser: @{call.from_user.username or 'N/A'}\nID: <code>{uid}</code>\nProduct: {PRODUCTS[pk]['title']}\nQty: {qty}\nAmount: ${total} USDT", parse_mode="HTML", reply_markup=admin_send_kb(uid))
        except: pass

@user_router.callback_query(F.data == "home_deposit")
async def cb_deposit(call: CallbackQuery):
    await call.answer()
    await safe_edit_or_answer(call.message, "\U0001f4b0 <b>Deposit Funds</b>\nSelect currency:", reply_markup=deposit_kb())

@user_router.callback_query(F.data == "home_support")
async def cb_support(call: CallbackQuery):
    await call.answer()
    await safe_edit_or_answer(call.message, f"{ce('support_msg')} <b>Quick support:</b>\n{SUPPORT}", reply_markup=back_kb())

@user_router.callback_query(F.data == "home_wallet")
async def cb_wallet(call: CallbackQuery):
    await call.answer()
    s = await get_stats(call.from_user.id)
    bal = s["balance_usdt"]
    refs = s["total_ref"]
    earnings = (refs // 10) * 0.50
    t = (f"{ce('wallet')} <b>Your Wallet</b>\n{ce('user')} Name: <b>{esc(call.from_user.first_name)}</b>\n"
         f"{ce('price')} Balance: <b>{bal} USDT</b>\n{ce('users_group')} Referrals: <b>{refs}</b>\n"
         f"{ce('money_fly')} Earnings: <b>{fa(earnings)} USDT</b>")
    await safe_edit_or_answer(call.message, t, reply_markup=wallet_kb())

@user_router.callback_query(F.data == "home_share")
async def cb_share(call: CallbackQuery):
    await call.answer()
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={call.from_user.id}"
    s = await get_stats(call.from_user.id)
    refs = s["total_ref"]
    earnings = (refs // 10) * 0.50
    t = (f"{ce('share')} <b>Share & Earn!</b>\nInvite 10 friends = <b>$0.50 USDT</b>!\n\n"
         f"{ce('users_group')} Total Invites: <b>{refs}</b>\n{ce('money_fly')} Earned: <b>{fa(earnings)} USDT</b>\n\n"
         f"{ce('link_pin')} <b>Your Link:</b>\n<code>{link}</code>")
    await safe_edit_or_answer(call.message, t, reply_markup=back_kb())

@user_router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery):
    try:
        m = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=call.from_user.id)
        if m.status in ["member", "administrator", "creator"]:
            await process_ref(call.from_user.id)
            await call.message.delete()
            await call.answer("\u2705 Subscribed! Welcome!", show_alert=True)
            await send_home(call.message)
        else: await call.answer("\u274c You haven't joined yet!", show_alert=True)
    except: await call.answer("Error checking subscription.", show_alert=True)

@user_router.callback_query(F.data == "dep_USDT")
async def cb_dep_usdt(call: CallbackQuery):
    await call.answer()
    deposit_wait[call.from_user.id] = "USDT"
    await safe_edit_or_answer(call.message, "\U0001f4b0 <b>Enter amount to deposit:</b>", reply_markup=back_kb())

async def rcv_deposit(message):
    uid = message.from_user.id
    if uid not in deposit_wait: return
    try:
        amt = float(message.text.strip())
        if amt < 1: raise ValueError
    except:
        await message.answer(f"{ce('error')} Enter a valid number > 1.", parse_mode="HTML")
        return
    deposit_wait.pop(uid, None)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{ce('binance')} Binance Pay \u2022 {fa(amt)} USDT", callback_data=f"topup_bin_{fa(amt)}_USDT")],
        [InlineKeyboardButton(text=f"{ce('usdt')} USDT (BEP20) \u2022 {fa(amt)} USDT", callback_data=f"topup_bep_{fa(amt)}_USDT")],
    ])
    await message.answer(f"\U0001f4b3 <b>Deposit {amt} USDT</b>\nChoose method:", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data.startswith("topup_bin_"))
async def cb_topup_bin(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amt = float(parts[2])
    uid = call.from_user.id
    t = f"{ce('binance')} <b>Binance Deposit</b>\nAmount: <b>{amt} USDT</b>\n\nTransfer to:\n<code>{BINANCE_ID}</code>\n\nAfter transfer, contact: {SUPPORT}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")], [InlineKeyboardButton(text=f"{ce('back')} Main Menu", callback_data="home_main")]])
    await safe_edit_or_answer(call.message, t, reply_markup=kb)
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\U0001f7e1 Top-up Request (Binance)!\nUser: @{call.from_user.username or 'N/A'}\nID: <code>{uid}</code>\nAmount: {amt} USDT", parse_mode="HTML")
        except: pass

@user_router.callback_query(F.data.startswith("topup_bep_"))
async def cb_topup_bep(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_")
    amt = float(parts[2])
    uid = call.from_user.id
    t = f"{ce('usdt')} <b>USDT (BEP20) Deposit</b>\nAmount: <b>{amt} USDT</b>\n\nAddress:\n<code>{BEP20_ADDRESS}</code>\n\nAfter transfer, contact: {SUPPORT}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Contact Support", url=f"https://t.me/{SUPPORT.replace('@', '')}")], [InlineKeyboardButton(text=f"{ce('back')} Main Menu", callback_data="home_main")]])
    await safe_edit_or_answer(call.message, t, reply_markup=kb)
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, f"\U0001f4b5 Top-up Request (BEP20)!\nUser: @{call.from_user.username or 'N/A'}\nID: <code>{uid}</code>\nAmount: {amt} USDT", parse_mode="HTML")
        except: pass

@user_router.message(F.text)
async def handle_text(message: Message):
    uid = message.from_user.id
    txt = message.text.strip()
    if txt in ["\u274c Cancel", "Cancel"]:
        deposit_wait.pop(uid, None); buy_wait.pop(uid, None); bnb_txid_wait.pop(uid, None)
        if uid in admin_reply_wait: admin_reply_wait.pop(uid, None)
        await message.answer(f"{ce('error')} Cancelled.", reply_markup=main_reply_kb(), parse_mode="HTML")
        await send_home(message)
        return
    if txt.startswith("/"): return
    if uid in buy_wait: await rcv_qty(message); return
    if uid in deposit_wait: await rcv_deposit(message); return
    if uid in bnb_txid_wait or (len(txt) >= 10 and txt.isalnum()):
        order = await get_payment_by_txid(txt) if not (uid in bnb_txid_wait) else None
        if uid in bnb_txid_wait or order: await rcv_bnb_txid(message); return
    if txt == "\U0001f6cd Products":
        count = await get_stock_count("cdk_chatgpt")
        await message.answer(plist(), reply_markup=product_kb(count), parse_mode="HTML")
    elif txt == "\U0001fa7b Support":
        await message.answer(f"{ce('support_msg')} Support:\n{SUPPORT}", reply_markup=back_kb(), parse_mode="HTML")
    elif txt == "\U0001f4b0 Wallet":
        s = await get_stats(uid); bal = s["balance_usdt"]; refs = s["total_ref"]; earnings = (refs // 10) * 0.50
        t = f"{ce('wallet')} <b>Your Wallet</b>\n{ce('user')} {esc(message.from_user.first_name)}\n{ce('price')} Balance: <b>{bal} USDT</b>\n{ce('users_group')} Refs: <b>{refs}</b>\n{ce('money_fly')} Earned: <b>{fa(earnings)} USDT</b>"
        await message.answer(t, reply_markup=wallet_kb(), parse_mode="HTML")
    elif txt == "\U0001f381 Share & Earn":
        me = await bot.get_me(); link = f"https://t.me/{me.username}?start={uid}"
        s = await get_stats(uid); refs = s["total_ref"]; earnings = (refs // 10) * 0.50
        t = f"{ce('share')} <b>Share & Earn!</b>\nInvite 10 friends = <b>$0.50</b>!\n{ce('users_group')} Invites: <b>{refs}</b>\n{ce('money_fly')} Earned: <b>{fa(earnings)} USDT</b>\n\n<code>{link}</code>"
        await message.answer(t, reply_markup=back_kb(), parse_mode="HTML")
    else: await send_home(message)

# ═══════════════════════════════════════════════════════════
# ADMIN HANDLERS
# ═══════════════════════════════════════════════════════════
@admin_router.message(Command("ban"))
async def cmd_ban(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.text.split()
    if len(parts) < 2: await message.answer(f"{ce('error')} Usage: <code>/ban user_id</code>", parse_mode="HTML"); return
    try: tid = int(parts[1]); await set_ban(tid, True); await message.answer(f"{ce('success')} Banned user {tid}!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

@admin_router.message(Command("unban"))
async def cmd_unban(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.text.split()
    if len(parts) < 2: await message.answer(f"{ce('error')} Usage: <code>/unban user_id</code>", parse_mode="HTML"); return
    try: tid = int(parts[1]); await set_ban(tid, False); await message.answer(f"{ce('success')} Unbanned user {tid}!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

@admin_router.message(Command("addbalance"))
async def cmd_addbal(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.text.split()
    if len(parts) < 3: await message.answer(f"{ce('error')} Usage: <code>/addbalance user_id amount</code>", parse_mode="HTML"); return
    try: tid = int(parts[1]); amt = float(parts[2]); await add_balance(tid, amt); await message.answer(f"{ce('success')} Added ${amt} to user {tid}!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

@admin_router.message(Command("send"))
async def cmd_send(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.html_text.split(" ", 2)
    if len(parts) < 3: await message.answer(f"{ce('error')} Usage: <code>/send user_id message</code>", parse_mode="HTML"); return
    try: tid = int(parts[1]); await bot.send_message(tid, f"\U0001f4e2 <b>Message from Admin:</b>\n{parts[2]}", parse_mode="HTML"); await message.answer(f"{ce('success')} Sent!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    txt = message.html_text.replace("/broadcast", "", 1).strip()
    if not txt: await message.answer(f"{ce('error')} Write message after command.", parse_mode="HTML"); return
    users = await get_all_users(); sent = 0
    for u in users:
        try: await bot.send_message(u[0], txt, parse_mode="HTML"); sent += 1; await asyncio.sleep(0.05)
        except: pass
    await message.answer(f"{ce('success')} Broadcast sent to {sent} users!", parse_mode="HTML")

@admin_router.message(Command("pull"))
async def cmd_pull(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit(): await message.answer(f"{ce('error')} Usage: <code>/pull qty</code>", parse_mode="HTML"); return
    qty = int(parts[1])
    if qty < 1: return
    pn = PRODUCTS["cdk_chatgpt"]["stock_name"]
    items = await reserve_stock(pn, qty)
    if items is None: await message.answer(f"{ce('error')} Not enough stock!", parse_mode="HTML"); return
    codes = "\n".join([f"<code>{i[1]}</code>" for i in items])
    await message.answer(f"{ce('success')} Pulled {qty} codes!\n\n{codes}", parse_mode="HTML")

@admin_router.message(Command("addstock"))
async def cmd_addstock(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    lines = [x.strip() for x in message.text.replace("/addstock", "").strip().splitlines() if x.strip()]
    if len(lines) < 2: await message.answer(f"{ce('error')} Format:\n<code>/addstock CDK</code>\n<code>CODE1</code>", parse_mode="HTML"); return
    pn = PRODUCTS["cdk_chatgpt"]["stock_name"]
    items = lines[1:]
    added = await add_stock_items(pn, items)
    total = await get_stock_count("cdk_chatgpt")
    await message.answer(f"{ce('success')} Added {added} codes!\nTotal stock: {total}", parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("sendprod_"))
async def cb_sendprod(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return await call.answer("Unauthorized!", show_alert=True)
    tid = int(call.data.split("_")[1])
    admin_reply_wait[call.from_user.id] = tid
    await call.message.reply(f"{ce('pencil')} Send the code/message for user <code>{tid}</code>:\n<i>Send text, photo, or file. Cancel: \u274c Cancel</i>", parse_mode="HTML")
    await call.answer()

@admin_router.message(F.photo | F.document)
async def admin_media(message: Message):
    uid = message.from_user.id
    if uid not in ADMIN_IDS or uid not in admin_reply_wait: return
    tid = admin_reply_wait.pop(uid)
    try:
        cap = message.html_text or ""
        new_cap = f"\U0001f381 <b>Your order is ready!</b>\n{cap}\n\n{ce('heart')} Thank you!"
        await message.copy_to(tid, caption=new_cap, parse_mode="HTML")
        await message.answer(f"{ce('success')} Sent to user {tid}!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

@admin_router.message(F.text)
async def admin_text_msg(message: Message):
    uid = message.from_user.id; txt = message.text.strip()
    if txt in ["\u274c Cancel", "Cancel"] and uid in admin_reply_wait:
        admin_reply_wait.pop(uid)
        await message.answer(f"{ce('error')} Cancelled.", reply_markup=main_reply_kb(), parse_mode="HTML"); return
    if uid not in ADMIN_IDS or uid not in admin_reply_wait: return
    tid = admin_reply_wait.pop(uid)
    try:
        msg = f"\U0001f381 <b>Your order is ready!</b>\n{message.html_text}\n\n{ce('heart')} Thank you!"
        await bot.send_message(tid, msg, parse_mode="HTML")
        await message.answer(f"{ce('success')} Sent to user {tid}!", parse_mode="HTML")
    except Exception as e: await message.answer(f"{ce('error')} Error: {e}", parse_mode="HTML")

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
async def on_startup():
    await init_db()
    await bot.set_my_commands([BotCommand(command="start", description="Start"), BotCommand(command="menu", description="Menu")])

async def main():
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
