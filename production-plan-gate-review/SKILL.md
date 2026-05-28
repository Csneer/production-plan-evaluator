---
name: production-plan-gate-review
description: Use when reviewing an existing AI-generated or human-written production implementation, migration, rollout, service-management, traffic, certificate, permission, or infrastructure change plan before redesign or approval; reconstruct the execution path, verify step executability, attach evidence, compare native/industry alternatives, and decide whether elevation is required. Do not use for final Go/No-Go approval or for designing the replacement plan.
---

# Production Plan Gate Review

## Core intent

Review an already-proposed production plan at the execution-path level. This is the core skill in the suite: if it fails to find path, evidence, or alternative-design problems, later elevation and final gatekeeping become unreliable.

Do not redesign the solution and do not issue a final Go/No-Go verdict. The output must make the real operator journey visible, attach evidence to claims, compare risky steps against native or mainstream alternatives, and identify exactly which steps require elevation, more evidence, or author rework.

## Use when

- The user has a draft production implementation, migration, rollout, service-management, traffic, certificate, permission, or infrastructure change plan.
- The user asks for方案评审、路径复盘、实施风险、证据检查、缺陷定位、是否需要升维, industry practice, service-native practice, platform-native practice, or pre-approval review.
- The plan may be AI-generated, nonstandard, weakly evidenced, hard to execute, hard to operate, hard to roll back, or hard to hand over.

Do not use this skill to design the elevated replacement or make final production admission decisions. Send those to `production-plan-elevation` or `production-plan-final-gate`.

## Non-negotiable rules

- **Path first.** Always reconstruct the actual implementation path before judging quality.
- **Full enumeration before judgment.** Before any quality assessment, extract ALL steps from the original proposal verbatim into a numbered source list. This list is the ground truth. Path decomposition must account for every item; steps cannot be silently merged or dropped.
- **Step executability first — minimum standard enforced.** Every material step is only executable if ALL of the following are present and non-vague:
  - `execution_detail`: 包含具体命令、配置项或制品名称，禁止"按正常流程执行"、"参考文档操作"等无操作性表述
  - `verification`: 命名具体指标、命令输出或可观测状态，禁止"确认服务正常"、"观察运行情况"
  - `rollback`: 包含触发条件 + 操作序列 + 预计恢复时长，禁止"回滚到上一版本"
  - `owner`: 指定具体角色或团队名称，禁止"相关负责人"
  缺少任意一项，该步骤不得标记为 `OK`，必须标记为 `GAP` 或 `NEED-EVIDENCE`。
- **No evidence, no confidence.** If key claims lack evidence, mark them `NEED-EVIDENCE`.
- **No evidence-backed check, no OK.** Never mark a step `OK` unless it has evidence references and a concrete verification method.
- **No skipped alternatives — web search required.** Every `RISK` or `ELEVATE` step must include a native, baseline, or industry alternative check. The `evidence_basis` field of every AlternativeCheck must contain at least one URL sourced from a live web search performed during this review, plus the search date. Entries citing only training knowledge must be marked `[TRAINING-ONLY — web search pending]` and treated as L4 evidence.
- **No final admission.** Never output `Go`, `Conditional Go`, `No-Go`, or final approval as the verdict of this skill.
- **Findings must attach to steps.** Every material deficiency must point to a concrete path step and finding ID.
- **Depth first.** Prefer a complete evidence-backed review over a short summary. Any field containing "根据实际情况"、"视环境而定"、"参考官方文档" or equivalent vague filler is automatically invalid and must be flagged.

## Required references

- Read `references/orchestrator-state-machine.md` before producing the report. Follow its phases and gate conditions.
- Read `references/evidence-ledger.md` for evidence tiers and minimum evidence rules.
- Read `references/path-canvas-template.md` when the plan has more than three steps, optional execution, branches, rollback, or handoff.
- Read `references/calibration-cases.md` for broad production cases, especially service lifecycle, database migration, Kubernetes rollout, and certificate or permission rotation.

## Gate v2 workflow

Run these phases in order. Do not collapse them into a generic risk summary.

