import re
import sqlite3
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import CallbackContext
from report_generator import generate_pdf
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Global cache: key -> (latest_reading_timestamp, advice)
cache = {}


# Set OpenAI API key

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
    # Regex to match command with optional heart rate, optional description, and optional datetime
    match = re.match(
        r'/log (\d+) (\d+)(?: (\d+))?(?: (.+?))?(?: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}))?$', text)

    if match:
        systolic, diastolic = match.group(1), match.group(2)
        heart_rate = match.group(3) if match.group(3) else None
        description = match.group(4) if match.group(4) else None
        datetime_str = match.group(5)
        try:
            datetime_input = datetime.now().replace(second=0, microsecond=0) if not datetime_str else datetime.strptime(
                datetime_str, "%Y-%m-%d %H:%M").replace(second=0, microsecond=0)  # Normalize datetime
        except ValueError:
            await update.message.reply_text('Invalid date/time format. Please use YYYY-MM-DD HH:MM format.')
            return

        with sqlite3.connect('blood_pressure.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO blood_pressure_readings (user_id, systolic, diastolic, heart_rate, reading_datetime, description)
                         VALUES (?, ?, ?, ?, ?, ?)''', (update.message.from_user.id, systolic, diastolic, heart_rate, datetime_input, description))

        await update.message.reply_text(f'Blood pressure (and heart rate, if provided) logged successfully for {datetime_input.strftime("%Y-%m-%d %H:%M")}.')
    else:
        await update.message.reply_text('Usage: /log <systolic> <diastolic> [heart rate] [description] [YYYY-MM-DD HH:MM]')

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
/log <systolic> <diastolic> [heart rate] [description] [YYYY-MM-DD HH:MM] - Log a new blood pressure reading. Heart rate, description, date, and time are optional.
/report [start_date] [end_date] - Generate a PDF report of your blood pressure readings. Date range is optional.
/removelast - Remove the most recent blood pressure reading.
/removebydate <YYYY-MM-DD> - Remove all readings for a specific date.
/removeall - Remove all readings.
/summarize [start_date] [end_date] - Summarize your blood pressure readings and get medical advice. Date range is optional.
/help - Show this help message.
"""
    await update.message.reply_text(help_text)
async def summarize(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = update.message.text.split()

    start_date = end_date = None
    if len(args) == 3:
        # User provided start and end dates
        try:
            start_date = datetime.strptime(args[1], "%Y-%m-%d").date()
            end_date = datetime.strptime(args[2], "%Y-%m-%d").date()
        except ValueError:
            await update.message.reply_text("Incorrect date format. Please use YYYY-MM-DD for both start and end dates.")
            return
    elif len(args) == 2:
        # User provided only one date: treat it as the start date and use today's date as the end date.
        try:
            start_date = datetime.strptime(args[1], "%Y-%m-%d").date()
            end_date = datetime.now().date()
        except ValueError:
            await update.message.reply_text("Incorrect date format. Please use YYYY-MM-DD.")
            return

    # Fetch readings from the database
    query, params = prepare_query(user_id, start_date, end_date)
    with sqlite3.connect('blood_pressure.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        readings = cursor.fetchall()

    if not readings:
        await update.message.reply_text("No blood pressure readings found for the specified date range.")
        return

    # Compute the maximum reading timestamp from the fetched readings.
    try:
        # Assume reading_datetime is in ISO format; adjust if necessary.
        max_timestamp = max(datetime.fromisoformat(r[3]) for r in readings)
    except Exception as e:
        await update.message.reply_text(f"Error parsing reading dates: {e}")
        return

    # Prepare cache key based on user and date range
    cache_key = (user_id, start_date, end_date)

    # Check if we already have cached advice and if the cached data is up-to-date
    if cache_key in cache:
        cached_max_timestamp, cached_advice = cache[cache_key]
        if cached_max_timestamp == max_timestamp:
            await update.message.reply_text("Please wait, fetching your medical advice from cache...")
            await update.message.reply_text(f"Medical Advice:\n{cached_advice}")
            return

    # Format the readings for ChatGPT
    formatted_readings = "\n".join(
        [f"Systolic: {r[0]}, Diastolic: {r[1]}, Heart Rate: {r[2] or 'N/A'}, Date: {r[3]}" for r in readings]
    )
    prompt = (
        f"Here are the blood pressure readings for a user:\n{formatted_readings}\n\n"
        "Please analyze the data and provide medical advice if needed."
    )

    # Inform the user that the advice is being fetched
    await update.message.reply_text("Please wait, fetching your medical advice...")

    # Send the data to ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        advice = response.choices[0].message.content
    except Exception as e:
        await update.message.reply_text(f"An error occurred while fetching advice: {e}")
        return

    # Cache the new advice along with the latest reading timestamp
    cache[cache_key] = (max_timestamp, advice)

    # Send the advice back to the user
    await update.message.reply_text(f"Medical Advice:\n{advice}")

def prepare_query(user_id: int, start_date: datetime.date = None, end_date: datetime.date = None):
    """
    Prepares the SQL query and parameters to fetch blood pressure readings
    based on the user ID and optional date range.
    """
    if start_date and end_date:
        query = '''SELECT systolic, diastolic, heart_rate, reading_datetime 
                   FROM blood_pressure_readings 
                   WHERE user_id = ? AND DATE(reading_datetime) BETWEEN ? AND ? 
                   ORDER BY reading_datetime'''
        params = (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    elif start_date:
        query = '''SELECT systolic, diastolic, heart_rate, reading_datetime 
                   FROM blood_pressure_readings 
                   WHERE user_id = ? AND DATE(reading_datetime) = ? 
                   ORDER BY reading_datetime'''
        params = (user_id, start_date.strftime("%Y-%m-%d"))
    else:
        query = '''SELECT systolic, diastolic, heart_rate, reading_datetime 
                   FROM blood_pressure_readings 
                   WHERE user_id = ? 
                   ORDER BY reading_datetime'''
        params = (user_id,)

    return query, params