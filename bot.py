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
SUPPORT = "@YourUsername"

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

def deposit_keyboard(lang="ar"):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data="dep_binance")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data="dep_vodafone")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data="dep_binance")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data="dep_vodafone")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    if lang == "en":
        await message.answer("👋 Welcome to Shop Bot\nChoose from menu:", reply_markup=menu_en)
    else:
        await message.answer("👋 أهلاً بيك في Shop Bot\nاختار من القائمة:", reply_markup=menu_ar)

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
        await conn.execute(
            "UPDATE users SET lang=$1 WHERE telegram_id=$2",
            lang, call.from_user.id
        )
    if lang == "en":
        await call.message.answer("✅ Language changed to English", reply_markup=menu_en)
    else:
        await call.message.answer("✅ تم تغيير اللغة للعربية", reply_markup=menu_ar)
    await call.answer()

@dp.message(F.text.in_(["👛 المحفظة", "👛 Wallet"]))
async def wallet(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT balance_usdt, balance_egp FROM users WHERE telegram_id=$1",
            message.from_user.id
        )

    if lang == "en":
        await message.answer(
            f"👛 Your Wallet\n\n"
            f"USDT Balance: {user['balance_usdt']} USDT\n"
            f"EGP Balance: {user['balance_egp']} EGP\n\n"
            f"Choose deposit method:",
            reply_markup=deposit_keyboard("en")
        )
    else:
        await message.answer(
            f"👛 محفظتك\n\n"
            f"رصيد USDT: {user['balance_usdt']} USDT\n"
            f"رصيد مصري: {user['balance_egp']} جنيه\n\n"
            f"اختار طريقة الإيداع:",
            reply_markup=deposit_keyboard("ar")
        )

@dp.callback_query(F.data == "dep_binance")
async def dep_binance(call: CallbackQuery):
    await call.message.answer(
        f"🟡 Binance Payment\n\n"
        f"Send to Binance UID:\n`{BINANCE_UID}`\n\n"
        f"بعد التحويل ابعت رسالة بالشكل ده:\n"
        f"/deposit binance 5 usdt\n\n"
        f"ثم ابعت صورة إثبات الدفع.",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data == "dep_vodafone")
async def dep_vodafone(call: CallbackQuery):
    await call.message.answer(
        f"🔴 Vodafone Cash\n\n"
        f"Send to:\n`{VODAFONE_CASH}`\n\n"
        f"بعد التحويل ابعت رسالة بالشكل ده:\n"
        f"/deposit vodafone 250 egp\n\n"
        f"ثم ابعت صورة إثبات الدفع.",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.message(Command("deposit"))
async def deposit(message: Message):
    await ensure_user(message)
    parts = message.text.split()

    if len(parts) != 4:
        await message.answer(
            "استخدم الأمر كده:\n"
            "/deposit binance 5 usdt\n"
            "أو\n"
            "/deposit vodafone 250 egp"
        )
        return

    method = parts[1].lower()
    amount = float(parts[2])
    currency = parts[3].lower()

    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("""
        INSERT INTO deposits(telegram_id, method, amount, currency)
        VALUES($1,$2,$3,$4)
        RETURNING id
        """, message.from_user.id, method, amount, currency)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"💰 طلب إيداع جديد #{dep_id}\n\n"
        f"User: @{message.from_user.username}\n"
        f"ID: {message.from_user.id}\n"
        f"Method: {method}\n"
        f"Amount: {amount} {currency}\n\n"
        f"انتظر صورة إثبات الدفع من العميل.",
        reply_markup=kb
    )

    await message.answer("✅ تم تسجيل طلب الإيداع. ابعت صورة إثبات الدفع الآن.")

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

        if dep["currency"] == "usdt":
            await conn.execute(
                "UPDATE users SET balance_usdt = balance_usdt + $1 WHERE telegram_id=$2",
                dep["amount"], dep["telegram_id"]
            )
        else:
            await conn.execute(
                "UPDATE users SET balance_egp = balance_egp + $1 WHERE telegram_id=$2",
                dep["amount"], dep["telegram_id"]
            )

        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)

    await bot.send_message(dep["telegram_id"], f"✅ تم قبول الإيداع وإضافة الرصيد.")
    await call.message.edit_text(f"✅ Deposit #{dep_id} approved")
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
        await bot.send_message(dep["telegram_id"], "❌ تم رفض طلب الإيداع. تواصل مع الدعم.")
    await call.message.edit_text(f"❌ Deposit #{dep_id} rejected")
    await call.answer()

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    async with db_pool.acquire() as conn:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            "ChatGPT Plus"
        )
    await message.answer(
        f"🤖 ChatGPT Plus\n\n"
        f"💰 5 USDT\n"
        f"🇪🇬 250 EGP\n"
        f"📦 Stock: {count}\n\n"
        f"زر الشراء هنضيفه بعد اختبار المحفظة."
    )

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    async with db_pool.acquire() as conn:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            "ChatGPT Plus"
        )
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
    asyncio.run(main())        """)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 أهلاً بيك في Shop Bot\n\nاختار من القائمة:", reply_markup=menu)

@dp.message(F.text == "🛍 Products")
async def products(message: Message):
    async with db_pool.acquire() as conn:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            "ChatGPT Plus"
        )

    await message.answer(
        f"📦 المنتج المتاح:\n\n"
        f"🤖 ChatGPT Plus\n"
        f"💰 السعر: 5 USDT\n"
        f"🇪🇬 السعر بالمصري: 250 EGP\n"
        f"📦 المتوفر: {count}\n\n"
        f"الدفع والشراء هنضيفهم في الخطوة الجاية."
    )

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    async with db_pool.acquire() as conn:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            "ChatGPT Plus"
        )

    await message.answer(f"📦 المخزون الحالي: {count}")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addstock", "").strip()

    if not text:
        await message.answer(
            "ابعت المخزون بالشكل ده:\n\n"
            "/addstock\n"
            "item1\n"
            "item2\n"
            "item3"
        )
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

@dp.message(F.text == "💬 Support")
async def support(message: Message):
    await message.answer("💬 الدعم: @YourUsername")

@dp.message(F.text == "👛 Wallet")
async def wallet(message: Message):
    await message.answer("👛 رصيدك الحالي: 0 USDT")

@dp.message(F.text == "🔗 API")
async def api(message: Message):
    await message.answer("🔗 API قريبًا")

@dp.message(F.text == "🌐 Language")
async def language(message: Message):
    await message.answer("🌐 اختر اللغة:\n🇪🇬 عربي\n🇬🇧 English")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
@dp.message(F.text == "🔗 API")
async def api(message: Message):
    await message.answer("🔗 API قريبًا")

@dp.message(F.text == "🌐 Language")
async def language(message: Message):
    await message.answer("🌐 اختر اللغة:\n🇪🇬 عربي\n🇬🇧 English")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
