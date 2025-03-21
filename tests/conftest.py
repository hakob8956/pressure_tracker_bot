import pytest
import os
import sqlite3
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

# Set up test environment
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_key'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Import after setting environment variables
from models.database import Database
from models.reading import Reading

# Common test database path
TEST_DB_PATH = 'test_common_db.db'

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Clean up any test files before and after all tests."""
    # Clean up before tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    yield
    
    # Clean up after tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture
def test_db_path():
    """Return a temporary database path."""
    return TEST_DB_PATH

@pytest.fixture
def test_db(test_db_path):
    """Create a test database."""
    # Ensure the database exists with the correct schema
    db = Database(test_db_path)
    return db

@pytest.fixture
def sample_reading():
    """Return a sample reading object."""
    return Reading(
        systolic=120,
        diastolic=80,
        heart_rate=70,
        reading_datetime=datetime(2023, 1, 1, 12, 0),
        description="Test reading",
        user_id=12345
    )

@pytest.fixture
def mock_update():
    """Create a mock Update object for telegram."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.message.reply_markdown_v2 = AsyncMock()
    update.message.from_user = MagicMock()
    update.message.from_user.id = 12345
    update.effective_user = MagicMock()
    update.effective_user.mention_markdown_v2 = MagicMock(return_value="@test_user")
    return update

@pytest.fixture
def mock_context():
    """Create a mock Context object for telegram."""
    context = MagicMock()
    context.bot = MagicMock()
    return context

@pytest.fixture
def populated_db(test_db_path):
    """Create a database with sample readings."""
    # Create a new instance to ensure a clean state
    db = Database(test_db_path)
    
    # Add sample data
    db.add_reading(
        user_id=12345,
        systolic=120,
        diastolic=80,
        heart_rate=70,
        reading_datetime=datetime(2023, 1, 1, 12, 0),
        description="Normal reading"
    )
    db.add_reading(
        user_id=12345,
        systolic=140,
        diastolic=90,
        heart_rate=75,
        reading_datetime=datetime(2023, 1, 2, 12, 0),
        description="Elevated reading"
    )
    db.add_reading(
        user_id=12345,
        systolic=110,
        diastolic=70,
        heart_rate=65,
        reading_datetime=datetime(2023, 1, 3, 12, 0),
        description="Low reading"
    )
    return db

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test medical advice"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client