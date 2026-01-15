"""
Chrome DevTools MCP 整合模組
用於 taifex-query 和 DGtech 專案的自動化驗證

使用方式：
    from mcp_tools.chrome_integration import ChromeDevToolsVerifier
    
    verifier = ChromeDevToolsVerifier()
    print(verifier.verify_taifex_data_fetch())
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VerificationTask:
    """驗證任務"""
    name: str
    url: str
    checks: List[str]
    description: str = ""
    priority: str = "medium"  # low, medium, high


class ChromeDevToolsVerifier:
    """Chrome DevTools 驗證器 - 用於自動化驗證網頁和資料爬蟲"""
    
    def __init__(self):
        self.tools_available = True
        self.timestamp = datetime.now().isoformat()
    
    # ============= taifex-query 相關驗證 =============
    
    def verify_taifex_data_fetch(self) -> str:
        """
        驗證台期所資料爬蟲 - F14 外資未平倉
        
        Returns:
            可直接複製到 Claude Code 的提示文本
        """
        prompt = """
🔍 【自動驗證】台期所資料爬蟲 - F14 外資未平倉

請幫我驗證以下內容：

1️⃣ **打開目標網頁**
   - 網址: https://www.taifex.com.tw/cht/3/totalTableDate
   - 等待頁面完全載入

2️⃣ **檢查資料載入**
   - 確認「三大法人」表格出現
   - 確認「外資」行的數據正確顯示
   - 特別檢查以下欄位：
     ✓ 外資未平倉 - 多方口數
     ✓ 外資未平倉 - 空方口數
     ✓ 外資未平倉 - 多空淨額

3️⃣ **監控 Network 請求**
   - 打開 DevTools > Network tab
   - 查看所有 API 請求的狀態
   - 確認沒有 5xx 或 4xx 錯誤
   - 記錄任何失敗的請求

4️⃣ **檢查 Console 日誌**
   - 打開 DevTools > Console tab
   - 查看是否有紅色錯誤訊息
   - 記錄任何重要警告

5️⃣ **拍攝驗證截圖**
   - 截圖整個數據表格
   - 截圖 Network tab（如有問題）
   - 截圖 Console（如有錯誤）

📋 **期望結果** (驗證清單)
□ 頁面於 3 秒內載入
□ 外資數據表格可見且內容完整
□ Network 所有請求都是 200 狀態
□ Console 無紅色錯誤訊息
□ 所有 3 個外資欄位都有數值

❌ **如果發現問題**
- 記錄錯誤訊息
- 截圖記錄狀態
- 提供除錯建議

請執行以上驗證，並告訴我結果！
        """
        return prompt
    
    def verify_taifex_data_structure(self) -> str:
        """
        驗證爬蟲資料結構是否正確
        
        Returns:
            驗證清單
        """
        prompt = """
🔍 【資料結構驗證】外資未平倉資料

請驗證爬蟲取得的資料結構：

📊 **期望資料結構**
{
    "date": "2026/01/14",
    "foreign_investor": {
        "open_interest": {
            "long_position": {
                "contracts": 297271,
                "amount_million": 297307
            },
            "short_position": {
                "contracts": 473500,
                "amount_million": 558495
            },
            "net_position": {
                "contracts": -176229,
                "amount_million": -261188
            }
        }
    }
}

✅ **驗證清單**
□ 所有必需字段都存在
□ 數值類型正確（int 或 float）
□ 日期格式為 YYYY/MM/DD
□ 多空淨額的計算公式正確
□ 沒有 null 或缺失值
□ 單位標籤正確（口數、百萬元）

🔧 **驗證命令範例**
```python
import json
from taifex_query import F14

# 取得 F14 資料
data = F14.fetch_foreign_investor_oi()

# 驗證結構
assert "date" in data
assert "foreign_investor" in data
assert "open_interest" in data["foreign_investor"]
print("✓ 資料結構驗證通過")
```
        """
        return prompt
    
    # ============= DGtech 網站相關驗證 =============
    
    def verify_website_page(self, module_name: str, url: str, 
                           expected_elements: Optional[List[str]] = None) -> str:
        """
        驗證網站單個頁面
        
        Args:
            module_name: 模組名稱 (e.g., "M00 - 首頁")
            url: 頁面 URL (e.g., "http://localhost:8000/index.html")
            expected_elements: 期望的頁面元素清單
        
        Returns:
            驗證提示文本
        """
        elements_check = ""
        if expected_elements:
            elements_check = "\n".join([f"   ✓ {elem}" for elem in expected_elements])
        
        prompt = f"""
