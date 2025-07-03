from __future__ import annotations

from typing import Dict, List, Tuple


class CitationManager:
    """Tracks unique citations (web sources) and provides numbered tags.

    Usage::
        cm = CitationManager()
        tag = cm.add("https://example.com")   # returns "web:1"
        compiled = cm.render()  # returns list of (tag, url)
    """

    def __init__(self) -> None:
        self._citations: Dict[str, str] = {}
        # Maintains insertion order by default on Py3.7+

    def add(self, url: str) -> str:
        if url in self._citations:
            return self._citations[url]
        tag = f"web:{len(self._citations) + 1}"
        self._citations[url] = tag
        return tag

    def render(self) -> List[Tuple[str, str]]:
        """Return list of (tag, url) in insertion order."""
        # Reverse dict to list of tuples tag, url sorted by tag number
        items = sorted(self._citations.items(), key=lambda kv: int(kv[1].split(":")[1]))
        return [(tag, url) for url, tag in items]

    def inline(self, url: str) -> str:
        """Convenience to return formatted citation string for inline use."""
        return f"[{self.add(url)}]"