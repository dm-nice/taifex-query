#!/bin/bash

# 1. 先從遠端抓取最新更新，確保本地是最新的
echo ">>> Step 1: 正在從 GitHub 更新..."
git pull --rebase

# 檢查 pull 是否成功 (如果有衝突會停止)
if [ $? -ne 0 ]; then
    echo "錯誤：更新過程中發生衝突，請先手動解決後再執行。"
    exit 1
fi

# 2. 將所有異動加入暫存區
echo ">>> Step 2: 正在加入變更..."
git add .

# 3. 提交變更 (使用當前時間作為預設訊息，你也可以手動修改)
msg="Update at $(date '+%Y-%m-%d %H:%M:%S')"
echo ">>> Step 3: 正在提交變更: $msg"
git commit -m "$msg"

# 4. 推送到遠端
echo ">>> Step 4: 正在推送到 GitHub..."
git push origin main

echo ">>> 完成！所有動作已成功處理。"
