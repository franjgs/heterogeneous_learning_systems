"""Execute the pre-registered deterministic A1b sweep exactly once."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.a1b import (  # noqa: E402
    OPPORTUNITY_THRESHOLD,
    PHASE_1,
    PHASE_2,
    PHASE_3,
    RHO_STAR,
    run_sweep,
)


RESULT_DIR = ROOT / "results/foundations/a1b_phase_boundary"
PROTOCOL_PATH = ROOT / "docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md"
A1A_PATH = ROOT / "src/hls/a1a.py"
A1B_PATH = ROOT / "src/hls/a1b.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _write_csv(rows: tuple[dict[str, object], ...], path: Path) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _phase_rows(rows: tuple[dict[str, object], ...], phase: str) -> list[dict[str, object]]:
    return [row for row in rows if row["phase"] == phase]


def _write_figures(rows: tuple[dict[str, object], ...]) -> tuple[Path, ...]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figure_paths = []

    coupling = sorted(_phase_rows(rows, PHASE_1), key=lambda row: float(row["rho"]))
    figure, axis = plt.subplots(figsize=(7, 4.5))
    axis.plot(
        [float(row["rho"]) for row in coupling],
        [float(row["Delta_J_cons"]) for row in coupling],
        marker="o",
        markersize=3,
    )
    axis.axvline(float(RHO_STAR), color="black", linestyle="--", label="rho*=50/133")
    axis.axhline(0.0, color="grey", linewidth=0.8)
    axis.set(xlabel="rho", ylabel="Delta_J_cons", title="A1b.1 coupling boundary")
    axis.legend()
    figure.tight_layout()
    path = RESULT_DIR / "a1b1_delta_j_vs_rho.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    figure_paths.append(path)

    development = _phase_rows(rows, PHASE_2)
    eta_values = sorted({float(row["eta"]) for row in development})
    kappa_values = sorted({float(row["kappa"]) for row in development})
    delta = np.empty((len(kappa_values), len(eta_values)))
    margin = np.empty_like(delta)
    by_pair = {
        (float(row["eta"]), float(row["kappa"])): row for row in development
    }
    for kappa_index, kappa in enumerate(kappa_values):
        for eta_index, eta in enumerate(eta_values):
            row = by_pair[(eta, kappa)]
            delta[kappa_index, eta_index] = float(row["Delta_J_cons"])
            margin[kappa_index, eta_index] = float(row["analytical_margin"])
    figure, axis = plt.subplots(figsize=(7, 5))
    image = axis.pcolormesh(eta_values, kappa_values, delta, shading="nearest")
    if margin.min() <= 0.0 <= margin.max():
        axis.contour(
            eta_values,
            kappa_values,
            margin,
            levels=[0.0],
            colors="white",
            linewidths=1.2,
        )
    figure.colorbar(image, ax=axis, label="Delta_J_cons")
    axis.set(
        xlabel="eta",
        ylabel="kappa",
        title="A1b.2 development effectiveness/cost boundary",
    )
    figure.tight_layout()
    path = RESULT_DIR / "a1b2_eta_kappa_phase_map.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    figure_paths.append(path)

    opportunity = [
        row
        for row in _phase_rows(rows, PHASE_3)
        if row["configuration_source"] == "cartesian_grid"
    ]
    e_h_values = sorted({float(row["e_h"]) for row in opportunity})
    e_s_values = sorted({float(row["e_s"]) for row in opportunity})
    delta = np.empty((len(e_s_values), len(e_h_values)))
    by_pair = {
        (float(row["e_h"]), float(row["e_s"])): row for row in opportunity
    }
    for e_s_index, e_s in enumerate(e_s_values):
        for e_h_index, e_h in enumerate(e_h_values):
            delta[e_s_index, e_h_index] = float(
                by_pair[(e_h, e_s)]["Delta_J_cons"]
            )
    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.pcolormesh(e_h_values, e_s_values, delta, shading="nearest")
    line_x = np.linspace(0.0, 1.0 - float(OPPORTUNITY_THRESHOLD), 200)
    line_y = line_x + float(OPPORTUNITY_THRESHOLD)
    axis.plot(line_x, line_y, color="white", linewidth=1.2, label="e_s-e_h=20/57")
    figure.colorbar(image, ax=axis, label="Delta_J_cons")
    axis.set(
        xlabel="e_h",
        ylabel="e_s",
        title="A1b.3 opportunity-geometry boundary",
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
    )
    axis.legend()
    figure.tight_layout()
    path = RESULT_DIR / "a1b3_opportunity_geometry_phase_map.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    figure_paths.append(path)

    return tuple(figure_paths)


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
            "section": "21. A1b predefined primitive-parameter phase-boundary sweep",
            "sha256": _sha256(PROTOCOL_PATH),
        },
        "a1a_solver": {
            "path": A1A_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(A1A_PATH),
        },
        "a1b_implementation": {
            "path": A1B_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(A1B_PATH),
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
        "experiment_id": "A1b",
        "kind": "pre_registered_exact_phase_boundary_sweep",
        "status": summary["status"],
        "command": "python experiments/synthetic/a1b/run_sweep.py",
        "repository_commit": _git_output("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git_output("status", "--porcelain")),
        "deterministic": True,
        "seeds": [],
        "tolerance": summary["tolerance"],
        "counts": summary["effective_counts"],
        "protocol": summary["provenance"]["protocol"],
        "code": [
            summary["provenance"]["a1a_solver"],
            summary["provenance"]["a1b_implementation"],
            summary["provenance"]["runner"],
        ],
        "results": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha256(path),
            }
            for path in result_paths
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
