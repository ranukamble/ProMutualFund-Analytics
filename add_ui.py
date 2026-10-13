import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. HTML Insertion
new_html = """
          <!-- ── NEW SECTION 1: SIP PROJECTION CALCULATOR ── -->
          <div style="background: #0D1B2A; border: 1px solid rgba(255,255,255,0.07); border-radius: 18px; padding: 20px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
              <div>
                <div style="font-size:14px;font-weight:800; color:#F1F5F9;">💰 SIP Projection Calculator</div>
                <div style="font-size:11px;color:#4A5568;margin-top:2px;">Based on your portfolio's historical CAGR performance</div>
              </div>
              <div style="display: flex; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 3px;">
                <button id="sipToggleBtn" onclick="switchMode('SIP')" style="padding: 6px 16px; border-radius: 8px; border: none; font-size: 11px; font-weight: 700; cursor: pointer; background: linear-gradient(135deg,#8B5CF6,#6D28D9); color: white; transition: all 200ms;">SIP</button>
                <button id="lumpToggleBtn" onclick="switchMode('LUMP')" style="padding: 6px 16px; border-radius: 8px; border: none; font-size: 11px; font-weight: 700; cursor: pointer; background: transparent; color: #4A5568; transition: all 200ms;">Lump Sum</button>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px;">
              <div>
                <label id="sipAmountLabel" style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Monthly SIP (₹)</label>
                <input id="sipAmount" type="number" value="5000" oninput="calculateProjection()" style="width:100%;box-sizing:border-box; background:#131D2E; border:1px solid rgba(139,92,246,0.3); border-radius:10px;padding:10px 12px; font-size:14px;font-weight:700; color:#A78BFA;outline:none;" />
              </div>
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Time Period (Years)</label>
                <input id="sipYears" type="range" min="1" max="40" value="10" oninput="document.getElementById('sipYearsDisplay').textContent = this.value + ' yrs'; calculateProjection();" style="width:100%;accent-color:#8B5CF6;margin-top:8px;" />
                <div id="sipYearsDisplay" style="font-size:14px;font-weight:800;color:#8B5CF6; text-align:center;margin-top:4px;">10 yrs</div>
              </div>
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Expected CAGR (%)</label>
                <div style="display:flex;gap:4px;flex-wrap:wrap;">
                  ${[8,10,12,15,18].map(r => `<button onclick="document.getElementById('sipRate').value = ${r}; calculateProjection(); document.querySelectorAll('.rateBtn').forEach(b => { b.style.background='rgba(255,255,255,0.04)'; b.style.color='#4A5568'; }); this.style.background='rgba(139,92,246,0.2)'; this.style.color='#A78BFA';" class="rateBtn" style="padding:4px 8px;border-radius:6px; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.04); color:#4A5568;font-size:10px; font-weight:600;cursor:pointer;">${r}%</button>`).join('')}
                  <input id="sipRate" type="number" value="12" min="1" max="50" oninput="calculateProjection()" style="width:48px;background:#131D2E; border:1px solid rgba(139,92,246,0.2); border-radius:6px;padding:3px 6px; font-size:11px;font-weight:700; color:#A78BFA;text-align:center; outline:none;" />
                </div>
              </div>
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Annual Step-Up (%)</label>
                <div style="display:flex;gap:4px;">
                  ${[0,5,10,15].map(s => `<button onclick="document.getElementById('sipStepUp').value=${s}; calculateProjection(); document.querySelectorAll('.stepBtn').forEach(b => { b.style.background='rgba(255,255,255,0.04)'; b.style.color='#4A5568'; }); this.style.background='rgba(0,210,255,0.15)'; this.style.color='#00D2FF';" class="stepBtn" style="padding:4px 10px;border-radius:6px; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.04); color:#4A5568;font-size:10px; font-weight:600;cursor:pointer;">${s}%</button>`).join('')}
                </div>
                <input id="sipStepUp" type="number" value="0" min="0" max="30" oninput="calculateProjection()" style="display:none;" />
              </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; margin-bottom: 18px;">
              ${[
                {id:'projTotalInvested', label:'Total Invested', color:'#00D2FF', icon:'💰'},
                {id:'projFutureValue',   label:'Future Value', color:'#34D399', icon:'📈'},
                {id:'projWealthGain',   label:'Wealth Gain', color:'#A78BFA', icon:'💎'},
                {id:'projAbsReturn',    label:'Absolute Return', color:'#F59E0B', icon:'🎯'},
                {id:'projMonthly',      label:'Monthly Returns', color:'#06B6D4', icon:'📅'}
              ].map(c => `<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px; text-align: center;"><div style="font-size:16px;margin-bottom:6px;">${c.icon}</div><div id="${c.id}" style="font-size:16px;font-weight:900; color:${c.color};letter-spacing:-0.3px; margin-bottom:3px;">—</div><div style="font-size:9px;color:#374151; text-transform:uppercase;letter-spacing:0.06em; font-weight:600;">${c.label}</div></div>`).join('')}
            </div>
            
            <div style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; overflow: hidden;">
              <div class="sipTableHdr" style="display: grid; grid-template-columns: 60px 1fr 1fr 1fr 1fr; padding: 10px 16px; background: rgba(255,255,255,0.03); border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size:9px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;">YEAR</span>
                <span style="font-size:9px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;">INVESTED</span>
                <span style="font-size:9px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;">GAINS</span>
                <span style="font-size:9px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;">TOTAL VALUE</span>
                <span style="font-size:9px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;">RETURN %</span>
              </div>
              <div id="sipYearlyTable" style="max-height: 200px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #1E2D42 transparent;"></div>
            </div>
          </div>

          <!-- ── NEW SECTION 2: ASSUMPTION-BASED SCENARIOS ── -->
          <div style="background: #0D1B2A; border: 1px solid rgba(255,255,255,0.07); border-radius: 18px; padding: 20px; margin-bottom: 16px;">
            <div style="margin-bottom:16px;">
              <div style="font-size:14px;font-weight:800;color:#F1F5F9;">🔮 Return Scenario Analysis</div>
              <div style="font-size:11px;color:#4A5568;margin-top:2px;">How your portfolio performs under different market conditions</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
              ${[
                {label: '🐻 Bear Case', desc: 'Pessimistic scenario', cagr: 6, color: '#F87171', bg: 'rgba(248,113,113,0.08)', border: 'rgba(248,113,113,0.2)'},
                {label: '📊 Base Case', desc: 'Historical average', cagr: 12, color: '#F59E0B', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)'},
                {label: '🐂 Bull Case', desc: 'Optimistic scenario', cagr: 18, color: '#34D399', bg: 'rgba(52,211,153,0.08)', border: 'rgba(52,211,153,0.2)'}
              ].map((sc, idx) => `<div style="background: ${sc.bg}; border: 1px solid ${sc.border}; border-radius: 14px; padding: 18px; position: relative; overflow: hidden;"><div style="font-size:12px;font-weight:800; color:${sc.color};margin-bottom:4px;">${sc.label}</div><div style="font-size:10px;color:#4A5568; margin-bottom:14px;">${sc.desc}</div><div style="display:flex;align-items:center;gap:6px; margin-bottom:14px;"><span style="font-size:11px;color:#4A5568;">Assumed CAGR:</span><input type="number" id="scenarioCagr${idx}" value="${sc.cagr}" min="1" max="50" oninput="calculateScenarios()" style="width:48px;background:rgba(0,0,0,0.3); border:1px solid ${sc.border}; border-radius:6px;padding:3px 6px; font-size:12px;font-weight:700; color:${sc.color};text-align:center; outline:none;" /><span style="color:${sc.color};font-weight:700;">%</span></div>${[5,10,15,20].map(yr => `<div style="display:flex;justify-content:space-between; padding:7px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span style="font-size:11px;color:#4A5568;">${yr} Years</span><span id="sc${idx}yr${yr}" style="font-size:11px;font-weight:700; color:${sc.color};">—</span></div>`).join('')}</div>`).join('')}
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 12px; padding: 16px;">
              <div style="font-size:11px;font-weight:700;color:#64748B; text-transform:uppercase;letter-spacing:0.08em; margin-bottom:12px;">10-Year Projection Comparison</div>
              <canvas id="scenarioBarChart" height="120"></canvas>
            </div>
          </div>

          <!-- ── NEW SECTION 3: GOAL PLANNER ── -->
          <div style="background: #0D1B2A; border: 1px solid rgba(255,255,255,0.07); border-radius: 18px; padding: 20px; margin-bottom: 16px;">
            <div style="margin-bottom:16px;">
              <div style="font-size:14px;font-weight:800;color:#F1F5F9;">🎯 Goal Planner</div>
              <div style="font-size:11px;color:#4A5568;margin-top:2px;">How much SIP needed to reach your financial goal?</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-bottom: 16px;">
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Target Amount (₹)</label>
                <div style="position:relative;">
                  <span style="position:absolute;left:10px;top:50%; transform:translateY(-50%); color:#34D399;font-weight:700;font-size:14px;">₹</span>
                  <input id="goalTarget" type="number" value="10000000" oninput="calculateGoal()" style="width:100%;box-sizing:border-box; background:#131D2E; border:1px solid rgba(52,211,153,0.3); border-radius:10px; padding:10px 12px 10px 26px; font-size:13px;font-weight:700; color:#34D399;outline:none;" />
                </div>
                <div style="display:flex;gap:4px;margin-top:6px;flex-wrap:wrap;">
                  ${[{label:'1Cr',val:10000000},{label:'2Cr',val:20000000},{label:'5Cr',val:50000000},{label:'10Cr',val:100000000}].map(g => `<button onclick="document.getElementById('goalTarget').value=${g.val}; calculateGoal();" style="padding:3px 8px;border-radius:5px; border:1px solid rgba(52,211,153,0.2); background:rgba(52,211,153,0.08); color:#34D399;font-size:10px; font-weight:600;cursor:pointer;">${g.label}</button>`).join('')}
                </div>
              </div>
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Time Horizon (Years)</label>
                <input id="goalYears" type="range" min="1" max="40" value="15" oninput="document.getElementById('goalYrsDisplay').textContent = this.value + ' years'; calculateGoal();" style="width:100%;accent-color:#34D399;margin-top:8px;" />
                <div id="goalYrsDisplay" style="font-size:14px;font-weight:800;color:#34D399; text-align:center;margin-top:4px;">15 years</div>
              </div>
              <div>
                <label style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; display:block;margin-bottom:6px;">Expected Return (%)</label>
                <input id="goalCagr" type="number" value="12" oninput="calculateGoal()" style="width:100%;box-sizing:border-box; background:#131D2E; border:1px solid rgba(52,211,153,0.3); border-radius:10px;padding:10px 12px; font-size:14px;font-weight:700; color:#34D399;outline:none;" />
                <div style="font-size:10px;color:#4A5568;margin-top:4px;">Your portfolio 3Y CAGR: <span id="goalPortfolioCagr" style="color:#34D399;font-weight:700;">—</span></div>
              </div>
            </div>
            <div id="goalResult" style="background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(16,185,129,0.06)); border: 1px solid rgba(52,211,153,0.25); border-radius: 14px; padding: 20px;">
              <div style="display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 16px;">
                ${[
                  {id:'goalSIPNeeded', label:'Monthly SIP Needed', color:'#34D399', big:true},
                  {id:'goalTotalInvested', label:'Total You Invest', color:'#00D2FF', big:false},
                  {id:'goalWealthGain', label:'Wealth Created', color:'#A78BFA', big:false},
                  {id:'goalMultiplier', label:'Money Multiplier', color:'#F59E0B', big:false}
                ].map(g => `<div style="text-align:center;"><div id="${g.id}" style="font-size:${g.big?'24px':'18px'}; font-weight:900;color:${g.color}; letter-spacing:-0.5px;margin-bottom:4px;">—</div><div style="font-size:9px;color:#4A5568; text-transform:uppercase; letter-spacing:0.06em;font-weight:600;">${g.label}</div></div>`).join('')}
              </div>
              <div>
                <div style="font-size:10px;color:#4A5568;font-weight:700; text-transform:uppercase;letter-spacing:0.06em; margin-bottom:10px;">Wealth Milestones</div>
                <div id="goalMilestones" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
              </div>
            </div>
          </div>

          <!-- ── NEW SECTION 4: INFLATION-ADJUSTED ANALYSIS ── -->
          <div style="background: #0D1B2A; border: 1px solid rgba(255,159,10,0.2); border-radius: 18px; padding: 20px; margin-bottom: 16px;">
            <div style="margin-bottom:14px;">
              <div style="font-size:13px;font-weight:800;color:#F1F5F9;">📊 Inflation-Adjusted Returns</div>
              <div style="font-size:11px;color:#4A5568;margin-top:2px;">Real purchasing power of your investment</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px; margin-bottom:14px;">
              <span style="font-size:11px;color:#4A5568;">Inflation Rate:</span>
              ${[4,6,7].map(r => `<button onclick="document.getElementById('inflationRate').value=${r}; calculateInflationAdjusted(); document.querySelectorAll('.inflBtn').forEach(b=>{ b.style.background='rgba(255,255,255,0.04)'; b.style.color='#4A5568'; }); this.style.background='rgba(245,158,11,0.15)'; this.style.color='#F59E0B';" class="inflBtn" style="padding:4px 10px;border-radius:6px; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.04); color:#4A5568;font-size:10px;font-weight:600; cursor:pointer;">${r}%</button>`).join('')}
              <input id="inflationRate" type="number" value="6" oninput="calculateInflationAdjusted()" style="width:44px;background:#131D2E; border:1px solid rgba(245,158,11,0.2); border-radius:6px;padding:3px 6px; font-size:11px;font-weight:700; color:#F59E0B;text-align:center;outline:none;" />
              <span style="color:#F59E0B;font-weight:700;">%</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;">
              ${[5,10,15,20].map(yr => `<div style="display:grid; grid-template-columns:60px 1fr 1fr 1fr; padding:8px 12px; background:rgba(255,255,255,0.02); border-radius:8px;align-items:center; gap:8px;"><span style="font-size:11px;font-weight:700;color:#F59E0B;">${yr}Y</span><div style="text-align:center;"><div id="inflNominal${yr}" style="font-size:12px;font-weight:700;color:#34D399;">—</div><div style="font-size:9px;color:#374151;">Nominal</div></div><div style="text-align:center;"><div id="inflReal${yr}" style="font-size:12px;font-weight:700;color:#F59E0B;">—</div><div style="font-size:9px;color:#374151;">Real Value</div></div><div style="text-align:center;"><div id="inflPurchasing${yr}" style="font-size:11px;font-weight:700;color:#F87171;">—</div><div style="font-size:9px;color:#374151;">Purchasing Power</div></div></div>`).join('')}
            </div>
          </div>
"""

