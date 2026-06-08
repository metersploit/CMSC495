from dataclasses import dataclass
from typing import Optional

@dataclass
class Enrollment:
    """Maps to the enrollment table."""
    student_id: int
    course_id: int
    enrollment_id: Optional[int] = None