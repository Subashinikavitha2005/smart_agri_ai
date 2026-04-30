/* ════════════════════════════════
   schemes.js — Government Schemes
   ════════════════════════════════ */

async function loadSchemes() {
    const display = document.getElementById('schemesDisplay');
    if (!display || display.querySelector('.scheme-card')) return; // Already loaded

    display.innerHTML = `<div class="loading-spinner"><div class="spinner"></div><p>Loading schemes... / திட்டங்களை ஏற்றுகிறது...</p></div>`;

    try {
        const data = await apiGet('/api/schemes');
        if (data.success) renderSchemes(data.schemes);
    } catch {
        display.innerHTML = `<div style="color:var(--red-500);padding:20px;">Failed to load schemes.</div>`;
    }
}

function renderSchemes(schemes) {
    const display = document.getElementById('schemesDisplay');

    const categoryIcons = {
        income_support: '💰', insurance: '🛡️', credit: '💳',
        irrigation: '💧', soil: '🌱'
    };

    display.innerHTML = `
        <div style="background:rgba(46,171,46,0.06);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.5rem">📢</span>
            <div>
                <div style="font-weight:600;color:var(--text-primary)">Kisan Call Center / கிசான் கால் சென்டர்</div>
                <div style="font-size:0.85rem;color:var(--text-secondary)">Free Expert Advice Available 24x7</div>
                <div style="font-size:1rem;font-weight:700;color:var(--green-300);margin-top:4px;">📞 1800-180-1551</div>
            </div>
        </div>
        <div class="schemes-display">
            ${schemes.map(s => renderSchemeCard(s, categoryIcons)).join('')}
        </div>
    `;
}

function renderSchemeCard(scheme, icons) {
    const icon = icons[scheme.category] || '📋';
    const desc = currentLang === 'ta' ? scheme.description_tamil : scheme.description;
    const name_ta = scheme.tamil_name;

    return `
        <div class="scheme-card" style="animation:slide-in-up 0.4s ease">
            <div class="scheme-header">
                <div>
                    <div class="scheme-name">${icon} ${scheme.name}</div>
                    <div style="font-size:0.78rem;color:var(--text-muted)">${scheme.full_name}</div>
                    <div class="scheme-ta-name">${name_ta}</div>
                </div>
                <div class="scheme-benefit-badge">✨ ${scheme.benefit}</div>
            </div>
            <div class="scheme-desc">${desc}</div>
            <div style="margin-bottom:12px;">
                <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:6px">Eligibility</div>
                <div style="font-size:0.82rem;color:var(--text-secondary)">${scheme.eligibility}</div>
            </div>
            <div style="margin-bottom:14px;">
                <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:6px">How to Apply / விண்ணப்பிக்கும் முறை</div>
                <div style="font-size:0.82rem;color:var(--text-secondary);font-family:var(--font-tamil)">${scheme.how_to_apply}</div>
            </div>
            <div class="scheme-footer">
                <span class="scheme-tag">📞 ${scheme.helpline}</span>
                <span class="scheme-tag">🏷 ${scheme.category.replace('_', ' ')}</span>
                <a href="${scheme.website}" target="_blank" rel="noopener" class="scheme-apply-btn">
                    🌐 Apply / விண்ணப்பி →
                </a>
            </div>
        </div>
    `;
}