🔍 【頁面驗證】{module_name}

**目標網址**: {url}

1️⃣ **打開頁面**
   - 在 Chrome 中打開上述網址
   - 等待頁面完全載入（所有資源就緒）

2️⃣ **視覺驗證**
   - 檢查頁面布局是否正確
   - 驗證所有圖片都正確載入
   - 確認所有文字內容可視
   - 檢查色彩和排版
{elements_check}

3️⃣ **功能驗證**
   - 點擊所有按鈕和連結
   - 測試表單輸入（如有）
   - 驗證互動元素反應正常
   - 檢查頁面跳轉功能

4️⃣ **DevTools 檢查**
   - 打開 DevTools (F12)
   - 檢查 Console 標籤：確認無紅色錯誤
   - 檢查 Network 標籤：確認所有資源狀態為 200
   - 檢查 Elements 標籤：驗證 HTML 結構

5️⃣ **效能檢查**
   - 記錄頁面載入時間
   - 檢查 Lighthouse 效能評分
   - 識別任何緩慢的資源

6️⃣ **拍攝截圖**
   - 整個頁面截圖（正常狀態）
   - Console 截圖（確認無錯誤）
   - Network 截圖（如有加載問題）

✅ **驗證清單**
□ 頁面於 2 秒內載入
□ 所有視覺元素正確顯示
□ 所有互動功能運作正常
□ Console 無紅色錯誤
□ Network 所有請求為 200 狀態
□ 響應式設計正常運作（如適用）

📋 **請告訴我**
- 驗證是否全部通過
- 發現的任何問題
- 建議的改進方向
        """
        return prompt
    
    def verify_form_validation(self, form_url: str, form_name: str) -> str:
        """
        驗證表單驗證邏輯
        
        Args:
            form_url: 表單所在頁面的 URL
            form_name: 表單名稱 (e.g., "登入表單")
        
        Returns:
            表單驗證提示
        """
        prompt = f"""
🔍 【表單驗證】{form_name}

**目標網址**: {form_url}

1️⃣ **打開表單頁面**
   - 導航到上述 URL
   - 確認表單可見且可交互

2️⃣ **必填欄位驗證**
   - 不填任何欄位直接提交
   - 驗證是否顯示「欄位必填」的提示
   - 記錄提示訊息

3️⃣ **格式驗證**
   - 測試無效的電子郵件格式（如有）
   - 測試無效的電話號碼格式（如有）
   - 測試密碼強度驗證（如有）
   - 記錄驗證訊息

4️⃣ **邊界值測試**
   - 測試最小/最大長度限制
   - 測試特殊字符處理
   - 測試超長輸入

5️⃣ **提交驗證**
   - 填入有效資料後提交
   - 檢查 Network tab 中的請求
   - 驗證伺服器回應（成功/失敗）
   - 檢查頁面重定向

6️⃣ **DevTools 監控**
   - 監控所有 API 呼叫
   - 記錄請求內容和回應
   - 檢查 Console 中的任何錯誤

✅ **驗證清單**
□ 所有必填欄位驗證正常運作
□ 格式驗證邏輯正確
□ 錯誤訊息清晰易懂
□ 成功提交後正確重定向
□ Network 請求格式正確
□ 無意外的 JavaScript 錯誤

📋 **請告訴我**
- 所有驗證是否通過
- 發現的任何驗證問題
- 用戶體驗改進建議
        """
        return prompt
    
    def verify_api_integration(self, api_endpoint: str) -> str:
        """
        驗證 API 整合
        
        Args:
            api_endpoint: API 端點 (e.g., "/api/users")
        
        Returns:
            API 驗證提示
        """
        prompt = f"""
🔍 【API 驗證】{api_endpoint}

1️⃣ **打開開發者工具**
   - F12 打開 DevTools
   - 切換到 Network 標籤

