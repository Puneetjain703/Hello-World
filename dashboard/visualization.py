from __future__ import annotations

from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def plot_year_series(
    series: Dict[int, float],
    title: str = "Money flow trend",
    ylabel: str = "USD million",
    figsize: Tuple[int, int] = (8, 4),
) -> plt.Figure:
    """Render a simple line chart for a year->value series and return the Figure."""
    if not series:
        raise ValueError("Empty series provided to plot_year_series")
    years = sorted(series.keys())
    values = [series[y] for y in years]

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(years, values, marker="o")
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    return fig