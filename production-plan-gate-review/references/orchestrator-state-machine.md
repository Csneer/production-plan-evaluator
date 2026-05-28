# Gate Review v2 Orchestrator

Use this state machine to keep Gate Review deterministic. Each phase must produce structured facts before the next phase consumes them.

## States

| State | Required output | May continue when |
|---|---|---|
| `S1_INPUT_NORMALIZED` | `normalized_proposal` with goal, current plan, impact, constraints, success criteria, rollback expectation, owner/handoff | Missing fields are explicitly marked as evidence gaps |
| `S2_PATH_DECOMPOSED` | `path_steps` with stable `step_id` values and phases | Every material operator action is represented |
| `S3_EXECUTABILITY_CHECKED` | step-level preconditions, execution detail, expected result, verification, rollback, owner, marker | Each step has either enough detail to judge or `NEED-EVIDENCE` with missing evidence |
| `S4_EVIDENCE_CHECKED` | `evidence_ledger` and step `evidence_refs` | Each key claim has a tier, source, confidence, and impact |
| `S5_ALTERNATIVES_CHECKED` | `alternative_checks` for every `RISK` or `ELEVATE` step | Each high-risk or nonstandard step has native/baseline/industry comparison |
| `S6_DEFICIENCIES_CHAINED` | `deficiency_chains` | Each material deficiency maps to a path step and evidence |
| `S7_ELEVATION_ENTRY_READY` | `elevation_entry` | Blocking steps and what elevation must solve are explicit |

## Hard gates

- Do not mark any step `OK` without evidence references and verification.
- Do not leave a `RISK` or `ELEVATE` step without an alternative check.
- Do not leave a `NEED-EVIDENCE` step without `missing_evidence`.
- Do not output fewer than three deficiency chains when there are at least three path steps, unless the evidence proves there are fewer than three material deficiencies.
- Do not continue to Final Gate handoff when `elevation_entry.elevation_required` is true.

## Degradation rules

- If the proposal lacks enough information to reconstruct the path, return `Need Evidence` and still produce partial `normalized_proposal`, partial `path_steps`, missing evidence, and collection instructions.
- If official or platform-native evidence is unavailable, state the search gap and mark the relevant claim as `NEED-EVIDENCE`; do not silently accept L4 oral claims.
- If the current path may be acceptable only as a non-native exception, mark the relevant step `ELEVATE` and require the Elevation skill to handle exception approval and compensating controls.

## Handoff rules

- Handoff to `production-plan-elevation` when any step is `ELEVATE`, when native/baseline alternatives look safer, or when hard production gates fail.
- Handoff directly to `production-plan-final-gate` only when no elevation is required and the proof package can be collected for final admission.
