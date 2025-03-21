import pytest
from unittest.mock import AsyncMock
from handlers.help_handler import help_command

@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test that help command sends the help message."""
    # Execute the handler
    await help_command(mock_update, mock_context)
    
    # Check that the message was sent
    mock_update.message.reply_text.assert_called_once()
    
    # Verify that the message contains key help information
    help_message = mock_update.message.reply_text.call_args[0][0]
    assert "/start" in help_message
    assert "/log" in help_message
    assert "/report" in help_message
    assert "/removelast" in help_message
    assert "/removebydate" in help_message
    assert "/removeall" in help_message
    assert "/summarize" in help_message
    assert "/help" in help_message