from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .citation import CitationManager
from .search import TrustedSourcesSearcher, SearchResult
from .status import flag_status, StatusFlag
from .parser import extract_year_value_pairs
from .visualization import plot_year_series
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class Dashboard:
    """High-level orchestrator implementing domain logic for India Prediction Dashboard."""

    def __init__(self, max_results: int = 25):
        self.searcher = TrustedSourcesSearcher()
        self.citations = CitationManager()
        self.max_results = max_results

    # ---------------------------------------------------------------------
    # Past predictions
    # ---------------------------------------------------------------------
    def investigate_past_forecasts(
        self, reference_year: int, target_year: int
    ) -> List[Dict[str, str]]:
        """Find archival forecasts around `reference_year` about `target_year`.

        Returns list of dicts with keys: forecast, source, status.
        """
        query = f"India {reference_year} forecast {target_year}"
        logger.info("Searching past forecasts: %s", query)
        results = self.searcher.search(query, max_results=self.max_results)

        processed: List[Dict[str, str]] = []
        for res in results:
            tag = self.citations.add(res.url)
            forecast_text = self._extract_forecast_summary(res)
            status = self._evaluate_past_forecast(forecast_text, target_year)
            processed.append(
                {
                    "forecast": forecast_text,
                    "source": f"{tag}",
                    "url": res.url,
                    "status": status,
                }
            )
        return processed

    def _extract_forecast_summary(self, res: SearchResult) -> str:
        """Naive extraction of forecast summary from snippet/title."""
        text = res.snippet or res.title
        # Clean extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Truncate long
        if len(text) > 300:
            text = text[:297] + "..."
        return text

    def _evaluate_past_forecast(self, text: str, target_year: int) -> StatusFlag:
        """Very naive approach: look for keywords indicating success timing.

        In real system we would fetch full article and parse actual numbers vs realized.
        Here we default to LATE unless keywords show early.
        """
        lowered = text.lower()
        achieved_year: Optional[int] = None
        # Look for patterns like "achieved in 2018" or "reached by 2019"
        m = re.search(r"(19|20)\d{2}", lowered)
        if m:
            yr = int(m.group())
            if 1900 <= yr <= datetime.utcnow().year:
                achieved_year = yr
        return flag_status(target_year, achieved_year=achieved_year)

    # ---------------------------------------------------------------------
    # Future targets
    # ---------------------------------------------------------------------
    def evaluate_future_target(
        self, description: str, target_year: int
    ) -> Dict[str, object]:
        """Search latest evidence for target described, return status flag and citations."""
        query = f"India {description} {target_year} progress"
        logger.info("Searching future target: %s", query)
        results = self.searcher.search(query, max_results=self.max_results)
        # Determine progress
        progress_pct = self._estimate_progress_percent(results)
        status = flag_status(target_year, progress_pct=progress_pct)

        evidence_lines: List[str] = []
        for res in results[:5]:
            tag = self.citations.add(res.url)
            evidence_lines.append(f"{tag}: {res.title}")

        return {
            "description": description,
            "status": status,
            "progress_pct": f"{progress_pct:.0f}%" if progress_pct is not None else "N/A",
            "evidence": evidence_lines,
        }

    def _estimate_progress_percent(self, results: List[SearchResult]) -> Optional[float]:
        """Extract a crude progress percentage from snippets."""
        for res in results:
            m = re.search(r"(\d{1,3})%", res.snippet)
            if m:
                pct = int(m.group(1))
                if 0 <= pct <= 100:
                    return float(pct)
        return None

    # ---------------------------------------------------------------------
    # Money flow trends & visualization
    # ---------------------------------------------------------------------
    def money_flow_data(
        self,
        topic_query: str,
        start_year: int = 2010,
        end_year: Optional[int] = None,
        max_results: int = 25,
    ) -> Dict[int, float]:
        """Return aggregated year->value series parsed from trusted sources snippets."""
        end_year = end_year or datetime.utcnow().year
        query = f"India {topic_query} investment {start_year}-{end_year}"
        logger.info("Searching money flow data: %s", query)
        results = self.searcher.search(query, max_results=max_results)
        series: Dict[int, List[float]] = {}
        for res in results:
            pairs = extract_year_value_pairs(res.snippet + " " + res.title)
            for year, val in pairs:
                if year < start_year or year > end_year:
                    continue
                series.setdefault(year, []).append(val)
            # collect citations even if pairs empty
            self.citations.add(res.url)
        # Aggregate by taking median value per year to reduce outliers
        aggregated: Dict[int, float] = {}
        for year, values in series.items():
            if values:
                values_sorted = sorted(values)
                median_val = values_sorted[len(values) // 2]
                aggregated[year] = median_val
        return aggregated

    def money_flow_chart(
        self,
        topic_query: str,
        start_year: int = 2010,
        end_year: Optional[int] = None,
    ) -> Tuple[Dict[int, float], "plt.Figure"]:
        """Convenience method that returns (series, matplotlib Figure)."""
        series = self.money_flow_data(topic_query, start_year, end_year)
        if not series:
            raise ValueError("Could not extract numeric money-flow data from snippets.")
        title = f"{topic_query.title()} money flow ({start_year}-{end_year or datetime.utcnow().year})"
        fig = plot_year_series(series, title=title, ylabel="USD million")
        return series, fig

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------
    def render_citations(self) -> str:
        lines = [f"{tag}: {url}" for tag, url in self.citations.render()]
        return "\n".join(lines)