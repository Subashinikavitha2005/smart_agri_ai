import json
import os
import random
import requests

INTENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_intents.json')

AGRI_SYSTEM_PROMPT = """You are SmartAgri, an expert AI agriculture assistant for Indian farmers, especially Tamil Nadu farmers.

Your expertise covers:
- Crop cultivation (rice, wheat, cotton, sugarcane, maize, tomato, groundnut, banana)
- Plant disease identification and treatment (chemical, organic, preventive)
- Smart irrigation and water management
- Fertilizer recommendations (NPK, Urea, DAP, MOP)
- Weather-based farming advice
- Government agricultural schemes (PM-KISAN, PMFBY, KCC, PMKSY, Soil Health Card)
- Market prices and selling strategies
- Organic farming methods
- Pest management (IPM approach)
- Soil health and testing

Rules:
1. Always respond in the SAME language the user writes in. If Tamil script → reply in Tamil. If English → reply in English.
2. Keep answers practical, concise, and farmer-friendly. Avoid technical jargon.
3. Give specific quantities, timings, and product names when recommending treatments.
4. Always mention safety precautions for chemical treatments.
5. If you don't know something specific to a region, say so honestly.
6. End with one actionable tip the farmer can do TODAY.

Do NOT answer questions unrelated to agriculture, farming, or rural livelihoods."""

def load_intents():
    with open(INTENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['intents']

def get_response(user_message, language='en', gemini_api_key=''):
    """
    Get chatbot response.
    Uses Google Gemini AI if API key is provided, otherwise falls back to rule-based matching.
    """
    if not user_message.strip():
        return {
            "response": "Please type your question. / உங்கள் கேள்வியை தட்டச்சு செய்யுங்கள்.",
            "intent": "empty",
            "confidence": 0,
            "source": "fallback"
        }

    # ── Try Gemini AI first ──────────────────────────────────────────────
    if gemini_api_key:
        result = _gemini_response(user_message, gemini_api_key)
        if result:
            return result

    # ── Fallback: rule-based intent matching ─────────────────────────────
    return _rule_based_response(user_message, language)


def _gemini_response(message, api_key):
    """Call Google Gemini 1.5 Flash API (free tier)."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": AGRI_SYSTEM_PROMPT}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "Understood. I'm SmartAgri, ready to help Tamil Nadu farmers with crop, disease, irrigation, and market questions."}]
                },
                {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400,
                "topP": 0.9
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"}
            ]
        }

        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if text:
                return {
                    "response": text.strip(),
                    "intent": "gemini_ai",
                    "confidence": 98,
                    "source": "gemini"
                }
    except requests.exceptions.Timeout:
        pass  # Fall through to rule-based
    except Exception:
        pass

    return None


def _rule_based_response(message, language='en'):
    """Keyword-based intent matching fallback."""
    message_lower = message.lower().strip()
    intents = load_intents()

    best_intent = None
    best_score = 0

    for intent in intents:
        score = 0
        for pattern in intent['patterns']:
            pattern_lower = pattern.lower()
            if pattern_lower in message_lower:
                score = max(score, len(pattern_lower))
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_intent and best_score > 2:
        responses = best_intent['responses']
        response = responses[0] if language == 'ta' else (responses[1] if len(responses) > 1 else responses[0])
        return {
            "response": response,
            "intent": best_intent['tag'],
            "confidence": min(90, int((best_score / 20) * 100 + 50)),
            "source": "rule_based"
        }

    fallbacks = {
        'en': "I'm not sure about that. Ask me about crops, diseases, weather, irrigation, fertilizers, or market prices! 🌱",
        'ta': "புரியவில்லை. பயிர், நோய், வானிலை, நீர்ப்பாசனம், உரம் அல்லது சந்தை விலை பற்றி கேளுங்கள்! 🌱"
    }
    return {
        "response": fallbacks.get(language, fallbacks['en']),
        "intent": "unknown",
        "confidence": 0,
        "source": "fallback"
    }


def get_quick_topics():
    return [
        {"text": "Best crop for clay soil",       "text_ta": "களிமண்ணுக்கு சிறந்த பயிர்", "icon": "🌾"},
        {"text": "How to treat rice blast",        "text_ta": "நெல் குழி நோய் சிகிச்சை",   "icon": "🔬"},
        {"text": "Fertilizer for cotton 2 acres",  "text_ta": "2 ஏக்கர் பருத்திக்கு உரம்",  "icon": "🧪"},
        {"text": "PM-KISAN scheme how to apply",   "text_ta": "PM-KISAN விண்ணப்பிக்கும் முறை","icon": "📋"},
        {"text": "Today's tomato market price",    "text_ta": "இன்று தக்காளி சந்தை விலை",   "icon": "📈"},
        {"text": "When to irrigate rice",          "text_ta": "நெல்லுக்கு நீர்ப்பாசன நேரம்", "icon": "💧"},
        {"text": "Organic pest control methods",   "text_ta": "கரிம பூச்சி கட்டுப்பாடு",     "icon": "🌿"},
        {"text": "Drip irrigation subsidy",        "text_ta": "சொட்டு நீர் மானியம்",          "icon": "💰"},
    ]
