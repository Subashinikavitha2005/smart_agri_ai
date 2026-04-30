def calculate_irrigation(crop, soil_moisture, temperature, humidity, rainfall_last_7_days, area_hectares=1.0):
    """
    Calculate smart irrigation recommendations using simplified ET₀ approach.
    
    Parameters:
    - crop: crop type string
    - soil_moisture: 0-100 (percent)
    - temperature: current temperature in °C
    - humidity: relative humidity %
    - rainfall_last_7_days: mm in past 7 days
    - area_hectares: farm area
    """
    
    # Crop water requirements (mm/day) by crop
    CROP_ETC = {
        'rice': 8.0, 'wheat': 4.5, 'maize': 5.5, 'cotton': 5.0,
        'sugarcane': 7.0, 'groundnut': 4.0, 'tomato': 5.5, 'banana': 6.0,
        'default': 5.0
    }
    
    # Critical moisture thresholds by crop
    MOISTURE_THRESHOLD = {
        'rice': 50, 'wheat': 40, 'maize': 35, 'cotton': 35,
        'sugarcane': 45, 'groundnut': 30, 'tomato': 40, 'banana': 50,
        'default': 40
    }
    
    crop_lower = crop.lower()
    daily_etc = CROP_ETC.get(crop_lower, CROP_ETC['default'])
    threshold = MOISTURE_THRESHOLD.get(crop_lower, MOISTURE_THRESHOLD['default'])
    
    # Adjust for temperature
    if temperature > 35:
        daily_etc *= 1.25
        temp_note = "high"
    elif temperature < 20:
        daily_etc *= 0.75
        temp_note = "low"
    else:
        temp_note = "normal"
    
    # Adjust for humidity
    if humidity > 80:
        daily_etc *= 0.85
    elif humidity < 40:
        daily_etc *= 1.15
    
    # Effective rainfall consideration
    effective_rain = min(rainfall_last_7_days * 0.7, daily_etc * 7)
    
    # Calculate deficit
    deficit = max(0, (daily_etc * 7) - effective_rain)
    
    # Volume in mm per hectare (1mm = 10,000 liters/ha)
    total_liters_per_ha = deficit * 10000
    total_liters = total_liters_per_ha * area_hectares
    
    # Urgency assessment
    if soil_moisture < threshold * 0.7:
        urgency = "critical"
        urgency_ta = "அவசரம்"
        action = "Irrigate immediately. Soil moisture critically low."
        action_ta = "உடனனே நீர்ப்பாசனம் செய்யுங்கள். மண் ஈரப்பதம் மிகக் குறைவாக உள்ளது."
    elif soil_moisture < threshold:
        urgency = "needed"
        urgency_ta = "தேவை"
        action = "Irrigation required in the next 1-2 days."
        action_ta = "அடுத்த 1-2 நாட்களில் நீர்ப்பாசனம் தேவை."
    elif soil_moisture < threshold * 1.2:
        urgency = "monitor"
        urgency_ta = "கண்காணிக்கவும்"
        action = "Moisture adequate but monitor daily."
        action_ta = "ஈரப்பதம் போதுமானது, ஆனால் தினமும் கண்காணிக்கவும்."
    else:
        urgency = "adequate"
        urgency_ta = "போதுமானது"
        action = "Soil moisture is good. No irrigation needed today."
        action_ta = "மண் ஈரப்பதம் நல்லது. இன்று நீர்ப்பாசனம் தேவையில்லை."
        total_liters = 0
    
    # Best irrigation times
    best_times = ["6:00 AM - 8:00 AM", "5:00 PM - 7:00 PM"]
    best_times_ta = ["காலை 6:00 - 8:00", "மாலை 5:00 - 7:00"]
    
    # Method recommendation
    if crop_lower in ['banana', 'sugarcane', 'tomato']:
        method = "Drip Irrigation"
        method_ta = "சொட்டு நீர்ப்பாசனம்"
        method_reason = "Saves 40-60% water, prevents leaf diseases"
    elif crop_lower in ['rice']:
        method = "Flood / FMD Irrigation"
        method_ta = "வெள்ள நீர்ப்பாசனம்"
        method_reason = "Traditional flooding with AWD technique saves 30% water"
    else:
        method = "Sprinkler or Furrow"
        method_ta = "தெளிப்பு நீர்ப்பாசனம்"
        method_reason = "Efficient for field crops"
    
    return {
        "urgency": urgency,
        "urgency_ta": urgency_ta,
        "action": action,
        "action_ta": action_ta,
        "water_needed_liters": round(total_liters),
        "water_needed_per_hectare": round(total_liters_per_ha),
        "best_times": best_times,
        "best_times_ta": best_times_ta,
        "irrigation_method": method,
        "irrigation_method_ta": method_ta,
        "method_reason": method_reason,
        "daily_water_need_mm": round(daily_etc, 1),
        "temperature_effect": temp_note,
        "weekly_deficit_mm": round(deficit, 1)
    }
