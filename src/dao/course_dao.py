import sqlite3
from typing import Optional, Sequence

from dao.base_dao import BaseDAO
from models.course import Course

class CourseDAO(BaseDAO[Course]):
    @property
    def table(self) -> str:
        return "courses"

    @property
    def pk(self) -> str:
        return "course_id"

    @property
    def columns(self) -> Sequence[str]:
        return ("course_name", "course_number", "instructor",
                "capacity", "num_enrolled")

    def to_values(self, record: Course):
        return (record.course_name, record.course_number, record.instructor,
                record.capacity, record.num_enrolled)

    def from_row(self, row: sqlite3.Row) -> Course:
        return Course(
            course_name=row["course_name"],
            course_number=row["course_number"],
            instructor=row["instructor"],
            capacity=row["capacity"],
            num_enrolled=row["num_enrolled"],
            course_id=row["course_id"],
        )

    def get_id(self, record: Course) -> Optional[int]:
        return record.course_id

    def set_id(self, record: Course, record_id: int) -> None:
        record.course_id = record_id

    def search(self, term: str) -> list[Course]:
        query = (
            "SELECT * FROM courses "
            "WHERE course_name LIKE ? OR course_number LIKE ? OR instructor LIKE ?"
        )
        pattern = f"%{term}%"
        rows = self._conn.execute(query, (pattern, pattern, pattern)).fetchall()
        return [self.from_row(row) for row in rows]