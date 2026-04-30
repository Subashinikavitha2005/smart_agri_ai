import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'crop_data.json')

def load_crop_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def recommend_crops(soil_type, season, temperature, rainfall, language='en'):
    """
    Recommend crops based on soil type, season, temperature, and rainfall.
    Uses rule-based matching with scoring algorithm.
    """
    data = load_crop_data()
    crops = data['crops']
    
    scored_crops = []
    
    for crop in crops:
        score = 0
        reasons = []
        
        # Soil compatibility (40 points max)
        soil_lower = soil_type.lower()
        if any(s.lower() in soil_lower or soil_lower in s.lower() 
               for s in crop['soil_types']):
            score += 40
            reasons.append(f"Soil compatible")
        elif len(crop['soil_types']) >= 3:
            score += 15  # Versatile crop
        
        # Season compatibility (30 points)
        season_lower = season.lower()
        if season_lower in [s.lower() for s in crop['seasons']]:
            score += 30
            reasons.append(f"Right season")
        elif 'annual' in [s.lower() for s in crop['seasons']]:
            score += 20

        # Temperature range (20 points)
        if crop['temp_min'] <= temperature <= crop['temp_max']:
            score += 20
            reasons.append(f"Optimal temperature")
        elif (crop['temp_min'] - 5) <= temperature <= (crop['temp_max'] + 5):
            score += 10

        # Rainfall compatibility (10 points)
        if crop['rainfall_min'] <= rainfall <= crop['rainfall_max']:
            score += 10
            reasons.append(f"Good rainfall match")
        elif rainfall > crop['rainfall_min']:
            score += 5

        # Add slight randomness to break ties
        score += random.uniform(0, 2)
        
        if score > 20:
            scored_crops.append({
                'score': score,
                'crop': crop,
                'reasons': reasons
            })
    
    # Sort by score descending
    scored_crops.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 3
    results = []
    for i, item in enumerate(scored_crops[:3]):
        crop = item['crop']
        confidence = min(95, int((item['score'] / 100) * 100))
        
        result = {
            'rank': i + 1,
            'name': crop['name'],
            'tamil_name': crop['tamil_name'],
            'confidence': confidence,
            'duration_days': crop['duration_days'],
            'water_requirement': crop['water_requirement'],
            'market_price_range': crop['market_price_range'],
            'yield_per_hectare': crop['yield_per_hectare'],
            'reasons': item['reasons'],
            'tips': crop['tips_tamil'] if language == 'ta' else crop['tips']
        }
        results.append(result)
    
    return results

def get_soil_types():
    data = load_crop_data()
    return data['soil_types']
