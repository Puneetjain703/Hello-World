"""
Configuration file for India Prediction Dashboard
===============================================

Contains settings, constants, and configuration parameters for the dashboard.
"""

import os
from datetime import datetime
from typing import Dict, List

# Application Settings
APP_NAME = "India Prediction Dashboard"
APP_VERSION = "1.0.0"
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# Time Settings
CURRENT_YEAR = datetime.now().year
HISTORICAL_START_YEAR = 1924  # 100 years back from ~2024
FUTURE_END_YEAR = CURRENT_YEAR + 100  # 100 years ahead
FORECAST_STEP_YEARS = 5

# Cache Settings
CACHE_DURATION_SECONDS = 3600  # 1 hour
ENABLE_CACHING = True

# Data Source Configurations
DATA_SOURCE_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
REQUEST_DELAY = 1  # seconds between requests

# Supported Sectors
SECTORS = [
    "Economy",
    "Energy", 
    "Infrastructure",
    "Technology",
    "Agriculture",
    "Education",
    "Healthcare",
    "Environment",
    "Social Development"
]

# Supported Data Sources  
DATA_SOURCES = [
    "IEA",
    "RBI", 
    "MoSPI",
    "NITI Aayog",
    "PIB",
    "UN DESA",
    "World Bank",
    "Reuters",
    "The Hindu",
    "Economic Times",
    "Mint",
    "Planning Commission"
]

# API Endpoints
API_ENDPOINTS = {
    'WORLD_BANK': 'https://api.worldbank.org/v2/country/IND/indicator',
    'RBI': 'https://www.rbi.org.in/scripts/rss.aspx',
    'NITI_AAYOG': 'https://www.niti.gov.in/documents-reports',
    'ECONOMIC_TIMES': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    'THE_HINDU': 'https://www.thehindu.com/news/national/feeder/default.rss'
}

# World Bank Indicators
WORLD_BANK_INDICATORS = {
    'GDP_GROWTH': 'NY.GDP.MKTP.KD.ZG',
    'GDP_TOTAL': 'NY.GDP.MKTP.CD', 
    'GDP_PER_CAPITA': 'NY.GDP.PCAP.CD',
    'POPULATION': 'SP.POP.TOTL',
    'ENERGY_USE': 'EG.USE.COMM.KT.OE',
    'ELECTRIC_POWER': 'EG.ELC.PROD.KH',
    'RENEWABLE_ENERGY': 'EG.FEC.RNEW.ZS',
    'CO2_EMISSIONS': 'EN.ATM.CO2E.KT',
    'FOREST_AREA': 'AG.LND.FRST.K2',
    'LIFE_EXPECTANCY': 'SP.DYN.LE00.IN',
    'LITERACY_RATE': 'SE.ADT.LITR.ZS',
    'INFANT_MORTALITY': 'SP.DYN.IMRT.IN'
}

# Classification Thresholds
ACCURACY_THRESHOLDS = {
    'strict': 0.05,    # 5% tolerance
    'moderate': 0.15,  # 15% tolerance
    'loose': 0.25      # 25% tolerance
}

# Prediction Confidence Levels
CONFIDENCE_LEVELS = {
    'high': 0.8,
    'medium': 0.6,
    'low': 0.4
}

# Sector Analysis Patterns
SECTOR_PATTERNS = {
    'Economy': {
        'early_indicators': ['digital', 'services', 'IT', 'startup', 'fintech'],
        'late_indicators': ['manufacturing', 'infrastructure', 'heavy industry', 'mining'],
        'accuracy_weight': 0.7,
        'typical_delays': ['policy implementation', 'regulatory approval', 'land acquisition']
    },
    'Energy': {
        'early_indicators': ['solar', 'wind', 'renewable', 'digital', 'private sector'],
        'late_indicators': ['coal', 'nuclear', 'grid', 'transmission', 'government'],
        'accuracy_weight': 0.6,
        'typical_delays': ['environmental clearance', 'land acquisition', 'grid connectivity']
    },
    'Infrastructure': {
        'early_indicators': ['metro', 'airports', 'digital', 'private'],
        'late_indicators': ['railway', 'highway', 'ports', 'land acquisition', 'government'],
        'accuracy_weight': 0.5,
        'typical_delays': ['land acquisition', 'environmental clearance', 'funding delays']
    },
    'Technology': {
        'early_indicators': ['mobile', 'internet', 'digital', 'startup', 'private'],
        'late_indicators': ['manufacturing', 'hardware', 'regulation', 'government'],
        'accuracy_weight': 0.8,
        'typical_delays': ['regulatory approval', 'data privacy laws', 'spectrum allocation']
    },
    'Agriculture': {
        'early_indicators': ['irrigation', 'seeds', 'technology', 'private'],
        'late_indicators': ['land reform', 'subsidies', 'weather', 'government'],
        'accuracy_weight': 0.6,
        'typical_delays': ['weather dependency', 'policy changes', 'market access']
    },
    'Education': {
        'early_indicators': ['digital', 'online', 'private', 'technology'],
        'late_indicators': ['government', 'infrastructure', 'teachers', 'rural'],
        'accuracy_weight': 0.7,
        'typical_delays': ['teacher recruitment', 'infrastructure development', 'curriculum updates']
    },
    'Healthcare': {
        'early_indicators': ['digital', 'private', 'pharma', 'technology'],
        'late_indicators': ['government', 'infrastructure', 'rural', 'doctors'],
        'accuracy_weight': 0.6,
        'typical_delays': ['doctor shortage', 'infrastructure gaps', 'regulatory approval']
    },
    'Environment': {
        'early_indicators': ['solar', 'electric', 'private', 'technology'],
        'late_indicators': ['coal', 'government', 'industrial', 'policy'],
        'accuracy_weight': 0.5,
        'typical_delays': ['policy implementation', 'industrial resistance', 'cost factors']
    },
    'Social Development': {
        'early_indicators': ['digital', 'urban', 'private', 'technology'],
        'late_indicators': ['rural', 'government', 'infrastructure', 'traditional'],
        'accuracy_weight': 0.6,
        'typical_delays': ['rural-urban divide', 'implementation gaps', 'behavioral change']
    }
}

