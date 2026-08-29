from __future__ import annotations

import pandas as pd

from src.data_observability_agent.detection.schema_drift import (
    detect_schema_drift,
)

from src.data_observability_agent.detection.distribution_drift import (
    detect_distribution_drift,
)


class DriftAgent:

    def run(
        self,
        current_df: pd.DataFrame,
        current_profile: dict,
        baseline_df: pd.DataFrame | None,
        baseline_profile: dict | None,
    ) -> dict:

        if (
            baseline_df is None
            or baseline_profile is None
        ):

            return {
                "agent": "DriftAgent",
                "status": "NO_BASELINE",
                "issues": [],
            }

        schema_result = detect_schema_drift(
            current_profile["schema"],
            baseline_profile["schema"],
        )

        distribution_result = (
            detect_distribution_drift(
                current_df,
                baseline_df,
            )
        )

        issues = []

        if schema_result[
            "drift_detected"
        ]:

            issues.append(
                {
                    "type": "SCHEMA_DRIFT",
                    "details": schema_result,
                }
            )

        drifting_columns = [
            item
            for item in distribution_result
            if item["drift_detected"]
        ]

        if drifting_columns:

            issues.append(
                {
                    "type": "DISTRIBUTION_DRIFT",
                    "columns": drifting_columns,
                }
            )

        return {
            "agent": "DriftAgent",
            "status": (
                "HEALTHY"
                if not issues
                else "ISSUES_DETECTED"
            ),
            "schema_drift": schema_result,
            "distribution_drift": (
                distribution_result
            ),
            "issues": issues,
        }
