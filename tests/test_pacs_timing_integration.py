from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNERS = {
    "B2.0": ROOT / "experiments/pilots/b2_pacs_calibration/run.py",
    "B2.1": ROOT / "experiments/pilots/b21_pacs_factorial/run.py",
    "B2.2": ROOT / "experiments/pilots/b22_opportunity_value/run.py",
    "B2.3": ROOT / "experiments/pilots/b23_portfolio_opportunity/run.py",
}


def test_all_pacs_runners_use_common_separate_timing_metadata():
    for name, path in RUNNERS.items():
        source = path.read_text()
        assert "from hls.experiment_timing import ExperimentTimingLogger" in source, name
        assert "state_path=" in source and "experiment_timing.json" in source, name
        assert ".interrupt(RESTART_COMMAND, error)" in source, name


def test_timing_metadata_is_not_written_into_scientific_outputs_or_hashes():
    for name, path in RUNNERS.items():
        source = path.read_text()
        assert '"timing_sha256"' not in source, name
        assert '"experiment_timing.json":' not in source, name


def test_historical_scientific_counts_and_test_guards_remain_present():
    b20 = RUNNERS["B2.0"].read_text()
    b21 = RUNNERS["B2.1"].read_text()
    b22 = RUNNERS["B2.2"].read_text()
    b23 = RUNNERS["B2.3"].read_text()

    assert "base_fractions_for_fast" in b20 and "split_seeds" in b20
    assert '"TEST: governed by the unchanged B2.0 post-selection rule"' in b20
    assert '"fits": 160' in b21 and '"test_used": False' in b21
    assert "TOTAL_UPDATES = len(SEEDS) * len(DOMAINS) * len(N_VALUES)" in b22
    assert "TOTAL_GRID_ROWS = TOTAL_UPDATES * len(COSTS) * len(FUTURE_WEIGHTS)" in b22
    assert "TOTAL_UPDATES != 60 or TOTAL_GRID_ROWS != 1200" in b22
    assert 'choices=("cpu",)' in b22 and '"TEST: CLOSED"' in b22
    assert "TOTAL_FITS = 160" in b23 and "TOTAL_EVALUATIONS = 250" in b23
    assert "TOTAL_PRIMARY_ROWS = 1800" in b23 and "TOTAL_DOSE_ROWS = 450" in b23
    assert 'parser.add_argument("--device", default="cpu")' in b23
    assert "require_cpu(args.device)" in b23 and '"TEST: CLOSED"' in b23


def test_dry_run_loggers_are_non_persistent_and_analyze_only_stays_separate():
    b22 = RUNNERS["B2.2"].read_text()
    b23 = RUNNERS["B2.3"].read_text()
    assert "state_path=None, resume=True, persist=False" in b22
    assert "state_path=None, resume=True, persist=False" in b23
    assert "if args.analyze_only:" in b22
    assert "if args.analyze_only:" in b23
