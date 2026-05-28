---
name: production-plan-final-gate
description: Use when making an independent final production admission decision for an implementation plan after Gate Review v2 and any Elevation work, focusing only on Go, Conditional Go, No-Go, or Defer verdicts, not initial path review or alternative design.
---

# Production Plan Final Gate

## Core intent

Make the independent final production admission decision. This skill must judge readiness from evidence, the Gate Review v2 Structured Gate Record, and any Elevation report; it must not redo the initial path review, redesign the solution, or create new elevated alternatives during the approval step.

## Use when

- The user asks for最终准入、上线把关、Go/No-Go、Conditional Go、生产变更批准, or final change gate.
- A Gate Review v2 Structured Gate Record exists and either an Elevation report exists or Gate Review explicitly says no elevation is required.
- The decision affects production, service lifecycle, rollout, migration, traffic, data, certificates, permissions, or infrastructure.

Do not use this skill for initial review or alternative design. If design is still needed, return to `production-plan-gate-review` or `production-plan-elevation`.

## Required inputs

- Original proposal or final candidate plan.
- Gate Review v2 Structured Gate Record with `path_steps`, `evidence_ledger`, `alternative_checks`, `deficiency_chains`, `gate_checks`, and `elevation_entry`.
- Elevation report, or explicit Gate Review rationale for no elevation.
- Proof package: command output, monitoring evidence, rehearsal record, change-ticket link, config diff, owner/risk acceptance, and rollback proof where relevant.

If required inputs are missing, return `Defer / Need Evidence` rather than filling gaps with design assumptions.

## Non-negotiable rules

- **No design in Final Gate.** Do not create or modify the solution while judging it.
- **Consume Gate v2, do not redo it.** Treat the Structured Gate Record as the path-risk source of truth; return to Gate Review if path reconstruction is missing or invalid.
- **Hard gates override scores.** Missing rollback, observability, owner, audit, approval, or exception acceptance blocks `Go`.
- **Evidence controls verdict.** `Go` or `Conditional Go` requires sufficient evidence, normally L1/L2 plus L3 for key claims.
- **Conditions must be provable.** Every `Conditional Go` condition needs proof form, owner, and deadline.
- **Always compare now vs defer.** The final decision must explicitly explain why executing now is or is not better than waiting.

## Allowed verdicts

- `Go` — evidence is sufficient, hard gates pass, and residual risk is owned.
- `Conditional Go` — execution may proceed only after explicit conditions are met.
- `No-Go / Return to Design` — hard gates fail or the candidate is not production-ready.
- `Defer / Need Evidence` — evidence is insufficient, stale, missing, or conflicting.

## Workflow

1. Confirm required inputs exist, including a Gate Review v2 Structured Gate Record. If not, return `Defer / Need Evidence`.
2. Read `references/final-gate-checklist.md` and evaluate each hard gate.
3. Reconcile Gate Review findings, Elevation recommendation, exception approvals, and proof package.
4. Compare current execution, recommended candidate, and defer/no-change.
5. Decide one allowed verdict only.
6. For `Conditional Go`, list conditions with proof form, owner, and deadline.
7. For `No-Go / Return to Design`, name the failed hard gates and where to return: Gate Review or Elevation.

## Output contract

Return this report shape in Chinese by default:

```markdown
# Final Gate Report

## Verdict
Go / Conditional Go / No-Go / Return to Design / Defer / Need Evidence

## One-line Rationale
...

## Input Completeness
| Required input | Present? | Evidence/source | Impact |

## Gate v2 Structured Record Status
| Field | Present? | Blocking issue | Verdict impact |

## Hard Gate Checklist
| Gate | Pass? | Evidence | Blocking issue | Verdict impact |

## Now vs Defer Comparison
| Option | Benefit | Risk | Evidence | Decision impact |
| Execute now | | | | |
| Defer / no-change | | | | |

## Conditions and Proof Forms
| Condition | Proof form | Owner | Deadline | Blocks execution? |

## Residual Risk and Ownership
- Residual risks:
- Owner:
- Risk acceptor:
- Observation window:
- Handoff target:

## Return Path
- If Go: execution package accepted:
- If Conditional Go: conditions that must be satisfied before execution:
- If No-Go: return to Gate Review or Elevation with reasons:
- If Defer: missing evidence and how to collect it:
```

## Boundaries

- Do not add new candidate designs.
- Do not downgrade missing evidence into a minor note.
- Do not issue `Go` for non-native exceptions without explicit owner, risk acceptor, compensating controls, and review date.
