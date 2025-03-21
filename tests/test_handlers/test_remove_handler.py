import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from handlers.remove_handler import remove_last, remove_by_date, remove_all
from datetime import date

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_last_success(mock_db, mock_update, mock_context):
    """Test successful removal of last reading."""
    # Setup
    mock_db.remove_last_reading.return_value = True
    
    # Execute the handler
    await remove_last(mock_update, mock_context)
    
    # Check that remove_last_reading was called with correct user ID
    mock_db.remove_last_reading.assert_called_once_with(12345)
    
    # Check success message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "has been removed" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_last_no_readings(mock_db, mock_update, mock_context):
    """Test response when there are no readings to remove."""
    # Setup
    mock_db.remove_last_reading.return_value = False
    
    # Execute the handler
    await remove_last(mock_update, mock_context)
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "don't have any" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_by_date_success(mock_db, mock_update, mock_context):
    """Test successful removal of readings by date."""
    # Setup
    mock_update.message.text = "/removebydate 2023-01-01"
    mock_db.remove_readings_by_date.return_value = True
    
    # Execute the handler
    await remove_by_date(mock_update, mock_context)
    
    # Check that remove_readings_by_date was called with correct parameters
    mock_db.remove_readings_by_date.assert_called_once()
    args = mock_db.remove_readings_by_date.call_args[0]
    assert args[0] == 12345  # user_id
    assert args[1] == date(2023, 1, 1)  # target_date
    
    # Check success message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "have been removed" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_by_date_no_readings(mock_db, mock_update, mock_context):
    """Test response when no readings exist for the specified date."""
    # Setup
    mock_update.message.text = "/removebydate 2023-01-01"
    mock_db.remove_readings_by_date.return_value = False
    
    # Execute the handler
    await remove_by_date(mock_update, mock_context)
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "No readings found" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_by_date_missing_date(mock_db, mock_update, mock_context):
    """Test response when date is not provided."""
    # Setup
    mock_update.message.text = "/removebydate"
    
    # Execute the handler
    await remove_by_date(mock_update, mock_context)
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Please specify the date" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_by_date_invalid_date(mock_db, mock_update, mock_context):
    """Test response when invalid date format is provided."""
    # Setup
    mock_update.message.text = "/removebydate invalid-date"
    
    # Execute the handler
    await remove_by_date(mock_update, mock_context)
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Invalid date format" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_all_success(mock_db, mock_update, mock_context):
    """Test successful removal of all readings."""
    # Setup
    mock_db.remove_all_readings.return_value = True
    
    # Execute the handler
    await remove_all(mock_update, mock_context)
    
    # Check that remove_all_readings was called with correct user ID
    mock_db.remove_all_readings.assert_called_once_with(12345)
    
    # Check success message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "have been removed" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.remove_handler.db')
async def test_remove_all_no_readings(mock_db, mock_update, mock_context):
    """Test response when there are no readings to remove."""
    # Setup
    mock_db.remove_all_readings.return_value = False
    
    # Execute the handler
    await remove_all(mock_update, mock_context)
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    # Update the assertion to match the actual message
    assert "don't have any" in mock_update.message.reply_text.call_args[0][0] or \
           "No readings found" in mock_update.message.reply_text.call_args[0][0]