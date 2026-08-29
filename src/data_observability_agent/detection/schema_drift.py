from __future__ import annotations


def detect_schema_drift(
    current_schema: dict,
    baseline_schema: dict,
) -> dict:

    current_columns = set(
        current_schema.keys()
    )

    baseline_columns = set(
        baseline_schema.keys()
    )

    added_columns = list(
        current_columns - baseline_columns
    )

    removed_columns = list(
        baseline_columns - current_columns
    )

    type_changes = []

    common_columns = (
        current_columns & baseline_columns
    )

    for column in common_columns:

        current_type = current_schema[
            column
        ]

        baseline_type = baseline_schema[
            column
        ]

        if current_type != baseline_type:

            type_changes.append(
                {
                    "column": column,
                    "baseline_type": baseline_type,
                    "current_type": current_type,
                }
            )

    drift_detected = bool(
        added_columns
        or removed_columns
        or type_changes
    )

    return {
        "drift_detected": drift_detected,
        "added_columns": added_columns,
        "removed_columns": removed_columns,
        "type_changes": type_changes,
    }
