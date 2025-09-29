from telegram.ext import ApplicationBuilder, CommandHandler
from app.bot.handlers import start
from telegram.ext import CallbackQueryHandler, ContextTypes
from app.bot.handlers import add_symbol_command, add_symbol_callback
from dotenv import load_dotenv
import os
load_dotenv()



application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

application.add_handler(CommandHandler("addsymbol", add_symbol_command))
application.add_handler(CallbackQueryHandler(add_symbol_callback, pattern=r"^add_symbol:"))

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))

