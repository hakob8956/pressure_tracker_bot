from telegram import Update, ForceReply
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
    """Command to start the bot and provide instructions."""
    user = update.effective_user
    start_message = (
        fr"Hi {user.mention_markdown_v2()}\! Welcome to the Blood Pressure Log Bot\.\n"
        "Use /log to record your blood pressure readings and /report to generate a PDF report of your readings\.\n"
        "For more commands and how to use them, send /help\."
    )
    await update.message.reply_markdown_v2(start_message, reply_markup=ForceReply(selective=True))