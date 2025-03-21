import pytest
from datetime import datetime
from models.reading import Reading

def test_reading_initialization():
    """Test that Reading objects are initialized correctly."""
    # Create a reading with all fields
    reading = Reading(
        systolic=120,
        diastolic=80,
        heart_rate=70,
        reading_datetime=datetime(2023, 1, 1, 12, 0),
        description="Test reading",
        user_id=12345,
        id=1
    )
    
    # Verify all fields were set correctly
    assert reading.systolic == 120
    assert reading.diastolic == 80
    assert reading.heart_rate == 70
    assert reading.reading_datetime == datetime(2023, 1, 1, 12, 0)
    assert reading.description == "Test reading"
    assert reading.user_id == 12345
    assert reading.id == 1

def test_reading_from_tuple():
    """Test creating a Reading object from a database tuple."""
    # Create a reading from a tuple
    data_tuple = (120, 80, 70, "2023-01-01 12:00:00", "Test reading")
    reading = Reading.from_tuple(data_tuple)
    
    # Verify the reading was created correctly
    assert reading.systolic == 120
    assert reading.diastolic == 80
    assert reading.heart_rate == 70
    assert reading.reading_datetime == datetime(2023, 1, 1, 12, 0)
    assert reading.description == "Test reading"

def test_reading_default_values():
    """Test that default values are set when not provided."""
    # Create a reading with minimal fields
    reading = Reading(systolic=120, diastolic=80)
    
    # Verify default values were set
    assert reading.heart_rate is None
    assert reading.description is None
    assert reading.id is None
    assert reading.user_id is None
    # reading_datetime should be a valid datetime, but we won't check 
    # exact time to avoid timing issues
    assert isinstance(reading.reading_datetime, datetime)

def test_reading_is_normal():
    """Test the is_normal property."""
    # Normal reading
    reading = Reading(systolic=119, diastolic=79)
    assert reading.is_normal is True
    
    # Not normal reading
    reading = Reading(systolic=120, diastolic=79)
    assert reading.is_normal is False

def test_reading_is_elevated():
    """Test the is_elevated property."""
    # Elevated reading
    reading = Reading(systolic=125, diastolic=75)
    assert reading.is_elevated is True
    
    # Not elevated reading (systolic too low)
    reading = Reading(systolic=119, diastolic=75)
    assert reading.is_elevated is False
    
    # Not elevated reading (diastolic too high)
    reading = Reading(systolic=125, diastolic=80)
    assert reading.is_elevated is False

def test_reading_is_stage1():
    """Test the is_stage1 property."""
    # Stage 1 by systolic
    reading = Reading(systolic=135, diastolic=75)
    assert reading.is_stage1 is True
    
    # Stage 1 by diastolic
    reading = Reading(systolic=125, diastolic=85)
    assert reading.is_stage1 is True
    
    # Not stage 1 (too low)
    reading = Reading(systolic=125, diastolic=75)
    assert reading.is_stage1 is False
    
    # Not stage 1 (too high)
    reading = Reading(systolic=145, diastolic=95)
    assert reading.is_stage1 is False

def test_reading_is_stage2():
    """Test the is_stage2 property."""
    # Stage 2 by systolic
    reading = Reading(systolic=145, diastolic=85)
    assert reading.is_stage2 is True
    
    # Stage 2 by diastolic
    reading = Reading(systolic=135, diastolic=95)
    assert reading.is_stage2 is True
    
    # Not stage 2 (too low)
    reading = Reading(systolic=135, diastolic=85)
    assert reading.is_stage2 is False
    
    # Not stage 2 (crisis level)
    reading = Reading(systolic=185, diastolic=125)
    assert reading.is_stage2 is True  # Note: Stage 2 is TRUE because is_crisis is a separate classification

def test_reading_is_crisis():
    """Test the is_crisis property."""
    # Crisis by systolic
    reading = Reading(systolic=185, diastolic=85)
    assert reading.is_crisis is True
    
    # Crisis by diastolic
    reading = Reading(systolic=145, diastolic=125)
    assert reading.is_crisis is True
    
    # Not crisis (too low)
    reading = Reading(systolic=175, diastolic=115)
    assert reading.is_crisis is False

def test_reading_str_representation():
    """Test the string representation of Reading."""
    # Reading with all fields
    reading = Reading(
        systolic=120,
        diastolic=80,
        heart_rate=70,
        reading_datetime=datetime(2023, 1, 1, 12, 0),
        description="Test reading"
    )
    
    # Verify string representation
    reading_str = str(reading)
    assert "12:00" in reading_str
    assert "Systolic: 120" in reading_str
    assert "Diastolic: 80" in reading_str
    assert "Heart Rate: 70" in reading_str
    assert "Description: Test reading" in reading_str
    
    # Reading without optional fields
    reading = Reading(
        systolic=120,
        diastolic=80,
        reading_datetime=datetime(2023, 1, 1, 12, 0)
    )
    
    # Verify string representation without optional fields
    reading_str = str(reading)
    assert "Heart Rate" not in reading_str
    assert "Description" not in reading_str