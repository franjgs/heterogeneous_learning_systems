# HLS Role Register

**Status:** Operational governance record. This register does not summarize
scientific results; consult the repository authority map for scientific state.

**Initialization note:** at register creation, repository sources did not
establish named identities. The PI's explicit 2026-10-19 governance decision
now identifies the outgoing and incoming CE for the pending transfer below;
the PI and expert identities remain uninitialized.

| Role | Status | Responsible identifier | Baseline commit | Latest accepted handover | Source of mission / authority |
| --- | --- | --- | --- | --- | --- |
| PI | ACTIVE | UNKNOWN / TO BE INITIALIZED | `2912ca3b9a40961d98010a76c87f8464555ed04e` | None — register initialized | PI authority as recorded in [Team Handover Protocol](HLS_TEAM_HANDOVER_PROTOCOL.md) |
| Chief Engineer — outgoing | OUTGOING | Previous ChatGPT instance coordinating HLS | `e6ad5a80e31986610bd2b597d3a4078c11d2b5f4` | [2026-10-19 REPLACE CE handover](handovers/2026-10-19_replace_chief_engineer.md) — pending acceptance; supersedes 2026-10-05 transfer | [Team Handover Protocol §8](HLS_TEAM_HANDOVER_PROTOCOL.md#8-replace-chief-engineer) |
| Chief Engineer — incoming | PENDING | Current GPT-6 instance in this conversation | `e6ad5a80e31986610bd2b597d3a4078c11d2b5f4` | [2026-10-19 REPLACE CE handover](handovers/2026-10-19_replace_chief_engineer.md) — pending acceptance; supersedes 2026-10-05 transfer | [Team Handover Protocol §8](HLS_TEAM_HANDOVER_PROTOCOL.md#8-replace-chief-engineer) |
| Expert / Beam Owner | VACANT | No named role record — TO BE INITIALIZED | `2912ca3b9a40961d98010a76c87f8464555ed04e` | None — register initialized | Scope assigned by PI or CE under the protocol |
| Handover Steward | ACTIVE | Codex-equivalent operational steward; appointment identity TO BE INITIALIZED | `2912ca3b9a40961d98010a76c87f8464555ed04e` | None — register initialized | [Team Handover Protocol](HLS_TEAM_HANDOVER_PROTOCOL.md) |

Permitted statuses are: **ACTIVE**, **OUTGOING**, **PENDING**, **VACANT**,
**FROZEN**, and **REPLACED**. Do not change a status without the corresponding
handover operation and confirmation defined in the protocol.
