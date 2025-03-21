import sqlite3
from datetime import datetime
import re
from config import DB_PATH

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS blood_pressure_readings (
                           id INTEGER PRIMARY KEY,
                           user_id INTEGER NOT NULL,
                           systolic INTEGER NOT NULL,
                           diastolic INTEGER NOT NULL,
                           heart_rate INTEGER NULL,
                           reading_datetime DATETIME NOT NULL,
                           description TEXT NULL)''')
    
    def add_reading(self, user_id, systolic, diastolic, heart_rate=None, 
                   reading_datetime=None, description=None):
        """Add a new blood pressure reading to the database."""
        if not reading_datetime:
            reading_datetime = datetime.now().replace(second=0, microsecond=0)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO blood_pressure_readings 
                           (user_id, systolic, diastolic, heart_rate, reading_datetime, description) 
                           VALUES (?, ?, ?, ?, ?, ?)''', 
                           (user_id, systolic, diastolic, heart_rate, reading_datetime, description))
            return cursor.lastrowid
    
    def get_readings(self, user_id, start_date=None, end_date=None, regex_pattern=None):
        """Get blood pressure readings with optional date range and regex filtering."""
        query, params = self._prepare_query(user_id, start_date, end_date)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            readings = cursor.fetchall()
            
            # Apply regex filtering if pattern provided
            if regex_pattern and readings:
                try:
                    pattern = re.compile(regex_pattern, re.IGNORECASE)
                    # Filter readings where description matches the pattern
                    # Index 4 is the description field in the readings tuple
                    filtered_readings = [r for r in readings if r[4] and pattern.search(r[4])]
                    readings = filtered_readings
                except re.error:
                    # Re-raise with more informative message
                    raise ValueError(f"Invalid regex pattern: {regex_pattern}")
            
            return readings
    
    def remove_last_reading(self, user_id):
        """Remove the last reading for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT id FROM blood_pressure_readings 
                           WHERE user_id = ? ORDER BY reading_datetime DESC LIMIT 1''', 
                           (user_id,))
            last_reading = cursor.fetchone()
            
            if last_reading:
                cursor.execute('DELETE FROM blood_pressure_readings WHERE id = ?', 
                             (last_reading[0],))
                return True
            return False
    
    def remove_readings_by_date(self, user_id, target_date):
        """Remove readings for a specific date."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM blood_pressure_readings 
                           WHERE user_id = ? AND DATE(reading_datetime) = ?''', 
                           (user_id, target_date.strftime("%Y-%m-%d")))
            return cursor.rowcount > 0
    
    def remove_all_readings(self, user_id):
        """Remove all readings for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM blood_pressure_readings WHERE user_id = ?', 
                         (user_id,))
            return cursor.rowcount > 0
    
    def _prepare_query(self, user_id, start_date=None, end_date=None):
        """Prepare the SQL query and parameters based on date filters."""
        query = '''SELECT systolic, diastolic, heart_rate, reading_datetime, description 
                  FROM blood_pressure_readings WHERE user_id = ?'''
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

# Initialize database instance
db = Database()

def init_db(db_path=DB_PATH):
    """Initialize the database. This function is kept for backward compatibility."""
    global db
    db = Database(db_path)
    return db