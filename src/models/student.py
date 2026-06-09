# Filename: student.py
#
# Description: This script provides a class for data in students. It is a data
# only class. 
#
# Parent: None

from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    """maps to the students table."""
    first_name: str
    last_name: str
    email: str
    password_hash: str
    phone_number: Optional[str] = None
    student_id: Optional[int] = None