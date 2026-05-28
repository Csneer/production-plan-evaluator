# 升维审查 SOP — 对齐手册
**配套 Skill：** `production-plan-elevation`  
**适用阶段：** Gate Review v2 完成后 → Final Gate 之前  
**文档用途：** 人工对齐检查，不替代 Skill 本身

---

## 一、这个 Skill 干什么的？

```
Gate Review v2（初审）
      ↓
  本 Skill：升维审查        ← 你现在在这里
      ↓
Final Gate（准入）
```

**一句话定位：** 把 Gate Review 发现的问题步骤，转化为可执行的、更接近行业标准的替代方案，供 Final Gate 做准入判断。

**它不做的事：**
- ❌ 不重新做 Gate Review
- ❌ 不给最终 Go / No-Go 结论
- ❌ 不跳过任何一个问题步骤

---

## 二、启动前检查单（喂给 Skill 前先核对）

在把材料交给 Skill 之前，确认以下输入都齐了：

| # | 需要的输入 | 从哪里拿 | 缺了怎么办 |
|---|---|---|---|
| 1 | Gate Review v2 Structured Gate Record | Gate Review 输出 | 退回，重跑 Gate Review |
| 2 | 所有 path_steps（含 step_id 和 Marker） | Structured Gate Record | 退回，Gate Record 不完整 |
| 3 | Finding ID + 阻断原因 | Gate Review 报告 | 退回 |
| 4 | Evidence Ledger | Gate Review 报告 | 可部分重建，但需注明 |
| 5 | 约束条件（停机容忍、变更窗口、平台限制、回滚预期） | 业务方/运维方确认 | 需先向业务方确认再启动 |

---

## 三、正常执行流程（7步）

### 第 0 步：全量枚举 path_steps（不可跳过）

**做什么：** 把所有 path_steps 列成表格，一行一步，不得合并。

**你应该看到：**
```
| step_id | 步骤描述 | Marker |
| S-01    | 变更 nginx 配置 | PASS |
| S-02    | 停止旧服务进程 | ELEVATE |
| S-03    | 数据库迁移脚本 | RISK |
...
```

**红线：** 如果输出里的行数少于 Gate Record 里的 path_steps 数量，说明有步骤被合并或遗漏，需要打回重做。

---

### 第 1 步：还原阻断项清单

**做什么：** 把所有 ELEVATE / RISK / NEED-EVIDENCE 的步骤单独列出，说明每个的问题和当前证据强度。

**你应该看到：**
```
| Finding ID | Step ID | Marker | 阻断步骤 | 问题 | 证据强度 |
| F-01 | S-02 | ELEVATE | 停止旧服务进程 | 无蓝绿/滚动机制 | 弱 |
```

**红线：** Finding 数量应与 Gate Review 报告一致，不得少于 Gate Review 发现的阻断数。

---

### 第 2 步：联网核查（每个阻断 step 都要做）

**做什么：** 对每个阻断步骤，搜索三类信息：
1. 官方当前推荐做法
2. 近12个月有没有 deprecation 或 breaking change
3. 有没有相关 CVE 或运维事故案例

**你应该看到：**
```
step_id：S-02
- 官方当前推荐：Kubernetes rolling update 策略，来源：kubernetes.io/docs/... 搜索时间：2025-06-01
- 近期 deprecation：未发现，来源：已搜索 GitHub changelog
- CVE/事故：未发现直接相关，来源：已搜索 NVD
```

**红线：**
- 不接受"行业通行做法是…"没有 URL 的表述
- 不接受某个阻断步骤没有对应搜索记录
- 搜索无结果也必须写"已搜索，未找到"

---

### 第 3 步：生成升维候选方案（1–3个）

**做什么：** 基于联网核查结果，提出替代方案。优先顺序：

```
service-native > platform-native > distribution-native > internal baseline > wrapper/custom
```

**红线：** 不接受没有技术锚点的方案，比如"使用更稳定的方式"、"参考最佳实践"。

---

### 第 4 步：逐字段填写每个 Candidate

这是最容易出泛泛内容的步骤。逐字段核对：

| 字段 | 最低标准 | 常见不合格写法 |
|---|---|---|
| Core idea | 说明为何优于当前方案 | "更加稳定可靠" |
| Native mechanism | 具体机制名称 | "使用平台原生能力" |
| Evidence source | URL + 搜索时间 | "官方文档建议" |
| Cutover path | ≥3步，含执行者+耗时 | "按正常变更流程执行" |
| Rollback path | 触发条件+操作序列+数据一致性+恢复时长 | "回滚到上一版本" |
| Observability | 具体指标名/告警项/验证命令 | "监控服务状态" |
| Owner/handoff | 具体角色或团队 | "相关负责人" |
| Applicability boundaries | 明确不适用场景 | 空白 |
| Covered step_ids | 逐一列出 step_id | 不填 |

