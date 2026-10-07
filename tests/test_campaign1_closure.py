"""Documentation/provenance checks for the closed Campaign 1 record."""

import csv
import hashlib
import json
from pathlib import Path

from hls.campaign1_protocol import SCENARIO_IDS


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "campaigns" / "campaign1_test_range"
CLOSURE = RESULTS / "closure_provenance.json"


def _rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def test_campaign1_closure_has_frozen_commits_scope_and_test_range():
    closure = json.loads(CLOSURE.read_text())
    assert closure["commits"] == {
        "frozen_test_range": "05b86cb",
        "frozen_execution_protocol": "bcc3ad8",
        "campaign1_results": "ac9d421",
    }
    assert closure["classification"]["status"] == "PASS"
    assert tuple(closure["frozen_test_range_carried_forward"]["scenario_ids"]) == SCENARIO_IDS
    assert closure["transition_status"]["campaign2_design"] == "NOT DESIGNED"


def test_campaign1_closure_hashes_authoritative_result_artifacts():
    closure = json.loads(CLOSURE.read_text())
    for artifact in closure["source_artifacts"]:
        path = ROOT / artifact["path"]
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_campaign1_closure_records_counts_and_no_new_executions():
    closure = json.loads(CLOSURE.read_text())
    assert closure["integrity"]["new_campaign1_team_executions"] == 0
    assert closure["integrity"]["new_campaign1_simulation_runs"] == 0
    assert _rows(RESULTS / "runs.csv") == 960
    assert _rows(RESULTS / "trajectories.csv") == 17_280


def test_campaign1_closure_retains_nulls_and_limits_instead_of_winner_claims():
    closure = json.loads(CLOSURE.read_text())
    negative = " ".join(closure["epistemic_status"]["negative_null"])
    limitations = " ".join(closure["epistemic_status"]["limitations_and_unsupported"])
    assert "G07" in negative and "no diversity" in negative
    assert "not a pure additive cost of DISCOVER" in limitations
    assert "not matched" in limitations
