# Change Proposal: add-error-logging

**Change ID**: `add-error-logging`  
**Status**: Draft (未审批)  
**Created**: 2025-12-15  
**Target Module**: F01 Fetcher

---

## 📋 需求概述

当前 F01 的错误处理能力有限，错误信息不够详细，不利于快速定位问题。

### 现状
```python
# 当前的错误返回
F01 错误: 连線逾時，請檢查網路連線 [TAIFEX]
```

### 期望状态
```python
# 希望的错误返回（包含更多信息）
F01 错误: 连線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
```

---

## 🎯 改进目标

1. **增加错误时间戳** - 记录错误发生的确切时间
2. **增加错误上下文** - 记录相关参数（如 timeout 值、请求 URL 等）
3. **改善调试体验** - 让开发者更快定位问题

---

## 📊 影响范围

### 受影响的文件
- `modules/f01_fetcher.py` - 修改 `format_f01_output()` 函数
- `dev/f01_package/f01_fetcher_dev.py` - 同步修改
- `openspec/project.md` - 更新 Code Style 部分

### 受影响的接口
- `format_f01_output(date, status, data, error)` 
  - 新增可选参数 `timestamp` 和 `context`

### 向后兼容性
✅ **完全向后兼容** - 新参数可选，不影响现有调用

---

## 📝 规格变更 (Spec Delta)

### MODIFIED Requirements

#### 需求：增强错误输出格式

**当前**:
```python
def format_f01_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """格式化 F01 输出为统一文字格式 v5.0"""
```

**改为**:
```python
def format_f01_output(
    date: str, 
    status: str, 
    data: Optional[Dict] = None, 
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[Dict] = None
) -> str:
    """格式化 F01 输出为统一文字格式 v5.0（增强错误信息）"""
```

##### Scenario 1: 网络超时错误
- **输入**:
  ```python
  status = "error"
  error = "连線逾時，請檢查網路連線"
  timestamp = "2025-12-15 14:30:45"
  context = {"timeout": 30, "url": "https://www.taifex.com.tw/..."}
  ```
- **输出**:
  ```
  F01 错误: 连線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
  ```
- **说明**: 在错误信息后添加时间戳和关键上下文

##### Scenario 2: 向后兼容（不传递新参数）
- **输入**:
  ```python
  status = "error"
  error = "日期格式錯誤，請使用 YYYY-MM-DD"
  # timestamp 和 context 不提供
  ```
- **输出**:
  ```
  F01 错误: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]
  ```
- **说明**: 不提供新参数时，输出格式不变（向后兼容）

#### 需求：增加错误日志记录

**当前**: 错误仅输出文字，不记录日志

**改为**: 
- 所有 error 状态 → 记录到 ERROR 级别日志
- 所有 failed 状态 → 记录到 WARNING 级别日志
- 包含时间戳、错误信息、上下文

##### Scenario: 日志输出
- **执行**:
  ```python
  result = fetch("2025-13-01")  # 无效日期
  ```
- **日志输出**:
  ```
  2025-12-15 14:30:45,123 [ERROR] [f01_fetcher] 日期格式错误 - error=日期格式錯誤，請使用 YYYY-MM-DD, date=2025-13-01
  ```

---

## 🔍 验收标准

### 功能验收
- [ ] `format_f01_output()` 支持新参数 `timestamp` 和 `context`
- [ ] 新参数可选（不传递时保持现有行为）
- [ ] 错误输出包含时间戳
- [ ] 错误输出包含关键上下文

### 代码质量
- [ ] 所有代码遵循 [project.md](../../openspec/project.md) 中的 Code Style
- [ ] 添加必要的类型注解
- [ ] 添加中文注释说明

### 测试覆盖
- [ ] 编写单元测试验证新参数行为
- [ ] 测试向后兼容性（不传新参数）
- [ ] 测试多种错误场景

### 文档更新
- [ ] 更新 `f01_fetcher_spec.md` 的版本号和说明
- [ ] 更新 `project.md` 的 Code Style 部分（如有变化）

---

## 📅 实施计划

### 任务分解
1. **规格评审** - 确认需求清晰无歧义
2. **代码实现** - 修改 `format_f01_output()` 和 `fetch()` 函数
3. **单元测试** - 编写 test cases
4. **集成测试** - 在 `run.py dev` 模式下验证
5. **文档更新** - 同步规格书和项目文档
6. **代码审查** - 自我检查代码质量

### 预计耗时
- 代码实现：30 分钟
- 测试：20 分钟
- 文档：15 分钟
- 总计：~1 小时

---

## ❓ 待讨论项

- [ ] 是否需要在 `project.md` 中添加错误处理的详细说明？
- [ ] 上下文的详细程度（仅 timeout，还是记录完整请求头？）
- [ ] 日志输出的格式是否需要标准化？

---

**提案状态**: 🟡 Draft - 等待评审  
**下一步**: 讨论、评审、然后实施
