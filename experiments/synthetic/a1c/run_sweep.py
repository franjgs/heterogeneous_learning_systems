"""Execute the pre-registered deterministic A1c sweep exactly once."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.a1c import PHASE_1, PHASE_2, run_sweep  # noqa: E402


RESULT_DIR = ROOT / "results/foundations/a1c_competence_geometry"
PROTOCOL_PATH = ROOT / "docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md"
A1A_PATH = ROOT / "src/hls/a1a.py"
A1C_PATH = ROOT / "src/hls/a1c.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _write_csv(rows: tuple[dict[str, object], ...], path: Path) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _phase_rows(rows: tuple[dict[str, object], ...], phase: str) -> list[dict[str, object]]:
    return [row for row in rows if row["phase"] == phase]


def _write_figures(rows: tuple[dict[str, object], ...]) -> tuple[Path, ...]:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/hls-a1c-matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    phase_1 = sorted(_phase_rows(rows, PHASE_1), key=lambda row: float(row["delta_R"] or 0.0))
    figure, axis = plt.subplots(figsize=(7, 4.5))
    axis.plot(
        [float(row["delta_R"] or 0.0) for row in phase_1],
        [float(row["Delta_J_cons"]) for row in phase_1],
        marker="o",
        markersize=4,
    )
    axis.axhline(0.0, color="grey", linewidth=0.8)
    axis.set(
        xlabel="delta_R",
        ylabel="Delta_J_cons",
        title="A1c.1 present operational competence gap",
    )
    figure.tight_layout()
    phase_1_path = RESULT_DIR / "a1c1_delta_j_vs_delta_r.png"
    figure.savefig(phase_1_path, dpi=160)
    plt.close(figure)

    phase_2 = _phase_rows(rows, PHASE_2)
    c_12_values = sorted({float(row["c_12"]) for row in phase_2})
    c_22_values = sorted({float(row["c_22"]) for row in phase_2})
    delta = np.empty((len(c_22_values), len(c_12_values)))
    by_pair = {(float(row["c_12"]), float(row["c_22"])): row for row in phase_2}
    for c_22_index, c_22 in enumerate(c_22_values):
        for c_12_index, c_12 in enumerate(c_12_values):
            delta[c_22_index, c_12_index] = float(
                by_pair[(c_12, c_22)]["Delta_J_cons"]
            )
    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.pcolormesh(c_12_values, c_22_values, delta, shading="nearest")
    figure.colorbar(image, ax=axis, label="Delta_J_cons")
    axis.set(
        xlabel="c_12",
        ylabel="c_22",
        title="A1c.2 future competence geometry",
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
    )
    figure.tight_layout()
    phase_2_path = RESULT_DIR / "a1c2_future_competence_phase_map.png"
    figure.savefig(phase_2_path, dpi=160)
    plt.close(figure)
    return phase_1_path, phase_2_path


def main() -> None:
    rows, summary = run_sweep()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = RESULT_DIR / "all_configurations.csv"
    summary_path = RESULT_DIR / "summary.json"
    manifest_path = RESULT_DIR / "manifest.json"
    _write_csv(rows, csv_path)
    figure_paths = _write_figures(rows)

    run_path = Path(__file__).resolve()
    summary["provenance"] = {
        "protocol": {
            "path": PROTOCOL_PATH.relative_to(ROOT).as_posix(),
            "section": "22. A1c competence-geometry phase sweep",
            "sha256": _sha256(PROTOCOL_PATH),
        },
        "a1a_solver": {
            "path": A1A_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(A1A_PATH),
        },
        "a1c_implementation": {
            "path": A1C_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(A1C_PATH),
        },
        "runner": {
            "path": run_path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(run_path),
        },
        "deterministic": True,
        "seeds": [],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    result_paths = (csv_path, summary_path, *figure_paths)
    manifest = {
        "schema_version": 1,
        "experiment_id": "A1c",
        "kind": "pre_registered_exact_competence_geometry_sweep",
        "status": summary["status"],
        "command": "python experiments/synthetic/a1c/run_sweep.py",
        "repository_commit": _git_output("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git_output("status", "--porcelain")),
        "deterministic": True,
        "seeds": [],
        "tolerance": summary["tolerance"],
        "counts": summary["effective_counts"],
        "protocol": summary["provenance"]["protocol"],
        "code": [
            summary["provenance"]["a1a_solver"],
            summary["provenance"]["a1c_implementation"],
            summary["provenance"]["runner"],
        ],
        "results": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}
            for path in result_paths
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
