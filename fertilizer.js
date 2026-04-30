/* ═══════════════════════════════════════
   fertilizer.js — Fertilizer Calculator
   ═══════════════════════════════════════ */

document.getElementById('fertilizerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    setLoading(btn, true);

    const payload = {
        crop:           document.getElementById('fertCrop').value,
        area_hectares:  parseFloat(document.getElementById('fertArea').value),
        soil_ph:        parseFloat(document.getElementById('fertPh').value),
        organic_matter: document.getElementById('fertOM').value
    };

    try {
        const data = await apiPost('/api/fertilizer/calculate', payload);
        if (data.success) {
            renderFertilizerResult(data.result);
            showToast('Fertilizer plan ready! / உர திட்டம் தயார்!', 'success');
        }
    } catch (err) {
        showToast('Calculation failed. Please try again.', 'error');
    } finally {
        setLoading(btn, false);
    }
});

function renderFertilizerResult(r) {
    const container = document.getElementById('fertilizerResults');
    container.classList.remove('hidden');

    const fertIcons = { 'DAP (Di-Ammonium Phosphate)': '🔵', 'Urea': '⚪', 'MOP (Muriate of Potash)': '🔴' };
    const scheduleEntries = Object.entries(r.application_schedule);

    container.innerHTML = `
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:28px;animation:bounce-in 0.4s ease">

            <!-- Header -->
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)">
                <div style="font-size:2rem">🧪</div>
                <div>
                    <div style="font-size:1.2rem;font-weight:700;color:var(--text-primary)">${r.crop} / ${r.crop_ta}</div>
                    <div style="font-size:0.85rem;color:var(--text-muted)">Area: ${r.area_hectares} ha &nbsp;|&nbsp; NPK Required: <strong style="color:var(--green-300)">${r.npk_kg.N}:${r.npk_kg.P}:${r.npk_kg.K} kg</strong></div>
                </div>
            </div>

            <!-- Fertilizer Bags -->
            <h3 style="font-size:0.9rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:14px">Fertilizer Quantities / உர அளவுகள்</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin-bottom:24px">
                ${r.fertilizers.map(f => `
                    <div style="background:var(--bg-input);border:1px solid var(--border);border-radius:var(--radius-md);padding:18px;text-align:center">
                        <div style="font-size:1.8rem;margin-bottom:8px">${fertIcons[f.name] || '🟢'}</div>
                        <div style="font-size:0.78rem;font-weight:600;color:var(--text-muted);margin-bottom:4px">${f.formula}</div>
                        <div style="font-size:0.85rem;font-weight:500;color:var(--text-secondary);margin-bottom:8px">${f.name.split('(')[0].trim()}</div>
                        <div style="font-size:1.4rem;font-weight:800;color:var(--amber-400)">${f.quantity_kg} kg</div>
                        <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px">${f.bags}</div>
                    </div>
                `).join('')}
            </div>

            <!-- Application Schedule -->
            <h3 style="font-size:0.9rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:12px">Application Schedule / உரமிடல் அட்டவணை</h3>
            <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:20px">
                ${scheduleEntries.map(([key, val], i) => `
                    <div style="background:var(--bg-input);border-left:3px solid var(--green-${i===0?'500':'600'});border-radius:0 var(--radius-sm) var(--radius-sm) 0;padding:12px 16px">
                        <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:4px">
                            ${key === 'basal' ? '1️⃣ Basal Dose' : key === 'top_dress_1' ? '2️⃣ Top Dressing 1' : '3️⃣ Top Dressing 2'}
                        </div>
                        <div style="font-size:0.85rem;color:var(--text-secondary)">${val}</div>
                    </div>
                `).join('')}
            </div>

            <!-- Organic tip -->
            <div style="background:rgba(46,171,46,0.06);border:1px solid var(--green-800);border-radius:var(--radius-md);padding:14px 16px;display:flex;gap:10px;align-items:flex-start">
                <span style="font-size:1.2rem;flex-shrink:0">🌿</span>
                <div>
                    <div style="font-size:0.78rem;font-weight:700;color:var(--green-300);margin-bottom:4px">ORGANIC SUPPLEMENT / கரிம சேர்க்கை</div>
                    <div style="font-size:0.83rem;color:var(--text-secondary)">${r.organic_supplement}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:6px">ℹ️ ${r.note}</div>
                </div>
            </div>
        </div>
    `;
}
