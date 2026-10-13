import os

def patch_generate_ui():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    target = "$('pgInfoRange').textContent = `${s.date_range.start} – ${s.date_range.end}`;"
    
    new_js = """$('pgInfoRange').textContent = `${s.date_range.start} – ${s.date_range.end}`;
            
            // --- NEW: Professional Portfolio Overview and Allocation Analysis ---
            let overviewBox = document.getElementById('pg_professional_overview');
            if (!overviewBox) {
                overviewBox = document.createElement('div');
                overviewBox.id = 'pg_professional_overview';
                overviewBox.style.marginTop = '24px';
                overviewBox.style.marginBottom = '24px';
                overviewBox.style.padding = '24px';
                overviewBox.style.background = 'linear-gradient(135deg, rgba(13,27,42,0.8), rgba(19,29,46,0.9))';
                overviewBox.style.borderRadius = '16px';
                overviewBox.style.border = '1px solid rgba(0,210,255,0.2)';
                
                // Insert it just before the timeline section
                const timelineSection = document.getElementById('pgTimelineChart').closest('div[style*="background: #0D1B2A"]');
                if (timelineSection) {
                    timelineSection.parentNode.insertBefore(overviewBox, timelineSection);
                }
            }
            
            // Build the allocation strings
            let eqDebtString = `Equity: ${data.asset_allocation.Equity || 0}% | Debt: ${data.asset_allocation.Debt || 0}% | Hybrid: ${data.asset_allocation.Hybrid || 0}% | Gold: ${data.asset_allocation.Gold || 0}%`;
            
            // Build AMC string (top 3)
            let amcEntries = Object.entries(data.amc_allocation || {}).sort((a,b) => b[1]-a[1]);
            let amcString = amcEntries.slice(0, 3).map(e => `${e[0]}: ${e[1]}%`).join(' | ');
            if (amcEntries.length > 3) amcString += ' | Others...';
            
            overviewBox.innerHTML = `
                <h3 style="color:#F1F5F9; margin-top:0; margin-bottom:16px; font-size:16px; display:flex; align-items:center; gap:8px;">
                    <span style="font-size:20px;">🔬</span> Professional Portfolio Overview
                </h3>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px;">
                    <div style="background:rgba(0,0,0,0.2); padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                        <h4 style="color:#A78BFA; margin:0 0 12px 0; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Summary</h4>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <div style="display:flex; justify-content:space-between;"><span style="color:#94A3B8; font-size:12px;">Total Funds</span><span style="color:#F1F5F9; font-weight:700; font-size:12px;">${s.fund_count}</span></div>
                            <div style="display:flex; justify-content:space-between;"><span style="color:#94A3B8; font-size:12px;">Total AMCs</span><span style="color:#F1F5F9; font-weight:700; font-size:12px;">${s.total_amcs || '—'}</span></div>
                            <div style="display:flex; justify-content:space-between;"><span style="color:#94A3B8; font-size:12px;">Exp. Ratio (Wt.)</span><span style="color:#F1F5F9; font-weight:700; font-size:12px;">${s.expense_ratio || 'Data unavailable'}</span></div>
                        </div>
                    </div>
                    <div style="background:rgba(0,0,0,0.2); padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                        <h4 style="color:#00D2FF; margin:0 0 12px 0; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Allocation Analysis</h4>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <div><span style="color:#94A3B8; font-size:11px; display:block; margin-bottom:2px;">Asset Class</span><span style="color:#F1F5F9; font-weight:600; font-size:11px;">${eqDebtString}</span></div>
                            <div><span style="color:#94A3B8; font-size:11px; display:block; margin-bottom:2px;">Top AMC Exposure</span><span style="color:#F1F5F9; font-weight:600; font-size:11px;">${amcString || '—'}</span></div>
                            <div><span style="color:#94A3B8; font-size:11px; display:block; margin-bottom:2px;">Market Cap</span><span style="color:#F1F5F9; font-weight:600; font-size:11px;">${s.market_cap_allocation || 'Data unavailable'}</span></div>
                        </div>
                    </div>
                </div>
            `;
"""
    
    if target in content:
        content = content.replace(target, new_js)
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched renderResults in templates/index.html")
    else:
        print("Target not found in templates/index.html")

if __name__ == "__main__":
    patch_generate_ui()
