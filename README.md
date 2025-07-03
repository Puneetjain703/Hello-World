# Hello-World

I love to bike upside down and reverse to the wind.

# India Prediction Dashboard (Core Library)

This repository implements the **core logic** behind the _India Prediction Dashboard_ described in the product brief.  It focuses on four pillars:

1. **Trusted-source web search** (`dashboard.search`)
2. **Citation manager** that emits numbered `web:` tags (`dashboard.citation`)
3. **Status flagging engine** evaluating **EARLY / ON-TIME / LATE / LATE-RISK** (`dashboard.status`)
4. **High-level orchestrator** combining the above to process past forecasts and future targets (`dashboard.core`).

## Quick start

```bash
# (Inside the project root)
pip install --break-system-packages -r requirements.txt  # or use a venv

python - << 'PY'
from dashboard.core import Dashboard

dash = Dashboard()

# Example – evaluate 450 GW renewables target for 2030
result = dash.evaluate_future_target("450 GW renewables", 2030)
print(result)
print("\n--- citations ---\n" + dash.render_citations())
PY
```

The first call will perform live DuckDuckGo searches restricted to domains such as `iea.org`, `pib.gov.in`, `worldbank.org`, etc., then infer a status flag and manage inline citations.

_Note_: For production‐grade use you would swap out the scraping‐based `TrustedSourcesSearcher` for an official search API and implement detailed parsers for numerical extraction.
