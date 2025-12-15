# F01 OpenSpec 学习与开发路线图

**目的**：从零开始学习 OpenSpec，最终完成 F01 新程式的开发  
**总耗时**：估计 2-3 小时（根据学习深度）  
**最终目标**：F01 完全采用 OpenSpec 工作流程开发

---

## 📍 4 大学习阶段

### 🎯 第 1 阶段：OpenSpec 核心概念（15-20 分钟）

**目标**：理解 OpenSpec 是什么、能解决什么问题

#### 📖 阅读材料
1. [AGENTS.md](AGENTS.md) - 前 50 行（快速参考）
2. [project.md](project.md) - 完整阅读（了解 F01 上下文）

#### 🎓 核心知识点
- [ ] OpenSpec 的三个核心概念：**Project**、**Change**、**Spec**
- [ ] **三阶段工作流**：Creating → Implementing → Validating
- [ ] **Change Proposal** 的作用（规范化功能开发）
- [ ] **Spec Delta** 的概念（记录需求变更）

#### ✍️ 学习检查清单
```
□ 理解什么是 "change proposal"（变更提案）
□ 理解什么是 "spec delta"（规格变更）
□ 理解 OpenSpec 为什么要分离 "proposal" 和 "implementation"
□ 理解 project.md 对 AI 助手的价值
```

#### 💡 学习提示
- 不需要理解所有细节，只需掌握大方向
- 关键是理解「为什么需要规范化」而不是「如何使用每个命令」

---

### 🛠️ 第 2 阶段：OpenSpec 工作流实战（30-40 分钟）

**目标**：通过实际操作掌握 OpenSpec 工作流

#### 📖 相关文档
- [AGENTS.md](AGENTS.md) - 全文（重点：三阶段工作流）
- [SPEC_TO_OPENSPEC_MAPPING.md](SPEC_TO_OPENSPEC_MAPPING.md) - 理解映射关系

#### 🎯 实战任务 1：创建第一个变更提案

**场景**：为 F01 增加一个新功能：「支持从历史日期查询」

**执行步骤**：

```bash
# 1. 在 f01_package 目录执行
cd c:\Taifex\dev\f01_package

# 2. 创建变更提案
openspec create add-historical-date-support
```

**预期结果**：
- 在 `openspec/changes/add-historical-date-support/` 目录生成：
  - `proposal.md` - 变更提案
  - `tasks.md` - 任务列表
  - `design.md`（可选）- 设计文档
  - 一个或多个 spec delta 文件

#### 📋 变更提案应该包含的内容

```markdown
# Change Proposal: add-historical-date-support

## 需求说明
当前 F01 只能查询最后交易日数据，需要支持查询任意历史日期。

## 影响范围
- fetch() 接口：新增 `use_selenium` 参数
- 项目依赖：新增 selenium, webdriver-manager
- 技术方案：引入浏览器自动化（改为方案 2）

## 规格变更
### MODIFIED Requirements

#### 场景：查询历史日期
- 输入：date="2024-12-04", use_selenium=True
- 输出：返回该日期的真实外资数据
```

#### ✍️ 学习检查清单
```
□ 理解 proposal.md 的结构
□ 理解 tasks.md 中的任务追踪
□ 理解如何定义「ADDED」「MODIFIED」「REMOVED」需求
□ 理解每个需求为什么要包含 Scenario（场景）
```

#### 💡 实战技巧
- 第一次创建不需要完美，关键是理解流程
- 如果 `openspec create` 无法自动打开编辑器，手动编辑也可以
- 变更提案可以分多次提交，逐步完善

---

### 📝 第 3 阶段：F01 新程式需求分析（20-30 分钟）

**目标**：用 OpenSpec 方式分析 F01 需要做什么改动

#### 🎯 实战任务 2：分析 F01 的改进需求

根据 [f01_fetcher_spec.md](../f01_fetcher_spec.md) 和 [project.md](project.md)，列出：

**问题 1：当前 F01 的限制**
```
❌ 无法查询历史日期（API 无视日期参数）
❌ 只能返回最新交易日的数据
❌ 若需要回测历史数据，无法使用
```

