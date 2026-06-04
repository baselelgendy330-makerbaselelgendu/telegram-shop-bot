import asyncio
import os
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    URLInputFile,
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
        [KeyboardButton(text="👛 المحفظة"), KeyboardButton(text="🌐 اللغة")],
    ],
    resize_keyboard=True,
)

menu_en = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Products"), KeyboardButton(text="💬 Support")],
        [KeyboardButton(text="👛 Wallet"), KeyboardButton(text="🌐 Language")],
    ],
    resize_keyboard=True,
)

PRODUCTS = {
    "chatgpt": {
        "stock_name": CHATGPT_PRODUCT,
        "title_en": "ChatGPT Plus 1M",
        "title_ar": "ChatGPT Plus 1M",
        "image": CHATGPT_IMAGE,
        "usd": 5,
        "egp": 250,
        "type": "stock",
        "warranty_ar": "15 يوم",
        "warranty_en": "15 days",
    },
    "gemini_ready": {
        "stock_name": GEMINI_READY_PRODUCT,
        "title_en": "Gemini Pro 12M Ready Account",
        "title_ar": "Gemini Pro 12M حساب جاهز",
        "image": GEMINI_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "stock",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    },
    "gemini_email": {
        "stock_name": GEMINI_EMAIL_PRODUCT,
        "title_en": "Gemini Pro 12M On Your Email",
        "title_ar": "Gemini Pro 12M تفعيل على إيميلك",
        "image": GEMINI_IMAGE,
        "usd": 6,
        "egp": 300,
        "type": "activation",
        "warranty_ar": "سنة كاملة",
        "warranty_en": "1 Year",
    },
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

async def ensure_user_by_id(user_id: int, username: str | None = None):
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users(telegram_id, username)
            VALUES($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE SET username=$2
            """,
            user_id,
            username,
        )

async def ensure_user(message: Message):
    await ensure_user_by_id(message.from_user.id, message.from_user.username)

async def get_lang(user_id: int) -> str:
    async with db_pool.acquire() as conn:
        lang = await conn.fetchval("SELECT lang FROM users WHERE telegram_id=$1", user_id)
    return lang or "ar"

async def get_stock_count(product_key: str = "chatgpt"):
    product = PRODUCTS[product_key]
    if product["type"] == "activation":
        return "∞"
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM stock WHERE product=$1 AND sold=false",
            product["stock_name"],
        )

async def loading_bar(message: Message, title: str):
    msg = await message.answer(f"{title}\n\n▱▱▱▱▱▱▱▱▱▱ 0%")
    frames = [
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
    ]
    for bar, percent in frames:
        await asyncio.sleep(0.08)
        try:
            await msg.edit_text(f"{title}\n\n{bar} {percent}%")
        except Exception:
            pass
    return msg

def product_buttons(lang: str, counts: dict):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | $5 | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
            [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | $6 | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
            [InlineKeyboardButton(text="👑 Gemini On Your Email | $6", callback_data="product_gemini_email")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_products")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 ChatGPT Plus 1M | 250 جنيه | 📦 {counts['chatgpt']}", callback_data="product_chatgpt")],
        [InlineKeyboardButton(text=f"💎 Gemini Pro 12M | 300 جنيه | 📦 {counts['gemini_ready']}", callback_data="product_gemini_ready")],
        [InlineKeyboardButton(text="👑 تفعيل Gemini على إيميلك | 300 جنيه", callback_data="product_gemini_email")],
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_products")],
    ])

def product_details_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Now", callback_data=f"buy_{product_key}")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="refresh_products")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء الآن", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="refresh_products")],
    ])

def payment_buttons(lang: str, product_key: str):
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟡 Binance UID", callback_data=f"pay_binance_{product_key}")],
            [InlineKeyboardButton(text="🔴 Vodafone Cash", callback_data=f"pay_vodafone_{product_key}")],
            [InlineKeyboardButton(text="🟣 InstaPay", callback_data=f"pay_instapay_{product_key}")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 بينانس UID", callback_data=f"pay_binance_{product_key}")],
        [InlineKeyboardButton(text="🔴 فودافون كاش", callback_data=f"pay_vodafone_{product_key}")],
        [InlineKeyboardButton(text="🟣 انستا باي", callback_data=f"pay_instapay_{product_key}")],
    ])

async def product_counts():
    return {
        "chatgpt": await get_stock_count("chatgpt"),
        "gemini_ready": await get_stock_count("gemini_ready"),
        "gemini_email": "∞",
    }

@dp.message(CommandStart())
async def start(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    caption = (
        "🤖 Welcome to ChatGPT Shop\n\nPremium AI Accounts\nFast • Secure • Trusted"
        if lang == "en"
        else "🤖 أهلاً بك في ChatGPT Shop\n\nPremium AI Accounts\nFast • Secure • Trusted"
    )
    await message.answer_photo(
        photo=URLInputFile(CHATGPT_IMAGE),
        caption=caption,
        reply_markup=menu_en if lang == "en" else menu_ar,
    )

@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
async def language(message: Message):
    await ensure_user(message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇪🇬 عربي", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
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
        reply_markup=menu_en if lang == "en" else menu_ar,
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
        else "👛 المحفظة\n━━━━━━━━━━━━━━\n\n"
        "💳 طرق الدفع:\n🟡 بينانس UID\n🔴 فودافون كاش\n🟣 انستا باي\n\n"
        "اختار طريقة الدفع من صفحة المنتج."
    )
    await message.answer(text)

@dp.message(F.text.in_(["🛍 المنتجات", "🛍 Products"]))
async def products(message: Message):
    await ensure_user(message)
    lang = await get_lang(message.from_user.id)
    await loading_bar(message, "🛍 Loading products..." if lang == "en" else "🛍 جاري تحميل المنتجات...")
    counts = await product_counts()
    text = product_list_text(lang)
    await message.answer(text, reply_markup=product_buttons(lang, counts))

def product_list_text(lang: str):
    if lang == "en":
        return (
            "🛍 Available Products\n━━━━━━━━━━━━━━\n\n"
            "🤖 ChatGPT Plus 1M\n💰 $5 | 🛡 15 days\n\n"
            "💎 Gemini Pro 12M\n💰 $6 | 🛡 1 Year\n\n"
            "👑 Gemini On Your Email\n💰 $6 | 🛡 1 Year\n\n"
            "Choose a product below:"
        )
    return (
        "🛍 المنتجات المتاحة\n━━━━━━━━━━━━━━\n\n"
        "🤖 ChatGPT Plus 1M\n💰 250 جنيه | 🛡 15 يوم\n\n"
        "💎 Gemini Pro 12M\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "👑 تفعيل Gemini على إيميلك\n💰 300 جنيه | 🛡 سنة كاملة\n\n"
        "اختار المنتج:"
    )

@dp.callback_query(F.data == "refresh_products")
async def refresh_products(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    counts = await product_counts()
    try:
        await call.message.edit_text(product_list_text(lang), reply_markup=product_buttons(lang, counts))
    except Exception:
        await call.message.answer(product_list_text(lang), reply_markup=product_buttons(lang, counts))
    await call.answer("Updated ✅")

@dp.callback_query(F.data == "product_chatgpt")
async def product_chatgpt(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("chatgpt")
    if lang == "en":
        caption = (
            f"🤖 CHATGPT PLUS 1M\n━━━━━━━━━━━━━━\n\n"
            f"💰 Price: $5\n📦 Stock: {count}\n🛡 Warranty: 15 Days\n\n"
            f"📌 Private Account\n📌 1 Month Subscription\n📌 Instant Delivery"
        )
    else:
        caption = (
            f"🤖 ChatGPT Plus 1M\n━━━━━━━━━━━━━━\n\n"
            f"💰 السعر: 250 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: 15 يوم\n\n"
            f"📌 حساب خاص\n📌 اشتراك شهر\n📌 تسليم فوري"
        )
    await call.message.answer_photo(
        photo=URLInputFile(CHATGPT_IMAGE),
        caption=caption,
        reply_markup=product_details_buttons(lang, "chatgpt"),
    )
    await call.answer()

@dp.callback_query(F.data == "product_gemini_ready")
async def product_gemini_ready(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    count = await get_stock_count("gemini_ready")
    if lang == "en":
        caption = (
            f"💎 Gemini Pro 12M\n━━━━━━━━━━━━━━\n\n"
            f"💰 Price: $6\n📦 Stock: {count}\n🛡 Warranty: 1 Year\n\n"
            f"☁️ 5TB Storage\n🤖 Gemini Advanced\n⚡ Ready Account"
        )
    else:
        caption = (
            f"💎 Gemini Pro 12M\n━━━━━━━━━━━━━━\n\n"
            f"💰 السعر: 300 جنيه\n📦 المتوفر: {count}\n🛡 الضمان: سنة كاملة\n\n"
            f"☁️ مساحة 5 تيرا بايت\n🤖 Gemini Advanced\n⚡ حساب جاهز"
        )
    await call.message.answer_photo(
        photo=URLInputFile(GEMINI_IMAGE),
        caption=caption,
        reply_markup=product_details_buttons(lang, "gemini_ready"),
    )
    await call.answer()

@dp.callback_query(F.data == "product_gemini_email")
async def product_gemini_email(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    if lang == "en":
        caption = (
            f"👑 Gemini Pro On Your Email\n━━━━━━━━━━━━━━\n\n"
            f"💰 Price: $6\n🛡 Warranty: 1 Year\n\n"
            f"☁️ 5TB Storage\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 Monthly Credits\n"
            f"👥 Add 5 Family Members\n🔑 You Become The Owner\n\n"
            f"📧 Activated On Your Personal Email"
        )
    else:
        caption = (
            f"👑 Gemini على إيميلك الشخصي\n━━━━━━━━━━━━━━\n\n"
            f"💰 السعر: 300 جنيه\n🛡 الضمان: سنة كاملة\n\n"
            f"☁️ مساحة 5 تيرا بايت\n🤖 Gemini Advanced\n🎬 Google Flow\n💎 1000 كريديت شهري\n"
            f"👥 إضافة 5 أشخاص\n🔑 تصبح المالك الأساسي\n\n"
            f"📧 التفعيل على إيميلك الشخصي"
        )
    await call.message.answer_photo(
        photo=URLInputFile(GEMINI_IMAGE),
        caption=caption,
        reply_markup=product_details_buttons(lang, "gemini_email"),
    )
    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    product_key = call.data.replace("buy_", "")
    lang = await get_lang(call.from_user.id)
    product = PRODUCTS[product_key]
    if product["type"] == "stock":
        count = await get_stock_count(product_key)
        if count <= 0:
            await call.answer("Out of stock ❌" if lang == "en" else "المخزون غير متوفر ❌", show_alert=True)
            return
    text = (
        f"🛒 Checkout\n━━━━━━━━━━━━━━\n\n💰 Price: ${product['usd']} / {product['egp']} EGP\n\nChoose payment method:"
        if lang == "en"
        else f"🛒 إتمام الشراء\n━━━━━━━━━━━━━━\n\n💰 السعر: {product['egp']} جنيه / {product['usd']} USDT\n\nاختار طريقة الدفع:"
    )
    await call.message.answer(text, reply_markup=payment_buttons(lang, product_key))
    await call.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def pay_product(call: CallbackQuery):
    parts = call.data.split("_")
    method = parts[1]
    product_key = "_".join(parts[2:])
    product = PRODUCTS[product_key]
    currency = "USDT" if method == "binance" else "EGP"
    amount = product["usd"] if method == "binance" else product["egp"]

    async with db_pool.acquire() as conn:
        dep_id = await conn.fetchval(
            """
            INSERT INTO deposits (telegram_id, method, amount, currency, product_key)
            VALUES($1,$2,$3,$4,$5)
            RETURNING id
            """,
            call.from_user.id,
            method,
            amount,
            currency,
            product_key,
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve_{dep_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{dep_id}"),
        ]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"🛒 New Order #{dep_id}\n"
        f"User: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"Product: {product['title_en']}\n"
        f"Method: {method}\n"
        f"Amount: {amount} {currency}",
        reply_markup=kb,
    )

    if method == "binance":
        pay_text = f"🟡 Binance UID:\n`{BINANCE_UID}`\n\n💰 Amount: {amount} USDT"
    elif method == "vodafone":
        pay_text = f"🔴 Vodafone Cash:\n`{VODAFONE_CASH}`\n\n💰 Amount: {amount} EGP"
    else:
        pay_text = f"🟣 InstaPay:\n`{INSTAPAY}`\n\n💰 Amount: {amount} EGP"

    await call.message.answer(
        f"{pay_text}\n\n📸 بعد الدفع ابعت صورة إثبات الدفع هنا.\n🧾 Order ID: #{dep_id}",
        parse_mode="Markdown",
    )
    await call.answer()

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if not dep or dep["status"] != "pending":
            await call.answer("Already handled")
            return
        product_key = dep["product_key"]
        product = PRODUCTS[product_key]
        if product["type"] == "activation":
            await bot.send_message(
                dep["telegram_id"],
                f"✅ تم تأكيد الدفع بنجاح\n━━━━━━━━━━━━━━\n\n"
                f"📧 تفعيل Gemini على إيميلك الشخصي\n\n"
                f"يرجى التواصل مع الأدمن لإتمام التفعيل:\n{SUPPORT}\n\nشكراً لثقتك ❤️",
            )
        else:
            item = await conn.fetchrow(
                """
                SELECT id, item_data FROM stock
                WHERE product=$1 AND sold=false
                ORDER BY id ASC
                LIMIT 1
                """,
                product["stock_name"],
            )
            if not item:
                await call.message.edit_text("❌ لا يوجد مخزون متاح حاليًا")
                await bot.send_message(dep["telegram_id"], "❌ لا يوجد مخزون حاليًا. تواصل مع الدعم.")
                return
            await conn.execute("UPDATE stock SET sold=true WHERE id=$1", item["id"])
            await bot.send_message(
                dep["telegram_id"],
                f"✅ تم تأكيد الدفع\n━━━━━━━━━━━━━━\n\n📦 بيانات الحساب:\n\n{item['item_data']}\n\nشكراً لشرائك ❤️",
            )
        await conn.execute("UPDATE deposits SET status='approved' WHERE id=$1", dep_id)
    await call.message.edit_text(f"✅ Order #{dep_id} Approved")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    dep_id = int(call.data.split("_")[1])
    async with db_pool.acquire() as conn:
        dep = await conn.fetchrow("SELECT * FROM deposits WHERE id=$1", dep_id)
        if dep:
            await conn.execute("UPDATE deposits SET status='rejected' WHERE id=$1", dep_id)
            await bot.send_message(dep["telegram_id"], "❌ تم رفض الطلب. تواصل مع الدعم.")
    await call.message.edit_text(f"❌ Order #{dep_id} Rejected")
    await call.answer()

@dp.message(F.photo)
async def payment_photo(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer("📤 تم إرسال الإثبات للمراجعة.")

@dp.message(Command("stock"))
async def stock_count(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    chatgpt = await get_stock_count("chatgpt")
    gemini = await get_stock_count("gemini_ready")
    await message.answer(f"📦 ChatGPT Stock: {chatgpt}\n💎 Gemini Ready Stock: {gemini}")

@dp.message(Command("addstock"))
async def add_stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addstock", "").strip()

    if not text:
        await message.answer(
            "📦 إضافة استوك:\n\n"
            "ChatGPT:\n"
            "/addstock chatgpt\n"
            "email1:pass1\n"
            "email2:pass2\n\n"
            "Gemini Ready Account:\n"
            "/addstock gemini\n"
            "email1:pass1\n"
            "email2:pass2\n\n"
            "ملاحظة: منتج Gemini على الإيميل الشخصي لا يحتاج استوك."
        )
        return

    lines = [x.strip() for x in text.splitlines() if x.strip()]
    product_type = lines[0].lower()

    aliases = {
        "chatgpt": "chatgpt",
        "chat": "chatgpt",
        "gpt": "chatgpt",
        "gemini": "gemini_ready",
        "gemini_ready": "gemini_ready",
        "gemini-ready": "gemini_ready",
    }

    product_key = aliases.get(product_type)

    if not product_key:
        await message.answer(
            "❌ نوع المنتج غير صحيح. استخدم:\n"
            "/addstock chatgpt\n"
            "أو\n"
            "/addstock gemini"
        )
        return

    items = lines[1:]

    if not items:
        await message.answer("❌ اكتب الحسابات تحت اسم المنتج، كل حساب في سطر.")
        return

    async with db_pool.acquire() as conn:
        for item in items:
            await conn.execute(
                "INSERT INTO stock(product,item_data) VALUES($1,$2)",
                PRODUCTS[product_key]["stock_name"],
                item,
            )

    product_label = "ChatGPT Plus" if product_key == "chatgpt" else "Gemini Ready"
    await message.answer(f"✅ تم إضافة {len(items)} حساب إلى {product_label}")

@dp.message(F.text.in_(["💬 الدعم", "💬 Support"]))
async def support(message: Message):
    await message.answer(f"💬 {SUPPORT}")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
