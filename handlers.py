import re
import sqlite3
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import CallbackContext
from report_generator import generate_pdf
# Command to start the bot and provide instructions


async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    start_message = (
        fr"Hi {user.mention_markdown_v2()}\! Welcome to the Blood Pressure Log Bot\.\n"
        "Use /log to record your blood pressure readings and /report to generate a PDF report of your readings\.\n"
        "For more commands and how to use them, send /help\."
    )
    await update.message.reply_markdown_v2(start_message, reply_markup=ForceReply(selective=True))

# Command to log a new blood pressure reading


async def log(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    # Regex to match command with optional heart rate and optional datetime
    match = re.match(
        r'/log (\d+) (\d+)(?: (\d+))?(?: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}))?$', text)

    if match:
        systolic, diastolic = match.group(1), match.group(2)
        heart_rate = match.group(3) if match.group(3) else None
        datetime_str = match.group(4)
        try:
            datetime_input = datetime.now().replace(second=0, microsecond=0) if not datetime_str else datetime.strptime(
                datetime_str, "%Y-%m-%d %H:%M").replace(second=0, microsecond=0)  # Normalize datetime
        except ValueError:
            await update.message.reply_text('Invalid date/time format. Please use YYYY-MM-DD HH:MM format.')
            return

        with sqlite3.connect('blood_pressure.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO blood_pressure_readings (user_id, systolic, diastolic, heart_rate, reading_datetime)
                         VALUES (?, ?, ?, ?, ?)''', (update.message.from_user.id, systolic, diastolic, heart_rate, datetime_input))

        await update.message.reply_text(f'Blood pressure (and heart rate, if provided) logged successfully for {datetime_input.strftime("%Y-%m-%d %H:%M")}.')
    else:
        await update.message.reply_text('Usage: /log <systolic> <diastolic> [heart rate] [YYYY-MM-DD HH:MM]')


# Command to send the PDF report
async def report(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = update.message.text.split()  # Split the command input

    start_date = end_date = None
    if len(args) == 3:
        # User provided start and/or end date
        try:
            start_date = datetime.strptime(args[1], "%Y-%m-%d").date()
            end_date = datetime.strptime(args[2], "%Y-%m-%d").date()
        except ValueError:
            await update.message.reply_text('Incorrect date format. Please use YYYY-MM-DD for both start and end dates.')
            return
    elif len(args) == 2:
        # User provided only one date, use it as both start and end date for a single day report
        try:
            start_date = end_date = datetime.strptime(
                args[1], "%Y-%m-%d").date()
        except ValueError:
            await update.message.reply_text('Incorrect date format. Please use YYYY-MM-DD.')
            return

    # Pass the date range to generate_pdf
    filename = generate_pdf(user_id, start_date=start_date, end_date=end_date)
    with open(filename, 'rb') as f:
        await update.message.reply_document(document=f, caption='Here is your blood pressure report.')


# Command to remove the last blood pressure reading
async def remove_last(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    with sqlite3.connect('blood_pressure.db') as conn:
        cursor = conn.cursor()
        # Find the most recent reading's ID
        cursor.execute('''SELECT id FROM blood_pressure_readings WHERE user_id = ? 
                          ORDER BY reading_datetime DESC LIMIT 1''', (user_id,))
        last_reading = cursor.fetchone()

        if last_reading:
            # Delete the most recent reading
            cursor.execute(
                'DELETE FROM blood_pressure_readings WHERE id = ?', (last_reading[0],))
            await update.message.reply_text("Your last blood pressure reading has been removed.")
        else:
            await update.message.reply_text("You don't have any logged blood pressure readings to remove.")


# Command to remove all readings for a specific date
async def remove_by_date(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = update.message.text.split()

    if len(args) < 2:
        await update.message.reply_text("Please specify the date in YYYY-MM-DD format.")
        return

    try:
        target_date = datetime.strptime(args[1], "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("Incorrect date format. Please use YYYY-MM-DD.")
        return

    with sqlite3.connect('blood_pressure.db') as conn:
        cursor = conn.cursor()
        # Delete readings for the specified date
        cursor.execute('''DELETE FROM blood_pressure_readings WHERE user_id = ? 
                          AND DATE(reading_datetime) = ?''', (user_id, target_date.strftime("%Y-%m-%d")))

        if cursor.rowcount > 0:
            await update.message.reply_text(f"Blood pressure readings for {target_date.strftime('%Y-%m-%d')} have been removed.")
        else:
            await update.message.reply_text("No readings found for the specified date.")

# Command to remove all readings


async def remove_all(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    with sqlite3.connect('blood_pressure.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM blood_pressure_readings WHERE user_id = ?', (user_id,))

        conn.commit()

        if cursor.rowcount > 0:
            await update.message.reply_text("Blood pressure readings have been removed.")
        else:
            await update.message.reply_text("No readings found.")

# Command to show help messages
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
Here's how you can use this bot:
/start - Start the bot and get a welcome message.
/log <systolic> <diastolic> [heart rate] [YYYY-MM-DD HH:MM] - Log a new blood pressure reading. Date and time are optional.
/report [start_date] [end_date] - Generate a PDF report of your blood pressure readings. Date range is optional.
/removelast - Remove the most recent blood pressure reading.
/removebydate <YYYY-MM-DD> - Remove all readings for a specific date.
/removeall - Remove all readings.
/help - Show this help message.
"""
    await update.message.reply_text(help_text)
