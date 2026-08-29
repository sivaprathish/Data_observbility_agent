# Define the file contents as a hashtable
$files = @{
    "app.py" = @"
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_observability_agent.graph.workflow import (
    observability_workflow,
)

from src.data_observability_agent.services.incident_store import (
    IncidentStore,
)


st.set_page_config(
    page_title=""Data Observability Agent"",
    page_icon=""���🔭"",
    layout=""wide"",
)


st.title(
    ""Data Observability Agent""
)

st.caption(
    ""Monitor data quality, freshness, ""
    ""volume, drift and anomalies with ""
    ""AI-powered root cause analysis.""
)


store = IncidentStore()


# =====================================
# Upload
# =====================================

st.header(
    ""1. Upload Data""
)

current_file = st.file_uploader(
    ""Current Dataset"",
    type=[""csv""],
)

baseline_file = st.file_uploader(
    ""Baseline Dataset (optional)"",
    type=[""csv""],
)


if current_file:

    current_df = pd.read_csv(
        current_file
    )

    st.success(
        f""Loaded {len(current_df):,} rows ""
        f""and {len(current_df.columns)} columns.""
    )

    st.dataframe(
        current_df.head(20),
        use_container_width=True,
    )

    # =================================
    # Timestamp
    # =================================

    timestamp_options = [
        ""None""
    ] + list(current_df.columns)

    timestamp_column = st.selectbox(
        ""Timestamp Column"",
        timestamp_options,
    )

    if timestamp_column == ""None"":
        timestamp_column = None

    # =================================
    # Baseline
    # =================================

    baseline_df = None

    if baseline_file:

        baseline_df = pd.read_csv(
            baseline_file
        )

        st.info(
            f""Baseline contains ""
            f""{len(baseline_df):,} rows.""
        )

    # =================================
    # Run
    # =================================

    if st.button(
        ""Run Observability Analysis"",
        type=""primary"",
        use_container_width=True,
    ):

        with st.spinner(
            ""Analyzing dataset...""
        ):

            result = (
                observability_workflow.invoke(
                    {
                        ""current_df"": current_df,
                        ""baseline_df"": baseline_df,
                        ""timestamp_column"": (
                            timestamp_column
                        ),
                    }
                )
            )

        incident = result[
            ""incident_result""
        ]

        # =================================
        # Health Overview
        # =================================

        st.header(
            ""2. Data Health""
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            ""Health Score"",
            f""{incident[''health_score'']}/100"",
        )

        col2.metric(
            ""Severity"",
            incident[""severity""],
        )

        col3.metric(
            ""Incidents"",
            incident[
                ""incident_count""
            ],
        )

        col4.metric(
            ""Rows"",
            f""{len(current_df):,}"",
        )

        # =================================
        # Profiling
        # =================================

        st.header(
            ""3. Data Profile""
        )

        profile = result[
            ""current_profile""
        ]

        profile_col1, profile_col2 = (
            st.columns(2)
        )

        with profile_col1:

            st.subheader(
                ""Schema""
            )

            schema_df = pd.DataFrame(
                list(
                    profile[
                        ""schema""
                    ].items()
                ),
                columns=[
                    ""Column"",
                    ""Data Type"",
                ],
            )

            st.dataframe(
                schema_df,
                use_container_width=True,
            )

        with profile_col2:

            st.subheader(
                ""Null Percentage""
            )

            null_df = pd.DataFrame(
                {
                    ""Column"": list(
                        profile[
                            ""null_percentages""
                        ].keys()
                    ),
                    ""Null %"": list(
                        profile[
                            ""null_percentages""
                        ].values()
                    ),
                }
            )

            st.dataframe(
                null_df,
                use_container_width=True,
            )

        # =================================
        # Agent Status
        # =================================

        st.header(
            ""4. Observability Agents""
        )

        agent_results = [
            (
                ""Quality"",
                result[
                    ""quality_result""
                ],
            ),
            (
                ""Freshness"",
                result[
                    ""freshness_result""
                ],
            ),
            (
                ""Volume"",
                result[
                    ""volume_result""
                ],
            ),
            (
                ""Drift"",
                result[
                    ""drift_result""
                ],
            ),
        ]

        cols = st.columns(
            len(agent_results)
        )

        for col, (
            name,
            agent_result,
        ) in zip(
            cols,
            agent_results,
        ):

            with col:

                st.subheader(
                    name
                )

                st.write(
                    agent_result.get(
                        ""status""
                    )
                )

        # =================================
        # Issues
        # =================================

        st.header(
            ""5. Detected Incidents""
        )

        issues = result.get(
            ""issues"",
            []
        )

        if not issues:

            st.success(
                ""No significant data ""
                ""quality incidents detected.""
            )

        else:

            for index, issue in enumerate(
                issues,
                start=1,
            ):

                with st.expander(
                    f""Incident {index}: ""
                    f""{issue.get(''type'')}"
                ):

                    st.json(
                        issue
                    )

        # =================================
        # Drift
        # =================================

        drift_result = result.get(
            ""drift_result"",
            {}
        )

        distribution = (
            drift_result.get(
                ""distribution_drift"",
                [],
            )
        )

        if distribution:

            st.header(
                ""6. Distribution Drift""
            )

            drift_df = pd.DataFrame(
                distribution
            )

            st.dataframe(
                drift_df,
                use_container_width=True,
            )

            fig = px.bar(
                drift_df,
                x=""column"",
                y=""ks_statistic"",
                title=(
                    ""Distribution Drift ""
                    ""by Column""
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        # =================================
        # Anomalies
        # =================================

        st.header(
            ""7. Record Anomalies""
        )

        anomaly_result = result[
            ""anomaly_result""
        ]

        a1, a2 = st.columns(2)

        a1.metric(
            ""Detected Anomalies"",
            anomaly_result[
                ""anomaly_count""
            ],
        )

        a2.metric(
            ""Anomaly %"",
            f""{anomaly_result[''anomaly_percentage'']}%"",
        )

        # =================================
        # RCA
        # =================================

        st.header(
            ""8. AI Root Cause Analysis""
        )

        rca = result[
            ""rca_result""
        ]

        if rca[
            ""status""
        ] == ""ERROR"":

            st.warning(
                rca[""analysis""]
            )

        else:

            st.markdown(
                rca[""analysis""]
            )

        # =================================
        # Store incident
        # =================================

        if issues:

            store.save(
                incident_result=incident,
                issues=issues,
                rca=rca.get(
                    ""analysis"",
                    """"
                ),
            )

            st.success(
                ""Incident saved to ""
                ""observability history.""
            )


# =====================================
# Historical Incidents
# =====================================

st.divider()

st.header(
    ""Incident History""
)

history = store.get_all()

if history:

    history_df = pd.DataFrame(
        history,
        columns=[
            ""ID"",
            ""Timestamp"",
            ""Health Score"",
            ""Severity"",
            ""Incident Count"",
        ],
    )

    st.dataframe(
        history_df,
        use_container_width=True,
    )

else:

    st.info(
        ""No historical incidents yet.""
    )
"@
    "pyproject.toml" = @"
[project]
name = ""data-observability-agent""
version = ""0.1.0""
description = ""AI-powered Data Observability Agent""
requires-python = "">=3.11""

dependencies = [
    ""streamlit"",
    ""pandas"",
    ""numpy"",
    ""scipy"",
    ""scikit-learn"",
    ""plotly"",
    ""langgraph"",
    ""groq"",
    ""python-dotenv"",
    ""pydantic""
]
"@
    ".env" = @"
GROQ_API_KEY=your_groq_api_key_here

GROQ_MODEL=llama-3.3-70b-versatile
"@
    ".gitignore" = @"
"@
    "data/sample/sample_data.csv" = @"
"@
    "src/profiling/__init__.py" = @"
"@
    "src/profiling/data_profiler.py" = @"
from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


class DataProfiler:

    def profile(self, df: pd.DataFrame) -> dict[str, Any]:

        if df.empty:
            raise ValueError(""Dataset is empty."")

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
                ""mean"": float(series.mean()),
                ""median"": float(series.median()),
                ""std"": float(series.std()) if len(series) > 1 else 0.0,
                ""min"": float(series.min()),
                ""max"": float(series.max()),
            }

        schema = {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

        profile = {
            ""profile_timestamp"": datetime.utcnow().isoformat(),
            ""row_count"": row_count,
            ""column_count"": column_count,
            ""columns"": list(df.columns),
            ""schema"": schema,
            ""null_counts"": null_counts.to_dict(),
            ""null_percentages"": null_percentages.to_dict(),
            ""duplicate_count"": duplicate_count,
            ""duplicate_percentage"": duplicate_percentage,
            ""numeric_stats"": numeric_stats,
        }

        return profile
"@
    "src/agents/__init__.py" = @"
"@
    "src/agents/freshness_agent.py" = @"
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd


class FreshnessAgent:

    def __init__(
        self,
        max_age_hours: float = 24,
    ):
        self.max_age_hours = max_age_hours

    def run(
        self,
        df: pd.DataFrame,
        timestamp_column: str | None,
    ) -> dict:

        if not timestamp_column:

            return {
                ""agent"": ""FreshnessAgent"",
                ""status"": ""SKIPPED"",
                ""issues"": [],
                ""message"": ""Timestamp column not selected."",
            }

        if timestamp_column not in df.columns:

            return {
                ""agent"": ""FreshnessAgent"",
                ""status"": ""ERROR"",
                ""issues"": [],
                ""message"": ""Timestamp column not found."",
            }

        timestamps = pd.to_datetime(
            df[timestamp_column],
            errors=""coerce"",
            utc=True,
        )

        valid = timestamps.dropna()

        if valid.empty:

            return {
                ""agent"": ""FreshnessAgent"",
                ""status"": ""ERROR"",
                ""issues"": [
                    {
                        ""type"": ""INVALID_TIMESTAMP"",
                        ""message"": (
                            ""No valid timestamps found.""
                        ),
                    }
                ],
            }

        latest_timestamp = valid.max()

        now = pd.Timestamp.now(tz=""UTC"")

        age_hours = (
            now - latest_timestamp
        ).total_seconds() / 3600

        issues = []

        if age_hours > self.max_age_hours:

            issues.append(
                {
                    ""type"": ""STALE_DATA"",
                    ""latest_timestamp"": (
                        latest_timestamp.isoformat()
                    ),
                    ""age_hours"": round(
                        age_hours,
                        2,
                    ),
                    ""threshold_hours"": self.max_age_hours,
                    ""message"": (
                        f""Latest data is ""
                        f""{age_hours:.2f} hours old.""
                    ),
                }
            )

        return {
            ""agent"": ""FreshnessAgent"",
            ""status"": (
                ""HEALTHY""
                if not issues
                else ""ISSUES_DETECTED""
            ),
            ""latest_timestamp"": (
                latest_timestamp.isoformat()
            ),
            ""age_hours"": round(age_hours, 2),
            ""issues"": issues,
        }
"@
    "src/agents/quality_agent.py" = @"
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
            ""null_percentages""
        ].items():

            if null_pct > self.null_threshold:

                issues.append(
                    {
                        ""type"": ""HIGH_NULL_RATE"",
                        ""column"": column,
                        ""value"": null_pct,
                        ""threshold"": self.null_threshold,
                        ""message"": (
                            f""{column} contains ""
                            f""{null_pct}% null values.""
                        ),
                    }
                )

        # -------------------------
        # DUPLICATE CHECK
        # -------------------------

        duplicate_pct = profile[
            ""duplicate_percentage""
        ]

        if duplicate_pct > self.duplicate_threshold:

            issues.append(
                {
                    ""type"": ""HIGH_DUPLICATE_RATE"",
                    ""value"": duplicate_pct,
                    ""threshold"": self.duplicate_threshold,
                    ""message"": (
                        f""Duplicate rate is ""
                        f""{duplicate_pct}%.""
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
                        ""type"": ""CONSTANT_COLUMN"",
                        ""column"": column,
                        ""message"": (
                            f""{column} contains ""
                            ""only one unique value.""
                        ),
                    }
                )

        status = (
            ""HEALTHY""
            if not issues
            else ""ISSUES_DETECTED""
        )

        return {
            ""agent"": ""QualityAgent"",
            ""status"": status,
            ""issues"": issues,
        }
"@
    "src/agents/volume_agent.py" = @"
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
                ""agent"": ""VolumeAgent"",
                ""status"": ""NO_BASELINE"",
                ""issues"": [],
            }

        current_rows = current_profile[
            ""row_count""
        ]

        baseline_rows = baseline_profile[
            ""row_count""
        ]

        if baseline_rows == 0:
            return {
                ""agent"": ""VolumeAgent"",
                ""status"": ""NO_BASELINE"",
                ""issues"": [],
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
                ""decrease""
                if change_pct < 0
                else ""increase""
            )

            issues.append(
                {
                    ""type"": ""VOLUME_ANOMALY"",
                    ""current_rows"": current_rows,
                    ""baseline_rows"": baseline_rows,
                    ""change_percentage"": round(
                        change_pct,
                        2,
                    ),
                    ""message"": (
                        f""Row volume {direction} ""
                        f""of {abs(change_pct):.2f}% ""
                        ""detected.""
                    ),
                }
            )

        return {
            ""agent"": ""VolumeAgent"",
            ""status"": (
                ""HEALTHY""
                if not issues
                else ""ISSUES_DETECTED""
            ),
            ""issues"": issues,
        }
"@
    "src/agents/drift_agent.py" = @"
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
                ""agent"": ""DriftAgent"",
                ""status"": ""NO_BASELINE"",
                ""issues"": [],
            }

        schema_result = detect_schema_drift(
            current_profile[""schema""],
            baseline_profile[""schema""],
        )

        distribution_result = (
            detect_distribution_drift(
                current_df,
                baseline_df,
            )
        )

        issues = []

        if schema_result[
            ""drift_detected""
        ]:

            issues.append(
                {
                    ""type"": ""SCHEMA_DRIFT"",
                    ""details"": schema_result,
                }
            )

        drifting_columns = [
            item
            for item in distribution_result
            if item[""drift_detected""]
        ]

        if drifting_columns:

            issues.append(
                {
                    ""type"": ""DISTRIBUTION_DRIFT"",
                    ""columns"": drifting_columns,
                }
            )

        return {
            ""agent"": ""DriftAgent"",
            ""status"": (
                ""HEALTHY""
                if not issues
                else ""ISSUES_DETECTED""
            ),
            ""schema_drift"": schema_result,
            ""distribution_drift"": (
                distribution_result
            ),
            ""issues"": issues,
        }
"@
    "src/agents/rca_agent.py" = @"
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
            ""issues"",
            []
        )

        if not issues:

            return {
                ""agent"": ""RCAAgent"",
                ""status"": ""HEALTHY"",
                ""analysis"": (
                    ""No significant data ""
                    ""observability incidents detected.""
                ),
            }

        prompt = f""""
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
            ""agent"": ""RCAAgent"",
            ""status"": ""ANALYZED"",
            ""analysis"": response,
        }
"@
    "src/agents/incident_agent.py" = @"
from __future__ import annotations


class IncidentAgent:

    SEVERITY_SCORE = {
        ""HIGH_NULL_RATE"": 15,
        ""HIGH_DUPLICATE_RATE"": 15,
        ""CONSTANT_COLUMN"": 5,
        ""VOLUME_ANOMALY"": 20,
        ""STALE_DATA"": 20,
        ""SCHEMA_DRIFT"": 20,
        ""DISTRIBUTION_DRIFT"": 10,
    }

    def run(
        self,
        issues: list[dict],
    ) -> dict:

        penalty = 0

        for issue in issues:

            issue_type = issue.get(
                ""type""
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
            severity = ""HEALTHY""

        elif health_score >= 70:
            severity = ""LOW""

        elif health_score >= 50:
            severity = ""MEDIUM""

        else:
            severity = ""HIGH""

        return {
            ""health_score"": health_score,
            ""severity"": severity,
            ""incident_count"": len(issues),
        }
"@
    "src/detection/__init__.py" = @"
"@
    "src/detection/anomaly_detector.py" = @"
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
        include=""number""
    )

    if numeric_df.empty:

        return {
            ""anomaly_count"": 0,
            ""anomaly_percentage"": 0,
            ""indices"": [],
        }

    imputer = SimpleImputer(
        strategy=""median""
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
        ""anomaly_count"": count,
        ""anomaly_percentage"": round(
            percentage,
            2,
        ),
        ""indices"": anomaly_indices[:100],
    }
"@
    "src/detection/schema_drift.py" = @"
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
                    ""column"": column,
                    ""baseline_type"": baseline_type,
                    ""current_type"": current_type,
                }
            )

    drift_detected = bool(
        added_columns
        or removed_columns
        or type_changes
    )

    return {
        ""drift_detected"": drift_detected,
        ""added_columns"": added_columns,
        ""removed_columns"": removed_columns,
        ""type_changes"": type_changes,
    }
"@
    "src/detection/distribution_drift.py" = @"
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
        .select_dtypes(include=""number"")
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
                ""column"": column,
                ""ks_statistic"": round(
                    float(statistic),
                    4,
                ),
                ""p_value"": round(
                    float(pvalue),
                    6,
                ),
                ""drift_detected"": drift_detected,
            }
        )

    return results