### Phase 0 — 原始步骤全量提取（强制，不可跳过）

从原始方案中逐字提取所有步骤，输出源清单：

| 原始序号 | 原文步骤描述 | 来源位置（段落/章节） |

规则：
- 必须逐行列出，不得合并相似步骤
- 若原始方案无明确步骤编号，按文本顺序自行编号
- 此清单的行数是后续 Path Decomposition 的下界：`path_steps` 条目数必须 ≥ 原始步骤数（允许拆分隐含步骤使其增多，不允许合并导致减少）
- 若发现原始方案某段文字隐含多个操作，在此阶段标注，并在 Phase 2 拆分为独立 step_id

### Phase 1 — Input normalization

Extract goal, current plan, production impact, constraints, success criteria, rollback expectation, owner, and handoff expectation. Missing critical inputs become `NEED-EVIDENCE`; do not invent them.

### Phase 2 — Path decomposition

Reconstruct the operator journey from pre-check through preparation, execution or cutover, verification, rollback, observation, and handoff. Assign every step a stable `step_id`.

覆盖验证：Phase 2 结束后，对照 Phase 0 源清单，确认每个原始步骤在 path_steps 中有对应条目（直接对应或拆分后对应）。若有原始步骤无对应 step_id，必须在 Path Findings Map 中注明原因，不得静默省略。

### Phase 3 — Executability check

For every step, verify against the minimum executability standard defined in Non-negotiable rules. Steps that do not meet the standard must be marked `GAP` or `NEED-EVIDENCE`, never `OK`.

### Phase 4 — Evidence check

Build an Evidence Ledger. Key claims need L1 or L2 plus L3 when possible. L4-only claims cannot support `OK`. Evidence sourced from training knowledge without live verification must be marked `L4` even if the model is confident.

### Phase 5 — Alternative/baseline check with mandatory web search

For every step marked `RISK` or `ELEVATE`, and for any step using a nonstandard, manual, wrapper-based, or weakly evidenced approach:

**Step 5a（强制联网核查，每个目标步骤执行一次）：**

对每个需做 AlternativeCheck 的步骤，执行以下搜索，并将结果写入 `evidence_basis`：

1. 官方/主流文档当前推荐做法
   - 示例：`[service/tool name] production best practice [year] site:[vendor].com/docs`
2. 近12个月是否有 deprecation、breaking change 或重大更新
   - 示例：`[step mechanism] deprecated OR breaking change 2024 OR 2025`
3. 是否有已知 CVE、运维事故案例或社区告警
   - 示例：`[step mechanism] CVE OR incident OR outage 2024`

`evidence_basis` 字段格式要求：
- 每条来源注明 URL + 搜索时间
- 若搜索无结果，注明"已搜索，未找到相关文档，搜索词：…，时间：…"
- 禁止以"行业通行做法"、"业界普遍认为"等无来源表述填充

**Step 5b：** Based on web search results, compare current method with service-native, platform-native, distribution-native, internal baseline, or industry-standard options. Fill all AlternativeCheck contract fields.

### Phase 6 — Deficiency chains

Produce at least three deficiency chains unless the proposal has fewer than three path steps. Each chain must follow the structure:

`finding_id` → `step_id` → `defect`（具体缺陷，不得写"该步骤有风险"） → `evidence_refs`（指向 Evidence Ledger 中的具体 evidence_id） → `production_consequence`（生产后果，量化影响或失效场景） → `required_fix_or_proof`（具体修复或证明要求，可操作粒度）

禁止在 deficiency_chains 中使用"需进一步评估"、"建议加强"等无操作性结论。

### Phase 7 — Elevation entry

Decide `Elevation Required?` using only Gate Review evidence. Name the blocking path steps and what elevation must solve.

---

## Structured Gate Record

The report must include a fenced JSON block named `Structured Gate Record`. Use stable English field names so downstream skills and `scripts/validate_gate_record.py` can validate it.

Required top-level fields:

