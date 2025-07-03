from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

StatusFlag = Literal["EARLY", "ON-TIME", "LATE", "LATE-RISK"]


def flag_status(
    target_year: int,
    current_year: Optional[int] = None,
    progress_pct: Optional[float] = None,
    achieved_year: Optional[int] = None,
) -> StatusFlag:
    """Return status flag for a milestone.

    Parameters
    ----------
    target_year: int
        Year the milestone is supposed to be achieved.
    current_year: int, optional
        Defaults to current calendar year.
    progress_pct: float, optional
        Percent progress towards milestone (0-100) if known.
    achieved_year: int, optional
        Year when milestone was actually achieved (for past targets).
    """
    current_year = current_year or datetime.utcnow().year

    # Past-looking evaluation
    if achieved_year is not None:
        if achieved_year < target_year:
            return "EARLY"
        elif achieved_year == target_year:
            return "ON-TIME"
        else:
            return "LATE"

    # Future-looking evaluation
    years_left = target_year - current_year
    if years_left <= 0:
        # Target year already passed but no achieved_year given -> treat as late
        return "LATE"

    # If progress known, project simple linear extrapolation
    if progress_pct is not None:
        # Assume linear growth; determine required annual pace
        elapsed_years = target_year - years_left - (target_year - current_year)
        # Correction: elapsed_years = total timeframe minus years_left.
        total_span = target_year - (current_year - (years_left))
        if total_span <= 0:
            total_span = 1
        fraction_time_elapsed = (total_span - years_left) / total_span
        expected_progress = fraction_time_elapsed * 100
        # Compare progress vs expected
        if progress_pct >= expected_progress + 10:
            return "EARLY"  # ahead
        elif abs(progress_pct - expected_progress) <= 10:
            return "ON-TIME"
        else:
            return "LATE-RISK"

    # If no progress data, default to ON-TIME for targets within 2 years else LATE-RISK.
    if years_left <= 2:
        return "ON-TIME"
    return "LATE-RISK"