new_right_html = """
          <!-- Summary Stats in right panel -->
          <div style="display:flex;flex-direction:column;gap:8px; margin-top:14px;">
            <div style="background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.15); border-radius:10px;padding:12px;">
              <div style="font-size:9px;color:#4A5568; text-transform:uppercase;letter-spacing:0.06em; margin-bottom:4px;">10-Year SIP Value <span style="color:#34D399;">(@12% CAGR)</span></div>
              <div id="overviewProj10Y" style="font-size:18px;font-weight:900;color:#34D399;">—</div>
              <div style="font-size:9px;color:#374151;margin-top:2px;">on ₹5,000/month SIP</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:10px;padding:12px;">
              <div style="font-size:9px;color:#4A5568; text-transform:uppercase;letter-spacing:0.06em; margin-bottom:8px;">Risk Profile</div>
              <div style="display:flex;gap:4px;margin-bottom:4px;">
                ${['Low','Moderate','High','Very High'].map((lvl,i) => `<div id="riskBar${i}" style="height:6px;flex:1;border-radius:3px; background:rgba(255,255,255,0.06); transition:background 300ms;"></div>`).join('')}
              </div>
              <div id="riskLabel" style="font-size:11px;font-weight:700;color:#F59E0B;">Moderate-High</div>
            </div>
          </div>
"""

