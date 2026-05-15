"""
Verona Store Telegram Bot — финальная версия с фото
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
 
POSTS = [
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/2da/2da22e46b6959d9b10c20b159d4bc327/00.jpg",
        "caption": "🪨 Когда природа входит в дом\n\nМассивная скала, ванна PERLA из литьевого мрамора, круглые раковины ARMONIA — этот проект доказывает: ванная может быть произведением искусства. Salini делает сантехнику из искусственного камня, которая живёт в интерьере как природный объект.\n\nПриходите в наш шоурум — покажем коллекцию вживую.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b0e/b0ee08dc1424defc20c54a118fd21434/SpalnaNovyy%20blok_View110000.jpg",
        "caption": "🌿 Три стихии в одном пространстве\n\nДерево, камень, мрамор — три вида декоративной плитки создают многослойную атмосферу. Ванна Ornella от Salini стала центром этого эко-проекта. Здесь каждая деталь работает на цельность образа.\n\nХотите создать такое пространство? Мы поможем подобрать всё необходимое.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/4d3/4d32cf86850dc131d284f24a6a488ade/R_1.jpg",
        "caption": "🏔 Мансарда как роскошь\n\nКосой потолок — не ограничение, а особенность. Ванна LUCE от Salini органично вписалась в нестандартное пространство мансарды. Иногда именно сложные условия рождают самые интересные интерьеры.\n\nПодберём решение для любой планировки.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/9b5/9b5a3c65786a4d225ab6682a43f07809/R_2.jpg",
        "caption": "✨ Минимализм в деталях\n\nСветлые тона, чистые линии, ничего лишнего. Сантехника Salini из литьевого мрамора создаёт ощущение спокойствия и продуманной роскоши. Это не про дорого — это про правильно.\n\nПриходите в шоурум — почувствуйте разницу вживую.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/cb9/cb955b6bac92a7e8e1788bd9a5a58728/03.jpg",
        "caption": "💎 Литьевой мрамор — материал который не стареет\n\nSalini производит сантехнику из искусственного камня — это не пластик и не акрил. Твёрдая поверхность, устойчивая к царапинам, тёплая на ощупь. Ванны и раковины которые выглядят одинаково хорошо через 10 лет.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/220/220b573f70d0bade97dd6bf15eb1558c/05.jpg",
        "caption": "🛁 Отдельностоящая ванна — главный герой\n\nКогда ванна стоит отдельно от стены — она становится скульптурой. Salini делает отдельностоящие ванны из литьевого мрамора в разных формах и цветах. Каждая — арт-объект в вашем интерьере.\n\nСмотрите коллекцию в нашем шоуруме.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f97/f9767080f0a51c9ba8ef815f53ac8851/07.jpg",
        "caption": "🤍 Ванная как личное пространство\n\nЗдесь начинается и заканчивается каждый день. Именно поэтому важно чтобы это пространство было вашим — по стилю, по материалам, по ощущению. Salini и Verona Store помогают создать именно такую ванную.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/226/2260a325989a35ff96882a803d46e1a2/08.jpg",
        "caption": "📐 Большая ванная — как не потеряться\n\nПросторная ванная требует правильного зонирования. Длинная линия мебели от стены до стены, встроенные ниши, продуманное освещение — всё это создаёт структуру пространства. Наши менеджеры помогут спланировать.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b55/b5521eb42e6dff26e1344850faf7db95/09.jpg",
        "caption": "⬛ Тёмные тона — смело и роскошно\n\nГрафит, антрацит, чёрный мрамор — тёмные ванные комнаты создают ощущение глубины и камерности. Salini выпускает сантехнику в широкой палитре тёмных оттенков. Это для тех кто не боится экспериментировать.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f5e/f5e01a1dfd6418a0ee8e15b180fce7be/01.jpg",
        "caption": "🌊 Форма следует за водой\n\nПлавные изгибы ванны Salini — не случайность, а философия. Форма которая повторяет движение воды, поверхность которая приятна на ощупь. Литьевой камень сохраняет тепло воды дольше обычного акрила.\n\nПриходите и потрогайте сами.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/54c/54c053241a36ba1a06f064b460b490a8/04.jpg",
        "caption": "🏠 Компактная ванная — не компромисс\n\nДаже в 5 кв.м можно создать красивое и функциональное пространство. Правильный выбор мебели, встроенные хранилища, подвесная сантехника — и маленькая ванная становится уютной. Поможем спланировать.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/d3c/d3cdf37b46e3d5e72fd60b198dd1f442/06.jpg",
        "caption": "💡 Свет который меняет всё\n\nПравильное освещение — половина успеха ванной комнаты. Световая стена вместо окна, подсветка ниш, зеркало с подсветкой — всё это создаёт атмосферу. Приходите в наш шоурум — у нас работают живые примеры освещения.\n\n📞 8 495 998-60-60\n🌐 verona-store.ru\n🤖 @VeronaStoreBot"
    },
]
 
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
 
async def publish_post(app: Application, post_index: int = None):
    if post_index is None:
        day = datetime.now(MOSCOW_TZ).timetuple().tm_yday
        post_index = day % len(POSTS)
    post = POSTS[post_index]
    try:
        await app.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=post["photo"],
            caption=post["caption"]
        )
        logging.info(f"✅ Пост опубликован!")
        if MANAGER_CHAT_ID:
            await app.bot.send_message(
                MANAGER_CHAT_ID,
                f"✅ Пост опубликован в канал!"
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
            await publish_post(app)
        except Exception as e:
            logging.error(f"Ошибка планировщика: {e}")
            await asyncio.sleep(60)
 
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"Добро пожаловать, {name}! 👋\n\nЯ бот *Verona Store* — официального дилера премиальной мебели для ванных комнат.\n\nВыберите, что вас интересует:",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )
 
async def force_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MANAGER_CHAT_ID:
        return
    await update.message.reply_text("⏳ Публикую пост...")
    await publish_post(ctx.application)
 
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
    # Сначала удаляем webhook и сбрасываем все обновления
    app = Application.builder().token(BOT_TOKEN).build()
 
    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.shutdown()
 
    # Теперь запускаем бота чисто
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
    app.add_handler(CommandHandler("post", force_post))
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
