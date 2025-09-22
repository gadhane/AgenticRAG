import requests, urllib.parse
from bs4 import BeautifulSoup
from .util import backoff


class WebTools:
    """
    DuckDuckGo-based web tools (no API key required).
    - search(): scrapes DuckDuckGo HTML results (non-JS endpoint).
    - read(): fetches and cleans page text.
    """
    def __init__(self, search_timeout=6, read_timeout=10, max_retries=2):
        self.search_timeout = search_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries


    def search(self, query: str, k: int = 5):
        base = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        url = f"{base}?{urllib.parse.urlencode(params)}"
        headers = {"User-Agent": "rl-copilot/1.0"}
        for r in range(self.max_retries + 1):
            try:
                resp = requests.get(url, headers=headers, timeout=self.search_timeout)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for a in soup.select("a.result__a"):
                    href = a.get("href")
                    title = a.get_text(strip=True)
                    if href and title:
                        results.append({"title": title, "url": href, "snippet": ""})
                    if len(results) >= k:
                        break
                return results
            except Exception:
                if r == self.max_retries:
                    return []
                import time; time.sleep(backoff(r, 0.6))
        return []


    def read(self, url: str):
        headers = {"User-Agent": "rl-copilot/1.0"}
        for r in range(self.max_retries + 1):
            try:
                resp = requests.get(url, headers=headers, timeout=self.read_timeout)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for s in soup(["script", "style", "nav", "footer", "header"]):
                    s.decompose()
                text = " ".join(soup.get_text(" ").split())
                return text[:15000]
            except Exception:
                if r == self.max_retries:
                    return ""
                import time; time.sleep(backoff(r, 0.6))
        return ""