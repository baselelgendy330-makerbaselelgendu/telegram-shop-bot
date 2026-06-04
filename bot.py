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
GEMINI_IMAGE = "https://i.postimg.cc/0Qfr71mh/images-(1).jpg"

CHATGPT_PRODUCT = "ChatGPT Plus"
GEMINI_READY_PRODUCT = "Gemini Ready"
GEMINI_EMAIL_PRODUCT = "Gemini Email Activation"

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

PRODUCTS = {
    "chatgpt": {
        "stock_name": CHATGPT_PRODUCT,
        "image": CHATGPT_IMAGE,
        "usd": 5,
        "egp": 250,
        "type": "stock",
        "warranty_ar": "15 يوم",
        "warranty_en": "15 days",
    },
    "gemini_ready": {
        "stock_name": GEMINI_READY_PRODUCT,
        "image": GEMINI_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "stock",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    },
    "gemini_email": {
        "stock_name": GEMINI_EMAIL_PRODUCT,
        "image": GEMINI_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "activation",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    }
}

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
            product_key TEXT DEFAULT 'chatgpt',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("""
        ALTER TABLE deposits
        ADD COLUMN IF NOT EXISTS product_key TEXT DEFAULT 'chatgpt';
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

async def get_stock_count(product_key="chatgpt"):
    product = PRODUCTS[product_key]
    if product["type"] == "activation":
        return "∞"
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            product["stock_name"]
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
        await asyncio.sleep(0.08)
        try:
            await msg.edit_text(f"{title}\n\n{bar} {percent}%")
        except:
            pass
    return msg

def product_buttons(lang, counts):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | $5 | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | $6 | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
            [InlineKeyboardButton(text=f"👑 Gemini On Your Email | $6", callback_data="product_gemini_email")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | 250 جنيه | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | 300 جنيه | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
        [InlineKeyboardButton(text=f"👑 تفعيل Gemini على إيميلك | 300 جنيه", callback_data="product_gemini_email")],
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_products")]
    ])

def product_details_buttons(lang, product_key):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Now", callback_data=f"buy_{product_key}")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="refresh_products")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="refresh_products")]
    ])

def payment_buttons(lang, product_key):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data=f"pay_binance_{product_key}")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data=f"pay_vodafone_{product_key}")],
            [InlineKeyboardButton(text="🟣 InstaPay", callback_data=f"pay_instapay_{product_key}")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data=f"pay_vodafone_{product_key}")],
        [InlineKeyboardButton(text="🟣 انستا باي", callback_data=f"pay_instapay_{product_key}")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    photo = URLInputFile(CHATGPT_IMAGE)

    caption = (
        "🤖 Welcome to ChatGPT Shop\n\nPremium AI Accounts\nFast • Secure • Trusted"
        if lang == "en"
        else
        "🤖 أهلاً بك في ChatGPT Shop\n\nPremium AI Accounts\nFast • Secure • Trusted"
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
        "👛 YOUR WALLET\n━━━━━━━━━━━━━━\n\n"
        "💳 Deposit Methods:\n🟡 Binance UID\n🔴 Vodafone Cash\n🟣 InstaPay\n\n"
        "Choose deposit method from product checkout."
        if lang == "en"
        else
        "👛 المحفظة\n━━━━━━━━━━━━━━\n\n"
        "💳 طرق الدفع:\n🟡 بينانس UID\n🔴 فودافون كاش\n🟣 انستا باي\n\n"
        "اختار طريقة الدفع من صفحة المنتج."
    )

    await message.answer(text)

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await loading_bar(message, "🛍 Loading products..." if lang == "en" else "🛍 جاري تحميل المنتجات...")

    counts = {
        "chatgpt": await get_stock_count("chatgpt"),
        "gemini_ready": await get_stock_count("gemini_ready"),
        "gemini_email": "∞"
    }

    text = (
        "🛍 Available Products\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 $5 | 🛡 15 days\n\n"
        "💎 Gemini Pro 12M\n💰 $6 | 🛡 1 Year\n\n"
        "👑 Gemini On Your Email\n💰 $6 | 🛡 1 Year\n\n"
        "Choose a product below:"
        if lang == "en"
        else
        "🛍 المنتجات المتاحة\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 250 جنيه | 🛡 15 يوم\n\n"
        "💎 Gemini Pro 12M\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "👑 تفعيل Gemini على إيميلك\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "اختار المنتج:"
    )

    await message.answer(text, reply_markup=product_buttons(lang, counts))

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)

    counts = {
        "chatgpt": await get_stock_count("chatgpt"),
        "gemini_ready": await get_stock_count("gemini_ready"),
        "gemini_email": "∞"
    }

    text = (
        "🛍 Available Products\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 $5 | 🛡 15 days\n\n"
        "💎 Gemini Pro 12M\n💰 $6 | 🛡 1 Year\n\n"
        "👑 Gemini On Your Email\n💰 $6 | 🛡 1 Year\n\n"
        "Choose a product below:"
        if lang == "en"
        else
        "🛍 المنتجات المتاحة\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 250 جنيه | 🛡 15 يوم\n\n"
        "💎 Gemini Pro 12M\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "👑 تفعيل Gemini على إيميلك\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "اختار المنتج:"
    )

    await call.message.edit_text(text, reply_markup=product_buttons(lang, counts))
    await call.answer("Updated ✅")
    @dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("chatgpt")

    await call.message.answer_photo(
        photo=URLInputFile(CHATGPT_IMAGE),
        caption=(
            f"🤖 CHATGPT PLUS 1M\n\n"
            f"💰 Price: $5\n"
            f"📦 Stock: {count}\n"
            f"🛡 Warranty: 15 Days\n\n"
            f"📌 Private Account\n"
            f"📌 1 Month Subscription\n"
            f"📌 Instant Delivery"
            if lang == "en":
else:
            f"🤖 ChatGPT Plus 1M\n\n"
            f"💰 السعر: 250 جنيه\n"
            f"📦 المتوفر: {count}\n"
            f"🛡 الضمان: 15 يوم\n\n"
            f"📌 حساب خاص\n"
            f"📌 اشتراك شهر\n"
            f"📌 تسليم فوري"
        ),
        reply_markup=product_details_buttons(lang, "chatgpt")
    )

@dp.callback_query(F.data == "product_gemini_ready")
async def product_gemini_ready(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("gemini_ready")

    await call.message.answer_photo(
        photo=URLInputFile(GEMINI_IMAGE),
        caption=(
            f"💎 Gemini Pro 12M\n\n"
            f"💰 Price: $6\n"
            f"📦 Stock: {count}\n"
            f"🛡 Warranty: 1 Year\n\n"
            f"☁️ 5TB Storage\n"
            f"🤖 Gemini Advanced\n"
            f"⚡ Ready Account"
            if lang == "en"
            else
            f"💎 Gemini Pro 12M\n\n"
            f"💰 السعر: 300 جنيه\n"
            f"📦 المتوفر: {count}\n"
            f"🛡 الضمان: سنة كاملة\n\n"
            f"☁️ مساحة 5 تيرا\n"
            f"🤖 Gemini Advanced\n"
            f"⚡ حساب جاهز"
        ),
        reply_markup=product_details_buttons(lang, "gemini_ready")
    )

@dp.callback_query(F.data == "product_gemini_email")
async def product_gemini_email(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)

    await call.message.answer_photo(
        photo=URLInputFile(GEMINI_IMAGE),
        caption=(
            f"👑 Gemini Pro On Your Email\n\n"
            f"💰 Price: $6\n"
            f"🛡 Warranty: 1 Year\n\n"
            f"☁️ 5TB Storage\n"
            f"🤖 Gemini Advanced\n"
            f"🎬 Google Flow\n"
            f"💎 1000 Monthly Credits\n"
            f"👥 Add 5 Family Members\n"
            f"🔑 You Become The Owner\n\n"
            f"📧 Activated On Your Personal Email"
            if lang == "en"
            else
            f"👑 Gemini على إيميلك الشخصي\n\n"
            f"💰 السعر: 300 جنيه\n"
            f"🛡 الضمان: سنة كاملة\n\n"
            f"☁️ مساحة 5 تيرا بايت\n"
            f"🤖 Gemini Advanced\n"
            f"🎬 Google Flow\n"
            f"💎 1000 كريديت شهري\n"
            f"👥 إضافة 5 أشخاص\n"
            f"🔑 تصبح المالك الأساسي\n\n"
            f"📧 التفعيل على إيميلك الشخصي"
        ),
        reply_markup=product_details_buttons(lang, "gemini_email")
    )

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)

    product = PRODUCTS[product_key]

    await call.message.answer(
        (
            f"🛒 Checkout\n\n"
            f"💰 Price: ${product['usd']}\n\n"
            f"Choose payment method:"
            if lang == "en"
            else
            f"🛒 إتمام الشراء\n\n"
            f"💰 السعر: {product['egp']} جنيه\n\n"
            f"اختار طريقة الدفع:"
        ),
        reply_markup=payment_buttons(lang, product_key)
    )

@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")

    method = parts[1]
    product_key = "_".join(parts[2:])

    product = PRODUCTS[product_key]

    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval("""
        INSERT INTO deposits
        (telegram_id, method, amount, currency, product_key)
        VALUES($1,$2,$3,$4,$5)
        RETURNING id
        """,
        call.from_user.id,
        method,
        product["usd"],
        "USDT",
        product_key)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Approve",
                callback_data=f"approve_{dep_id}"
            ),
            InlineKeyboardButton(
                text="❌ Reject",
                callback_data=f"reject_{dep_id}"
            )
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"🛒 New Order #{dep_id}\n"
        f"User: @{call.from_user.username}\n"
        f"Product: {product_key}",
        reply_markup=kb
    )

    if method == "binance":
        text = f"🟡 Binance UID:\n{BINANCE_UID}"
    elif method == "vodafone":
        text = f"🔴 Vodafone Cash:\n{VODAFONE_CASH}"
    else:
        text = f"🟣 InstaPay:\n{INSTAPAY}"

    await call.message.answer(
        f"{text}\n\n📸 ابعت صورة إثبات الدفع."
    )

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    dep_id = int(call.data.split("_")[1])

    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow(
            "SELECT * FROM deposits WHERE id=$1",
            dep_id
        )

        product_key = dep["product_key"]

        if product_key == "gemini_email":

            await bot.send_message(
                dep["telegram_id"],
                "✅ تم تأكيد الدفع بنجاح\n\n"
                "📧 تفعيل Gemini على إيميلك الشخصي\n\n"
                f"يرجى التواصل مع الأدمن:\n{SUPPORT}"
            )

        else:

            item = await conn.fetchrow("""
            SELECT * FROM stock
            WHERE product=$1
            AND sold=false
            LIMIT 1
            """, PRODUCTS[product_key]["stock_name"])

            if item:
                await conn.execute(
                    "UPDATE stock SET sold=true WHERE id=$1",
                    item["id"]
                )

                await bot.send_message(
                    dep["telegram_id"],
                    f"✅ تم تأكيد الدفع\n\n"
                    f"📦 بيانات الحساب:\n\n"
                    f"{item['item_data']}"
                )

        await conn.execute(
            "UPDATE deposits SET status='approved' WHERE id=$1",
            dep_id
        )

    await call.message.edit_text(
        f"✅ Order #{dep_id} Approved"
    )

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    dep_id = int(call.data.split("_")[1])

    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow(
            "SELECT * FROM deposits WHERE id=$1",
            dep_id
        )

        if dep:
            await bot.send_message(
                dep["telegram_id"],
                "❌ تم رفض الطلب."
            )

    await call.message.edit_text(
        f"❌ Order #{dep_id} Rejected"
    )

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return

    await bot.forward_message(
        ADMIN_ID,
        message.chat.id,
        message.message_id
    )

    await message.answer(
        "📤 تم إرسال الإثبات للمراجعة."
    )

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    count = await get_stock_count("chatgpt")
    await message.answer(f"📦 ChatGPT Stock: {count}")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addstock", "").strip()

    items = [x.strip() for x in text.splitlines() if x.strip()]

    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute(
                "INSERT INTO stock(product,item_data) VALUES($1,$2)",
                CHATGPT_PRODUCT,
                item
            )

    await message.answer(f"✅ Added {len(items)} items")

@dp.message(F.text.in_(["💬 الدعم","💬 Support"]))
async def support(message: Message):
    await message.answer(f"💬 {SUPPORT}")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