"@
    "src/graph/__init__.py" = @"
"@
    "src/graph/state.py" = @"
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
"@
    "src/graph/workflow.py" = @"
from __future__ import annotations

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from src.data_observability_agent.agents.drift_agent import (
    DriftAgent,
)
from src.data_observability_agent.agents.freshness_agent import (
    FreshnessAgent,
)
from src.data_observability_agent.agents.incident_agent import (
    IncidentAgent,
)
from src.data_observability_agent.agents.quality_agent import (
    QualityAgent,
)
from src.data_observability_agent.agents.rca_agent import RCAAgent
from src.data_observability_agent.agents.volume_agent import (
    VolumeAgent,
)

from src.data_observability_agent.detection.anomaly_detector import (
    detect_anomalies,
)

from src.data_observability_agent.graph.state import (
    ObservabilityState,
)

from src.data_observability_agent.profiling.data_profiler import (
    DataProfiler,
)


profiler = DataProfiler()

quality_agent = QualityAgent()

volume_agent = VolumeAgent()

freshness_agent = FreshnessAgent()

drift_agent = DriftAgent()

incident_agent = IncidentAgent()


def profile_node(
    state: ObservabilityState,
):

    current_profile = profiler.profile(
        state[""current_df""]
    )

    baseline_profile = None

    baseline_df = state.get(
        ""baseline_df""
    )

    if baseline_df is not None:

        baseline_profile = profiler.profile(
            baseline_df
        )

    return {
        ""current_profile"": current_profile,
        ""baseline_profile"": baseline_profile,
    }


