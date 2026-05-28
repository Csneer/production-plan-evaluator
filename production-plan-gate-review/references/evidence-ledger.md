# Evidence Ledger Contract

## Evidence tiers

| Tier | Meaning | Examples |
|---|---|---|
| L1 | Official, platform, vendor, or distribution documentation | official docs, platform docs, distro default unit/chart/config |
| L2 | Internal production standard | SRE runbook, production baseline, change policy, incident postmortem decision |
| L3 | Environment fact | command output, current config, runtime state, metrics, logs, rehearsal record, change ticket |
| L4 | Experience or oral claim | operator memory, author statement, team habit |

## Minimum evidence

- Step-level confidence normally needs L1 or L2 plus at least one L3 environment fact.
- `Need Evidence` applies when evidence is missing, stale, conflicting, or only L4.
- If L1/L2 conflicts with L3, report both and explain why the environment differs.

## Ledger template

| Claim | Tier | Source | Environment/date | Summary | Confidence | Impact |
|---|---|---|---|---|---|---|
