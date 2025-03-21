import logging
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL

# Import handlers
from handlers.start_handler import start
from handlers.log_handler import log
from handlers.report_handler import report
from handlers.remove_handler import remove_last, remove_by_date, remove_all
from handlers.summarize_handler import summarize
from handlers.help_handler import help_command

# Initialize database
from models.database import init_db

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting the bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    logger.info("Registering command handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("removelast", remove_last))
    application.add_handler(CommandHandler("removebydate", remove_by_date))
    application.add_handler(CommandHandler("removeall", remove_all))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()