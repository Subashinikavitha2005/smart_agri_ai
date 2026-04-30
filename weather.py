import requests
import json
import os
from datetime import datetime, timedelta

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'weather_cache.json')

# Demo weather data for when API key is not configured
DEMO_WEATHER = {
    "current": {
        "city": "Chennai",
        "temperature": 32,
        "feels_like": 36,
        "humidity": 78,
        "wind_speed": 12,
        "description": "Partly Cloudy",
        "icon": "02d",
        "pressure": 1010,
        "visibility": 8,
        "rain_chance": 30
    },
    "forecast": [
        {"date": "Tomorrow", "max": 34, "min": 26, "description": "Sunny", "icon": "01d", "rain_chance": 10, "humidity": 70},
        {"date": "Day 3", "max": 31, "min": 25, "description": "Light Rain", "icon": "10d", "rain_chance": 65, "humidity": 85},
        {"date": "Day 4", "max": 29, "min": 24, "description": "Heavy Rain", "icon": "09d", "rain_chance": 80, "humidity": 90},
        {"date": "Day 5", "max": 30, "min": 25, "description": "Cloudy", "icon": "04d", "rain_chance": 40, "humidity": 80}
    ],
    "demo": True
}

def get_weather(city="Chennai", api_key=None):
    """
    Fetch weather data from OpenWeatherMap API.
    Falls back to demo data if API key is missing or request fails.
    """
    if not api_key or api_key == 'demo_key':
        weather = DEMO_WEATHER.copy()
        weather['farming_advice'] = generate_farming_advice(weather['current'], weather['forecast'])
        return weather
    
    # Check cache first
    cached = load_cache(city)
    if cached:
        return cached
    
    try:
        # Current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        curr_data = resp.json()
        
        # 5-day forecast
        fc_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&cnt=32"
        fc_resp = requests.get(fc_url, timeout=5)
        fc_resp.raise_for_status()
        fc_data = fc_resp.json()
        
        weather = parse_weather_response(curr_data, fc_data)
        weather['farming_advice'] = generate_farming_advice(weather['current'], weather['forecast'])
        
        # Cache it
        save_cache(city, weather)
        return weather
        
    except Exception as e:
        demo = DEMO_WEATHER.copy()
        demo['farming_advice'] = generate_farming_advice(demo['current'], demo['forecast'])
        demo['error'] = str(e)
        return demo

def parse_weather_response(curr, fc):
    current = {
        "city": curr['name'],
        "temperature": round(curr['main']['temp']),
        "feels_like": round(curr['main']['feels_like']),
        "humidity": curr['main']['humidity'],
        "wind_speed": round(curr['wind']['speed'] * 3.6, 1),
        "description": curr['weather'][0]['description'].title(),
        "icon": curr['weather'][0]['icon'],
        "pressure": curr['main']['pressure'],
        "visibility": round(curr.get('visibility', 10000) / 1000, 1),
        "rain_chance": round(curr.get('rain', {}).get('1h', 0) * 100)
    }
    
    # Process daily forecast - one entry per day
    forecast = []
    seen_dates = set()
    for item in fc['list']:
        date = datetime.fromtimestamp(item['dt'])
        date_str = date.strftime('%Y-%m-%d')
        if date_str not in seen_dates and len(forecast) < 4:
            seen_dates.add(date_str)
            forecast.append({
                "date": date.strftime('%b %d'),
                "max": round(item['main']['temp_max']),
                "min": round(item['main']['temp_min']),
                "description": item['weather'][0]['description'].title(),
                "icon": item['weather'][0]['icon'],
                "rain_chance": round(item.get('pop', 0) * 100),
                "humidity": item['main']['humidity']
            })
    
    return {"current": current, "forecast": forecast, "demo": False}

def generate_farming_advice(current, forecast):
    """Generate actionable farming advice based on weather conditions."""
    advice = []
    temp = current['temperature']
    humidity = current['humidity']
    
    # Rain prediction
    upcoming_rain = [d for d in forecast if d['rain_chance'] > 50]
    if upcoming_rain:
        advice.append({
            "type": "rain",
            "icon": "🌧️",
            "message": f"Rain expected in {len(upcoming_rain)} of next 4 days. Delay chemical spraying and harvest if possible.",
            "message_tamil": f"அடுத்த 4 நாட்களில் {len(upcoming_rain)} நாட்கள் மழை எதிர்பார்க்கப்படுகிறது. ரசாயன தெளிப்பு மற்றும் அறுவடையை தள்ளிப்போடுங்கள்.",
            "priority": "high"
        })
    
    if temp > 35:
        advice.append({
            "type": "heat",
            "icon": "🌡️",
            "message": f"High temperature {temp}°C. Water crops early morning or evening. Mulching recommended.",
            "message_tamil": f"அதிக வெப்பநிலை {temp}°C. அதிகாலை அல்லது மாலையில் நீர்ப்பாசனம் செய்யுங்கள். மல்ச்சிங் பரிந்துரைக்கப்படுகிறது.",
            "priority": "high"
        })
    
    if humidity > 85:
        advice.append({
            "type": "humidity",
            "icon": "💧",
            "message": f"High humidity ({humidity}%). Watch for fungal diseases. Ensure good air circulation in crop rows.",
            "message_tamil": f"அதிக ஈரப்பதம் ({humidity}%). பூஞ்சை நோய்களைக் கவனியுங்கள். பயிர் வரிசைகளில் நல்ல காற்று சுழற்சி உறுதி செய்யுங்கள்.",
            "priority": "medium"
        })
    
    if not advice:
        advice.append({
            "type": "good",
            "icon": "✅",
            "message": "Weather conditions are favorable for most farming activities today.",
            "message_tamil": "இன்று பெரும்பாலான விவசாய செயல்பாட்டிற்கு வானிலை சாதகமாக உள்ளது.",
            "priority": "low"
        })
    
    return advice

def load_cache(city):
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        entry = cache.get(city.lower())
        if not entry:
            return None
        
        cached_time = datetime.fromisoformat(entry['cached_at'])
        if datetime.now() - cached_time > timedelta(minutes=30):
            return None
        
        return entry['data']
    except:
        return None

def save_cache(city, data):
    try:
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
        cache[city.lower()] = {'cached_at': datetime.now().isoformat(), 'data': data}
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except:
        pass
