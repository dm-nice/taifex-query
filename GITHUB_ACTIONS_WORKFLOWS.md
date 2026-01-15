# GitHub Actions 工作流配置

## 1. daytime-schedule.yml (F01-F20, 21:00 執行)

**位置**: `.github/workflows/daytime-schedule.yml`

```yaml
name: TAIFEX Daytime Query (F01-F20)

on:
  schedule:
    # 每週一至週五 21:00 執行 (UTC+8)
    # GitHub Actions 時間為 UTC，台灣 UTC+8，所以 21:00 = UTC 13:00
    - cron: '0 13 * * 1-5'

  # 允許手動觸發
  workflow_dispatch:

jobs:
  query:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run daytime query
        run: python daytime_query.py
        env:
          PYTHONUNBUFFERED: 1

      - name: Check for output changes
        id: check_changes
        run: |
          if git diff --quiet output/; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Configure Git
        if: steps.check_changes.outputs.has_changes == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

      - name: Commit and push changes
        if: steps.check_changes.outputs.has_changes == 'true'
        run: |
          git add output/
          git commit -m "feat: TAIFEX daytime data $(date +%Y.%m.%d)"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: daytime-output-${{ github.run_number }}
          path: output/
          retention-days: 30

      - name: Notify on failure
        if: failure()
        run: |
          echo "❌ Daytime query failed"
          exit 1
```

---

## 2. nighttime-schedule.yml (F21-F25, 隔日 05:10 執行)

**位置**: `.github/workflows/nighttime-schedule.yml`

```yaml
name: TAIFEX Nighttime Query (F21-F25)

on:
  schedule:
    # 每週二至週六 05:10 執行 (UTC+8)
    # GitHub Actions 時間為 UTC，台灣 UTC+8，所以 05:10 = UTC 前一天 21:10
    - cron: '10 21 * * 1-5'

  # 允許手動觸發
  workflow_dispatch:

jobs:
  query:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run nighttime query
        run: python nighttime_query.py
        env:
          PYTHONUNBUFFERED: 1

      - name: Check for output changes
        id: check_changes
        run: |
          if git diff --quiet output/; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Configure Git
        if: steps.check_changes.outputs.has_changes == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

      - name: Commit and push changes
        if: steps.check_changes.outputs.has_changes == 'true'
        run: |
          git add output/
          git commit -m "feat: TAIFEX nighttime data $(date +%Y.%m.%d)"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: nighttime-output-${{ github.run_number }}
          path: output/
          retention-days: 30

      - name: Notify on failure
        if: failure()
        run: |
          echo "❌ Nighttime query failed"
          exit 1
```

---

## 3. Cron 表達式解說

### daytime-schedule.yml
```
0 13 * * 1-5
│ │  │ │ │
│ │  │ │ └─ 週一到週五 (1=Mon, 5=Fri)
│ │  │ └─── 每月 (*)
│ │  └────── 每天 (*)
│ └──────── 分鐘 (0 = 整點)
└────────── 小時 (13 = UTC+0, 對應台灣 UTC+8 的 21:00)
```

**台灣時間**: 每週一至週五 21:00
**UTC 時間**: 每週一至週五 13:00

### nighttime-schedule.yml
```
10 21 * * 1-5
│  │  │ │ │
│  │  │ │ └─ 週一到週五 (1=Mon, 5=Fri)
│  │  │ └─── 每月 (*)
│  │  └────── 每天 (*)
│  └──────── 小時 (21 = UTC+0, 對應台灣 UTC+8 前一天的 05:10)
└────────── 分鐘 (10)
```

**台灣時間**: 每週二至週六 05:10 (隔日)
**UTC 時間**: 每週一至週五 21:10 (前一天)

---

## 4. 工作流特性說明

### 共同特性

#### 1. Python 環境
```yaml
python-version: '3.9'
```
- 使用 Python 3.9+
- 確保相容性

