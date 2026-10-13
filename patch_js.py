import os

def patch_js():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    old_fetch = """            try {
                const res = await fetch('/api/portfolio/analyze', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ portfolio: portfolio })
                });"""
                
    new_fetch = """            try {
                // Gather inputs from the builder UI
                const invType = document.getElementById('pbInvType') ? document.getElementById('pbInvType').value : 'SIP';
                const invAmt = parseFloat(document.getElementById('pbTotalInvestment').value) || 100000;
                const horizon = parseInt(document.getElementById('pbHorizon') ? document.getElementById('pbHorizon').value : 5);
                const risk = document.getElementById('pbRisk') ? document.getElementById('pbRisk').value : 'Moderate';
                const goal = document.getElementById('pbGoal') ? document.getElementById('pbGoal').value : 'Wealth Creation';
                
                // Construct allocation dict
                const allocation = {};
                portfolio.forEach(f => {
                    allocation[f.code] = parseFloat(f.weight) || 0;
                });
                
                const investment_details = {
                    type: invType,
                    sip_amount: invType.includes('SIP') ? invAmt : 0,
                    lumpsum_amount: invType.includes('Lumpsum') ? invAmt : 0,
                    horizon: horizon,
                    risk: risk,
                    goal: goal
                };

                const res = await fetch('/api/portfolio/analyze', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        funds: portfolio, 
                        allocation: allocation, 
                        investment_details: investment_details 
                    })
                });"""
                
    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched analyzeAndShow in templates/index.html")
    else:
        print("Target fetch call not found in templates/index.html")

if __name__ == "__main__":
    patch_js()
