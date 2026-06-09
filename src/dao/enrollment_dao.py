# Filename: enrollment_dao.py
#
# Description: The class operates on the enrollment table in the database. It
# implements the abstract subroutines from its parent and also allows for searching
# for a student's schedule.
#
# Parent: BaseDAO

import sqlite3
from typing import Optional, Sequence

from dao.base_dao import BaseDAO
from models.enrollment import Enrollment

class EnrollmentDAO(BaseDAO[Enrollment]):
    @property
    def table(self) -> str:
        return "enrollment"

    @property
    def pk(self) -> str:
        return "enrollment_id"

    @property
    def columns(self) -> Sequence[str]:
        return ("student_id", "course_id")

    def to_values(self, record: Enrollment):
        return (record.student_id, record.course_id)

    def from_row(self, row: sqlite3.Row) -> Enrollment:
        return Enrollment(
            student_id=row["student_id"],
            course_id=row["course_id"],
            enrollment_id=row["enrollment_id"],
        )

    def get_id(self, record: Enrollment) -> Optional[int]:
        return record.enrollment_id

    def set_id(self, record: Enrollment, record_id: int) -> None:
        record.enrollment_id = record_id

    # Search by student ID. Returns all enrolled classes.
    def find_by_student(self, student_id: int) -> list[Enrollment]:
        sql = "SELECT * FROM enrollment WHERE student_id = ?"
        rows = self._conn.execute(sql, (student_id,)).fetchall()
        return [self.from_row(row) for row in rows]

    # Search for a student's enrollment in a course by student id and course id.
    # Returns the row or None.
    def find_active(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        sql = "SELECT * FROM enrollment WHERE student_id = ? AND course_id = ?"
        row = self._conn.execute(sql, (student_id, course_id)).fetchone()
        return self.from_row(row) if row is not None else None