import pytest
import sqlite3
from datetime import datetime, date
import re
import os
from models.database import Database

# Use a physical file for tests to avoid in-memory DB issues
TEST_DB_PATH = 'test_blood_pressure.db'

@pytest.fixture(scope="module")
def db_path():
    """Return a test database path and clean up after tests."""
    # Make sure we start with a fresh DB
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    yield TEST_DB_PATH
    
    # Clean up after tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture
def clean_db(db_path):
    """Provide a clean database for each test."""
    # Create a fresh DB
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize the database
    db = Database(db_path)
    return db

@pytest.fixture
def populated_db(db_path):
    """Create a database with sample readings."""
    # Start with a clean DB
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize the database
    db = Database(db_path)
    
    # Add sample readings
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

def test_init_db(db_path):
    """Test database initialization creates the expected table."""
    # Make sure we start with a clean slate
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create a new database
    db = Database(db_path)
    
    # Check if the table was created
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blood_pressure_readings'")
        table_exists = cursor.fetchone() is not None
    
    assert table_exists is True

def test_add_reading(clean_db):
    """Test adding a reading to the database."""
    # Add a reading
    reading_id = clean_db.add_reading(
        user_id=12345,
        systolic=120,
        diastolic=80,
        heart_rate=70,
        reading_datetime=datetime(2023, 1, 1, 12, 0),
        description="Test reading"
    )
    
    # Verify the reading was added
    assert reading_id is not None
    
    # Check if the reading exists in the database
    with sqlite3.connect(clean_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blood_pressure_readings WHERE id = ?", (reading_id,))
        reading = cursor.fetchone()
    
    assert reading is not None
    assert reading[1] == 12345  # user_id
    assert reading[2] == 120    # systolic
    assert reading[3] == 80     # diastolic
    assert reading[4] == 70     # heart_rate
    assert "Test reading" in reading[6]  # description

def test_get_readings_all(populated_db):
    """Test retrieving all readings for a user."""
    # Get all readings for user
    readings = populated_db.get_readings(user_id=12345)
    
    # Verify we got all readings
    assert len(readings) == 3
    
    # Check that readings are sorted by datetime
    assert "2023-01-01" in readings[0][3]
    assert "2023-01-02" in readings[1][3]
    assert "2023-01-03" in readings[2][3]

def test_get_readings_by_date(populated_db):
    """Test retrieving readings for a specific date."""
    # Get readings for a specific date
    readings = populated_db.get_readings(
        user_id=12345,
        start_date=date(2023, 1, 2)
    )
    
    # Verify we got only the readings for that date
    assert len(readings) == 1
    assert "2023-01-02" in readings[0][3]
    assert readings[0][0] == 140  # systolic for the elevated reading

def test_get_readings_by_date_range(populated_db):
    """Test retrieving readings within a date range."""
    # Get readings for a date range
    readings = populated_db.get_readings(
        user_id=12345,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 2)
    )
    
    # Verify we got only the readings in that range
    assert len(readings) == 2
    assert "2023-01-01" in readings[0][3]
    assert "2023-01-02" in readings[1][3]

def test_get_readings_with_regex(populated_db):
    """Test retrieving readings filtered by regex pattern."""
    # Get readings matching a regex pattern
    readings = populated_db.get_readings(
        user_id=12345,
        regex_pattern="elevated"
    )
    
    # Verify we got only the matching readings
    assert len(readings) == 1
    assert "Elevated" in readings[0][4]
    assert readings[0][0] == 140  # systolic for the elevated reading

def test_get_readings_with_invalid_regex(populated_db):
    """Test handling of invalid regex pattern."""
    # Try to get readings with an invalid regex
    with pytest.raises(ValueError) as excinfo:
        populated_db.get_readings(
            user_id=12345,
            regex_pattern="[invalid"
        )
    
    # Verify the correct error is raised
    assert "Invalid regex pattern" in str(excinfo.value)

def test_remove_last_reading(populated_db):
    """Test removing the most recent reading."""
    # Remove the last reading
    result = populated_db.remove_last_reading(user_id=12345)
    
    # Verify the reading was removed
    assert result is True
    
    # Check that the reading no longer exists
    readings = populated_db.get_readings(user_id=12345)
    assert len(readings) == 2
    
    # The most recent reading (Low reading from Jan 3) should be gone
    dates = [reading[3] for reading in readings]
    assert all("2023-01-03" not in date for date in dates)

def test_remove_readings_by_date(populated_db):
    """Test removing readings for a specific date."""
    # Remove readings for a specific date
    result = populated_db.remove_readings_by_date(
        user_id=12345,
        target_date=date(2023, 1, 2)
    )
    
    # Verify readings were removed
    assert result is True
    
    # Check that the readings no longer exist
    readings = populated_db.get_readings(user_id=12345)
    assert len(readings) == 2
    
    # The Jan 2 reading (Elevated reading) should be gone
    dates = [reading[3] for reading in readings]
    assert all("2023-01-02" not in date for date in dates)

def test_remove_all_readings(populated_db):
    """Test removing all readings for a user."""
    # Remove all readings
    result = populated_db.remove_all_readings(user_id=12345)
    
    # Verify readings were removed
    assert result is True
    
    # Check that no readings remain
    readings = populated_db.get_readings(user_id=12345)
    assert len(readings) == 0

def test_remove_nonexistent_reading(clean_db):
    """Test attempting to remove a reading that doesn't exist."""
    # Try to remove the last reading when there are none
    result = clean_db.remove_last_reading(user_id=12345)
    
    # Verify the operation failed
    assert result is False

def test_remove_readings_nonexistent_date(populated_db):
    """Test attempting to remove readings for a date with no readings."""
    # Try to remove readings for a date with no entries
    result = populated_db.remove_readings_by_date(
        user_id=12345,
        target_date=date(2023, 2, 1)
    )
    
    # Verify the operation failed
    assert result is False