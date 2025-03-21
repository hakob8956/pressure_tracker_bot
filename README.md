# Blood Pressure Tracking Telegram Bot

A Telegram bot for tracking blood pressure readings, generating reports, and providing medical advice based on your readings.

## Features

- Log blood pressure readings with optional heart rate and notes
- Generate PDF reports of your readings with data visualization
- Filter readings by date range and description pattern
- Get AI-powered medical advice based on your readings
- Manage your readings (remove last, by date, or all)

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blood-pressure-bot.git
   cd blood-pressure-bot
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   LOG_LEVEL=INFO
   ```

4. Run the bot:
   ```
   python main.py
   ```

## Commands

- `/start` - Start the bot and get a welcome message
- `/log <systolic> <diastolic> [heart rate] [description] [YYYY-MM-DD HH:MM]` - Log a new reading
- `/report [start_date] [end_date] pattern:"regex"` - Generate a PDF report
- `/removelast` - Remove the most recent reading
- `/removebydate <YYYY-MM-DD>` - Remove all readings for a specific date
- `/removeall` - Remove all readings
- `/summarize [start_date] [end_date] pattern:"regex"` - Get medical advice
- `/help` - Show the help message

## Project Structure

```
blood_pressure_bot/
├── main.py             # Application entry point
├── config.py           # Configuration settings
├── models/             # Data models and database interactions
├── handlers/           # Telegram command handlers
├── services/           # Business logic services
├── utils/              # Helper utilities
└── blood_pressure.db   # SQLite database
```

## License

MIT License