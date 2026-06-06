import sqlite3

def build_db() -> None:
    with sqlite3.connect("../../db/registration_app.db") as connect:
        
        cursor = connect.cursor()
        connect.execute("PRAGMA foreign_keys = ON;")

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
                num_enrolled INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollment (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER REFERENCES students(student_id),
                course_id INTEGER REFERENCES courses(course_id)
            )
        """)

        cursor.execute(";")
    connect.close()

if __name__ == "__main__":
    build_db()