def quality_node(
    state: ObservabilityState,
):

    result = quality_agent.run(
        state[""current_df""],
        state[""current_profile""],
    )

    return {
        ""quality_result"": result
    }


def freshness_node(
    state: ObservabilityState,
):

    result = freshness_agent.run(
        state[""current_df""],
        state.get(
            ""timestamp_column""
        ),
    )

    return {
        ""freshness_result"": result
    }


def volume_node(
    state: ObservabilityState,
):

    result = volume_agent.run(
        state[""current_profile""],
        state.get(
            ""baseline_profile""
        ),
    )

    return {
        ""volume_result"": result
    }


def drift_node(
    state: ObservabilityState,
):

    result = drift_agent.run(
        current_df=state[""current_df""],
        current_profile=state[
            ""current_profile""
        ],
        baseline_df=state.get(
            ""baseline_df""
        ),
        baseline_profile=state.get(
            ""baseline_profile""
        ),
    )

    return {
        ""drift_result"": result
    }


def anomaly_node(
    state: ObservabilityState,
):

    result = detect_anomalies(
        state[""current_df""]
    )

    return {
        ""anomaly_result"": result
    }


def collect_incidents_node(
    state: ObservabilityState,
):

    issues = []

    for result_name in [
        ""quality_result"",
        ""freshness_result"",
        ""volume_result"",
        ""drift_result"",
    ]:

        result = state.get(
            result_name,
            {}
        )

        issues.extend(
            result.get(
                ""issues"",
                []
            )
        )

    anomaly = state.get(
        ""anomaly_result"",
        {}
    )

    if anomaly.get(
        ""anomaly_count"",
        0,
    ) > 0:

        issues.append(
            {
                ""type"": ""RECORD_ANOMALIES"",
                ""anomaly_count"": anomaly[
                    ""anomaly_count""
                ],
                ""anomaly_percentage"": anomaly[
                    ""anomaly_percentage""
                ],
            }
        )

    return {
        ""issues"": issues
    }


