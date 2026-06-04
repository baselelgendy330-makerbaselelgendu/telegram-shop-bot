import asyncio
import os
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="💬 Support")],
        [KeyboardButton(text="👛 Wallet"), KeyboardButton(text="🔗 API")],
        [KeyboardButton(text="🌐 Language")]
    ],
    resize_keyboard=True
)

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id SERIAL PRIMARY KEY,
                product TEXT NOT NULL,
                item_data TEXT NOT NULL,
                sold BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

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
