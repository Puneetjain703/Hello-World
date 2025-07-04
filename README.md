# 🇮🇳 India Prediction Dashboard (Auto-Fetch)

A comprehensive dashboard that analyzes India's past and future predictions across a 200-year span (100 years back to 100 years ahead) in 5-year intervals. The system compares historical forecasts with actual outcomes and predicts the likelihood of future targets being achieved.

## 🌟 Features

### Core Capabilities
- **Historical Analysis**: Compare past forecasts (1924-2024) with actual outcomes
- **Future Predictions**: Analyze current targets and predict likelihood of achievement
- **Multi-Sector Coverage**: Economy, Energy, Infrastructure, Technology, Agriculture, Education, Healthcare, Environment, Social Development
- **Real-Time Data**: Auto-fetches data from trusted sources (IEA, RBI, MoSPI, NITI Aayog, World Bank, etc.)
- **Interactive Visualizations**: Charts, graphs, and dashboards for data exploration

### Classification System
- 🟢 **LIKELY EARLY**: Targets likely to be achieved ahead of schedule
- 🟡 **ON-TIME**: Targets on track for timely completion
- 🔴 **LATE-RISK**: Targets at risk of delays or underachievement

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd india-prediction-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run dashboard.py
   ```

4. **Access the dashboard**
   Open your browser and go to `http://localhost:8501`

## 📊 Usage Examples

### Conversation Starters
- "Which 1975 Indian predictions about 2025 actually happened?"
- "Is India's 450 GW renewables target for 2030 on track?"
- "Show a chart of VC inflows into climate tech vs software since 2010"

### Query Types

#### 1. Past Forecast Analysis
```python
# Example: Analyze forecasts made in 1975 about 2000
forecast_year = 1975
target_year = 2000
sectors = ["Economy", "Energy"]
sources = ["Planning Commission", "RBI"]
```

#### 2. Future Prediction Analysis
```python
# Example: Analyze current predictions for 2030
target_year = 2030
sectors = ["Energy", "Infrastructure"]
sources = ["NITI Aayog", "World Bank"]
```

#### 3. Trend Comparison
```python
# Example: Compare trends from 2000 to 2030
start_year = 2000
end_year = 2030
sectors = ["Economy", "Technology"]
```

## 🏗️ Architecture

### Components

1. **Dashboard Core** (`dashboard.py`)
   - Main Streamlit application
   - User interface and interaction handling
   - Query processing and result display

2. **Data Sources** (`data_sources.py`)
   - Integration with multiple data sources
   - API calls and web scraping
   - Data caching and management

3. **Prediction Engine** (`prediction_engine.py`)
   - Forecast vs. actual comparison logic
   - Future likelihood analysis
   - Natural language query processing

4. **Visualization** (`visualization.py`)
   - Interactive charts and graphs
   - Dashboard summary visualizations
   - Export capabilities

5. **Configuration** (`config.py`)
   - Settings and constants
   - Data source configurations
   - Historical data samples

### Data Sources

#### Government Sources
- **RBI**: Reserve Bank of India (Monetary policy, economic data)
- **MoSPI**: Ministry of Statistics (GDP, inflation, industrial data)
- **NITI Aayog**: Policy think tank (development targets, strategies)
- **PIB**: Press Information Bureau (Government announcements)

#### International Sources
- **World Bank**: Economic indicators, development data
- **IEA**: International Energy Agency (Energy statistics, forecasts)
- **UN DESA**: United Nations Department of Economic and Social Affairs

#### Media Sources
- **Reuters**: News and financial data
- **The Hindu**: National news archives
- **Economic Times**: Business and economic news
- **Mint**: Financial news and analysis

## 📈 Supported Sectors

### 1. Economy
- GDP growth rates
- Per capita income
- Inflation rates
- Economic reforms impact

### 2. Energy
- Power generation capacity
- Renewable energy targets
- Coal production
- Energy security metrics

### 3. Infrastructure
- Railway network expansion
- Highway development
- Airport capacity
- Port infrastructure

### 4. Technology
- Internet penetration
- Mobile connectivity
- Digital India initiatives
- IT sector growth

### 5. Agriculture
- Food production
- Crop yields
- Irrigation coverage
- Agricultural reforms

### 6. Education
- Literacy rates
- School enrollment
- Higher education capacity
- Skill development

### 7. Healthcare
- Life expectancy
- Infant mortality rates
- Healthcare infrastructure
- Medical coverage

### 8. Environment
- Forest cover
- Carbon emissions
- Air quality indices
- Climate targets

### 9. Social Development
- Poverty reduction
- Human Development Index
- Social welfare programs
- Inclusive growth metrics

