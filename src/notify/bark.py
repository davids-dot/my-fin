import requests
from config import BARK_URL, logger

def send_notification(title: str, body: str):
    """
    发送 Bark 通知
    """
    if not BARK_URL:
        logger.info(f"[未配置Bark] 通知内容 -> {title}: {body}")
        return
        
    try:
        url = f"{BARK_URL.rstrip('/')}/{title}/{body}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        logger.info(f"[Bark 通知发送成功] {title}: {body}")
    except requests.exceptions.RequestException as e:
        logger.error(f"[Bark 通知发送失败] {e}", exc_info=True)
