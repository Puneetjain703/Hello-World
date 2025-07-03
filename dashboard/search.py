import dataclasses
import logging
import os
import random
import re
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

# List of trusted domains defined in system_prompt
TRUSTED_DOMAINS = [
    "iea.org",
    "rbi.org.in",
    "mospi.gov.in",
    "niti.gov.in",
    "pib.gov.in",
    "un.org",
    "worldbank.org",
    "reuters.com",
    "thehindu.com",
    "economictimes.indiatimes.com",
    "livemint.com",
]


@dataclasses.dataclass
class SearchResult:
    """Container for a single search result."""

    title: str
    url: str
    snippet: str
    domain: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "domain": self.domain,
        }


class TrustedSourcesSearcher:
    """Performs web search limited to trusted sources using DuckDuckGo Lite HTML interface.

    We avoid the need for API keys by scraping the lightweight HTML version of DuckDuckGo (license perm).
    Note: This is best-effort and may break if DDG layout changes. For production, use an official search API.
    """

    DDG_LITE_ENDPOINT = "https://lite.duckduckgo.com/50x.html"

    def __init__(self, delay_range: tuple[float, float] = (1.0, 2.0)) -> None:
        self.delay_range = delay_range
        self.session = requests.Session()
        # Identify ourselves politely
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0 Safari/537.36"
                )
            }
        )

    def _ddg_query(self, query: str) -> requests.Response:
        """Perform a GET request to DuckDuckGo Lite interface."""
        params = {"q": query, "kl": "in-en"}  # locale India English
        response = self.session.get(self.DDG_LITE_ENDPOINT, params=params, timeout=15)
        response.raise_for_status()
        return response

    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse DDG Lite HTML to extract result blocks."""
        soup = BeautifulSoup(html, "html.parser")
        results: List[SearchResult] = []
        for a in soup.select("a.result-link"):
            url: str = a.get("href") or ""
            title: str = str(a.get_text()).strip()
            parent = a.find_parent("tr")
            snippet_el = parent.find_next_sibling("tr") if parent else None
            snippet: str = str(snippet_el.get_text(" ", strip=True)) if snippet_el else ""
            domain_match = re.match(r"https?://([^/]+)/?", url)
            domain: str = domain_match.group(1) if domain_match else ""
            results.append(SearchResult(title=title, url=url, snippet=snippet, domain=domain))
        return results

    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search trusted domains for query.

        We perform site-restricted queries over all trusted domains and aggregate the results.
        """
        all_results: List[SearchResult] = []
        for domain in TRUSTED_DOMAINS:
            site_query = f"site:{domain} {query}"
            try:
                response = self._ddg_query(site_query)
                parsed = self._parse_results(response.text)
                # Filter again by domain (robustness)
                filtered = [r for r in parsed if domain in r.domain]
                all_results.extend(filtered[: max_results // len(TRUSTED_DOMAINS) + 1])
                # politeness delay
                time.sleep(random.uniform(*self.delay_range))
            except Exception as exc:  # broad catch to continue other domains
                logger.warning("Search failed for domain %s: %s", domain, exc)
                continue
        # Remove duplicates by URL
        seen = set()
        unique_results: List[SearchResult] = []
        for res in all_results:
            if res.url in seen:
                continue
            unique_results.append(res)
            seen.add(res.url)
            if len(unique_results) >= max_results:
                break
        return unique_results