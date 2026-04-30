/* ═══════════════════════════════════════
   app.js — Core SPA Router & Utilities
   ═══════════════════════════════════════ */

let currentLang = 'en';
let currentModule = 'dashboard';

const MODULE_TITLES = {
    dashboard: 'Dashboard / முகப்பு',
    dashboard: 'Dashboard / முகப்பு',
    crop: 'Crop Recommendation / பயிர் பரிந்துரை',
    disease: 'Disease & Pests / நோய் மற்றும் பூச்சி',
    weather: 'Weather Forecast / வானிலை முன்னறிவிப்பு',
    irrigation: 'Smart Irrigation / நீர்ப்பாசன ஆலோசனை',
    market: 'Market Prices / சந்தை விலை',
    chatbot: 'AI Chatbot / AI அரட்டை',
    schemes: 'Govt Schemes / அரசு திட்டங்கள்',
    fertilizer: 'Soil & Fertilizer / மண் மற்றும் உரம்',
    calendar: 'Crop Calendar / பயிர் நாட்காட்டி'
};

// ─── Module Router ───
function showModule(id) {
    document.querySelectorAll('.module-view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const view = document.getElementById(`module-${id}`);
    const nav  = document.getElementById(`nav-${id}`);
    if (view) { view.classList.add('active'); view.scrollTop = 0; }
    if (nav)  nav.classList.add('active');

    currentModule = id;
    document.getElementById('topbarTitle').textContent = MODULE_TITLES[id] || id;

    // Update URL hash
    window.location.hash = id === 'dashboard' ? '' : id;
    closeSidebar();

    // Lazy-load module data
    if (id === 'weather')    loadWeather();
    if (id === 'market')     loadMarketPrices();
    if (id === 'chatbot')    initChatbot();
    if (id === 'schemes')    loadSchemes();
    if (id === 'calendar')   loadCropCalendar();
}

// ─── Nav click listeners ───
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        showModule(item.dataset.module);
    });
});

// ─── Mobile Sidebar ───
document.getElementById('menuBtn').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('active');
});

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('overlay').classList.remove('active');
}

// ─── Language Toggle ───
function setLanguage(lang) {
    currentLang = lang;
    document.getElementById('langEn').classList.toggle('active', lang === 'en');
    document.getElementById('langTa').classList.toggle('active', lang === 'ta');
    showToast(lang === 'ta' ? '🌿 தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது' : '🌿 English selected', 'info');
}

// ─── Toast Notifications ───
function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('dismissing');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ─── API Helpers ───
async function apiPost(url, data) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!resp.ok) throw new Error(`API error ${resp.status}`);
    return resp.json();
}

async function apiGet(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`API error ${resp.status}`);
    return resp.json();
}

// ─── Button loading state ───
function setLoading(btn, loading) {
    if (loading) {
        btn.disabled = true;
        btn.classList.add('loading');
        btn._origText = btn.innerHTML;
    } else {
        btn.disabled = false;
        btn.classList.remove('loading');
        if (btn._origText) btn.innerHTML = btn._origText;
    }
}

// ─── Hash routing on load ───
window.addEventListener('load', () => {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    showModule(hash);
    loadWeatherPill();
});

// ─── Weather pill (top bar) ───
async function loadWeatherPill() {
    try {
        const data = await apiGet('/api/weather?city=Chennai');
        if (data.success) {
            const w = data.weather.current;
            document.getElementById('weatherPillTemp').textContent = `${w.temperature}°C`;
            document.getElementById('weatherPillCity').textContent = w.city;
        }
    } catch {}
}



// ─── Drag & drop for disease upload ───
document.addEventListener('DOMContentLoaded', () => {
    const zone = document.getElementById('uploadZone');
    if (!zone) return;
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) handleImageFile(e.dataTransfer.files[0]);
    });
    zone.addEventListener('click', () => document.getElementById('diseaseImageInput').click());
    document.getElementById('diseaseImageInput').addEventListener('change', e => {
        if (e.target.files[0]) handleImageFile(e.target.files[0]);
    });
});
