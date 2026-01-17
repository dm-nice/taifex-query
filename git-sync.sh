#!/bin/bash
cd /home/dm/taifex-query
source venv-linux/bin/activate

# 1. 暫存所有變更，讓工作區變乾淨
echo ">>> Step 1: 暫存本地變更 (Stash)..."
git stash

# 2. 從 GitHub 更新程式碼
echo ">>> Step 2: 從 GitHub 更新..."
git pull --rebase

# 3. 把剛才暫存的變更拿回來
echo ">>> Step 3: 套用本地變更 (Pop)..."
git stash pop

# 4. 再次全部加入並提交
echo ">>> Step 4: 提交並推送..."
git add .
msg="Auto sync at $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$msg"
git push origin main

echo "✅ 流程完成！"
