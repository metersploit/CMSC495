# Filename: course.py
#
# Description: This script provides a class for data in courses. It is a data
# only class. 
#
# Parent: None

from dataclasses import dataclass
from typing import Optional

@dataclass
class Course:
    """maps to the courses table."""
    course_name: str
    course_number: str
    instructor: str
    capacity: int
    num_enrolled: int = 0
    course_id: Optional[int] = None

    # Make sure there is space left in the class
    @property
    def has_available_seats(self) -> bool:
        return self.num_enrolled < self.capacity