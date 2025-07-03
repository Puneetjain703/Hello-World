"""
India Prediction Dashboard (Auto-Fetch)
========================================

Answers questions about India's past and future—100 years back to 100 years ahead—
in 5-year steps. Compares earlier forecasts with what really happened and flags
future targets as Likely EARLY, ON-TIME, or LATE.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from data_sources import DataSourceManager
from prediction_engine import PredictionEngine
from visualization import ChartGenerator

class IndiaPredictionDashboard:
    """Main dashboard class for India Prediction Dashboard"""
    
    def __init__(self):
        self.data_manager = DataSourceManager()
        self.prediction_engine = PredictionEngine()
        self.chart_generator = ChartGenerator()
        self.current_year = datetime.now().year
        
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="India Prediction Dashboard",
            page_icon="🇮🇳",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🇮🇳 India Prediction Dashboard")
        st.markdown("""
        **Answers questions about India's past and future—100 years back to 100 years ahead—in 5-year steps.**
        
        Compare earlier forecasts with what really happened and flags future targets as:
        - 🟢 **LIKELY EARLY** 
        - 🟡 **ON-TIME**
        - 🔴 **LATE-RISK**
        
        *All evidence pulled from trusted public sources (IEA, RBI, MoSPI, NITI Aayog, PIB, UN DESA, World Bank, Reuters, The Hindu, ET, Mint)*
        """)
        
    def render_sidebar(self):
        """Render the sidebar with controls"""
        st.sidebar.header("Dashboard Controls")
        
        # Query type selection
        query_type = st.sidebar.selectbox(
            "Select Query Type",
            ["Past Forecast Analysis", "Future Prediction Analysis", "Trend Comparison", "Custom Query"]
        )
        
        # Year range selection
        st.sidebar.subheader("Year Range")
        if query_type == "Past Forecast Analysis":
            forecast_year = st.sidebar.slider(
                "Forecast Made In Year", 
                1924, self.current_year - 5, 1975
            )
            target_year = st.sidebar.slider(
                "Target Year of Forecast", 
                forecast_year + 5, self.current_year, 2000
            )
        elif query_type == "Future Prediction Analysis":
            target_year = st.sidebar.slider(
                "Target Year", 
                self.current_year, self.current_year + 100, 2030
            )
            forecast_year = None
        else:
            start_year = st.sidebar.slider("Start Year", 1924, self.current_year + 100, 2000)
            end_year = st.sidebar.slider("End Year", start_year, self.current_year + 100, 2030)
            forecast_year, target_year = start_year, end_year
            
        # Sector selection
        sectors = st.sidebar.multiselect(
            "Select Sectors",
            ["Economy", "Energy", "Infrastructure", "Technology", "Agriculture", 
             "Education", "Healthcare", "Environment", "Social Development"],
            default=["Economy", "Energy"]
        )
        
        # Data sources
        sources = st.sidebar.multiselect(
            "Preferred Data Sources",
            ["IEA", "RBI", "MoSPI", "NITI Aayog", "PIB", "UN DESA", "World Bank", 
             "Reuters", "The Hindu", "Economic Times", "Mint", "Planning Commission"],
            default=["RBI", "NITI Aayog", "World Bank"]
        )
        
        return {
            "query_type": query_type,
            "forecast_year": forecast_year,
            "target_year": target_year,
            "sectors": sectors,
            "sources": sources
        }
    
    def analyze_past_forecasts(self, forecast_year: int, target_year: int, 
                             sectors: List[str], sources: List[str]) -> Dict:
        """Analyze past forecasts and their accuracy"""
        st.header(f"📊 Past Forecast Analysis: {forecast_year} → {target_year}")
        
        with st.spinner("Fetching historical forecasts and actual data..."):
            # Fetch historical forecasts
            forecasts = self.data_manager.fetch_historical_forecasts(
                forecast_year, target_year, sectors, sources
            )
            
            # Fetch actual outcomes
            actuals = self.data_manager.fetch_actual_outcomes(
                target_year, sectors
            )
            
            # Compare and classify
            results = self.prediction_engine.compare_forecasts_vs_actuals(
                forecasts, actuals
            )
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Forecast vs Reality")
            if results:
                for sector, data in results.items():
                    with st.expander(f"{sector} Forecasts"):
                        for forecast in data.get('forecasts', []):
                            status_color = {
                                'EARLY': '🟢',
                                'ON-TIME': '🟡', 
                                'LATE': '🔴'
                            }.get(forecast.get('status', 'UNKNOWN'), '⚪')
                            
                            st.markdown(f"""
                            {status_color} **{forecast.get('metric', 'Unknown')}**
                            - **Forecast ({forecast_year})**: {forecast.get('predicted_value', 'N/A')}
                            - **Actual ({target_year})**: {forecast.get('actual_value', 'N/A')}
                            - **Status**: {forecast.get('status', 'Unknown')}
                            - **Source**: {forecast.get('source', 'Unknown')}
                            """)
            else:
                st.warning("No historical forecast data found for the specified parameters.")
        
        with col2:
            st.subheader("Accuracy Summary")
            if results:
                accuracy_data = self.prediction_engine.calculate_accuracy_stats(results)
                
                # Create pie chart
                fig = px.pie(
                    values=list(accuracy_data.values()),
                    names=list(accuracy_data.keys()),
                    title="Forecast Accuracy Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        return results
    
    def analyze_future_predictions(self, target_year: int, sectors: List[str], 
                                 sources: List[str]) -> Dict:
        """Analyze current predictions for future targets"""
        st.header(f"🔮 Future Prediction Analysis: Current → {target_year}")
        
        with st.spinner("Fetching latest forecasts and analyzing trends..."):
            # Fetch current predictions
            predictions = self.data_manager.fetch_current_predictions(
                target_year, sectors, sources
            )
            
            # Analyze likelihood based on historical patterns
            analysis = self.prediction_engine.analyze_future_likelihood(
                predictions, target_year
            )
        
        # Display predictions with likelihood assessment
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Current Predictions & Likelihood")
            if analysis:
                for sector, data in analysis.items():
                    with st.expander(f"{sector} Predictions"):
                        for prediction in data.get('predictions', []):
                            likelihood_color = {
                                'LIKELY EARLY': '🟢',
                                'ON-TIME': '🟡',
                                'LATE-RISK': '🔴'
                            }.get(prediction.get('likelihood', 'UNKNOWN'), '⚪')
                            
                            st.markdown(f"""
                            {likelihood_color} **{prediction.get('metric', 'Unknown')}**
                            - **Target ({target_year})**: {prediction.get('target_value', 'N/A')}
                            - **Current Progress**: {prediction.get('current_progress', 'N/A')}
                            - **Likelihood**: {prediction.get('likelihood', 'Unknown')}
                            - **Reasoning**: {prediction.get('reasoning', 'N/A')}
                            - **Source**: {prediction.get('source', 'Unknown')}
                            """)
            else:
                st.warning("No current prediction data found for the specified parameters.")
        
        with col2:
            st.subheader("Likelihood Distribution")
            if analysis:
                likelihood_data = self.prediction_engine.calculate_likelihood_stats(analysis)
                
                # Create bar chart
                fig = px.bar(
                    x=list(likelihood_data.keys()),
                    y=list(likelihood_data.values()),
                    title="Future Target Likelihood",
                    color=list(likelihood_data.keys()),
                    color_discrete_map={
                        'LIKELY EARLY': 'green',
                        'ON-TIME': 'orange', 
                        'LATE-RISK': 'red'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        return analysis
    
    def show_trend_comparison(self, start_year: int, end_year: int, 
                            sectors: List[str]) -> None:
        """Show trend comparison charts"""
        st.header(f"📈 Trend Analysis: {start_year} - {end_year}")
        
        with st.spinner("Generating trend analysis..."):
            trend_data = self.data_manager.fetch_trend_data(
                start_year, end_year, sectors
            )
        
        if trend_data:
            # Create interactive charts for each sector
            for sector in sectors:
                if sector in trend_data:
                    st.subheader(f"{sector} Trends")
                    
                    # Use the chart generator
                    chart = self.chart_generator.create_trend_chart(
                        trend_data[sector], 
                        title=f"{sector} Forecasts vs Actuals Over Time"
                    )
                    st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("No trend data available for the specified parameters.")
    
    def handle_custom_query(self, query: str) -> None:
        """Handle custom user queries"""
        st.header("🤖 Custom Query Analysis")
        
        if query:
            with st.spinner("Processing your query..."):
                # Parse the query to understand what's being asked
                parsed_query = self.prediction_engine.parse_natural_language_query(query)
                
                # Fetch relevant data based on parsed query
                if parsed_query.get('type') == 'past_forecast':
                    results = self.analyze_past_forecasts(
                        parsed_query.get('forecast_year'),
                        parsed_query.get('target_year'),
                        parsed_query.get('sectors', []),
                        parsed_query.get('sources', [])
                    )
                elif parsed_query.get('type') == 'future_prediction':
                    results = self.analyze_future_predictions(
                        parsed_query.get('target_year'),
                        parsed_query.get('sectors', []),
                        parsed_query.get('sources', [])
                    )
                else:
                    st.warning("Could not understand the query. Please try rephrasing or use the structured options.")
    
    def run(self):
        """Main application runner"""
        self.setup_page()
        
        # Get user inputs
        params = self.render_sidebar()
        
        # Main content area
        if params["query_type"] == "Past Forecast Analysis":
            self.analyze_past_forecasts(
                params["forecast_year"], 
                params["target_year"],
                params["sectors"],
                params["sources"]
            )
            
        elif params["query_type"] == "Future Prediction Analysis":
            self.analyze_future_predictions(
                params["target_year"],
                params["sectors"], 
                params["sources"]
            )
            
        elif params["query_type"] == "Trend Comparison":
            self.show_trend_comparison(
                params["forecast_year"],  # start_year
                params["target_year"],    # end_year
                params["sectors"]
            )
            
        elif params["query_type"] == "Custom Query":
            st.subheader("Ask Your Question")
            custom_query = st.text_area(
                "Enter your question about India's past forecasts or future predictions:",
                placeholder="e.g., Which 1975 Indian predictions about 2025 actually happened?"
            )
            
            if st.button("Analyze Query"):
                self.handle_custom_query(custom_query)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        **Data Sources**: IEA, RBI, MoSPI, NITI Aayog, PIB, UN DESA, World Bank, Reuters, The Hindu, ET, Mint
        
        **Note**: All data is fetched in real-time from public sources. Predictions are based on historical patterns and current trends.
        """)

def main():
    """Main entry point"""
    dashboard = IndiaPredictionDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()