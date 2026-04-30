import json
import os
import random
import base64
import requests

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'disease_data.json')

# Hugging Face model for plant disease detection
# Using nateraw/plant-disease - trained on PlantVillage dataset (38 classes)
HF_MODEL_URL = "https://api-inference.huggingface.co/models/nateraw/plant-disease"

# Label mapping from PlantVillage classes → our disease_data IDs
HF_LABEL_MAP = {
    "Rice___Leaf_blast":                    "rice_blast",
    "Rice___Brown_spot":                    "leaf_blight",
    "Rice___Bacterial_leaf_blight":         "leaf_blight",
    "Tomato___Early_blight":                "early_blight_tomato",
    "Tomato___Bacterial_spot":              "early_blight_tomato",
    "Tomato___Leaf_Mold":                   "powdery_mildew",
    "Tomato___healthy":                     "healthy",
    "Rice___healthy":                       "healthy",
    "Corn_(maize)___Common_rust_":          "powdery_mildew",
    "Cotton___Bacterial_blight":            "leaf_blight",
}

DISEASE_CLASSES = ['rice_blast', 'leaf_blight', 'powdery_mildew',
                   'early_blight_tomato', 'cotton_bollworm', 'armyworm', 'aphids', 'healthy']

def load_disease_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_disease(image_path, language='en', hf_api_key=''):
    """
    Detect disease from plant leaf image.
    Uses Hugging Face plant-disease model when API key is provided.
    Falls back to simulation otherwise.
    """
    detected_id = None
    confidence  = 0.0
    is_real     = False

    # ── Try real Hugging Face inference ─────────────────────────────────
    if hf_api_key:
        result = _hf_inference(image_path, hf_api_key)
        if result:
            detected_id = result['disease_id']
            confidence  = result['confidence']
            is_real     = True

    # ── Demo simulation fallback ─────────────────────────────────────────
    if not detected_id:
        detected_id = _simulate_detection(image_path)
        confidence  = round(random.uniform(72, 94), 1)
        is_real     = False

    # ── Build response from knowledge base ───────────────────────────────
    data     = load_disease_data()
    diseases = {d['id']: d for d in data['diseases']}

    if detected_id not in diseases:
        detected_id = 'healthy'

    disease = diseases[detected_id]
    lang_ta = (language == 'ta')

    return {
        'disease_id':      disease['id'],
        'disease_name':    disease['tamil_name'] if lang_ta else disease['name'],
        'disease_name_en': disease['name'],
        'disease_name_ta': disease['tamil_name'],
        'crop':            disease['crop'],
        'confidence':      confidence,
        'severity':        disease['severity'],
        'cause':           disease['cause'],
        'symptoms':        disease['symptoms_tamil'] if lang_ta else disease['symptoms'],
        'crop_protection': disease['crop_protection_tamil'] if lang_ta else disease.get('crop_protection', ''),
        'treatment': {
            'chemical':  disease['treatment_tamil']['chemical']  if lang_ta else disease['treatment']['chemical'],
            'organic':   disease['treatment_tamil']['organic']   if lang_ta else disease['treatment']['organic'],
            'preventive':disease['treatment_tamil']['preventive']if lang_ta else disease['treatment']['preventive'],
        },
        'is_demo': not is_real
    }


def _hf_inference(image_path, api_key):
    """Call Hugging Face Inference API with the plant disease image."""
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.post(
            HF_MODEL_URL,
            headers=headers,
            data=image_bytes,
            timeout=15
        )

        if resp.status_code == 503:
            # Model is loading — fall back to simulation
            return None

        resp.raise_for_status()
        predictions = resp.json()

        if not isinstance(predictions, list) or not predictions:
            return None

        # Pick the top prediction
        top = predictions[0]
        raw_label  = top.get('label', '')
        confidence = round(top.get('score', 0) * 100, 1)

        # Map HF label → our disease ID
        disease_id = HF_LABEL_MAP.get(raw_label, None)

        # Try partial matching if exact match fails
        if not disease_id:
            raw_lower = raw_label.lower()
            if 'blast'  in raw_lower:  disease_id = 'rice_blast'
            elif 'blight' in raw_lower: disease_id = 'leaf_blight'
            elif 'mildew' in raw_lower or 'rust' in raw_lower: disease_id = 'powdery_mildew'
            elif 'healthy' in raw_lower: disease_id = 'healthy'
            else: disease_id = 'powdery_mildew'   # generic fungal

        return {'disease_id': disease_id, 'confidence': confidence, 'raw_label': raw_label}

    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None


def _simulate_detection(image_path):
    try:
        file_size = os.path.getsize(image_path)
        weights = [12, 10, 10, 10, 12, 14, 12, 20]   # 20 % chance healthy
        return random.choices(DISEASE_CLASSES, weights=weights, k=1)[0]
    except Exception:
        return random.choice(DISEASE_CLASSES)


def get_all_diseases():
    return load_disease_data()['diseases']
