# Filename: data_access_object.py
#
# Description: This script provides a generic, abstract class that serves as the
# contract for DAO subclasses. The concrete subclasses are bound to a single
# object of type T and its table, so the the table is fixed by the subclass
# rather than passed each function call.
#
# Parent: None

from typing import Generic, Optional, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")

class DataAccessObject(ABC, Generic[T]):

    @abstractmethod
    def insert_row(self, record: T) -> int:
        """Insert a row into a table."""

    @abstractmethod
    def find_row(self, record_id: int) -> Optional[T]:
        """Find a row in a table."""

    @abstractmethod
    def update_row(self, record: T) -> bool:
        """Update a row in a table."""

    @abstractmethod
    def delete_row(self, table_name: str) -> None:
        """Delete a row in a table."""