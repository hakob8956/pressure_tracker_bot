import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import String


def create_pdf_header(pdf_canvas, y_position):
    """Function to create the PDF header with enhanced style."""
    pdf_canvas.setFont("Times-Bold", 16)
    pdf_canvas.setFillColor(colors.darkblue)
    pdf_canvas.drawString(40, y_position, "Blood Pressure Readings Report")
    pdf_canvas.setFillColor(colors.black)  # Reset color to default
    return y_position - 30  # Adjust y_position after the header


def check_add_new_page(pdf_canvas, y_position, margin=100):
    """Check if a new page is needed and add it if so."""
    if y_position < margin:  # Consider a margin for adding new page
        pdf_canvas.showPage()
        y_position = 750
        y_position = create_pdf_header(pdf_canvas, y_position)
    return y_position


def add_section_header(pdf_canvas, text, y_position):
    """Adds section headers with a specific style."""
    pdf_canvas.setFont("Times-BoldItalic", 14)
    pdf_canvas.drawString(40, y_position, text)
    pdf_canvas.setFont("Helvetica", 12)  # Reset font for body text
    return y_position - 20


def add_reading_entry(pdf_canvas, line, y_position):
    """Adds a reading entry with standard body text style."""
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(40, y_position, line)
    return y_position - 15


def add_blood_pressure_graph(pdf_canvas, readings, y_position):
    """
    Adds a blood pressure graph at the specified position in the PDF.

    :param pdf_canvas: The canvas of the PDF document.
    :param readings: A list of tuples containing the readings. 
                     Each tuple should have the form (systolic, diastolic, heart_rate, reading_datetime).
    :param y_position: The Y position where the graph should start.
    """
    # Prepare data for the plot
    data = []
    dates = []
    for reading in readings:
        reading_date = datetime.strptime(reading[3], "%Y-%m-%d %H:%M:%S")
        dates.append(reading_date.strftime("%d-%b"))  # Format date as 'DD-MMM'
        # Convert readings into a (position, value) format
        data.append((len(dates) - 1, reading[0]))  # Systolic
        data.append((len(dates) - 1, reading[1]))  # Diastolic

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
    lp.xValueAxis.labelTextFormat = lambda x: dates[int(
        x)] if int(x) % skip_every == 0 else ''

    # Y-axis configuration
    # lp.yValueAxis.title = 'Pressure (mm Hg)'
    y_axis_title = String(20, y_position - 75,

                          'Pressure (mm Hg)', fontSize=10, textAnchor='middle')
    drawing.add(y_axis_title)
    # lp.yValueAxis.titleFontSize = 10
    # lp.yValueAxis.labels.fontSize = 8

    drawing.add(lp)

    # Adjust y_position based on the content above the graph
    renderPDF.draw(drawing, pdf_canvas, 100,
                   y_position - 200)  # Position the graph


def generate_pdf(user_id, db_path='blood_pressure.db', start_date=None, end_date=None):
    filename = f'{user_id}_blood_pressure_report.pdf'
    pdf_canvas = canvas.Canvas(filename, pagesize=letter)
    y_position = 750  # Start position on the first page

    # Initialize the first page with a styled header
    y_position = create_pdf_header(pdf_canvas, y_position)

    # Prepare database query
    query, params = prepare_query(user_id, start_date, end_date)

    # Connect to the database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        readings = cursor.fetchall()

        # Calculate averages
        avg_query = '''SELECT AVG(systolic) AS avg_systolic, AVG(diastolic) AS avg_diastolic, AVG(heart_rate) AS avg_heart FROM blood_pressure_readings WHERE user_id = ?'''
        if start_date and end_date:
            avg_query += " AND DATE(reading_datetime) BETWEEN ? AND ?"
        elif start_date:
            avg_query += " AND DATE(reading_datetime) = ?"
        cursor.execute(avg_query, params)
        avg_systolic, avg_diastolic, avg_heart = cursor.fetchone()

    current_date = None
    for systolic, diastolic, heart_rate, reading_datetime in readings:
        y_position = check_add_new_page(pdf_canvas, y_position)

        reading_date = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").date()
        if reading_date != current_date:
            if current_date is not None:
                # Add a visual spacer or line if you prefer
                pdf_canvas.setStrokeColor(colors.lightgrey)
                y_position -= 5
                pdf_canvas.line(40, y_position, 560, y_position)  # Draw a line
                y_position -= 12
                y_position = check_add_new_page(pdf_canvas, y_position)

            y_position = add_section_header(
                pdf_canvas, reading_date.strftime('%A, %B %d, %Y'), y_position)
            current_date = reading_date

        time_str = datetime.strptime(
            reading_datetime, "%Y-%m-%d %H:%M:%S").strftime('%H:%M')
        heart_str = f", Heart Rate: {heart_rate}" if heart_rate else ""
        line = f"{time_str} - Systolic: {systolic}, Diastolic: {diastolic}{heart_str}"
        y_position = add_reading_entry(pdf_canvas, line, y_position)

    # Ensure space for averages
    y_position = check_add_new_page(pdf_canvas, y_position)
    y_position -= 30  # Space before averages

    # Display styled averages
    avg_line = f"Average Blood Pressure: Systolic: {round(avg_systolic, 2)}, Diastolic: {round(avg_diastolic, 2)}, Heart Rate: {round(avg_heart, 2) if avg_heart else 'N/A'}"
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(40, y_position, avg_line)

    graph_space_required = 250
    y_position = check_add_new_page(
        pdf_canvas, y_position, graph_space_required)

    add_blood_pressure_graph(pdf_canvas, readings, y_position)
    y_position -= graph_space_required

    pdf_canvas.save()
    return filename


def prepare_query(user_id, start_date, end_date):
    """Prepare the database query and parameters."""
    query = '''SELECT systolic, diastolic, heart_rate, reading_datetime FROM blood_pressure_readings WHERE user_id = ?'''
    params = [user_id]
    if start_date and end_date:
        query += " AND DATE(reading_datetime) BETWEEN ? AND ?"
        params.extend([start_date.strftime("%Y-%m-%d"),
                      end_date.strftime("%Y-%m-%d")])
    elif start_date:
        query += " AND DATE(reading_datetime) = ?"
        params.append(start_date.strftime("%Y-%m-%d"))
    query += " ORDER BY reading_datetime"
    return query, params
