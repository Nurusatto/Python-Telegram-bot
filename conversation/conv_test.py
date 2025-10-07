from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from DATA import TEST
from utils import check_answer  # type: ignore

ASK_NAME, ASK_1 = range(2)


class TestConversation:
    def __init__(self):
        self.correct_answer = 0
        self.state = {
            "correct": "correct",
            "wrong": "wrong"
        }
        self.alert = {
            "yes": "✅ Правильно!",
            "no": "❌ Неправильно!"
        }

    # ───────────────────────────────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

        self.correct_answer = 0
        context.user_data.clear() # type: ignore    

        if query:
            await query.answer()
            await query.message.reply_text("Как тебя зовут?") # type: ignore
        else:
            await update.message.reply_text("Как тебя зовут?") # type: ignore
        return ASK_NAME

    # ───────────────────────────────
    async def ask_one(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Срабатывает один раз — когда пользователь написал имя"""
        name = update.message.text # type: ignore
        context.user_data["name"] = name# type: ignore
        context.user_data["current"] = 0# type: ignore
        

        await update.message.reply_text(f"Хорошо, {name}! Начнём тест 🎯")# type: ignore

        # переходим к вопросам
        await self.send_question(update, context)
        return ASK_1  # ⬅️ теперь переключаемся в следующее состояние

    # ───────────────────────────────
    async def send_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        idx = context.user_data.get("current", 0)# type: ignore

        if idx >= len(TEST):
            # тест закончен
            msg = f"🎉 Тест завершён! Правильных ответов: {self.correct_answer}/{len(TEST)}"
            if update.message:
                await update.message.reply_text(msg)
            else:
                await update.callback_query.message.reply_text(msg)# type: ignore
            
            return ConversationHandler.END

        q = TEST[idx]
        keyboard = [
            [InlineKeyboardButton(q["options"]["correct"], callback_data="correct")],
            [InlineKeyboardButton(q["options"]["wrong"], callback_data="wrong")]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        # безопасно отвечаем независимо от типа update
        if update.message:
            await update.message.reply_text(q["question"], reply_markup=markup)
        else:
            await update.callback_query.message.reply_text(q["question"], reply_markup=markup)# type: ignore
        return ASK_1

    # ───────────────────────────────
    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()# type: ignore

        if check_answer(query.data, "correct"):# type: ignore
            self.correct_answer += 1
            await query.edit_message_text(self.alert["yes"])# type: ignore
        else:
            await query.edit_message_text(self.alert["no"])# type: ignore

        context.user_data["current"] = context.user_data.get("current", 0) + 1# type: ignore

        # небольшой переход
        await query.message.reply_text("⏳ Подготавливаю следующий вопрос...")# type: ignore

        # показываем следующий
        await self.send_question(update, context)
        return ASK_1

    # ───────────────────────────────
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚪 Тест окончен.")# type: ignore
        return ConversationHandler.END

    # ───────────────────────────────
    def get_handler(self):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start, pattern="^testing$")],
            states={
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_one)],
                ASK_1: [CallbackQueryHandler(self.handle_answer)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
