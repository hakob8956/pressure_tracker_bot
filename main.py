from telegram.ext import Application, CommandHandler
from handlers import start, log, report, remove_last, remove_by_date, help_command
from db import init_db


def main() -> None:
    """Start the bot."""
    init_db()  # Initialize the database
    application = Application.builder().token(
        '7088463256:AAGVZfLViO_yUh2IO_7txHKE5xYR4tPnVeU').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("removelast", remove_last))
    application.add_handler(CommandHandler("removebydate", remove_by_date))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()


if __name__ == '__main__':
    main()
