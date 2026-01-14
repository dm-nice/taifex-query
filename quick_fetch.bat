@echo off
setlocal
cd /d "%~dp0"
echo 正在準備環境並抓取數據...
.\venv32\Scripts\python.exe quick_fetch.py %*
if errorlevel 1 (
    echo.
    echo [錯誤] 執行失敗，請檢查網路連線或日期是否正確。
    pause
)
endlocal
