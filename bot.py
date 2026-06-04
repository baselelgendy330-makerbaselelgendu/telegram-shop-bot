from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ البوت شغال بنجاح")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
