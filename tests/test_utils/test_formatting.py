import pytest
from datetime import datetime, date
from utils.formatting import (
    parse_command_with_args, 
    format_date,
    format_datetime,
    parse_date,
    parse_datetime,
    extract_regex_pattern
)

def test_parse_command_with_args():
    """Test parsing command with arguments."""
    # Command with arguments
    command_text = "/test arg1 arg2 arg3"
    args = parse_command_with_args(command_text, "test")
    assert args == "arg1 arg2 arg3"
    
    # Command without arguments
    command_text = "/test"
    args = parse_command_with_args(command_text, "test")
    assert args == ""
    
    # Different command
    command_text = "/other arg1 arg2"
    args = parse_command_with_args(command_text, "test")
    assert args is None

def test_format_date():
    """Test formatting a date."""
    test_date = date(2023, 1, 15)
    formatted = format_date(test_date)
    assert formatted == "2023-01-15"

def test_format_datetime():
    """Test formatting a datetime."""
    test_datetime = datetime(2023, 1, 15, 14, 30)
    formatted = format_datetime(test_datetime)
    assert formatted == "2023-01-15 14:30"

def test_parse_date():
    """Test parsing a date string."""
    # Valid date
    parsed = parse_date("2023-01-15")
    assert parsed == date(2023, 1, 15)
    
    # Invalid date
    with pytest.raises(ValueError) as excinfo:
        parse_date("invalid-date")
    assert "Invalid date format" in str(excinfo.value)

def test_parse_datetime():
    """Test parsing a datetime string."""
    # Valid datetime
    parsed = parse_datetime("2023-01-15 14:30")
    assert parsed == datetime(2023, 1, 15, 14, 30)
    
    # Invalid datetime
    with pytest.raises(ValueError) as excinfo:
        parse_datetime("invalid-datetime")
    assert "Invalid datetime format" in str(excinfo.value)

def test_extract_regex_pattern():
    """Test extracting regex pattern from text."""
    # Text with pattern
    text = '/command pattern:"test-pattern"'
    pattern, clean_text = extract_regex_pattern(text)
    assert pattern == "test-pattern"
    assert clean_text == "/command"
    
    # Text with pattern using single quotes
    text = "/command pattern:'test-pattern'"
    pattern, clean_text = extract_regex_pattern(text)
    assert pattern == "test-pattern"
    assert clean_text == "/command"
    
    # Text without pattern
    text = "/command arg1 arg2"
    pattern, clean_text = extract_regex_pattern(text)
    assert pattern is None
    assert clean_text == "/command arg1 arg2"
    
    # Pattern with special characters
    text = '/command pattern:"\\d+-\\d+"'
    pattern, clean_text = extract_regex_pattern(text)
    assert pattern == "\\d+-\\d+"
    assert clean_text == "/command"