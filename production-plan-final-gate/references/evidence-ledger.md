# Evidence Ledger Contract

## Evidence tiers

| Tier | Meaning | Examples |
|---|---|---|
| L1 | Official, platform, vendor, or distribution documentation | official docs, platform docs, distro default unit/chart/config |
| L2 | Internal production standard | SRE runbook, production baseline, change policy, incident postmortem decision |
| L3 | Environment fact | command output, current config, runtime state, metrics, logs, rehearsal record, change ticket |
| L4 | Experience or oral claim | operator memory, author statement, team habit |

## Final gate minimum evidence

- `Go` normally requires L1 or L2 plus L3 for key operational claims.
- `Conditional Go` requires every missing item to have proof form, owner, and deadline.
- `Defer / Need Evidence` is mandatory when evidence is missing, stale, conflicting, or only L4 for a hard gate.
- `No-Go / Return to Design` applies when evidence proves a hard gate fails or the candidate remains unready.
