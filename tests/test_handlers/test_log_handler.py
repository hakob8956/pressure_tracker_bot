import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from handlers.log_handler import log
from datetime import datetime

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_basic(mock_db, mock_update, mock_context):
    """Test basic blood pressure logging without optional parameters."""
    # Setup
    mock_update.message.text = "/log 120 80"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # Check database call
    mock_db.add_reading.assert_called_once()
    args = mock_db.add_reading.call_args[0]
    kwargs = mock_db.add_reading.call_args[1]
    
    # Verify correct user ID, systolic, and diastolic values
    assert args[0] == 12345  # user_id
    assert args[1] == "120"  # systolic
    assert args[2] == "80"   # diastolic
    assert args[3] is None   # heart_rate
    assert args[5] is None   # description
    
    # Check response message
    mock_update.message.reply_text.assert_called_once()
    assert "logged successfully" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_with_heart_rate(mock_db, mock_update, mock_context):
    """Test logging with heart rate."""
    # Setup
    mock_update.message.text = "/log 120 80 75"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # Check database call
    mock_db.add_reading.assert_called_once()
    args = mock_db.add_reading.call_args[0]
    
    # Verify heart rate was included
    assert args[3] == "75"  # heart_rate
    
    # Check response message
    assert "logged successfully" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_with_description(mock_db, mock_update, mock_context):
    """Test logging with description."""
    # Setup
    mock_update.message.text = "/log 120 80 75 After exercise"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # Check database call
    mock_db.add_reading.assert_called_once()
    args = mock_db.add_reading.call_args[0]
    
    # Verify description was included
    assert args[5] == "After exercise"  # description
    
    # Check response message
    assert "logged successfully" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_with_datetime(mock_db, mock_update, mock_context):
    """Test logging with custom datetime."""
    # Setup
    mock_update.message.text = "/log 120 80 75 After exercise 2023-01-01 08:30"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # Check database call
    mock_db.add_reading.assert_called_once()
    args = mock_db.add_reading.call_args[0]
    
    # Verify datetime was parsed correctly
    assert args[4].year == 2023
    assert args[4].month == 1
    assert args[4].day == 1
    assert args[4].hour == 8
    assert args[4].minute == 30
    
    # Check response message
    assert "logged successfully" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_invalid_format(mock_db, mock_update, mock_context):
    """Test response when command format is invalid."""
    # Setup
    mock_update.message.text = "/log invalid"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # Verify database was not called
    mock_db.add_reading.assert_not_called()
    
    # Check error message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Usage:" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.log_handler.db')
async def test_log_handler_invalid_datetime(mock_db, mock_update, mock_context):
    """Test handling of invalid datetime format."""
    # Setup 
    # Change to a format that will be caught by the regex but is an invalid date
    mock_update.message.text = "/log 120 80 75 After exercise 2023-99-99 99:99"
    
    # Execute the handler
    await log(mock_update, mock_context)
    
    # In this case, the database is not called because parse_datetime will raise an error
    # when it tries to parse the invalid datetime
    
    # Check error message was sent
    mock_update.message.reply_text.assert_called_once()
    # The handler should report a datetime format error, not the usage message
    assert "Invalid date" in mock_update.message.reply_text.call_args[0][0] or \
           "Invalid datetime" in mock_update.message.reply_text.call_args[0][0]