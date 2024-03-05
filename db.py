import sqlite3

# Initialize SQLite Database


def init_db(db_path='blood_pressure.db'):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS blood_pressure_readings (
                     id INTEGER PRIMARY KEY,
                     user_id INTEGER NOT NULL,
                     systolic INTEGER NOT NULL,
                     diastolic INTEGER NOT NULL,
                     heart_rate INTEGER NULL,
                     reading_datetime DATETIME NOT NULL)''')
