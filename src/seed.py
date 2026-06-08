"""Populate the database with sample courses and a test student.

Run once, after building the database:
    python3 db/build_db.py
    python3 seed.py

it skips data that already exists.
"""
import sqlite3

from db.database_connection import DatabaseConnection
from service.backend_controller import BackendController, RegistrationError
from dao.course_dao import CourseDAO
from models.course import Course

SAMPLE_COURSES = [
    Course(course_name="Introduction to Programming", course_number="CMSC 115",
           instructor="Dr. Alan Turing", capacity=30),
    Course(course_name="Data Structures", course_number="CMSC 215",
           instructor="Dr. Ada Lovelace", capacity=25),
    Course(course_name="Software Engineering", course_number="CMSC 495",
           instructor="Prof. Grace Hopper", capacity=20),
    Course(course_name="Database Systems", course_number="CMSC 461",
           instructor="Dr. Edgar Codd", capacity=1),   # small, to test the "full" path
    Course(course_name="Computer Networks", course_number="CMSC 451",
           instructor="Dr. Vint Cerf", capacity=40),
]

TEST_STUDENT = {
    "first_name": "Test",
    "last_name": "Student",
    "email": "test@umgc.edu",
    "phone_number": "555-0100",
    "password": "password123",
}


def seed() -> None:
    db = DatabaseConnection()
    try:
        conn = db.get_connection()
        controller = BackendController(db)
        course_dao = CourseDAO(db)

        # creates courses if the table is empty
        try:
            existing = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        except sqlite3.OperationalError:
            print("Tables not found. Run `python db/build_db.py` first.")
            return

        if existing:
            print(f"Courses already present ({existing}); skipping course seed.")
        else:
            with conn:
                for course in SAMPLE_COURSES:
                    course_dao.insert_row(course)
            print(f"Inserted {len(SAMPLE_COURSES)} courses.")

        # Creates a student if the email isnt already taken
        try:
            controller.create_account(**TEST_STUDENT)
            print(f"Created test student {TEST_STUDENT['email']} "
                  f"(password: {TEST_STUDENT['password']})")
        except RegistrationError:
            print(f"Test student {TEST_STUDENT['email']} already exists; skipping.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed complete.")