2️⃣ **觸發 API 呼叫**
   - 執行會呼叫此 API 的操作
   - 在 Network tab 中查找相應的請求

3️⃣ **檢查請求**
   - 驗證 HTTP 方法正確 (GET/POST/PUT/DELETE)
   - 檢查請求標頭是否完整
   - 驗證請求體（如有）格式正確
   - 確認認證令牌正確（如有）

4️⃣ **檢查回應**
   - 驗證回應狀態碼 (200/201 成功，4xx/5xx 失敗)
   - 檢查回應格式 (JSON/XML)
   - 驗證回應時間 (<500ms 為佳)
   - 查看完整的回應內容

5️⃣ **錯誤情況測試**
   - 測試無效輸入的 API 回應
   - 測試超時情況
   - 測試網路中斷後的重試機制

✅ **驗證清單**
□ API 請求格式正確
□ 回應狀態碼符合預期
□ 回應資料格式正確
□ 錯誤處理邏輯有效
□ 回應時間在可接受範圍

📊 **請提供**
- API 請求的完整詳情（截圖）
- API 回應的示例資料
- 任何錯誤信息和狀態碼
        """
        return prompt
    
    # ============= 回歸測試相關 =============
    
    def generate_regression_test_suite(self, modules: List[Dict]) -> str:
        """
        生成回歸測試套件
        
        Args:
            modules: 模組列表 [{"name": "M00", "url": "...", "checks": [...]}]
        
        Returns:
            回歸測試提示
        """
        test_list = "\n".join([
            f"   - {m['name']}: {m['url']}"
            for m in modules
        ])
        
        prompt = f"""
🔄 【回歸測試】完整測試套件

⚠️ **測試順序** (依次執行以下測試)

{test_list}

📋 **每個頁面的驗證步驟**

1. 頁面載入時間 < 3 秒
2. 所有視覺元素正確顯示
3. 所有連結可點擊且目標正確
4. 表單功能正常運作
5. Console 無紅色錯誤
6. Network 無 4xx/5xx 錯誤
7. 響應式設計在各尺寸正常

📊 **測試結果格式**

請以以下格式報告結果：

```
=== 回歸測試報告 ===
測試日期: [日期]
測試環境: Chrome / {os信息}

頁面測試結果:
- M00 首頁: ✅ PASS / ❌ FAIL
- M01 登入: ✅ PASS / ❌ FAIL
- ... (其他頁面)

失敗詳情 (如有):
1. [頁面名稱] - [問題描述]
2. [頁面名稱] - [問題描述]

總結: X/Y 頁面通過測試
```

💡 **提示**
- 遇到失敗時，截圖記錄
- 記錄任何警告訊息
- 如發現多個頁面有相同問題，優先處理
        """
        return prompt
    
    # ============= 效能驗證 =============
    
    def verify_performance_metrics(self, url: str, target_name: str = "網站") -> str:
        """
        驗證效能指標 (Core Web Vitals)
        
        Args:
            url: 目標 URL
            target_name: 目標名稱
        
        Returns:
            效能驗證提示
        """
        prompt = f"""
⚡ 【效能驗證】{target_name} Core Web Vitals

**目標**: {url}

1️⃣ **打開頁面並記錄效能**
   - 打開上述 URL
   - 使用 Lighthouse (DevTools > Lighthouse)
   - 運行「Mobile」和「Desktop」測試

2️⃣ **Core Web Vitals 指標**

   📏 **LCP (Largest Contentful Paint)**
      - 綠色: < 2.5 秒
      - 黃色: 2.5-4.0 秒
      - 紅色: > 4.0 秒

   🎯 **FID (First Input Delay)**
      - 綠色: < 100 毫秒
      - 黃色: 100-300 毫秒
      - 紅色: > 300 毫秒

   📐 **CLS (Cumulative Layout Shift)**
      - 綠色: < 0.1
      - 黃色: 0.1-0.25
      - 紅色: > 0.25

3️⃣ **Lighthouse 檢查**
   - 記錄整體評分 (0-100)
   - 查看各項詳細評分：
     ✓ 效能 (Performance)
     ✓ 可訪問性 (Accessibility)
     ✓ 最佳實踐 (Best Practices)
     ✓ SEO
     ✓ PWA (如適用)

