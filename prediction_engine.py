"""
Prediction Engine for India Prediction Dashboard
===============================================

Handles forecast analysis, accuracy calculations, and future likelihood predictions.
Uses historical patterns to classify predictions as EARLY, ON-TIME, or LATE.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from textblob import TextBlob
import numpy as np

logger = logging.getLogger(__name__)

class PredictionEngine:
    """Engine for analyzing predictions and forecasts"""
    
    def __init__(self):
        # Historical accuracy patterns by sector
        self.sector_patterns = {
            'Economy': {
                'early_indicators': ['digital', 'services', 'IT', 'startup'],
                'late_indicators': ['manufacturing', 'infrastructure', 'heavy industry'],
                'accuracy_weight': 0.7
            },
            'Energy': {
                'early_indicators': ['solar', 'wind', 'renewable', 'digital'],
                'late_indicators': ['coal', 'nuclear', 'grid', 'transmission'],
                'accuracy_weight': 0.6
            },
            'Infrastructure': {
                'early_indicators': ['metro', 'airports', 'digital'],
                'late_indicators': ['railway', 'highway', 'ports', 'land acquisition'],
                'accuracy_weight': 0.5
            },
            'Technology': {
                'early_indicators': ['mobile', 'internet', 'digital', 'startup'],
                'late_indicators': ['manufacturing', 'hardware', 'regulation'],
                'accuracy_weight': 0.8
            },
            'Agriculture': {
                'early_indicators': ['irrigation', 'seeds', 'technology'],
                'late_indicators': ['land reform', 'subsidies', 'weather'],
                'accuracy_weight': 0.6
            },
            'Education': {
                'early_indicators': ['digital', 'online', 'private'],
                'late_indicators': ['government', 'infrastructure', 'teachers'],
                'accuracy_weight': 0.7
            },
            'Healthcare': {
                'early_indicators': ['digital', 'private', 'pharma'],
                'late_indicators': ['government', 'infrastructure', 'rural'],
                'accuracy_weight': 0.6
            },
            'Environment': {
                'early_indicators': ['solar', 'electric', 'private'],
                'late_indicators': ['coal', 'government', 'industrial'],
                'accuracy_weight': 0.5
            },
            'Social Development': {
                'early_indicators': ['digital', 'urban', 'private'],
                'late_indicators': ['rural', 'government', 'infrastructure'],
                'accuracy_weight': 0.6
            }
        }
        
        # Tolerance thresholds for classification
        self.tolerance_thresholds = {
            'strict': 0.05,    # 5% tolerance
            'moderate': 0.15,  # 15% tolerance  
            'loose': 0.25      # 25% tolerance
        }
    
    def compare_forecasts_vs_actuals(self, forecasts: Dict, actuals: Dict) -> Dict:
        """Compare forecasts against actual outcomes"""
        results = {}
        
        for sector in forecasts.keys():
            if sector in actuals:
                results[sector] = {
                    'forecasts': [],
                    'accuracy_score': 0.0,
                    'total_comparisons': 0
                }
                
                forecast_data = forecasts[sector].get('forecasts', [])
                actual_data = actuals[sector].get('actuals', [])
                
                # Match forecasts with actuals
                matched_pairs = self._match_forecasts_with_actuals(forecast_data, actual_data)
                
                for forecast, actual in matched_pairs:
                    comparison = self._compare_single_forecast(forecast, actual, sector)
                    results[sector]['forecasts'].append(comparison)
                    results[sector]['total_comparisons'] += 1
                
                # Calculate overall accuracy score
                results[sector]['accuracy_score'] = self._calculate_sector_accuracy(
                    results[sector]['forecasts']
                )
        
        return results
    
    def _match_forecasts_with_actuals(self, forecasts: List[Dict], actuals: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """Match forecast entries with corresponding actual entries"""
        matches = []
        
        for forecast in forecasts:
            forecast_metric = forecast.get('metric', '').lower()
            
            # Find best matching actual
            best_match = None
            best_score = 0
            
            for actual in actuals:
                actual_metric = actual.get('metric', '').lower()
                
                # Calculate similarity score
                similarity = self._calculate_metric_similarity(forecast_metric, actual_metric)
                
                if similarity > best_score and similarity > 0.5:  # Minimum threshold
                    best_score = similarity
                    best_match = actual
            
            if best_match:
                matches.append((forecast, best_match))
        
        return matches
    
    def _calculate_metric_similarity(self, metric1: str, metric2: str) -> float:
        """Calculate similarity between two metric names"""
        # Simple word overlap calculation
        words1 = set(metric1.lower().split())
        words2 = set(metric2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _compare_single_forecast(self, forecast: Dict, actual: Dict, sector: str) -> Dict:
        """Compare a single forecast with its actual outcome"""
        result = {
            'metric': forecast.get('metric', 'Unknown'),
            'predicted_value': forecast.get('predicted_value', 'N/A'),
            'actual_value': actual.get('actual_value', 'N/A'),
            'source': forecast.get('source', 'Unknown'),
            'status': 'UNKNOWN',
            'accuracy_score': 0.0,
            'analysis': ''
        }
        
        # Extract numeric values for comparison
        predicted_num = self._extract_numeric_value(forecast.get('predicted_value', ''))
        actual_num = self._extract_numeric_value(actual.get('actual_value', ''))
        
        if predicted_num is not None and actual_num is not None:
            # Calculate percentage difference
            if predicted_num != 0:
                diff_percent = abs(actual_num - predicted_num) / abs(predicted_num)
            else:
                diff_percent = 1.0 if actual_num != 0 else 0.0
            
            # Classify based on accuracy
            tolerance = self.tolerance_thresholds['moderate']  # Use moderate tolerance
            
            if diff_percent <= tolerance:
                result['status'] = 'ON-TIME'
                result['accuracy_score'] = 1.0 - diff_percent
                result['analysis'] = f"Prediction was accurate within {tolerance*100:.0f}% tolerance"
            elif actual_num > predicted_num:
                result['status'] = 'EARLY'
                result['accuracy_score'] = max(0.0, 1.0 - diff_percent)
                result['analysis'] = f"Actual outcome exceeded prediction by {diff_percent*100:.1f}%"
            else:
                result['status'] = 'LATE'
                result['accuracy_score'] = max(0.0, 1.0 - diff_percent)
                result['analysis'] = f"Actual outcome fell short of prediction by {diff_percent*100:.1f}%"
        else:
            # Text-based comparison
            result['status'] = self._compare_text_values(
                forecast.get('predicted_value', ''),
                actual.get('actual_value', '')
            )
            result['analysis'] = "Comparison based on qualitative assessment"
        
        return result
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        if not text:
            return None
        
        # Remove common units and symbols
        clean_text = re.sub(r'[%$₹,]', '', str(text))
        
        # Find numbers (including decimals)
        numbers = re.findall(r'\d+\.?\d*', clean_text)
        
        if numbers:
            try:
                # Handle different units
                value = float(numbers[0])
                
                # Scale based on units mentioned
                text_lower = text.lower()
                if 'crore' in text_lower or 'cr' in text_lower:
                    value *= 10000000  # 1 crore = 10 million
                elif 'lakh' in text_lower:
                    value *= 100000    # 1 lakh = 100 thousand
                elif 'thousand' in text_lower or 'k' in text_lower:
                    value *= 1000
                elif 'million' in text_lower or 'm' in text_lower:
                    value *= 1000000
                elif 'billion' in text_lower or 'b' in text_lower:
                    value *= 1000000000
                elif 'trillion' in text_lower or 't' in text_lower:
                    value *= 1000000000000
                
                return value
            except ValueError:
                pass
        
        return None
    
    def _compare_text_values(self, predicted: str, actual: str) -> str:
        """Compare text values qualitatively"""
        if not predicted or not actual:
            return 'UNKNOWN'
        
        # Use TextBlob for sentiment analysis as a proxy for achievement
        pred_sentiment = TextBlob(predicted).sentiment.polarity
        actual_sentiment = TextBlob(actual).sentiment.polarity
        
        if abs(pred_sentiment - actual_sentiment) < 0.2:
            return 'ON-TIME'
        elif actual_sentiment > pred_sentiment:
            return 'EARLY'
        else:
            return 'LATE'
    
    def _calculate_sector_accuracy(self, forecasts: List[Dict]) -> float:
        """Calculate overall accuracy score for a sector"""
        if not forecasts:
            return 0.0
        
        total_score = sum(f.get('accuracy_score', 0.0) for f in forecasts)
        return total_score / len(forecasts)
    
    def calculate_accuracy_stats(self, results: Dict) -> Dict[str, int]:
        """Calculate accuracy statistics across all results"""
        stats = {'EARLY': 0, 'ON-TIME': 0, 'LATE': 0, 'UNKNOWN': 0}
        
        for sector_data in results.values():
            for forecast in sector_data.get('forecasts', []):
                status = forecast.get('status', 'UNKNOWN')
                stats[status] = stats.get(status, 0) + 1
        
        return stats
    
    def analyze_future_likelihood(self, predictions: Dict, target_year: int) -> Dict:
        """Analyze likelihood of future predictions based on historical patterns"""
        results = {}
        current_year = datetime.now().year
        time_horizon = target_year - current_year
        
        for sector, data in predictions.items():
            results[sector] = {
                'predictions': [],
                'overall_likelihood': 'ON-TIME',
                'confidence_score': 0.0
            }
            
            sector_predictions = []
            
            for prediction in data.get('predictions', []):
                analysis = self._analyze_single_prediction(prediction, sector, time_horizon)
                sector_predictions.append(analysis)
            
            results[sector]['predictions'] = sector_predictions
            
            # Calculate overall sector likelihood
            if sector_predictions:
                results[sector]['overall_likelihood'] = self._calculate_sector_likelihood(
                    sector_predictions
                )
                results[sector]['confidence_score'] = self._calculate_confidence_score(
                    sector, sector_predictions, time_horizon
                )
        
        return results
    
    def _analyze_single_prediction(self, prediction: Dict, sector: str, time_horizon: int) -> Dict:
        """Analyze likelihood of a single prediction"""
        result = {
            'metric': prediction.get('metric', 'Unknown'),
            'target_value': prediction.get('target_value', 'N/A'),
            'current_progress': prediction.get('current_progress', 'N/A'),
            'source': prediction.get('source', 'Unknown'),
            'likelihood': 'ON-TIME',
            'confidence': 0.0,
            'reasoning': '',
            'risk_factors': [],
            'positive_factors': []
        }
        
        # Get sector patterns
        patterns = self.sector_patterns.get(sector, {})
        
        # Analyze target and current progress
        target_text = str(prediction.get('target_value', '')).lower()
        progress_text = str(prediction.get('current_progress', '')).lower()
        metric_text = str(prediction.get('metric', '')).lower()
        
        # Check for early/late indicators
        early_score = 0
        late_score = 0
        
        all_text = f"{target_text} {progress_text} {metric_text}"
        
        for indicator in patterns.get('early_indicators', []):
            if indicator in all_text:
                early_score += 1
                result['positive_factors'].append(f"Contains early indicator: {indicator}")
        
        for indicator in patterns.get('late_indicators', []):
            if indicator in all_text:
                late_score += 1
                result['risk_factors'].append(f"Contains late indicator: {indicator}")
        
        # Calculate progress ratio if possible
        progress_ratio = self._calculate_progress_ratio(
            prediction.get('current_progress', ''),
            prediction.get('target_value', '')
        )
        
        # Time horizon analysis
        if time_horizon <= 5:
            time_factor = 0.2  # Short term - easier to achieve
        elif time_horizon <= 10:
            time_factor = 0.0  # Medium term - neutral
        else:
            time_factor = -0.2  # Long term - harder to predict
        
        # Combine factors
        base_score = 0.0
        
        if progress_ratio is not None:
            if progress_ratio >= 0.8:
                base_score += 0.3
                result['positive_factors'].append(f"High progress ratio: {progress_ratio:.1%}")
            elif progress_ratio >= 0.5:
                base_score += 0.1
                result['positive_factors'].append(f"Moderate progress: {progress_ratio:.1%}")
            else:
                base_score -= 0.2
                result['risk_factors'].append(f"Low progress ratio: {progress_ratio:.1%}")
        
        # Factor in early/late indicators
        indicator_score = (early_score - late_score) * 0.1
        
        # Historical sector accuracy
        sector_weight = patterns.get('accuracy_weight', 0.6)
        historical_factor = (sector_weight - 0.5) * 0.2
        
        # Final score calculation
        final_score = base_score + indicator_score + time_factor + historical_factor
        
        # Classify likelihood
        if final_score > 0.15:
            result['likelihood'] = 'LIKELY EARLY'
            result['confidence'] = min(0.9, 0.6 + final_score)
        elif final_score < -0.15:
            result['likelihood'] = 'LATE-RISK'
            result['confidence'] = min(0.9, 0.6 + abs(final_score))
        else:
            result['likelihood'] = 'ON-TIME'
            result['confidence'] = 0.6 + abs(final_score) * 0.5
        
        # Generate reasoning
        result['reasoning'] = self._generate_reasoning(result, time_horizon, sector)
        
        return result
    
    def _calculate_progress_ratio(self, current_progress: str, target_value: str) -> Optional[float]:
        """Calculate progress ratio from current progress and target"""
        current_num = self._extract_numeric_value(current_progress)
        target_num = self._extract_numeric_value(target_value)
        
        if current_num is not None and target_num is not None and target_num != 0:
            return min(1.0, current_num / target_num)
        
        return None
    
    def _generate_reasoning(self, analysis: Dict, time_horizon: int, sector: str) -> str:
        """Generate human-readable reasoning for the likelihood assessment"""
        reasoning_parts = []
        
        # Time horizon
        if time_horizon <= 5:
            reasoning_parts.append("Short-term target allows for focused implementation")
        elif time_horizon > 10:
            reasoning_parts.append("Long-term horizon increases uncertainty")
        
        # Sector characteristics
        sector_patterns = self.sector_patterns.get(sector, {})
        accuracy = sector_patterns.get('accuracy_weight', 0.6)
        if accuracy > 0.7:
            reasoning_parts.append(f"{sector} sector has historically high accuracy")
        elif accuracy < 0.6:
            reasoning_parts.append(f"{sector} sector has historically faced implementation challenges")
        
        # Risk and positive factors
        if analysis['risk_factors']:
            reasoning_parts.append(f"Risk factors: {len(analysis['risk_factors'])} identified")
        if analysis['positive_factors']:
            reasoning_parts.append(f"Positive factors: {len(analysis['positive_factors'])} identified")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Standard assessment based on historical patterns"
    
    def _calculate_sector_likelihood(self, predictions: List[Dict]) -> str:
        """Calculate overall likelihood for a sector"""
        if not predictions:
            return 'ON-TIME'
        
        likelihood_scores = {
            'LIKELY EARLY': 1,
            'ON-TIME': 0,
            'LATE-RISK': -1
        }
        
        total_score = sum(likelihood_scores.get(p['likelihood'], 0) for p in predictions)
        avg_score = total_score / len(predictions)
        
        if avg_score > 0.3:
            return 'LIKELY EARLY'
        elif avg_score < -0.3:
            return 'LATE-RISK'
        else:
            return 'ON-TIME'
    
    def _calculate_confidence_score(self, sector: str, predictions: List[Dict], time_horizon: int) -> float:
        """Calculate confidence score for sector predictions"""
        if not predictions:
            return 0.0
        
        # Average individual confidences
        avg_confidence = sum(p.get('confidence', 0.0) for p in predictions) / len(predictions)
        
        # Adjust based on number of predictions (more predictions = higher confidence)
        count_factor = min(1.0, len(predictions) / 5.0) * 0.1
        
        # Adjust based on time horizon
        time_factor = max(0.0, 1.0 - time_horizon / 20.0) * 0.1
        
        return min(1.0, avg_confidence + count_factor + time_factor)
    
    def calculate_likelihood_stats(self, analysis: Dict) -> Dict[str, int]:
        """Calculate likelihood statistics across all analysis results"""
        stats = {'LIKELY EARLY': 0, 'ON-TIME': 0, 'LATE-RISK': 0}
        
        for sector_data in analysis.values():
            for prediction in sector_data.get('predictions', []):
                likelihood = prediction.get('likelihood', 'ON-TIME')
                stats[likelihood] = stats.get(likelihood, 0) + 1
        
        return stats
    
    def parse_natural_language_query(self, query: str) -> Dict:
        """Parse natural language query to extract parameters"""
        result = {
            'type': 'unknown',
            'forecast_year': None,
            'target_year': None,
            'sectors': [],
            'sources': []
        }
        
        query_lower = query.lower()
        
        # Extract years
        years = re.findall(r'\b(19|20)\d{2}\b', query)
        if len(years) >= 2:
            result['forecast_year'] = int(years[0])
            result['target_year'] = int(years[1])
        elif len(years) == 1:
            year = int(years[0])
            current_year = datetime.now().year
            if year <= current_year:
                result['target_year'] = year
                result['type'] = 'past_forecast'
            else:
                result['target_year'] = year
                result['type'] = 'future_prediction'
        
        # Determine query type based on keywords
        if any(word in query_lower for word in ['predictions', 'forecast', 'made', 'predicted']):
            if any(word in query_lower for word in ['happened', 'actual', 'reality', 'outcome']):
                result['type'] = 'past_forecast'
            else:
                result['type'] = 'future_prediction'
        
        # Extract sectors
        sector_keywords = {
            'Economy': ['economy', 'gdp', 'growth', 'economic'],
            'Energy': ['energy', 'power', 'renewable', 'solar', 'wind', 'coal'],
            'Infrastructure': ['infrastructure', 'railway', 'highway', 'transport'],
            'Technology': ['technology', 'digital', 'internet', 'mobile', 'it'],
            'Agriculture': ['agriculture', 'farming', 'crop', 'food'],
            'Education': ['education', 'literacy', 'school', 'university'],
            'Healthcare': ['health', 'medical', 'hospital', 'life expectancy'],
            'Environment': ['environment', 'climate', 'pollution', 'forest'],
            'Social Development': ['poverty', 'development', 'social', 'human development']
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                result['sectors'].append(sector)
        
        # Extract sources
        source_keywords = {
            'RBI': ['rbi', 'reserve bank'],
            'NITI Aayog': ['niti', 'aayog', 'planning'],
            'World Bank': ['world bank'],
            'Planning Commission': ['planning commission', 'five year plan'],
            'IEA': ['iea', 'international energy'],
            'Economic Times': ['economic times', 'et'],
            'The Hindu': ['hindu', 'the hindu']
        }
        
        for source, keywords in source_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                result['sources'].append(source)
        
        return result