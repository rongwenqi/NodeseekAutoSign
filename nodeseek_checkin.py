import os
import json
import time
import requests
from curl_cffi import requests as cf_requests

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
COOKIE_RAW = os.getenv("NODESEEK_COOKIE")
ACCOUNTS_RAW = os.getenv("NODESEEK_ACCOUNTS")


def send_tg(msg):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=15)
    except Exception:
        pass


def checkin(cookie):
    headers = {
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "referer": "https://www.nodeseek.com/"
    }
    # 保底固定签到，不开启随机鸡腿
    payload = {}
    try:
        resp = cf_requests.post(
            "https://www.nodeseek.com/api/attendance",
            headers=headers,
            json=payload,
            impersonate="chrome124",
            timeout=20
        )
        res = resp.json()
        if res.get("success"):
            return f"✅ NodeSeek保底签到成功！消息：{res.get('message')}"
        else:
            return f"⚠️ NodeSeek签到返回：{res.get('message')}"
    except Exception as e:
        return f"❌ NodeSeek签到失败，异常：{str(e)}"


def main():
    tasks = []
    if COOKIE_RAW:
        tasks.append({"cookie": COOKIE_RAW})
    if ACCOUNTS_RAW:
        try:
            acc_list = json.loads(ACCOUNTS_RAW)
            tasks.extend(acc_list)
        except Exception:
            send_tg("❌ NODESEEK_ACCOUNTS JSON格式错误")
            return
    if not tasks:
        send_tg("❌ 没有配置NodeSeek账号Cookie")
        return

    output_text = "【NodeSeek保底签到结果】\n"
    for idx, item in enumerate(tasks, start=1):
        ret = checkin(item["cookie"])
        output_text += f"\n账号{idx}: {ret}"
        time.sleep(2)
    print(output_text)
    send_tg(output_text)


if __name__ == "__main__":
    main()