4️⃣ **效能問題分析**
   - 識別 Lighthouse 標記的問題
   - 記錄建議的改進項目
   - 優先順序排列

5️⃣ **截圖記錄**
   - Lighthouse 評分截圖
   - Core Web Vitals 詳細數據截圖
   - 效能問題列表截圖

📊 **效能目標**
□ LCP < 2.5 秒
□ FID < 100 毫秒
□ CLS < 0.1
□ Lighthouse 整體評分 > 80
□ 無嚴重效能問題

💡 **常見問題根源**
- 大型未優化的圖片
- 過多 JavaScript 阻塞渲染
- CSS 未壓縮
- 請求過多或資源過大
- 缺少快取策略

📋 **請提供**
- Lighthouse 完整報告截圖
- Core Web Vitals 各項數據
- 發現的主要問題和建議
        """
        return prompt


# ============= 驗證任務管理器 =============

class VerificationTaskManager:
    """驗證任務管理器 - 組織和追蹤所有驗證任務"""
    
    def __init__(self):
        self.tasks: List[VerificationTask] = []
        self.completed_tasks: List[str] = []
    
    def add_taifex_tasks(self):
        """為 taifex-query 添加驗證任務"""
        self.tasks.extend([
            VerificationTask(
                name="F14 外資未平倉 - 資料爬蟲",
                url="https://www.taifex.com.tw/cht/3/totalTableDate",
                checks=["page_load", "data_present", "network_errors", "console_errors"],
                description="驗證 F14 模組的資料爬蟲功能",
                priority="high"
            ),
            VerificationTask(
                name="F14 資料結構驗證",
                url="local",
                checks=["json_structure", "data_types", "required_fields"],
                description="驗證爬蟲取得的資料格式正確",
                priority="high"
            ),
        ])
    
    def add_dgtech_tasks(self):
        """為 DGtech 網站添加驗證任務"""
        pages = [
            ("M00", "http://localhost:8000/index.html", "首頁"),
            ("M01", "http://localhost:8000/login.html", "登入頁"),
            ("M02", "http://localhost:8000/dashboard.html", "儀表板"),
        ]
        
        for module, url, name in pages:
            self.tasks.append(
                VerificationTask(
                    name=f"{module} - {name}",
                    url=url,
                    checks=["layout", "images", "links", "forms", "console"],
                    description=f"驗證 {name}頁面",
                    priority="medium"
                )
            )
    
    def print_task_summary(self) -> str:
        """生成任務摘要"""
        high_priority = [t for t in self.tasks if t.priority == "high"]
        medium_priority = [t for t in self.tasks if t.priority == "medium"]
        
        summary = f"""
📋 【驗證任務摘要】

🔴 高優先級 ({len(high_priority)} 個):
{chr(10).join(f"  - {t.name}" for t in high_priority)}

🟡 中優先級 ({len(medium_priority)} 個):
{chr(10).join(f"  - {t.name}" for t in medium_priority)}

已完成: {len(self.completed_tasks)}/{len(self.tasks)}
        """
        return summary


# ============= 使用範例 =============

if __name__ == "__main__":
    # 建立驗證器
    verifier = ChromeDevToolsVerifier()
    
    # 範例 1: 驗證 taifex 資料爬蟲
    print("=" * 60)
    print("【taifex-query F14 驗證提示】")
    print("=" * 60)
    print(verifier.verify_taifex_data_fetch())
    
    # 範例 2: 驗證網站頁面
    print("\n" + "=" * 60)
    print("【DGtech 網站頁面驗證提示】")
    print("=" * 60)
    print(verifier.verify_website_page(
        "M00 - 首頁",
        "http://localhost:8000/index.html",
        expected_elements=["導航欄", "大標題", "按鈕", "頁腳"]
    ))
    
    # 範例 3: 任務管理
    print("\n" + "=" * 60)
    print("【驗證任務管理】")
    print("=" * 60)
    manager = VerificationTaskManager()
    manager.add_taifex_tasks()
    manager.add_dgtech_tasks()
    print(manager.print_task_summary())
