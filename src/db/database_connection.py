# this class is a wrapper for a sqlite connection. Use it to 
# create and close connections.

import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "registration_app.db"

class DatabaseConnection:

    _instance: Optional["DatabaseConnection"] = None

    # make sure this points to the file that was created with build_db() 
    def __init__(self, db_path: str = str(DB_PATH)) -> None:
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @classmethod
    def get_instance(cls, db_path: str = str(DB_PATH)) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance
    
    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None