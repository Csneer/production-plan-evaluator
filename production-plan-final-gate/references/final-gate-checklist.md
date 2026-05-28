# Final Gate Checklist

Hard gates must pass for `Go`. Any failed hard gate requires `Conditional Go`, `No-Go / Return to Design`, or `Defer / Need Evidence`.

| Gate | Required proof |
|---|---|
| Scope and target clear | final candidate plan, affected systems, change window |
| Evidence sufficient | L1/L2 baseline plus L3 environment proof for key claims |
| Rollback proven | rollback steps, expected state, validation command, owner |
| Observability ready | metrics/logs/health checks, alert owner, observation window |
| Ownership assigned | operator, approver, risk acceptor, handoff target |
| Audit trail present | ticket/change record, config diff, approval record |
| Exception approved | compensating controls, review date, expiry date when non-native |
| Now vs defer justified | execution-now benefit outweighs waiting, or defer selected |

`Conditional Go` conditions must include proof form, owner, and deadline.
