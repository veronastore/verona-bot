"""
Verona Store Telegram Bot — с автоперезапуском
"""
 
import logging
import asyncio
import time
import httpx
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
 
BOT_TOKEN = "8851790776:AAFBvLHCYIXLTweEf1hc-ewuyPZoG8a9LCw"
MANAGER_CHAT_ID = 825970353
CHANNEL_ID = "@veronastore_ru"
MOSCOW_TZ = timezone(timedelta(hours=3))
 
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
 
WAITING_NAME, WAITING_PHONE = range(2)
 
COLLECTIONS = {
    "verona_design": {
        "title": "Verona Design",
        "desc": "Премиальная линейка с выразительным дизайном и богатым выбором отделок.",
        "items": ["Frame", "My Time", "Optima+", "Classic", "Ampio", "Quadro+"],
        "url": "https://verona-store.ru"
    },
    "verona_basic": {
        "title": "Verona Basic",
        "desc": "Чистые линии, практичность и доступность без компромисса по качеству.",
        "items": ["Shape", "Dune", "Quadro", "Зеркала EDGE", "Зеркала UPPER"],
        "url": "https://verona-store.ru"
    },
    "brenta": {
        "title": "Brenta",
        "desc": "Итальянская коллекция с авторским характером и архитектурной эстетикой.",
        "items": ["Verso", "Lester", "Scala", "Manhattan", "Fusion", "Fly", "Simple"],
        "url": "https://verona-store.ru"
    },
}
 
FAQ = {
    "faq_price": "💰 *Цены*\n\nСтоимость зависит от коллекции, размеров и комплектации.\nДля точного расчёта свяжитесь с менеджером.",
    "faq_delivery": "🚚 *Доставка*\n\nДоставляем по всей России.\nСроки: 4–8 недель с момента подтверждения заказа.",
    "faq_showroom": "🏠 *Шоурум*\n\nМосква\n📞 8 495 998-60-60\n✉️ info@verona-store.ru\n🕐 Пн–Пт 10:00–19:00, Сб 11:00–17:00",
    "faq_install": "🔧 *Монтаж*\n\nРаботаем с проверенными бригадами в Москве и МО.\nОбсуждается индивидуально при заказе.",
}
 
WEEKLY_SCHEDULE = {
    0: {"brand": "Verona & Brenta", "topics": [
        "Напиши пост о коллекции Frame от Verona Design — минималистичный дизайн, чистые линии.",
        "Напиши пост о коллекции Verso от Brenta — итальянский характер, авторская эстетика.",
        "Напиши пост о коллекции My Time от Verona Design — уют, персональный стиль.",
        "Напиши пост о коллекции Scala от Brenta — современная выразительность.",
    ]},
    1: {"brand": "Итальянская керамика", "topics": [
        "Напиши пост о бренде Catalano — итальянская керамика с 1967 года, инновационная глазурь CATAglaze.",
        "Напиши пост о бренде Alice Ceramica — смелые формы, яркие цвета.",
        "Напиши пост о бренде Ceramica Flaminia — итальянское производство с 1956 года.",
        "Напиши пост о бренде Scarabeo — нестандартные раковины, более 400 моделей.",
        "Напиши пост о бренде Ceramica Cielo — поэзия в керамике, пастельные цвета.",
        "Напиши пост о бренде GSI Ceramica — функциональность и стиль.",
        "Напиши пост о бренде Kerasan — сочетание традиций и инноваций.",
    ]},
    2: {"brand": "Смесители и сантехника", "topics": [
        "Напиши пост о бренде Gessi — итальянские смесители ручной сборки, бронза и матовое золото.",
        "Напиши пост о бренде Dornbracht — немецкие смесители класса люкс с 1950 года.",
        "Напиши пост о бренде Fantini — итальянские смесители с 1947 года, ручная полировка.",
        "Напиши пост о бренде CEA Design — баланс технологии и красоты.",
        "Напиши пост о бренде Salini — российский производитель из литьевого камня.",
    ]},
    3: {"brand": "Ванны и душевые", "topics": [
        "Напиши пост о бренде Bette — немецкие стальные ванны, 30 лет гарантии.",
        "Напиши пост о бренде Valdama — итальянская керамика ручной работы.",
        "Напиши пост о бренде Antonio Lupi — авангардный дизайн, натуральные материалы.",
        "Напиши пост о бренде Falper — итальянские ванны из дерева, камня и металла.",
        "Напиши пост о бренде Radaway — душевые ограждения, надёжное качество.",
    ]},
    4: {"brand": "Аксессуары и радиаторы", "topics": [
        "Напиши пост о бренде Decor Walther — немецкие аксессуары ручной работы, хром и матовое золото.",
        "Напиши пост о бренде Duravit — немецкий производитель с 200-летней историей.",
        "Напиши пост о бренде Broner Radiator — дизайнерские радиаторы, тепло и стиль.",
    ]},
    5: {"brand": "Интерьерное вдохновение", "topics": [
        "Напиши пост с советами как правильно спланировать ванную комнату.",
        "Напиши пост о трендах в дизайне ванных комнат 2025 года.",
        "Напиши пост о том как выбрать мебель для ванной.",
        "Напиши пост об уходе за мебелью и сантехникой премиум-класса.",
    ]},
    6: {"brand": "Шоурум и сервис", "topics": [
        "Напиши пост-приглашение в шоурум Verona Store в Москве.",
        "Напиши пост о преимуществах покупки через Verona Store — опыт 15 лет.",
        "Напиши пост о бесплатной консультации дизайнера в Verona Store.",
    ]},
}
 
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛋 Коллекции", callback_data="collections"),
         InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton("📞 Консультация", callback_data="consult"),
         InlineKeyboardButton("🌐 Сайт", url="https://verona-store.ru")],
    ])
 