def incident_node(
    state: ObservabilityState,
):

    result = incident_agent.run(
        state.get(
            ""issues"",
            []
        )
    )

    return {
        ""incident_result"": result
    }


def rca_node(
    state: ObservabilityState,
):

    try:

        agent = RCAAgent()

        result = agent.run(
            {
                ""issues"": state.get(
                    ""issues"",
                    []
                )
            }
        )

    except Exception as exc:

        result = {
            ""agent"": ""RCAAgent"",
            ""status"": ""ERROR"",
            ""analysis"": (
                ""RCA generation failed: ""
                f""{exc}""
            ),
        }

    return {
        ""rca_result"": result
    }


def create_workflow():

    builder = StateGraph(
        ObservabilityState
    )

    builder.add_node(
        ""profile"",
        profile_node,
    )

    builder.add_node(
        ""quality"",
        quality_node,
    )

    builder.add_node(
        ""freshness"",
        freshness_node,
    )

    builder.add_node(
        ""volume"",
        volume_node,
    )

    builder.add_node(
        ""drift"",
        drift_node,
    )

    builder.add_node(
        ""anomaly"",
        anomaly_node,
    )

    builder.add_node(
        ""collect_incidents"",
        collect_incidents_node,
    )

    builder.add_node(
        ""incident"",
        incident_node,
    )

    builder.add_node(
        ""rca"",
        rca_node,
    )

    # -----------------------------
    # Workflow
    # -----------------------------

    builder.add_edge(
        START,
        ""profile"",
    )

    builder.add_edge(
        ""profile"",
        ""quality"",
    )

    builder.add_edge(
        ""quality"",
        ""freshness"",
    )

    builder.add_edge(
        ""freshness"",
        ""volume"",
    )

    builder.add_edge(
        ""volume"",
        ""drift"",
    )

    builder.add_edge(
        ""drift"",
        ""anomaly"",
    )

    builder.add_edge(
        ""anomaly"",
        ""collect_incidents"",
    )

    builder.add_edge(
        ""collect_incidents"",
        ""incident"",
    )

    builder.add_edge(
        ""incident"",
        ""rca"",
    )

    builder.add_edge(
        ""rca"",
        END,
    )

    return builder.compile()


