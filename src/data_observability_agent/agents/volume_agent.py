from __future__ import annotations

from typing import Any


class VolumeAgent:

    def __init__(
        self,
        deviation_threshold: float = 20.0,
    ):
        self.deviation_threshold = deviation_threshold

    def run(
        self,
        current_profile: dict[str, Any],
        baseline_profile: dict[str, Any] | None,
    ) -> dict[str, Any]:

        if baseline_profile is None:

            return {
                "agent": "VolumeAgent",
                "status": "NO_BASELINE",
                "issues": [],
            }

        current_rows = current_profile[
            "row_count"
        ]

        baseline_rows = baseline_profile[
            "row_count"
        ]

        if baseline_rows == 0:
            return {
                "agent": "VolumeAgent",
                "status": "NO_BASELINE",
                "issues": [],
            }

        difference = (
            current_rows - baseline_rows
        )

        change_pct = (
            difference / baseline_rows
        ) * 100

        issues = []

        if abs(change_pct) >= self.deviation_threshold:

            direction = (
                "decrease"
                if change_pct < 0
                else "increase"
            )

            issues.append(
                {
                    "type": "VOLUME_ANOMALY",
                    "current_rows": current_rows,
                    "baseline_rows": baseline_rows,
                    "change_percentage": round(
                        change_pct,
                        2,
                    ),
                    "message": (
                        f"Row volume {direction} "
                        f"of {abs(change_pct):.2f}% "
                        "detected."
                    ),
                }
            )

        return {
            "agent": "VolumeAgent",
            "status": (
                "HEALTHY"
                if not issues
                else "ISSUES_DETECTED"
            ),
            "issues": issues,
        }