```json
{
  "schema_version": "gate-review.v2",
  "normalized_proposal": {},
  "path_steps": [],
  "evidence_ledger": [],
  "alternative_checks": [],
  "deficiency_chains": [],
  "gate_checks": [],
  "elevation_entry": {}
}
```

### PathStep contract

Every item in `path_steps` must include:

- `step_id`
- `phase`: `precheck`, `prepare`, `execute`, `verify`, `rollback`, `observe`, or `handoff`
- `action`
- `preconditions`
- `execution_detail`（必须包含具体命令、配置项或制品名称；不可填"按正常流程"）
- `expected_result`
- `verification`（必须命名具体指标、命令输出或可观测状态；不可填"确认正常"）
- `rollback`（必须包含触发条件 + 操作序列 + 预计恢复时长；不可填"回滚上一版本"）
- `owner`（必须指定具体角色或团队；不可填"相关负责人"）
- `evidence_refs`
- `marker`: `OK`, `GAP`, `RISK`, `ELEVATE`, or `NEED-EVIDENCE`
- `finding_refs`
- `source_step_ref`（对应 Phase 0 源清单的原始序号，用于覆盖追踪）

In human-readable tables and diagrams, render markers as `[OK]`, `[GAP]`, `[RISK]`, `[ELEVATE]`, and `[NEED-EVIDENCE]`. In JSON, use the bare enum values.

Conditional requirements:

- `OK` requires non-empty `evidence_refs` and a concrete `verification` that meets the minimum standard above.
- `RISK` and `ELEVATE` require non-empty `finding_refs`, a `alternative_checks` entry for the same `step_id`, and that entry's `evidence_basis` must contain at least one URL from a live web search.
- `NEED-EVIDENCE` requires `missing_evidence`.
- `GAP` requires `gap_description` stating specifically which minimum-standard field is missing or vague.

### Evidence ledger contract

Every item in `evidence_ledger` must include:

- `evidence_id`
- `claim`
- `tier`: `L1`, `L2`, `L3`, or `L4`
- `source`（L1/L2/L3 必须含 URL；L4 标注"训练知识，未现场验证"）
- `environment_date`
- `confidence`
- `impact`

### AlternativeCheck contract

Every item in `alternative_checks` must include:

- `step_id`
- `current_method`
- `native_or_standard_alternatives`
- `better_option`
- `evidence_basis`（必须含 Phase 5a 联网搜索结果：URL + 搜索时间；禁止无来源表述）
- `why_current_is_weaker`
- `recommendation`
- `web_search_performed`: `true` / `false`（false 时该条目视为 L4，需在 evidence_basis 中注明补搜计划）

### DeficiencyChain contract

Every item in `deficiency_chains` must include:

- `finding_id`
- `step_id`
- `defect`（具体缺陷描述，不得写"该步骤有风险"）
- `evidence_refs`（指向 evidence_ledger 中的具体 evidence_id）
- `production_consequence`（具体失效场景或量化影响）
- `required_fix_or_proof`（可操作的修复或证明要求）
- `elevation_required`

---

## Elevation triggers

Mark `Elevation Required? = Yes` when any apply:

- production or zero-downtime change with weak rollback or verification
- migration, service lifecycle, traffic, data, security, certificate, permission, or compliance change
- any hard gate lacks evidence: rollback, observability, owner, audit trail, approval, or rehearsal
- proposal bypasses service/platform-native mechanisms without written exception
- maintainability or handoff risk is high
- evidence suggests a safer mainstream or native path (including from Phase 5a web search)
- any path step is marked `ELEVATE`

---

## Output contract

以中文输出，结构如下：

````markdown
# Gate Review Report

## Review Result
- Status: Pass to Elevation / Need Evidence / Return to Author for Rework / No Elevation Needed
- One-line rationale:
- Elevation Required?: Yes/No

## Normalized Proposal
- Goal:
- Current plan:
- Production impact:
- Constraints:
- Success criteria:
- Rollback expectation:
- Owner / handoff:

## Phase 0 — 原始步骤源清单
| 原始序号 | 原文步骤描述 | 来源位置 |
（逐行列出，不得合并；行数 = 原始方案中的步骤总数）

