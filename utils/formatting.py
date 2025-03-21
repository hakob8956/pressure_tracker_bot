import re
from datetime import datetime

def parse_command_with_args(text, command):
    """Parse a command with its arguments."""
    pattern = fr'^/{command}\s*(.*)$'
    match = re.match(pattern, text)
    if not match:
        return None
    return match.group(1).strip()

def format_date(date):
    """Format a date for display."""
    return date.strftime("%Y-%m-%d")

def format_datetime(dt):
    """Format a datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")

def parse_date(date_str):
    """Parse a date string to a date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Please use YYYY-MM-DD.")

def parse_datetime(datetime_str):
    """Parse a datetime string to a datetime object."""
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Please use YYYY-MM-DD HH:MM.")

def extract_regex_pattern(text):
    """Extract a regex pattern from text."""
    pattern_match = re.search(r'pattern:(["\'])(.*?)\1', text)
    if pattern_match:
        return pattern_match.group(2), text.replace(pattern_match.group(0), "").strip()
    return None, text