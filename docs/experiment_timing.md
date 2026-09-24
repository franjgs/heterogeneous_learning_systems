# Common experiment timing logger

Long-running project runners use
`hls.experiment_timing.ExperimentTimingLogger`. It prints one shared format for
headers, phases, item start/completion, internal units, ETA, interruption, and
final timing summaries. Durations use `time.perf_counter()`; `datetime` is used
only for readable timestamps.

Minimal usage:

```python
from hls.experiment_timing import ExperimentTimingLogger

timing = ExperimentTimingLogger(
    "Experiment name",
    total_items=20,
    planned_counts={"base": 4, "update": 16},
    state_path=output_dir / ".cache/experiment_timing.json",
    resume=True,
)
timing.header(["Device: CPU", "TEST: CLOSED"])
timing.phase(1, 2, "Training")
timing.start_item("base_seed0", "base", 1, "seed=0 state=base")
# work; use timing.item_progress(...) at epochs or other natural units
timing.finish_item()
timing.finish()
```

Use `persist=False` for dry-runs. On restart, call `adopt_completed` only for
an artifact whose scientific provenance has already been validated. Reused
items contribute valid historical duration but consume zero session time.
Record analysis or other non-fit work with `record_auxiliary`.

Timing lives in a separate `.cache/experiment_timing.json`. It is operational
metadata and must never enter model, dataset, opportunity, or scientific
equivalence hashes. If old artifacts contain no valid duration, report their
historical timing as unavailable rather than reconstructing it.
