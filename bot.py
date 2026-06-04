import asyncio, os, asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, URLInputFile
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
VODAFONE_CASH = "01063467929"
INSTAPAY = "mahmoud2662000"
SUPPORT = "@VNV_I"

CHATGPT_IMAGE = "https://i.postimg.cc/g0GQwy2V/f413a409aabc9c298e8b6b461affaa99.jpg"

PRODUCT_NAME = "ChatGPT Plus"
PRICE_USDT = 5
PRICE_EGP = 250

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

async def ensure_user_by_id(user_id, username=None):
    async with db_pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users(telegram_id, username)
        VALUES($1, $2)
        ON CONFLICT (telegram_id) DO UPDATE SET username=$2
        """, user_id, username)

async def ensure_user(message: Message):
    await ensure_user_by_id(message.from_user.id, message.from_user.username)

async def get_lang(user_id):
    async with db_pool.acquire() as conn:
        lang = await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id)
    return lang or "ar"

async def get_stock_count():
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            PRODUCT_NAME
        )

async def loading_bar(message, title):
    msg = await message.answer(f"{title}\n\n▱▱▱▱▱▱▱▱▱▱ 0%")
    for bar, percent in [
        ("▰▱▱▱▱▱▱▱▱▱", 10),
        ("▰▰▱▱▱▱▱▱▱▱", 20),
        ("▰▰▰▱▱▱▱▱▱▱", 30),
        ("▰▰▰▰▱▱▱▱▱▱", 40),
        ("▰▰▰▰▰▱▱▱▱▱", 50),
        ("▰▰▰▰▰▰▱▱▱▱", 60),
        ("▰▰▰▰▰▰▰▱▱▱", 70),
        ("▰▰▰▰▰▰▰▰▱▱", 80),
        ("▰▰▰▰▰▰▰▰▰▱", 90),
        ("▰▰▰▰▰▰▰▰▰▰", 100),
    ]:
        await asyncio.sleep(0.12)
        try:
            await msg.edit_text(f"{title}\n\n{bar} {percent}%")
        except:
            pass
    return msg

def product_buttons(lang, count):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | $5 | 📦 {count}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | 250 جنيه | 📦 {count}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_products")]
    ])

def product_details_buttons(lang):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Now", callback_data="buy_chatgpt")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء الآن", callback_data="buy_chatgpt")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="refresh_products")]
    ])

def payment_buttons(lang):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data="pay_binance")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data="pay_vodafone")],
            [InlineKeyboardButton(text="🟣 InstaPay", callback_data="pay_instapay")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data="pay_binance")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data="pay_vodafone")],
        [InlineKeyboardButton(text="🟣 انستا باي", callback_data="pay_instapay")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    photo = URLInputFile(CHATGPT_IMAGE)

    caption = (
        "🤖 Welcome to ChatGPT Shop\n\n"
        "Premium AI Accounts\n"
        "Fast • Secure • Trusted"
        if lang == "en"
        else
        "🤖 أهلاً بك في ChatGPT Shop\n\n"
        "Premium AI Accounts\n"
        "Fast • Secure • Trusted"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=menu_en if lang == "en" else menu_ar
    )

@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
async def language(message: Message):
    await ensure_user(message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.answer("🌐 اختر اللغة / Choose language:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    await ensure_user_by_id(call.from_user.id, call.from_user.username)

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

    await loading_bar(message, "👛 Opening wallet..." if lang == "en" else "👛 جاري فتح المحفظة...")

    text = (
        "👛 YOUR WALLET\n"
        "━━━━━━━━━━━━━━\n\n"
        "💳 Deposit Methods:\n"
        "🟡 Binance UID\n"
        "🔴 Vodafone Cash\n"
        "🟣 InstaPay\n\n"
        "Choose deposit method:"
        if lang == "en"
        else
        "👛 المحفظة\n"
        "━━━━━━━━━━━━━━\n\n"
        "💳 طرق الدفع:\n"
        "🟡 بينانس UID\n"
        "🔴 فودافون كاش\n"
        "🟣 انستا باي\n\n"
        "اختار طريقة الدفع:"
    )

    await message.answer(text, reply_markup=payment_buttons(lang))

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)

    await loading_bar(message, "🛍 Loading products..." if lang == "en" else "🛍 جاري تحميل المنتجات...")
    count = await get_stock_count()

    text = (
        f"🛍 Available Products\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🤖 ChatGPT Plus 1M\n"
        f"💰 Price: $5\n"
        f"📦 Stock: {count} accounts\n"
        f"🛡 Warranty: 15 days\n\n"
        f"Choose a product below:"
        if lang == "en"
        else
        f"🛍 المنتجات المتاحة\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🤖 ChatGPT Plus 1M\n"
        f"💰 السعر: 250 جنيه\n"
        f"📦 المتوفر: {count} حساب\n"
        f"🛡 الضمان: 15 يوم\n\n"
        f"اختار المنتج:"
    )

    await message.answer(text, reply_markup=product_buttons(lang, count))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count()

    text = (
        f"🛍 Available Products\n━━━━━━━━━━━━━━\n\n"
        f"🤖 ChatGPT Plus 1M\n"
        f"💰 Price: $5\n"
        f"📦 Stock: {count} accounts\n"
        f"🛡 Warranty: 15 days\n\n"
        f"Choose a product below:"
        if lang == "en"
        else
        f"🛍 المنتجات المتاحة\n━━━━━━━━━━━━━━\n\n"
        f"🤖 ChatGPT Plus 1M\n"
        f"💰 السعر: 250 جنيه\n"
        f"📦 المتوفر: {count} حساب\n"
        f"🛡 الضمان: 15 يوم\n\n"
        f"اختار المنتج:"
    )

    await call.message.edit_text(text, reply_markup=product_buttons(lang, count))
    await call.answer("Updated ✅")

@dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count()
    photo = URLInputFile(CHATGPT_IMAGE)

    caption = (
        f"🤖 CHATGPT PLUS 1M\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💵 Price: $5.00\n"
        f"➕ Stock: {count} accounts\n"
        f"📊 Warranty: 15 days\n\n"
        f"💬 Description:\n"
        f"📌 Private account\n"
        f"📌 1 Month Plus subscription\n"
        f"📌 15 days warranty\n"
        f"📌 Delivery after payment approval\n\n"
        f"🛒 Press Buy Now to continue."
        if lang == "en"
        else
        f"🤖 CHATGPT PLUS 1M\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💵 السعر: 250 جنيه\n"
        f"➕ المتوفر: {count} حساب\n"
        f"📊 الضمان: 15 يوم\n\n"
        f"💬 الوصف:\n"
        f"📌 حساب خاص\n"
        f"📌 اشتراك Plus لمدة شهر\n"
        f"📌 ضمان 15 يوم\n"
        f"📌 التسليم بعد تأكيد الدفع\n\n"
        f"🛒 اضغط شراء الآن للمتابعة."
    )

    await call.message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=product_details_buttons(lang)
    )
    await call.answer()

@dp.callback_query(F.data == "buy_chatgpt")
async def buy_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count()

    if count <= 0:
        await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
        return

    text = (
        f"🛒 Checkout\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🤖 Product: ChatGPT Plus 1M\n"
        f"💰 Price: $5 / 250 EGP\n"
        f"🛡 Warranty: 15 days\n\n"
        f"Choose payment method:"
        if lang == "en"
        else
        f"🛒 إتمام الشراء\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🤖 المنتج: ChatGPT Plus 1M\n"
        f"💰 السعر: 250 جنيه / 5 USDT\n"
        f"🛡 الضمان: 15 يوم\n\n"
        f"اختار طريقة الدفع:"
    )

    await call.message.answer(text, reply_markup=payment_buttons(lang))
    await call.answer()

async def create_order(call: CallbackQuery, method, amount, currency):
    await ensure_user_by_id(call.from_user.id, call.from_user.username)

    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("""
        INSERT INTO deposits(telegram_id, method, amount, currency)
        VALUES($1,$2,$3,$4)
        RETURNING id
        """, call.from_user.id, method, amount, currency)

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
        f"Product: ChatGPT Plus 1M\n"
        f"Method: {method}\n"
        f"Amount: {amount} {currency}\n\n"
        f"بعد التأكد اضغط Approve & Deliver.",
        reply_markup=kb
    )

    return dep_id

@dp.callback_query(F.data == "pay_binance")
async def pay_binance(call: CallbackQuery):
    dep_id = await create_order(call, "Binance UID", 5, "USDT")
    await call.message.answer(
        f"🟡 Binance UID Payment\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💰 Amount: 5 USDT\n"
        f"🆔 Binance UID:\n`{BINANCE_UID}`\n\n"
        f"📸 بعد الدفع ابعت صورة الإثبات هنا.\n"
        f"🧾 Order ID: #{dep_id}",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data == "pay_vodafone")
async def pay_vodafone(call: CallbackQuery):
    dep_id = await create_order(call, "Vodafone Cash", 250, "EGP")
    await call.message.answer(
        f"🔴 Vodafone Cash Payment\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💰 Amount: 250 EGP\n"
        f"📱 Number:\n`{VODAFONE_CASH}`\n\n"
        f"📸 بعد الدفع ابعت صورة الإثبات هنا.\n"
        f"🧾 Order ID: #{dep_id}",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data == "pay_instapay")
async def pay_instapay(call: CallbackQuery):
    dep_id = await create_order(call, "InstaPay", 250, "EGP")
    await call.message.answer(
        f"🟣 InstaPay Payment\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💰 Amount: 250 EGP\n"
        f"🏦 InstaPay:\n`{INSTAPAY}`\n\n"
        f"📸 بعد الدفع ابعت صورة الإثبات هنا.\n"
        f"🧾 Order ID: #{dep_id}",
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
        """, PRODUCT_NAME)

        if not item:
            await call.message.edit_text("❌ لا يوجد مخزون متاح حاليًا")
            await bot.send_message(dep["telegram_id"], "❌ لا يوجد مخزون حاليًا. تواصل مع الدعم.")
            return

        await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)

    await bot.send_message(
        dep["telegram_id"],
        f"✅ تم تأكيد الدفع بنجاح\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🤖 ChatGPT Plus 1M\n"
        f"🛡 الضمان: 15 يوم\n\n"
        f"📦 بيانات الحساب:\n{item['item_data']}\n\n"
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
        await message.answer("/addstock\nemail:password\nemail2:password2")
        return

    items = [line.strip() for line in text.splitlines() if line.strip()]

    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute(
                "INSERT INTO stock(product, item_data) VALUES($1, $2)",
                PRODUCT_NAME,
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
