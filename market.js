/* ════════════════════════════════
   market.js — Market Prices
   ════════════════════════════════ */

let allMarketData = {};

async function loadMarketPrices(cropFilter = null) {
    const display = document.getElementById('marketDisplay');
    if (!display) return;

    display.innerHTML = `<div class="loading-spinner"><div class="spinner"></div><p>Loading prices... / விலைகள் ஏற்றுகிறது...</p></div>`;

    try {
        const url = cropFilter ? `/api/market/prices?crop=${cropFilter}` : '/api/market/prices';
        const data = await apiGet(url);
        if (data.success) {
            allMarketData = data.prices;
            renderMarketPrices(data.prices);
        }
    } catch (err) {
        display.innerHTML = `<div style="color:var(--red-500);padding:20px;">Failed to load market data.</div>`;
    }
}

function filterMarket(crop, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    loadMarketPrices(crop === 'all' ? null : crop);
}

function renderMarketPrices(prices) {
    const display = document.getElementById('marketDisplay');
    const dateStr = new Date().toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });

    display.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
            <span style="font-size:0.82rem;color:var(--text-muted)">📅 Updated: ${dateStr}</span>
            <button onclick="loadMarketPrices()" class="btn-outline" style="padding:7px 14px;font-size:0.8rem;">🔄 Refresh / புதுப்பி</button>
        </div>
        ${Object.entries(prices).map(([key, crop]) => renderCropPriceCard(key, crop)).join('')}
    `;
}

function renderCropPriceCard(key, crop) {
    const mspNote = crop.msp
        ? `<span class="market-msp">MSP: ₹${crop.msp}/${crop.unit}</span>`
        : '';

    const rows = crop.markets.map(m => {
        const trendIcon = m.trend === 'up' ? '↑' : m.trend === 'down' ? '↓' : '→';
        const trendClass = m.trend === 'up' ? 'price-up' : m.trend === 'down' ? 'price-down' : 'price-stable';
        const changeSign = m.change > 0 ? '+' : '';

        return `
            <tr>
                <td>
                    <div style="font-weight:500">${m.market}</div>
                    <div style="font-size:0.72rem;color:var(--text-muted)">${m.state}</div>
                </td>
                <td style="font-size:0.75rem;color:var(--text-muted)">${m.variety}</td>
                <td>
                    <span style="font-weight:700;color:var(--text-primary)">₹${m.price.toLocaleString()}</span>
                    <span style="font-size:0.72rem;color:var(--text-muted)">/${crop.unit}</span>
                </td>
                <td class="${trendClass}">
                    <span class="trend-icon">${trendIcon}</span>
                    <span style="font-size:0.78rem">${changeSign}${m.change}</span>
                </td>
            </tr>
        `;
    }).join('');

    return `
        <div class="market-crop-card" data-crop="${key}">
            <div class="market-crop-header">
                <div>
                    <div class="market-crop-name">${crop.name}</div>
                    <div class="market-crop-ta">${crop.tamil_name}</div>
                </div>
                <div style="text-align:right;">
                    <div class="market-avg-price">₹${crop.avg_price.toLocaleString()} <span style="font-size:0.7rem;color:var(--text-muted);font-weight:400">avg/${crop.unit}</span></div>
                    ${mspNote}
                </div>
            </div>
            <table class="market-table">
                <thead>
                    <tr>
                        <th>Market / சந்தை</th>
                        <th>Variety</th>
                        <th>Price / விலை</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;
}
