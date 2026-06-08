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

    def find_by_student(self, student_id: int) -> list[Enrollment]:
        """All enrollments for a student (used to build the schedule)."""
        sql = "SELECT * FROM enrollment WHERE student_id = ?"
        rows = self._conn.execute(sql, (student_id,)).fetchall()
        return [self.from_row(row) for row in rows]

    def find_active(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        """Find a student's enrollment in a course (used when dropping)."""
        sql = "SELECT * FROM enrollment WHERE student_id = ? AND course_id = ?"
        row = self._conn.execute(sql, (student_id, course_id)).fetchone()
        return self.from_row(row) if row is not None else None