## 🎯 Prediction Methodology

### Historical Analysis
1. **Data Collection**: Fetch historical forecasts from archives
2. **Matching**: Align predictions with actual outcomes
3. **Classification**: Categorize as EARLY, ON-TIME, or LATE
4. **Pattern Recognition**: Identify sectoral accuracy patterns

### Future Likelihood Assessment
1. **Progress Analysis**: Current achievement vs. targets
2. **Sectoral Patterns**: Apply historical accuracy weights
3. **Indicator Analysis**: Check for early/late indicators
4. **Time Horizon**: Adjust confidence based on timeframe
5. **Risk Assessment**: Identify potential delays or accelerators

### Confidence Scoring
- **High Confidence** (>80%): Strong historical accuracy, clear progress
- **Medium Confidence** (60-80%): Moderate accuracy, some uncertainty
- **Low Confidence** (<60%): High uncertainty, limited data

## 📊 Visualization Features

### Chart Types
- **Pie Charts**: Accuracy distribution, likelihood statistics
- **Bar Charts**: Sector comparisons, trend analysis
- **Line Charts**: Time series, progress tracking
- **Scatter Plots**: Confidence analysis, correlation studies
- **Gauge Charts**: Progress indicators, target achievement
- **Heatmaps**: Multi-dimensional data visualization

### Interactive Features
- **Hover Details**: Detailed information on data points
- **Zoom/Pan**: Explore data at different scales
- **Export Options**: PNG, PDF, HTML formats
- **Real-time Updates**: Live data refresh capabilities

## 🔧 Configuration

### Environment Variables
```bash
DEBUG=False                    # Enable debug mode
CACHE_DURATION=3600           # Cache duration in seconds
API_TIMEOUT=30                # API request timeout
MAX_RETRIES=3                 # Maximum retry attempts
```

### Data Source Settings
```python
# In config.py
DATA_SOURCE_TIMEOUT = 30      # seconds
MAX_RETRIES = 3
REQUEST_DELAY = 1             # seconds between requests
```

### Classification Thresholds
```python
ACCURACY_THRESHOLDS = {
    'strict': 0.05,     # 5% tolerance
    'moderate': 0.15,   # 15% tolerance
    'loose': 0.25       # 25% tolerance
}
```

## 📁 File Structure

```
india-prediction-dashboard/
├── dashboard.py              # Main application
├── data_sources.py          # Data fetching and management
├── prediction_engine.py     # Analysis and prediction logic
├── visualization.py         # Chart generation
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # Data storage
├── cache/                 # Cached data
├── exports/               # Exported visualizations
└── logs/                  # Application logs
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Make your changes
5. Add tests for new features
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Write comprehensive tests

## 📋 API Reference

### DataSourceManager
```python
# Fetch historical forecasts
forecasts = data_manager.fetch_historical_forecasts(
    forecast_year=1975,
    target_year=2000,
    sectors=["Economy"],
    sources=["RBI"]
)

# Fetch current predictions
predictions = data_manager.fetch_current_predictions(
    target_year=2030,
    sectors=["Energy"],
    sources=["NITI Aayog"]
)
```

### PredictionEngine
```python
# Compare forecasts vs actuals
results = prediction_engine.compare_forecasts_vs_actuals(
    forecasts, actuals
)

# Analyze future likelihood
analysis = prediction_engine.analyze_future_likelihood(
    predictions, target_year=2030
)
```

### ChartGenerator
```python
# Create accuracy pie chart
chart = chart_generator.create_accuracy_pie_chart(
    accuracy_stats, title="Forecast Accuracy"
)

# Create trend chart
trend_chart = chart_generator.create_trend_chart(
    trend_data, title="Economic Growth Trends"
)
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   ```

2. **Data Source Timeouts**
   ```python
   # Increase timeout in config.py
   DATA_SOURCE_TIMEOUT = 60
   ```

3. **Memory Issues**
   ```python
   # Reduce cache duration
   CACHE_DURATION_SECONDS = 1800
   ```

4. **Visualization Errors**
   ```bash
   # Install additional visualization dependencies
   pip install kaleido
   ```

### Performance Tips
- Use caching for frequently accessed data
- Limit the number of concurrent API requests
- Adjust visualization complexity based on data size
- Monitor memory usage for large datasets

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Government of India for providing open data access
- World Bank for comprehensive development indicators
- IEA for energy statistics and forecasts
- All news organizations for historical archives
- Open source community for tools and libraries

## 📞 Support

For support, please:
1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed description
4. Include relevant logs and error messages

---

**Built with ❤️ for India's development journey**
