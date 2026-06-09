# Filename: build_db.py
#
# Description: This script initializes a SQLite database in this directory and is 
# part of the development environment setup. Three tables will be created 
# which are students, courses, and enrollments. No data is added to the tables.
#
# Parent: none

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "registration_app.db"

def build_db() -> None:
    with sqlite3.connect(DB_PATH) as connect:
        connect.execute("PRAGMA foreign_keys = ON;")
        cursor = connect.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                password_hash TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                course_number TEXT NOT NULL,
                instructor TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                num_enrolled INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollment (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(student_id),
                course_id INTEGER NOT NULL REFERENCES courses(course_id),
                UNIQUE (student_id, course_id)
            )
        """)

        connect.commit()

if __name__ == "__main__":
    build_db()
    print(f"Database built at {DB_PATH}")