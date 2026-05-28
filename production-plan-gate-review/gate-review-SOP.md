# Gate Review SOP — 对齐手册
**配套 Skill：** `production-plan-gate-review`  
**适用阶段：** 收到原始方案后 → Elevation 之前  
**文档用途：** 人工对齐检查，不替代 Skill 本身

---

## 一、这个 Skill 干什么的？

```
原始方案（人写或 AI 生成）
      ↓
  本 Skill：Gate Review        ← 你现在在这里
      ↓
  Elevation Skill（升维）
      ↓
  Final Gate（准入）
```

**一句话定位：** 把原始方案拆成可执行路径，逐步检查能不能跑、证据够不够、有没有更标准的做法，输出 Structured Gate Record 供后续升维使用。

**它不做的事：**
- ❌ 不设计替代方案（那是 Elevation 的职责）
- ❌ 不给最终 Go / No-Go 结论（那是 Final Gate 的职责）
- ❌ 不跳过任何原始步骤

---

## 二、启动前检查单

| # | 需要的输入 | 从哪里拿 | 缺了怎么办 |
|---|---|---|---|
| 1 | 原始方案全文（含所有步骤描述） | 业务方/开发方提交 | 不得启动，退回补充 |
| 2 | 生产影响范围和约束条件 | 业务方确认 | 以 NEED-EVIDENCE 标记，继续但注明 |
| 3 | 回滚预期（可接受停机时长等） | 业务方/运维方确认 | 以 NEED-EVIDENCE 标记 |
| 4 | Owner 和交接预期 | 业务方确认 | 以 NEED-EVIDENCE 标记 |

---

## 三、正常执行流程（7个 Phase）

### Phase 0：原始步骤全量提取（不可跳过）

**做什么：** 从原始方案逐字提取所有步骤，输出源清单，确定步骤总数。

**你应该看到：**
```
| 原始序号 | 原文步骤描述 | 来源位置 |
| 1 | 停止旧服务 | 第3节·执行步骤 |
| 2 | 更新 nginx 配置 | 第3节·执行步骤 |
| 3 | 执行数据库迁移脚本 | 第4节·数据处理 |
...
```

**红线：**
- 后续 `path_steps` 条目数必须 ≥ 此表行数
- 若少于此表行数，说明有步骤被合并或遗漏，需打回重做

---

### Phase 1：Input normalization

**做什么：** 提取目标、当前方案、生产影响、约束、成功标准、回滚预期、Owner。

**你应该看到：** Normalized Proposal 章节中每个字段有具体内容，不能只写"待确认"——缺失的用 `NEED-EVIDENCE` 标记，不能留空。

---

### Phase 2：Path Decomposition

**做什么：** 把原始方案重建为 precheck → prepare → execute → verify → rollback → observe → handoff 的完整路径，每步分配 `step_id`，并标注 `source_step_ref`（对应 Phase 0 原始序号）。

**你应该看到：** Step Executability Matrix 中每行有 `source_step_ref` 列，能追回到 Phase 0 源清单。

**红线：** Phase 2 结束后看"Phase 0 覆盖追踪"表，所有原始步骤必须有对应 step_id，无"未覆盖且无原因"的行。

---

### Phase 3：Executability Check

**做什么：** 对每个步骤检查4个最低标准字段，逐字段打分。

逐字段核对，不合格直接标 GAP：

| 字段 | 最低标准 | 常见不合格 |
|---|---|---|
| execution_detail | 具体命令/配置项/制品名称 | "按正常流程执行"、"参考文档" |
| verification | 具体指标名/命令输出/可观测状态 | "确认服务正常"、"观察运行情况" |
| rollback | 触发条件 + 操作序列 + 预计恢复时长 | "回滚到上一版本" |
| owner | 具体角色或团队名称 | "相关负责人"、"运维团队" |

**判断规则：**
- 4个字段全满足 → 可标 `OK`（还需有 evidence_refs）
- 任意1个字段不满足 → 标 `GAP`，不得标 `OK`

---

### Phase 4：Evidence Check

**做什么：** 为每个关键声明建立 Evidence Ledger 条目，按 L1–L4 分级。

**证据分级快速参考：**