def collections_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Verona Design", callback_data="col_verona_design")],
        [InlineKeyboardButton("Verona Basic", callback_data="col_verona_basic")],
        [InlineKeyboardButton("Brenta", callback_data="col_brenta")],
        [InlineKeyboardButton("← Назад", callback_data="back_main")],
    ])
 
def faq_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Цены", callback_data="faq_price")],
        [InlineKeyboardButton("🚚 Доставка", callback_data="faq_delivery")],
        [InlineKeyboardButton("🏠 Шоурум", callback_data="faq_showroom")],
        [InlineKeyboardButton("🔧 Монтаж", callback_data="faq_install")],
        [InlineKeyboardButton("← Назад", callback_data="back_main")],
    ])
 
def cancel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="cancel_consult")]])
 
async def generate_post(topic: str, brand: str) -> str:
    system = (
        f"Ты контент-менеджер магазина Verona Store (verona-store.ru). "
        f"Пишешь живые, интересные посты для Telegram-канала о премиальной мебели для ванных комнат. "
        f"Сегодняшняя тема — {brand}. "
        f"Стиль: живой, вдохновляющий, как будто пишет человек а не робот. Без штампов. "
        f"Длина: 5-7 предложений. "
        f"В конце добавь:\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot\n\n"
        f"Используй 1-2 эмодзи. Пиши на русском языке."
    )
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 600,
                    "system": system,
                    "messages": [{"role": "user", "content": topic}]
                }
            )
        return r.json()["content"][0]["text"]
    except Exception as e:
        logging.error(f"Ошибка генерации поста: {e}")
        return None
 
async def publish_daily_post(app: Application):
    now = datetime.now(MOSCOW_TZ)
    weekday = now.weekday()
    day_of_year = now.timetuple().tm_yday
    schedule = WEEKLY_SCHEDULE[weekday]
    topics = schedule["topics"]
    topic = topics[day_of_year % len(topics)]
    brand = schedule["brand"]
    logging.info(f"📝 Генерирую пост: {brand}")
    post = await generate_post(topic, brand)
    if post:
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=post)
            logging.info(f"✅ Пост опубликован! Тема: {brand}")
            if MANAGER_CHAT_ID:
                await app.bot.send_message(
                    MANAGER_CHAT_ID,
                    f"✅ Пост опубликован!\n\n📌 {brand}\n\n{post[:300]}..."
                )
        except Exception as e:
            logging.error(f"Ошибка публикации: {e}")
 