js_block = """
// ══════════════════════════════════════════
// FINANCIAL CALCULATORS
// ══════════════════════════════════════════

let calcState = { mode: 'SIP', sipAmount: 5000, lumpAmount: 100000, years: 10, rate: 12, stepUp: 0, inflation: 6, goalTarget: 10000000, goalYears: 15, goalRate: 12, scenarioRates: [6, 12, 18], scBarChart: null };

const fmtCr = n => { if (n >= 1e7) return '₹' + (n/1e7).toFixed(2) + ' Cr'; if (n >= 1e5) return '₹' + (n/1e5).toFixed(2) + ' L'; return '₹' + Math.round(n).toLocaleString('en-IN'); };

function switchMode(mode) {
  calcState.mode = mode;
  const sipBtn  = document.getElementById('sipToggleBtn');
  const lumpBtn = document.getElementById('lumpToggleBtn');
  if (mode === 'SIP') {
    if(sipBtn) { sipBtn.style.background = 'linear-gradient(135deg,#8B5CF6,#6D28D9)'; sipBtn.style.color = 'white'; }
    if(lumpBtn) { lumpBtn.style.background = 'transparent'; lumpBtn.style.color = '#4A5568'; }
  } else {
    if(lumpBtn) { lumpBtn.style.background = 'linear-gradient(135deg,#8B5CF6,#6D28D9)'; lumpBtn.style.color = 'white'; }
    if(sipBtn) { sipBtn.style.background = 'transparent'; sipBtn.style.color = '#4A5568'; }
    const input = document.getElementById('sipAmount');
    if (input) {
      input.value = calcState.lumpAmount;
      input.previousElementSibling.textContent = 'Lump Sum Amount (₹)';
    }
  }
  calculateProjection();
}

function calculateProjection() {
  const amount = parseFloat(document.getElementById('sipAmount')?.value || 5000);
  const years  = parseInt(document.getElementById('sipYears')?.value || 10);
  const rate   = parseFloat(document.getElementById('sipRate')?.value || 12);
  const stepUp = parseFloat(document.getElementById('sipStepUp')?.value || 0) / 100;
  const mode   = calcState.mode;
  const r      = rate / 100;
  const mRate  = r / 12;
  
  let totalInvested = 0; let futureValue = 0; const yearlyData = [];
  if (mode === 'SIP') {
    let monthlyAmt = amount; let cumInvested = 0; let cumValue = 0;
    for (let y = 1; y <= years; y++) {
      for (let m = 1; m <= 12; m++) { cumValue = (cumValue + monthlyAmt) * (1 + mRate); cumInvested += monthlyAmt; }
      yearlyData.push({ year: y, invested: cumInvested, value: cumValue, gains: cumValue - cumInvested, returnPct: ((cumValue - cumInvested) / cumInvested * 100) });
      if (stepUp > 0) monthlyAmt *= (1 + stepUp);
    }
    totalInvested = yearlyData[years-1].invested; futureValue = yearlyData[years-1].value;
  } else {
    totalInvested = amount;
    for (let y = 1; y <= years; y++) {
      const val = amount * Math.pow(1 + r, y);
      yearlyData.push({ year: y, invested: amount, value: val, gains: val - amount, returnPct: (val - amount) / amount * 100 });
    }
    futureValue = yearlyData[years-1].value;
  }
  
  const wealthGain = futureValue - totalInvested;
  const absReturn = (wealthGain / totalInvested) * 100;
  const monthlyIncome = futureValue * 0.08 / 12;
  
  const ids = { projTotalInvested: fmtCr(totalInvested), projFutureValue: fmtCr(futureValue), projWealthGain: fmtCr(wealthGain), projAbsReturn: '+' + absReturn.toFixed(1) + '%', projMonthly: fmtINR(monthlyIncome) + '/mo' };
  Object.entries(ids).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.textContent = val; });
  renderYearlyTable(yearlyData);
}

function renderYearlyTable(data) {
  const container = document.getElementById('sipYearlyTable');
  if (!container) return;
  container.innerHTML = data.map((row, i) => {
    const isHighlight = [1,3,5,10,15,20].includes(row.year);
    return `<div style="display:grid; grid-template-columns:60px 1fr 1fr 1fr 1fr; padding:8px 16px; border-bottom:1px solid rgba(255,255,255,0.03); background:${isHighlight ? 'rgba(139,92,246,0.06)' : 'transparent'}; transition:background 130ms; cursor:default;" onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background='${isHighlight ? 'rgba(139,92,246,0.06)' : 'transparent'}'"><span style="font-size:11px;font-weight:700; color:${isHighlight ? '#A78BFA' : '#4A5568'};">Yr ${row.year}</span><span style="font-size:11px;color:#64748B;">${fmtCr(row.invested)}</span><span style="font-size:11px;color:#34D399;">+${fmtCr(row.gains)}</span><span style="font-size:11px;font-weight:700;color:#00D2FF;">${fmtCr(row.value)}</span><span style="font-size:11px;font-weight:700; color:${row.returnPct > 100 ? '#34D399' : '#F59E0B'};">+${row.returnPct.toFixed(1)}%</span></div>`;
  }).join('');
}

function calculateScenarios() {
  const amount  = parseFloat(document.getElementById('sipAmount')?.value || 5000);
  const mode    = calcState.mode;
  const years   = [5, 10, 15, 20];
  const scData  = [0, 1, 2].map(i => ({ rate: parseFloat(document.getElementById(`scenarioCagr${i}`)?.value || [6, 12, 18][i]) }));
  
  scData.forEach((sc, idx) => {
    const r = sc.rate / 100;
    const mRate = r / 12;
    years.forEach(yr => {
      let val;
      if (mode === 'SIP') {
        const n = yr * 12;
        val = amount * ((Math.pow(1+mRate, n) - 1) / mRate) * (1 + mRate);
      } else { val = amount * Math.pow(1 + r, yr); }
      const el = document.getElementById(`sc${idx}yr${yr}`);
      if (el) el.textContent = fmtCr(val);
    });
  });
  updateScenarioChart(amount, mode, scData);
}

function updateScenarioChart(amount, mode, scData) {
  const canvas = document.getElementById('scenarioBarChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const labels = ['5 Years','10 Years','15 Years','20 Years'];
  const colors = ['#F87171','#F59E0B','#34D399'];
  const names  = ['Bear ('+scData[0].rate+'%)','Base ('+scData[1].rate+'%)','Bull ('+scData[2].rate+'%)'];
  
  if (calcState.scBarChart) { calcState.scBarChart.destroy(); }
  const datasets = scData.map((sc, i) => {
    const r = sc.rate / 100; const mRate = r / 12;
    return {
      label: names[i],
      data: [5,10,15,20].map(yr => {
        if (mode === 'SIP') { const n = yr * 12; return Math.round(amount * ((Math.pow(1+mRate,n)-1)/mRate) * (1+mRate)); }
        else { return Math.round(amount * Math.pow(1+r, yr)); }
      }),
      backgroundColor: colors[i] + '80', borderColor: colors[i], borderWidth: 1.5, borderRadius: 6
    };
  });
  calcState.scBarChart = new Chart(ctx, { type: 'bar', data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color:'#4A5568', font:{size:10} } }, tooltip: { backgroundColor: '#131D2E', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, callbacks: { label: ctx => ` ${ctx.dataset.label}: ${fmtCr(ctx.raw)}` } } }, scales: { x: { ticks: { color:'#374151', font:{size:10} }, grid: { color:'rgba(255,255,255,0.03)' } }, y: { ticks: { color:'#374151',font:{size:9}, callback: v => fmtCr(v) }, grid: { color:'rgba(255,255,255,0.03)' } } } } });
}

function calculateGoal() {
  const target = parseFloat(document.getElementById('goalTarget')?.value || 10000000);
  const years  = parseInt(document.getElementById('goalYears')?.value || 15);
  const rate   = parseFloat(document.getElementById('goalCagr')?.value || 12);
  const mRate  = rate / 100 / 12; const n = years * 12;
  const sipNeeded = target * mRate / ((Math.pow(1+mRate, n) - 1) * (1+mRate));
  const totalInvested = sipNeeded * n; const wealthGain = target - totalInvested;
  const multiplier = (target / totalInvested).toFixed(1);
  const updates = { goalSIPNeeded: fmtINR(sipNeeded) + '/mo', goalTotalInvested: fmtCr(totalInvested), goalWealthGain: fmtCr(wealthGain), goalMultiplier: multiplier + 'x' };
  Object.entries(updates).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.textContent = val; });
  const portEl = document.getElementById('goalPortfolioCagr');
  if (portEl && window._portfolioCagr3Y) {
    portEl.textContent = window._portfolioCagr3Y + '%';
    const goalCagrInput = document.getElementById('goalCagr');
    if (goalCagrInput && !goalCagrInput._userEdited) { goalCagrInput.value = window._portfolioCagr3Y; }
  }
  const milestones = [0.25, 0.5, 0.75, 1.0].map(pct => {
    const targetPct = target * pct; let cumVal = 0;
    for (let m = 1; m <= n; m++) {
      cumVal = (cumVal + sipNeeded) * (1 + mRate);
      if (cumVal >= targetPct) return { pct: Math.round(pct*100), months: m, years: (m/12).toFixed(1), amount: fmtCr(targetPct) };
    }
    return null;
  }).filter(Boolean);
  const msContainer = document.getElementById('goalMilestones');
  if (msContainer) {
    const colors = ['#F59E0B','#06B6D4','#A78BFA','#34D399'];
    msContainer.innerHTML = milestones.map((ms, i) => `<div style="background:${colors[i]}15; border:1px solid ${colors[i]}30; border-radius:10px;padding:10px 14px; flex:1;min-width:100px;"><div style="font-size:16px;font-weight:900; color:${colors[i]};margin-bottom:2px;">${ms.years} yrs</div><div style="font-size:10px;color:#4A5568;">Reach ${ms.pct}% of goal<br/><span style="color:${colors[i]};font-weight:600;">${ms.amount}</span></div></div>`).join('');
  }
}

function calculateInflationAdjusted() {
  const inflation = parseFloat(document.getElementById('inflationRate')?.value || 6) / 100;
  const amount = parseFloat(document.getElementById('sipAmount')?.value || 5000);
  const rate = parseFloat(document.getElementById('sipRate')?.value || 12) / 100;
  const mRate = rate / 12;
  [5, 10, 15, 20].forEach(yr => {
    const n = yr * 12;
    const nominalVal = amount * ((Math.pow(1+mRate, n) - 1) / mRate) * (1+mRate);
    const realVal = nominalVal / Math.pow(1+inflation, yr);
    const purchasingPowerLoss = (1 - 1/Math.pow(1+inflation, yr)) * 100;
    const nEl = document.getElementById(`inflNominal${yr}`); const rEl = document.getElementById(`inflReal${yr}`); const pEl = document.getElementById(`inflPurchasing${yr}`);
    if (nEl) nEl.textContent = fmtCr(nominalVal); if (rEl) rEl.textContent = fmtCr(realVal); if (pEl) pEl.textContent = '-' + purchasingPowerLoss.toFixed(1) + '%';
  });
}

function initCalculators() { calculateProjection(); calculateScenarios(); calculateGoal(); calculateInflationAdjusted(); }

function syncCalculatorsWithPortfolio(analysisData) {
  if (!analysisData?.summary) return;
  const s = analysisData.summary;
  window._portfolioCagr3Y = s.cagr_3y ? s.cagr_3y.toFixed(2) : '12.00';
  window._portfolioCagr5Y = s.cagr_5y ? s.cagr_5y.toFixed(2) : '12.00';
  
  const rateInput = document.getElementById('sipRate');
  if (rateInput && s.cagr_3y && s.cagr_3y > 0) rateInput.value = Math.round(s.cagr_3y);
  const goalCagr = document.getElementById('goalCagr');
  if (goalCagr && s.cagr_3y && s.cagr_3y > 0) goalCagr.value = Math.round(s.cagr_3y);
  const sc1 = document.getElementById('scenarioCagr1');
  if (sc1 && s.cagr_3y) sc1.value = Math.round(s.cagr_3y);
  
  calculateProjection(); calculateScenarios(); calculateGoal(); calculateInflationAdjusted();
  
  const portEl = document.getElementById('goalPortfolioCagr');
  if (portEl && s.cagr_3y) portEl.textContent = s.cagr_3y.toFixed(2) + '%';
  
  // Right panel overview update
  const mRate = (s.cagr_3y || 12) / 100 / 12;
  const proj10y = 5000 * ((Math.pow(1+mRate, 120) - 1) / mRate) * (1+mRate);
  const ovEl = document.getElementById('overviewProj10Y');
  if (ovEl) ovEl.textContent = fmtCr(proj10y);
  
  // Update Risk Profile (dummy logic for visual)
  let vol = s.volatility || 15;
  let rLevel = vol < 8 ? 0 : vol < 12 ? 1 : vol < 18 ? 2 : 3;
  let labels = ['Low', 'Moderate', 'High', 'Very High'];
  let colors = ['#34D399', '#F59E0B', '#F87171', '#EF4444'];
  const rlEl = document.getElementById('riskLabel');
  if (rlEl) { rlEl.textContent = labels[rLevel]; rlEl.style.color = colors[rLevel]; }
  for(let i=0; i<4; i++) {
    let bar = document.getElementById(`riskBar${i}`);
    if (bar) bar.style.background = (i <= rLevel) ? colors[i] : 'rgba(255,255,255,0.06)';
  }
}

document.addEventListener('DOMContentLoaded', () => { setTimeout(initCalculators, 500); });
"""

