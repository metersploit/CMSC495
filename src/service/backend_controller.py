# Filename: backend_controller.py
#
# Description: This script provides a class that creates the primary dataflow
# pipeline between the front and back end. Data from the validator is handed 
# to this class for pushing to the database. This is also where main functionalities
# live such as account creation, authentication, enrollment, dropping, searching,
# and schedule creation. Additionally, there are two standalone subroutines that
# handle password hashing (SHA256 + 16-byte salting) and password checking.
#
# Parent: none

import hashlib
import hmac
import os
from typing import Optional

from db.database_connection import DatabaseConnection
from dao.student_dao import StudentDAO
from dao.course_dao import CourseDAO
from dao.enrollment_dao import EnrollmentDAO
from models.student import Student
from models.course import Course
from models.enrollment import Enrollment

class RegistrationError(Exception):
    """Raised when an operation fails (course full, already enrolled,
    bad credentials, etc.). The middleware/UI catches this and shows the message
    to the user."""

# Standalone password hashing function.
def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"{salt.hex()}${digest.hex()}"

# Standalone password matching for login functionality
def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(),
                                 bytes.fromhex(salt_hex), 100_000)
    return hmac.compare_digest(digest.hex(), hash_hex)


class BackendController:

    def __init__(self, db: Optional[DatabaseConnection] = None) -> None:
        self._db = db or DatabaseConnection.get_instance()
        self._students = StudentDAO(self._db)
        self._courses = CourseDAO(self._db)
        self._enrollments = EnrollmentDAO(self._db)

    @property
    def _conn(self):
        return self._db.get_connection()

    # Account creation. Returns a Student object.
    def create_account(self, first_name: str, last_name: str, email: str,
                       phone_number: Optional[str], password: str) -> Student:
        if self._students.find_by_email(email) is not None:
            raise RegistrationError("An account with that email already exists.")
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=_hash_password(password),
            phone_number=phone_number,
        )
        with self._conn:
            self._students.insert_row(student)
        return student

    # Account authentication. Returns a Student object if successful.
    def authenticate(self, email: str, password: str) -> Student:
        student = self._students.find_by_email(email)
        if student is None or not _verify_password(password, student.password_hash):
            raise RegistrationError("Invalid email or password.")
        return student

    # Course searching. Returns a list of Course objects.
    def search_courses(self, term: str) -> list[Course]:
        return self._courses.search(term)

    # Enroll in a course. Updates the enrollments table if successful or return
    # an error string if it isnt.
    def enroll(self, student_id: int, course_id: int) -> None:
        course = self._courses.find_row(course_id)
        if course is None:
            raise RegistrationError("Course not found.")
        if not course.has_available_seats:
            raise RegistrationError("That course is full.")
        if self._enrollments.find_active(student_id, course_id) is not None:
            raise RegistrationError("You are already enrolled in that course.")

        course.num_enrolled += 1
        with self._conn:                   
            self._enrollments.insert_row(
                Enrollment(student_id=student_id, course_id=course_id)
            )
            self._courses.update_row(course)

    # Drop a course. Updates the appropriate enrollment row.
    def drop(self, student_id: int, course_id: int) -> None:
        enrollment = self._enrollments.find_active(student_id, course_id)
        if enrollment is None:
            raise RegistrationError("You are not enrolled in that course.")
        course = self._courses.find_row(course_id)

        with self._conn:
            self._enrollments.delete_row(enrollment.enrollment_id)
            if course is not None and course.num_enrolled > 0:
                course.num_enrolled -= 1
                self._courses.update_row(course)

    # Get a student's schedule. Returns a list of Courses.
    def get_schedule(self, student_id: int) -> list[Course]:
        enrollments = self._enrollments.find_by_student(student_id)
        schedule = []
        for enrollment in enrollments:
            course = self._courses.find_row(enrollment.course_id)
            if course is not None:
                schedule.append(course)
        return schedule