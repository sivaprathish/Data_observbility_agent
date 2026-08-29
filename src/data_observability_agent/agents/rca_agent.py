from __future__ import annotations

import json

from src.data_observability_agent.llm.client import LLMClient


class RCAAgent:

    def __init__(self):

        self.llm = LLMClient()

    def run(
        self,
        observations: dict,
    ) -> dict:

        issues = observations.get(
            "issues",
            []
        )

        if not issues:

            return {
                "agent": "RCAAgent",
                "status": "HEALTHY",
                "analysis": (
                    "No significant data "
                    "observability incidents detected."
                ),
            }

        prompt = f"""
Analyze the following data observability
incidents.

INCIDENTS:

{json.dumps(issues, indent=2, default=str)}

Determine:

1. Most likely root cause
2. Evidence supporting the conclusion
3. Potential downstream impact
4. Severity
5. Recommended investigation
6. Recommended remediation

Do not invent infrastructure facts that are
not present in the evidence.

Return a concise professional incident analysis.
"""

        response = self.llm.generate(
            prompt
        )

        return {
            "agent": "RCAAgent",
            "status": "ANALYZED",
            "analysis": response,
        }
