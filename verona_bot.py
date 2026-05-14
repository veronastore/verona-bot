"""
Verona Store Telegram Bot
Запуск: pip install python-telegram-bot httpx
        python verona_bot.py
"""

import logging
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─── НАСТРОЙКИ ────────────────────────────────────────────────────────────────
BOT_TOKEN = "8851790776:AAFBvLHCYIXLTweEf1hc-ewuyPZoG8a9LCw"
MANAGER_CHAT_ID = 825970353   # ← вставь свой Telegram ID чтобы получать заявки
                          #   узнать можно у @userinfobot

# ─── СОСТОЯНИЯ ДИАЛОГА ────────────────────────────────────────────────────────
WAITING_NAME, WAITING_PHONE = range(2)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ─── ДАННЫЕ О КОЛЛЕКЦИЯХ ──────────────────────────────────────────────────────
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
    "faq_price": (
        "💰 *Цены*\n\n"
        "Стоимость зависит от коллекции, размеров и комплектации.\n"
        "Для точного расчёта свяжитесь с нашим менеджером — подберём оптимальный вариант под ваш проект и бюджет."
    ),
    "faq_delivery": (
        "🚚 *Доставка*\n\n"
        "Доставляем по всей России. Сроки зависят от наличия товара на складе и региона.\n"
        "Стандартные сроки: 4–8 недель с момента подтверждения заказа."
    ),
    "faq_showroom": (
        "🏠 *Шоурум*\n\n"
        "Наш шоурум находится в Москве.\n"
        "📞 *Телефон:* 8 495 998-60-60\n"
        "✉️ *Email:* info@verona-store.ru\n"
        "🕐 *Пн–Пт:* 10:00 – 19:00\n"
        "🕐 *Сб:* 11:00 – 17:00\n\n"
        "Запись на визит через кнопку «Консультация»."
    ),
    "faq_install": (
        "🔧 *Монтаж*\n\n"
        "Мы работаем с проверенными бригадами монтажников в Москве и МО.\n"
        "Услуга монтажа обсуждается индивидуально при оформлении заказа."
    ),
}

# ─── КЛАВИАТУРЫ ───────────────────────────────────────────────────────────────

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
        [InlineKeyboardButton("Verona Basic",  callback_data="col_verona_basic")],
        [InlineKeyboardButton("Brenta",        callback_data="col_brenta")],
        [InlineKeyboardButton("← Назад",       callback_data="back_main")],
    ])

def faq_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Цены",       callback_data="faq_price")],
        [InlineKeyboardButton("🚚 Доставка",   callback_data="faq_delivery")],
        [InlineKeyboardButton("🏠 Шоурум",     callback_data="faq_showroom")],
        [InlineKeyboardButton("🔧 Монтаж",     callback_data="faq_install")],
        [InlineKeyboardButton("← Назад",       callback_data="back_main")],
    ])

def back_keyboard(target="back_main"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data=target)]])

def cancel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="cancel_consult")]])

# ─── ХЭНДЛЕРЫ ─────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    text = (
        f"Добро пожаловать, {name}! 👋\n\n"
        "Я бот *Verona Store* — официального дилера премиальной мебели\n"
        "и сантехники для ванных комнат.\n\n"
        "Выберите, что вас интересует:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())


async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # ГЛАВНОЕ МЕНЮ
    if data == "back_main":
        await q.edit_message_text(
            "Чем могу помочь? Выберите раздел:",
            reply_markup=main_keyboard()
        )

    # КОЛЛЕКЦИИ
    elif data == "collections":
        await q.edit_message_text(
            "🛋 *Наши коллекции*\n\nВыберите линейку, чтобы узнать подробнее:",
            parse_mode="Markdown",
            reply_markup=collections_keyboard()
        )

    elif data.startswith("col_"):
        key = data[4:]
        col = COLLECTIONS.get(key)
        if col:
            items = "\n".join(f"• {i}" for i in col["items"])
            text = (
                f"*{col['title']}*\n\n"
                f"{col['desc']}\n\n"
                f"*Коллекции:*\n{items}\n\n"
                f"Для подбора конкретной модели и уточнения деталей — "
                f"нажмите «Консультация» или посетите наш сайт."
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Консультация", callback_data="consult"),
                 InlineKeyboardButton("🌐 Подробнее", url=col["url"])],
                [InlineKeyboardButton("← К коллекциям", callback_data="collections")],
            ])
            await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # FAQ
    elif data == "faq":
        await q.edit_message_text(
            "❓ *Частые вопросы*\n\nВыберите тему:",
            parse_mode="Markdown",
            reply_markup=faq_keyboard()
        )

    elif data in FAQ:
        await q.edit_message_text(
            FAQ[data],
            parse_mode="Markdown",
            reply_markup=back_keyboard("faq")
        )

    # КОНСУЛЬТАЦИЯ
    elif data == "consult":
        await q.edit_message_text(
            "📝 *Заявка на консультацию*\n\nКак вас зовут?",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
        return WAITING_NAME

    elif data == "cancel_consult":
        await q.edit_message_text("Отменено. Чем могу помочь?", reply_markup=main_keyboard())
        return ConversationHandler.END

    return ConversationHandler.END


async def got_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        f"Отлично, {ctx.user_data['name']}! 📞\n\nУкажите ваш номер телефона:",
        reply_markup=cancel_keyboard()
    )
    return WAITING_PHONE


async def got_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    name  = ctx.user_data.get("name", "—")
    user  = update.effective_user

    # Подтверждение клиенту
    await update.message.reply_text(
        "✅ *Заявка принята!*\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n\n"
        "📞 Или позвоните сами: *8 495 998-60-60*\n"
        "🕐 Пн–Пт 10:00–19:00, Сб 11:00–17:00",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

    # Уведомление менеджеру
    if MANAGER_CHAT_ID:
        msg = (
            "🔔 *Новая заявка на консультацию*\n\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 Telegram: @{user.username or '—'} (id: {user.id})"
        )
        await ctx.bot.send_message(MANAGER_CHAT_ID, msg, parse_mode="Markdown")

    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=main_keyboard())
    return ConversationHandler.END


async def ai_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Умный ответ через Claude AI на любой вопрос."""
    user_text = update.message.text
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")

    system = (
        "Ты — помощник магазина Verona Store (verona-store.ru). "
        "Магазин продаёт премиальную мебель и сантехнику для ванных комнат: "
        "коллекции Verona Design, Verona Basic, Brenta, а также бренды Salini, Valdama, Catalano. "
        "Шоурум в Москве. Телефон: 8 495 998-60-60. "
        "Отвечай кратко, по-русски, дружелюбно. "
        "Если не знаешь точного ответа — предложи позвонить менеджеру."
    )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 400,
                    "system": system,
                    "messages": [{"role": "user", "content": user_text}]
                }
            )
        data = r.json()
        reply = data["content"][0]["text"]
    except Exception:
        reply = (
            "Извините, сейчас не могу ответить автоматически.\n"
            "Позвоните нам: *8 495 998-60-60* или выберите раздел ниже."
        )

    await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=main_keyboard())


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button, pattern="^consult$")],
        states={
            WAITING_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            WAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(button, pattern="^cancel_consult$"),
        ],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("✅ Verona Store Bot запущен!")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
