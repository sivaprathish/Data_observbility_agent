from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd


class FreshnessAgent:

    def __init__(
        self,
        max_age_hours: float = 24,
    ):
        self.max_age_hours = max_age_hours

    def run(
        self,
        df: pd.DataFrame,
        timestamp_column: str | None,
    ) -> dict:

        if not timestamp_column:

            return {
                "agent": "FreshnessAgent",
                "status": "SKIPPED",
                "issues": [],
                "message": "Timestamp column not selected.",
            }

        if timestamp_column not in df.columns:

            return {
                "agent": "FreshnessAgent",
                "status": "ERROR",
                "issues": [],
                "message": "Timestamp column not found.",
            }

        timestamps = pd.to_datetime(
            df[timestamp_column],
            errors="coerce",
            utc=True,
        )

        valid = timestamps.dropna()

        if valid.empty:

            return {
                "agent": "FreshnessAgent",
                "status": "ERROR",
                "issues": [
                    {
                        "type": "INVALID_TIMESTAMP",
                        "message": (
                            "No valid timestamps found."
                        ),
                    }
                ],
            }

        latest_timestamp = valid.max()

        now = pd.Timestamp.now(tz="UTC")

        age_hours = (
            now - latest_timestamp
        ).total_seconds() / 3600

        issues = []

        if age_hours > self.max_age_hours:

            issues.append(
                {
                    "type": "STALE_DATA",
                    "latest_timestamp": (
                        latest_timestamp.isoformat()
                    ),
                    "age_hours": round(
                        age_hours,
                        2,
                    ),
                    "threshold_hours": self.max_age_hours,
                    "message": (
                        f"Latest data is "
                        f"{age_hours:.2f} hours old."
                    ),
                }
            )

        return {
            "agent": "FreshnessAgent",
            "status": (
                "HEALTHY"
                if not issues
                else "ISSUES_DETECTED"
            ),
            "latest_timestamp": (
                latest_timestamp.isoformat()
            ),
            "age_hours": round(age_hours, 2),
            "issues": issues,
        }
