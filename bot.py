import asyncio
import os
import html
import re
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    URLInputFile,
    FSInputFile,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 6728595587

BINANCE_UID = "381880403"
SUPPORT = "@VNV_I"
BOT_NAME = "✦ 𝗔𝗜𝗫 𝗦𝘁𝗼𝗿𝗲 ✦"

# رابط صورة الهيدر الخضراء
AIX_HEADER_IMAGE = os.getenv("AIX_HEADER_IMAGE", "https://i.postimg.cc/m2xpGPZP/a-dark-futuristic-neon-digital-banner-promotiona.png")
AIX_HEADER_FILE = os.getenv("AIX_HEADER_FILE", "aix_header.jpg")

# --- قائمة الإيموجيات المتحركة ---
EMOJI = {
    "store": "5859297284029681680",
    "wallet": "6088990159334808217",
    "support": "6181322172263308706",
    "telegram": "6089099509202164251",
    "language": "5447410659077661506",
    "home": "5195140682590722632",
    "chatgpt": "5864127571754489150",
    "stock": "6089247294731852091",
    "shield": "5251203410396458957",
    "link": "5282843764451195532",
    "step": "5397782960512444700",
    "rocket": "6181682949516173646",
    "success": "6179298314953956852",
    "refresh": "5341715473882955310",
    "lightning": "6181421841274379029",
    "payment": "5352662091390008496",
    "binance": "6222208096257712941",
    "fire": "6266887773454603583",
    "announcement": "6181594486074777254
