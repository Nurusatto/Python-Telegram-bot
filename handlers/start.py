from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ContextTypes
from DATA import MESSAGES

async def start( update: Update, context: ContextTypes.DEFAULT_TYPE):
        button_configs = MESSAGES["buttons"]

        keyboard = [
                [InlineKeyboardButton(text=btn["text"], callback_data=btn["data"])]
                for btn in button_configs
        ]
        
        buttons = InlineKeyboardMarkup(keyboard)

        text = MESSAGES["start"]["text"]
        assert update.message
        await update.message.reply_text(text,reply_markup=buttons)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer() # type: ignore
        await query.edit_message_text("Выбрано тестирование... ⏳") # type: ignore
