from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from app.bot.handlers import start, add_symbol_command, add_symbol_callback, settings_command, settings_callback
from dotenv import load_dotenv
import os
load_dotenv()

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addsymbol", add_symbol_command))
app.add_handler(CommandHandler("settings", settings_command))
app.add_handler(CallbackQueryHandler(add_symbol_callback, pattern=r"^add_symbol:"))
app.add_handler(CallbackQueryHandler(settings_callback, pattern=r"^(set_oversold_threshold|set_overbought_threshold|view_settings|oversold_threshold_|overbought_threshold_)"))

