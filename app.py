from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler,CallbackQueryHandler
from typing import Any
from handlers import *

from conversation import *

class ShizukaBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()
        self.add_handlers()
        self.app.post_init = self.set_commands

        print("---------------")
        print("Бот запущен ✅")
        print("---------------")

    def add_handlers(self):
        self.app.add_handler(CommandHandler("start",start))
        self.app.add_handler(TestConversation().get_handler())

        self.app.add_handler(CallbackQueryHandler(button_handler))



    async def set_commands(self, app:Any):
        await app.bot.set_my_commands([
            BotCommand("start", "Запустить бота"),
        ])

    def run(self):
        self.app.run_polling()


if __name__ == "__main__":
    bot = ShizukaBot("7143012249:AAEOghUwq03TtvyoFlEnjW9dN4a_SBE7URM")
    bot.run()
