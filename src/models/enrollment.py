# Filename: enrollment.py
#
# Description: This script provides a class for data in enrollments. It is a data
# only class. 
#
# Parent: None

from dataclasses import dataclass
from typing import Optional

@dataclass
class Enrollment:
    """Maps to the enrollment table."""
    student_id: int
    course_id: int
    enrollment_id: Optional[int] = None