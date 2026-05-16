---
name: production-plan-evaluator
description: Use when reviewing an already-proposed production implementation, operations, migration, rollout, service-management, zero-downtime, or infrastructure change plan before execution, especially when it may be AI-generated, nonstandard, hard to maintain, weakly evidenced, or risky to operate.
---

# Production Plan Evaluator

## Core intent

Evaluate an existing implementation plan before production execution. Do not start by designing from scratch. Normalize the proposal, challenge it with evidence, elevate it only when warranted, then keep final production Go/No-Go independent from solution design.

## Use when

- A user already has a draft implementation or operations plan.
- The plan affects production, service lifecycle, rollout, migration, traffic, data, certificates, permissions, or infrastructure.
- The proposed path may be clever but nonstandard, hard to hand over, weakly evidenced, or based on AI output.
- The user asks for方案评估, 升维, 最终把关, industry practice, official practice, service-native practice, rollback, maintainability, or production readiness.

Do not use for greenfield architecture unless the user first provides a candidate plan to review.

## Non-negotiable principles

- **No evidence, no final verdict.** If evidence is insufficient, return `Defer / Need Evidence`.
- **Can run is not enough.** Production plans must be maintainable, observable, reversible, and owned.
- **Service-native and platform-native first.** Deviations are allowed only with exception approval and compensating controls.
- **Final Gate must stay independent.** The final gatekeeper must not design a new solution during the approval step.
- **Hard gates override scores.** A good total score cannot offset missing rollback, observability, owner, audit, or exception approval.

## Quick evidence and exception reference

Evidence tiers: `L1` official/platform/distribution documentation, `L2` internal production baseline or SRE runbook, `L3` environment fact, `L4` experience or oral claim. Production `Go` normally needs L1/L2 plus L3. Non-native exceptions must name compensating controls, owner, and review date.

## Workflow

### Layer 1 — Gate Review

Goal: decide whether the existing plan is ready for further design/review and whether it triggers elevation.

1. Normalize inputs:
   - goal and success criteria
   - current proposal
   - production impact and downtime tolerance
   - environment/version/deployment facts
   - rollback expectation
   - owner and handoff expectations
2. Decompose the plan across control, data/state, cutover, failure, operations, and audit surfaces.
3. Compare with official, industry, service-native, platform-native, and internal baseline practices.
4. Produce at least three deficiencies with consequence chains. Cover standardness, maintainability, operational risk, observability, and ownership where relevant.
5. Build an Evidence Ledger. For evidence rules, read `references/evidence-ledger.md` when the case is production, high-risk, disputed, or externally dependent.
6. Decide whether Layer 2 is triggered.

Layer 2 triggers when any apply:
- production or zero-downtime change
- migration, service lifecycle, traffic, data, security, certificate, permission, or compliance change
- any hard gate fails
- the proposal bypasses existing service/platform-native mechanisms without written justification
- maintainability or handoff risk is high
- the user asks to elevate, compare industry options, or perform final gatekeeping
- evidence suggests a safer or more standard mainstream path

### Layer 2 — Elevation

Goal: generate a better production-ready alternative when triggered. Do not merely criticize.

For each elevated option include:
- name and core idea
- native/industry mechanism it aligns with
- evidence source
- cutover path
- rollback path
- observability and verification
- owner/handoff implications
- new costs and constraints
- applicability boundaries

If keeping a non-native or nonstandard proposal, require exception approval. Use `references/exception-template.md`.

### Layer 3 — Final Gate

Goal: make the independent Go/No-Go decision. The Final Gate must not design a new solution; if design is still needed, return to Layer 1 or Layer 2.

Allowed verdicts:
- `Go` — evidence is sufficient, hard gates pass, residual risk is owned.
- `Conditional Go` — execution may proceed only after explicit conditions are met.
- `No-Go / Return to Design` — hard gates fail or the plan is not production-ready.
- `Defer / Need Evidence` — evidence is insufficient or conflicting.

Final Gate must compare now vs defer even when Layer 2 is not triggered. At minimum compare:
- current proposal
- elevated option if any
- do nothing / defer for evidence or rehearsal

For `Conditional Go`, every condition must include proof form, owner, and deadline. Proof forms include command output, monitoring screenshot, rehearsal record, change-ticket link, config diff, or owner confirmation.

## Output contract

Return a structured report:

```markdown
# Production Plan Evaluation and Elevation Report

## Verdict
Go / Conditional Go / No-Go / Defer

## One-line rationale
...

## Normalized proposal
- Goal:
- Current plan:
- Constraints:
- Success criteria:
- Rollback expectation:

## Evidence Ledger
| Claim | Evidence tier | Source | Confidence | Impact |

## Key deficiencies
1. Deficiency / evidence / production consequence / mitigation
2. ...
3. ...

## Principle → Gate → Verdict mapping
| Principle | Observed fact/evidence | Satisfied? | Verdict impact |

## Alternatives considered
| Option | Score/gates | Why accepted or rejected |
| Current proposal | | |
| Native/baseline option | | |
| Defer/no-change | | |

## Elevation result
Triggered / not triggered, with reason.

## Elevated option
Include only if triggered.

## Exception approval
Include if retaining a non-native/nonstandard plan.

## Final Gate
- Verdict:
- Hard gate status:
- Remaining risk:
- Owner/risk acceptor:
- Conditions and proof forms:
```

## Calibration

For cross-domain calibration and pressure scenarios, read `references/calibration-cases.md` before judging broad production plans or when you suspect the case is being overfit to one technology.
