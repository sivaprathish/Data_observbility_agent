from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd


class ObservabilityState(TypedDict, total=False):

    current_df: pd.DataFrame

    baseline_df: pd.DataFrame | None

    timestamp_column: str | None

    current_profile: dict[str, Any]

    baseline_profile: dict[str, Any] | None

    quality_result: dict

    volume_result: dict

    freshness_result: dict

    drift_result: dict

    anomaly_result: dict

    issues: list[dict]

    incident_result: dict

    rca_result: dict
