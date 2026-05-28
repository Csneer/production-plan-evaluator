---
name: production-plan-elevation
description: Use when a production Gate Review v2 Structured Gate Record has identified ELEVATE, RISK, or NEED-EVIDENCE implementation steps and the user needs elevated production-ready alternatives, not initial path review or final approval.
---

# Production Plan Elevation

## Core intent

Convert a Gate Review v2 Structured Gate Record's blocking findings into one or more stronger production-ready candidate paths. This skill designs elevated alternatives; it must not redo the initial path review and must not issue final Go/No-Go approval.

## Use when

- A Gate Review v2 report says `Elevation Required? = Yes`.
- The Gate Review Structured Gate Record contains `ELEVATE`, `RISK`, or `NEED-EVIDENCE` path steps that need design elevation, proof collection, or exception handling.
- The user asks for升维方案、替代路径、service-native/platform-native方案、industry practice、维护性改造、标准化实施路径, or exception handling.
- A current plan is nonstandard but may be retained only with exception approval and compensating controls.

Do not use this skill to perform the initial implementation-path critique or final production admission. Use `production-plan-gate-review` first and `production-plan-final-gate` last.

## Required inputs

- Original proposal or enough summary to understand the current path.
- Gate Review v2 Structured Gate Record, especially `path_steps`, `alternative_checks`, `deficiency_chains`, `evidence_ledger`, and `elevation_entry`.
- Gate Review output, especially blocking path steps, finding IDs, evidence ledger, and what elevation must solve.
- Known constraints: downtime tolerance, rollout window, platform limits, owner, operational baseline, and rollback expectations.

If the Gate Review v2 Structured Gate Record is missing, reconstruct only the minimum context needed and return the user to `production-plan-gate-review`; do not pretend a full gate review was performed.

## Non-negotiable rules

- **Design alternatives, not approval.** Never output final `Go`, `Conditional Go`, or `No-Go` verdicts.
- **Consume Gate v2, do not redo it.** Use Gate Review's `ELEVATE`, `RISK`, and `NEED-EVIDENCE` blockers as inputs; do not restart implementation-path critique except to clarify missing context.
- **Native/baseline first.** Prefer service-native, platform-native, distribution-native, or internal baseline mechanisms.
- **Exception is explicit.** Keeping a non-native or wrapper-based plan requires exception approval, compensating controls, owner, and review date.
- **Every option needs operations detail — minimum standard enforced.** A candidate is only valid if ALL of the following are present:
  - Cutover: 有序操作步骤不少于3步，每步注明执行者和预计耗时
  - Rollback: 包含触发条件、回滚操作序列、数据一致性处置、预计恢复时长
  - Observability: 命名具体指标名称或告警项，不得使用"监控运行状态"等模糊描述
  - Owner/handoff: 指定具体角色或团队，不得写"相关负责人"
  - Applicability boundaries: 明确列出不适用场景
  缺少任意一项，该 candidate 标记为 `[INCOMPLETE]`，不得进入 Option Comparison，不得被推荐为 Final Gate candidate。
- **Depth first.** 每个字段禁止使用"根据实际情况"、"视具体环境而定"、"参考官方文档"等无操作性语句。所有建议必须达到操作员可直接执行的粒度。
- **Full step coverage enforced.** 所有 path_steps 必须在报告中被显式覆盖。未被任何 candidate 覆盖的 step_id 必须在 Residual Risks 中逐条注明原因，不得静默省略。

## Workflow

### Step 0 — 全量枚举（强制，不可跳过）

从 Gate Review v2 Structured Gate Record 中提取所有 `path_steps`，输出完整清单：

| step_id | 步骤描述 | Marker（ELEVATE / RISK / NEED-EVIDENCE / PASS） |

规则：
- 必须逐行列出，不得合并相似步骤
- 此清单是后续所有步骤的锚点
- 每个 step_id 必须在报告正文中至少出现一次
- 未被任何 candidate 覆盖的 step_id 必须在 Residual Risks 中逐条说明

### Step 1 — 还原 Gate Review 阻断项

按 finding ID、`step_id`、marker、路径步骤描述、需解决的问题、当前证据强度，逐条列出所有 ELEVATE / RISK / NEED-EVIDENCE 项。不得合并、不得按主题归组省略。

### Step 2 — 联网核查行业当前标准（强制，每个阻断 step 执行一次）

对 Step 1 中每个阻断步骤，执行以下网络搜索，并将结果作为 Evidence source 的强制组成部分：

1. 官方/主流文档当前推荐做法
   - 搜索示例：`[service/tool name] production best practice [year] site:[vendor].com/docs`
2. 近12个月内是否有 deprecation、breaking change 或重大更新
   - 搜索示例：`[step mechanism] deprecated OR breaking change 2024 OR 2025`
3. 是否有已知 CVE、运维事故案例或社区告警与该步骤相关
   - 搜索示例：`[step mechanism] CVE OR incident OR outage 2024`

