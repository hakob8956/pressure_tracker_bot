from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from utils.formatting import parse_date, extract_regex_pattern
from models.database import db
from services.analysis_service import analyze_readings

async def summarize(update: Update, context: CallbackContext) -> None:
    """Command to summarize blood pressure readings and get medical advice."""
    user_id = update.message.from_user.id
    full_text = update.message.text
    
    # Initialize variables
    start_date = end_date = None
    
    # Extract regex pattern from the command
    regex_pattern, clean_text = extract_regex_pattern(full_text)
    
    # Split the remaining text to get command and date arguments
    args = clean_text.strip().split()
    
    # Process date arguments
    try:
        if len(args) >= 3:  # /summarize + two dates
            start_date = parse_date(args[1])
            end_date = parse_date(args[2])
        elif len(args) >= 2:  # /summarize + one date
            start_date = parse_date(args[1])
            end_date = datetime.now().date()
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    
    # Inform the user that their request is being processed
    await update.message.reply_text("Please wait, analyzing your blood pressure readings...")
    
    # Get readings from database
    try:
        readings = db.get_readings(user_id, start_date, end_date, regex_pattern)
        
        if not readings:
            await update.message.reply_text("No blood pressure readings found for the specified criteria.")
            return
        
        # Analyze readings
        advice = analyze_readings(readings, user_id, start_date, end_date, regex_pattern)
        
        # Send the advice back to the user
        await update.message.reply_text(f"Medical Advice:\n{advice}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred while processing your request: {e}")