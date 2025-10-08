from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

step_1, step_2, step_3 = range(3)

class BookingConversation:
    def __init__(self):
        self.alert = {
            "start": "🏫 Введите номер аудитории (например 101)(101,102,103 есть):",
            "noRoom": "❌ Аудитория не найдена.",
            "roomFound": "✅ Найдена аудитория {room}. Выберите время:",
            "confirmed": "✅ Аудитория {room} забронирована на {time}!",
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()# type: ignore
        context.user_data.clear()  # type: ignore
        await query.message.reply_text(self.alert["start"])  # type: ignore
        return step_1

    async def ask_room(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            await update.effective_chat.send_message("Ошибка: сообщение не распознано.")  # type: ignore
            return ConversationHandler.END

        room = update.message.text.strip() # type: ignore
        context.user_data["room"] = room  # type: ignore

        if room not in ["101", "102", "103"]:
            await update.message.reply_text(f"{self.alert['noRoom']}")  # type: ignore
            return ConversationHandler.END

        times = ["09:00", "11:00", "13:00", "15:00"]
        keyboard = [[InlineKeyboardButton(t, callback_data=t)] for t in times]
        markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            self.alert["roomFound"].format(room=room), reply_markup=markup
        )  # type: ignore
        return step_2

    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # type: ignore

        time = query.data  # type: ignore
        room = context.user_data.get("room")  # type: ignore

        await query.edit_message_text(# type: ignore
            self.alert["confirmed"].format(room=room, time=time)
        )  # type: ignore
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Бронирование отменено ❌")  # type: ignore
        context.user_data.clear()  # type: ignore
        return ConversationHandler.END

    def get_handler(self):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start, pattern="^booking$")],
            states={
                step_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_room)],
                step_2: [CallbackQueryHandler(self.confirm_booking)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            allow_reentry=True,
        )
