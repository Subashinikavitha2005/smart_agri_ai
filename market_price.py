import json
import os
import random
from datetime import datetime, timedelta

# Mock market data - In production: connect to Agmarknet API
# API: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
MARKET_DATA = {
    "rice": {
        "tamil": "நெல்",
        "unit": "Quintal",
        "markets": [
            {"market": "Chennai APMC", "state": "Tamil Nadu", "base_price": 2100, "variety": "IR-20"},
            {"market": "Thanjavur", "state": "Tamil Nadu", "base_price": 2050, "variety": "Ponni"},
            {"market": "Trichy Market", "state": "Tamil Nadu", "base_price": 2080, "variety": "BPT"},
        ]
    },
    "wheat": {
        "tamil": "கோதுமை",
        "unit": "Quintal",
        "markets": [
            {"market": "Delhi Azadpur", "state": "Delhi", "base_price": 2200, "variety": "HD-2967"},
            {"market": "Ludhiana", "state": "Punjab", "base_price": 2150, "variety": "PBW-343"},
            {"market": "Jaipur", "state": "Rajasthan", "base_price": 2180, "variety": "GW-322"},
        ]
    },
    "cotton": {
        "tamil": "பருத்தி",
        "unit": "Quintal",
        "markets": [
            {"market": "Coimbatore APMC", "state": "Tamil Nadu", "base_price": 6200, "variety": "MCU-5"},
            {"market": "Erode Market", "state": "Tamil Nadu", "base_price": 6150, "variety": "Bunny Bt"},
            {"market": "Nagpur", "state": "Maharashtra", "base_price": 6300, "variety": "Suraj"},
        ]
    },
    "tomato": {
        "tamil": "தக்காளி",
        "unit": "Quintal",
        "markets": [
            {"market": "Koyambedu", "state": "Tamil Nadu", "base_price": 1200, "variety": "Local"},
            {"market": "Hosur APMC", "state": "Tamil Nadu", "base_price": 1100, "variety": "PKM-1"},
            {"market": "Bangalore APMC", "state": "Karnataka", "base_price": 1300, "variety": "Hybrid"},
        ]
    },
    "maize": {
        "tamil": "சோளம்",
        "unit": "Quintal",
        "markets": [
            {"market": "Erode APMC", "state": "Tamil Nadu", "base_price": 1900, "variety": "Hybrid"},
            {"market": "Salem Market", "state": "Tamil Nadu", "base_price": 1870, "variety": "Local"},
            {"market": "Davangere", "state": "Karnataka", "base_price": 1920, "variety": "HQPM-1"},
        ]
    },
    "groundnut": {
        "tamil": "நிலக்கடலை",
        "unit": "Quintal",
        "markets": [
            {"market": "Tirunelveli APMC", "state": "Tamil Nadu", "base_price": 5500, "variety": "TMV-2"},
            {"market": "Vellore Market", "state": "Tamil Nadu", "base_price": 5400, "variety": "TMV-7"},
            {"market": "Junagadh", "state": "Gujarat", "base_price": 5600, "variety": "GG-20"},
        ]
    },
    "sugarcane": {
        "tamil": "கரும்பு",
        "unit": "Tonne",
        "markets": [
            {"market": "Cuddalore Mill", "state": "Tamil Nadu", "base_price": 320, "variety": "Co-86032"},
            {"market": "Tiruchengode", "state": "Tamil Nadu", "base_price": 315, "variety": "Co-0212"},
            {"market": "Kolhapur", "state": "Maharashtra", "base_price": 335, "variety": "Co-86032"},
        ]
    },
    "banana": {
        "tamil": "வாழை",
        "unit": "Quintal",
        "markets": [
            {"market": "Trichy APMC", "state": "Tamil Nadu", "base_price": 2200, "variety": "Poovan"},
            {"market": "Erode Market", "state": "Tamil Nadu", "base_price": 2100, "variety": "Rasthali"},
            {"market": "Theni", "state": "Tamil Nadu", "base_price": 2400, "variety": "Grand Naine"},
        ]
    }
}

def get_market_prices(crop_name=None):
    """Get current market prices with simulated daily fluctuation."""
    today = datetime.now()
    
    def add_fluctuation(base_price):
        """Add realistic daily price fluctuation of ±5%"""
        seed = today.year * 365 + today.month * 30 + today.day
        random.seed(seed + hash(str(base_price)) % 1000)
        fluctuation = random.uniform(-0.05, 0.05)
        return round(base_price * (1 + fluctuation))
    
    def get_trend():
        """Simulate price trend"""
        random.seed(today.day + today.month)
        return random.choice(['up', 'down', 'stable', 'stable'])
    
    result = {}
    
    data_to_process = {}
    if crop_name and crop_name.lower() in MARKET_DATA:
        data_to_process[crop_name.lower()] = MARKET_DATA[crop_name.lower()]
    else:
        data_to_process = MARKET_DATA
    
    for crop_key, crop_info in data_to_process.items():
        markets_data = []
        for market in crop_info['markets']:
            current_price = add_fluctuation(market['base_price'])
            markets_data.append({
                'market': market['market'],
                'state': market['state'],
                'variety': market['variety'],
                'price': current_price,
                'unit': crop_info['unit'],
                'trend': get_trend(),
                'change': round(current_price - market['base_price'])
            })
        
        avg_price = round(sum(m['price'] for m in markets_data) / len(markets_data))
        
        result[crop_key] = {
            'name': crop_key.capitalize(),
            'tamil_name': crop_info['tamil'],
            'unit': crop_info['unit'],
            'avg_price': avg_price,
            'markets': markets_data,
            'last_updated': today.strftime('%d %b %Y, %I:%M %p'),
            'msp': get_msp(crop_key)
        }
    
    return result

def get_msp(crop):
    """Minimum Support Price for major crops (2024-25 season)"""
    msp_data = {
        'rice': 2300, 'wheat': 2275, 'maize': 2090, 'cotton': 7121,
        'groundnut': 6783, 'sugarcane': 340, 'tomato': None, 'banana': None
    }
    return msp_data.get(crop)
