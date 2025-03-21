import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from handlers.summarize_handler import summarize
from datetime import date

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_basic(mock_db, mock_analyze, mock_update, mock_context):
    """Test basic summarization without filters."""
    # Setup
    mock_update.message.text = "/summarize"
    mock_db.get_readings.return_value = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading")
    ]
    mock_analyze.return_value = "Test medical advice"
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that get_readings was called with correct parameters
    mock_db.get_readings.assert_called_once_with(
        12345, None, None, None
    )
    
    # Check that analyze_readings was called
    mock_analyze.assert_called_once()
    
    # Check that response messages were sent
    assert mock_update.message.reply_text.call_count == 2
    first_call = mock_update.message.reply_text.call_args_list[0]
    second_call = mock_update.message.reply_text.call_args_list[1]
    assert "Please wait" in first_call[0][0]
    assert "Medical Advice" in second_call[0][0]

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_with_date(mock_db, mock_analyze, mock_update, mock_context):
    """Test summarization with specific date."""
    # Setup
    mock_update.message.text = "/summarize 2023-01-01"
    mock_db.get_readings.return_value = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading")
    ]
    mock_analyze.return_value = "Test medical advice"
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that get_readings was called with correct date parameters
    mock_db.get_readings.assert_called_once()
    call_args = mock_db.get_readings.call_args[0]
    assert call_args[0] == 12345  # user_id
    assert call_args[1] == date(2023, 1, 1)  # start_date
    
    # Check that response contains medical advice
    assert "Medical Advice" in mock_update.message.reply_text.call_args_list[1][0][0]

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_with_date_range(mock_db, mock_analyze, mock_update, mock_context):
    """Test summarization with date range."""
    # Setup
    mock_update.message.text = "/summarize 2023-01-01 2023-01-31"
    mock_db.get_readings.return_value = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading"),
        (130, 85, 75, "2023-01-15 12:00:00", "Slightly elevated")
    ]
    mock_analyze.return_value = "Test medical advice for range"
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that get_readings was called with correct date parameters
    mock_db.get_readings.assert_called_once()
    call_args = mock_db.get_readings.call_args[0]
    assert call_args[0] == 12345  # user_id
    assert call_args[1] == date(2023, 1, 1)  # start_date
    assert call_args[2] == date(2023, 1, 31)  # end_date

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_with_regex(mock_db, mock_analyze, mock_update, mock_context):
    """Test summarization with regex pattern."""
    # Setup
    mock_update.message.text = '/summarize pattern:"elevated"'
    mock_db.get_readings.return_value = [
        (130, 85, 75, "2023-01-15 12:00:00", "Slightly elevated")
    ]
    mock_analyze.return_value = "Test medical advice for elevated readings"
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that get_readings was called with correct regex parameter
    mock_db.get_readings.assert_called_once()
    call_args = mock_db.get_readings.call_args[0]
    assert call_args[3] == "elevated"  # regex_pattern

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_no_readings(mock_db, mock_analyze, mock_update, mock_context):
    """Test response when no readings are found."""
    # Setup
    mock_update.message.text = "/summarize"
    mock_db.get_readings.return_value = []
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that analyze_readings was not called
    mock_analyze.assert_not_called()
    
    # Check appropriate message was sent
    # First message is "Please wait"
    assert mock_update.message.reply_text.call_count == 2
    second_call = mock_update.message.reply_text.call_args_list[1][0][0]
    assert "No blood pressure readings found" in second_call

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_invalid_date(mock_db, mock_analyze, mock_update, mock_context):
    """Test response with invalid date format."""
    # Setup
    mock_update.message.text = "/summarize invalid-date"
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that get_readings was not called
    mock_db.get_readings.assert_not_called()
    
    # Check that analyze_readings was not called
    mock_analyze.assert_not_called()
    
    # Check appropriate message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Invalid date format" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.summarize_handler.analyze_readings')
@patch('handlers.summarize_handler.db')
async def test_summarize_invalid_regex(mock_db, mock_analyze, mock_update, mock_context):
    """Test response with invalid regex pattern."""
    # Setup
    mock_update.message.text = '/summarize pattern:"[invalid"'
    
    # Mock the get_readings to raise an exception with invalid regex
    mock_db.get_readings.side_effect = ValueError("Invalid regex pattern: [invalid")
    
    # Execute the handler
    await summarize(mock_update, mock_context)
    
    # Check that analyze_readings was not called
    mock_analyze.assert_not_called()
    
    # The handler sends an initial "Please wait" message and then an error message
    # So we expect two calls to reply_text
    assert mock_update.message.reply_text.call_count == 2
    
    # First message should be "Please wait"
    first_call = mock_update.message.reply_text.call_args_list[0][0][0]
    assert "wait" in first_call.lower() or "analyzing" in first_call.lower()
    
    # Second message should indicate an error
    second_call = mock_update.message.reply_text.call_args_list[1][0][0]
    assert "error" in second_call.lower() or "invalid" in second_call.lower()