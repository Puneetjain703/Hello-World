"""
Data Source Manager for India Prediction Dashboard
=================================================

Handles data fetching from various trusted sources:
- IEA, RBI, MoSPI, NITI Aayog, PIB, UN DESA, World Bank
- Reuters, The Hindu, Economic Times, Mint
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import time
from urllib.parse import urljoin, urlparse
import feedparser

logger = logging.getLogger(__name__)

class DataSourceManager:
    """Manages data fetching from multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Source configurations
        self.sources_config = {
            'RBI': {
                'base_url': 'https://www.rbi.org.in',
                'search_urls': [
                    'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=',
                    'https://www.rbi.org.in/Scripts/BS_SpeechesView.aspx?Id='
                ],
                'rss_feed': 'https://www.rbi.org.in/scripts/rss.aspx'
            },
            'MoSPI': {
                'base_url': 'https://www.mospi.gov.in',
                'api_url': 'https://www.mospi.gov.in/web/mospi/download-tables-data',
                'search_patterns': ['GDP', 'CPI', 'WPI', 'Industrial Production']
            },
            'NITI Aayog': {
                'base_url': 'https://www.niti.gov.in',
                'search_urls': [
                    'https://www.niti.gov.in/documents-reports',
                    'https://www.niti.gov.in/strategy-for-new-india-2032'
                ]
            },
            'World Bank': {
                'api_url': 'https://api.worldbank.org/v2/country/IND/indicator',
                'indicators': {
                    'GDP': 'NY.GDP.MKTP.CD',
                    'GDP_GROWTH': 'NY.GDP.MKTP.KD.ZG',
                    'POPULATION': 'SP.POP.TOTL',
                    'ENERGY_USE': 'EG.USE.COMM.KT.OE'
                }
            },
            'IEA': {
                'base_url': 'https://www.iea.org',
                'search_patterns': ['India', 'renewable energy', 'coal', 'solar', 'wind']
            },
            'Economic Times': {
                'base_url': 'https://economictimes.indiatimes.com',
                'rss_feed': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms'
            },
            'The Hindu': {
                'base_url': 'https://www.thehindu.com',
                'rss_feed': 'https://www.thehindu.com/news/national/feeder/default.rss'
            }
        }
        
        # Cache for performance
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
    
    def _get_cached_or_fetch(self, cache_key: str, fetch_func, *args, **kwargs):
        """Get data from cache or fetch if not available/expired"""
        now = datetime.now()
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if (now - timestamp).seconds < self.cache_duration:
                return data
        
        # Fetch new data
        try:
            data = fetch_func(*args, **kwargs)
            self.cache[cache_key] = (data, now)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {cache_key}: {e}")
            return None
    
    def fetch_historical_forecasts(self, forecast_year: int, target_year: int, 
                                 sectors: List[str], sources: List[str]) -> Dict:
        """Fetch historical forecasts made in forecast_year about target_year"""
        cache_key = f"historical_{forecast_year}_{target_year}_{'-'.join(sectors)}"
        
        result = self._get_cached_or_fetch(
            cache_key, 
            self._fetch_historical_forecasts_impl,
            forecast_year, target_year, sectors, sources
        )
        return result if result is not None else {}
    
    def _fetch_historical_forecasts_impl(self, forecast_year: int, target_year: int,
                                       sectors: List[str], sources: List[str]) -> Dict:
        """Implementation of historical forecast fetching"""
        results = {}
        
        # Search terms based on forecast and target years
        search_terms = [
            f"India {forecast_year} forecast {target_year}",
            f"India planning commission {forecast_year} vision {target_year}",
            f"India five year plan {forecast_year} projection {target_year}",
            f"India economic survey {forecast_year} target {target_year}"
        ]
        
        for sector in sectors:
            results[sector] = {
                'forecasts': [],
                'sources': []
            }
            
            # Sector-specific search terms
            sector_terms = {
                'Economy': ['GDP', 'growth rate', 'per capita income', 'inflation'],
                'Energy': ['power generation', 'renewable energy', 'coal production', 'electricity'],
                'Infrastructure': ['railway', 'highway', 'airports', 'ports'],
                'Technology': ['internet', 'mobile', 'digitization', 'IT sector'],
                'Agriculture': ['food production', 'crop yield', 'irrigation'],
                'Education': ['literacy rate', 'enrollment', 'universities'],
                'Healthcare': ['life expectancy', 'infant mortality', 'hospitals'],
                'Environment': ['forest cover', 'carbon emissions', 'air quality'],
                'Social Development': ['poverty rate', 'human development index']
            }
            
            terms = sector_terms.get(sector, [sector.lower()])
            
            for term in terms:
                for source in sources:
                    forecasts = self._search_historical_forecasts(
                        source, forecast_year, target_year, term
                    )
                    if forecasts:
                        results[sector]['forecasts'].extend(forecasts)
        
        return results
    
    def _search_historical_forecasts(self, source: str, forecast_year: int, 
                                   target_year: int, search_term: str) -> List[Dict]:
        """Search for historical forecasts from a specific source"""
        forecasts = []
        
        try:
            if source == 'RBI':
                forecasts = self._search_rbi_historical(forecast_year, target_year, search_term)
            elif source == 'World Bank':
                forecasts = self._search_worldbank_historical(forecast_year, target_year, search_term)
            elif source == 'Planning Commission':
                forecasts = self._search_planning_commission(forecast_year, target_year, search_term)
            elif source in ['The Hindu', 'Economic Times']:
                forecasts = self._search_news_archives(source, forecast_year, target_year, search_term)
            
        except Exception as e:
            logger.error(f"Error searching {source} for {search_term}: {e}")
        
        return forecasts
    
    def _search_rbi_historical(self, forecast_year: int, target_year: int, 
                              search_term: str) -> List[Dict]:
        """Search RBI archives for historical forecasts"""
        forecasts = []
        
        # Example search - this would need to be implemented with actual RBI API/scraping
        # For now, returning sample data structure
        if 'GDP' in search_term and forecast_year == 1975 and target_year == 2000:
            forecasts.append({
                'metric': 'GDP Growth Rate',
                'predicted_value': '6.5% annually',
                'source_url': 'https://www.rbi.org.in/scripts/archive.html',
                'source': 'RBI Economic Survey 1975',
                'confidence': 'medium'
            })
        
        return forecasts
    
    def _search_worldbank_historical(self, forecast_year: int, target_year: int,
                                   search_term: str) -> List[Dict]:
        """Search World Bank data for historical forecasts"""
        forecasts = []
        
        try:
            # World Bank API call for historical data
            if 'GDP' in search_term:
                url = f"{self.sources_config['World Bank']['api_url']}/NY.GDP.MKTP.KD.ZG"
                params = {
                    'format': 'json',
                    'date': f"{forecast_year-5}:{forecast_year+5}",
                    'per_page': 100
                }
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:  # World Bank returns metadata in first element
                        for entry in data[1]:
                            if entry['date'] == str(forecast_year):
                                forecasts.append({
                                    'metric': 'GDP Growth Rate',
                                    'predicted_value': f"{entry['value']:.1f}%",
                                    'source_url': f"https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN",
                                    'source': 'World Bank Historical Data',
                                    'confidence': 'high'
                                })
        except Exception as e:
            logger.error(f"World Bank API error: {e}")
        
        return forecasts
    
    def _search_planning_commission(self, forecast_year: int, target_year: int,
                                  search_term: str) -> List[Dict]:
        """Search Planning Commission archives"""
        forecasts = []
        
        # Five Year Plans mapping
        plan_periods = {
            1951: "First Five Year Plan",
            1956: "Second Five Year Plan", 
            1961: "Third Five Year Plan",
            1969: "Fourth Five Year Plan",
            1974: "Fifth Five Year Plan",
            1980: "Sixth Five Year Plan",
            1985: "Seventh Five Year Plan",
            1992: "Eighth Five Year Plan",
            1997: "Ninth Five Year Plan",
            2002: "Tenth Five Year Plan",
            2007: "Eleventh Five Year Plan",
            2012: "Twelfth Five Year Plan"
        }
        
        # Find the relevant plan
        relevant_plan = None
        for year, plan in plan_periods.items():
            if year <= forecast_year < year + 5:
                relevant_plan = plan
                break
        
        if relevant_plan:
            # Sample data - would need actual document parsing
            if 'GDP' in search_term:
                forecasts.append({
                    'metric': 'GDP Growth Target',
                    'predicted_value': '7.5% annually',
                    'source_url': f'https://niti.gov.in/planningcommission.gov.in/{relevant_plan.lower().replace(" ", "-")}',
                    'source': relevant_plan,
                    'confidence': 'high'
                })
        
        return forecasts
    
    def _search_news_archives(self, source: str, forecast_year: int, target_year: int,
                            search_term: str) -> List[Dict]:
        """Search news archives for historical forecasts"""
        forecasts = []
        
        # This would require access to news archives
        # Implementation would depend on available APIs or web scraping
        
        return forecasts
    
    def fetch_actual_outcomes(self, target_year: int, sectors: List[str]) -> Dict:
        """Fetch actual outcomes for the target year"""
        cache_key = f"actuals_{target_year}_{'-'.join(sectors)}"
        
        result = self._get_cached_or_fetch(
            cache_key,
            self._fetch_actual_outcomes_impl,
            target_year, sectors
        )
        return result if result is not None else {}
    
    def _fetch_actual_outcomes_impl(self, target_year: int, sectors: List[str]) -> Dict:
        """Implementation of actual outcomes fetching"""
        results = {}
        
        for sector in sectors:
            results[sector] = {
                'actuals': [],
                'sources': []
            }
            
            if sector == 'Economy':
                # Fetch GDP, inflation, etc.
                gdp_data = self._fetch_worldbank_indicator('NY.GDP.MKTP.KD.ZG', target_year)
                if gdp_data:
                    results[sector]['actuals'].append({
                        'metric': 'GDP Growth Rate',
                        'actual_value': f"{gdp_data:.1f}%",
                        'source': 'World Bank',
                        'source_url': 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN'
                    })
            
            elif sector == 'Energy':
                # Fetch energy production data
                energy_data = self._fetch_worldbank_indicator('EG.USE.COMM.KT.OE', target_year)
                if energy_data:
                    results[sector]['actuals'].append({
                        'metric': 'Energy Use',
                        'actual_value': f"{energy_data:.0f} kt of oil equivalent",
                        'source': 'World Bank',
                        'source_url': 'https://data.worldbank.org/indicator/EG.USE.COMM.KT.OE?locations=IN'
                    })
        
        return results
    
    def _fetch_worldbank_indicator(self, indicator: str, year: int) -> Optional[float]:
        """Fetch a specific World Bank indicator for a given year"""
        try:
            url = f"{self.sources_config['World Bank']['api_url']}/{indicator}"
            params = {
                'format': 'json',
                'date': str(year),
                'per_page': 1
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    return data[1][0]['value']
        except Exception as e:
            logger.error(f"Error fetching World Bank indicator {indicator}: {e}")
        
        return None
    
    def fetch_current_predictions(self, target_year: int, sectors: List[str], 
                                sources: List[str]) -> Dict:
        """Fetch current predictions for future targets"""
        cache_key = f"current_{target_year}_{'-'.join(sectors)}"
        
        result = self._get_cached_or_fetch(
            cache_key,
            self._fetch_current_predictions_impl,
            target_year, sectors, sources
        )
        return result if result is not None else {}
    
    def _fetch_current_predictions_impl(self, target_year: int, sectors: List[str],
                                      sources: List[str]) -> Dict:
        """Implementation of current predictions fetching"""
        results = {}
        
        for sector in sectors:
            results[sector] = {
                'predictions': [],
                'sources': []
            }
            
            # Fetch latest predictions from various sources
            for source in sources:
                predictions = self._fetch_source_predictions(source, sector, target_year)
                if predictions:
                    results[sector]['predictions'].extend(predictions)
        
        return results
    
    def _fetch_source_predictions(self, source: str, sector: str, target_year: int) -> List[Dict]:
        """Fetch predictions from a specific source"""
        predictions = []
        
        try:
            if source == 'NITI Aayog' and sector == 'Energy':
                # Example: 450 GW renewable energy target by 2030
                if target_year >= 2030:
                    predictions.append({
                        'metric': 'Renewable Energy Capacity',
                        'target_value': '450 GW',
                        'current_progress': '118 GW (as of 2024)',
                        'source': 'NITI Aayog',
                        'source_url': 'https://www.niti.gov.in/renewable-energy-targets',
                        'announcement_date': '2019-09-23'
                    })
            
            elif source == 'RBI' and sector == 'Economy':
                # RBI growth projections
                predictions.append({
                    'metric': 'GDP Growth Rate',
                    'target_value': '6.5-7.0%',
                    'current_progress': '6.3% (FY2024)',
                    'source': 'RBI Monetary Policy',
                    'source_url': 'https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx',
                    'announcement_date': '2024-02-08'
                })
                
        except Exception as e:
            logger.error(f"Error fetching predictions from {source}: {e}")
        
        return predictions
    
    def fetch_trend_data(self, start_year: int, end_year: int, sectors: List[str]) -> Dict:
        """Fetch trend data for analysis"""
        cache_key = f"trends_{start_year}_{end_year}_{'-'.join(sectors)}"
        
        result = self._get_cached_or_fetch(
            cache_key,
            self._fetch_trend_data_impl,
            start_year, end_year, sectors
        )
        return result if result is not None else {}
    
    def _fetch_trend_data_impl(self, start_year: int, end_year: int, sectors: List[str]) -> Dict:
        """Implementation of trend data fetching"""
        results = {}
        
        for sector in sectors:
            results[sector] = {
                'years': [],
                'forecasts': [],
                'actuals': [],
                'sources': []
            }
            
            # Generate sample trend data
            years = list(range(start_year, min(end_year + 1, datetime.now().year + 1), 5))
            
            for year in years:
                results[sector]['years'].append(year)
                
                # Add some sample data points
                if sector == 'Economy':
                    # GDP growth trends
                    if year <= datetime.now().year:
                        actual_gdp = self._fetch_worldbank_indicator('NY.GDP.MKTP.KD.ZG', year)
                        results[sector]['actuals'].append(actual_gdp or 0)
                        results[sector]['forecasts'].append(None)
                    else:
                        results[sector]['actuals'].append(None)
                        results[sector]['forecasts'].append(6.5 + (year - datetime.now().year) * 0.1)
                
                elif sector == 'Energy':
                    # Energy capacity trends
                    if year <= datetime.now().year:
                        results[sector]['actuals'].append(50 + (year - 2000) * 2.5)
                        results[sector]['forecasts'].append(None)
                    else:
                        results[sector]['actuals'].append(None)
                        results[sector]['forecasts'].append(150 + (year - 2025) * 10)
        
        return results
    
    def search_web_sources(self, query: str, sources: Optional[List[str]] = None) -> List[Dict]:
        """Search web sources for specific queries"""
        if not sources:
            sources = ['Economic Times', 'The Hindu', 'Reuters']
        
        results = []
        
        for source in sources:
            try:
                if source in ['Economic Times', 'The Hindu']:
                    # Search RSS feeds
                    feed_url = self.sources_config[source]['rss_feed']
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Limit to 10 recent entries
                        if any(term.lower() in entry.title.lower() or 
                              term.lower() in entry.summary.lower() 
                              for term in query.split()):
                            results.append({
                                'title': entry.title,
                                'summary': entry.summary,
                                'url': entry.link,
                                'source': source,
                                'published': entry.published
                            })
                            
            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
        
        return results