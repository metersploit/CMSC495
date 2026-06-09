# Filename: base_dao.py
#
# Description: This script provides an abstract class with both abstract and
# concrete subroutines. It is a subclass of DataAccessObject that implements
# multiple abstract subroutines. The abstract subroutines should be implemented 
# by entity DAO subclasses. The concrete subroutines are various SQL operations
# on tables: insert, update, delete, find. Additionally, there is a subroutine
# to determine if a row exists.
# 
# Parent: DataAccessObject

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
    
    #################################################################
    #### Implement the subroutines in this section in subclasses ####
    #################################################################

    # Return a table name.
    @property
    @abstractmethod
    def table(self) -> str: ...

    # Return the Primary Key column name.
    @property
    @abstractmethod
    def pk(self) -> str: ...

    # Return a Sequence of column names.
    @property
    @abstractmethod
    def columns(self) -> Sequence[str]: ...

    # Return the values of a model class.
    @abstractmethod
    def to_values(self, record: T) -> Sequence[Any]: ...

    # Return the values of a row.
    @abstractmethod
    def from_row(self, row: sqlite3.Row) -> T: ...

    # Return the PK of a row.
    @abstractmethod
    def get_id(self, record: T) -> Optional[int]: ...

    # Set the PK of a row.
    @abstractmethod
    def set_id(self, record: T, record_id: int) -> None: ...
    
    #########################################
    #### Concrete subroutines begin here ####
    #########################################

    # Insert a row into a table. Returns the PK.
    def insert_row(self, record: T) -> int:
        cols = ", ".join(self.columns)
        placeholders = ", ".join("?" for _ in self.columns)
        query = f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"
        cursor = self._conn.execute(query, tuple(self.to_values(record)))
        new_id = cursor.lastrowid
        self.set_id(record, new_id)
        return new_id

    # Find a row by PK. Returns the row values.
    def find_row(self, record_id: int) -> Optional[T]:
        query = f"SELECT * FROM {self.table} WHERE {self.pk} = ?"
        row = self._conn.execute(query, (record_id,)).fetchone()
        return self.from_row(row) if row is not None else None

    # Update a row. Returns True if successful.
    def update_row(self, record: T) -> bool:
        assignments = ", ".join(f"{c} = ?" for c in self.columns)
        query = f"UPDATE {self.table} SET {assignments} WHERE {self.pk} = ?"
        values = (*self.to_values(record), self.get_id(record))
        cursor = self._conn.execute(query, values)
        return cursor.rowcount > 0

    # Delete a row by PK. Returns True if successful.
    def delete_row(self, record_id: int) -> bool:
        query = f"DELETE FROM {self.table} WHERE {self.pk} = ?"
        cursor = self._conn.execute(query, (record_id,))
        return cursor.rowcount > 0

    # Check if a row exists by PK. Returns True if it exists.
    def exists(self, record_id: int) -> bool:
        return self.find_row(record_id) is not None