import asyncio, os, asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
VODAFONE_CASH = "01063467929"
SUPPORT = "@VNV_I"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

menu_ar = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 المنتجات"), KeyboardButton(text="💬 الدعم")],
        [KeyboardButton(text="👛 المحفظة"), KeyboardButton(text="🌐 اللغة")]
    ],
    resize_keyboard=True
)

menu_en = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="💬 Support")],
        [KeyboardButton(text="👛 Wallet"), KeyboardButton(text="🌐 Language")]
    ],
    resize_keyboard=True
)

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
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            method TEXT,
            amount NUMERIC,
            currency TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id SERIAL PRIMARY KEY,
            product TEXT NOT NULL,
            item_data TEXT NOT NULL,
            sold BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

async def ensure_user(message: Message):
    async with db_pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users(telegram_id, username)
        VALUES($1, $2)
        ON CONFLICT (telegram_id) DO UPDATE SET username=$2
        """, message.from_user.id, message.from_user.username)

async def get_lang(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id) or "ar"

async def get_stock_count():
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            "ChatGPT Plus"
        )

def product_list_keyboard(lang, count):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 ChatGPT Plus Account | $5 | 📦 {count}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text="🔄 Refresh products", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 حساب ChatGPT Plus | 250 جنيه | 📦 {count}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text="🔄 تحديث المنتجات", callback_data="refresh_products")]
    ])

def product_details_keyboard(lang):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Now", callback_data="buy_chatgpt")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء الآن", callback_data="buy_chatgpt")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="refresh_products")]
    ])

def payment_keyboard(lang):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Pay Binance UID", callback_data="pay_binance")],
            [InlineKeyboardButton(text="🔴 Pay Vodafone Cash", callback_data="pay_vodafone")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 دفع بينانس UID", callback_data="pay_binance")],
        [InlineKeyboardButton(text="🔴 دفع فودافون كاش", callback_data="pay_vodafone")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await message.answer(
        "👋 Welcome to Shop Bot\nChoose from menu:" if lang == "en" else "👋 أهلاً بيك في Shop Bot\nاختار من القائمة:",
        reply_markup=menu_en if lang == "en" else menu_ar
    )

@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
async def language(message: Message):
    await ensure_user(message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.answer("اختر اللغة / Choose language:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, call.from_user.id)
    await call.message.answer(
        "✅ Language changed to English" if lang == "en" else "✅ تم تغيير اللغة للعربية",
        reply_markup=menu_en if lang == "en" else menu_ar
    )
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet"]))
async def wallet(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT balance_usdt, balance_egp FROM users WHERE telegram_id=$1", message.from_user.id)

    await message.answer(
        f"👛 Your Wallet\n\nUSDT Balance: {user['balance_usdt']} USDT\nEGP Balance: {user['balance_egp']} EGP\n\nChoose deposit method:"
        if lang == "en"
        else f"👛 محفظتك\n\nرصيد USDT: {user['balance_usdt']} USDT\nرصيد مصري: {user['balance_egp']} جنيه\n\nاختار طريقة الإيداع:",
        reply_markup=payment_keyboard(lang)
    )

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    loading = await message.answer("⏳ Loading products..." if lang == "en" else "⏳ جاري تحميل المنتجات...")
    await asyncio.sleep(1)
    count = await get_stock_count()

    text = (
        "🛍 Available Products\n\n"
        "━━━━━━━━━━━━━━\n"
        "🤖 ChatGPT Plus Account\n"
        "💰 Price: $5\n"
        f"📦 Available: {count}\n"
        "🛡 Warranty: 15 days\n"
        "━━━━━━━━━━━━━━\n\n"
        "Choose a product below:"
    ) if lang == "en" else (
        "🛍 المنتجات المتاحة\n\n"
        "━━━━━━━━━━━━━━\n"
        "🤖 حساب ChatGPT Plus\n"
        "💰 السعر: 250 جنيه\n"
        f"📦 المتوفر: {count}\n"
        "🛡 الضمان: 15 يوم\n"
        "━━━━━━━━━━━━━━\n\n"
        "اختار المنتج من الزر بالأسفل:"
    )

    await loading.edit_text(text, reply_markup=product_list_keyboard(lang, count))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await call.message.edit_text("🔄 Refreshing..." if lang == "en" else "🔄 جاري التحديث...")
    await asyncio.sleep(1)
    count = await get_stock_count()

    text = (
        "🛍 Available Products\n\n🤖 ChatGPT Plus Account\n💰 Price: $5\n"
        f"📦 Available: {count}\n🛡 Warranty: 15 days"
    ) if lang == "en" else (
        "🛍 المنتجات المتاحة\n\n🤖 حساب ChatGPT Plus\n💰 السعر: 250 جنيه\n"
        f"📦 المتوفر: {count}\n🛡 الضمان: 15 يوم"
    )

    await call.message.edit_text(text, reply_markup=product_list_keyboard(lang, count))
    await call.answer("Updated ✅")

@dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count()

    text = (
        "🤖 ChatGPT Plus Account\n\n"
        "💰 Price: $5\n"
        f"📦 Available: {count}\n"
        "🛡 Warranty: 15 days\n\n"
        "Press Buy Now to continue."
    ) if lang == "en" else (
        "🤖 حساب ChatGPT Plus\n\n"
        "💰 السعر: 250 جنيه\n"
        f"📦 المتوفر: {count}\n"
        "🛡 الضمان: 15 يوم\n\n"
        "اضغط شراء الآن للمتابعة."
    )

    await call.message.edit_text(text, reply_markup=product_details_keyboard(lang))
    await call.answer()

@dp.callback_query(F.data == "buy_chatgpt")
async def buy_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count()

    if count <= 0:
        await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
        return

    text = (
        "🛒 Buy ChatGPT Plus Account\n\n"
        "💰 Price: $5\n"
        "🛡 Warranty: 15 days\n\n"
        "Choose payment method:"
    ) if lang == "en" else (
        "🛒 شراء حساب ChatGPT Plus\n\n"
        "💰 السعر: 250 جنيه\n"
        "🛡 الضمان: 15 يوم\n\n"
        "اختار طريقة الدفع:"
    )

    await call.message.edit_text(text, reply_markup=payment_keyboard(lang))
    await call.answer()

@dp.callback_query(F.data == "pay_binance")
async def pay_binance(call: CallbackQuery):
    await ensure_user(call.message)
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("""
        INSERT INTO deposits(telegram_id, method, amount, currency)
        VALUES($1,$2,$3,$4)
        RETURNING id
        """, call.from_user.id, "binance", 5, "usdt")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"💰 طلب شراء جديد #{dep_id}\n\n"
        f"User: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"Product: ChatGPT Plus\n"
        f"Method: Binance UID\n"
        f"Amount: 5 USDT\n\n"
        f"بعد ما تتأكد من الدفع اضغط Approve.",
        reply_markup=kb
    )

    await call.message.edit_text(
        f"🟡 Binance Payment\n\n"
        f"Send 5 USDT to Binance UID:\n`{BINANCE_UID}`\n\n"
        f"بعد التحويل ابعت صورة إثبات الدفع هنا.\n"
        f"Order ID: #{dep_id}",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data == "pay_vodafone")
async def pay_vodafone(call: CallbackQuery):
    await ensure_user(call.message)
    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("""
        INSERT INTO deposits(telegram_id, method, amount, currency)
        VALUES($1,$2,$3,$4)
        RETURNING id
        """, call.from_user.id, "vodafone", 250, "egp")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"💰 طلب شراء جديد #{dep_id}\n\n"
        f"User: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"Product: ChatGPT Plus\n"
        f"Method: Vodafone Cash\n"
        f"Amount: 250 EGP\n\n"
        f"بعد ما تتأكد من الدفع اضغط Approve.",
        reply_markup=kb
    )

    await call.message.edit_text(
        f"🔴 Vodafone Cash\n\n"
        f"Send 250 EGP to:\n`{VODAFONE_CASH}`\n\n"
        f"بعد التحويل ابعت صورة إثبات الدفع هنا.\n"
        f"Order ID: #{dep_id}",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer("📤 تم إرسال صورة الإثبات للأدمن للمراجعة.")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_deposit(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    dep_id = int(call.data.replace("approve_", ""))

    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if not dep or dep["status"] != "pending":
            await call.answer("Already handled")
            return

        item = await conn.fetchrow("""
            SELECT id, item_data FROM stock
            WHERE product=$1 AND sold=false
            ORDER BY id ASC
            LIMIT 1
        """, "ChatGPT Plus")

        if not item:
            await call.message.edit_text("❌ لا يوجد مخزون متاح حاليًا")
            await bot.send_message(dep["telegram_id"], "❌ الدفع اتقبل لكن لا يوجد مخزون حاليًا. تواصل مع الدعم.")
            return

        await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)

    await bot.send_message(
        dep["telegram_id"],
        f"✅ تم تأكيد الدفع بنجاح\n\n"
        f"🤖 ChatGPT Plus Account\n"
        f"🛡 الضمان: 15 يوم\n\n"
        f"📦 بيانات المنتج:\n"
        f"{item['item_data']}\n\n"
        f"شكراً لشرائك ❤️"
    )

    await call.message.edit_text(f"✅ Order #{dep_id} approved\n📦 Product delivered automatically")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject_deposit(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    dep_id = int(call.data.replace("reject_", ""))
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)

    if dep:
        await bot.send_message(dep["telegram_id"], "❌ تم رفض الطلب. تواصل مع الدعم.")
    await call.message.edit_text(f"❌ Order #{dep_id} rejected")
    await call.answer()

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    count = await get_stock_count()
    await message.answer(f"📦 المخزون الحالي: {count}")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addstock", "").strip()
    if not text:
        await message.answer("/addstock\nitem1\nitem2\nitem3")
        return

    items = [line.strip() for line in text.splitlines() if line.strip()]
    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute(
                "INSERT INTO stock(product, item_data) VALUES($1, $2)",
                "ChatGPT Plus",
                item
            )
    await message.answer(f"✅ تم إضافة {len(items)} عنصر للمخزون")

@dp.message(F.text.in_(["💬 الدعم", "💬 Support"]))
async def support(message: Message):
    await message.answer(f"💬 Support: {SUPPORT}")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
