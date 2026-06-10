import requests
import time
from app.config import REQUEST_TIMEOUT, RATE_LIMIT_DELAY, MAX_RETRIES

def fetch_html(url: str) -> str:
    """Shared HTTP fetcher for all extensions"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            time.sleep(RATE_LIMIT_DELAY)
            return response.text
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            time.sleep(RATE_LIMIT_DELAY * 2)