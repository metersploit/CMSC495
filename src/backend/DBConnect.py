# TODO:
#   - Retrieve students
#   - Retrieve courses
#   - Retrieve enrollment
#   - Custom query

import sqlite3
from typing import Self

class DBConnect:
    # Class constructor
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    # Create connection to db
    def __establish_conn__(self) -> Self:
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self
    
    # Commit db changes and close connection
    def __teardown_conn__(self, exec_type) -> None:
        if self.connection:
            # Save changes if there are no SQL errors
            if exec_type is None:
                self.connection.commit()
            # roll back changes if there is an error
            else:
                self.connection.rollback()

            self.cursor.close()
            self.connection.close()

    def insert_students(self, first_name: str, last_name: str, email: str,
                        phone_number: str, password_hash: str) -> None:
        query = """INSERT INTO students (first_name, last_name, email,
            phone_mumber, password_hash) VALUES (?, ?, ?, ?, ?)"""
        
        self.cursor.execute(query, (first_name, last_name, email, phone_number,
                                    password_hash))

    def insert_courses(self, course_name: str, course_number: str,
                       instructor: str, capacity: int, num_enrolled: int = 0
                       ) -> None:
        query = """INSERT INTO courses (course_name, course_number, instructor,
            capacity, num_enrolled) VALUES (?, ?, ?, ?, ?)"""
        
        self.cursor.execute(query, (course_name, course_number, instructor,
                                    capacity, num_enrolled))
        
    def insert_enrollment(self, student_id: int, course_id: int) -> None:
        query = """INSERT INTO enrollment (student_id, course_id) VALUES (?, ?)"""

        self.cursor.execute(query, (student_id, course_id))