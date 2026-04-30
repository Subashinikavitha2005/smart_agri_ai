/* ════════════════════════════════
   irrigation.js — Smart Irrigation
   ════════════════════════════════ */

function updateMoistureDisplay(value) {
    document.getElementById('moistureReading').textContent = `${value}%`;
    document.getElementById('moistureFill').style.width = `${value}%`;

    const fill = document.getElementById('moistureFill');
    if (value < 30) {
        fill.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
    } else if (value < 55) {
        fill.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
    } else {
        fill.style.background = 'linear-gradient(90deg, var(--green-700), var(--green-400))';
    }
}

document.getElementById('irrigationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.submitter || e.target.querySelector('button[type="submit"]');
    setLoading(btn, true);

    const payload = {
        crop:           document.getElementById('irrigCrop').value,
        soil_moisture:  parseFloat(document.getElementById('moistureSlider').value),
        temperature:    parseFloat(document.getElementById('irrigTemp').value),
        humidity:       parseFloat(document.getElementById('irrigHumidity').value),
        rainfall_7days: parseFloat(document.getElementById('rainfall7d').value),
        area_hectares:  parseFloat(document.getElementById('farmArea').value)
    };

    try {
        const data = await apiPost('/api/irrigation/advice', payload);
        if (data.success) {
            renderIrrigationResult(data.advice, payload.crop);
            showToast('Irrigation advice ready! / நீர்ப்பாசன ஆலோசனை தயார்!', 'success');
        }
    } catch (err) {
        showToast('Failed to calculate irrigation advice.', 'error');
    } finally {
        setLoading(btn, false);
    }
});

function renderIrrigationResult(advice, crop) {
    const container = document.getElementById('irrigationResults');
    container.classList.remove('hidden');

    const urgencyIcons = {
        critical: '🚨', needed: '⚠️', monitor: '👀', adequate: '✅'
    };

    const actionText = currentLang === 'ta' ? advice.action_ta : advice.action;
    const urgencyText = currentLang === 'ta' ? advice.urgency_ta : advice.urgency.toUpperCase();
    const methodText = currentLang === 'ta' ? advice.irrigation_method_ta : advice.irrigation_method;
    const timeText = currentLang === 'ta' ? advice.best_times_ta : advice.best_times;

    container.innerHTML = `
        <div class="irrigation-result">
            <div class="urgency-banner urgency-${advice.urgency}" style="animation:bounce-in 0.4s ease">
                <span style="font-size:1.5rem">${urgencyIcons[advice.urgency]}</span>
                <div>
                    <div style="font-weight:700">${urgencyText}</div>
                    <div style="font-size:0.85rem;opacity:0.85;font-family:var(--font-tamil)">${actionText}</div>
                </div>
            </div>

            <div class="irrigation-stats">
                <div class="irrig-stat-card">
                    <div class="irrig-stat-value">${advice.water_needed_liters > 0 ? advice.water_needed_liters.toLocaleString() : '—'}</div>
                    <div class="irrig-stat-label">Total Liters Needed</div>
                </div>
                <div class="irrig-stat-card">
                    <div class="irrig-stat-value">${advice.daily_water_need_mm} mm</div>
                    <div class="irrig-stat-label">Daily Water Need</div>
                </div>
                <div class="irrig-stat-card">
                    <div class="irrig-stat-value">${advice.weekly_deficit_mm} mm</div>
                    <div class="irrig-stat-label">Weekly Deficit</div>
                </div>
                <div class="irrig-stat-card">
                    <div class="irrig-stat-value">${advice.temperature_effect === 'high' ? '🌡️ High' : advice.temperature_effect === 'low' ? '❄️ Low' : '✅ Normal'}</div>
                    <div class="irrig-stat-label">Temperature Effect</div>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
                <div class="irrig-method-card">
                    <div class="irrig-method-name">💧 ${methodText}</div>
                    <div class="irrig-method-reason">${advice.method_reason}</div>
                </div>
                <div class="irrig-method-card">
                    <div class="irrig-method-name">⏰ Best Time to Water</div>
                    <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px;">
                        ${timeText.map(t => `<span style="font-size:0.85rem;color:var(--green-300);font-family:var(--font-tamil)">${t}</span>`).join('')}
                    </div>
                </div>
            </div>

            <div style="background:rgba(46,171,46,0.06);border-radius:8px;padding:14px;border:1px solid var(--border)">
                <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.7px;color:var(--text-muted);margin-bottom:8px">
                    💡 Pro Tips for ${crop.charAt(0).toUpperCase() + crop.slice(1)}
                </div>
                <ul style="list-style:none;display:flex;flex-direction:column;gap:6px;">
                    <li style="font-size:0.82rem;color:var(--text-secondary)">• Water at soil level to avoid leaf wetting and fungal risk</li>
                    <li style="font-size:0.82rem;color:var(--text-secondary)">• Avoid irrigating on windy days (>20 km/h) to reduce evaporation loss</li>
                    <li style="font-size:0.82rem;color:var(--text-secondary)">• Check soil moisture with a simple finger test 5cm deep before each irrigation</li>
                </ul>
            </div>
        </div>
    `;
}