# Find injection points
# 1. Insert new_html after <div id="pgTimelineStats"...</div></div>\n
insert_pos_html = content.find('<div id="pgTimelineStats" style="display:grid; grid-template-columns:repeat(5, 1fr); gap:16px; margin-top:20px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.03);"></div>\n          </div>')
if insert_pos_html != -1:
    end_of_div = content.find('</div>', insert_pos_html) + 6
    content = content[:end_of_div] + '\n' + new_html + content[end_of_div:]
    print("HTML inserted successfully.")
else:
    print("Could not find insert_pos_html!")

# 2. Insert right panel HTML
insert_pos_right = content.find('<div id="pgDonutLegend" style="width:100%; display:flex; flex-direction:column; gap:6px;"><div style="text-align:center; font-size:11px; color:#374151;">Add funds to see allocation</div></div>\n          </div>')
if insert_pos_right != -1:
    end_of_div = content.find('</div>', insert_pos_right) + 6
    end_of_div2 = content.find('</div>', end_of_div) + 6
    content = content[:end_of_div2] + '\n' + new_right_html + content[end_of_div2:]
    print("Right HTML inserted successfully.")
else:
    print("Could not find insert_pos_right!")

# 3. Insert JS block before "// Initialize"
js_insert = content.find('// Initialize')
if js_insert != -1:
    content = content[:js_insert] + js_block + '\n        ' + content[js_insert:]
    print("JS inserted successfully.")
else:
    print("Could not find JS insert position!")

# 4. Insert syncCalculatorsWithPortfolio(data) after renderResults(data);
render_pos = content.find('renderResults(data);')
if render_pos != -1:
    end_pos = render_pos + len('renderResults(data);')
    content = content[:end_pos] + '\n              syncCalculatorsWithPortfolio(data);' + content[end_pos:]
    print("Hook inserted successfully.")
else:
    print("Could not find renderResults!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

