# Production Plan Evaluator

A Codex skill for reviewing and elevating already-proposed production implementation plans before execution.

It is designed for cases where a plan may be technically workable but risky for production because it is nonstandard, hard to maintain, weakly evidenced, difficult to roll back, or misaligned with service/platform-native operations.

## What it does

The skill evaluates an existing implementation plan through three layers:

1. **Gate Review** — normalize the proposal, expose assumptions, compare against official/industry/native practices, and identify deficiencies.
2. **Elevation** — when risk or nonstandard design warrants it, produce a more production-ready alternative.
3. **Final Gate** — independently decide `Go`, `Conditional Go`, `No-Go`, or `Defer / Need Evidence`.

## When to use

Use it before production changes such as:

- service lifecycle / process supervision changes
- migrations and stateful changes
- Kubernetes rollouts and traffic cutovers
- certificate, permission, and security rotations
- zero-downtime or high-risk infrastructure changes
- AI-generated implementation proposals that need production review

## Install

Copy the skill directory into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R production-plan-evaluator ~/.codex/skills/
```

Then start a new Codex session so the skill metadata is loaded.

## Structure

```text
production-plan-evaluator/
  SKILL.md
  references/
    evidence-ledger.md
    exception-template.md
    calibration-cases.md
```

## Verification

Run the contract tests:

```bash
python3 -m pytest tests/test_production_plan_evaluator_skill.py -q
```

The tests validate the skill discovery metadata, three-layer workflow, evidence contract, exception governance, calibration cases, and absence of auxiliary documentation clutter.

## License

No license has been selected yet. Until a license is added, all rights are reserved by default.
