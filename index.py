import re
import sqlite3
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Initialize SQLite Database


def init_db(db_path='blood_pressure.db'):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS blood_pressure_readings (
                     id INTEGER PRIMARY KEY,
                     user_id INTEGER NOT NULL,
                     systolic INTEGER NOT NULL,
                     diastolic INTEGER NOT NULL,
                     heart_rate INTEGER NULL,
                     reading_datetime DATETIME NOT NULL)''')

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


def generate_pdf(user_id, db_path='blood_pressure.db', start_date=None, end_date=None):
    filename = f'{user_id}_blood_pressure_report.pdf'
    pdf_canvas = canvas.Canvas(filename, pagesize=letter)

    # Base query to fetch readings
    query = '''SELECT systolic, diastolic, heart_rate, reading_datetime FROM blood_pressure_readings WHERE user_id = ?'''
    params = [user_id]

    # Extend query for date filtering
    if start_date and end_date:
        query += " AND DATE(reading_datetime) BETWEEN ? AND ?"
        params.extend([start_date.strftime("%Y-%m-%d"),
                      end_date.strftime("%Y-%m-%d")])
    elif start_date:  # Single day report
        query += " AND DATE(reading_datetime) = ?"
        params.append(start_date.strftime("%Y-%m-%d"))
    query += " ORDER BY reading_datetime"

    # Connect to the database and fetch readings
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        readings = cursor.fetchall()

    # Prepare to write on the PDF
    text = pdf_canvas.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.textLine("Blood Pressure Readings Report")

    # Loop through and add readings to PDF
    current_date = None
    for systolic, diastolic, heart_rate, reading_datetime in readings:
        reading_date = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").date()
        if reading_date != current_date:
            if current_date is not None:
                text.textLine("")  # Spacer between days
            date_header = reading_date.strftime('%A, %B %d, %Y')
            text.textLine(date_header)
            current_date = reading_date

        time_str = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").strftime('%H:%M')
        heart_str = f", Heart Rate: {heart_rate}" if heart_rate else ""
        line = f"    {time_str} - Systolic: {systolic}, Diastolic: {diastolic}{heart_str}"
        text.textLine(line)

    # Calculate and add average blood pressure
    avg_query = '''SELECT AVG(systolic) AS avg_systolic, AVG(diastolic) AS avg_diastolic, AVG(heart_rate) AS avg_heart FROM blood_pressure_readings WHERE user_id = ?'''
    if start_date and end_date:
        avg_query += " AND DATE(reading_datetime) BETWEEN ? AND ?"
    elif start_date:
        avg_query += " AND DATE(reading_datetime) = ?"
    cursor.execute(avg_query, params)
    avg_systolic, avg_diastolic, avg_heart = cursor.fetchone()

    # Append average blood pressure to the PDF
    text.textLine("")  # Spacer before averages
    avg_line = f"Average Blood Pressure: Systolic: {round(avg_systolic, 2)}, Diastolic: {round(avg_diastolic, 2)} BPM: {round(avg_heart, 2)}"
    text.textLine(avg_line)

    # Finalize and save PDF
    pdf_canvas.drawText(text)
    pdf_canvas.save()

    return filename
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


async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
Here's how you can use this bot:
/start - Start the bot and get a welcome message.
/log <systolic> <diastolic> [heart rate] [YYYY-MM-DD HH:MM] - Log a new blood pressure reading. Date and time are optional.
/report [start_date] [end_date] - Generate a PDF report of your blood pressure readings. Date range is optional.
/removelast - Remove the most recent blood pressure reading.
/removebydate <YYYY-MM-DD> - Remove all readings for a specific date.
/help - Show this help message.
"""
    await update.message.reply_text(help_text)


def main() -> None:
    """Start the bot."""
    init_db()  # Initialize the database
    application = Application.builder().token(
        'YOUR_BOT_TOKEN').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("removelast", remove_last))
    application.add_handler(CommandHandler("removebydate", remove_by_date))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()


if __name__ == '__main__':
    main()
