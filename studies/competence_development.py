"""Run the exact dynamic development null and value-coupling controls."""
from __future__ import annotations
import json
from hls.dynamic_development import FRONTIER_NULL_UNDER_LEARNING, DEVELOPMENT_VALUE_REVERSAL


def run() -> dict[str, object]:
    null = FRONTIER_NULL_UNDER_LEARNING.compare_choices(0.5)
    reversal = DEVELOPMENT_VALUE_REVERSAL.compare_choices(0.75)
    return {"study": "two-period-competence-development-boundaries",
            "efficient_terminal_outcomes_null_under_learning": {"state_changes": null.agent_1_choice.competence_after_action != null.agent_2_choice.competence_after_action,
                   "efficient_outcomes_equal": null.agent_1_choice.efficient_terminal_outcomes == null.agent_2_choice.efficient_terminal_outcomes,
                   "development_value": null.future_development_value_difference},
            "development_value_reversal": {"immediate_difference": reversal.immediate_value_difference,
                   "development_value": reversal.future_development_value_difference,
                   "total_difference": reversal.total_value_difference},
            "scope": "exact finite two-agent/two-task/two-period constructions"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
