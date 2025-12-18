name: Update README with Project Structure

on:
  schedule:
    - cron: "0 22 * * *"   # UTC 22:00 → 台灣時間隔天 06:00
  workflow_dispatch:       # 手動觸發

jobs:
  update-readme:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.9"

    - name: Generate README structure
      run: |
        python - <<'EOF'
        import os

        def tree(dir_path, prefix=""):
            entries = sorted(os.listdir(dir_path))
            lines = []
            for i, entry in enumerate(entries):
                path = os.path.join(dir_path, entry)
                connector = "├── " if i < len(entries)-1 else "└── "
                lines.append(prefix + connector + entry)
                if os.path.isdir(path) and not entry.startswith(".git"):
                    extension = "│   " if i < len(entries)-1 else "    "
                    lines.extend(tree(path, prefix + extension))
            return lines

        # 產生目錄結構
        structure = "\n".join(tree("."))

        # 更新 README
        readme_path = "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# TAIFEX 自動化查詢專案（每日更新）\n\n")
            f.write("📅 最新更新：每日 06:00 台灣時間\n\n")
            f.write("## 📂 專案目錄結構\n\n")
            f.write("```\n" + structure + "\n```\n\n")
            f.write("本專案每天自動抓取 TAIFEX 資料，並更新目錄結構與分析結果。")
        EOF

    - name: Commit and push results
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add README.md
        git commit -m "docs: 自動更新 README 目錄結構"
        git push



