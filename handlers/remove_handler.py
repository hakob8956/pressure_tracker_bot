from telegram import Update
from telegram.ext import CallbackContext
from models.database import db
from utils.formatting import parse_date

async def remove_last(update: Update, context: CallbackContext) -> None:
    """Command to remove the last blood pressure reading."""
    user_id = update.message.from_user.id
    
    if db.remove_last_reading(user_id):
        await update.message.reply_text("Your last blood pressure reading has been removed.")
    else:
        await update.message.reply_text("You don't have any logged blood pressure readings to remove.")

async def remove_by_date(update: Update, context: CallbackContext) -> None:
    """Command to remove all readings for a specific date."""
    user_id = update.message.from_user.id
    args = update.message.text.split()

    if len(args) < 2:
        await update.message.reply_text("Please specify the date in YYYY-MM-DD format.")
        return

    try:
        target_date = parse_date(args[1])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return

    if db.remove_readings_by_date(user_id, target_date):
        await update.message.reply_text(
            f"Blood pressure readings for {target_date.strftime('%Y-%m-%d')} have been removed."
        )
    else:
        await update.message.reply_text("No readings found for the specified date.")

async def remove_all(update: Update, context: CallbackContext) -> None:
    """Command to remove all readings."""
    user_id = update.message.from_user.id
    
    if db.remove_all_readings(user_id):
        await update.message.reply_text("All your blood pressure readings have been removed.")
    else:
        await update.message.reply_text("You don't have any logged blood pressure readings to remove.")