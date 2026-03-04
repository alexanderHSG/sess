"""SQLite repositories."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from sess.domain.errors import ArtifactNotFoundError


class SQLiteFeatureRepository:
    def __init__(self, db_path: Path, table_name: str) -> None:
        self._db_path = db_path
        self._table_name = table_name

    def load_feature_rows(self) -> pd.DataFrame:
        if not self._db_path.exists():
            raise ArtifactNotFoundError(f"Required SQLite database not found: {self._db_path}")

        query = f"SELECT * FROM {self._table_name}"
        with sqlite3.connect(self._db_path) as conn:
            return pd.read_sql_query(query, conn)

