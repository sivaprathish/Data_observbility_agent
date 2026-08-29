from __future__ import annotations

import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def detect_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.01,
) -> dict:

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.empty:

        return {
            "anomaly_count": 0,
            "anomaly_percentage": 0,
            "indices": [],
        }

    imputer = SimpleImputer(
        strategy="median"
    )

    values = imputer.fit_transform(
        numeric_df
    )

    scaler = StandardScaler()

    values = scaler.fit_transform(
        values
    )

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
    )

    predictions = model.fit_predict(
        values
    )

    anomaly_mask = (
        predictions == -1
    )

    anomaly_indices = (
        df.index[anomaly_mask]
        .tolist()
    )

    count = len(anomaly_indices)

    percentage = (
        count / len(df) * 100
        if len(df)
        else 0
    )

    return {
        "anomaly_count": count,
        "anomaly_percentage": round(
            percentage,
            2,
        ),
        "indices": anomaly_indices[:100],
    }
