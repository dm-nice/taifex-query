

Write-Host ">>> Starting Windows Auto Sync..." -ForegroundColor Cyan

# 1. Stash and Pull
Write-Host ">>> Step 1: Stash local changes and Pulling..." -ForegroundColor Yellow
git add .
git stash
git pull --rebase

# 2. Pop and Add
Write-Host ">>> Step 2: Applying local changes..." -ForegroundColor Yellow
git stash pop
git add .

# 3. Commit and Push
$msg = "Win Update at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m "$msg"
Write-Host ">>> Step 3: Pushing to GitHub: $msg" -ForegroundColor Yellow
git push origin main

Write-Host "✅ Done! Windows and N100 are synchronized." -ForegroundColor Green