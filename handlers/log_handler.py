import re
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from models.database import db
from utils.formatting import parse_datetime

async def log(update: Update, context: CallbackContext) -> None:
    """Command to log a new blood pressure reading."""
    text = update.message.text
    # Regex to match command with optional heart rate, optional description, and optional datetime
    match = re.match(
        r'/log (\d+) (\d+)(?: (\d+))?(?: (.+?))?(?: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}))?$', text)

    if match:
        systolic, diastolic = match.group(1), match.group(2)
        heart_rate = match.group(3) if match.group(3) else None
        description = match.group(4) if match.group(4) else None
        datetime_str = match.group(5)
        
        try:
            reading_datetime = datetime.now().replace(second=0, microsecond=0)
            if datetime_str:
                reading_datetime = parse_datetime(datetime_str)
        except ValueError as e:
            await update.message.reply_text(str(e))
            return

        # Add reading to the database
        db.add_reading(
            update.message.from_user.id, 
            systolic, 
            diastolic, 
            heart_rate, 
            reading_datetime, 
            description
        )

        await update.message.reply_text(
            f'Blood pressure (and heart rate, if provided) logged successfully for '
            f'{reading_datetime.strftime("%Y-%m-%d %H:%M")}.'
        )
    else:
        await update.message.reply_text(
            'Usage: /log <systolic> <diastolic> [heart rate] [description] [YYYY-MM-DD HH:MM]'
        )