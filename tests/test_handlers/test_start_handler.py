import pytest
from unittest.mock import AsyncMock, patch
from handlers.start_handler import start
from telegram import ForceReply

@pytest.mark.asyncio
async def test_start_handler(mock_update, mock_context):
    """Test that start handler sends the welcome message."""
    # Execute the handler
    await start(mock_update, mock_context)
    
    # Check that the message was sent with correct content
    mock_update.message.reply_markdown_v2.assert_called_once()
    
    # Verify that the message contains welcome text
    call_args = mock_update.message.reply_markdown_v2.call_args[0][0]
    assert "Welcome to the Blood Pressure Log Bot" in call_args
    
    # Verify that ForceReply was used
    call_kwargs = mock_update.message.reply_markdown_v2.call_args[1]
    assert isinstance(call_kwargs.get('reply_markup'), ForceReply)