| 级别 | 含义 | 能支持 OK？ |
|---|---|---|
| L1 | 本环境实测截图/日志/命令输出 | ✅ |
| L2 | 类生产环境测试或官方文档原文（含 URL） | ✅ |
| L3 | 可信第三方报告或案例（含 URL） | 辅助 |
| L4 | 训练知识 / 操作经验 / 无来源 | ❌ 不能单独支持 OK |

**红线：**
- L4 单独出现 → 该步骤不得标 OK，改为 NEED-EVIDENCE
- Source 字段没有 URL → 降为 L4

---

### Phase 5：Alternative/Baseline Check（含强制联网核查）

**做什么：** 对每个 RISK/ELEVATE 步骤，先联网搜索，再填 AlternativeCheck 条目。

**5a — 联网搜索（每个目标步骤执行3类搜索）：**

| 搜索类型 | 目的 | 示例搜索词 |
|---|---|---|
| 官方推荐 | 找当前文档推荐做法 | `[工具名] production best practice 2025 site:[vendor].com` |
| 近期变更 | 确认无 deprecation/breaking change | `[机制名] deprecated OR breaking change 2024 OR 2025` |
| 风险案例 | 找已知 CVE 或事故 | `[机制名] CVE OR incident OR outage 2024` |

**你应该看到（evidence_basis 字段）：**
```
- 官方推荐：Kubernetes rolling update 为生产推荐策略。来源：kubernetes.io/docs/tutorials/... 搜索时间：2025-06-01
- 近期变更：未发现 deprecation。来源：已搜索 GitHub kubernetes/kubernetes changelog
- 风险案例：未发现直接相关 CVE。来源：已搜索 NVD nvd.nist.gov
```

**红线：**
- `evidence_basis` 无 URL → 标 `[TRAINING-ONLY]`，视为 L4
- 某个 RISK/ELEVATE 步骤没有 AlternativeCheck 条目 → 违反 Non-negotiable rule，打回

**5b — 填写 AlternativeCheck 条目：**

基于搜索结果，比较当前方法 vs 原生/标准方法，填写所有字段（包括 `web_search_performed: true/false`）。

---

### Phase 6：Deficiency Chains

**做什么：** 产出至少3条缺陷链（步骤少于3步时除外），每条链完整追踪从步骤缺陷到生产后果的路径。

**合格链的结构：**
```
F-01 → S-03（数据库迁移步骤）→ 缺陷：无回滚脚本，仅依赖备份恢复
→ 证据：E-02（L4，无测试记录）→ 生产后果：迁移失败时恢复时间 > 4h，超出 RTO 窗口
→ 修复要求：提供已在预发环境测试通过的回滚脚本（含命令 + 执行时间记录）
```

**红线：**
- `required_fix_or_proof` 出现"需进一步评估"、"建议加强监控" → 不合格，需补具体操作要求
- `production_consequence` 仅写"可能造成故障" → 不合格，需写具体失效场景

---

### Phase 7：Elevation Entry

**做什么：** 基于 Gate Review 证据决定是否需要 Elevation，列出阻断步骤和 Elevation 需解决的问题。

**任一条件成立即 Elevation Required = Yes：**
- 任何步骤标 ELEVATE
- 有零停机要求但回滚/验证证据弱
- 方案绕过 service/platform-native 机制无书面例外
- 联网搜索发现有更安全的主流替代路径

---

## 四、输出质量检查表

收到 Skill 输出后逐项打勾：

### 结构完整性
- [ ] 包含"Phase 0 — 原始步骤源清单"章节
- [ ] 包含"Phase 0 覆盖追踪"表格
- [ ] 源清单行数 = 原始方案步骤总数
- [ ] 覆盖追踪表中无"未覆盖且无原因"条目

### Step Executability Matrix
- [ ] 每行有 `source_step_ref` 列（追回原始序号）
- [ ] 无 OK 步骤的 execution_detail 含模糊表述
- [ ] 无 OK 步骤的 verification 含模糊表述
- [ ] 无 OK 步骤的 rollback 仅写"回滚上一版本"
- [ ] 无 OK 步骤的 owner 写"相关负责人"

