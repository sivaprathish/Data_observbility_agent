from __future__ import annotations

import pandas as pd

from scipy.stats import ks_2samp


def detect_distribution_drift(
    current_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    alpha: float = 0.05,
) -> list[dict]:

    results = []

    numeric_columns = (
        current_df
        .select_dtypes(include="number")
        .columns
    )

    for column in numeric_columns:

        if column not in baseline_df.columns:
            continue

        current_values = (
            current_df[column]
            .dropna()
        )

        baseline_values = (
            baseline_df[column]
            .dropna()
        )

        if (
            len(current_values) < 10
            or len(baseline_values) < 10
        ):
            continue

        statistic, pvalue = ks_2samp(
            current_values,
            baseline_values,
        )

        drift_detected = (
            pvalue < alpha
        )

        results.append(
            {
                "column": column,
                "ks_statistic": round(
                    float(statistic),
                    4,
                ),
                "p_value": round(
                    float(pvalue),
                    6,
                ),
                "drift_detected": drift_detected,
            }
        )

    return results
