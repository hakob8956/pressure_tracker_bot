import sqlite3
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Initialize SQLite Database


def init_db(db_path='blood_pressure.db'):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS blood_pressure_readings (
                     id INTEGER PRIMARY KEY,
                     user_id INTEGER NOT NULL,
                     systolic INTEGER NOT NULL,
                     diastolic INTEGER NOT NULL,
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
    parts = text.split()
    user_id = update.message.from_user.id

    if len(parts) == 3 or len(parts) == 5:
        systolic, diastolic = parts[1], parts[2]
        datetime_input = datetime.now() if len(parts) == 3 else datetime.strptime(
            f"{parts[3]} {parts[4]}", "%Y-%m-%d %H:%M")
        datetime_input = datetime_input.replace(
            second=0, microsecond=0)  # Normalize datetime

        with sqlite3.connect('blood_pressure.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO blood_pressure_readings (user_id, systolic, diastolic, reading_datetime)
                         VALUES (?, ?, ?, ?)''', (user_id, systolic, diastolic, datetime_input))

        await update.message.reply_text(f'Blood pressure logged successfully for {datetime_input.strftime("%Y-%m-%d %H:%M")}.')
    else:
        await update.message.reply_text('Usage: /log <systolic> <diastolic> [YYYY-MM-DD HH:MM]')

# Generate a PDF report of the user's blood pressure readings


def generate_pdf(user_id, db_path='blood_pressure.db', start_date=None, end_date=None):
    filename = f'{user_id}_blood_pressure_report.pdf'
    pdf_canvas = canvas.Canvas(filename, pagesize=letter)

    # Build the base query with optional date range filtering
    query = '''SELECT systolic, diastolic, reading_datetime FROM blood_pressure_readings 
               WHERE user_id = ?'''
    params = [user_id]

    if start_date and end_date:
        query += " AND DATE(reading_datetime) BETWEEN ? AND ?"
        params.extend([start_date.strftime("%Y-%m-%d"),
                      end_date.strftime("%Y-%m-%d")])
    elif start_date:  # Allows for a single day report
        query += " AND DATE(reading_datetime) = ?"
        params.append(start_date.strftime("%Y-%m-%d"))

    query += " ORDER BY reading_datetime"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        readings = cursor.fetchall()

    text = pdf_canvas.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.textLine("Blood Pressure Readings Report")

    current_date = None
    for systolic, diastolic, reading_datetime in readings:
        reading_date = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").date()
        if reading_date != current_date:
            # This is a new day, so print the date header
            if current_date is not None:  # Add a spacer between days, but not before the first
                text.textLine("")
            date_header = reading_date.strftime('%A, %Y-%m-%d')
            text.textLine(date_header)
            current_date = reading_date

        # Print the reading information
        time_str = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").strftime('%H:%M')
        line = f"    {time_str} - Systolic: {systolic}, Diastolic: {diastolic}"
        text.textLine(line)

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
/log <systolic> <diastolic> [YYYY-MM-DD HH:MM] - Log a new blood pressure reading. Date and time are optional.
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
