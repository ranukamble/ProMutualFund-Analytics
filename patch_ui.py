import os

HTML_NEW_SECTION = """
            <div style="background: #0D1B2A; border: 1px solid rgba(0,210,255,0.15); border-radius: 16px; padding: 20px; margin-bottom: 20px;">
                <h3 style="font-size: 14px; font-weight: 700; color: #F1F5F9; margin-top: 0; margin-bottom: 16px;">Investment Details</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div>
                        <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Investment Type</label>
                        <select id="pbInvType" style="width: 100%; background: #131D2E; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #E2E8F0; outline: none;">
                            <option value="SIP">SIP</option>
                            <option value="Lumpsum">Lumpsum</option>
                            <option value="SIP+Lumpsum">SIP + Lumpsum</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Monthly SIP / Lumpsum</label>
                        <div style="position: relative;">
                            <span style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #00D2FF; font-weight: 700; font-size: 14px;">₹</span>
                            <input id="pbTotalInvestment" type="number" value="10000" oninput="updateAllAmounts()" style="width: 100%; box-sizing: border-box; background: #131D2E; border: 1px solid rgba(0,210,255,0.2); border-radius: 8px; padding: 8px 12px 8px 24px; font-size: 14px; font-weight: 700; color: #00D2FF; outline: none;" />
                        </div>
                    </div>
                    <div>
                        <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Investment Horizon</label>
                        <select id="pbHorizon" style="width: 100%; background: #131D2E; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #E2E8F0; outline: none;">
                            <option value="1">1 Year</option>
                            <option value="3">3 Years</option>
                            <option value="5" selected>5 Years</option>
                            <option value="7">7 Years</option>
                            <option value="10">10 Years</option>
                            <option value="15">15 Years</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Risk Preference</label>
                        <select id="pbRisk" style="width: 100%; background: #131D2E; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #E2E8F0; outline: none;">
                            <option value="Conservative">Conservative</option>
                            <option value="Moderate" selected>Moderate</option>
                            <option value="Aggressive">Aggressive</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Investment Goal</label>
                        <select id="pbGoal" style="width: 100%; background: #131D2E; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #E2E8F0; outline: none;">
                            <option value="Wealth Creation">Wealth Creation</option>
                            <option value="Retirement">Retirement</option>
                            <option value="Child Education">Child Education</option>
                            <option value="House">House</option>
                            <option value="Emergency Corpus">Emergency Corpus</option>
                        </select>
                    </div>
                </div>
            </div>
"""

def patch_ui():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    target = '''            <div style="background: #0D1B2A; border: 1px solid rgba(0,210,255,0.15); border-radius: 16px; padding: 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 24px;">
                <div style="flex: 1;">
                    <label style="font-size: 10px; font-weight: 700; color: #4A5568; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 8px;">Total Investment Amount</label>
                    <div style="position: relative;">
                        <span style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #00D2FF; font-weight: 700; font-size: 16px;">₹</span>
                        <input id="pbTotalInvestment" type="number" value="100000" oninput="updateAllAmounts()" style="width: 200px; background: #131D2E; border: 1px solid rgba(0,210,255,0.2); border-radius: 10px; padding: 10px 14px 10px 30px; font-size: 16px; font-weight: 700; color: #00D2FF; outline: none;" />
                    </div>
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;" id="pbAmountButtons"></div>
            </div>'''
            
    if target in content:
        new_content = content.replace(target, HTML_NEW_SECTION.strip('\n'))
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Patched templates/index.html")
    else:
        print("Target not found.")

if __name__ == "__main__":
    patch_ui()
