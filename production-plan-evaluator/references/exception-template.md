# Non-native Exception Approval Template

Use this when a plan keeps a non-native, nonstandard, wrapper-based, manual, or otherwise surprising implementation path.

```markdown
## Exception approval

- Reason for deviation:
- Constraint source:
- Why the native/baseline path is unavailable or riskier:
- Compensating controls:
- Rollback proof:
- Monitoring/alerting compensation:
- Operational handoff:
- owner:
- risk acceptor:
- review date:
- expiry date:
- plan to return to native/baseline path:
```

A missing exception approval blocks Final Gate `Go` when the plan deviates from service-native, platform-native, official, or internal baseline practice.
