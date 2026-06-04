import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="💬 Support")],
        [KeyboardButton(text="👛 Wallet"), KeyboardButton(text="🔗 API")],
        [KeyboardButton(text="🌐 Language")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 أهلاً بيك في Shop Bot\n\nاختار من القائمة:",
        reply_markup=main_menu
    )

@dp.message(F.text == "🛍 Products")
async def products(message: Message):
    await message.answer("📦 الأقسام:\n\n1️⃣ AI Accounts\n2️⃣ Design Accounts\n3️⃣ Emails")

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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
