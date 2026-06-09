# Filename: student_dao.py
#
# Description: The class operates on the students table in the database. It
# implements the abstract subroutines from its parent and allows for searching
# for a student by email address.
#
# Parent: BaseDAO

import sqlite3
from typing import Optional, Sequence

from dao.base_dao import BaseDAO
from models.student import Student

class StudentDAO(BaseDAO[Student]):

    @property
    def table(self) -> str:
        return "students"

    @property
    def pk(self) -> str:
        return "student_id"

    @property
    def columns(self) -> Sequence[str]:
        return ("first_name", "last_name", "email", "phone_number", "password_hash")

    def to_values(self, record: Student):
        return (record.first_name, record.last_name, record.email,
                record.phone_number, record.password_hash)

    def from_row(self, row: sqlite3.Row) -> Student:
        return Student(
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            phone_number=row["phone_number"],
            student_id=row["student_id"],
        )

    def get_id(self, record: Student) -> Optional[int]:
        return record.student_id

    def set_id(self, record: Student, record_id: int) -> None:
        record.student_id = record_id

    # Search for a student by email address. Intended for login functionality.
    def find_by_email(self, email: str) -> Optional[Student]:
        sql = "SELECT * FROM students WHERE email = ?"
        row = self._conn.execute(sql, (email,)).fetchone()
        return self.from_row(row) if row is not None else None

    