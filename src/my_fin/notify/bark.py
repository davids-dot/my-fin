import requests
from my_fin.config import BARK_URL

def send_notification(title: str, body: str):
    """
    发送 Bark 通知
    """
    if not BARK_URL:
        print(f"[未配置Bark] 通知内容 -> {title}: {body}")
        return
        
    try:
        url = f"{BARK_URL.rstrip('/')}/{title}/{body}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print(f"[Bark 通知发送成功] {title}: {body}")
    except Exception as e:
        print(f"[Bark 通知发送失败] {e}")
