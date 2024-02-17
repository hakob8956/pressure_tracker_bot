# Blood Pressure Log Bot

The Blood Pressure Log Bot is a Telegram bot designed to help users track their blood pressure readings over time. It offers features for logging readings, generating reports, and managing logged data directly through Telegram.

## Features

- **Log Readings**: Users can log their systolic and diastolic blood pressure readings along with optional date and time.
- **Generate Reports**: Generates a PDF report of blood pressure readings for a specified date range or all logged readings.
- **Remove Readings**: Users can remove their most recent reading or all readings for a specific date.

## Getting Started

### Prerequisites

- Python 3.8+
- SQLite3
- Telegram account

### Installation

1. Clone the repository:
2. Install the required Python packages:
   ```
   pip install python-telegram-bot reportlab
   ```
3. Initialize the SQLite database:
   ```
   python -c 'from index import init_db; init_db()'
   ```
4. Set your Telegram Bot Token:
   - Replace `'YOUR_BOT_TOKEN'` in the `main` function with your actual bot token provided by BotFather.

### Running the Bot

Run the bot with the following command:

```
python index.py
```

## Usage

- **Start the Bot**: Send `/start` to get started with the bot.
- **Log a Reading**: Use `/log <systolic> <diastolic> [YYYY-MM-DD HH:MM]` to log a new blood pressure reading.
- **Generate a Report**: Send `/report [start_date] [end_date]` to generate and receive a PDF report.
- **Remove the Last Reading**: Use `/removelast` to remove your most recent reading.
- **Remove Readings by Date**: Use `/removebydate <YYYY-MM-DD>` to remove all readings for a specific date.
- **Help**: Send `/help` to see all available commands.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## License

[MIT](LICENSE) - See the LICENSE file for details.

---
