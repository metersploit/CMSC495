import re
from typing import Optional

from service.backend_controller import BackendController
from models.student import Student
from models.course import Course

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^[0-9+\-\s().]{7,20}$")
MIN_PASSWORD_LENGTH = 8

class ValidationError(Exception):
    """Raised when one or more fields fail validation."""

    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__("; ".join(f"{field}: {msg}" for field, msg in errors.items()))


class Validator:
    """Checks that input is complete and well formed, then forwards valid
    requests to the BackendController. Invalid input is rejected."""

    def __init__(self, controller: Optional[BackendController] = None) -> None:
        self._controller = controller or BackendController()

    # Account creation checks
    def create_account(self, first_name: str, last_name: str, email: str,
                       phone_number: Optional[str], password: str) -> Student:
        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        email = (email or "").strip().lower()
        phone_number = (phone_number or "").strip()
        password = password or ""

        errors: dict[str, str] = {}
        if not first_name:
            errors["first_name"] = "First name is required."
        if not last_name:
            errors["last_name"] = "Last name is required."
        if not email:
            errors["email"] = "Email is required."
        elif not _EMAIL_RE.match(email):
            errors["email"] = "Enter a valid email address."
        if phone_number and not _PHONE_RE.match(phone_number):
            errors["phone_number"] = "Enter a valid phone number."
        if not password:
            errors["password"] = "Password is required."
        elif len(password) < MIN_PASSWORD_LENGTH:
            errors["password"] = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

        if errors:
            raise ValidationError(errors)

        return self._controller.create_account(
            first_name, last_name, email, phone_number or None, password
        )

    # Login checks
    def login(self, email: str, password: str) -> Student:
        email = (email or "").strip().lower()
        password = password or ""

        errors: dict[str, str] = {}
        if not email:
            errors["email"] = "Email is required."
        elif not _EMAIL_RE.match(email):
            errors["email"] = "Enter a valid email address."
        if not password:
            errors["password"] = "Password is required."

        if errors:
            raise ValidationError(errors)

        return self._controller.authenticate(email, password)

    # Course search checks
    def search_courses(self, term: str) -> list[Course]:
        term = (term or "").strip()
        if not term:
            raise ValidationError({"search": "Enter a search term."})
        return self._controller.search_courses(term)

    # Enroll/drop checks
    def enroll(self, student_id: int, course_id: int) -> None:
        self._require_ids(student_id, course_id)
        self._controller.enroll(student_id, course_id)

    def drop(self, student_id: int, course_id: int) -> None:
        self._require_ids(student_id, course_id)
        self._controller.drop(student_id, course_id)

    # Schedule checks
    def get_schedule(self, student_id: int) -> list[Course]:
        if not self._is_positive_int(student_id):
            raise ValidationError({"student_id": "A valid student id is required."})
        return self._controller.get_schedule(student_id)

    # Checks to make sure inputs are positive ints.
    @staticmethod
    def _is_positive_int(value) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and value > 0

    # makes sure there is an id and it is valid
    def _require_ids(self, student_id: int, course_id: int) -> None:
        errors: dict[str, str] = {}
        if not self._is_positive_int(student_id):
            errors["student_id"] = "A valid student id is required."
        if not self._is_positive_int(course_id):
            errors["course_id"] = "A valid course id is required."
        if errors:
            raise ValidationError(errors)