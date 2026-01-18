import requests

# 您的 Channel Access Token
TOKEN = "YyFz6dpvNqqHc0M5gEEY4iJMgRVlYQY8YsF7nRRsuiTeMdImY4M64UyLtYBQBh26TEb9KC/gCaQDj0HLVXcX3SfqrW+kUYVEvoDTcATUXtboiacQ8II2TmfaT5AfpHRb+PA9hK32lRpBX+5im7kdkQdB04t89/1O/w1cDnyilFU="

# 您抓到的群組 ID
GROUP_ID = "C06180c9e6ef756d8c4ef6da0f2bc277c" 

def send_to_group(message):
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
        print("✅ 成功發送至多人群組！")
    else:
        print(f"❌ 錯誤碼：{res.status_code}, 內容：{res.text}")

if __name__ == "__main__":
    msg = "📊 Taifex 團隊通知：\nAI 通知助手已成功連線至本群組！\n未來將在此同步盤後數據。"
    send_to_group(msg)