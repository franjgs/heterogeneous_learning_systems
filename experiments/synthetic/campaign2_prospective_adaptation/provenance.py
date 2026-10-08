"""Bind validated raw/derived outputs and source without self-referential hashes."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import matplotlib
from . import run


def main():
    run.preflight()
    manifest=json.loads((run.OUT/"execution_manifest.json").read_text())
    assert manifest["execution_code_sha256"]==run.digest(run.ROOT/"experiments/synthetic/campaign2_prospective_adaptation/run.py")
    validation=json.loads((run.OUT/"validation_summary.json").read_text())
    assert validation["passed"]
    for name,sha in validation["raw_sha256"].items():
        assert run.digest(run.OUT/name)==sha
    allowed=("experiments/synthetic/campaign2_prospective_adaptation/",
        "results/campaigns/campaign2_prospective_adaptation/",
        "docs/experiments/CAMPAIGN_2_RESULTS.md",
        "docs/experiments/CAMPAIGN_2_IO_INCIDENT.md","tests/test_campaign2_execution.py")
    changed=subprocess.check_output(["git","diff","--name-only",run.PREREG_COMMIT,"--"],cwd=run.ROOT,text=True).splitlines()
    assert all(any(p.startswith(prefix) for prefix in allowed) for p in changed),changed
    suites=ET.parse(run.OUT/"tests.xml").getroot().iter("testsuite")
    tests=dict.fromkeys(("tests","failures","errors","skipped"),0)
    for suite in suites:
        for k in tests:
            tests[k]+=int(suite.attrib.get(k,0))
    assert tests["failures"]==tests["errors"]==tests["skipped"]==0,tests
    sources=[*sorted((run.ROOT/"experiments/synthetic/campaign2_prospective_adaptation").glob("*.py")),
        run.ROOT/"docs/experiments/CAMPAIGN_2_RESULTS.md",
        run.ROOT/"docs/experiments/CAMPAIGN_2_IO_INCIDENT.md",run.ROOT/"tests/test_campaign2_execution.py",
        run.INCIDENT/".gitattributes"]
    incident_files=("validation_failure.json","execution_manifest.json","raw_completion.json",
                    "failed_attempt_01_runner.py.txt","io_forensic_evidence.json")
    incident_hashes={name:run.digest(run.INCIDENT/name) for name in incident_files}
    assert incident_hashes["validation_failure.json"]==manifest["validation_failure_sha256"]
    assert incident_hashes["execution_manifest.json"]==manifest["failed_attempt_manifest_sha256"]
    run.dump(run.OUT/"provenance.json",dict(
        result_id="campaign2-prospective-adaptation-results-v1",
        preregistration_commit=run.PREREG_COMMIT,C2_commit=manifest["C2_commit"],
        execution_base_commit=manifest["code_base_commit"],
        execution_command="python experiments/synthetic/campaign2_prospective_adaptation/run.py --workers 8",
        runtime=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,matplotlib=matplotlib.__version__),
        final_commit_identity="the single git commit containing this artifact; not embedded to avoid self-reference",
        source_sha256={str(p.relative_to(run.ROOT)):run.digest(p) for p in sources},
        output_sha256={p.name:run.digest(p) for p in sorted(run.OUT.iterdir()) if p.is_file() and p.name!="provenance.json"},
        original_failed_attempt_sha256=incident_hashes,
        original_failed_attempt_unchanged=True,
        serialization_notes=dict(csv="original CRLF action tables preserved; scoped whitespace attributes recognize CRLF",
            svg="generated trailing blanks stripped; XML trees verified equal modulo nonsemantic path/text whitespace"),
        tests=tests,
        historical_test_exclusion="test_campaign2_preregistration.py::test_no_confirmatory_execution_result_artifacts_or_frozen_file_changes is a pre-execution-only boundary assertion; preserved unchanged, not weakened",
        frozen_source_hashes_verified=True,preregistration_unchanged=True,C2_unchanged=True,
        historical_results_unchanged=True,physics_inference_policies_scenarios_unchanged=True,
        historical_seeds_in_confirmatory_data=0,new_policies=0,Campaign3_executions=0))
    print(json.dumps(tests),flush=True)


if __name__=="__main__":
    main()
