import re

def fix_portfolio_donut_legend():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace the tooltip callback and the pgDonutLegend HTML.
    
    # 1. Tooltip Callback Replacement
    old_tooltip = "tooltip: { backgroundColor: 'var(--bg-card-alt)', borderColor: 'var(--border-alpha-10)', borderWidth: 1, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.raw.toFixed(1)}%` } }"
    new_tooltip = "tooltip: { backgroundColor: 'var(--bg-card-alt)', borderColor: 'var(--border-alpha-10)', borderWidth: 1, callbacks: { label: ctx => { const t = parseFloat(document.getElementById('pgInvestmentAmount')?.value||10000); return ` ${ctx.label}: ₹${(t*ctx.raw/100).toLocaleString('en-IN')} (${ctx.raw.toFixed(1)}%)`; } } }"
    content = content.replace(old_tooltip, new_tooltip)
    
    # 2. Legend HTML Replacement
    # old line: <span style="color:${COLORS[i%COLORS.length]};font-weight:700;flex-shrink:0;">${f.weight.toFixed(1)}%</span>
    
    # We need to compute totalInvAmt and suffix before the map
    # We will replace the entire if ($('pgDonutLegend')) block
    
    old_legend_block = """            if ($('pgDonutLegend')) {
              $('pgDonutLegend').innerHTML = _funds.map((f, i) => `
                <div style="display:flex;align-items:center;gap:7px;font-size:11px;">
                  <div style="width:9px;height:9px;border-radius:2px;background:${COLORS[i%COLORS.length]};flex-shrink:0;"></div>
                  <span style="color:var(--text-muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${f.name.substring(0,24)}${f.name.length>24?'…':''}</span>
                  <span style="color:${COLORS[i%COLORS.length]};font-weight:700;flex-shrink:0;">${f.weight.toFixed(1)}%</span>
                </div>
              `).join('');
            }"""

    new_legend_block = """            if ($('pgDonutLegend')) {
              const totalInvAmt = parseFloat(document.getElementById('pgInvestmentAmount')?.value || 10000);
              const invType = document.getElementById('pgInvestmentType')?.value || 'lumpsum';
              const suffix = invType === 'sip' ? '/mo' : '';
              
              $('pgDonutLegend').innerHTML = _funds.map((f, i) => {
                const amt = (totalInvAmt * f.weight / 100);
                return `
                <div style="display:flex;align-items:center;gap:7px;font-size:11px;">
                  <div style="width:9px;height:9px;border-radius:2px;background:${COLORS[i%COLORS.length]};flex-shrink:0;"></div>
                  <span style="color:var(--text-muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${f.name.substring(0,24)}${f.name.length>24?'…':''}</span>
                  <span style="color:${COLORS[i%COLORS.length]};font-weight:700;flex-shrink:0;">₹${amt.toLocaleString('en-IN')}${suffix} <span style="opacity:0.6;font-size:9px;">(${f.weight.toFixed(1)}%)</span></span>
                </div>
              `}).join('');
            }"""

    content = content.replace(old_legend_block, new_legend_block)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Portfolio Donut Legend successfully patched!")

if __name__ == '__main__':
    fix_portfolio_donut_legend()
