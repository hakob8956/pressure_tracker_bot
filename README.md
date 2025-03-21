# Blood Pressure Tracking Telegram Bot
![Tests](https://github.com/hakob8956/pressure_tracker_bot/actions/workflows/python-tests.yml/badge.svg)

[![codecov](https://codecov.io/gh/hakob8956/pressure_tracker_bot/branch/main/graph/badge.svg)](https://codecov.io/gh/hakob8956/pressure_tracker_bot)


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
├── tests/              # Unit and integration tests
└── blood_pressure.db   # SQLite database
```

## Testing

The project includes comprehensive test coverage for all components:

```
tests/
├── conftest.py                # Pytest fixtures
├── test_handlers/             # Tests for all Telegram command handlers
├── test_models/               # Tests for database and data models
├── test_services/             # Tests for business logic services
└── test_utils/                # Tests for helper utilities
```

### Running Tests

Run all tests:

```
pytest
```

Run specific test modules:

```
pytest tests/test_handlers/test_log_handler.py
```

Run with coverage report:

```
pytest --cov=. --cov-report=term-missing
```

### Test Features

- **Isolated testing**: All tests use mocking to avoid external API calls
- **No token usage**: Tests for AI features don't consume OpenAI API tokens
- **Database testing**: Uses file-based SQLite databases for reliable testing
- **Comprehensive coverage**: Tests include success cases, edge cases, and error handling

### Testing Dependencies

All testing dependencies are included in requirements.txt:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock

## License

MIT License