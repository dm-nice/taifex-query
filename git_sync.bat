@echo off
:: ---------------------------------------------------------
:: 通用版設定 (含自動提交功能)
:: ---------------------------------------------------------
chcp 65001 >nul

echo.
echo [1/5] 🔍 尋找並啟動 Python 虛擬環境...
set "VENV_PATH="
if exist ".\venv32-win\Scripts\activate.bat" set "VENV_PATH=.\venv32-win\Scripts\activate.bat"
if exist ".\venv32\Scripts\activate.bat"     set "VENV_PATH=.\venv32\Scripts\activate.bat"
if exist ".\venv\Scripts\activate.bat"       set "VENV_PATH=.\venv\Scripts\activate.bat"
if exist ".\.venv\Scripts\activate.bat"      set "VENV_PATH=.\.venv\Scripts\activate.bat"

if defined VENV_PATH (
    echo ✅ 找到虛擬環境： %VENV_PATH%
    call "%VENV_PATH%"
) else (
    echo ⚠️  沒有找到常見的虛擬環境 (將跳過啟動)
)

:: ---------------------------------------------------------
:: 新增步驟：自動提交 (Auto-Commit)
:: ---------------------------------------------------------
echo.
echo [2/5] 💾 檢查並提交本地變更...

:: 將所有變更加入暫存區
git add .

:: 嘗試提交，訊息設為 "Auto-save before sync"
:: 如果沒有東西需要提交，這一行會說 "nothing to commit" (不會報錯)
git commit -m "Auto-save: 自動同步前存檔"

:: ---------------------------------------------------------
:: Git 同步流程
:: ---------------------------------------------------------
echo.
echo [3/5] 🔄 拉取 GitHub 最新版本（Rebase 模式）...
git pull --rebase origin main

if %errorlevel% neq 0 (
    echo.
    echo 🛑 嚴重警告：更新發生衝突！即使自動提交後仍有衝突。
    echo    請手動解決衝突後再執行。
    pause
    exit /b %errorlevel%
)

echo.
echo [4/5] 🚀 推送本地更新到 GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ 推送失敗，請檢查網路。
    pause
    exit /b %errorlevel%
)

echo.
echo [5/5] 📜 專案目前的 Git 狀態...
git branch -v
echo.
echo --- 最近的 10 筆提交記錄 ---
git log --oneline --graph --all -n 10

echo.
echo ✅ 作業全部完成！
pause