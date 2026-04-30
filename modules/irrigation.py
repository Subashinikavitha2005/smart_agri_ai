def calculate_irrigation(temperature, humidity):
    if temperature > 30:
        return "High water needed"
    elif temperature > 20:
        return "Medium water needed"
    else:
        return "Low water needed"