**判断一个 Candidate 是否合格：**
- ✅ 所有字段满足最低标准 → `[COMPLETE]`，可进入对比和推荐
- ❌ 任一字段不满足 → `[INCOMPLETE]`，不得被推荐，需补充后重来

---

### 第 5 步：Option Comparison 表格

**做什么：** 对比所有方案，包括"保留当前方案"和"不变更"。

**表格必须包含的列：**
```
Option | Covers step_ids | Operational risk | Maintainability | Evidence quality | Final Gate readiness
```

**红线：**
- 每一行的 Covers step_ids 要写具体 step_id 编号，不写"全部"
- 即使只有一个 COMPLETE candidate，也不得跳过这张表

---

### 第 6 步：推荐 Final Gate 候选

**做什么：** 从 COMPLETE candidates 中推荐恰好一个，给出：
- 推荐理由
- 需要准备的证明材料清单
- 带入 Final Gate 的残余风险（含所有未被覆盖的 step_id）

**红线：**
- 不得推荐 `[INCOMPLETE]` candidate
- "Residual risks"必须逐条列出未被任何 candidate 覆盖的 step_id，不得写"暂无"然后实际上有漏项

---

### 第 7 步：Exception Approval（仅保留非标方案时填写）

**做什么：** 如果最终选择保留原有非标方案，必须填写：

| 字段 | 说明 |
|---|---|
| 保留理由 | 具体业务或技术原因 |
| 补偿控制措施 | 具体措施，不得写"加强监控" |
| 负责人 | 具体姓名或角色 |
| 复审日期 | 明确日期 |

---

## 四、输出质量检查表（收到报告后逐项打勾）

收到 Skill 输出后，用这张表做人工验收：

### 结构完整性
- [ ] 包含"全量 path_steps 清单"章节
- [ ] 清单行数 = Gate Record 中 path_steps 总数
- [ ] 每个 ELEVATE/RISK/NEED-EVIDENCE 步骤在"阻断项清单"中有对应行
- [ ] 每个阻断步骤在"联网核查结果"中有对应段落

### 联网核查质量
- [ ] 每个阻断步骤有3类搜索（官方推荐 / deprecation / CVE）
- [ ] 所有 Evidence source 含 URL，不含"行业通行做法"等无来源表述
- [ ] 搜索无结果的项目有明确的"已搜索，未找到"说明

### Candidate 质量
- [ ] 每个 Candidate 标注了 `[COMPLETE]` 或 `[INCOMPLETE: 缺失字段]`
- [ ] 所有 `[INCOMPLETE]` candidate 未出现在推荐位置
- [ ] Cutover path ≥3步，含执行者和耗时
- [ ] Rollback 含触发条件 + 操作序列 + 数据一致性 + 恢复时长
- [ ] Observability 含具体指标名或告警项

### 覆盖完整性
- [ ] Option Comparison 表格存在，含 Covers step_ids 列
- [ ] Residual risks 中逐条列出了未被 candidate 覆盖的 step_id
- [ ] 没有 step_id 被静默省略

### 推荐合理性
- [ ] 恰好推荐了一个 Final Gate candidate（不是零个，不是多个）
- [ ] 推荐 candidate 标记为 `[COMPLETE]`
- [ ] 需要 Exception Approval 时该章节存在且字段完整

---

## 五、常见问题处理

| 现象 | 原因 | 处理方式 |
|---|---|---|
| 报告比 Gate Record 的 path_steps 少 | 步骤被合并或遗漏 | 打回，要求重做 Step 0，逐行列出 |
| Evidence source 无 URL | 未执行联网搜索 | 打回，要求补充 Step 2 搜索记录 |
| Candidate 写了一句话的 Cutover | 未执行最低标准校验 | 打回，要求补充至 ≥3步含执行者耗时 |
| 推荐了 `[INCOMPLETE]` candidate | 未执行完整性标注 | 打回，要求先标注 COMPLETE/INCOMPLETE |
| Option Comparison 缺列 | 模板被简化 | 打回，要求补充 Covers step_ids 列 |
| Residual risks 写"暂无" | 未与 Step 0 清单对比 | 打回，要求逐一核对未覆盖的 step_id |

---

## 六、与其他 Skill 的边界

```
production-plan-gate-review
  └─ 输出：Gate Review v2 Structured Gate Record（含 path_steps、finding ID、evidence ledger）
        ↓ 本 Skill 的输入起点

production-plan-elevation（本 Skill）
  └─ 输出：Elevation Report（含推荐 candidate、残余风险、证明材料清单）
        ↓ 本 Skill 的输出终点

production-plan-final-gate
  └─ 输入：Elevation Report 的推荐 candidate + 残余风险
```

**边界原则：**
- 本 Skill **不判断**某个步骤是否应该被标记为 ELEVATE（那是 Gate Review 的职责）
- 本 Skill **不发放**最终准入（那是 Final Gate 的职责）
- 本 Skill **只设计**替代方案并推荐一个进入 Final Gate

---

*本 SOP 随 SKILL.md 同步更新，版本：v2.0*
