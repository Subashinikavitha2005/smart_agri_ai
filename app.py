import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime

from config import Config
from modules.crop_recommend import recommend_crops, get_soil_types
from modules.disease_detect import detect_disease
from modules.weather import get_weather
from modules.irrigation import calculate_irrigation
from modules.market_price import get_market_prices
from modules.chatbot import get_response, get_quick_topics

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS crop_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soil_type TEXT, season TEXT, temperature REAL,
            rainfall REAL, recommended_crops TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS disease_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT, detected_disease TEXT, confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

# ——— Routes ———

@app.route('/')
def welcome():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()
        # Check if email exists
        if conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            conn.close()
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
            
        # Create user
        hashed_pw = generate_password_hash(password)
        conn.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                     (name, email, hashed_pw))
        conn.commit()
        conn.close()
        
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user_name=session.get('user_name', 'Farmer'))


# ——— Crop Recommendation ———
@app.route('/api/crop/recommend', methods=['POST'])
def crop_recommend():
    data = request.get_json()
    soil_type = data.get('soil_type', 'loamy')
    season = data.get('season', 'kharif')
    temperature = float(data.get('temperature', 28))
    rainfall = float(data.get('rainfall', 100))
    language = data.get('language', 'en')
    
    results = recommend_crops(soil_type, season, temperature, rainfall, language)
    
    # Save to history
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO crop_history (soil_type, season, temperature, rainfall, recommended_crops) VALUES (?,?,?,?,?)',
            (soil_type, season, temperature, rainfall, json.dumps([r['name'] for r in results]))
        )
        conn.commit()
        conn.close()
    except:
        pass
    
    return jsonify({'success': True, 'recommendations': results})

@app.route('/api/crop/soil-types', methods=['GET'])
def soil_types():
    return jsonify({'soil_types': get_soil_types()})

# ——— Disease Detection ———
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/disease/detect', methods=['POST'])
def disease_detect():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    file = request.files['image']
    language = request.form.get('language', 'en')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Use JPG, PNG, or WEBP'}), 400
    
    if file:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = detect_disease(filepath, language, hf_api_key=app.config.get('HF_API_KEY', ''))
        
        # Save to history
        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO disease_history (image_path, detected_disease, confidence) VALUES (?,?,?)',
                (filename, result.get('disease_name_en', ''), result.get('confidence', 0))
            )
            conn.commit()
            conn.close()
        except:
            pass
        
        result['image_url'] = f"/uploads/{filename}"
        return jsonify({'success': True, 'result': result})

# ——— Weather ———
@app.route('/api/weather', methods=['GET'])
def weather():
    city = request.args.get('city', 'Chennai')
    api_key = app.config.get('WEATHER_API_KEY', 'demo_key')
    data = get_weather(city, api_key)
    return jsonify({'success': True, 'weather': data})

# ——— Irrigation ———
@app.route('/api/irrigation/advice', methods=['POST'])
def irrigation_advice():
    data = request.get_json()
    crop = data.get('crop', 'rice')
    soil_moisture = float(data.get('soil_moisture', 50))
    temperature = float(data.get('temperature', 30))
    humidity = float(data.get('humidity', 70))
    rainfall_7days = float(data.get('rainfall_7days', 20))
    area = float(data.get('area_hectares', 1.0))
    
    result = calculate_irrigation(crop, soil_moisture, temperature, humidity, rainfall_7days, area)
    return jsonify({'success': True, 'advice': result})

# ——— Market Prices ———
@app.route('/api/market/prices', methods=['GET'])
def market_prices():
    crop = request.args.get('crop', None)
    data = get_market_prices(crop)
    return jsonify({'success': True, 'prices': data})

# ——— Chatbot ———
@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    data     = request.get_json()
    message  = data.get('message', '')
    language = data.get('language', 'en')
    gemini_key = app.config.get('GEMINI_API_KEY', '')
    result   = get_response(message, language, gemini_api_key=gemini_key)
    return jsonify({'success': True, **result})

@app.route('/api/chatbot/topics', methods=['GET'])
def chatbot_topics():
    return jsonify({'success': True, 'topics': get_quick_topics()})