observability_workflow = (
    create_workflow()
)
"@
    "src/llm/__init__.py" = @"
"@
    "src/llm/client.py" = @"
from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv(
            ""GROQ_API_KEY""
        )

        if not api_key:
            raise ValueError(
                ""GROQ_API_KEY is missing.""
            )

        self.model = os.getenv(
            ""GROQ_MODEL"",
            ""llama-3.3-70b-versatile"",
        )

        self.client = Groq(
            api_key=api_key
        )

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        ""role"": ""system"",
                        ""content"": (
                            ""You are a senior data ""
                            ""reliability and data ""
                            ""observability engineer.""
                        ),
                    },
                    {
                        ""role"": ""user"",
                        ""content"": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=1200,
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )
"@
    "src/services/__init__.py" = @"
"@
    "src/services/incident_store.py" = @"
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path(
    ""data/incidents/incidents.db""
)


class IncidentStore:

    def __init__(self):

        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
        )

        self._create_table()

    def _create_table(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                health_score INTEGER,
                severity TEXT,
                incident_count INTEGER,
                issues TEXT,
                rca TEXT
            )
            """
        )

        self.connection.commit()

    def save(
        self,
        incident_result: dict,
        issues: list,
        rca: str,
    ):

        self.connection.execute(
            """
            INSERT INTO incidents (
                created_at,
                health_score,
                severity,
                incident_count,
                issues,
                rca
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                incident_result.get(
                    ""health_score""
                ),
                incident_result.get(
                    ""severity""
                ),
                incident_result.get(
                    ""incident_count""
                ),
                json.dumps(
                    issues,
                    default=str,
                ),
                rca,
            ),
        )

        self.connection.commit()

    def get_all(self):

        cursor = self.connection.execute(
            """
            SELECT
                id,
                created_at,
                health_score,
                severity,
                incident_count
            FROM incidents
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()
"@
}

# Create directories
$dirs = @(
    ""data\sample"",
    ""data\profiles"",
    ""data\incidents"",
    ""src\profiling"",
    ""src\agents"",
    ""src\detection"",
    ""src\graph"",
    ""src\llm"",
    ""src\services""
)

foreach ($dir in $dirs) {
    $fullPath = Join-Path -Path $PSScriptRoot -ChildPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host ""Created directory: $dir""
    }
}

# Create or update files
foreach ($file in $files.Keys) {
    $fullPath = Join-Path -Path $PSScriptRoot -ChildPath $file
    $dir = Split-Path $fullPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (Test-Path $fullPath) {
        $oldContent = Get-Content -Path $fullPath -Raw
        Set-Content -Path $fullPath -Value $files[$file]
        Write-Host ""Updated file: $file""
    } else {
        New-Item -ItemType File -Path $fullPath -Value $files[$file] | Out-Null
        Write-Host ""Created file: $file""
    }
}

Write-Host ""Setup complete.""
"