"""
Visualization Module for India Prediction Dashboard
=================================================

Creates charts and visualizations for forecast analysis, trends, and comparisons.
Supports both static and interactive charts using matplotlib and plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generates charts and visualizations for the dashboard"""
    
    def __init__(self):
        # Set up default styling
        self.colors = {
            'EARLY': '#2E8B57',      # Sea Green
            'ON-TIME': '#FF8C00',    # Dark Orange  
            'LATE': '#DC143C',       # Crimson
            'LIKELY EARLY': '#2E8B57',
            'LATE-RISK': '#DC143C',
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'tertiary': '#2ca02c'
        }
        
        # Plotly theme
        self.plotly_theme = 'plotly_white'
        
        # Matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_accuracy_pie_chart(self, accuracy_stats: Dict[str, int], 
                                title: str = "Forecast Accuracy Distribution") -> go.Figure:
        """Create pie chart for accuracy statistics"""
        
        labels = list(accuracy_stats.keys())
        values = list(accuracy_stats.values())
        colors = [self.colors.get(label, self.colors['primary']) for label in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
        )
        
        return fig
    
    def create_likelihood_bar_chart(self, likelihood_stats: Dict[str, int],
                                  title: str = "Future Target Likelihood") -> go.Figure:
        """Create bar chart for likelihood statistics"""
        
        labels = list(likelihood_stats.keys())
        values = list(likelihood_stats.values())
        colors = [self.colors.get(label, self.colors['primary']) for label in labels]
        
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors),
            text=values,
            textposition='auto'
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Likelihood Category",
            yaxis_title="Number of Predictions",
            showlegend=False
        )
        
        return fig
    
    def create_trend_chart(self, trend_data: Dict, title: str = "Trend Analysis") -> go.Figure:
        """Create line chart showing trends over time"""
        
        years = trend_data.get('years', [])
        forecasts = trend_data.get('forecasts', [])
        actuals = trend_data.get('actuals', [])
        
        fig = go.Figure()
        
        # Add actual values line
        actual_years = [year for year, value in zip(years, actuals) if value is not None]
        actual_values = [value for value in actuals if value is not None]
        
        if actual_values:
            fig.add_trace(go.Scatter(
                x=actual_years,
                y=actual_values,
                mode='lines+markers',
                name='Actual Values',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8)
            ))
        
        # Add forecast values line
        forecast_years = [year for year, value in zip(years, forecasts) if value is not None]
        forecast_values = [value for value in forecasts if value is not None]
        
        if forecast_values:
            fig.add_trace(go.Scatter(
                x=forecast_years,
                y=forecast_values,
                mode='lines+markers',
                name='Forecasts',
                line=dict(color=self.colors['secondary'], width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))
        
        # Add vertical line at current year
        current_year = datetime.now().year
        if years and min(years) <= current_year <= max(years):
            fig.add_vline(
                x=current_year,
                line_dash="dot",
                line_color="gray",
                annotation_text="Current Year",
                annotation_position="top right"
            )
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Year",
            yaxis_title="Value",
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        return fig
    
    def create_sector_comparison_chart(self, sector_data: Dict[str, Dict], 
                                     metric: str = "accuracy_score") -> go.Figure:
        """Create bar chart comparing sectors"""
        
        sectors = list(sector_data.keys())
        values = [data.get(metric, 0) for data in sector_data.values()]
        
        fig = go.Figure(data=[go.Bar(
            x=sectors,
            y=values,
            marker=dict(color=self.colors['primary']),
            text=[f"{v:.2f}" for v in values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title=dict(text=f"Sector Comparison - {metric.title()}", x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Sector",
            yaxis_title=metric.replace('_', ' ').title(),
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_timeline_chart(self, timeline_data: List[Dict], 
                            title: str = "Prediction Timeline") -> go.Figure:
        """Create timeline chart for predictions"""
        
        fig = go.Figure()
        
        # Sort by year
        timeline_data = sorted(timeline_data, key=lambda x: x.get('year', 0))
        
        years = [item['year'] for item in timeline_data]
        predictions = [item.get('prediction', '') for item in timeline_data]
        statuses = [item.get('status', 'UNKNOWN') for item in timeline_data]
        
        # Create scatter plot with different colors for status
        for status in set(statuses):
            status_years = [year for year, s in zip(years, statuses) if s == status]
            status_predictions = [pred for pred, s in zip(predictions, statuses) if s == status]
            
            fig.add_trace(go.Scatter(
                x=status_years,
                y=[status] * len(status_years),
                mode='markers',
                name=status,
                marker=dict(
                    size=15,
                    color=self.colors.get(status, self.colors['primary']),
                    symbol='circle'
                ),
                text=status_predictions,
                hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Status: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Year",
            yaxis_title="Status",
            hovermode='closest'
        )
        
        return fig
    
    def create_progress_gauge(self, current_value: float, target_value: float,
                            title: str = "Progress Indicator") -> go.Figure:
        """Create gauge chart showing progress toward target"""
        
        if target_value == 0:
            progress_percent = 0
        else:
            progress_percent = min(100, (current_value / target_value) * 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=progress_percent,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': 100},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template=self.plotly_theme,
            height=400
        )
        
        return fig
    
    def create_heatmap(self, data: pd.DataFrame, title: str = "Data Heatmap") -> go.Figure:
        """Create heatmap visualization"""
        
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='RdBu',
            text=data.values,
            texttemplate="%{text:.2f}",
            textfont={"size": 10},
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Categories",
            yaxis_title="Sectors"
        )
        
        return fig
    
    def create_multi_line_chart(self, data_series: Dict[str, List[Tuple[float, float]]],
                              title: str = "Multi-Series Comparison") -> go.Figure:
        """Create multi-line chart for comparing multiple data series"""
        
        fig = go.Figure()
        
        colors = [self.colors['primary'], self.colors['secondary'], self.colors['tertiary']]
        
        for i, (series_name, points) in enumerate(data_series.items()):
            if points:
                x_vals, y_vals = zip(*points)
                color = colors[i % len(colors)]
                
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines+markers',
                    name=series_name,
                    line=dict(color=color, width=3),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="X Axis",
            yaxis_title="Y Axis",
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        return fig
    
    def create_confidence_scatter(self, predictions: List[Dict], 
                                title: str = "Prediction Confidence Analysis") -> go.Figure:
        """Create scatter plot showing confidence vs likelihood"""
        
        fig = go.Figure()
        
        # Group by likelihood
        likelihood_groups = {}
        for pred in predictions:
            likelihood = pred.get('likelihood', 'UNKNOWN')
            if likelihood not in likelihood_groups:
                likelihood_groups[likelihood] = {'confidence': [], 'metrics': []}
            
            likelihood_groups[likelihood]['confidence'].append(pred.get('confidence', 0))
            likelihood_groups[likelihood]['metrics'].append(pred.get('metric', 'Unknown'))
        
        # Add scatter points for each likelihood group
        for likelihood, data in likelihood_groups.items():
            fig.add_trace(go.Scatter(
                x=data['confidence'],
                y=[likelihood] * len(data['confidence']),
                mode='markers',
                name=likelihood,
                marker=dict(
                    size=12,
                    color=self.colors.get(likelihood, self.colors['primary']),
                    opacity=0.7
                ),
                text=data['metrics'],
                hovertemplate='<b>%{text}</b><br>Confidence: %{x:.2f}<br>Likelihood: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Confidence Score",
            yaxis_title="Likelihood Category",
            showlegend=False
        )
        
        return fig
    
    def create_waterfall_chart(self, categories: List[str], values: List[float],
                             title: str = "Impact Analysis") -> go.Figure:
        """Create waterfall chart for showing cumulative impact"""
        
        fig = go.Figure()
        
        # Calculate cumulative values
        cumulative = [0.0]
        for value in values:
            cumulative.append(cumulative[-1] + value)
        
        # Add bars
        for i, (category, value) in enumerate(zip(categories, values)):
            color = self.colors['primary'] if value >= 0 else self.colors['LATE']
            
            fig.add_trace(go.Bar(
                x=[category],
                y=[value],
                base=cumulative[i],
                marker=dict(color=color),
                text=f"{value:+.1f}",
                textposition='auto',
                showlegend=False
            ))
        
        # Add total bar
        fig.add_trace(go.Bar(
            x=['Total'],
            y=[cumulative[-1]],
            marker=dict(color=self.colors['tertiary']),
            text=f"{cumulative[-1]:.1f}",
            textposition='auto',
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.plotly_theme,
            xaxis_title="Factors",
            yaxis_title="Impact Value",
            bargap=0.3
        )
        
        return fig
    
    def create_dashboard_summary(self, summary_data: Dict) -> go.Figure:
        """Create comprehensive dashboard summary visualization"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Accuracy Distribution', 'Likelihood Trends', 
                          'Sector Performance', 'Confidence Levels'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Accuracy pie chart
        if 'accuracy_stats' in summary_data:
            accuracy_data = summary_data['accuracy_stats']
            fig.add_trace(go.Pie(
                labels=list(accuracy_data.keys()),
                values=list(accuracy_data.values()),
                name="Accuracy"
            ), row=1, col=1)
        
        # Likelihood bar chart
        if 'likelihood_stats' in summary_data:
            likelihood_data = summary_data['likelihood_stats']
            fig.add_trace(go.Bar(
                x=list(likelihood_data.keys()),
                y=list(likelihood_data.values()),
                name="Likelihood"
            ), row=1, col=2)
        
        # Sector performance
        if 'sector_performance' in summary_data:
            sector_data = summary_data['sector_performance']
            fig.add_trace(go.Bar(
                x=list(sector_data.keys()),
                y=list(sector_data.values()),
                name="Performance"
            ), row=2, col=1)
        
        # Confidence scatter
        if 'confidence_data' in summary_data:
            conf_data = summary_data['confidence_data']
            fig.add_trace(go.Scatter(
                x=conf_data.get('x', []),
                y=conf_data.get('y', []),
                mode='markers',
                name="Confidence"
            ), row=2, col=2)
        
        fig.update_layout(
            title=dict(text="Dashboard Summary", x=0.5, font=dict(size=18)),
            template=self.plotly_theme,
            height=700,
            showlegend=False
        )
        
        return fig
    
    def export_chart(self, fig: go.Figure, filename: str, format: str = 'png') -> str:
        """Export chart to file"""
        try:
            if format.lower() in ['png', 'jpg', 'jpeg']:
                fig.write_image(f"{filename}.{format}")
            elif format.lower() == 'html':
                fig.write_html(f"{filename}.html")
            elif format.lower() == 'pdf':
                fig.write_image(f"{filename}.pdf")
            else:
                logger.warning(f"Unsupported format: {format}")
                return ""
            
            logger.info(f"Chart exported to {filename}.{format}")
            return f"{filename}.{format}"
            
        except Exception as e:
            logger.error(f"Error exporting chart: {e}")
            return ""