# ——— Government Schemes ———
@app.route('/api/schemes', methods=['GET'])
def govt_schemes():
    with open('data/govt_schemes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify({'success': True, 'schemes': data['schemes']})

# ——— Fertilizer Calculator ———
@app.route('/api/fertilizer/calculate', methods=['POST'])
def fertilizer_calculate():
    data = request.get_json()
    crop = data.get('crop', 'rice').lower()
    area = float(data.get('area_hectares', 1.0))
    soil_ph = float(data.get('soil_ph', 6.5))
    organic_matter = data.get('organic_matter', 'medium')

    # Base NPK requirements per hectare (kg)
    NPK_BASE = {
        'rice':      {'N': 120, 'P': 60,  'K': 60},
        'wheat':     {'N': 120, 'P': 60,  'K': 40},
        'maize':     {'N': 120, 'P': 60,  'K': 40},
        'cotton':    {'N': 180, 'P': 90,  'K': 90},
        'sugarcane': {'N': 250, 'P': 100, 'K': 120},
        'tomato':    {'N': 150, 'P': 100, 'K': 100},
        'groundnut': {'N': 25,  'P': 50,  'K': 50},
        'banana':    {'N': 200, 'P': 60,  'K': 300},
    }
    base = NPK_BASE.get(crop, NPK_BASE['rice'])

    # Adjust for organic matter
    om_factor = {'low': 1.1, 'medium': 1.0, 'high': 0.85}.get(organic_matter, 1.0)
    N = round(base['N'] * om_factor * area)
    P = round(base['P'] * area)
    K = round(base['K'] * area)

    # Convert to fertilizer bags
    UREA_N    = 0.46  # 46% N
    DAP_NP    = {'N': 0.18, 'P': 0.46}
    MOP_K     = 0.60  # 60% K

    dap_bags_25kg  = round((P / DAP_NP['P']) / 25, 1)
    n_from_dap     = round(dap_bags_25kg * 25 * DAP_NP['N'])
    remaining_n    = max(0, N - n_from_dap)
    urea_bags_50kg = round((remaining_n / UREA_N) / 50, 1)
    mop_bags_50kg  = round((K / MOP_K) / 50, 1)

    crop_name_map = {
        'rice': 'நெல்', 'wheat': 'கோதுமை', 'maize': 'சோளம்',
        'cotton': 'பருத்தி', 'sugarcane': 'கரும்பு', 'tomato': 'தக்காளி',
        'groundnut': 'நிலக்கடலை', 'banana': 'வாழை'
    }

    return jsonify({
        'success': True,
        'result': {
            'crop': crop.capitalize(),
            'crop_ta': crop_name_map.get(crop, crop),
            'area_hectares': area,
            'npk_kg': {'N': N, 'P': P, 'K': K},
            'fertilizers': [
                {'name': 'DAP (Di-Ammonium Phosphate)',  'formula': '18:46:0', 'quantity_kg': round(dap_bags_25kg * 25), 'bags': f'{dap_bags_25kg} x 25kg bags'},
                {'name': 'Urea',                          'formula': '46:0:0',  'quantity_kg': round(urea_bags_50kg * 50), 'bags': f'{urea_bags_50kg} x 50kg bags'},
                {'name': 'MOP (Muriate of Potash)',        'formula': '0:0:60', 'quantity_kg': round(mop_bags_50kg * 50), 'bags': f'{mop_bags_50kg} x 50kg bags'},
            ],
            'application_schedule': {
                'basal': '50% N + full P + 50% K at sowing/transplanting',
                'top_dress_1': '25% N at 30 days after sowing',
                'top_dress_2': '25% N + 50% K at 60 days or before flowering'
            },
            'organic_supplement': f'Apply 5 tons FYM or vermicompost/hectare before sowing',
            'note': 'Adjust based on soil test report for best accuracy.'
        }
    })

# ——— Crop Calendar ———
@app.route('/api/crop/calendar', methods=['GET'])
def crop_calendar():
    calendar = [
        {'month': 'January',   'month_ta': 'ஜனவரி',    'activities': ['Harvest Kharif crops', 'Sow Rabi vegetables', 'Apply organic manure to fields'], 'season': 'rabi'},
        {'month': 'February',  'month_ta': 'பிப்ரவரி', 'activities': ['Irrigate Rabi crops', 'Pest monitoring', 'Prune fruit trees'], 'season': 'rabi'},
        {'month': 'March',     'month_ta': 'மார்ச்',    'activities': ['Harvest Rabi wheat', 'Prepare summer crop fields', 'Soil testing season'], 'season': 'summer'},
        {'month': 'April',     'month_ta': 'ஏப்ரல்',   'activities': ['Sow summer vegetables', 'Tomato & brinjal transplanting', 'Water conservation'], 'season': 'summer'},
        {'month': 'May',       'month_ta': 'மே',        'activities': ['Deep summer ploughing', 'Apply green manure', 'Repair irrigation channels'], 'season': 'summer'},
        {'month': 'June',      'month_ta': 'ஜூன்',     'activities': ['Sow Kharif crops (rice, cotton)', 'Monsoon preparation', 'Apply basal fertilizer'], 'season': 'kharif'},
        {'month': 'July',      'month_ta': 'ஜூலை',     'activities': ['Paddy transplanting', 'Cotton sowing', 'Weed management'], 'season': 'kharif'},
        {'month': 'August',    'month_ta': 'ஆகஸ்ட்',   'activities': ['Top dress nitrogen for rice', 'Pest scouting', 'Pheromone trap monitoring'], 'season': 'kharif'},
        {'month': 'September', 'month_ta': 'செப்டம்பர்', 'activities': ['Spray fungicide if blast risk', 'Harvesting early varieties', 'Fodder crop sowing'], 'season': 'kharif'},
        {'month': 'October',   'month_ta': 'அக்டோபர்',  'activities': ['Harvest Kharif paddy', 'Prepare Rabi fields', 'Apply FYM/compost'], 'season': 'transition'},
        {'month': 'November',  'month_ta': 'நவம்பர்',   'activities': ['Sow Rabi wheat & pulses', 'Plant winter vegetables', 'Install drip for horticulture'], 'season': 'rabi'},
        {'month': 'December',  'month_ta': 'டிசம்பர்',  'activities': ['Irrigate Rabi crops', 'Prune sugarcane ratoon', 'Apply zinc sulphate'], 'season': 'rabi'},
    ]
    current_month = datetime.now().month - 1  # 0-indexed
    return jsonify({'success': True, 'calendar': calendar, 'current_month_index': current_month})

# ——— Farming Tips & Smart Alerts ———
@app.route('/api/tips', methods=['GET'])
def daily_tips():
    # Simulated daily seasonal tips
    tips = [
        {"en": "Mulch your tomato plants to retain soil moisture during peak heat.", "ta": "கோடை வெயிலில் மண் ஈரப்பதத்தை தக்கவைக்க தக்காளி செடிகளுக்கு மூடாக்கு அமைக்கவும்."},
        {"en": "Check underneath cotton leaves for early signs of Whitefly infestation.", "ta": "பருத்தி இலைகளுக்கு அடியில் வெள்ளை ஈ தாக்குதல் உள்ளதா என கண்காணிக்கவும்."},
        {"en": "Ensure proper drainage in rice fields to prevent bacterial leaf blight spreading.", "ta": "நெல் வயல்களில் தண்ணீர் தேங்காமல் பார்த்துக் கொள்ளவும், இது பாக்டீரியா கருகல் நோயை தடுக்கும்."},
        {"en": "Deep plow your fields in summer to expose pest pupae to birds and heat.", "ta": "கோடையில் ஆழமாக உழுவதன் மூலம் பூச்சிகளின் கூட்டுப்புழுக்களை அழிக்கலாம்."},
        {"en": "Intercrop your main crop with legumes to naturally fix nitrogen in the soil.", "ta": "நைட்ரஜனை மண்ணில் நிலைநிறுத்த பயறு வகைகளை ஊடுபயிராக சாகுபடி செய்யவும்."}
    ]
    import random
    return jsonify({"success": True, "tip": random.choice(tips)})

@app.route('/api/alerts', methods=['GET'])
def smart_alerts():
    # Simulated real-time alerts
    alerts = [
        {"type": "weather", "icon": "🌧️", "title": "Heavy Rain Alert", "title_ta": "கனமழை எச்சரிக்கை", "desc": "Expected in next 48 hours. Secure harvested crops.", "desc_ta": "அடுத்த 48 மணி நேரத்தில் மழை பெய்ய வாய்ப்பு. அறுவடை செய்த பயிர்களை பாதுகாக்கவும்."},
        {"type": "pest", "icon": "🐛", "title": "Fall Armyworm Warning", "title_ta": "படைப்புழு எச்சரிக்கை", "desc": "High risk detected in nearby maize fields.", "desc_ta": "அருகிலுள்ள மக்காச்சோள வயல்களில் பாதிப்பு. கண்காணிக்கவும்."},
        {"type": "market", "icon": "📈", "title": "Tomato Price Surge", "title_ta": "தக்காளி விலை உயர்வு", "desc": "Prices are up 15% in Koyambedu market.", "desc_ta": "கோயம்பேடு சந்தையில் விலை 15% உயர்ந்துள்ளது."},
        {"type": "irrigation", "icon": "💧", "title": "Irrigation Recommended", "title_ta": "நீர்ப்பாசன ஆலோசனை", "desc": "Soil moisture drops critical tomorrow.", "desc_ta": "நாளை மண் ஈரப்பதம் குறையும். நீர் பாய்ச்சவும்."}
    ]
    import random
    # Return 2 random active alerts
    return jsonify({"success": True, "alerts": random.sample(alerts, 2)})

# ——— Static uploads ———
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    print("AgriSmart Assistant starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
