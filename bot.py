#!/usr/bin/env python3
"""
Бот-опросник «Формат блога» — @grigorii.ha
Запуск: python bot.py
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ══════════════════════════════════════════════════
# НАСТРОЙКИ
# ══════════════════════════════════════════════════
BOT_TOKEN = "8693629114:AAHO5Qav6i3LilbvecobQCr9H17gV3OZrT4"
CURATOR_ID = 8225752258  # ваш Telegram ID — сюда придут все ответы

# ══════════════════════════════════════════════════
# ВОПРОСЫ — 8 блоков по 3 вопроса + имя и контакт
# ══════════════════════════════════════════════════
QUESTIONS = [
    # Блок 0 — знакомство
    {
        "block": "Знакомство",
        "q": "Как вас зовут?",
        "hint": "Напишите имя — так куратор будет знать кто заполнял опросник."
    },
    {
        "block": "Знакомство",
        "q": "Как с вами связаться? Напишите ваш Telegram @username или номер телефона.",
        "hint": "Например: @username или +82 10-1234-5678"
    },

    # Блок 1 — результат
    {
        "block": "Блок 1. Результат от блога",
        "q": "Какой главный результат вы хотите получить от блога?",
        "hint": "💡 Клиенты на услуги, продажа товаров, личный бренд, обучение — выберите одно главное."
    },
    {
        "block": "Блок 1. Результат от блога",
        "q": "Как вы поймёте, что блог работает — что изменится конкретно?",
        "hint": "💡 Не «буду популярным». Конкретно: 5 заявок в неделю, первая продажа, 1000 подписчиков за 3 месяца."
    },
    {
        "block": "Блок 1. Результат от блога",
        "q": "Почему вы этим занимаетесь — настоящая причина, не «чтобы зарабатывать»?",
        "hint": "💡 Был ли момент, когда вы поняли что хотите именно этим заниматься? Что произошло?"
    },

    # Блок 2 — ниша
    {
        "block": "Блок 2. Ниша",
        "q": "Чем вы занимаетесь или хотите заниматься — максимально конкретно?",
        "hint": "💡 Не «маникюр» — а «маникюр для женщин, которые хотят выглядеть ухоженно». Добавьте: для кого + с каким результатом."
    },
    {
        "block": "Блок 2. Ниша",
        "q": "Есть ли что-то, что вы делаете иначе, чем большинство в вашей нише?",
        "hint": "💡 Не нужно быть уникальным. Достаточно одного отличия: личный опыт, конкретная аудитория, подход которого нет у других."
    },
    {
        "block": "Блок 2. Ниша",
        "q": "Если бы вы помогали только одному типу людей — кому именно и с чем?",
        "hint": "💡 Один человек, одна проблема, один результат. Упражнение на фокус."
    },

    # Блок 3 — аудитория
    {
        "block": "Блок 3. Аудитория",
        "q": "Опишите одного конкретного человека, которому нужен ваш блог.",
        "hint": "💡 Чем занимается, что беспокоит, что ищет прямо сейчас. Не демографию — а человека."
    },
    {
        "block": "Блок 3. Аудитория",
        "q": "Какие 3 главные проблемы есть у этого человека в вашей теме?",
        "hint": "💡 Вспомните реальные вопросы, которые вам задавали. Или что вы сами искали когда только начинали."
    },
    {
        "block": "Блок 3. Аудитория",
        "q": "Чего этот человек хочет добиться — какой конечный результат?",
        "hint": "💡 Люди покупают не услугу — они покупают результат. Опишите финальное состояние."
    },

    # Блок 4 — сильные стороны
    {
        "block": "Блок 4. Сильные стороны автора",
        "q": "За что вас чаще всего хвалят — коллеги, клиенты, друзья?",
        "hint": "💡 Всё считается: «хорошо объясняешь», «умеешь успокоить», «находишь решение». Не обесценивайте себя."
    },
    {
        "block": "Блок 4. Сильные стороны автора",
        "q": "О чём вы можете говорить часами без подготовки?",
        "hint": "💡 Это обычно и есть главная тема блога. Если тема не зажигает — через месяц выгорите."
    },
    {
        "block": "Блок 4. Сильные стороны автора",
        "q": "Какой опыт у вас уже есть, который может быть полезен другим?",
        "hint": "💡 Переехали в другую страну? Разобрались с чем-то сложным? Прошли путь с нуля до результата?"
    },

    # Блок 5 — рубрики
    {
        "block": "Блок 5. Рубрики",
        "q": "Назовите 3 направления в вашей теме, про которые можете говорить бесконечно.",
        "hint": "💡 Рубрика — это не одна тема, а целое направление. Одна рубрика = минимум 10–20 роликов."
    },
    {
        "block": "Блок 5. Рубрики",
        "q": "В каждой рубрике — какой вопрос клиент задаёт чаще всего?",
        "hint": "💡 Это готовые темы для роликов. Самый частый вопрос = самый нужный контент."
    },
    {
        "block": "Блок 5. Рубрики",
        "q": "Какая рубрика нравится вам лично — про что снимать легче?",
        "hint": "💡 Это ваша главная рубрика. С неё начинайте — здесь будет самый живой контент."
    },

    # Блок 6 — темы
    {
        "block": "Блок 6. Темы для контента",
        "q": "По формуле «ОШИБКИ»: назовите 3 типичные ошибки новичков в вашей нише.",
        "hint": "💡 Ошибка → последствие → решение. Самый кликабельный формат — люди боятся ошибиться."
    },
    {
        "block": "Блок 6. Темы для контента",
        "q": "По формуле «КАК СДЕЛАТЬ»: 3 вещи, которым вы можете научить за 60 секунд.",
        "hint": "💡 Пошаговые инструкции сохраняют и пересматривают. Одна инструкция = один ролик."
    },
    {
        "block": "Блок 6. Темы для контента",
        "q": "По формуле «МИФ»: 3 заблуждения, которые есть у вашей аудитории.",
        "hint": "💡 «Правда ли, что...» — один из лучших хуков. Вспомните что чаще всего приходится объяснять."
    },

    # Блок 7 — формат
    {
        "block": "Блок 7. Рабочий формат",
        "q": "Что вам легче всего делать на камеру?",
        "hint": "💡 Объяснять, показывать процесс, рассказывать истории или делать разборы? Выбирайте то, что легко — не то, что «правильно»."
    },
    {
        "block": "Блок 7. Рабочий формат",
        "q": "Что вам точно НЕ нравится делать в блоге?",
        "hint": "💡 Танцы, длинные монологи, лайфстайл, камера на лицо — что точно не ваше? Это не слабость — это ограничения формата."
    },
    {
        "block": "Блок 7. Рабочий формат",
        "q": "Что вы готовы снимать каждую неделю в течение 6 месяцев подряд?",
        "hint": "💡 Это и есть ваш рабочий формат. Не самый красивый — а тот, который не бросите."
    },

    # Блок 8 — Reels
    {
        "block": "Блок 8. Форматы Reels",
        "q": "Возьмите одну тему — какие 3 формата из списка готовы снять прямо сейчас?\n\nФорматы: Ошибка / Инструкция / До-после / Миф / История / Разбор / Топ-5 / Вопрос-ответ / Кейс",
        "hint": "💡 Выберите те, которые кажутся проще всего для вашей темы."
    },
    {
        "block": "Блок 8. Форматы Reels",
        "q": "Какой формат работал лучше всего у вас или в вашей нише?",
        "hint": "💡 Если не снимали — опишите что видите у конкурентов. Что набирает больше просмотров?"
    },
    {
        "block": "Блок 8. Форматы Reels",
        "q": "Какой формат пугает, но вы понимаете что он нужен вашей аудитории?",
        "hint": "💡 Это ваша зона роста. Не нужно делать его прямо сейчас — просто зафиксируйте."
    },
]

TOTAL = len(QUESTIONS)
ANSWERING = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════
# СТАРТ
# ══════════════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    ctx.user_data["answers"] = []
    ctx.user_data["step"] = 0

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я помогу вам найти рабочий формат блога.\n\n"
        "Это опросник из 8 блоков — займёт около 15–20 минут.\n"
        "Отвечайте честно — не как «правильно», а как есть на самом деле.\n\n"
        "В конце ваш куратор получит все ответы и пришлёт персональный портрет формата.\n\n"
        "Начнём? 👇",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Начать опросник"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return ANSWERING


async def handle_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    step = ctx.user_data.get("step", 0)
    answers = ctx.user_data.get("answers", [])

    # Если нажали «Начать» — отправляем первый вопрос
    if text == "✅ Начать опросник" and step == 0:
        await send_question(update, ctx, 0)
        return ANSWERING

    # Если нажали «Да, всё верно» — отправляем куратору
    if text == "✅ Да, всё верно — отправить куратору":
        await send_to_curator(update, ctx)
        return ConversationHandler.END

    # Если нажали «Изменить ответ» — возвращаемся на шаг назад
    if text == "✏️ Изменить последний ответ":
        if step > 0:
            ctx.user_data["step"] = step - 1
            ctx.user_data["answers"] = answers[:-1]
            await send_question(update, ctx, step - 1, edit=True)
        return ANSWERING

    # Обычный ответ
    if step < TOTAL:
        answers.append(text)
        ctx.user_data["answers"] = answers
        ctx.user_data["step"] = step + 1

        if step + 1 < TOTAL:
            # Следующий вопрос
            next_step = step + 1
            # Проверяем смену блока
            cur_block = QUESTIONS[step]["block"]
            next_block = QUESTIONS[next_step]["block"]
            if next_block != cur_block:
                await update.message.reply_text(
                    f"✓ Блок завершён!\n\nПереходим к следующему разделу 👇",
                    reply_markup=ReplyKeyboardRemove()
                )
            await send_question(update, ctx, next_step)
        else:
            # Все вопросы пройдены — показываем итог
            await show_summary(update, ctx)

    return ANSWERING


async def send_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE, step: int, edit=False):
    q = QUESTIONS[step]
    progress = f"{step + 1}/{TOTAL}"
    bar_filled = int((step / TOTAL) * 10)
    bar = "▓" * bar_filled + "░" * (10 - bar_filled)

    # Заголовок блока если первый вопрос блока
    is_first_in_block = (step == 0 or QUESTIONS[step]["block"] != QUESTIONS[step-1]["block"])

    prefix = ""
    if is_first_in_block:
        prefix = f"━━━━━━━━━━━━━━━━\n📌 {q['block']}\n━━━━━━━━━━━━━━━━\n\n"

    msg = (
        f"{prefix}"
        f"[{bar}] {progress}\n\n"
        f"{'✏️ ' if edit else ''}❓ {q['q']}\n\n"
        f"{q['hint']}"
    )

    kb = ReplyKeyboardMarkup(
        [["✏️ Изменить последний ответ"]] if step > 0 else [],
        resize_keyboard=True
    ) if step > 0 else ReplyKeyboardRemove()

    await update.message.reply_text(msg, reply_markup=kb)


async def show_summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    answers = ctx.user_data.get("answers", [])

    lines = ["📋 *Ваши ответы — проверьте перед отправкой:*\n"]
    cur_block = None
    for i, q in enumerate(QUESTIONS):
        if q["block"] != cur_block:
            cur_block = q["block"]
            lines.append(f"\n*{cur_block}*")
        ans = answers[i] if i < len(answers) else "—"
        lines.append(f"▸ {q['q'][:60]}{'...' if len(q['q'])>60 else ''}\n  💬 {ans}")

    lines.append("\n\nВсё верно? Нажмите кнопку ниже чтобы отправить куратору.")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["✅ Да, всё верно — отправить куратору"],
                ["✏️ Изменить последний ответ"]
            ],
            resize_keyboard=True
        )
    )


async def send_to_curator(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    answers = ctx.user_data.get("answers", [])
    user = update.effective_user

    # Строим сообщение куратору
    name = answers[0] if len(answers) > 0 else "—"
    contact = answers[1] if len(answers) > 1 else "—"
    tg_link = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    lines = [
        "📋 *НОВЫЙ ОПРОСНИК «ФОРМАТ БЛОГА»*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"👤 *Имя:* {name}",
        f"📱 *Контакт:* {contact}",
        f"🔗 *Telegram:* {tg_link}",
        "━━━━━━━━━━━━━━━━━━━━━━━━\n",
    ]

    cur_block = None
    # Пропускаем первые 2 вопроса (имя и контакт) — они уже в шапке
    for i, q in enumerate(QUESTIONS[2:], start=2):
        if q["block"] != cur_block:
            cur_block = q["block"]
            lines.append(f"\n*{cur_block}*")
        ans = answers[i] if i < len(answers) else "—"
        lines.append(f"\n❓ _{q['q']}_\n💬 {ans}")

    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("_Отправлено через бот-опросник @grigorii.ha_")

    msg = "\n".join(lines)

    try:
        await ctx.bot.send_message(
            chat_id=CURATOR_ID,
            text=msg,
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            "✅ Готово! Ваши ответы отправлены куратору.\n\n"
            "Куратор изучит ваш опросник и свяжется с вами в ближайшее время.\n\n"
            "Чтобы пройти опросник заново — напишите /start",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Send error: {e}")
        await update.message.reply_text(
            "⚠️ Что-то пошло не так при отправке. Напишите куратору напрямую: @grigorii.ha",
            reply_markup=ReplyKeyboardRemove()
        )


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Опросник прерван. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ══════════════════════════════════════════════════
# ЗАПУСК
# ══════════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ANSWERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)

    print("✅ Бот запущен. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
