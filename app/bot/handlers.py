from telegram import Update
from telegram.ext import CallbackContext
from app.db.session import get_db
from app.db.queries.user_crud import get_or_create_user

async def start(update: Update, context: CallbackContext):
    tg_user = update.effective_user
    db = next(get_db())
    user = get_or_create_user(db, tg_user)
    await update.message.reply_text(f"Welcome {tg_user.username}!")
