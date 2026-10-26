import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "docs/registry/validate_hls_scientific_registry.py"
SPEC = importlib.util.spec_from_file_location("hls_registry_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


def research_record(record_id="R1", result_refs=None, relations=None):
    return {
        "schema_version": "1.0",
        "record_type": "research",
        "id": record_id,
        "name": "Test research",
        "question": "A test question?",
        "hypotheses": None,
        "scenario_refs": [],
        "organization_refs": [],
        "model_refs": [],
        "policy_refs": [],
        "protocol_refs": [],
        "research_status": "closed",
        "evidence_status": ["exact_computation"],
        "limitations": [],
        "sources": [{"path": "source.md", "section": "Test", "role": "primary"}],
        "dates": {
            "event": None,
            "decision": None,
            "execution_start": None,
            "execution_end": None,
            "recorded": None,
        },
        "relations": relations or [],
        "result_refs": result_refs or [],
        "application_refs": [],
        "audit_experiment_families": [],
        "theory_ledger_refs": [],
    }


def result_record(research_id="R1", record_id="R1-RES"):
    return {
        "schema_version": "1.0",
        "record_type": "result",
        "id": record_id,
        "research_id": research_id,
        "claim": "A bounded test result.",
        "result_kind": "exact_computation",
        "outcome_class": "positive",
        "estimand": None,
        "value": None,
        "uncertainty": None,
        "unit_of_analysis": None,
        "conditions": {},
        "sources": [{"path": "source.md", "section": "Test", "role": "primary"}],
        "configuration": None,
        "code_commit": None,
        "config_hash": None,
        "artifact_manifest": None,
        "raw_artifact_status": "not_applicable",
        "artifact_availability": "not_applicable",
        "artifact_refs": [],
        "scope_and_nonclaims": [],
        "theory_ledger_refs": [],
        "provenance": {
            "code_commit": None,
            "config_hash": None,
            "configuration_path": None,
            "manifest_path": None,
            "execution_command": None,
            "software_versions": None,
        },
    }


class RegistryValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "source.md").write_text("primary source\n", encoding="utf-8")
        self.exp_csv = self.root / "experiment_matrix.csv"
        self.exp_csv.write_text("line\n", encoding="utf-8")
        self.theory_csv = self.root / "theory_ledger.csv"
        self.theory_csv.write_text("result\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "add", "source.md", "experiment_matrix.csv", "theory_ledger.csv"],
            cwd=self.root,
            check=True,
        )

    def tearDown(self):
        self.temp.cleanup()

    def validate_records(self, records):
        registry = self.root / "registry.jsonl"
        registry.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        return validator.validate_registry(registry, self.root, self.exp_csv, self.theory_csv)

    def test_valid_linked_pair_and_generated_summary(self):
        result = result_record()
        research = research_record(result_refs=[result["id"]])
        report = self.validate_records([research, result])
        self.assertTrue(report["valid"], report["summary"]["errors"])
        self.assertEqual(report["summary"]["research_count"], 1)
        self.assertEqual(report["summary"]["result_count"], 1)
        self.assertEqual(report["summary"]["research_without_results"], [])

    def test_duplicate_ids_and_broken_result_reference_are_errors(self):
        first = research_record(result_refs=["missing"])
        second = research_record()
        report = self.validate_records([first, second])
        self.assertFalse(report["valid"])
        self.assertTrue(any("duplicate id" in error for error in report["summary"]["errors"]))
        self.assertTrue(any("unknown result_ref" in error for error in report["summary"]["errors"]))

    def test_missing_primary_source_is_an_error(self):
        result = result_record()
        result["sources"][0]["path"] = "absent.md"
        report = self.validate_records([research_record(), result])
        self.assertFalse(report["valid"])
        self.assertTrue(any("source file does not exist" in error for error in report["summary"]["errors"]))

    def test_result_requires_accessible_primary_source(self):
        result = result_record()
        result["sources"][0]["role"] = "supporting"
        report = self.validate_records([research_record(), result])
        self.assertFalse(report["valid"])
        self.assertTrue(any("no Git-tracked primary source" in error for error in report["summary"]["errors"]))

    def test_invalid_state_and_inconsistent_dates_are_errors(self):
        research = research_record()
        research["research_status"] = "promising"
        research["dates"]["event"] = "2026-10-20"
        research["dates"]["decision"] = "2026-10-19"
        report = self.validate_records([research])
        self.assertFalse(report["valid"])
        self.assertTrue(any("invalid research_status" in error for error in report["summary"]["errors"]))
        self.assertTrue(any("decision date precedes event date" in error for error in report["summary"]["errors"]))

    def test_directional_relation_cycle_is_rejected(self):
        one = research_record("R1", relations=[{"type": "supersedes", "id": "R2"}])
        two = research_record("R2", relations=[{"type": "derived_from", "id": "R1"}])
        report = self.validate_records([one, two])
        self.assertFalse(report["valid"])
        self.assertTrue(any("contain a cycle" in error for error in report["summary"]["errors"]))

    def test_matrix_and_theory_coverage_gaps_are_reported(self):
        self.exp_csv.write_text("line\nfamily A\nfamily B\n", encoding="utf-8")
        self.theory_csv.write_text("result\nT0\nT1\n", encoding="utf-8")
        research = research_record()
        research["audit_experiment_families"] = ["family A"]
        research["theory_ledger_refs"] = ["T0"]
        report = self.validate_records([research])
        self.assertEqual(report["summary"]["audit_families_unrepresented"], ["family B"])
        self.assertEqual(report["summary"]["theory_ledger_unrepresented"], ["T1"])

    def test_invalid_jsonl_is_rejected(self):
        registry = self.root / "registry.jsonl"
        registry.write_text('{"record_type":\n', encoding="utf-8")
        report = validator.validate_registry(registry, self.root, self.exp_csv, self.theory_csv)
        self.assertFalse(report["valid"])
        self.assertTrue(any("invalid JSON" in error for error in report["summary"]["errors"]))

    def test_missing_protocol_and_artifact_paths_are_rejected(self):
        research = research_record()
        research["protocol_refs"] = ["missing_protocol.md"]
        result = result_record()
        result["artifact_refs"] = ["missing_result.csv"]
        report = self.validate_records([research, result])
        self.assertFalse(report["valid"])
        messages = report["summary"]["errors"]
        self.assertTrue(any("protocol_refs path does not exist" in error for error in messages))
        self.assertTrue(any("artifact_refs path does not exist" in error for error in messages))

    def test_unknown_relation_type_is_rejected(self):
        research = research_record(relations=[{"type": "invented", "id": "R1"}])
        report = self.validate_records([research])
        self.assertFalse(report["valid"])
        self.assertTrue(any("malformed or unknown research relation" in error for error in report["summary"]["errors"]))


if __name__ == "__main__":
    unittest.main()
