# Calibration Cases

Use these cases to avoid overfitting Gate Review to one technology or accepting AI-generated implementation steps at face value.

## Service lifecycle / process supervision

- Example: Nginx, Java service, or agent process managed through systemd, supervisord, Kubernetes, or a platform service manager.
- Native baseline: service manager ownership, reload/restart semantics, config validation, unit or workload definition, main process recognition, health checks, enable/start behavior.
- Typical anti-pattern: wrapper script owns pidfile/start/stop/reload without exception approval.
- Gate Review focus: control-plane ownership, operator commands, reload safety, rollback, handoff, audit trail, and service-native fit.
- Expected Gate result: `ELEVATE` or `NEED-EVIDENCE` unless the non-native path has proof, owner, rollback, and exception rationale.

## Database migration / stateful change

- Native baseline: migration tooling, backward-compatible schema, backup/restore, dual-write or expand-contract where needed, backfill validation, rollback or compensation.
- Typical anti-pattern: DDL/DML steps without lock analysis, backup, rollback, verification, rehearsal, or RTO/RPO.
- Gate Review focus: data consistency, irreversible operation, lock impact, validation query, backup proof, restore proof, monitoring, and owner.
- Expected Gate result: missing rollback or backup proof becomes `NEED-EVIDENCE` or `ELEVATE`; proven unsafe path returns to author for rework.

## Kubernetes rollout / traffic and probes

- Native baseline: Deployment rollout, readiness/liveness/startup probes, rolling update strategy, PDB, service selector, ingress/gateway, metrics and alerting.
- Typical anti-pattern: direct traffic cutover while bypassing probes and automated health gates.
- Gate Review focus: platform-native rollout, health signal, rollback command, traffic/error-rate observability, and cutover verification.
- Expected Gate result: L4-only health claims become `NEED-EVIDENCE`; bypassing rollout primitives requires `ELEVATE`.

## Certificate / permission / security rotation

- Native baseline: certificate manager or key rotation workflow, least privilege, audit logs, expiry alerting, staged replacement, owner and review date.
- Typical anti-pattern: manual secret replacement with no rollback window, no audit, unclear owner, or widened permissions.
- Gate Review focus: permission boundary, blast radius, auditability, rollback, expiry/failure alerting, owner, risk acceptor, and handoff.
- Expected Gate result: unclear audit or owner becomes `NEED-EVIDENCE`; widened privilege without compensating controls becomes `ELEVATE`.

## Calibration expectations

- Gate Review must challenge executability, not just list generic risks.
- Gate Review must compare current steps with native or mainstream alternatives before asking Elevation to design the replacement.
- Gate Review must not approve final production execution.
