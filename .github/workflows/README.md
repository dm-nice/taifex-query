組件,說明
Workflow,整個自動化的過程，存放在 .github/workflows/ 資料夾中。
Events,觸發自動化的事件（例如：push 程式碼、開啟 pull_request）。
Jobs,一個 Workflow 由多個 Job 組成，預設是平行執行的。
Steps,Job 內部的細節步驟，會按順序執行指令或 Action。
Actions,預先封裝好的功能模組（例如：設定 Python 環境、登入 Docker）。
Runners,"執行工作流程的伺服器（GitHub 預設提供 Ubuntu, Windows, macOS）。"





2. 如何設定（實作步驟）
第一步：建立路徑
在你的專案根目錄下，必須建立一個特殊的資料夾結構： .github/workflows/

第二步：建立 YAML 設定檔
在該資料夾內建立一個檔案，例如 ci.yml。GitHub 會自動偵測這個路徑下的所有 .yml 檔案。

第三步：撰寫指令
這是一個基礎的範例，當有人 Push 程式碼到 main 分支時，會自動印出 "Hello World"：

YAML

name: My First Action  # 工作流程名稱

on:                   # 什麼時候觸發？
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:                  # 要做什麼事？
  build:
    runs-on: ubuntu-latest  # 使用哪種伺服器執行

    steps:             # 執行的步驟
      - name: Checkout code  # 第一步：把程式碼下載到伺服器
        uses: actions/checkout@v4

      - name: Run a script   # 第二步：執行自定義指令
        run: echo "Hello, GitHub Actions!"
        
        
        3. 常用功能與語法
常用觸發條件 (on)
除了 push，你也可以設定定時觸發：

YAML

on:
  schedule:
    - cron: '0 0 * * *'  # 每天午夜執行一次
  workflow_dispatch:      # 允許手動從網頁按按鈕觸發
使用預設 Actions
GitHub 有個 Marketplace，你可以直接引用別人寫好的功能：

actions/setup-node@v4：設定 Node.js 環境。

actions/setup-python@v5：設定 Python 環境。

actions/upload-artifact@v4：將構建好的檔案（如 .exe 或 .zip）存檔。

4. 如何查看結果
將你的 .github/workflows/ci.yml 推送到 GitHub。

點擊儲存庫上方的 "Actions" 分頁。

在左側選擇你的 Workflow 名稱。

點進去具體的執行紀錄，你可以看到每一行指令的輸出 log。

5. 為什麼要用 GitHub Actions？
免費額度高： 公開儲存庫完全免費；私有儲存庫每月有 2,000 分鐘的免費額度。

生態系完整： 幾乎所有主流技術（Docker, AWS, Azure, NPM）都有現成的 Action 可以直接用。

高度整合： 不需額外架設 Jenkins 或伺服器。

你想為特定語言（例如 Python 測試 或 Node.js 部署）建立工作流程嗎？我可以幫你寫一個更精確的範例。
        
        