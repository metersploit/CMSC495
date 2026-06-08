import sqlite3
from abc import abstractmethod
from typing import Any, Optional, Sequence, TypeVar

from dao.data_access_object import DataAccessObject
from db.database_connection import DatabaseConnection

T = TypeVar("T")


class BaseDAO(DataAccessObject[T]):

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    @property
    def _conn(self) -> sqlite3.Connection:
        return self._db.get_connection()

    # hooks for the that the subclasses need to implement
    @property
    @abstractmethod
    def table(self) -> str: ...

    @property
    @abstractmethod
    def pk(self) -> str: ...

    @property
    @abstractmethod
    def columns(self) -> Sequence[str]: ...

    @abstractmethod
    def to_values(self, record: T) -> Sequence[Any]: ...

    @abstractmethod
    def from_row(self, row: sqlite3.Row) -> T: ...

    @abstractmethod
    def get_id(self, record: T) -> Optional[int]: ...

    @abstractmethod
    def set_id(self, record: T, record_id: int) -> None: ...

    # SQL operations
    def insert_row(self, record: T) -> int:
        cols = ", ".join(self.columns)
        placeholders = ", ".join("?" for _ in self.columns)
        query = f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"
        cursor = self._conn.execute(query, tuple(self.to_values(record)))
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
        return cursor.rowcount > 0

    def delete_row(self, record_id: int) -> bool:
        query = f"DELETE FROM {self.table} WHERE {self.pk} = ?"
        cursor = self._conn.execute(query, (record_id,))
        return cursor.rowcount > 0

    def exists(self, record_id: int) -> bool:
        return self.find_row(record_id) is not None