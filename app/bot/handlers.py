from telegram import Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.db.session import get_db
from app.db.queries.user_crud import get_or_create_user


from app.utils.constants import SYMBOLS
from app.db.session import get_db
from app.db.models.user_symbol import UserSymbol
from app.db.models.user import User

async def start(update: Update, context: CallbackContext):
    tg_user = update.effective_user
    db = next(get_db())
    user = get_or_create_user(db, tg_user)
    await update.message.reply_text(f"Welcome {tg_user.username}!")




async def add_symbol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(symbol, callback_data=f"add_symbol:{symbol}")]
        for symbol in SYMBOLS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a symbol to add:", reply_markup=reply_markup)

# 2. Callback to handle one-tap addition
async def add_symbol_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    symbol = query.data.split(":")[1]

    db = get_db()
    tg_user_id = query.from_user.id

    user = db.query(User).filter(User.telegram_id == tg_user_id).first()
    if not user:
        await query.edit_message_text("User not found. Start with /start first.")
        return

    # Check if symbol already added
    if any(s.symbol == symbol for s in user.symbols):
        await query.edit_message_text(f"{symbol} is already added.")
        return

    new_symbol = UserSymbol(user_id=user.id, symbol=symbol)
    db.add(new_symbol)
    db.commit()

    await query.edit_message_text(f"✅ {symbol} added successfully!")
