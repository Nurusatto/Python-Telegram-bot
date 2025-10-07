from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from DATA import TEST
from utils import check_answer # type: ignore

ASK_NAME ,ASK_1 ,ASK_2 ,ASK_3 ,ASK_4 ,ASK_5 = range(6)


class TestConversation:
    def __init__(self):
       
        self.name_key = ""
        self.correct_answer = 0
        self.state={
                "correct" : 'correct',
                "wrong ": "wrong"
            }
        self.alert={
            "yes":"✅ Правильно!",
            "no":"❌ Неправильно!"
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text("Как тебя зовут?") # type: ignore
        else:
            await update.message.reply_text("Как тебя зовут?")#type: ignore
        return ASK_NAME

    async def ask_one(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data[name] = update.message.text # type: ignore
        await update.message.reply_text("Тест начат") #type:ignore
        
        keyboard = [
                [InlineKeyboardButton(text=TEST[0]["options"]['correct'], callback_data=self.state['correct'])],
                [InlineKeyboardButton(text=TEST[0]["options"]['wrong'], callback_data=self.state['wrong'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query = update.callback_query

        await update.message.reply_text(TEST[0]["question"],reply_markup=reply_markup) # type: ignore
        await query.answer() # type: ignore
        
        return ASK_1



    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()#type:ignore

        if check_answer(query.data, "correct"):#type:ignore
            self.correct_answer += 1
            await query.edit_message_text(self.alert["yes"])#type:ignore
        else:
            await query.edit_message_text(self.alert["no"])#type:ignore

        await query.message.reply_text("Секунду, подготавливаю новый тест...")#type:ignore

        return 


    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Тест окончен") # type: ignore
        return ConversationHandler.END

    def get_handler(self):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start)],
            states={
                ASK_NAME: [CallbackQueryHandler(self.handle_answer)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
