// --- Performance Fixes ---
let searchDebounceTimer;
function searchFunds(query) {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => { performSearch(query); }, 300);
}

// Global chart instances
window.chartInstances = {};

function showLoading(elementId, message = 'Loading...') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; gap: 14px;">
            <div style="width: 36px; height: 36px; border-radius: 50%; border: 3px solid rgba(0,210,255,0.15); border-top-color: #00D2FF; animation: spin 0.8s linear infinite;"></div>
            <div style="font-size: 13px; color: #4A5568; font-weight: 500;">${message}</div>
        </div>`;
}

// Override original performSearch to update the new left panel too
const originalPerformSearch = performSearch;
performSearch = function(query) {
    // If we're in the builder view, update the left panel
    if (currentView === VIEWS.BUILDER) {
        const cat = document.getElementById('pbCategoryFilter').value;
        const q = (query || document.getElementById('pbSearchInput').value).toLowerCase();
        
        let filtered = allFunds.filter(f => 
            (cat === 'All' || f.category === cat) &&
            (!q || f.name.toLowerCase().includes(q) || f.code.includes(q))
        );
        
        // Virtual scrolling simulation: just show top 100 for now to avoid lag
        filtered = filtered.slice(0, 100);
        
        document.getElementById('pbFundSearchResults').innerHTML = filtered.map(f => `
        <div style="padding: 10px 12px; border-radius: 10px; margin-bottom: 4px; cursor: pointer; border: 1px solid transparent; transition: all 150ms;" onmouseover="this.style.background='#131D2E'; this.style.border='1px solid rgba(255,255,255,0.06)'" onmouseout="this.style.background='transparent'; this.style.border='1px solid transparent'">
            <div style="font-size: 12px; font-weight: 500; color: #94A3B8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 3px;">${f.name}</div>
            <div style="display: flex; gap: 6px; align-items: center;">
                <span style="font-size: 9px; font-weight: 700; background: rgba(139,92,246,0.15); color: #A78BFA; border-radius: 4px; padding: 2px 6px;">${f.category}</span>
                <button onclick="addFundToBuilder('${f.code}', '${f.name.replace(/'/g,"\\'").replace(/"/g,'&quot;')}', '${f.category}')" style="margin-left: auto; background: rgba(0,210,255,0.1); border: 1px solid rgba(0,210,255,0.2); border-radius: 6px; color: #00D2FF; font-size: 10px; font-weight: 700; padding: 3px 8px; cursor: pointer;">+ Add</button>
            </div>
        </div>`).join('');
    } else {
        originalPerformSearch(query); // use original
    }
}

function addFundToBuilder(code, name, category) {
    if(!portfolio.find(p => p.code === code)) {
        portfolio.push({code: code, name: name, category: category, weight: 0});
        autoBalanceWeights();
    }
}

// --- Portfolio Builder View Logic ---
function updateBuilderPreview() {
    const totalAlloc = portfolio.reduce((sum, f) => sum + (parseFloat(f.weight) || 0), 0);
    const totalInv = parseFloat(document.getElementById('pbTotalInvestment').value) || 100000;
    
    document.getElementById('pbTotalAlloc').textContent = totalAlloc.toFixed(1) + '%';
    const bar = document.getElementById('pbAllocBar');
    bar.style.width = Math.min(totalAlloc, 100) + '%';
    
    const status = document.getElementById('pbAllocStatus');
    if(totalAlloc === 100) {
        status.textContent = '✓ 100% Allocated';
        status.style.color = '#34D399';
        status.style.background = 'rgba(52,211,153,0.1)';
    } else if(totalAlloc > 100) {
        status.textContent = '⚠️ Over Allocated';
        status.style.color = '#F87171';
        status.style.background = 'rgba(248,113,113,0.1)';
    } else {
        status.textContent = `⚠️ Add ${Math.max(0, 100 - totalAlloc).toFixed(1)}% more`;
        status.style.color = '#F59E0B';
        status.style.background = 'rgba(245,158,11,0.1)';
    }
    
    const container = document.getElementById('pbFundsListContainer');
    const emptyState = document.getElementById('pbEmptyState');
    
    if(portfolio.length === 0) {
        container.innerHTML = '';
        emptyState.style.display = 'block';
    } else {
        emptyState.style.display = 'none';
        const colors = ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'];
        
        container.innerHTML = portfolio.map((fund, i) => {
            const color = colors[i % colors.length];
            const amt = totalInv * (parseFloat(fund.weight) || 0) / 100;
            return `
            <div style="display: grid; grid-template-columns: 2fr 80px 140px 100px 80px; padding: 14px 20px; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: center; transition: background 150ms;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, ${color}40, ${color}20); border: 1px solid ${color}40; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;">💼</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 600; color: #E2E8F0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 220px;">${fund.name}</div>
                        <div style="display: flex; gap: 6px; margin-top: 3px;">
                            <span style="font-size: 9px; font-weight: 700; background: ${color}20; color: ${color}; border-radius: 4px; padding: 1px 6px;">${fund.category}</span>
                            <span style="font-size: 10px; color: #4A5568;">Code: ${fund.code}</span>
                        </div>
                    </div>
                </div>
                <div>
                    <input type="number" min="0" max="100" step="0.5" value="${fund.weight}" onchange="updateWeight(${i}, this.value)" style="width: 60px; background: rgba(255,255,255,0.04); border: 1px solid ${color}40; border-radius: 8px; padding: 6px 8px; font-size: 13px; font-weight: 700; color: ${color}; text-align: center; outline: none;" />
                    <span style="color: ${color}; font-size: 12px; font-weight: 700; margin-left: 2px;">%</span>
                </div>
                <input type="range" min="0" max="100" step="0.5" value="${fund.weight}" oninput="updateWeight(${i}, this.value)" style="width: 100%; accent-color: ${color};" />
                <div style="font-size: 12px; font-weight: 600; color: ${color};">₹${Math.round(amt).toLocaleString('en-IN')}</div>
                <button onclick="removeFund(${i})" style="background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.15); border-radius: 8px; color: #F87171; padding: 6px 10px; cursor: pointer; font-size: 11px; font-weight: 600;">Remove</button>
            </div>`;
        }).join('');
    }
    
    // Quick Buttons
    const amts = [10000, 25000, 50000, 100000, 500000];
    document.getElementById('pbAmountButtons').innerHTML = amts.map(amt => `<button onclick="setInvestmentAmount(${amt})" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 12px; color: #64748B; font-size: 11px; font-weight: 500; cursor: pointer; transition: all 150ms;" onmouseover="this.style.background='rgba(0,210,255,0.08)'; this.style.color='#00D2FF'" onmouseout="this.style.background='rgba(255,255,255,0.04)'; this.style.color='#64748B'">₹${amt/1000}K</button>`).join('');
    
    // Donut Chart
    document.getElementById('pbDonutCenter').innerHTML = `${portfolio.length}<br/>Funds`;
    const ctx = document.getElementById('pbDonutPreview').getContext('2d');
    if(window.chartInstances['pbDonut']) window.chartInstances['pbDonut'].destroy();
    
    window.chartInstances['pbDonut'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: portfolio.map(p => p.name.substring(0, 15) + '...'),
            datasets: [{
                data: portfolio.map(p => p.weight),
                backgroundColor: ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '75%', animation: { duration: 600, easing: 'easeOutQuart' },
            plugins: { legend: { display: false }, tooltip: { backgroundColor: '#131D2E', bodyColor: '#E2E8F0' } }
        }
    });
    
    document.getElementById('pbDonutLegend').innerHTML = portfolio.map((p, i) => {
        const c = ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'][i % 7];
        return `<div style="display:flex; justify-content:space-between; font-size:10px;"><span style="display:flex; align-items:center; gap:6px; color:#94A3B8;"><div style="width:8px; height:8px; border-radius:50%; background:${c}"></div>${p.name.substring(0, 20)}...</span><span style="color:white; font-weight:600;">${p.weight}%</span></div>`;
    }).join('');
    
    // Quick Stats
    let eq = 0, dt = 0;
    portfolio.forEach(p => { if(p.category==='Equity') eq+=p.weight; else if(p.category==='Debt') dt+=p.weight; });
    
    document.getElementById('pbQuickStats').innerHTML = [
        { label: 'Total Funds', value: portfolio.length, color: '#00D2FF' },
        { label: 'Total Investment', value: '₹' + totalInv.toLocaleString('en-IN'), color: '#34D399' },
        { label: 'Equity Allocation', value: eq.toFixed(1) + '%', color: '#8B5CF6' },
        { label: 'Debt Allocation', value: dt.toFixed(1) + '%', color: '#3B82F6' }
    ].map(stat => `<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);"><span style="font-size: 11px; color: #4A5568;">${stat.label}</span><span style="font-size: 11px; font-weight: 700; color: ${stat.color};">${stat.value}</span></div>`).join('');
    
    document.getElementById('headerPortfolioCount').textContent = portfolio.length;
}

