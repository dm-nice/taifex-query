@echo off
REM 本地測試 GitHub Actions 工作流程
REM 在 push 到 GitHub 前，先確認程式能正常執行

echo ========================================
echo 測試 GitHub Actions 工作流程 (本地版)
echo ========================================
echo.

REM 獲取今天日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TODAY=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

echo 測試日期: %TODAY%
echo.

REM 測試 1: 檢查 Python 環境
echo [1/4] 檢查 Python 環境...
python --version
if errorlevel 1 (
    echo 錯誤: Python 未安裝或不在 PATH 中
    pause
    exit /b 1
)
echo ✓ Python 環境正常
echo.

REM 測試 2: 檢查依賴套件
echo [2/4] 檢查依賴套件...
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo 警告: selenium 未安裝，正在安裝...
    pip install -r requirements.txt
)
echo ✓ 依賴套件正常
echo.

REM 測試 3: 執行資料抓取 (只測試一個模組)
echo [3/4] 測試資料抓取 (F01)...
python run.py %TODAY% --module f01_fetcher
if errorlevel 1 (
    echo 警告: 資料抓取可能有問題，請檢查錯誤訊息
) else (
    echo ✓ 資料抓取測試成功
)
echo.

REM 測試 4: 檢查輸出檔案
echo [4/4] 檢查輸出檔案...
if exist "data\%TODAY:~0,4%-%TODAY:~5,2%-%TODAY:~8,2%*f01*.txt" (
    echo ✓ 找到輸出檔案
    dir /b data\%TODAY:~0,4%-%TODAY:~5,2%-%TODAY:~8,2%*f01*.txt
) else (
    echo 警告: 找不到輸出檔案
)
echo.

echo ========================================
echo 測試完成！
echo ========================================
echo.
echo 如果以上測試都正常，可以執行以下指令 push 到 GitHub:
echo.
echo   git add .github/workflows/ requirements.txt GITHUB_SETUP.md
echo   git commit -m "feat: Add GitHub Actions workflows"
echo   git push origin main
echo.
pause
