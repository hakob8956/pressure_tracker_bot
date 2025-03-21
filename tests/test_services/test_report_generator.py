import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
from datetime import date
from services.report_generator import ReportGenerator, generate_pdf

@patch('services.report_generator.canvas.Canvas')
def test_report_generator_init(mock_canvas):
    """Test initialization of ReportGenerator."""
    # Mock readings
    readings = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading")
    ]
    
    # Initialize ReportGenerator
    generator = ReportGenerator(12345, readings)
    
    # Check that canvas was created
    mock_canvas.assert_called_once()
    
    # Check that filename is correct
    assert generator.filename == '12345_blood_pressure_report.pdf'

@patch('services.report_generator.canvas.Canvas')
def test_report_generator_empty_readings(mock_canvas):
    """Test generation of report with no readings."""
    # Mock canvas and PDF methods
    mock_pdf = MagicMock()
    mock_canvas.return_value = mock_pdf
    
    # Initialize with empty readings
    generator = ReportGenerator(12345, [])
    
    # Generate report
    filename = generator.generate()
    
    # Check that appropriate message was added
    mock_pdf.drawString.assert_called_with(40, 720, "No blood pressure readings found matching your criteria.")
    
    # Check that PDF was saved
    mock_pdf.save.assert_called_once()
    
    # Check that filename was returned
    assert filename == '12345_blood_pressure_report.pdf'

@patch('services.report_generator.canvas.Canvas')
def test_report_generator_with_readings(mock_canvas):
    """Test generation of report with readings."""
    # Mock canvas and PDF methods
    mock_pdf = MagicMock()
    mock_canvas.return_value = mock_pdf
    
    # Mock readings
    readings = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading"),
        (130, 85, 75, "2023-01-02 12:00:00", "Elevated reading")
    ]
    
    # Initialize with readings
    generator = ReportGenerator(12345, readings)
    
    # Generate report
    filename = generator.generate()
    
    # Check that PDF was saved
    mock_pdf.save.assert_called_once()
    
    # Check that font was set multiple times for different elements
    assert mock_pdf.setFont.call_count > 1
    
    # Check that filename was returned
    assert filename == '12345_blood_pressure_report.pdf'

@patch('services.report_generator.canvas.Canvas')
def test_report_generator_with_filters(mock_canvas):
    """Test generation of report with date filters."""
    # Mock canvas and PDF methods
    mock_pdf = MagicMock()
    mock_canvas.return_value = mock_pdf
    
    # Mock readings
    readings = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading")
    ]
    
    # Initialize with readings
    generator = ReportGenerator(12345, readings)
    
    # Generate report with filters
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    regex_pattern = "Normal"
    filename = generator.generate(start_date, end_date, regex_pattern)
    
    # Check that PDF was saved
    mock_pdf.save.assert_called_once()
    
    # Check that filename was returned
    assert filename == '12345_blood_pressure_report.pdf'

@patch('services.report_generator.ReportGenerator')
@patch('services.report_generator.db')
def test_generate_pdf_function(mock_db, mock_generator):
    """Test the generate_pdf wrapper function."""
    # Setup mock database and generator
    mock_db.get_readings.return_value = [
        (120, 80, 70, "2023-01-01 12:00:00", "Normal reading")
    ]
    mock_instance = MagicMock()
    mock_generator.return_value = mock_instance
    mock_instance.generate.return_value = "test_report.pdf"
    
    # Call generate_pdf
    user_id = 12345
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    regex_pattern = "Normal"
    filename = generate_pdf(user_id, start_date=start_date, end_date=end_date, regex_pattern=regex_pattern)
    
    # Check that database was queried
    mock_db.get_readings.assert_called_once_with(user_id, start_date, end_date, regex_pattern)
    
    # Check that generator was created with correct arguments
    mock_generator.assert_called_once()
    call_args = mock_generator.call_args[0]
    assert call_args[0] == user_id
    
    # Check that generate was called with filters
    mock_instance.generate.assert_called_once_with(start_date, end_date, regex_pattern)
    
    # Check that filename was returned
    assert filename == "test_report.pdf"