import re

def fix_projection_bug():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the HTML
    html_old_title = '<div style="font-size:9px;color:var(--text-dark); text-transform:uppercase;letter-spacing:0.06em; margin-bottom:4px;">10-Year SIP Value <span style="color:#34D399;">(@12% CAGR)</span></div>'
    html_new_title = '<div id="overviewProjTitle" style="font-size:9px;color:var(--text-dark); text-transform:uppercase;letter-spacing:0.06em; margin-bottom:4px;">10-Year SIP Value <span style="color:#34D399;">(@12% CAGR)</span></div>'
    
    html_old_sub = '<div style="font-size:9px;color:#374151;margin-top:2px;">on ₹5,000/month SIP</div>'
    html_new_sub = '<div id="overviewProjSub" style="font-size:9px;color:#374151;margin-top:2px;">on ₹5,000/month SIP</div>'

    content = content.replace(html_old_title, html_new_title)
    content = content.replace(html_old_sub, html_new_sub)

    # 2. Update the JS logic
    js_old = """  // Right panel overview update
  const mRate = (s.cagr_3y || 12) / 100 / 12;
  const proj10y = 5000 * ((Math.pow(1+mRate, 120) - 1) / mRate) * (1+mRate);
  const ovEl = document.getElementById('overviewProj10Y');
  if (ovEl) ovEl.textContent = fmtCr(proj10y);"""

    js_new = """  // Right panel overview update dynamically based on user input
  const invAmtInput = document.getElementById('pgInvestmentAmount');
  const invTypeInput = document.getElementById('pgInvestmentType');
  const amt = invAmtInput ? parseFloat(invAmtInput.value) || 5000 : 5000;
  const isSip = invTypeInput ? invTypeInput.value === 'sip' : true;
  
  const rate = (s.cagr_3y || 12) / 100;
  const mRate = rate / 12;
  
  let proj10y = 0;
  if (isSip) {
      proj10y = amt * ((Math.pow(1+mRate, 120) - 1) / mRate) * (1+mRate);
  } else {
      proj10y = amt * Math.pow(1+rate, 10);
  }
  
  const ovEl = document.getElementById('overviewProj10Y');
  if (ovEl) ovEl.textContent = fmtCr(proj10y);
  
  const ovTitle = document.getElementById('overviewProjTitle');
  if (ovTitle) ovTitle.innerHTML = `10-Year ${isSip ? 'SIP' : 'Lumpsum'} Value <span style="color:#34D399;">(@${(s.cagr_3y || 12).toFixed(1)}% CAGR)</span>`;
  
  const ovSub = document.getElementById('overviewProjSub');
  if (ovSub) ovSub.textContent = `on ₹${amt.toLocaleString('en-IN')}${isSip ? '/month SIP' : ' Lumpsum'}`;"""

    content = content.replace(js_old, js_new)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Portfolio Projection logic dynamically updated!")

if __name__ == '__main__':
    fix_projection_bug()