# Color Schemes for Visualizations
COLOR_SCHEMES = {
    'status': {
        'EARLY': '#2E8B57',      # Sea Green
        'ON-TIME': '#FF8C00',    # Dark Orange
        'LATE': '#DC143C',       # Crimson
        'LIKELY EARLY': '#2E8B57',
        'LATE-RISK': '#DC143C',
        'UNKNOWN': '#808080'     # Gray
    },
    'primary': '#1f77b4',       # Blue
    'secondary': '#ff7f0e',     # Orange
    'tertiary': '#2ca02c',      # Green
    'quaternary': '#d62728'     # Red
}

# Search Terms for Historical Data
SEARCH_TERMS = {
    'historical_forecasts': [
        'India {} forecast {}',
        'India planning commission {} vision {}',  
        'India five year plan {} projection {}',
        'India economic survey {} target {}',
        'Planning Commission {} plan {}',
        'Government of India {} strategy {}'
    ],
    'sector_specific': {
        'Economy': ['GDP', 'growth rate', 'per capita income', 'inflation', 'economic'],
        'Energy': ['power generation', 'renewable energy', 'coal production', 'electricity', 'solar', 'wind'],
        'Infrastructure': ['railway', 'highway', 'airports', 'ports', 'transport', 'roads'],
        'Technology': ['internet', 'mobile', 'digitization', 'IT sector', 'software', 'telecom'],
        'Agriculture': ['food production', 'crop yield', 'irrigation', 'farming', 'agricultural'],
        'Education': ['literacy rate', 'enrollment', 'universities', 'schools', 'education'],
        'Healthcare': ['life expectancy', 'infant mortality', 'hospitals', 'health', 'medical'],
        'Environment': ['forest cover', 'carbon emissions', 'air quality', 'pollution', 'climate'],
        'Social Development': ['poverty rate', 'human development index', 'social', 'development']
    }
}

# Known Historical Predictions (Sample Data)
SAMPLE_HISTORICAL_DATA = {
    1975: {
        2000: {
            'Economy': [
                {
                    'metric': 'GDP Growth Rate',
                    'predicted_value': '6.5% annually',
                    'actual_value': '5.9% annually',
                    'source': 'Fifth Five Year Plan',
                    'status': 'LATE'
                }
            ],
            'Energy': [
                {
                    'metric': 'Power Generation Capacity',
                    'predicted_value': '100 GW',
                    'actual_value': '86 GW',
                    'source': 'Power Ministry Plan 1975',
                    'status': 'LATE'
                }
            ]
        }
    },
    2000: {
        2025: {
            'Economy': [
                {
                    'metric': 'GDP Size',
                    'predicted_value': '$5 Trillion',
                    'actual_value': '$3.7 Trillion (2024)',
                    'source': 'Vision 2020 Document',
                    'status': 'LATE'
                }
            ]
        }
    }
}

# Current Key Targets (2024-2030)
CURRENT_TARGETS = {
    2030: {
        'Energy': [
            {
                'metric': 'Renewable Energy Capacity',
                'target_value': '450 GW',
                'current_progress': '118 GW (2024)',
                'source': 'NITI Aayog',
                'announcement_date': '2019-09-23'
            }
        ],
        'Economy': [
            {
                'metric': 'GDP Size',
                'target_value': '$5 Trillion',
                'current_progress': '$3.7 Trillion (2024)',
                'source': 'Government of India',
                'announcement_date': '2019-08-15'
            }
        ],
        'Infrastructure': [
            {
                'metric': 'Highway Length',
                'target_value': '200,000 km',
                'current_progress': '146,000 km (2024)',
                'source': 'Ministry of Road Transport',
                'announcement_date': '2021-02-01'
            }
        ]
    }
}

# File Paths
DATA_DIR = "data"
CACHE_DIR = "cache"
EXPORT_DIR = "exports"
LOG_DIR = "logs"

# Create directories if they don't exist
import os
for directory in [DATA_DIR, CACHE_DIR, EXPORT_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/dashboard.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}