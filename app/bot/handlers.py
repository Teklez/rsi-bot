from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.db.session import get_db
from app.db.queries.user_crud import get_or_create_user


from app.utils.constants import SUPPORTED_SYMBOLS
from app.db.session import get_db
from app.db.models.user_symbol import UserSymbol
from app.db.models.user import User
from app.db.models.settings import Setting

async def start(update: Update, context: CallbackContext):
    tg_user = update.effective_user
    db = next(get_db())
    user = get_or_create_user(db, tg_user)
    await update.message.reply_text(f"Welcome {tg_user.username}!")




async def add_symbol_command(update: Update, context: CallbackContext):
    print(f"DEBUG: add_symbol_command called by user {update.effective_user.id}")
    
    # Create keyboard with 4 buttons per row
    keyboard = []
    for i in range(0, len(SUPPORTED_SYMBOLS), 4):
        row = [
            InlineKeyboardButton(symbol, callback_data=f"add_symbol:{symbol}")
            for symbol in SUPPORTED_SYMBOLS[i:i+4]
        ]
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a symbol to add:", reply_markup=reply_markup)

# 2. Callback to handle one-tap addition
async def add_symbol_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    symbol = query.data.split(":")[1]

    db = next(get_db())
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


async def settings_command(update: Update, context: CallbackContext):
    """Show current RSI settings and options to change them"""
    db = next(get_db())
    try:
        setting = db.query(Setting).first()
        oversold_threshold = setting.rsi_oversold_threshold if setting else 30
        overbought_threshold = setting.rsi_overbought_threshold if setting else 70
        
        keyboard = [
            [InlineKeyboardButton("Set Oversold Threshold", callback_data="set_oversold_threshold")],
            [InlineKeyboardButton("Set Overbought Threshold", callback_data="set_overbought_threshold")],
            [InlineKeyboardButton("View Current Settings", callback_data="view_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"🔧 RSI Settings\n\nOversold Threshold: {oversold_threshold}\nOverbought Threshold: {overbought_threshold}\n\nSelect an option:"
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    finally:
        db.close()


async def settings_callback(update: Update, context: CallbackContext):
    """Handle settings callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "view_settings":
        await view_settings(query)
    elif data.startswith("set_oversold_threshold"):
        await show_oversold_threshold_options(query)
    elif data.startswith("set_overbought_threshold"):
        await show_overbought_threshold_options(query)
    elif data.startswith("oversold_threshold_"):
        threshold = int(data.split("_")[2])
        await set_oversold_threshold(query, threshold)
    elif data.startswith("overbought_threshold_"):
        threshold = int(data.split("_")[2])
        await set_overbought_threshold(query, threshold)


async def view_settings(query):
    """Show current settings"""
    db = next(get_db())
    try:
        setting = db.query(Setting).first()
        oversold_threshold = setting.rsi_oversold_threshold if setting else 30
        overbought_threshold = setting.rsi_overbought_threshold if setting else 70
        
        message = f"📊 Current RSI Settings\n\nOversold Threshold: {oversold_threshold}\nOverbought Threshold: {overbought_threshold}\n\n• Oversold: Alerts when RSI drops below {oversold_threshold} (potential buying opportunity)\n• Overbought: Alerts when RSI rises above {overbought_threshold} (potential selling opportunity)"
        await query.edit_message_text(message)
        
    finally:
        db.close()


async def show_oversold_threshold_options(query):
    """Show oversold threshold selection options"""
    keyboard = [
        [InlineKeyboardButton("20 (Very Oversold)", callback_data="oversold_threshold_20")],
        [InlineKeyboardButton("25 (Oversold)", callback_data="oversold_threshold_25")],
        [InlineKeyboardButton("30 (Default)", callback_data="oversold_threshold_30")],
        [InlineKeyboardButton("35 (Less Sensitive)", callback_data="oversold_threshold_35")],
        [InlineKeyboardButton("40 (Very Less Sensitive)", callback_data="oversold_threshold_40")],
        [InlineKeyboardButton("Back to Settings", callback_data="view_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "📉 Select Oversold Threshold\n\nLower values = More sensitive alerts\nHigher values = Less sensitive alerts\n\nThis triggers when RSI drops below the threshold (potential buying opportunity)."
    await query.edit_message_text(message, reply_markup=reply_markup)


async def show_overbought_threshold_options(query):
    """Show overbought threshold selection options"""
    keyboard = [
        [InlineKeyboardButton("60 (Very Sensitive)", callback_data="overbought_threshold_60")],
        [InlineKeyboardButton("65 (Sensitive)", callback_data="overbought_threshold_65")],
        [InlineKeyboardButton("70 (Default)", callback_data="overbought_threshold_70")],
        [InlineKeyboardButton("75 (Less Sensitive)", callback_data="overbought_threshold_75")],
        [InlineKeyboardButton("80 (Very Less Sensitive)", callback_data="overbought_threshold_80")],
        [InlineKeyboardButton("Back to Settings", callback_data="view_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "📈 Select Overbought Threshold\n\nLower values = More sensitive alerts\nHigher values = Less sensitive alerts\n\nThis triggers when RSI rises above the threshold (potential selling opportunity)."
    await query.edit_message_text(message, reply_markup=reply_markup)


async def set_oversold_threshold(query, threshold: int):
    """Set the oversold RSI threshold"""
    db = next(get_db())
    try:
        setting = db.query(Setting).first()
        
        if not setting:
            setting = Setting(rsi_oversold_threshold=threshold, rsi_overbought_threshold=70)
            db.add(setting)
        else:
            setting.rsi_oversold_threshold = threshold
        
        db.commit()
        
        message = f"✅ Oversold threshold updated to {threshold}\n\nAlerts will now trigger when RSI drops below {threshold} (potential buying opportunity)."
        await query.edit_message_text(message)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Error updating oversold threshold: {str(e)}")
        db.rollback()
    finally:
        db.close()


async def set_overbought_threshold(query, threshold: int):
    """Set the overbought RSI threshold"""
    db = next(get_db())
    try:
        setting = db.query(Setting).first()
        
        if not setting:
            setting = Setting(rsi_oversold_threshold=30, rsi_overbought_threshold=threshold)
            db.add(setting)
        else:
            setting.rsi_overbought_threshold = threshold
        
        db.commit()
        
        message = f"✅ Overbought threshold updated to {threshold}\n\nAlerts will now trigger when RSI rises above {threshold} (potential selling opportunity)."
        await query.edit_message_text(message)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Error updating overbought threshold: {str(e)}")
        db.rollback()
    finally:
        db.close()
