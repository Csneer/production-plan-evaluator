# Production Plan Review Skills

Three focused Codex skills for deep production-change review. They keep each stage strict, evidence-led, and non-superficial.

## Skills

1. **`production-plan-gate-review`** — reconstructs the actual implementation path, checks step executability, compares native/industry alternatives, emits a Gate v2 structured record, and decides whether elevation is required.
2. **`production-plan-elevation`** — turns Gate v2 blockers into production-ready candidate paths, with cutover, rollback, observability, ownership, and exception handling.
3. **`production-plan-final-gate`** — independently decides `Go`, `Conditional Go`, `No-Go / Return to Design`, or `Defer / Need Evidence` from the Gate v2 record, prior elevation artifacts, and proof.

## Recommended workflow

Run the skills in order:

```text
Draft plan
  -> production-plan-gate-review
  -> production-plan-elevation, if Gate Review says elevation is required
  -> production-plan-final-gate
```

Do not ask one skill to complete all three stages. The skills intentionally do not include a routing or compatibility wrapper because the old combined flow encouraged shallow one-pass reviews.

## Install

Copy the skill directories into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R production-plan-gate-review ~/.codex/skills/
cp -R production-plan-elevation ~/.codex/skills/
cp -R production-plan-final-gate ~/.codex/skills/
```

Start a new Codex session so the skill metadata is loaded.

## Structure

```text
production-plan-gate-review/
  SKILL.md
  gate-review-SOP.md
  scripts/
    validate_gate_record.py
  references/
    calibration-cases.md
    evidence-ledger.md
    orchestrator-state-machine.md
    path-canvas-template.md
production-plan-elevation/
  SKILL.md
  production-plan-elevation-SOP.md
  references/
    elevation-options-template.md
    exception-template.md
production-plan-final-gate/
  SKILL.md
  references/
    evidence-ledger.md
    final-gate-checklist.md
```

## Gate v2 record

`production-plan-gate-review` emits a structured Gate v2 record so downstream skills can reason from explicit data rather than prose summaries. The record must include normalized inputs, path steps, evidence ledger items, alternative checks, deficiency chains, and elevation status.

Use the local validator before handing a Gate v2 record to the next stage:

```bash
python production-plan-gate-review/scripts/validate_gate_record.py path/to/gate-record.json
```

## Verification

Run the contract tests:

```bash
python -m pytest -q
```

The tests validate the three independent skill contracts, Gate v2 structured record requirements, validator behavior, downstream role boundaries, reference files, and removal of the old combined evaluator skill.

## License

No license has been selected yet. Until a license is added, all rights are reserved by default.