#### 2. 依賴快取
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```
- 加速 CI/CD 流程
- 只在 requirements.txt 變更時重新安裝

#### 3. 變更檢測
```yaml
- id: check_changes
  run: |
    if git diff --quiet output/; then
      echo "has_changes=false" >> $GITHUB_OUTPUT
    else
      echo "has_changes=true" >> $GITHUB_OUTPUT
    fi
```
- 只有在有新資料時才提交
- 避免空白提交

#### 4. Git 提交
```yaml
- name: Configure Git
  if: steps.check_changes.outputs.has_changes == 'true'
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"

- name: Commit and push changes
  if: steps.check_changes.outputs.has_changes == 'true'
  run: |
    git add output/
    git commit -m "feat: TAIFEX daytime data $(date +%Y.%m.%d)"
    git push
```
- 自動提交新資料
- 使用標準提交消息格式
- 包含執行日期

#### 5. 工件保存
```yaml
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: daytime-output-${{ github.run_number }}
    path: output/
    retention-days: 30
```
- 保存執行結果
- 便於調試和審計
- 保留 30 天

#### 6. 失敗通知
```yaml
- name: Notify on failure
  if: failure()
  run: |
    echo "❌ Daytime query failed"
    exit 1
```
- 清楚的失敗指示
- 便於 GitHub Actions 日誌追踪

---

## 5. 手動觸發工作流

```yaml
on:
  schedule:
    - cron: '0 13 * * 1-5'
  workflow_dispatch:
```

**在 GitHub 頁面手動執行**:
1. 前往 Actions tab
2. 選擇工作流 (daytime-schedule.yml 或 nighttime-schedule.yml)
3. 點擊 "Run workflow"
4. 選擇分支 (main)
5. 點擊 "Run workflow"

---

## 6. 環境變數

### PYTHONUNBUFFERED
```yaml
env:
  PYTHONUNBUFFERED: 1
```
- 防止 Python 輸出緩衝
- 使日誌實時顯示

### GITHUB_TOKEN
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
- GitHub Actions 自動提供
- 用於 Git push 權限

---

## 7. 監控和調試

### 查看工作流執行

1. **Actions 頁面**: GitHub 倉庫 → Actions tab
2. **查看日誌**: 點擊工作流 → 查看詳細輸出
3. **下載工件**: 點擊工件名稱 → 下載

### 常見問題排查

| 問題 | 原因 | 解決 |
|------|------|------|
| 工作流未執行 | Cron 表達式錯誤 | 驗證 UTC 時間轉換 |
| Python 導入錯誤 | 缺少依賴 | 檢查 requirements.txt |
| Git push 失敗 | 權限不足 | 檢查 GITHUB_TOKEN 設定 |
| 爬蟲失敗 | 網站結構變更 | 檢查選擇器和 xpath |
| 文件創建失敗 | 路徑錯誤 | 檢查 output/ 目錄權限 |

---

## 8. 推薦做法

### 1. 定期測試
```yaml
workflow_dispatch:  # 允許手動測試
```

### 2. 保存工件
```yaml
uses: actions/upload-artifact@v3
```

### 3. 監控執行
- 訂閱 GitHub 通知
- 定期檢查 Actions 日誌

### 4. 版本管理
- 使用 main 分支
- 標記重要版本

### 5. 備份輸出
- 定期備份 output/ 目錄
- 使用 git 歷史記錄

---

## 9. 次要工作流 (選用)

### test-schedule.yml - 單元測試
```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
```

### code-quality.yml - 代碼質量檢查
```yaml
name: Code Quality

on:
  push:
    branches: [ main ]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Black format check
        run: black --check .
      - name: Isort check
        run: isort --check-only .
```

---

## 10. 部署檢查清單

在部署到 GitHub 前，確認：

- [ ] Cron 表達式正確 (UTC 轉換)
- [ ] Python 版本兼容
- [ ] requirements.txt 完整
- [ ] daytime_query.py 和 nighttime_query.py 可運行
- [ ] output/ 目錄已創建
- [ ] .gitignore 已設定
- [ ] 本地測試通過
- [ ] Git 權限已設定
- [ ] GitHub 通知已啟用

