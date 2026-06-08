# This class abstracts some of the database access objects further
# to avoid needing to write sqlite related boilerplate code.

from dao.data_access_object import DataAccessObject
from db.database_connection import DatabaseConnection
import sqlite3
from abc import abstractmethod
from typing import Any, Optional, Sequence, TypeVar

T = TypeVar("T")

class BaseDAO(DataAccessObject[T]):

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    @property
    def _conn(self) -> sqlite3.Connection:
        return self._db.get_connection()
    
    # Subclasses need to implement table and pk.
    @property
    @abstractmethod
    def table(self) -> str: ...

    @property
    @abstractmethod
    def pk(self) -> str: ...

    @property
    @abstractmethod
    def columns(self) -> Sequence[str]:
        """Writable columns, in insert/update order."""

    @abstractmethod
    def to_values(self, record: T) -> Sequence[Any]:
        """Return the rows's values matching columns function output."""

    @abstractmethod
    def from_row(self, row: sqlite3.Row) -> T:
        """Build a model object from a database row."""

    @abstractmethod
    def get_id(self, record: T) -> Optional[int]:
        """Return the rows's primary-key value."""

    @abstractmethod
    def set_id(self, record: T, record_id: int) -> None:
        """Store a newly generated primary key back on the record."""

    # Concrete implementations of parent class methods are below here.
    def insert_row(self, record: T) -> int:
        joined_columns = ", ".join(self.columns)
        placeholder = ", ".join("?" for _ in self.columns)
        query = f"INSTER INTO {self.table} ({joined_columns} VALUES {placeholder})"
        cursor = self._conn.execute(query, tuple(self.to_values(record)))
        self.conn.commit()
        new_id = cursor.lastrowid
        self.set_id(record, new_id)
        return new_id
    
    def find_row(self, record_id: int) -> Optional[T]:
        query = f"SELECT * FROM {self.table} WHERE {self.pk} = ?"
        row = self._conn.execute(query, (record_id,)).fetchone()
        return self.from_row(row) if row is not None else None

    def update_row(self, record: T) -> bool:
        assignments = ", ".join(f"{c} = ?" for c in self.columns)
        query = f"UPDATE {self.table} SET {assignments} WHERE {self.pk} = ?"
        values = (*self.to_values(record), self.get_id(record))
        cursor = self._conn.execute(query, values)
        self._conn.commit()
        return cursor.rowcount > 0

    def delete_row(self, record_id: int) -> bool:
        query = f"DELETE FROM {self.table} WHERE {self.pk} = ?"
        cursor = self._conn.execute(query, (record_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    # Returns true if a row id exists.
    def exists(self, record_id: int) -> bool:
        return self.find_row(record_id) is not None