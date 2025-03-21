import os
import re
from telegram import Update
from telegram.ext import CallbackContext
from utils.formatting import parse_date, extract_regex_pattern
from services.report_generator import generate_pdf

async def report(update: Update, context: CallbackContext) -> None:
    """Command to generate a PDF report of blood pressure readings."""
    user_id = update.message.from_user.id
    full_text = update.message.text

    # Inform the user that the report is being generated
    await update.message.reply_text("Generating your blood pressure report. Please wait...")

    # Initialize variables
    start_date = end_date = None

    # Extract regex pattern from the command
    regex_pattern, clean_text = extract_regex_pattern(full_text)

    # Split the remaining text to get command and date arguments
    args = clean_text.strip().split()

    # Process date arguments
    try:
        if len(args) >= 3:  # /report + two dates
            start_date = parse_date(args[1])
            end_date = parse_date(args[2])
        elif len(args) >= 2:  # /report + one date
            start_date = end_date = parse_date(args[1])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return

    # Validate regex pattern
    if regex_pattern:
        try:
            re.compile(regex_pattern)
        except re.error:
            await update.message.reply_text(
                f'Invalid regex pattern: "{regex_pattern}". Please check your pattern syntax.'
            )
            return

    try:
        # Generate the report
        filename = generate_pdf(user_id, start_date=start_date, end_date=end_date, 
                               regex_pattern=regex_pattern)
        
        with open(filename, 'rb') as f:
            await update.message.reply_document(document=f, caption='Here is your blood pressure report.')
    except Exception as e:
        if "invalid regex" in str(e).lower():
            await update.message.reply_text(
                f'Error with regex pattern: "{regex_pattern}". The pattern could not be applied. '
                f'Please try a simpler pattern or check the syntax.'
            )
        else:
            await update.message.reply_text(f"An error occurred while generating the report: {e}")
    finally:
        # Clean up the file if it exists
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)