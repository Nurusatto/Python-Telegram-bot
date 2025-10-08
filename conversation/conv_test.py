from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from DATA import TEST
from utils import check_answer  # type: ignore

ASK_NAME, ASK_1 = range(2)


class TestConversation:
    def __init__(self):
        self.state = {
            "correct": "correct",
            "wrong": "wrong",
        }
        self.alert = {
            "yes": "✅ Правильно!",
            "no": "❌ Неправильно!",
        }

    # ───────────────────────────────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        query = update.callback_query

        context.user_data.clear() # type: ignore
        context.user_data["correct"] = 0 # type: ignore
        context.user_data["current"] = 0 # type: ignore

        if query:
            await query.answer()
            chat_id = query.message.chat.id # type: ignore
        else:
            chat_id = update.message.chat.id # type: ignore

        await context.bot.send_message(chat_id=chat_id, text="Как тебя зовут?")
        return ASK_NAME

    # ───────────────────────────────
    async def ask_one(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
      
        name = update.message.text  # type: ignore
        context.user_data["name"] = name # type: ignore
        
        await context.bot.send_message(chat_id=update.message.chat.id, text=f"Хорошо, {name}! Начнём тест 🎯") # type: ignore
        return await self.send_question(update, context)

    # ───────────────────────────────
    async def send_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        idx = context.user_data.get("current", 0) # type: ignore
        chat = update.effective_chat
        chat_id = chat.id if chat else None

        if idx >= len(TEST):
            correct = context.user_data.get("correct", 0) # type: ignore
            msg = f"🎉 Тест завершён! Правильных ответов: {correct}/{len(TEST)}"
            if chat_id:
                await context.bot.send_message(chat_id=chat_id, text=msg)
            context.user_data.clear() # type: ignore
            return ConversationHandler.END

        q = TEST[idx]
        keyboard = [
            [InlineKeyboardButton(q["options"]["correct"], callback_data="correct")],
            [InlineKeyboardButton(q["options"]["wrong"], callback_data="wrong")],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        # Всегда отправляем через bot — так меньше путаницы
        if chat_id:
            await context.bot.send_message(chat_id=chat_id, text=q["question"], reply_markup=markup)
        return ASK_1

    # ───────────────────────────────
    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатия кнопки ответа — pattern ограничит колбеки только 'correct'/'wrong'"""
        query = update.callback_query
        await query.answer()  # type: ignore

        data = query.data  # type: ignore #
        
        is_correct = check_answer(data, "correct")  # type: ignore
        

        if is_correct:
            context.user_data["correct"] = context.user_data.get("correct", 0) + 1 # type: ignore
            await query.edit_message_text(self.alert["yes"])  # type: ignore
        else:
            await query.edit_message_text(self.alert["no"]) # type: ignore 

        
        context.user_data["current"] = context.user_data.get("current", 0) + 1 # type: ignore

        chat_id = query.message.chat.id # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="⏳ Подготавливаю следующий вопрос...")
        return await self.send_question(update, context)

    # ───────────────────────────────
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="🚪 Тест окончен.")
        context.user_data.clear() # type: ignore
        return ConversationHandler.END

    # ───────────────────────────────
    def get_handler(self):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start, pattern="^testing$")],
            states={
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_one)],

                ASK_1: [CallbackQueryHandler(self.handle_answer, pattern="^(correct|wrong)$")],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            allow_reentry=True,
        )