async def scheduler(app: Application):
    logging.info("📅 Планировщик запущен — посты каждый день в 10:00 МСК")
    while True:
        try:
            now = datetime.now(MOSCOW_TZ)
            target = now.replace(hour=10, minute=0, second=0, microsecond=0)
            if now >= target:
                target = target + timedelta(days=1)
            wait_seconds = (target - now).total_seconds()
            h = int(wait_seconds // 3600)
            m = int((wait_seconds % 3600) // 60)
            logging.info(f"⏰ Следующий пост через {h}ч {m}м")
            await asyncio.sleep(wait_seconds)
            await publish_daily_post(app)
        except Exception as e:
            logging.error(f"Ошибка планировщика: {e}. Продолжаю...")
            await asyncio.sleep(60)
 
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"Добро пожаловать, {name}! 👋\n\nЯ бот *Verona Store* — официального дилера премиальной мебели для ванных комнат.\n\nВыберите, что вас интересует:",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )
 
async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "back_main":
        await q.edit_message_text("Чем могу помочь?", reply_markup=main_keyboard())
    elif data == "collections":
        await q.edit_message_text("🛋 *Наши коллекции*\n\nВыберите линейку:", parse_mode="Markdown", reply_markup=collections_keyboard())
    elif data.startswith("col_"):
        col = COLLECTIONS.get(data[4:])
        if col:
            items = "\n".join(f"• {i}" for i in col["items"])
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Консультация", callback_data="consult"),
                 InlineKeyboardButton("🌐 Подробнее", url=col["url"])],
                [InlineKeyboardButton("← К коллекциям", callback_data="collections")],
            ])
            await q.edit_message_text(f"*{col['title']}*\n\n{col['desc']}\n\n*Модели:*\n{items}", parse_mode="Markdown", reply_markup=kb)
    elif data == "faq":
        await q.edit_message_text("❓ *Частые вопросы*\n\nВыберите тему:", parse_mode="Markdown", reply_markup=faq_keyboard())
    elif data in FAQ:
        await q.edit_message_text(FAQ[data], parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="faq")]]))
    elif data == "consult":
        await q.edit_message_text("📝 *Заявка на консультацию*\n\nКак вас зовут?", parse_mode="Markdown", reply_markup=cancel_keyboard())
        return WAITING_NAME
    elif data == "cancel_consult":
        await q.edit_message_text("Отменено.", reply_markup=main_keyboard())
        return ConversationHandler.END
    return ConversationHandler.END
 
async def got_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(f"Отлично, {ctx.user_data['name']}! 📞\n\nУкажите ваш номер телефона:", reply_markup=cancel_keyboard())
    return WAITING_PHONE
 
async def got_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    name = ctx.user_data.get("name", "—")
    user = update.effective_user
    await update.message.reply_text(
        "✅ *Заявка принята!*\n\nМенеджер свяжется с вами в ближайшее время.\n📞 *8 495 998-60-60*",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )
    if MANAGER_CHAT_ID:
        await ctx.bot.send_message(
            MANAGER_CHAT_ID,
            f"🔔 *Новая заявка*\n\n👤 {name}\n📞 {phone}\n💬 @{user.username or '—'} (id: {user.id})",
            parse_mode="Markdown"
        )
    return ConversationHandler.END
 
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=main_keyboard())
    return ConversationHandler.END
 
async def ai_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 400,
                    "system": "Ты помощник магазина Verona Store (verona-store.ru). Продаём премиальную мебель для ванных: Verona, Brenta, Salini, Catalano, Valdama, Gessi, Dornbracht, Bette, Decor Walther и другие. Шоурум в Москве. Тел: 8 495 998-60-60. Отвечай кратко по-русски.",
                    "messages": [{"role": "user", "content": update.message.text}]
                }
            )
        reply = r.json()["content"][0]["text"]
    except Exception:
        reply = "Извините, сейчас не могу ответить.\nПозвоните: *8 495 998-60-60*"
    await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=main_keyboard())
 
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button, pattern="^consult$")],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            WAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(button, pattern="^cancel_consult$")],
        per_message=False,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
 
    print("✅ Verona Store Bot запущен!")
 
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        asyncio.create_task(scheduler(app))
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()
 
if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            logging.error(f"Бот упал: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)
