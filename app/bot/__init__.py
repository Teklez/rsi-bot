from telegram.ext import ApplicationBuilder, CommandHandler
from app.bot.handlers import start
from dotenv import load_dotenv
import os
load_dotenv()


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))

