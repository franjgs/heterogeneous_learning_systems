# SOCTRA–HLS availability robustness

Isolated synthetic extension studying L2 availability calendars and natural-time deadlines. It does not reproduce the GMV-CERT SOC, claim GMV service levels, change SOCTRA, alter D1/P1/WAPS, or rewrite historical campaigns.

The source RQ1 allocation dispatchers and the previous study's synthetic trace generation are reusable. `availability_engine.py` provides the separate preempt-and-resume clock needed for duty schedules. A job interrupted at shift end retains its analyst and completed service; it resumes at the next available interval. No handoff or new dispatch decision occurs for that job. New work is not started while unavailable.

The pilot specification is in `config/pilot.json`. Absolute simulation time starts Monday 00:00; deadlines are synthetic natural-hour offsets from original alert arrival: High 12 h, Medium 24 h, Low 72 h. The 24x7 versus weekday 09:00–17:00 comparison includes the intended reduction in weekly capacity. There is no terminal drain in deadline accounting.

Run technical checks with `pytest studies/soc_triage_hls_availability_robustness/tests`. Campaign outputs belong under `results/soc_triage_hls_availability_robustness/`; no historical result path is read for writing.