function updateWeight(idx, val) {
    if(portfolio[idx]) portfolio[idx].weight = parseFloat(val) || 0;
    updateBuilderPreview();
}
function setInvestmentAmount(amt) {
    document.getElementById('pbTotalInvestment').value = amt;
    updateBuilderPreview();
}
function updateAllAmounts() { updateBuilderPreview(); }
function autoBalanceWeights() {
    if(portfolio.length === 0) return;
    const w = parseFloat((100 / portfolio.length).toFixed(1));
    portfolio.forEach((p, i) => { p.weight = (i === portfolio.length-1) ? parseFloat((100 - w*(portfolio.length-1)).toFixed(1)) : w; });
    updateBuilderPreview();
}
function removeFund(idx) {
    portfolio.splice(idx, 1);
    updateBuilderPreview();
}

async function analyzeAndShow() {
    if (portfolio.length === 0) {
        alert("Please add at least one fund to analyze.");
        return;
    }
    
    const totalAlloc = portfolio.reduce((sum, f) => sum + (parseFloat(f.weight) || 0), 0);
    if (Math.abs(totalAlloc - 100) > 0.1) {
        alert("Total allocation must equal exactly 100%. Please auto-balance or adjust weights.");
        return;
    }

    try {
        const res = await fetch('/api/portfolio/analyze', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(portfolio)
        });
        
        if (!res.ok) throw new Error('Analysis failed');
        
        const result = await res.json();
        const analysisData = {
            portfolio: portfolio,
            totalInvestment: parseFloat(document.getElementById('pbTotalInvestment').value) || 100000,
            results: result,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('mf_portfolio_analysis', JSON.stringify(analysisData));
        localStorage.setItem('mf_portfolio', JSON.stringify([]));
        portfolio = [];
        updateBuilderPreview();
        
        renderSavedPortfolioView(analysisData);
        switchView(VIEWS.SAVED);
        
    } catch (error) {
        alert(`Analysis Error: ${error.message}`);
    }
}

