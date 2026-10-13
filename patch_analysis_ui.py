import os

def patch_analysis():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    target = "document.getElementById('savedTotalInv').textContent = '₹' + inv.toLocaleString('en-IN');"
    
    new_js = """document.getElementById('savedTotalInv').textContent = '₹' + inv.toLocaleString('en-IN');
            
            // New Data Architecture Injection
            if (data.results && data.results.status === 'success') {
                const res = data.results;
                
                // You can expand this to update the UI with all 25 sections
                console.log("Analysis Results:", res);
                
                // Update DOM elements if they exist (we will build the UI in the next iteration)
                // For now, let's inject a summary box dynamically
                let summaryBox = document.getElementById('portfolio_advanced_summary');
                if (!summaryBox) {
                    summaryBox = document.createElement('div');
                    summaryBox.id = 'portfolio_advanced_summary';
                    summaryBox.style.marginTop = '20px';
                    summaryBox.style.padding = '20px';
                    summaryBox.style.background = '#0D1B2A';
                    summaryBox.style.borderRadius = '16px';
                    summaryBox.style.border = '1px solid rgba(0,210,255,0.2)';
                    
                    // Insert it after the top stat cards
                    const statsContainer = document.getElementById('savedTotalInv').parentElement.parentElement;
                    statsContainer.parentNode.insertBefore(summaryBox, statsContainer.nextSibling);
                }
                
                summaryBox.innerHTML = `
                    <h3 style="color:#F1F5F9; margin-top:0;">📊 Advanced Portfolio Analysis</h3>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                        <div>
                            <h4 style="color:#A78BFA; margin-bottom:8px;">Asset Allocation</h4>
                            <p style="color:#94A3B8; font-size:12px;">Equity: ${res.allocation.equity}% | Debt: ${res.allocation.debt}% | Hybrid: ${res.allocation.hybrid}%</p>
                        </div>
                        <div>
                            <h4 style="color:#A78BFA; margin-bottom:8px;">Performance & Cost</h4>
                            <p style="color:#94A3B8; font-size:12px;">Weighted Exp. Ratio: ${res.cost.weighted_expense_ratio}%</p>
                            <p style="color:#94A3B8; font-size:12px;">3Y Expected Return: ${res.performance.returns_3yr}%</p>
                        </div>
                        <div>
                            <h4 style="color:#A78BFA; margin-bottom:8px;">Diversification</h4>
                            <p style="color:#94A3B8; font-size:12px;">Total Funds: ${res.diversification.total_funds}</p>
                            <p style="color:#94A3B8; font-size:12px;">Total AMCs: ${res.diversification.total_amcs}</p>
                        </div>
                        <div>
                            <h4 style="color:#A78BFA; margin-bottom:8px;">Projection</h4>
                            <p style="color:#94A3B8; font-size:12px;">Total Invested: ₹${res.projection.total_invested.toLocaleString('en-IN')}</p>
                            <p style="color:#94A3B8; font-size:12px;">Projected Value: ₹${res.projection.projected_value.toLocaleString('en-IN')}</p>
                        </div>
                    </div>
                `;
            }
"""
    
    if target in content:
        content = content.replace(target, new_js)
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched renderSavedPortfolioView in templates/index.html")
    else:
        print("Target not found in templates/index.html")

if __name__ == "__main__":
    patch_analysis()
