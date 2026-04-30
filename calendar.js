/* ═══════════════════════════════
   calendar.js — Crop Calendar
   ═══════════════════════════════ */

let calendarLoaded = false;

async function loadCropCalendar() {
    if (calendarLoaded) return;
    const display = document.getElementById('calendarDisplay');
    if (!display) return;

    try {
        const data = await apiGet('/api/crop/calendar');
        if (data.success) {
            renderCalendar(data.calendar, data.current_month_index);
            calendarLoaded = true;
        }
    } catch {
        display.innerHTML = `<div style="color:var(--red-500);padding:20px;">Failed to load calendar.</div>`;
    }
}

function renderCalendar(months, currentIdx) {
    const display = document.getElementById('calendarDisplay');
    const SEASON_COLORS = {
        kharif:     { bg: 'rgba(46,171,46,0.1)',   border: '#228b22', label: '🌧️ Kharif', labelColor: '#4ccc4c' },
        rabi:       { bg: 'rgba(59,130,246,0.1)',  border: '#3b82f6', label: '❄️ Rabi',   labelColor: '#60a5fa' },
        summer:     { bg: 'rgba(245,158,11,0.1)',  border: '#f59e0b', label: '☀️ Summer', labelColor: '#fbbf24' },
        transition: { bg: 'rgba(168,85,247,0.1)', border: '#a855f7', label: '🔄 Transition', labelColor: '#c084fc' }
    };

    const currentMonthName = months[currentIdx]?.month || '';

    display.innerHTML = `
        <!-- Current Month Banner -->
        <div style="background:linear-gradient(135deg,var(--green-800),var(--green-900));border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px 24px;margin-bottom:24px;display:flex;align-items:center;gap:16px">
            <div style="font-size:2.5rem">📅</div>
            <div>
                <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.7px;color:var(--green-300);margin-bottom:4px">Current Month / இந்த மாதம்</div>
                <div style="font-size:1.4rem;font-weight:800;color:var(--text-primary)">${currentMonthName} / ${months[currentIdx]?.month_ta || ''}</div>
                <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:4px">
                    ${months[currentIdx]?.activities.map(a => `✓ ${a}`).join(' &nbsp;|&nbsp; ') || ''}
                </div>
            </div>
        </div>

        <!-- Month Grid -->
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px">
            ${months.map((m, i) => {
                const sc = SEASON_COLORS[m.season] || SEASON_COLORS.transition;
                const isCurrent = i === currentIdx;
                return `
                    <div style="
                        background:${isCurrent ? 'rgba(46,171,46,0.12)' : 'var(--bg-card)'};
                        border:${isCurrent ? '2px solid var(--green-400)' : '1px solid var(--border)'};
                        border-radius:var(--radius-md);
                        padding:16px 18px;
                        position:relative;
                        transition:all 0.2s ease;
                        ${isCurrent ? 'box-shadow:0 0 20px rgba(46,171,46,0.25);' : ''}
                    ">
                        ${isCurrent ? `<div style="position:absolute;top:10px;right:12px;background:var(--green-600);color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:10px;text-transform:uppercase">NOW</div>` : ''}
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
                            <div style="font-size:1.1rem;font-weight:700;color:var(--text-primary)">${m.month}</div>
                            <div style="font-size:0.8rem;color:var(--green-400);font-family:var(--font-tamil)">${m.month_ta}</div>
                            <div style="margin-left:auto;background:${sc.bg};border:1px solid ${sc.border};color:${sc.labelColor};font-size:0.68rem;font-weight:600;padding:2px 10px;border-radius:20px;white-space:nowrap">${sc.label}</div>
                        </div>
                        <ul style="list-style:none;display:flex;flex-direction:column;gap:6px">
                            ${m.activities.map(a => `
                                <li style="display:flex;align-items:flex-start;gap:8px;font-size:0.82rem;color:var(--text-secondary)">
                                    <span style="color:${sc.labelColor};flex-shrink:0;margin-top:1px">▸</span> ${a}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }).join('')}
        </div>

        <!-- Season Legend -->
        <div style="margin-top:24px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:16px 20px">
            <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);margin-bottom:12px">Season Guide / பருவகால வழிகாட்டி</div>
            <div style="display:flex;flex-wrap:wrap;gap:12px">
                ${Object.entries(SEASON_COLORS).map(([s, sc]) => `
                    <div style="display:flex;align-items:center;gap:6px;font-size:0.82rem;color:var(--text-secondary)">
                        <div style="width:10px;height:10px;border-radius:50%;background:${sc.border}"></div>
                        ${sc.label}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
