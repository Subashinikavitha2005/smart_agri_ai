/* ═══════════════════════════
   crop.js — Crop Recommendation
   ═══════════════════════════ */

document.getElementById('cropForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('cropSubmitBtn');
    setLoading(btn, true);

    const payload = {
        soil_type: document.getElementById('soilType').value,
        season:    document.getElementById('season').value,
        temperature: parseFloat(document.getElementById('tempInput').value),
        rainfall:    parseFloat(document.getElementById('rainfallInput').value),
        language: currentLang
    };

    try {
        const data = await apiPost('/api/crop/recommend', payload);
        renderCropResults(data.recommendations);
        showToast('Crop recommendations ready! / பயிர் பரிந்துரைகள் தயார்!', 'success');
    } catch (err) {
        showToast('Failed to get recommendations. / பரிந்துரை தோல்வி.', 'error');
    } finally {
        setLoading(btn, false);
    }
});

function renderCropResults(recs) {
    const container = document.getElementById('cropResults');
    container.classList.remove('hidden');

    const html = `
        <h3 style="margin-bottom:16px;font-size:1.1rem;color:var(--green-300);">
            🏆 Top Crop Recommendations / சிறந்த பயிர் பரிந்துரைகள்
        </h3>
        <div class="crop-results-grid">
            ${recs.map(r => renderCropCard(r)).join('')}
        </div>
    `;
    container.innerHTML = html;

    // Animate confidence bars
    setTimeout(() => {
        container.querySelectorAll('.confidence-fill').forEach(bar => {
            bar.style.width = bar.dataset.width + '%';
        });
    }, 100);
}

function renderCropCard(crop) {
    const reasons = crop.reasons.join(' • ');
    return `
        <div class="crop-result-card rank-${crop.rank}">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                <div>
                    <div class="crop-name">${crop.name}</div>
                    <div class="crop-ta-name">${crop.tamil_name}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.3rem;font-weight:800;color:var(--amber-400)">${crop.confidence}%</div>
                    <div style="font-size:0.7rem;color:var(--text-muted)">Match</div>
                </div>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" data-width="${crop.confidence}" style="width:0"></div>
            </div>
            <div class="crop-meta">
                <span class="meta-tag">⏱ ${crop.duration_days} days</span>
                <span class="meta-tag">💧 ${crop.water_requirement}</span>
                <span class="meta-tag">📦 ${crop.yield_per_hectare}/ha</span>
                <span class="meta-tag">₹ ${crop.market_price_range}/q</span>
            </div>
            ${reasons ? `<div style="font-size:0.75rem;color:var(--green-400);margin-bottom:8px;">✓ ${reasons}</div>` : ''}
            <div class="crop-tips">${crop.tips}</div>
        </div>
    `;
}
