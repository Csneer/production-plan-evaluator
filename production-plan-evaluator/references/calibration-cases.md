# Calibration Cases

Use these cases to avoid overfitting the skill to one technology.

## Service lifecycle / process supervision

- Example: Nginx managed through systemd or similar service manager.
- Native baseline: service signals, config checks, unit files, restart/reload semantics, enable/start, main process recognition.
- Typical anti-pattern: wrapper script owns pidfile/start/stop/reload without exception approval.
- Check: control-plane ownership, reload/restart semantics, handoff, rollback, service-native fit.
- Expected verdict: `No-Go / Return to Design` or `Defer` unless exception approval and evidence are strong.

## Database migration / stateful change

- Native baseline: migration tooling, backward-compatible schema, backup/restore, dual-write/backfill/validation, rollback or compensation.
- Typical anti-pattern: DDL/DML steps without lock analysis, backup, rollback, verification, or RTO/RPO.
- Check: data consistency, rollback proof, rehearsal, monitoring, owner.
- Expected verdict: missing rollback is `No-Go`; missing evidence is `Defer / Need Evidence`.

## Kubernetes rollout / traffic and probes

- Native baseline: Deployment rollout, readiness/liveness/startup probes, rolling update, PDB, service selector, ingress/gateway, metrics and alerting.
- Typical anti-pattern: direct traffic cutover while bypassing probes and automated health gates.
- Check: platform-native rollout, health signal, rollback command, traffic/error-rate observability.
- Expected verdict: oral claim only is `Defer`; justified exception may be `Conditional Go`.

## Certificate / permission / security rotation

- Native baseline: cert manager or key rotation workflow, least privilege, audit logs, expiry alerting, staged replacement.
- Typical anti-pattern: manual secret replacement with no rollback window, no audit, unclear owner, or widened permissions.
- Check: permission boundary, auditability, rollback, expiry/failure alerting, owner and review date.
- Expected verdict: unclear audit or owner is `No-Go` or `Conditional Go` with proof conditions.

## Test matrix expectations

Cover all Final Gate verdicts: `Go`, `Conditional Go`, `No-Go`, and `Defer`. Cover both Layer 2 triggered and not triggered. The skill must not approve a plan with insufficient evidence, missing rollback, missing owner, or unapproved non-native deviation.
