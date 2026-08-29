from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


class DataProfiler:

    def profile(self, df: pd.DataFrame) -> dict[str, Any]:

        if df.empty:
            raise ValueError("Dataset is empty.")

        row_count = len(df)
        column_count = len(df.columns)

        null_counts = df.isnull().sum()
        null_percentages = (
            df.isnull().mean() * 100
        ).round(2)

        duplicate_count = int(
            df.duplicated().sum()
        )

        duplicate_percentage = round(
            duplicate_count / row_count * 100,
            2,
        )

        numeric_stats = {}

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        for column in numeric_columns:

            series = df[column].dropna()

            if series.empty:
                continue

            numeric_stats[column] = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()) if len(series) > 1 else 0.0,
                "min": float(series.min()),
                "max": float(series.max()),
            }

        schema = {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

        profile = {
            "profile_timestamp": datetime.utcnow().isoformat(),
            "row_count": row_count,
            "column_count": column_count,
            "columns": list(df.columns),
            "schema": schema,
            "null_counts": null_counts.to_dict(),
            "null_percentages": null_percentages.to_dict(),
            "duplicate_count": duplicate_count,
            "duplicate_percentage": duplicate_percentage,
            "numeric_stats": numeric_stats,
        }

        return profile