**问题 2：改进方案**
```
✅ 方案 A：保持现状（requests）— 适合日常监控
✅ 方案 B：升级到 Selenium — 适合历史数据查询
✅ 建议：两个版本共存（fetch vs fetch_historical）
```

**问题 3：实现步骤**
```
1. 确定需求：是否真的需要历史数据？
2. 选择方案：requests 还是 Selenium？
3. 修改接口：是新增函数还是修改现有函数？
4. 编写规格：更新 project.md 和 spec.md
5. 编写代码：实现新功能
6. 编写测试：验证功能正确
```

#### 💡 关键问题
在开始编码前，您需要回答：
1. **F01 需要支持历史日期查询吗？**
   - 如果不需要 → 保持现状，完成学习
   - 如果需要 → 选择 Selenium 方案，建立变更提案

2. **如果升级，是否需要向后兼容？**
   - 如果是 → 新增 `fetch_historical()` 函数
   - 如果不是 → 直接修改 `fetch()` 函数

---

### 💻 第 4 阶段：F01 新程式开发与测试（1-2 小时）

**目标**：按照 OpenSpec 流程完成 F01 代码开发

#### 🎯 开发工作流

**步骤 1：完善变更提案**
```bash
# 如果还没创建，创建变更提案
openspec create <change-id>

# 编辑 openspec/changes/<change-id>/proposal.md
# 定义清楚需求和 spec delta
```

**步骤 2：编写规格 Delta**
```
openspec/changes/<change-id>/
├── proposal.md          # 变更提案
├── tasks.md             # 任务清单
└── specs/
    └── f01_fetcher.md   # 新增或修改的规格部分
```

**步骤 3：验证规格**
```bash
cd c:\Taifex\dev\f01_package
openspec validate <change-id> --strict
```

**步骤 4：编写代码**
- 在 `f01_fetcher_dev.py` 中实现新功能
- 参考 `f01_fetcher_spec.md` 中的实现建议
- 保持 `openspec/project.md` 中定义的代码风格

**步骤 5：编写测试**
```python
# 在 test_f01_auto.py 中新增测试用例
def test_fetch_historical_date():
    result = fetch("2024-12-04", use_selenium=True)
    assert "F01:" in result
    assert "-26,823" in result  # 验证数据格式
```

**步骤 6：更新规格书**
- 更新 `f01_fetcher_spec.md` 中的版本号
- 添加新功能的说明（如果有）
- 更新 `project.md` 的约束和依赖

**步骤 7：标记实现完成**
```bash
# 在 openspec/changes/<change-id>/tasks.md 中标记任务完成
# 或者在 proposal.md 中添加实现完成的标记
```

---

## 🗺️ 详细工作清单

### 第 1 阶段：核心概念（必做 ✅）

```
□ 阅读 AGENTS.md 的 TL;DR 和三阶段工作流
□ 阅读 project.md 了解 F01 背景
□ 理解 project.md 如何帮助 AI 理解项目
□ 理解为什么 OpenSpec 要分离 proposal 和 implementation
□ 理解 "spec delta" 和 "change-id" 的概念
```

**预期耗时**：15-20 分钟

---

### 第 2 阶段：工作流实战（必做 ✅）

```
□ 执行 openspec create 命令创建第一个变更提案
□ 理解生成的 proposal.md、tasks.md 结构
□ 编辑 proposal.md，定义一个简单的需求变更
□ 理解如何写 "ADDED / MODIFIED / REMOVED Requirements"
□ 理解每个需求为什么要包含 "Scenario"
□ （可选）执行 openspec validate 验证提案
```

**预期耗时**：30-40 分钟

**实战例子**：
- 变更 ID：`add-error-logging`
- 需求：为 F01 增加详细的错误日志
- 场景：当网络连接失败时，记录详细的错误信息和时间戳

---

### 第 3 阶段：需求分析（根据实际情况）