### Evidence Ledger
- [ ] L1/L2/L3 条目的 source 含 URL
- [ ] L4 条目标注"训练知识，未现场验证"
- [ ] 无 L4-only 步骤被标为 OK

### Alternative/Baseline Checks
- [ ] 每个 RISK/ELEVATE 步骤有对应 AlternativeCheck 条目
- [ ] `evidence_basis` 含 URL + 搜索时间
- [ ] 无 URL 的条目标记为 `[TRAINING-ONLY]`
- [ ] `web_search_performed` 字段存在

### Deficiency Chains
- [ ] 链数 ≥ 3（或步骤数 < 3 时有说明）
- [ ] 每条链有具体 evidence_id 引用
- [ ] `required_fix_or_proof` 可操作，无"建议加强"

### Structured Gate Record（JSON）
- [ ] 包含所有 required top-level fields
- [ ] 每个 path_steps 条目含 `source_step_ref`
- [ ] RISK/ELEVATE 步骤的 AlternativeCheck 含 `web_search_performed: true`
- [ ] GAP 步骤含 `gap_description` 字段

---

## 五、常见问题处理

| 现象 | 原因 | 处理方式 |
|---|---|---|
| path_steps 少于 Phase 0 步骤数 | 步骤被合并或省略 | 打回，要求补 Phase 0 全量列出后重做 Phase 2 |
| evidence_basis 无 URL | 未执行联网搜索 | 打回，要求补 Phase 5a 三类搜索 |
| OK 步骤 verification 写"确认服务正常" | 未执行最低标准检查 | 打回，改标 GAP，要求具体指标 |
| Deficiency chain 结论写"建议加强监控" | 未执行深度分析 | 打回，要求写具体失效场景和可操作修复 |
| AlternativeCheck 无对应某 RISK 步骤 | 遗漏 alternative check | 打回，要求补充含 web_search 的条目 |
| Elevation Entry 写"暂无阻断步骤"但有 ELEVATE marker | 逻辑不一致 | 打回，要求对齐 path_steps marker 和 elevation_entry |

---

## 六、与其他 Skill 的边界

```
production-plan-gate-review（本 Skill）
  输入：原始方案全文
  输出：Structured Gate Record（path_steps, evidence_ledger, alternative_checks, deficiency_chains, elevation_entry）
        ↓

production-plan-elevation
  输入：Structured Gate Record 中的 ELEVATE/RISK/NEED-EVIDENCE 步骤
  输出：升维候选方案 + 推荐 Final Gate candidate
        ↓

production-plan-final-gate
  输入：推荐 candidate + 残余风险
  输出：Go / Conditional Go / No-Go（唯一有权出此结论的 Skill）
```

**边界原则：**
- 本 Skill **不设计**替代方案，只命名"Elevation 需解决什么"
- 本 Skill **不发放**准入，只说明路径问题和证据强度
- 本 Skill **必须**让每个原始步骤都有去处，不得静默省略

---

## 七、本 Skill 与 Elevation Skill 的四项改动对比

| 改动项 | Gate Review 的实现方式 | Elevation 的实现方式 |
|---|---|---|
| 全量枚举防漏查 | Phase 0 从原文逐字提取所有步骤，建立源清单；Phase 2 覆盖追踪表强制对账 | Step 0 从 Gate Record 枚举所有 path_steps，后续必须逐一覆盖 |
| 联网搜索强制化 | Phase 5a 对每个 RISK/ELEVATE 步骤执行3类搜索；AlternativeCheck 的 `evidence_basis` 必须含 URL | Step 2a 对每个阻断步骤执行3类搜索；Evidence source 必须含 URL |
| 约束有牙齿 | PathStep 4个字段有最低标准；违反即标 GAP，不得标 OK | Candidate 5个字段有最低标准；违反即标 INCOMPLETE，不得推荐 |
| 回复粒度 | Step Executability Matrix、Alternative Checks 表格字段加内联格式约束；Deficiency Chain 格式化为5段结构 | Candidate 模板每字段加格式约束；Option Comparison 加 Covers step_ids 列 |

---

*本 SOP 随 SKILL.md 同步更新，版本：v2.0*
