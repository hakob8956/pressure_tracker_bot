import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
from handlers.report_handler import report
from datetime import date

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
@patch('builtins.open', new_callable=mock_open, read_data=b'test pdf content')
@patch('os.path.exists', return_value=True)
@patch('os.remove')
async def test_report_handler_basic(mock_remove, mock_exists, mock_file, mock_generate_pdf, 
                                  mock_update, mock_context):
    """Test basic report generation without filters."""
    # Setup
    mock_update.message.text = "/report"
    mock_generate_pdf.return_value = "test_report.pdf"
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was called with correct parameters
    mock_generate_pdf.assert_called_once_with(
        12345, start_date=None, end_date=None, regex_pattern=None
    )
    
    # Check that the file was opened and sent
    mock_file.assert_called_once_with("test_report.pdf", 'rb')
    mock_update.message.reply_document.assert_called_once()
    
    # Check that the file was removed after sending
    mock_remove.assert_called_once_with("test_report.pdf")

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
@patch('builtins.open', new_callable=mock_open, read_data=b'test pdf content')
@patch('os.path.exists', return_value=True)
@patch('os.remove')
async def test_report_handler_with_date(mock_remove, mock_exists, mock_file, mock_generate_pdf, 
                                     mock_update, mock_context):
    """Test report generation with specific date."""
    # Setup
    mock_update.message.text = "/report 2023-01-01"
    mock_generate_pdf.return_value = "test_report.pdf"
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was called with correct date parameters
    mock_generate_pdf.assert_called_once()
    call_args = mock_generate_pdf.call_args[1]
    assert call_args['start_date'] == date(2023, 1, 1)
    assert call_args['end_date'] == date(2023, 1, 1)
    
    # Check that the file was sent and removed
    mock_update.message.reply_document.assert_called_once()
    mock_remove.assert_called_once()

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
@patch('builtins.open', new_callable=mock_open, read_data=b'test pdf content')
@patch('os.path.exists', return_value=True)
@patch('os.remove')
async def test_report_handler_with_date_range(mock_remove, mock_exists, mock_file, mock_generate_pdf, 
                                           mock_update, mock_context):
    """Test report generation with date range."""
    # Setup
    mock_update.message.text = "/report 2023-01-01 2023-01-31"
    mock_generate_pdf.return_value = "test_report.pdf"
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was called with correct date parameters
    mock_generate_pdf.assert_called_once()
    call_args = mock_generate_pdf.call_args[1]
    assert call_args['start_date'] == date(2023, 1, 1)
    assert call_args['end_date'] == date(2023, 1, 31)

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
@patch('builtins.open', new_callable=mock_open, read_data=b'test pdf content')
@patch('os.path.exists', return_value=True)
@patch('os.remove')
async def test_report_handler_with_regex(mock_remove, mock_exists, mock_file, mock_generate_pdf, 
                                      mock_update, mock_context):
    """Test report generation with regex pattern."""
    # Setup
    mock_update.message.text = '/report pattern:"exercise"'
    mock_generate_pdf.return_value = "test_report.pdf"
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was called with correct regex parameter
    mock_generate_pdf.assert_called_once()
    call_args = mock_generate_pdf.call_args[1]
    assert call_args['regex_pattern'] == "exercise"

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
async def test_report_handler_invalid_date(mock_generate_pdf, mock_update, mock_context):
    """Test report generation with invalid date format."""
    # Setup
    mock_update.message.text = "/report invalid-date"
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was not called
    mock_generate_pdf.assert_not_called()
    
    # Check that error message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Invalid date format" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
async def test_report_handler_invalid_regex(mock_generate_pdf, mock_update, mock_context):
    """Test report generation with invalid regex pattern."""
    # Setup
    mock_update.message.text = '/report pattern:"[invalid"'
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check that generate_pdf was not called
    mock_generate_pdf.assert_not_called()
    
    # Check that error message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "Invalid regex pattern" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('handlers.report_handler.generate_pdf')
async def test_report_handler_pdf_error(mock_generate_pdf, mock_update, mock_context):
    """Test handling of errors during PDF generation."""
    # Setup
    mock_update.message.text = "/report"
    mock_generate_pdf.side_effect = Exception("Test error")
    
    # Execute the handler
    await report(mock_update, mock_context)
    
    # Check error message was sent
    mock_update.message.reply_text.assert_called_once()
    assert "An error occurred" in mock_update.message.reply_text.call_args[0][0]