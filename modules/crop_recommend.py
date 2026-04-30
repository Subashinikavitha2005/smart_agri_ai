def recommend_crops(soil, season, temperature, rainfall):
    if soil == "Loamy":
        return ["Wheat", "Rice", "Sugarcane"]
    elif soil == "Sandy":
        return ["Millet", "Groundnut", "Cotton"]
    else:
        return ["Rice", "Maize", "Pulses"]

def get_soil_types():
    return ["Loamy", "Sandy", "Clay"]