```
□ 决定：F01 是否需要升级到 Selenium？
  - 不需要 → 跳过第 4 阶段，学习完成
  - 需要 → 继续第 4 阶段
  
□ 如果需要升级：
  □ 选择方案：新增函数还是修改现有函数？
  □ 评估影响：需要修改哪些文件？
  □ 规划测试：如何验证新功能？
```

**预期耗时**：20-30 分钟

---

### 第 4 阶段：实际开发（可选 ⚠️）

仅当「第 3 阶段」决定升级 F01 时执行

```
□ 创建变更提案：openspec create upgrade-to-selenium
□ 编写规格 delta：定义新的 fetch_historical() 接口
□ 编写代码：实现 Selenium 版本的数据爬取
□ 编写测试：验证新功能正常工作
□ 更新文档：同步 spec.md 和 project.md
□ 验证规格：openspec validate upgrade-to-selenium --strict
□ 整理代码：code review、注释、cleanup
```

**预期耗时**：1-2 小时

---

## 🎓 学习资源映射

| 学习阶段 | 关键文档 | 重点内容 |
|---------|---------|---------|
| **第 1 阶段** | AGENTS.md | TL;DR、三阶段工作流 |
| **第 1 阶段** | project.md | 完整阅读，理解 F01 背景 |
| **第 2 阶段** | AGENTS.md | 创建变更提案的规范 |
| **第 2 阶段** | SPEC_TO_OPENSPEC_MAPPING.md | 理解规格和 OpenSpec 的映射 |
| **第 3 阶段** | f01_fetcher_spec.md | 理解当前 F01 的限制和方案 |
| **第 4 阶段** | project.md | 代码风格、架构模式 |
| **第 4 阶段** | AGENTS.md | 规格 delta 写法 |

---

## 💡 学习技巧

### ✅ 推荐做法
1. **顺序学习** - 不要跳过前几个阶段
2. **动手实践** - 边学边试，立即执行命令
3. **逐步深化** - 不追求完美，理解概念即可
4. **记录疑问** - 遇到不明白的地方记下来

### ❌ 避免的做法
1. ❌ 一次性读完所有文档（太多信息，容易迷茫）
2. ❌ 不动手实践，只看理论（无法真正理解）
3. ❌ 追求完美规格（第一版不需要完美）
4. ❌ 跳过第 1、2 阶段直接写代码（会重复工作）

---

## 🔄 学习后的检查清单

完成以上阶段后，您应该能够：

```
□ 解释什么是 OpenSpec 变更提案（change proposal）
□ 创建并编辑一个 openspec 变更提案
□ 理解为什么 OpenSpec 要分离规格和实现
□ 理解 F01 的当前限制和可能的改进方向
□ 使用 openspec 命令验证规格的有效性
□ 根据 OpenSpec 规范编写 Python 代码
□ 维护 openspec/project.md 与代码的一致性
```

---

## 🚀 下一步行动

### 立即开始第 1 阶段
```bash
# 打开 AGENTS.md 开始阅读
code c:\Taifex\dev\f01_package\openspec\AGENTS.md
```

### 需要帮助时
- 遇到 OpenSpec 命令问题？查看 `openspec --help`
- 不理解规格 delta 写法？参考本文档的「第 2 阶段」
- 不知道 F01 应该怎么改？从「第 3 阶段」开始讨论

---

## 📞 FAQ

**Q: 需要完全理解 AGENTS.md 吗？**  
A: 不需要。第 1 阶段只需理解三阶段工作流，详细细节在实践中学习。

**Q: 第 2 阶段创建的变更提案可以删除吗？**  
A: 可以。第 2 阶段是练习，可以删除 `openspec/changes/` 中的练习文件。

**Q: 一定要升级 F01 到 Selenium 吗？**  
A: 不一定。如果只需要监控最新数据，保持现状也很好。第 3 阶段会帮您决定。

**Q: 学完后忘记命令怎么办？**  
A: `openspec --help` 和 `openspec <命令> --help` 随时查看，无需记忆。

---

**路线图版本**：1.0  
**最后更新**：2025-12-14  
**适用**：F01 模块 OpenSpec 学习与开发
