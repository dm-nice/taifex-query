name: Update README with Project Structure

on:
  schedule:
    # 每天 22:00 UTC -> 台灣隔天早上 6:00
    - cron: '0 22 * * *'
  workflow_dispatch:

jobs:
  update-readme:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout repository
      uses: actions/checkout@v4

    - name: 🌳 Generate project structure
      id: tree
      run: |
        # 排除不必要的目錄和檔案
        ls -R | grep -v -e '.git' -e '.github' -e '.vscode' -e 'venv' -e '__pycache__' -e '.pytest_cache' > project_structure.txt
    
    - name: 📝 Update README.md
      run: |
        {
          echo "# TAIFEX 自動化查詢專案（每日更新）"
          echo ""
          echo "📅 最新更新：每日 06:00 台灣時間"
          echo ""
          echo "## 📂 專案目錄結構"
          echo ""
          echo '```'
          cat project_structure.txt
          echo '```'
          echo ""
          echo "本專案每天自動抓取 TAIFEX 資料，並更新目錄結構與分析結果。"
        } > README.md

    - name: 💾 Commit and push README
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        # 檢查 README.md 是否有變更
        if ! git diff --quiet README.md; then
          git add README.md
          git commit -m "docs: 🤖 自動更新 README 目錄結構"
          git push
        else
          echo "✅ README.md is already up-to-date."
        fi