function renderSavedPortfolioView(data) {
    const pf = data.portfolio;
    const inv = data.totalInvestment;
    const res = data.results;
    
    document.getElementById('savedPortfolioTitle').textContent = 'My Custom Portfolio';
    document.getElementById('savedTotalInv').textContent = '₹' + inv.toLocaleString('en-IN');
    document.getElementById('savedFundCount').textContent = pf.length;
    
    // Calculate aggregate CAGRs (Weighted)
    let c1=0, c3=0, c5=0;
    res.forEach(f => {
        const w = (f.allocation || 0); // it's 0-1
        if(f.cagr_1y !== null) c1 += parseFloat(f.cagr_1y) * w;
        if(f.cagr_3y !== null) c3 += parseFloat(f.cagr_3y) * w;
        if(f.cagr_5y !== null) c5 += parseFloat(f.cagr_5y) * w;
    });
    
    document.getElementById('saved1Y').textContent = c1 ? (c1 > 0 ? '+' : '') + c1.toFixed(2) + '%' : '—';
    document.getElementById('saved3Y').textContent = c3 ? (c3 > 0 ? '+' : '') + c3.toFixed(2) + '%' : '—';
    document.getElementById('saved5Y').textContent = c5 ? (c5 > 0 ? '+' : '') + c5.toFixed(2) + '%' : '—';
    
    // Donut
    const ctx = document.getElementById('savedDonutChart').getContext('2d');
    if(window.chartInstances['savedDonut']) window.chartInstances['savedDonut'].destroy();
    
    window.chartInstances['savedDonut'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: pf.map(p => p.name.substring(0, 15) + '...'),
            datasets: [{
                data: pf.map(p => p.weight),
                backgroundColor: ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '75%', animation: { duration: 600, easing: 'easeOutQuart' },
            plugins: { legend: { display: false }, tooltip: { backgroundColor: '#131D2E', bodyColor: '#E2E8F0' } }
        }
    });
    
    document.getElementById('savedDonutLegend').innerHTML = pf.map((p, i) => {
        const c = ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'][i % 7];
        return `<div style="display:flex; justify-content:space-between; font-size:12px;"><span style="display:flex; align-items:center; gap:6px; color:#94A3B8;"><div style="width:8px; height:8px; border-radius:50%; background:${c}"></div>${p.name.substring(0, 20)}...</span><span style="color:white; font-weight:600;">${p.weight}%</span></div>`;
    }).join('');
    
    // Category Breakdown
    const catMap = {};
    pf.forEach(p => { catMap[p.category || 'Other'] = (catMap[p.category || 'Other'] || 0) + p.weight; });
    document.getElementById('savedFundBreakdown').innerHTML = Object.keys(catMap).map(k => `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 8px;">
            <span style="font-size: 12px; color: #E2E8F0; font-weight: 600;">${k}</span>
            <span style="font-size: 12px; color: #00D2FF; font-weight: 700;">${catMap[k].toFixed(1)}%</span>
        </div>
    `).join('');
    
    // Table
    const colors = ['#00D2FF', '#8B5CF6', '#34D399', '#F59E0B', '#F87171', '#3B82F6', '#EC4899'];
    document.getElementById('savedFundsTableBody').innerHTML = res.map((r, i) => {
        const c = colors[i % 7];
        return `
        <div style="display: grid; grid-template-columns: 2fr 80px 1fr 1fr 1fr 1fr; padding: 14px 22px; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: center;">
            <div style="display: flex; gap: 10px; align-items: center;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: ${c}20; border: 1px solid ${c}40; display: flex; align-items: center; justify-content: center; font-size: 13px;">📈</div>
                <div>
                    <div style="font-size: 12px; font-weight: 600; color: #E2E8F0;">${r.name.substring(0,35)}...</div>
                    <div style="font-size: 10px; color: #4A5568;">Code: ${r.code}</div>
                </div>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: ${c};">${(r.allocation*100).toFixed(1)}%</div>
            ${['cagr_1y','cagr_3y','cagr_5y'].map(key => `<div style="font-size: 12px; font-weight: 700; color: ${r[key] >= 0 ? '#34D399' : '#F87171'};">${r[key] !== null ? (r[key] >= 0 ? '+' : '') + r[key] + '%' : '—'}</div>`).join('')}
            <div style="font-size: 12px; font-weight: 600; color: #00D2FF;">₹${Math.round(inv * r.allocation).toLocaleString('en-IN')}</div>
        </div>`;
    }).join('');
    
    document.getElementById('savedChartSubtitle').textContent = `${pf.length} funds • Weighted aggregated NAV`;
}
function exportPortfolioPDF() { alert("Exporting report as PDF... (To be implemented)"); }
