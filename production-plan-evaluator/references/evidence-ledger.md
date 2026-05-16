# Evidence Ledger Contract

## Evidence tiers

| Tier | Meaning | Examples |
|---|---|---|
| L1 | Official, platform, vendor, or distribution documentation | official docs, platform docs, distro default unit/chart/config |
| L2 | Internal production standard | SRE runbook, production baseline, change policy, incident postmortem decision |
| L3 | Environment fact | command output, current config, runtime state, metrics, logs, rehearsal record, change ticket |
| L4 | Experience or oral claim | operator memory, author statement, team habit |

## Minimum evidence

- `Go` / `Conditional Go`: key claims need L1 or L2 plus at least one L3 environment fact.
- `No-Go / Return to Design`: the blocking claim needs high-confidence evidence or an explicit hard gate failure.
- `Defer / Need Evidence`: use when evidence is missing, stale, conflicting, or only L4.

## Conflict handling

- L1/L2 overrides L4 unless L3 environment facts explain why this environment differs.
- If official guidance and internal baseline conflict, report both and require owner/risk acceptance before Go.
- Record version, environment, and collection date for key evidence.

## Ledger template

| Claim | Tier | Source | Version/environment/date | Summary | Confidence | Verdict impact |
|---|---|---|---|---|---|---|
