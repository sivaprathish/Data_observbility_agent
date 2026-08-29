from __future__ import annotations

from typing import Any

import pandas as pd


class QualityAgent:

    def __init__(
        self,
        null_threshold: float = 5.0,
        duplicate_threshold: float = 2.0,
    ):
        self.null_threshold = null_threshold
        self.duplicate_threshold = duplicate_threshold

    def run(
        self,
        df: pd.DataFrame,
        profile: dict[str, Any],
    ) -> dict[str, Any]:

        issues = []

        # -------------------------
        # NULL CHECK
        # -------------------------

        for column, null_pct in profile[
            "null_percentages"
        ].items():

            if null_pct > self.null_threshold:

                issues.append(
                    {
                        "type": "HIGH_NULL_RATE",
                        "column": column,
                        "value": null_pct,
                        "threshold": self.null_threshold,
                        "message": (
                            f"{column} contains "
                            f"{null_pct}% null values."
                        ),
                    }
                )

        # -------------------------
        # DUPLICATE CHECK
        # -------------------------

        duplicate_pct = profile[
            "duplicate_percentage"
        ]

        if duplicate_pct > self.duplicate_threshold:

            issues.append(
                {
                    "type": "HIGH_DUPLICATE_RATE",
                    "value": duplicate_pct,
                    "threshold": self.duplicate_threshold,
                    "message": (
                        f"Duplicate rate is "
                        f"{duplicate_pct}%."
                    ),
                }
            )

        # -------------------------
        # CONSTANT COLUMNS
        # -------------------------

        for column in df.columns:

            unique_values = df[column].nunique(
                dropna=True
            )

            if unique_values == 1:

                issues.append(
                    {
                        "type": "CONSTANT_COLUMN",
                        "column": column,
                        "message": (
                            f"{column} contains "
                            "only one unique value."
                        ),
                    }
                )

        status = (
            "HEALTHY"
            if not issues
            else "ISSUES_DETECTED"
        )

        return {
            "agent": "QualityAgent",
            "status": status,
            "issues": issues,
        }
