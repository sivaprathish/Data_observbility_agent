from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path(
    "data/incidents/incidents.db"
)


class IncidentStore:

    def __init__(self):

        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
        )

        self._create_table()

    def _create_table(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                health_score INTEGER,
                severity TEXT,
                incident_count INTEGER,
                issues TEXT,
                rca TEXT
            )
            """
        )

        self.connection.commit()

    def save(
        self,
        incident_result: dict,
        issues: list,
        rca: str,
    ):

        self.connection.execute(
            """
            INSERT INTO incidents (
                created_at,
                health_score,
                severity,
                incident_count,
                issues,
                rca
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                incident_result.get(
                    "health_score"
                ),
                incident_result.get(
                    "severity"
                ),
                incident_result.get(
                    "incident_count"
                ),
                json.dumps(
                    issues,
                    default=str,
                ),
                rca,
            ),
        )

        self.connection.commit()

    def get_all(self):

        cursor = self.connection.execute(
            """
            SELECT
                id,
                created_at,
                health_score,
                severity,
                incident_count
            FROM incidents
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()
