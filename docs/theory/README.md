# HLS Theory Registry

This directory contains formal results and scoped models. It is not the
current-state document and does not replace the ontology or research doctrine.

## Current canonical theory

- [RQ0 routing integration boundaries](rq0_routing_integration_boundaries.md):
  policy-class inclusion, global reducibility, local routing-as-teaching, and
  the exact C(alpha) existence construction.

## Supporting formal models

- [Minimal HLS model](minimal_hls_model.md): scoped equivalence and
  coordination results.
- [Operational-development opportunity value](operational_development_opportunity_value.md):
  model-scoped opportunity-value identities and portfolio extensions.

Cross-domain theory import is governed by the
[Research Doctrine](../../RESEARCH_DOCTRINE.md), while semantic mappings and
compatibility judgments belong to the [HLS ontology](../hls_ontology.md).

The M0/M0.1 specifications remain supporting model material because their
executable checks still use their equations. The former CIV records were
condensed into [HISTORY](../HISTORY.md); neither branch is a general HLS
theorem or an official research question.

The surviving M0/M0.1 specifications under `docs/models/` are retained only
because the executable `src/hls/m0.py` and `src/hls/m01.py` identify them as
their equation references. They are not part of the active RQ0 theory.
