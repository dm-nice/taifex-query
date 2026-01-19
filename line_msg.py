import os
import sys
import requests
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數中取得資訊
TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GROUP_ID = os.getenv("LINE_GROUP_ID")

def send_to_group(message):
    """發送訊息至 LINE 群組"""
    if not TOKEN or not GROUP_ID:
        print("錯誤：找不到環境變數，請檢查 .env 檔案設定")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    payload = {
        "to": GROUP_ID,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers, json=payload)

    if res.status_code == 200:
        print("成功發送至 LINE 群組")
        return True
    else:
        print(f"錯誤碼：{res.status_code}, 內容：{res.text}")
        return False

def read_file_content(file_path):
    """讀取檔案內容"""
    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 - {file_path}")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python line_msg.py <檔案路徑>")
        print("範例: python line_msg.py C:\\AI\\Taifex\\output\\taifex_night_2026.01.20_v4.md")
        sys.exit(1)

    file_path = sys.argv[1]
    content = read_file_content(file_path)

    if content:
        send_to_group(content)
    
