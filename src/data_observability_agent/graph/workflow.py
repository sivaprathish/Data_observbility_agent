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
        state["current_df"]
    )

    baseline_profile = None

    baseline_df = state.get(
        "baseline_df"
    )

    if baseline_df is not None:

        baseline_profile = profiler.profile(
            baseline_df
        )

    return {
        "current_profile": current_profile,
        "baseline_profile": baseline_profile,
    }


def quality_node(
    state: ObservabilityState,
):

    result = quality_agent.run(
        state["current_df"],
        state["current_profile"],
    )

    return {
        "quality_result": result
    }


def freshness_node(
    state: ObservabilityState,
):

    result = freshness_agent.run(
        state["current_df"],
        state.get(
            "timestamp_column"
        ),
    )

    return {
        "freshness_result": result
    }


def volume_node(
    state: ObservabilityState,
):

    result = volume_agent.run(
        state["current_profile"],
        state.get(
            "baseline_profile"
        ),
    )

    return {
        "volume_result": result
    }


def drift_node(
    state: ObservabilityState,
):

    result = drift_agent.run(
        current_df=state["current_df"],
        current_profile=state[
            "current_profile"
        ],
        baseline_df=state.get(
            "baseline_df"
        ),
        baseline_profile=state.get(
            "baseline_profile"
        ),
    )

    return {
        "drift_result": result
    }


def anomaly_node(
    state: ObservabilityState,
):

    result = detect_anomalies(
        state["current_df"]
    )

    return {
        "anomaly_result": result
    }


def collect_incidents_node(
    state: ObservabilityState,
):

    issues = []

    for result_name in [
        "quality_result",
        "freshness_result",
        "volume_result",
        "drift_result",
    ]:

        result = state.get(
            result_name,
            {}
        )

        issues.extend(
            result.get(
                "issues",
                []
            )
        )

    anomaly = state.get(
        "anomaly_result",
        {}
    )

    if anomaly.get(
        "anomaly_count",
        0,
    ) > 0:

        issues.append(
            {
                "type": "RECORD_ANOMALIES",
                "anomaly_count": anomaly[
                    "anomaly_count"
                ],
                "anomaly_percentage": anomaly[
                    "anomaly_percentage"
                ],
            }
        )

    return {
        "issues": issues
    }


def incident_node(
    state: ObservabilityState,
):

    result = incident_agent.run(
        state.get(
            "issues",
            []
        )
    )

    return {
        "incident_result": result
    }


def rca_node(
    state: ObservabilityState,
):

    try:

        agent = RCAAgent()

        result = agent.run(
            {
                "issues": state.get(
                    "issues",
                    []
                )
            }
        )

    except Exception as exc:

        result = {
            "agent": "RCAAgent",
            "status": "ERROR",
            "analysis": (
                "RCA generation failed: "
                f"{exc}"
            ),
        }

    return {
        "rca_result": result
    }


def create_workflow():

    builder = StateGraph(
        ObservabilityState
    )

    builder.add_node(
        "profile",
        profile_node,
    )

    builder.add_node(
        "quality",
        quality_node,
    )

    builder.add_node(
        "freshness",
        freshness_node,
    )

    builder.add_node(
        "volume",
        volume_node,
    )

    builder.add_node(
        "drift",
        drift_node,
    )

    builder.add_node(
        "anomaly",
        anomaly_node,
    )

    builder.add_node(
        "collect_incidents",
        collect_incidents_node,
    )

    builder.add_node(
        "incident",
        incident_node,
    )

    builder.add_node(
        "rca",
        rca_node,
    )

    # -----------------------------
    # Workflow
    # -----------------------------

    builder.add_edge(
        START,
        "profile",
    )

    builder.add_edge(
        "profile",
        "quality",
    )

    builder.add_edge(
        "quality",
        "freshness",
    )

    builder.add_edge(
        "freshness",
        "volume",
    )

    builder.add_edge(
        "volume",
        "drift",
    )

    builder.add_edge(
        "drift",
        "anomaly",
    )

    builder.add_edge(
        "anomaly",
        "collect_incidents",
    )

    builder.add_edge(
        "collect_incidents",
        "incident",
    )

    builder.add_edge(
        "incident",
        "rca",
    )

    builder.add_edge(
        "rca",
        END,
    )

    return builder.compile()


observability_workflow = (
    create_workflow()
)