## Implementation Path Canvas
Mermaid flowchart or compact path table.
- 必须覆盖 Phase 0 源清单中所有步骤（直接对应或拆分后对应）
- 每步必须包含 step_id、OK/GAP/RISK/ELEVATE/NEED-EVIDENCE marker 和 finding ID
- 未能在 Canvas 中体现的原始步骤须在 Path Findings Map 中注明原因

## Step Executability Matrix
| step_id | source_step_ref | Preconditions | Execution detail（具体命令/配置/制品） | Expected result | Verification（具体指标/命令/状态） | Rollback（触发条件+序列+恢复时长） | Owner（具体角色/团队） | Marker |
（禁止在任何字段填写"按实际情况"、"确认正常"、"相关负责人"等模糊表述；出现即标记该步骤为 GAP）

## Evidence Ledger
| Evidence ID | Claim | Tier | Source（L1/L2/L3须含URL） | Environment/date | Confidence | Impact |

## Alternative / Baseline Checks
| step_id | Current method | Native/standard alternative | Better option | Evidence basis（URL + 搜索时间） | web_search_performed | Recommendation |
（evidence_basis 无 URL 的条目标记为 [TRAINING-ONLY]，视为 L4）

## Path Findings Map
| step_id | source_step_ref | Finding ID | Marker | Missing/unsafe element（具体字段或机制） | Consequence（具体失效场景） | Required fix/proof（可操作要求） |

## Key Deficiency Chains
格式：Finding ID → step_id → 具体缺陷 → evidence_id → 生产后果 → 可操作修复/证明要求
1. ...
2. ...
3. ...
（每条不得使用"需进一步评估"、"建议加强监控"等无操作性结论）

## Phase 0 覆盖追踪
| 原始序号 | 原文步骤 | 对应 step_id(s) | 覆盖状态（已覆盖 / 已拆分为X步 / 未覆盖:原因） |
（所有原始步骤必须在此表中有明确状态，无"未覆盖"条目方可继续）

## Structured Gate Record
```json
{
  "schema_version": "gate-review.v2"
}
```

## Elevation Entry
- Elevation Required?: Yes/No
- Trigger sources:
- Blocking path steps:
- What elevation must solve:
- If no elevation: why current plan can continue to Final Gate or evidence collection:

## Handoff to Next Skill
- For `production-plan-elevation`: pass the Structured Gate Record and all ELEVATE/RISK/NEED-EVIDENCE blockers.
- For `production-plan-final-gate` only if no elevation is required: pass the Structured Gate Record and proof package.
````

---

## Local validation

When a Structured Gate Record is available as JSON, validate it with:

```bash
python production-plan-gate-review/scripts/validate_gate_record.py gate-record.json
```

Validation failure means the report is incomplete. Fix the structured record or explicitly explain which source evidence is unavailable.

Additional self-check before submitting output:
- Phase 0 源清单行数 = 原始方案步骤总数 ✓
- Phase 0 覆盖追踪表中无"未覆盖且无原因"条目 ✓
- 所有 RISK/ELEVATE 步骤的 AlternativeCheck 含 URL（`web_search_performed: true`）✓
- Step Executability Matrix 无模糊字段（无"按实际情况"、"确认正常"、"相关负责人"）✓
- 所有 deficiency_chains 的 `required_fix_or_proof` 可被操作员直接执行 ✓

---

## Boundaries

- Do not create a replacement implementation plan beyond naming what elevation must solve.
- Do not make final production admission decisions.
- Do not hide weak evidence behind operational experience; mark it as L4.
- Do not mark high-risk steps as merely informational when they block executability, rollback, observability, ownership, auditability, or handoff.
- Do not skip Phase 0 (full enumeration) or Phase 5a (web search) under any circumstance.
- Do not accept vague filler ("根据实际情况"、"视环境而定"、"参考官方文档") in any PathStep or DeficiencyChain field; flag it as GAP.
- Do not allow any original step from Phase 0 to be silently absent from the Path Canvas or Coverage Tracking table.
