# Design: add-error-logging

**Change ID**: `add-error-logging`  
**Version**: 1.0  
**Status**: Draft

---

## 🏗️ 设计概述

### 目标
增强 F01 的错误处理，提供更详细的错误信息（时间戳 + 上下文），方便问题诊断。

### 设计原则
1. **最小化改动** - 仅修改必要的函数
2. **向后兼容** - 新参数可选，不影响现有代码
3. **易于扩展** - 上下文用 Dict，便于未来添加更多信息

---

## 📐 技术方案

### 方案 A：增强现有 format_f01_output()（推荐）

```python
def format_f01_output(
    date: str, 
    status: str, 
    data: Optional[Dict] = None, 
    error: Optional[str] = None,
    timestamp: Optional[str] = None,     # 新增
    context: Optional[Dict] = None       # 新增
) -> str:
    """
    格式化 F01 输出为统一文字格式 v5.0
    
    参数:
        date: 日期 (YYYY-MM-DD)
        status: 状态 (success / failed / error)
        data: 成功时的数据字典
        error: 错误信息
        timestamp: [新增] 错误发生时间 (YYYY-MM-DD HH:MM:SS)
        context: [新增] 错误上下文 (如 {"timeout": 30, "url": "..."})
        
    返回:
        格式化的文字字符串
    """
    if status == "success" and data:
        # 成功情况，保持现有逻辑
        ...
    else:
        # 错误情况，增加时间戳和上下文
        error_msg = error or "未知错误"
        
        # 构建错误后缀
        suffix = ""
        if timestamp:
            suffix += f" ({timestamp}"
            
        if context:
            context_str = ", ".join(
                f"{k}={v}{'s' if k == 'timeout' else ''}" 
                for k, v in context.items()
            )
            if suffix:
                suffix += f", {context_str})"
            else:
                suffix += f" ({context_str})"
        elif suffix:
            suffix += ")"
        
        return f"F01 错误: {error_msg} [TAIFEX]{suffix}"
```

**优点**：
- ✅ 修改最小化
- ✅ 向后兼容
- ✅ 易于扩展

**缺点**：
- ❌ 函数签名变长（但影响不大）

---

### 方案 B：创建新函数 format_f01_output_enhanced()

不推荐，会导致代码重复。

---

## 🔄 调用流程

### 当前流程
```
fetch(date) 
  → 捕获错误 
  → format_f01_output(date, "error", error="错误信息") 
  → 返回文字
```

### 改进后流程
```
fetch(date)
  → 捕获错误和时间戳
  → 收集上下文（timeout、url 等）
  → format_f01_output(
      date, "error", 
      error="错误信息",
      timestamp="2025-12-15 14:30:45",
      context={"timeout": 30}
    )
  → 返回带时间戳的错误文字
```

### 代码示例
```python
import time
from datetime import datetime

def fetch(date: str) -> str:
    try:
        # ... 现有代码 ...
        response = requests.get(url, headers=headers, timeout=30)
        
    except requests.Timeout:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return format_f01_output(
            date, 
            "error",
            error="連線逾時，請檢查網路連線",
            timestamp=timestamp,
            context={"timeout": 30}
        )
    
    except requests.HTTPError as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return format_f01_output(
            date,
            "error",
            error=f"HTTP 错误 {e.response.status_code}",
            timestamp=timestamp,
            context={"status_code": e.response.status_code, "url": str(url)}
        )
```

---

## 📊 输出示例

### 成功情况（无变化）
```
F01: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]
```

### 错误情况（新）

#### 有时间戳和上下文
```
F01 错误: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
```

#### 仅有时间戳
```
F01 错误: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX] (2025-12-15 14:30:45)
```

#### 无时间戳（向后兼容）
```
F01 错误: 該日無交易資料（可能是假日或休市日） [TAIFEX]
```

---

## 🧪 测试策略

### 单元测试
```python
# test_f01_auto.py 中新增

def test_format_with_timestamp():
    """测试带时间戳的错误格式"""
    result = format_f01_output(
        date="2025-12-15",
        status="error",
        error="連線逾時",
        timestamp="2025-12-15 14:30:45",
        context={"timeout": 30}
    )
    assert "2025-12-15 14:30:45" in result
    assert "timeout=30s" in result

def test_format_backward_compatible():
    """测试向后兼容（不传新参数）"""
    result = format_f01_output(
        date="2025-12-15",
        status="error",
        error="日期格式錯誤"
    )
    # 输出格式应该完全相同
    assert result == "F01 错误: 日期格式錯誤 [TAIFEX]"

def test_fetch_includes_timestamp():
    """测试 fetch() 调用时包含时间戳"""
    result = fetch("2025-13-01")  # 无效日期
    assert "F01 错误" in result
    assert "202" in result  # 年份中的数字
```

### 集成测试
```bash
# 手动测试各种错误场景
python run.py 2025-13-01 dev --module f01_fetcher_dev   # 日期错误
python run.py 2025-12-15 dev --module f01_fetcher_dev   # 正常
# （需要断网或修改 timeout 以测试网络错误）
```

---

## ⚙️ 实现细节

### 时间戳格式
- 格式：`YYYY-MM-DD HH:MM:SS`
- 时区：本地时区（使用 `datetime.now()`）
- 精度：秒级（不需要毫秒）

### 上下文字典的键值规范
```python
context = {
    "timeout": 30,           # 超时时间（秒），输出时自动添加 "s"
    "status_code": 404,      # HTTP 状态码
    "url": "https://...",    # 请求 URL（仅当相关时）
    "date": "2025-12-15",    # 查询日期（当参数无效时）
}
```

### 日志记录（可选增强）
```python
# 在 format_f01_output() 中添加日志
if status == "error":
    logger.error(
        f"F01 fetcher error",
        extra={
            "error": error,
            "date": date,
            "timestamp": timestamp,
            "context": context
        }
    )
elif status == "failed":
    logger.warning(
        f"F01 fetcher failed",
        extra={"error": error, "date": date}
    )
```

---

## 📋 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 破坏现有代码 | 低 | 高 | 新参数可选，充分测试 |
| 性能下降 | 极低 | 低 | 仅添加字符串操作，开销可忽略 |
| 格式不统一 | 低 | 中 | 定义统一的上下文规范 |

---

## ✅ 完成标准

- [ ] 代码实现完成
- [ ] 单元测试覆盖率 > 90%
- [ ] 集成测试通过
- [ ] 向后兼容性验证
- [ ] 文档更新同步
- [ ] Code review 通过

---

**设计者**: 架构专员  
**最后更新**: 2025-12-15  
**状态**: Draft - 等待评审
