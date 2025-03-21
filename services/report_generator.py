from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF
from reportlab.lib.utils import simpleSplit
from models.reading import Reading
from models.database import db
from services.analysis_service import analyze_readings

class ReportGenerator:
    """Service for generating PDF reports of blood pressure readings."""
    
    def __init__(self, user_id, readings, advice):
        self.user_id = user_id
        self.readings = readings
        self.advice = advice
        self.filename = f'{user_id}_blood_pressure_report.pdf'
        self.pdf_canvas = canvas.Canvas(self.filename, pagesize=letter)
        self.y_position = 750  # Start position on the first page
    
    def generate(self, start_date=None, end_date=None, regex_pattern=None):
        """Generate a PDF report of the readings."""
        # Create header
        self.y_position = self._create_pdf_header(self.pdf_canvas, self.y_position)
        
        # If no readings, display a message
        if not self.readings:
            self.pdf_canvas.setFont("Helvetica", 12)
            self.pdf_canvas.drawString(40, self.y_position, 
                                     "No blood pressure readings found matching your criteria.")
            self.pdf_canvas.save()
            return self.filename
        
        # Calculate averages
        reading_objs = [Reading.from_tuple(r) for r in self.readings]
        avg_systolic = sum(r.systolic for r in reading_objs) / len(reading_objs)
        avg_diastolic = sum(r.diastolic for r in reading_objs) / len(reading_objs)
        
        # Calculate average heart rate (excluding None values)
        heart_rates = [r.heart_rate for r in reading_objs if r.heart_rate is not None]
        avg_heart = sum(heart_rates) / len(heart_rates) if heart_rates else None
        
        # Add filter information
        self._add_filter_info(start_date, end_date, regex_pattern)
        
        # Process readings
        self._add_readings(reading_objs)
        
        # Add averages
        self.y_position = self._check_add_new_page(self.pdf_canvas, self.y_position)
        self.y_position -= 30  # Space before averages
        
        # Display averages
        avg_line = (f"Average Blood Pressure: Systolic: {round(avg_systolic, 2)}, "
                   f"Diastolic: {round(avg_diastolic, 2)}, "
                   f"Heart Rate: {round(avg_heart, 2) if avg_heart else 'N/A'}")
        self.pdf_canvas.setFont("Helvetica-Bold", 12)
        self.pdf_canvas.drawString(40, self.y_position, avg_line)
        
        # Add graph if we have enough data
        if len(reading_objs) > 1:
            graph_space_required = 250
            self.y_position = self._check_add_new_page(
                self.pdf_canvas, self.y_position, graph_space_required)
            
            self._add_blood_pressure_graph(reading_objs)
            self.y_position -= graph_space_required
        
        self.pdf_canvas.save()
        return self.filename
    
    def _create_pdf_header(self, pdf_canvas, y_position):
        """Create the PDF header with enhanced style."""
        pdf_canvas.setFont("Times-Bold", 16)
        pdf_canvas.setFillColor(colors.darkblue)
        pdf_canvas.drawString(40, y_position, "Blood Pressure Readings Report")
        pdf_canvas.setFillColor(colors.black)  # Reset color to default
        return y_position - 30
    
    def _check_add_new_page(self, pdf_canvas, y_position, margin=100):
        """Check if a new page is needed and add it if so."""
        if y_position < margin:
            pdf_canvas.showPage()
            y_position = 750
            y_position = self._create_pdf_header(pdf_canvas, y_position)
        return y_position
    
    def _add_section_header(self, text, y_position):
        """Add a section header with specific style."""
        self.pdf_canvas.setFont("Times-BoldItalic", 14)
        self.pdf_canvas.drawString(40, y_position, text)
        self.pdf_canvas.setFont("Helvetica", 12)  # Reset font for body text
        return y_position - 20
    
    def _add_reading_entry(self, line, y_position, max_width=500):
        """Add a reading entry with standard body text style, wrapping long lines."""
        self.pdf_canvas.setFont("Helvetica", 12)

        # Split the line into wrapped lines that fit within the max width
        wrapped_lines = simpleSplit(line, "Helvetica", 12, max_width)

        for wrapped_line in wrapped_lines:
            self.pdf_canvas.drawString(40, y_position, wrapped_line)
            y_position -= 15  # Move to the next line
        return y_position
    
    def _add_filter_info(self, start_date, end_date, regex_pattern):
        """Add filter information to the report."""
        filter_info = []
        if start_date and end_date and start_date == end_date:
            filter_info.append(f"Date: {start_date.strftime('%Y-%m-%d')}")
        elif start_date and end_date:
            filter_info.append(
                f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        if regex_pattern:
            filter_info.append(f"Description Filter: Pattern \"{regex_pattern}\"")
        
        if filter_info:
            self.y_position = self._add_section_header("Report Filters:", self.y_position)
            for info in filter_info:
                self.y_position = self._add_reading_entry(info, self.y_position)
            self.y_position -= 20  # Add some space after filters
    
    def _add_readings(self, readings):
        """Add readings to the report, grouped by date."""
        current_date = None
        for reading in readings:
            self.y_position = self._check_add_new_page(self.pdf_canvas, self.y_position)
            
            reading_date = reading.reading_datetime.date()
            if reading_date != current_date:
                if current_date is not None:
                    # Add a visual spacer
                    self.pdf_canvas.setStrokeColor(colors.lightgrey)
                    self.y_position -= 5
                    self.pdf_canvas.line(40, self.y_position, 560, self.y_position)
                    self.y_position -= 12
                    self.y_position = self._check_add_new_page(self.pdf_canvas, self.y_position)
                
                self.y_position = self._add_section_header(
                    reading_date.strftime('%A, %B %d, %Y'), self.y_position)
                current_date = reading_date
            
            self.y_position = self._add_reading_entry(str(reading), self.y_position)

    def _add_ai_recommendations(self):
        """Add AI medical recommendations to the report."""
        self.y_position = self._check_add_new_page(self.pdf_canvas, self.y_position, margin=150)
        self.y_position = self._add_section_header("AI Medical Recommendations:", self.y_position)

        # Display the advice generated earlier
        if self.advice:
            max_width = 500  # Maximum width for the text
            font_size = 12
            self.pdf_canvas.setFont("Helvetica", font_size)

            # Split the advice into lines that fit within the max width
            wrapped_lines = simpleSplit(self.advice, "Helvetica", font_size, max_width)

            for line in wrapped_lines:
                self.y_position = self._add_reading_entry(line, self.y_position)
                self.y_position = self._check_add_new_page(self.pdf_canvas, self.y_position)
        else:
            self.y_position = self._add_reading_entry("No specific recommendations available.", self.y_position)
    
    def _add_blood_pressure_graph(self, readings):
        """Add a blood pressure graph to the report."""
        # Prepare data for the plot
        data = []
        dates = []
        
        for reading in readings:
            reading_date = reading.reading_datetime
            dates.append(reading_date.strftime("%d-%b"))  # Format date as 'DD-MMM'
            
            # Convert readings into a (position, value) format
            data.append((len(dates) - 1, reading.systolic))  # Systolic
            data.append((len(dates) - 1, reading.diastolic))  # Diastolic
        
        # Drawing setup
        drawing = Drawing(400, 200)
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.width = 300
        lp.height = 100
        lp.data = [data[::2], data[1::2]]  # Separate systolic and diastolic data
        lp.lines[0].strokeColor = colors.red
        lp.lines[1].strokeColor = colors.blue
        
        skip_every = 1
        if len(dates) > 30:
            skip_every = len(dates) // 10
        
        # X-axis configuration
        lp.xValueAxis.valueSteps = list(range(len(dates)))
        lp.xValueAxis.labels.boxAnchor = 'n'
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 8
        lp.xValueAxis.labels.dx = -5
        lp.xValueAxis.labels.dy = -20
        lp.xValueAxis.labelTextFormat = lambda x: dates[int(x)] if int(x) % skip_every == 0 else ''
        
        # Add the plot to the drawing
        drawing.add(lp)
        
        # Render the drawing onto the PDF canvas
        renderPDF.draw(drawing, self.pdf_canvas, 100, self.y_position - 250)
        
        # Manually add Y-axis title
        self.pdf_canvas.saveState()
        self.pdf_canvas.setFont("Helvetica", 10)
        self.pdf_canvas.rotate(90)
        self.pdf_canvas.drawString(self.y_position - 200, -120, "Pressure (mm Hg)")
        self.pdf_canvas.restoreState()
        
        # Manually add X-axis title
        self.pdf_canvas.setFont("Helvetica", 10)
        self.pdf_canvas.drawString(300, self.y_position - 240, "Time")

         # Add AI medical recommendations
        self.y_position -= 270  # Adjust position for recommendations
        self._add_ai_recommendations()

def generate_pdf(user_id, db_path='blood_pressure.db', start_date=None, end_date=None, regex_pattern=None):
    """
    Generate a PDF report of blood pressure readings.
    This function is kept for backward compatibility.
    """
    # Get readings from the database
    readings = db.get_readings(user_id, start_date, end_date, regex_pattern)
    advice = analyze_readings(readings, user_id, start_date, end_date, regex_pattern)
    # Generate the report
    report_generator = ReportGenerator(user_id, readings, advice)
    return report_generator.generate(start_date, end_date, regex_pattern)