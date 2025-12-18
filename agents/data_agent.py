import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def data_agent(state: dict):
    url = state["url"]
    max_pages = state.get("max_pages", 3)

    visited, queue = set(), [url]
    base_domain = urlparse(url).netloc
    cro_data = []

    while queue and len(visited) < max_pages:
        current = queue.pop(0)
        if current in visited:
            continue

        try:
            r = requests.get(
                current,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5,
                verify=False
            )
            visited.add(current)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")

                buttons = [b.get_text(strip=True) for b in soup.find_all("button")]
                forms = len(soup.find_all("form"))

                cro_data.append(
                    f"URL:{current} | BUTTONS:{buttons[:5]} | FORMS:{forms}"
                )

                for a in soup.find_all("a", href=True):
                    link = urljoin(current, a["href"])
                    if urlparse(link).netloc == base_domain:
                        queue.append(link)

        except Exception:
            pass

    state["raw_cro_data"] = "\n".join(cro_data)
    return state

