import asyncio
import os
import html
import re
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, URLInputFile, FSInputFile, BotCommand, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587
BINANCE_UID = "381880403"
SUPPORT = "@VNV_I"
REFERRAL_REWARD = 0.10  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

buy_waiting = {}

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    # (نفس جداولك السابقة..)

# دالة الشراء الفوري (المحفظة) - عدلتها عشان تكون أسرع
@dp.callback_query(F.data.startswith("pay_wallet_"))
async def pay_wallet_product(call: CallbackQuery):
    await call.answer()
    data = call.data.replace("pay_wallet_", "")
    product_key, qty = data.rsplit("_", 1)
    qty = int(qty)
    lang = await get_lang(call.from_user.id)
    
    product = PRODUCTS.get(product_key)
    total_price = float(product["usd"]) * qty
    
    async with db_pool.acquire() as conn:
        balance = await get_wallet_balance(call.from_user.id)
        if balance < total_price:
            await call.message.answer("❌ رصيدك غير كافي للإتمام!" if lang=="ar" else "❌ Insufficient balance!")
            return
            
        # خصم الرصيد
        await conn.execute("UPDATE users SET balance_usdt = balance_usdt - $1 WHERE telegram_id=$2", total_price, call.from_user.id)
        
        # تسليم الأكواد
        items = await conn.fetch("SELECT id, item_data FROM stock WHERE product=$1 AND sold=false ORDER BY id ASC LIMIT $2", product["stock_name"], qty)
        if not items:
            await call.message.answer("❌ المخزون غير متاح حالياً - تم استرداد رصيدك.")
            await conn.execute("UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2", total_price, call.from_user.id)
            return

        await conn.execute("UPDATE stock SET sold=true WHERE id = ANY($1)", [i["id"] for i in items])
        codes = [i["item_data"] for i in items]
        await call.message.edit_text(get_delivery_text(lang, product, codes))

# دالة استقبال الكمية اليدوية - شلت منها شرط الـ Max
async def receive_custom_quantity(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    product_key = buy_waiting.get(user_id)
    try:
        qty = int(message.text.strip())
        if qty <= 0: raise ValueError
    except:
        await message.answer("❌ من فضلك اكتب رقم صحيح!")
        return
    buy_waiting.pop(user_id, None)
    # تخطي فحص المخزون في مرحلة الكتابة
    await proceed_to_checkout(message, product_key, qty)

async def proceed_to_checkout(call_obj, product_key: str, qty: int):
    lang = await get_lang(call_obj.from_user.id)
    product = PRODUCTS[product_key]
    total_price = float(product["usd"]) * qty
    text = f"📦 الكمية: {qty}\n💰 الإجمالي: {total_price}$\n\nاختار وسيلة الدفع:"
    # استخدمنا edit_text للـ message
    if isinstance(call_obj, Message):
        await call_obj.answer(text, reply_markup=checkout_payment_buttons(lang, product_key, qty))
    else:
        await call_obj.message.edit_text(text, reply_markup=checkout_payment_buttons(lang, product_key, qty))

