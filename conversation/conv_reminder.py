from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ContextTypes,ConversationHandler,CallbackQueryHandler,CommandHandler,filters,MessageHandler

from DATA import CLASS
from utils import normalize_text

step_1,step_2,step_3 = range(3)

class ReminderConversation:
    def __init__(self):
        self.alert ={
            "noClass":"❌ Не найдено класса",
            "yesClass":"✅ Найдено,выберите день",
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # type: ignore 
        context.user_data.clear()  # type: ignore
        chat_id = query.message.chat.id  # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="Напиши идентификатор класса (например C)")
        return step_1


    async def hello_student(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        if not update.message:
            await update.effective_chat.send_message("Ошибка: сообщение не распознано.") # type: ignore
            return ConversationHandler.END

        student_class = normalize_text(update.message.text)
        context.user_data["class"] = student_class  # type: ignore

        if student_class == "C":
            await update.message.reply_text(f"Добро пожаловать, ученик класса {student_class}! 🎓") # type: ignore      
            return await self.choose_day(update, context)
        else:
            await update.message.reply_text( # type: ignore
                f"{self.alert['noClass']} {student_class}, не зарегистрирован."
            )
            context.user_data.clear()   # type: ignore
            return ConversationHandler.END

    async def choose_day(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        classValue = context.user_data.get('class') # type: ignore

        schedule_for_class = CLASS[classValue]["schedule"]
        keyboard = []

        for day in schedule_for_class.keys():
            keyboard.append([InlineKeyboardButton(day, callback_data=day)]) # type: ignore

        markup = InlineKeyboardMarkup(keyboard) # type: ignore
        await update.message.reply_text("Выберите день недели:", reply_markup=markup) # type: ignore
        return step_3

    async def schedule(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
         
        query = update.callback_query
        await query.answer() #type:ignore

        chosen_day = query.data # type: ignore
        classValue = context.user_data.get('class')  # type: ignore
        schedule_for_class = CLASS[classValue]["schedule"] 
        day_schedule = schedule_for_class.get(chosen_day)
        
        if not day_schedule:
            await query.edit_message_text(f"❌ Нет расписания для {chosen_day}.") # type: ignore
            return ConversationHandler.END

        formatted_schedule = "\n".join([f"{time} — {subject}" for time, subject in day_schedule.items()])

        await query.edit_message_text(f"Ты выбрал {chosen_day} 📅:\n\n{formatted_schedule}") # type: ignore

        return ConversationHandler.END




    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="чат закрыт")
        context.user_data.clear() # type: ignore
        return ConversationHandler.END

    def get_handler(self):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start, pattern="^reminders$")],
            states={
                step_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.hello_student)],
                step_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.choose_day)],
                step_3: [CallbackQueryHandler(self.schedule)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            allow_reentry=True,
        )