规则：
- Evidence source 字段必须注明来源 URL 和搜索时间
- 禁止以"行业通行做法"、"业界普遍认为"等无来源表述代替搜索结果
- 若搜索无结果，必须在 Evidence source 中注明"已搜索，未找到相关文档，原因：…"

### Step 3 — 生成升维候选方案（1–3个 / 1–3 elevated candidate paths）

基于 Step 2 的联网核查结果和 Step 1 的阻断项，生成候选方案。优先顺序：service-native > platform-native > distribution-native > internal baseline > wrapper/custom。

### Step 4 — 逐字段填写每个 Candidate（执行最低标准校验）

对每个 candidate 填写以下字段，并在输出前自检是否满足 Non-negotiable rules 中的最低标准：

- Core idea（核心思路，说明为何优于当前方案）
- Native/baseline mechanism（具体机制名称，不得写泛称）
- Evidence source（Step 2 的搜索结果，含 URL + 搜索时间）
- Cutover path（有序步骤 ≥3，含执行者 + 预计耗时）
- Rollback path（触发条件 + 操作序列 + 数据一致性处置 + 恢复时长）
- Verification and observability（具体指标名 / 告警项 / 验证命令）
- Owner and handoff（具体角色或团队）
- Costs / constraints（资源、时间、许可、依赖等）
- Applicability boundaries（明确列出不适用场景）
- Covered step_ids（本方案覆盖了哪些 step_id，逐一列出）

若任何字段不满足最低标准，标记该 candidate 为 `[INCOMPLETE]` 并说明缺失项，不得继续推进。

### Step 5 — Option Comparison

比较：当前方案、所有 COMPLETE candidate、Defer/No-change。

表格必须包含列：`Option | Solves which step_ids | Operational risk | Maintainability | Evidence quality | Final Gate readiness`

### Step 6 — 推荐单一 Final Gate 候选

推荐恰好一个 candidate 进入 Final Gate，或说明需返回证据收集。不得推荐 `[INCOMPLETE]` candidate。

### Step 7 — Exception Approval（如保留非标方案）

如保留当前非 native/非标方案，使用 `references/exception-template.md` 填写 Exception Approval，包含：保留理由、补偿控制措施、负责人、复审日期。

---

## Output contract

以中文输出，结构如下：

```markdown
# Elevation Report

## Elevation Result
- Recommendation: Submit Candidate X to Final Gate / Need Evidence / Return to Design
- One-line rationale:
- Recommended candidate:

## Step 0 — 全量 path_steps 清单
| step_id | 步骤描述 | Marker |
（逐行列出，不得合并）

## Gate Review 阻断项（Step 1）
| Finding ID | Step ID | Marker | 阻断路径步骤 | 需解决的问题 | 当前证据强度 |

## 联网核查结果摘要（Step 2）
每个阻断 step_id 对应一段，格式：
- step_id：
  - 官方当前推荐：[描述] 来源：[URL] 搜索时间：[日期]
  - 近期 deprecation/breaking change：[描述或"未发现"] 来源：[URL]
  - CVE/事故案例：[描述或"未发现"] 来源：[URL]

## Current Plan Retention Conditions
- Conditions required to keep current plan:
- Exception required?: Yes/No
- Why current plan is or is not acceptable after compensation:

## Elevated Candidate Options

### Candidate 1 — [方案名] [COMPLETE / INCOMPLETE: 缺失字段]
- Core idea:
- Native/baseline mechanism:
- Evidence source:（含 URL + 搜索时间）
- Cutover path:
  - Step 1 [执行者] [预计耗时]：
  - Step 2 [执行者] [预计耗时]：
  - Step N …
- Rollback path:
  - 触发条件：
  - 操作序列：
  - 数据一致性处置：
  - 预计恢复时长：
- Verification and observability:（具体指标名/告警项/验证命令）
- Owner and handoff:（具体角色或团队）
- Costs / constraints:
- Applicability boundaries:（明确列出不适用场景）
- Covered step_ids:（逐一列出）

## Option Comparison
| Option | Covers step_ids | Operational risk | Maintainability | Evidence quality | Final Gate readiness |

## Recommended Path for Final Gate
- Candidate:
- Why this candidate:
- Required proof package:
- Residual risks to send to Final Gate:（含未被任何 candidate 覆盖的 step_ids 及原因）

## Exception Approval
（仅在保留非 native/非标当前方案时填写）
- 保留理由：
- 补偿控制措施：
- 负责人：
- 复审日期：
```

## Boundaries

- Do not issue final admission verdicts.
- Do not skip option comparison when only one option is viable.
- Do not recommend an option that lacks rollback, verification, owner, or handoff path.
- Do not skip Step 0 (full enumeration) or Step 2 (web search) under any circumstance.
- Do not accept "根据实际情况" or equivalent vague language in any field.
- Do not silently omit any step_id; every step_id must be accounted for in the report.

