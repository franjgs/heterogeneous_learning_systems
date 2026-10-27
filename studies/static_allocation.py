"""Run the finite static allocation reference at its symmetric control."""
from __future__ import annotations
import json
from hls.static_assignment import StaticAllocationModel


def run() -> dict[str, float | str]:
    model = StaticAllocationModel(1.0, 0.2, 0.2, 1.0)
    result = model.evaluate(0.5)
    return {"study": "static-allocation-under-crossed-competence", "demand_probability": 0.5,
            "same-agent_effectiveness": result.best_same_agent_effectiveness, "task-routed_effectiveness": result.best_taskwise_effectiveness,
            "difference": result.allocation_gain, "scope": "exact finite two-agent/two-task instance"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
