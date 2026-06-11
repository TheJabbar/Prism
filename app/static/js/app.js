// PRISM Terminal — Main Application Controller

const API_BASE = '/api/v1';

let charts = {};

// === Navigation ===
function closePopup() {
    const p = document.querySelector('.indicator-popup-chart');
    if (p) { if (p._chart) p._chart.destroy(); p.remove(); }
}
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        closePopup();
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelectorAll('.module').forEach(m => m.classList.remove('active'));
        this.classList.add('active');
        const module = this.dataset.module;
        document.getElementById(`module-${module}`).classList.add('active');
        document.getElementById('statusRight').textContent = `Module: ${module.toUpperCase()}`;
    });
});

// === Clock ===
function updateClock() {
    const now = new Date();
    const wib = now.toLocaleString('en-ID', { timeZone: 'Asia/Jakarta', hour12: false });
    document.getElementById('clock').textContent = wib;
}
setInterval(updateClock, 1000);
updateClock();

// === API Helper ===
async function apiGet(path) {
    try {
        const res = await fetch(`${API_BASE}${path}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error(`API GET ${path} failed:`, e);
        return null;
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error(`API POST ${path} failed:`, e);
        return null;
    }
}

// === Dashboard ===
async function loadDashboard() {
    const data = await apiGet('/market/summary');
    if (!data) return;

    document.getElementById('ihsg-value').textContent = data.ihsg.last.toLocaleString();
    document.getElementById('ihsg-change').textContent = `${data.ihsg.change_pct > 0 ? '+' : ''}${data.ihsg.change_pct.toFixed(2)}%`;
    document.getElementById('ihsg-change').className = `card-change ${data.ihsg.change_pct >= 0 ? 'up' : 'down'}`;

    document.getElementById('usdidr-value').textContent = data.usdidr.last.toLocaleString();
    document.getElementById('usdidr-change').textContent = `${data.usdidr.change_pct > 0 ? '+' : ''}${data.usdidr.change_pct.toFixed(2)}%`;
    document.getElementById('usdidr-change').className = `card-change ${data.usdidr.change_pct >= 0 ? 'up' : 'down'}`;

    // Ticker tape
    const tickerIhsg = document.getElementById('ticker-ihsg');
    if (tickerIhsg && data.ihsg) {
        tickerIhsg.innerHTML = `IHSG ${data.ihsg.last.toLocaleString()} <span class="change">${data.ihsg.change_pct > 0 ? '+' : ''}${data.ihsg.change_pct.toFixed(2)}%</span>`;
        tickerIhsg.className = `ticker-item ${data.ihsg.change_pct >= 0 ? 'up' : 'down'}`;
    }
    const tickerUsdidr = document.getElementById('ticker-usdidr');
    if (tickerUsdidr && data.usdidr) {
        tickerUsdidr.innerHTML = `USD/IDR ${data.usdidr.last.toLocaleString()} <span class="change">${data.usdidr.change_pct > 0 ? '+' : ''}${data.usdidr.change_pct.toFixed(2)}%</span>`;
        tickerUsdidr.className = `ticker-item ${data.usdidr.change_pct >= 0 ? 'up' : 'down'}`;
    }

    // Fetch BI rate for dashboard card and ticker
    apiGet('/indicators/macro').then(indData => {
        if (!indData) return;
        const biRate = indData.monetary_policy?.find(i => i.name === 'BI-7DRR');
        if (!biRate) return;
        const rateVal = parseFloat(biRate.value).toFixed(2);
        document.getElementById('birate-value').textContent = rateVal + '%';
        const tickerBirate = document.getElementById('ticker-birate');
        if (tickerBirate) tickerBirate.textContent = 'BI Rate ' + rateVal + '%';
    });

    // Sparkline charts
    createSparkline('chart-ihsg', [6820, 6840, 6830, 6850, 6845], '#00FF88');
    createSparkline('chart-usdidr', [16150, 16200, 16250, 16280, 16250], '#FF3B3B');
}

function createSparkline(canvasId, data, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.clientWidth;
    const height = 60;
    canvas.width = width;
    canvas.height = height;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    const stepX = width / (data.length - 1);

    ctx.clearRect(0, 0, width, height);
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    data.forEach((val, i) => {
        const x = i * stepX;
        const y = height - ((val - min) / range) * (height - 10) - 5;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Fill
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = color + '20';
    ctx.fill();
}

// === Market Monitor ===
const FORMATTERS = {
    number: (v) => v.toLocaleString('id-ID', { maximumFractionDigits: 0 }),
    decimal: (v) => v.toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    pct: (v) => v.toFixed(2) + '%',
    'pct-1dp': (v) => v.toFixed(1) + '%',
    'currency-idr': (v) => 'Rp' + v.toLocaleString('id-ID', { maximumFractionDigits: 0 }),
    'currency-usd': (v) => '$' + v.toFixed(2),
    bps: (v) => v.toFixed(0) + ' bps',
};

function makePopupChart(el) {
    let hist;
    try { hist = JSON.parse(el.dataset.history); } catch(ex) { return; }
    if (!hist || hist.length < 2) return;

    const fmt = FORMATTERS[el.dataset.fmt] || FORMATTERS.number;

    const rect = el.getBoundingClientRect();
    const popup = document.createElement('div');
    popup.className = 'indicator-popup-chart';
    const cvs = document.createElement('canvas');
    cvs.width = 260;
    cvs.height = 160;
    popup.appendChild(cvs);
    document.body.appendChild(popup);

    const left = Math.min(rect.left, window.innerWidth - 280);
    const top = rect.bottom + 4;
    popup.style.left = left + 'px';
    popup.style.top = top + 'px';

    const ctx = cvs.getContext('2d');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hist.map(h => h.date),
            datasets: [{
                data: hist.map(h => h.value),
                borderColor: '#D4A843',
                backgroundColor: 'rgba(212,168,67,0.08)',
                borderWidth: 1.5,
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                pointHoverRadius: 3,
            }],
        },
        options: {
            responsive: false,
            animation: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => fmt(ctx.parsed.y) } },
            },
            scales: {
                x: { ticks: { color: '#5A5270', font: { size: 8 }, maxTicksLimit: 4 }, grid: { display: false } },
                y: { ticks: { color: '#5A5270', font: { size: 8 }, callback: (v) => fmt(v) }, grid: { color: 'rgba(30,28,56,0.3)' } },
            },
        },
    });

    return { popup, chart };
}

function fmtForMarket(key) {
    const map = {
        ihsg: 'number', lq45: 'number',
        usdidr: 'currency-idr', dxy: 'decimal',
        brent: 'currency-usd', gold: 'currency-usd',
        cpo: 'number',
    };
    return map[key] || 'decimal';
}

function fmtForIndicator(unit, name) {
    if (!unit) return 'decimal';
    if (unit === '%') {
        if (name && (name.includes('BI') || name.includes('Rate') || name.includes('Deposit') || name.includes('Lending') || name.includes('Inflation') || name.includes('GDP') || name.includes('Growth'))) return 'pct';
        return 'pct-1dp';
    }
    if (unit.includes('bps')) return 'bps';
    if (unit.includes('trillion') || unit.includes('IDR')) return 'currency-idr';
    if (unit.includes('USD')) return 'currency-usd';
    return 'decimal';
}

function escAttr(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function setupPopupCharts(container) {
    container.querySelectorAll('.indicator-item.clickable').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            const existing = document.querySelector('.indicator-popup-chart');
            if (existing) {
                existing.remove();
                if (existing._chart) existing._chart.destroy();
                if (existing._source === el) return;
            }
            const result = makePopupChart(el);
            if (!result) return;
            result.popup._chart = result.chart;
            result.popup._source = el;
        });
    });
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePopup();
});

async function loadMarket() {
    const data = await apiGet('/market/summary');
    if (!data) return;
    document.getElementById('marketSummary').innerHTML = `
        <div class="indicator-grid">
            ${Object.entries(data).filter(([k]) => k !== 'updated_at' && k !== 'status').map(([key, val]) => {
                const hasHistory = val.history && val.history.length > 1;
                const histJson = hasHistory ? escAttr(JSON.stringify(val.history)) : '';
                const fmt = fmtForMarket(key);
                return `
                    <div class="indicator-item${hasHistory ? ' clickable' : ''}" data-history='${histJson}' data-fmt="${fmt}">
                        <div class="ind-name">${key.toUpperCase()}</div>
                        <div class="ind-value">${typeof val === 'object' ? val.last.toLocaleString() : val}</div>
                        <div class="ind-change ${typeof val === 'object' && val.change_pct >= 0 ? 'up' : 'down'}">
                            ${typeof val === 'object' ? `${val.change_pct > 0 ? '+' : ''}${val.change_pct.toFixed(2)}%` : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        <div style="margin-top: 0.5rem; font-size: 0.7rem; color: var(--text-muted);">
            Status: ${data.status} | Updated: ${data.updated_at}
        </div>
    `;

    setupPopupCharts(document.getElementById('marketSummary'));
}

// === News Feed ===
async function loadNews() {
    const source = document.getElementById('newsSourceFilter').value;
    const language = document.getElementById('newsLanguageFilter').value;
    let url = '/news/?limit=20';
    if (source) url += `&source=${encodeURIComponent(source)}`;
    if (language) url += `&language=${encodeURIComponent(language)}`;

    const [articles, sentiment, history] = await Promise.all([
        apiGet(url),
        apiGet('/news/sentiment'),
        apiGet('/news/sentiment/history?days=14'),
    ]);
    const feed = document.getElementById('newsFeed');

    // Sentiment bar + history
    let sentHtml = '';
    if (sentiment && sentiment.total > 0) {
        const pPos = sentiment.pct_positive;
        const pNeu = sentiment.pct_neutral;
        const pNeg = sentiment.pct_negative;
        const label = sentiment.score > 0.1 ? 'Bullish' : sentiment.score < -0.1 ? 'Bearish' : 'Neutral';

        let histSpark = '';
        if (history && history.length > 1) {
            const scores = history.map(h => h.score);
            const maxR = Math.max(...scores);
            const minR = Math.min(...scores);
            const rangeR = (maxR - minR) || 1;
            const w = 200, h2 = 28;
            const pts = scores.map((s, i) => {
                const x = (i / (scores.length - 1)) * w;
                const y = h2 - ((s - minR) / rangeR) * (h2 - 4) - 2;
                return `${x},${y}`;
            }).join(' ');
            histSpark = `
                <svg viewBox="0 0 ${w} ${h2}" style="width:100%;height:28px;margin-top:4px;">
                    <polyline points="${pts}" fill="none" stroke="var(--positive)" stroke-width="1.5"/>
                    ${history.map((h, i) => {
                        const x = (i / (scores.length - 1)) * w;
                        const y = h2 - ((h.score - minR) / rangeR) * (h2 - 4) - 2;
                        const color = h.score > 0.1 ? 'var(--positive)' : h.score < -0.1 ? 'var(--negative)' : 'var(--neutral)';
                        return `<circle cx="${x}" cy="${y}" r="1.5" fill="${color}"/>`;
                    }).join('')}
                </svg>
            `;
        }

        sentHtml = `
            <div class="sentiment-summary">
                <div class="sentiment-bar">
                    <div class="sent-bar-positive" style="width:${pPos}%"></div>
                    <div class="sent-bar-neutral" style="width:${pNeu}%"></div>
                    <div class="sent-bar-negative" style="width:${pNeg}%"></div>
                </div>
                <div class="sentiment-labels">
                    <span class="sent-up">${pPos}%</span>
                    <span class="sent-label">${label} · ${sentiment.total} articles · ${sentiment.date}</span>
                    <span class="sent-down">${pNeg}%</span>
                </div>
                ${histSpark}
                <div style="font-size:0.6rem;color:var(--text-muted);text-align:center;margin-top:2px;">Sentiment trend (last ${history.length} days)</div>
            </div>
        `;
    }

    if (!articles || articles.length === 0) {
        feed.innerHTML = sentHtml + '<div class="loading">No news articles. Click "Seed Sample" to add demo data.</div>';
        return;
    }

    feed.innerHTML = sentHtml + articles.map(a => {
        const sent = a.sentiment != null ? a.sentiment : 0;
        const sentiment = sent > 0.1 ? 'positive' : sent < -0.1 ? 'negative' : 'neutral';
        const timeAgo = a.published_at ? timeSince(new Date(a.published_at)) : '';
        const summary = a.summary && a.summary !== a.title ? a.summary : '';
        return `
            <div class="news-card sentiment-${sentiment}">
                <div class="news-source">${a.source || 'Unknown'} · ${timeAgo}</div>
                <div class="news-title">${escapeHtml(a.title)}</div>
                ${summary ? `<div class="news-summary">${escapeHtml(summary)}</div>` : ''}
                <div class="news-meta">
                    <span>${a.language === 'id' ? '🇮🇩' : '🇬🇧'} ${a.language.toUpperCase()}</span>
                    <span>Sentiment: ${sent.toFixed(2)}</span>
                </div>
                ${a.tags && a.tags.length ? `
                    <div class="news-tags">
                        ${a.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                    </div>
                ` : ''}
                ${a.ticker_mentions && a.ticker_mentions.length ? `
                    <div class="news-tags">
                        ${a.ticker_mentions.map(t => `<span class="tag" style="background: var(--accent-red); color: white;">${t}</span>`).join('')}
                    </div>
                ` : ''}
                <a href="${escapeHtml(a.url)}" target="_blank" class="news-readmore">Read full article →</a>
            </div>
        `;
    }).join('');
}

function timeSince(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
}

async function seedNews() {
    const result = await apiPost('/news/seed');
    if (result) {
        loadNews();
        updateStatus('Sample news seeded');
    }
}

// === Indicators ===
async function loadIndicators() {
    const data = await apiGet('/indicators/macro');
    if (!data) return;

    const container = document.getElementById('indicatorsContent');
    const categoryLabels = {
        monetary_policy: 'Monetary Policy',
        inflation: 'Inflation',
        growth: 'Growth',
        external_sector: 'External Sector',
        banking: 'Banking',
        fiscal: 'Fiscal',
    };

    function esc(s) {
        if (!s) return '';
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
    }

    let html = '';
    for (const [key, indicators] of Object.entries(data)) {
        if (key === 'updated_at' || key === 'status' || key === 'source' || key === 'bi_rate_history') continue;
        if (!Array.isArray(indicators)) continue;
        html += `
            <div class="indicator-category">
                <h3>${categoryLabels[key] || key}</h3>
                <div class="indicator-grid">
                    ${indicators.map(i => {
                        const hasHistory = i.history && i.history.length > 1;
                        const histJson = hasHistory ? esc(JSON.stringify(i.history)) : '';
                        const fmt = fmtForIndicator(i.unit, i.name);
                        return `
                            <div class="indicator-item${hasHistory ? ' clickable' : ''}" data-history='${histJson}' data-fmt="${fmt}">
                                <div class="ind-name">${i.name}</div>
                                <div class="ind-value">${i.value} ${i.unit || ''}</div>
                                <div class="ind-change ${i.change > 0 ? 'up' : i.change < 0 ? 'down' : ''}">
                                    ${i.change > 0 ? '+' : ''}${i.change} ${i.previous ? `(prev: ${i.previous})` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }
    html += `<div style="font-size: 0.7rem; color: var(--text-muted);">Updated: ${esc(data.updated_at)} | Status: ${esc(data.status)}</div>`;
    container.innerHTML = html;

    setupPopupCharts(container);
}

// === Bonds ===
async function loadBonds() {
    const curve = await apiGet('/bonds/yield-curve');
    const benchmarks = await apiGet('/bonds/benchmarks');
    const cds = await apiGet('/bonds/cds');

    if (curve) {
        const canvas = document.getElementById('yieldCurveChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (charts.yieldCurve) charts.yieldCurve.destroy();
            charts.yieldCurve = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: curve.tenors,
                    datasets: [
                        { label: 'Current', data: curve.yields, borderColor: '#00FF88', tension: 0.3, fill: false },
                        { label: 'Previous', data: curve.previous_yields, borderColor: '#8899AA', tension: 0.3, fill: false, borderDash: [5, 5] },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#8899AA' } } },
                    scales: {
                        x: { ticks: { color: '#8899AA' }, grid: { color: '#2A2A3E' } },
                        y: { ticks: { color: '#8899AA' }, grid: { color: '#2A2A3E' } },
                    },
                },
            });
        }
    }

    if (benchmarks && benchmarks.bonds) {
        document.getElementById('bondsBody').innerHTML = benchmarks.bonds.map(b => `
            <tr>
                <td>${b.name}</td>
                <td>${b.tenor}</td>
                <td>${b.coupon}%</td>
                <td>${b.ytm}%</td>
                <td>${b.price}</td>
                <td class="${b.change >= 0 ? 'up' : 'down'}">${b.change > 0 ? '+' : ''}${b.change}</td>
            </tr>
        `).join('');
    }

    if (cds) {
        document.getElementById('cdsDisplay').innerHTML = `
            <div style="display: flex; gap: 2rem; align-items: center;">
                <div>
                    <div style="font-size: 2rem; font-family: var(--font-mono); font-weight: 700;">${cds.indonesia_5y}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">bps</div>
                    <div style="font-size: 0.8rem;" class="${cds.change > 0 ? 'up' : 'down'}">${cds.change > 0 ? '+' : ''}${cds.change}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Regional Comparison:</div>
                    ${cds.comparison.map(c => `
                        <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
                            <span style="color: var(--text-secondary);">${c.country}</span>
                            <span style="font-family: var(--font-mono);">${c.cds} bps</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// === FX ===
async function loadFX() {
    const rates = await apiGet('/fx/rates');
    const jisdor = await apiGet('/fx/jisdor');

    if (rates && rates.pairs) {
        document.getElementById('fxBody').innerHTML = rates.pairs.map(p => `
            <tr>
                <td><strong>${p.pair}</strong></td>
                <td>${p.bid.toLocaleString()}</td>
                <td>${p.ask.toLocaleString()}</td>
                <td>${p.mid.toLocaleString()}</td>
                <td class="${p.change >= 0 ? 'up' : 'down'}">${p.change > 0 ? '+' : ''}${p.change.toLocaleString()}</td>
                <td class="${p.change_pct >= 0 ? 'up' : 'down'}">${p.change_pct > 0 ? '+' : ''}${p.change_pct.toFixed(2)}%</td>
            </tr>
        `).join('');
    }

    if (jisdor) {
        document.getElementById('jisdorDisplay').innerHTML = `
            <div class="indicator-grid">
                <div class="indicator-item">
                    <div class="ind-name">BI JISDOR Rate</div>
                    <div class="ind-value">${jisdor.rate.toLocaleString()}</div>
                    <div class="ind-change ${jisdor.change > 0 ? 'down' : 'up'}">${jisdor.change > 0 ? '+' : ''}${jisdor.change}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">Previous Rate</div>
                    <div class="ind-value">${jisdor.previous_rate.toLocaleString()}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">30D High</div>
                    <div class="ind-value">${jisdor.historical_30d_high.toLocaleString()}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">30D Low</div>
                    <div class="ind-value">${jisdor.historical_30d_low.toLocaleString()}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">200-day MA</div>
                    <div class="ind-value">${jisdor.ma_200.toLocaleString()}</div>
                </div>
            </div>
        `;
    }
}

// === Portfolio ===
async function loadPortfolio() {
    const data = await apiGet('/portfolio/demo');
    if (!data) return;

    const p = data.portfolio;
    const totalPnlClass = p.total_pnl >= 0 ? 'up' : 'down';
    document.getElementById('portfolioContent').innerHTML = `
        <div class="card">
            <div class="card-title">${p.name}</div>
            <div class="indicator-grid">
                <div class="indicator-item">
                    <div class="ind-name">Total Value</div>
                    <div class="ind-value">Rp ${p.total_value.toLocaleString()}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">Total Cost</div>
                    <div class="ind-value">Rp ${p.total_cost.toLocaleString()}</div>
                </div>
                <div class="indicator-item">
                    <div class="ind-name">Total P&L</div>
                    <div class="ind-value ${totalPnlClass}">Rp ${p.total_pnl.toLocaleString()}</div>
                    <div class="ind-change ${totalPnlClass}">${p.total_pnl_pct > 0 ? '+' : ''}${p.total_pnl_pct.toFixed(2)}%</div>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-title">Holdings</div>
            <table class="data-table">
                <thead><tr><th>Ticker</th><th>Qty</th><th>Avg Price</th><th>Last Price</th><th>P&L%</th><th>Weight</th></tr></thead>
                <tbody>
                    ${data.holdings.map(h => `
                        <tr>
                            <td><strong>${h.ticker}</strong></td>
                            <td>${h.quantity.toLocaleString()}</td>
                            <td>Rp ${h.avg_price.toLocaleString()}</td>
                            <td>Rp ${h.last_price.toLocaleString()}</td>
                            <td class="${h.pnl_pct >= 0 ? 'up' : 'down'}">${h.pnl_pct > 0 ? '+' : ''}${h.pnl_pct.toFixed(2)}%</td>
                            <td>${h.weight.toFixed(2)}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// === AI Analyst ===
async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const container = document.getElementById('chatMessages');
    container.innerHTML += `
        <div class="message user">
            <div class="msg-sender">You</div>
            <div class="msg-text">${escapeHtml(message)}</div>
        </div>
    `;
    input.value = '';
    container.scrollTop = container.scrollHeight;

    const sendBtn = document.getElementById('chatSendBtn');
    sendBtn.disabled = true;
    sendBtn.textContent = '...';

    const msgId = 'ai-msg-' + Date.now();
    container.innerHTML += `
        <div class="message ai" id="${msgId}">
            <div class="msg-sender">PRISM AI</div>
            <div class="msg-text processing">Analyzing market data...</div>
        </div>
    `;
    container.scrollTop = container.scrollHeight;

    const textDiv = document.querySelector(`#${msgId} .msg-text`);
    let buffer = '';

    try {
        const res = await fetch(`${API_BASE}/ai/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        if (!res.body) throw new Error('No response body');

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let pending = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            pending += decoder.decode(value, { stream: true });
            const lines = pending.split('\n');
            pending = lines.pop() || '';

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(trimmed.slice(6));
                    if (data.token) {
                        if (textDiv.classList.contains('processing')) {
                            textDiv.classList.remove('processing');
                            textDiv.innerHTML = '';
                        }
                        buffer += data.token;
                        textDiv.innerHTML = marked.parse(buffer);
                        container.scrollTop = container.scrollHeight;
                    } else if (data.done) {
                        if (textDiv.classList.contains('processing')) {
                            textDiv.classList.remove('processing');
                            textDiv.innerHTML = '';
                        }
                        textDiv.innerHTML = marked.parse(buffer);
                        const sender = document.querySelector(`#${msgId} .msg-sender`);
                        if (sender && data.provider) sender.textContent = `PRISM AI (${data.provider})`;
                    } else if (data.error) {
                        textDiv.classList.remove('processing');
                        textDiv.innerHTML = `<span class="error">Error: ${escapeHtml(data.error)}</span>`;
                    }
                } catch (e) {
                    console.warn('SSE parse error:', e);
                }
            }
        }
    } catch (e) {
        textDiv.classList.remove('processing');
        textDiv.innerHTML = `<span class="error">Connection error: ${escapeHtml(e.message)}</span>`;
    }

    container.scrollTop = container.scrollHeight;
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
}

document.getElementById('chatInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChat();
    }
});

// === Alerts ===
async function loadAlerts() {
    const alerts = await apiGet('/alerts/');
    const container = document.getElementById('alertsList');
    if (!alerts || alerts.length === 0) {
        container.innerHTML = 'No alerts configured.';
        return;
    }
    container.innerHTML = alerts.map(a => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; border-bottom: 1px solid var(--border);">
            <div>
                <strong>${a.type.toUpperCase()}</strong>
                ${a.symbol ? `· ${a.symbol}` : ''}
                ${a.condition ? `· ${a.condition} ${a.threshold}` : ''}
                ${a.keyword ? `· "${a.keyword}"` : ''}
            </div>
            <button class="btn btn-sm" onclick="deleteAlert(${a.id})">Delete</button>
        </div>
    `).join('');
}

async function createAlert() {
    const symbol = document.getElementById('alertSymbol').value.trim();
    const type = document.getElementById('alertType').value;
    const condition = document.getElementById('alertCondition').value.trim();
    const threshold = parseFloat(document.getElementById('alertThreshold').value);

    const body = { alert_type: type };
    if (symbol) body.symbol = symbol;
    if (condition) body.condition = condition;
    if (!isNaN(threshold)) body.threshold = threshold;

    const result = await apiPost('/alerts/', body);
    if (result) {
        document.getElementById('alertSymbol').value = '';
        document.getElementById('alertCondition').value = '';
        document.getElementById('alertThreshold').value = '';
        loadAlerts();
        updateStatus(`Alert created: ${type}`);
    }
}

async function deleteAlert(id) {
    try {
        const res = await fetch(`${API_BASE}/alerts/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadAlerts();
            updateStatus('Alert deleted');
        }
    } catch (e) {
        console.error('Delete failed:', e);
    }
}

// === About / Health ===
async function checkHealth() {
    try {
        const health = await fetch('/health').then(r => r.json());
        const el = document.getElementById('healthStatus');
        el.textContent = health.status;
        el.className = 'status-badge live';
    } catch {
        const el = document.getElementById('healthStatus');
        el.textContent = 'unreachable';
        el.className = 'status-badge live';
        el.style.background = 'rgba(255,51,102,0.1)';
        el.style.color = 'var(--coral)';
        el.style.borderColor = 'rgba(255,51,102,0.2)';
    }

    try {
        const ready = await fetch('/ready').then(r => r.json());
        const el = document.getElementById('dbStatus');
        el.textContent = ready.database;
        el.className = ready.status === 'ready' ? 'status-badge live' : 'status-badge simulated';
    } catch {
        const el = document.getElementById('dbStatus');
        el.textContent = 'unreachable';
        el.className = 'status-badge live';
        el.style.background = 'rgba(255,51,102,0.1)';
        el.style.color = 'var(--coral)';
        el.style.borderColor = 'rgba(255,51,102,0.2)';
    }
}

// === Status Bar ===
function updateStatus(msg) {
    document.getElementById('statusText').textContent = msg;
    setTimeout(() => { document.getElementById('statusText').textContent = 'System Ready'; }, 3000);
}

// === Refresh All ===
async function refreshAll() {
    updateStatus('Refreshing all modules...');
    await Promise.all([
        loadDashboard(),
        loadMarket(),
        loadNews(),
        loadIndicators(),
        loadBonds(),
        loadFX(),
        loadPortfolio(),
        loadTickers(),
        loadAlerts(),
    ]);
    updateStatus('All modules refreshed');
}

// === Ticker Data ===
async function loadTickers() {
    const tickers = await apiGet('/tickers/');
    const body = document.getElementById('tickersBody');
    if (!tickers || tickers.length === 0) {
        body.innerHTML = '<tr><td colspan="8" class="loading">No ticker data. Click "Seed Data" to add initial tickers.</td></tr>';
        return;
    }
    body.innerHTML = tickers.map(t => {
        const timeStr = t.updated_at ? new Date(t.updated_at).toLocaleTimeString('en-ID', { timeZone: 'Asia/Jakarta' }) : '-';
        const changeClass = t.change >= 0 ? 'up' : 'down';
        return `
            <tr>
                <td><strong>${escapeHtml(t.symbol)}</strong></td>
                <td>${escapeHtml(t.type)}</td>
                <td>${t.last_price.toLocaleString()}</td>
                <td class="${changeClass}">${t.change >= 0 ? '+' : ''}${t.change.toFixed(2)}</td>
                <td class="${changeClass}">${t.change_pct >= 0 ? '+' : ''}${t.change_pct.toFixed(2)}%</td>
                <td>${t.volume ? t.volume.toLocaleString() : '-'}</td>
                <td style="font-size:0.75rem; color: var(--text-muted);">${timeStr}</td>
                <td><button class="btn btn-sm" onclick="deleteTicker('${escapeHtml(t.symbol)}')" style="color: var(--negative);">Delete</button></td>
            </tr>
        `;
    }).join('');
}

async function addTicker() {
    const symbol = document.getElementById('tickerSymbol').value.trim();
    const type = document.getElementById('tickerType').value;
    const price = parseFloat(document.getElementById('tickerPrice').value);
    const change = parseFloat(document.getElementById('tickerChange').value) || 0;
    if (!symbol || isNaN(price)) {
        updateStatus('Please enter symbol and price');
        return;
    }
    const changePct = price !== 0 ? (change / (price - change)) * 100 : 0;
    const body = {
        symbol: symbol,
        snapshot_type: type,
        last_price: price,
        change: change,
        change_pct: Math.round(changePct * 100) / 100,
    };
    const result = await apiPost('/tickers/', body);
    if (result) {
        document.getElementById('tickerSymbol').value = '';
        document.getElementById('tickerPrice').value = '';
        document.getElementById('tickerChange').value = '';
        await loadTickers();
        updateStatus(`Ticker ${symbol} updated`);
    }
}

async function deleteTicker(symbol) {
    try {
        const res = await fetch(`${API_BASE}/tickers/${encodeURIComponent(symbol)}`, { method: 'DELETE' });
        if (res.ok) {
            await loadTickers();
            updateStatus(`Ticker ${symbol} deleted`);
        } else {
            updateStatus(`Failed to delete ${symbol}`);
        }
    } catch (e) {
        console.error('Delete ticker failed:', e);
    }
}

async function refreshTickers() {
    updateStatus('Refreshing ticker prices...');
    const result = await apiPost('/tickers/refresh');
    if (result) {
        await loadTickers();
        updateStatus(`Refreshed ${result.count} tickers`);
    } else {
        updateStatus('Refresh failed');
    }
}

async function seedTickers() {
    updateStatus('Seeding ticker data...');
    const result = await apiPost('/tickers/seed');
    if (result) {
        await loadTickers();
        updateStatus(`Seeded ${result.count} tickers`);
    }
}

// === Utility ===
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// === Init ===
async function init() {
    updateStatus('Loading PRISM Terminal...');
    await Promise.all([
        loadDashboard(),
        loadMarket(),
        loadNews(),
        loadIndicators(),
        loadBonds(),
        loadFX(),
        loadPortfolio(),
        loadTickers(),
        loadAlerts(),
        checkHealth(),
    ]);
    updateStatus('System Ready');

    // Auto-refresh every 60 seconds
    setInterval(refreshAll, 60000);
}

document.addEventListener('DOMContentLoaded', init);
