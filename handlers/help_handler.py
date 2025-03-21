from telegram import Update
from telegram.ext import CallbackContext

async def help_command(update: Update, context: CallbackContext) -> None:
    """Command to show help messages."""
    help_text = """
Here's how you can use this bot:

/start - Start the bot and get a welcome message.

/log <systolic> <diastolic> [heart rate] [description] [YYYY-MM-DD HH:MM] - Log a new blood pressure reading. Heart rate, description, date, and time are optional.

/report [start_date] [end_date] pattern:"regex" - Generate a PDF report of your blood pressure readings. Date range and regex pattern for filtering descriptions are optional.

/removelast - Remove the most recent blood pressure reading.

/removebydate <YYYY-MM-DD> - Remove all readings for a specific date.

/removeall - Remove all your blood pressure readings.

/summarize [start_date] [end_date] pattern:"regex" - Summarize your blood pressure readings and get medical advice. Date range and regex pattern for filtering descriptions are optional.

/help - Show this help message.

All dates should be in YYYY-MM-DD format. 
Times should be in 24-hour format (HH:MM).
"""
    await update.message.reply_text(help_text)