/* ════════════════════════════════
   weather.js — Weather Forecast
   ════════════════════════════════ */

const WEATHER_ICONS = {
    '01d':'☀️','01n':'🌙','02d':'⛅','02n':'🌙',
    '03d':'☁️','03n':'☁️','04d':'☁️','04n':'☁️',
    '09d':'🌧️','09n':'🌧️','10d':'🌦️','10n':'🌦️',
    '11d':'⛈️','11n':'⛈️','13d':'❄️','13n':'❄️',
    '50d':'🌫️','50n':'🌫️'
};

function getWeatherIcon(code) {
    return WEATHER_ICONS[code] || '🌤️';
}

async function loadWeather() {
    const city = document.getElementById('cityInput')?.value || 'Chennai';
    const display = document.getElementById('weatherDisplay');
    if (!display) return;

    display.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Fetching weather for ${city}... / ${city} வானிலை பெறுகிறது...</p>
        </div>`;

    try {
        const data = await apiGet(`/api/weather?city=${encodeURIComponent(city)}`);
        if (data.success) {
            renderWeather(data.weather);
            document.getElementById('weatherPillTemp').textContent = `${data.weather.current.temperature}°C`;
            document.getElementById('weatherPillCity').textContent = data.weather.current.city;
        }
    } catch (err) {
        display.innerHTML = `<div style="color:var(--red-500);padding:20px;">Failed to load weather. / வானிலை பெற முடியவில்லை.</div>`;
    }
}

function renderWeather(weather) {
    const w = weather.current;
    const display = document.getElementById('weatherDisplay');
    const icon = getWeatherIcon(w.icon);
    const isDemo = weather.demo;

    display.innerHTML = `
        ${isDemo ? `<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:8px;padding:8px 14px;font-size:0.8rem;color:var(--blue-400);margin-bottom:16px;display:flex;gap:8px;">
            <span>ℹ️</span> Demo weather data — Add your OpenWeatherMap API key in config.py for live data.
        </div>` : ''}
        
        <div class="weather-current-card">
            <div class="weather-main">
                <div class="weather-icon-large">${icon}</div>
                <div>
                    <div class="weather-city">📍 ${w.city}</div>
                    <div class="weather-temp">${w.temperature}°C</div>
                    <div class="weather-desc">${w.description}</div>
                </div>
            </div>
            <div class="weather-stats">
                <div class="weather-stat">
                    <div class="weather-stat-value">💧 ${w.humidity}%</div>
                    <div class="weather-stat-label">Humidity / ஈரப்பதம்</div>
                </div>
                <div class="weather-stat">
                    <div class="weather-stat-value">💨 ${w.wind_speed} km/h</div>
                    <div class="weather-stat-label">Wind / காற்று</div>
                </div>
                <div class="weather-stat">
                    <div class="weather-stat-value">🌡️ ${w.feels_like}°C</div>
                    <div class="weather-stat-label">Feels Like</div>
                </div>
                <div class="weather-stat">
                    <div class="weather-stat-value">🔵 ${w.pressure} hPa</div>
                    <div class="weather-stat-label">Pressure</div>
                </div>
            </div>
        </div>

        <h3 style="margin-bottom:14px;font-size:1rem;font-weight:600;color:var(--text-primary)">📅 5-Day Forecast / 5 நாள் முன்னறிவிப்பு</h3>
        <div class="forecast-grid">
            ${weather.forecast.map(f => `
                <div class="forecast-card">
                    <div class="forecast-date">${f.date}</div>
                    <div class="forecast-icon">${getWeatherIcon(f.icon)}</div>
                    <div class="forecast-temp">
                        <span class="max">${f.max}°</span>
                        <span style="color:var(--text-muted)"> / </span>
                        <span class="min">${f.min}°</span>
                    </div>
                    <div class="forecast-rain">🌧 ${f.rain_chance}% rain</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);margin-top:3px;">${f.description}</div>
                </div>
            `).join('')}
        </div>

        <div class="farming-advice-section">
            <h3>🌾 Farming Advice / விவசாய ஆலோசனை</h3>
            <div class="advice-cards">
                ${weather.farming_advice.map(a => `
                    <div class="advice-card ${a.priority}">
                        <div class="advice-icon">${a.icon}</div>
                        <div class="advice-text">${currentLang === 'ta' ? a.message_tamil : a.message}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function useMyLocation() {
    if (!navigator.geolocation) {
        showToast('Geolocation not supported on this device.', 'error');
        return;
    }
    showToast('Detecting location... / இடம் கண்டறிகிறது...', 'info');
    navigator.geolocation.getCurrentPosition(
        pos => {
            // Use coordinates to get weather (requires lat/lon API call)
            showToast('Location detected! Loading weather...', 'success');
            loadWeather(); // Simplified: use default city for now
        },
        () => {
            showToast('Location access denied. / இட அணுகல் மறுக்கப்பட்டது.', 'error');
        }
    );
}

// Auto-load on enter key
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('cityInput');
    if (input) {
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') loadWeather();
        });
    }
});
