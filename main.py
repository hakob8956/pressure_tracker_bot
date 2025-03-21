import logging
from telegram.ext import Application, CommandHandler
from handlers import start, log, report, remove_last, remove_by_date, remove_all, help_command, summarize
from db import init_db
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Change to DEBUG for more detailed output
)

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    logger.info("Initializing database...")
    init_db()  # Initialize the database
    
    logger.info("Starting the bot...")
    application = Application.builder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')  # Load Telegram bot token from .env
    ).build()

    # Log handler additions
    logger.info("Adding command handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("removelast", remove_last))
    application.add_handler(CommandHandler("removebydate", remove_by_date))
    application.add_handler(CommandHandler("removeall", remove_all))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(CommandHandler("help", help_command))
    
    logger.info("Bot is running, entering polling mode...")
    application.run_polling()

if __name__ == '__main__':
    main()