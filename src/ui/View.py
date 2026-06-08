# Abstract base for every screen in the application

from abc import ABC, abstractmethod
from typing import Optional

from validator import Validator, ValidationError
from models.student import Student

class View(ABC):

    def __init__(self, validator: Validator, title: str = "") -> None:
        self.validator = validator
        self.title = title
        self.current_student: Optional[Student] = None

    # These need to be implemented in subclasses or in gui framework
    @abstractmethod
    def render(self) -> None:
        """Build and display this screen's widgets."""

    @abstractmethod
    def show_error(self, field: str, message: str) -> None:
        """Show one field-level errors."""

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show a general message (e.g. 'That course is full')."""

    # This should work regardless of gui framework
    def report_validation_error(self, error: ValidationError) -> None:

        for field, message in error.errors.items():
            self.show_error(field, message)