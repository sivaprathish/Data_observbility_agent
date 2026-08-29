from __future__ import annotations


class IncidentAgent:

    SEVERITY_SCORE = {
        "HIGH_NULL_RATE": 15,
        "HIGH_DUPLICATE_RATE": 15,
        "CONSTANT_COLUMN": 5,
        "VOLUME_ANOMALY": 20,
        "STALE_DATA": 20,
        "SCHEMA_DRIFT": 20,
        "DISTRIBUTION_DRIFT": 10,
    }

    def run(
        self,
        issues: list[dict],
    ) -> dict:

        penalty = 0

        for issue in issues:

            issue_type = issue.get(
                "type"
            )

            penalty += self.SEVERITY_SCORE.get(
                issue_type,
                5,
            )

        health_score = max(
            0,
            100 - penalty,
        )

        if health_score >= 90:
            severity = "HEALTHY"

        elif health_score >= 70:
            severity = "LOW"

        elif health_score >= 50:
            severity = "MEDIUM"

        else:
            severity = "HIGH"

        return {
            "health_score": health_score,
            "severity": severity,
            "incident_count": len(issues),
        }
