from flask import Flask, render_template, render_template_string, jsonify, request
from mftool import Mftool
from datetime import datetime, timedelta
from functools import wraps
from flask_caching import Cache
from flask_socketio import SocketIO
import os
import requests
import threading
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 86400  # 24 hours
cache = Cache(app)

TASKS = {}  # In-memory store for background tasks

import database

@cache.memoize(timeout=86400)
def get_fund_raw_data(code):
    # Try fetching from local SQLite database first
    db_result = database.get_fund_from_db(code)
    if db_result:
        print(f"Loaded {code} from SQLite DB!")
        return db_result

    print(f"Fetching {code} from mfapi.in API...")
    resp = requests.get(f'https://api.mfapi.in/mf/{code}', timeout=12)
    resp.raise_for_status()
    mf_data = resp.json()
    meta = mf_data.get('meta', {})
    
    rating = 0
    try:
        import re
        scheme_name = meta.get('scheme_name', '')
        if scheme_name:
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', scheme_name.lower())
            search_id = "-".join(clean_name.split())
            g_resp = requests.get(f"https://groww.in/v1/api/data/mf/web/v1/scheme/search/{search_id}", timeout=5)
            if g_resp.ok:
                g_data = g_resp.json()
                rating = g_data.get('rating', 0)
    except Exception:
        pass
        
    # Save the newly fetched data into SQLite
    database.save_fund_data(code, meta, mf_data.get('data', []), rating)
        
    return mf_data, rating

import schedule
import time

def pre_load_funds():
    print("Starting background pre-load of popular funds to cache...")
    popular_funds = ["122639", "120586", "118989", "113373", "120716", "119609", "118968", "118987", "118222", "108466", "118991"]
    for code in popular_funds:
        try:
            get_fund_raw_data(code)
            print(f"Pre-loaded {code}")
        except Exception as e:
            print(f"Failed to pre-load {code}: {e}")

def start_scheduler():
    schedule.every().day.at("23:30").do(pre_load_funds)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler thread
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()

mf = Mftool()

API_KEY = "POWER_BI_KEY_2026"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided = request.headers.get('x-api-key') or request.args.get('api_key')
        if provided:
            if provided != API_KEY:
                return jsonify({"error": "Invalid API Key"}), 401
            return f(*args, **kwargs)
            
        referer = request.headers.get('Referer', '')
        if request.host in referer or "127.0.0.1" in referer or "localhost" in referer:
            return f(*args, **kwargs)
            
        return jsonify({"error": "Unauthorized. Please provide ?api_key= in the URL."}), 401
    return decorated_function
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Pro Mutual Fund Analytics</title>
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/static/logo.png?v=3">
    <link rel="apple-touch-icon" href="/static/logo.png?v=3">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: #0B0E14;
            color: #E2E8F0;
            overflow: hidden;
            position: relative;
        }
        /* Animated Background Blobs */
        .blob {
            position: absolute;
            filter: blur(80px);
            z-index: -1;
            opacity: 0.6;
            animation: float 10s infinite ease-in-out alternate;
        }
        .blob-1 {
            width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(59,130,246,0.8) 0%, rgba(59,130,246,0) 70%);
            top: -100px; left: -100px;
        }
        .blob-2 {
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(139,92,246,0.6) 0%, rgba(139,92,246,0) 70%);
            bottom: -150px; right: -100px;
            animation-delay: -5s;
        }
        .blob-3 {
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(14,165,233,0.5) 0%, rgba(14,165,233,0) 70%);
            top: 40%; left: 60%;
            animation-duration: 12s;
        }
        
        @keyframes float {
            0% { transform: translateY(0) scale(1); }
            100% { transform: translateY(-30px) scale(1.1); }
        }

        .login-container {
            background: rgba(16, 24, 39, 0.4);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            padding: 48px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
            animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            z-index: 10;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 40px;
        }
        .logo-icon {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            position: relative;
            background: transparent;
            overflow: hidden;
        }
        .logo-icon img { width: 100%; height: 100%; object-fit: cover; }
        .logo-text h1 { font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; }
        .logo-text p { font-size: 12px; color: #94A3B8; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 4px; }
        
        .form-group { margin-bottom: 24px; position: relative; }
        .form-group label { 
            display: block; 
            font-size: 12px; 
            font-weight: 600; 
            color: #94A3B8; 
            margin-bottom: 8px; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .form-control {
            width: 100%;
            padding: 14px 16px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            color: #FFFFFF;
            font-size: 15px;
            font-family: inherit;
            outline: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .form-control::placeholder { color: #475569; }
        .form-control:focus { 
            background: rgba(15, 23, 42, 0.8);
            border-color: #3B82F6; 
            box-shadow: 0 0 0 4px rgba(59,130,246,0.15); 
            transform: translateY(-2px);
        }
        
        .captcha-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 30px;
        }
        .captcha-box {
            background: linear-gradient(135deg, #1E293B, #0F172A);
            padding: 12px 20px;
            border-radius: 12px;
            border: 1px dashed rgba(255,255,255,0.2);
            font-size: 24px;
            font-weight: 800;
            color: #3B82F6;
            letter-spacing: 6px;
            user-select: none;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .refresh-btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: #94A3B8;
            padding: 14px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .refresh-btn:hover { background: rgba(255,255,255,0.1); color: #FFFFFF; transform: rotate(15deg); }
        .refresh-btn svg { width: 20px; height: 20px; }
        
        .login-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #3B82F6, #8B5CF6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }
        .login-btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: all 0.5s;
        }
        .login-btn:hover::before { left: 100%; }
        .login-btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 25px rgba(59,130,246,0.5); 
        }
        .login-btn:active { transform: translateY(0); }
        
        .footer-links {
            display: flex;
            justify-content: center;
        }
        .footer-links a {
            color: #94A3B8;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: color 0.2s;
        }
        .footer-links a:hover { color: #FFFFFF; }
        
        #error-msg {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #FCA5A5;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 20px;
            text-align: center;
            display: none;
            animation: shake 0.4s;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
    </style>
</head>
<body>
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <div class="login-container">
        <div class="logo">
            <div class="logo-icon">
                <img src="/static/logo.png" alt="Logo">
            </div>
            <div class="logo-text">
                <h1>Pro Mutual Fund</h1>
                <p>Institutional Grade Portfolio Builder</p>
            </div>
        </div>
        <form id="loginForm" onsubmit="handleLogin(event)">
            <div class="form-group">
                <label>Partner ID</label>
                <input type="text" id="partnerId" class="form-control" placeholder="e.g. PRO2026" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="password" class="form-control" placeholder="Enter your password" required>
            </div>
            <div id="error-msg"></div>
            <div class="captcha-row">
                <div class="captcha-box" id="captchaText">32330</div>
                <button type="button" class="refresh-btn" onclick="generateCaptcha()" title="Refresh Captcha">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                </button>
                <input type="text" id="captchaInput" class="form-control" placeholder="Enter Captcha" required style="flex:1;">
            </div>
            <button type="submit" class="login-btn">Secure Login</button>
            <div class="footer-links">
                <a href="#" onclick="handleForgotPassword(event)">Forgot Your Password?</a>
            </div>
        </form>
    </div>
    <script>
        let currentCaptcha = "";
        function generateCaptcha() {
            currentCaptcha = Math.floor(10000 + Math.random() * 90000).toString();
            document.getElementById('captchaText').textContent = currentCaptcha;
            document.getElementById('captchaInput').value = "";
        }
        
        function handleForgotPassword(e) {
            e.preventDefault();
            const errorMsg = document.getElementById('error-msg');
            errorMsg.textContent = "Please contact the system administrator to reset your password. (Default: PRO2026 / admin)";
            errorMsg.style.display = 'block';
            errorMsg.style.color = '#60A5FA';
            errorMsg.style.background = 'rgba(59, 130, 246, 0.1)';
            errorMsg.style.borderColor = 'rgba(59, 130, 246, 0.3)';
            errorMsg.style.animation = 'none'; // remove shake
        }
        
        function handleLogin(e) {
            e.preventDefault();
            const partnerId = document.getElementById('partnerId').value;
            const password = document.getElementById('password').value;
            const input = document.getElementById('captchaInput').value;
            const errorMsg = document.getElementById('error-msg');
            
            errorMsg.style.display = 'none';

            if (partnerId !== "PRO2026" || password !== "admin") {
                errorMsg.textContent = "Invalid Partner ID or Password.";
                errorMsg.style.display = 'block';
                return;
            }

            if (input !== currentCaptcha) {
                errorMsg.textContent = "Incorrect Captcha. Please try again.";
                errorMsg.style.display = 'block';
                generateCaptcha();
                return;
            }
            window.location.href = "/dashboard";
        }
        
        // Initialize captcha
        generateCaptcha();
    </script>
</body>
</html>
"""



def normalize_scheme_category(raw_category, scheme_name):
    cat_lower = str(raw_category or '').lower()
    name_lower = str(scheme_name or '').lower()
    text = cat_lower + " " + name_lower
    
    if 'flexi cap' in text: return 'Flexi Cap'
    if 'multi cap' in text: return 'Multi Cap'
    if 'large cap' in text: return 'Large Cap'
    if 'mid cap' in text: return 'Mid Cap'
    if 'small cap' in text: return 'Small Cap'
    if 'elss' in text or 'tax' in text: return 'ELSS'
    if 'index' in text: return 'Index'
    if 'etf' in text: return 'ETF'
    if 'liquid' in text or 'overnight' in text or 'money market' in text: return 'Liquid'
    if 'balanced advantage' in text or 'baf' in text: return 'Balanced Advantage'
    if 'aggressive hybrid' in text: return 'Aggressive Hybrid'
    if 'conservative hybrid' in text: return 'Conservative Hybrid'
    if 'hybrid' in text or 'balanced' in text: return 'Hybrid'
    if 'debt' in text or 'bond' in text or 'gilt' in text or 'income' in text or 'short term' in text or 'long term' in text or 'duration' in text or 'floater' in text or 'psu' in text or 'corporate' in text or 'credit risk' in text: return 'Debt'
    if 'gold' in text or 'silver' in text: return 'Gold'
    if 'arbitrage' in text: return 'Arbitrage'
    if 'multi asset' in text: return 'Multi Asset'
    if 'dividend yield' in text: return 'Dividend Yield'
    if 'retirement' in text: return 'Retirement'
    if 'fund of fund' in text or ' fof ' in text or '- fof' in text: return 'Fund of Funds'
    if 'sector' in text or 'thematic' in text or 'consumption' in text or 'rural' in text or 'pharma' in text or 'tech' in text: return 'Sectoral/Thematic'
    if 'value' in text: return 'Value'
    if 'contra' in text: return 'Contra'
    if 'focused' in text: return 'Focused'
    if 'children' in text or 'child' in text: return 'Children'
    if 'equity savings' in text: return 'Equity Savings'
    if 'international' in text or 'global' in text or 'us equity' in text: return 'International'
    
    if raw_category and raw_category.strip().lower() not in ['other', 'other scheme', '', 'unknown']:
        if raw_category.strip().lower() != 'other scheme':
            return raw_category.strip().title()
            
    return 'Other'

@app.route('/')
def login():
    return render_template_string(LOGIN_HTML)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Mutual Fund Manager",
        "short_name": "MF App",
        "start_url": "/dashboard",
        "display": "standalone",
        "background_color": "#060A10",
        "theme_color": "#060A10",
        "icons": [
            {
                "src": "/static/logo.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/logo.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    })

@app.route('/sw.js')
def service_worker():
    sw = '''
    self.addEventListener('install', function(e) {
      self.skipWaiting();
    });
    self.addEventListener('fetch', function(e) {
      // Empty fetch handler to satisfy PWA install requirements
    });
    '''
    return app.response_class(sw, mimetype='application/javascript')

@app.route('/dashboard')
def dashboard():
    return render_template("index.html")

@app.route('/api/schemes')
@require_api_key
@cache.cached(timeout=86400)
def get_all_schemes():
    import os
    import json
    # Attempt to load from local file first to prevent Vercel being blocked by AMFI
    local_path = os.path.join(os.path.dirname(__file__), 'active_funds.json')
    if os.path.exists(local_path):
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                schemes_list = json.load(f)
                return jsonify(schemes_list)
        except Exception:
            pass

    import requests
    try:
        r = requests.get('https://www.amfiindia.com/spages/NAVAll.txt', timeout=5)
        lines = r.text.split('\n')
        schemes_list = []
        for line in lines:
            parts = line.split(';')
            if len(parts) >= 6 and parts[0].strip().isdigit():
                code = parts[0].strip()
                name = parts[3].strip()
                plan = parts[4].strip()
                opt = parts[5].strip()
                
                # Build full name
                full_name = name
                if plan and plan not in full_name:
                    full_name += f" - {plan}"
                if opt and opt not in full_name:
                    full_name += f" - {opt}"
                    
                schemes_list.append({"code": code, "name": full_name, "category": normalize_scheme_category('', full_name)})
        
        return jsonify(schemes_list)
    except Exception as e:
        # Fallback to mftool if direct fetch fails
        schemes_dict = mf.get_scheme_codes()
        schemes_list = [{"code": str(k), "name": v, "category": normalize_scheme_category('', v)} for k, v in schemes_dict.items() if str(k) != "Scheme Code"]
        return jsonify(schemes_list)

@app.route('/api/portfolio/generate', methods=['POST'])
def generate_portfolio():
    import concurrent.futures
    import numpy as np
    from datetime import datetime, timedelta
    
    try:
        data = request.get_json()
        portfolio_items = data.get('portfolio', [])
        investment_amount = data.get('investment_amount', 100000)
        investment_type = data.get('investment_type', 'lumpsum')
        duration_years = int(data.get('duration_years', 5))
        
        if not portfolio_items or len(portfolio_items) < 1:
            return jsonify({'error': 'Add at least 1 fund'}), 400
        
        total_alloc = sum(
            f.get('allocation_pct', 0) for f in portfolio_items
        )
        if abs(total_alloc - 1.0) > 0.02:
            return jsonify({
                'error': f'Allocations must sum to 100%. '
                         f'Got {total_alloc*100:.1f}%'
            }), 400

        # ── Step 1: Parallel fetch NAV data ──────────────────
        def fetch_fund_data(item):
            code = item['code']
            mf_data, rating = get_fund_raw_data(code)
            
            meta = mf_data['meta']
            nav_list = mf_data['data']  # [{date, nav}, ...]
            
            nav_dict = {}
            for entry in nav_list:
                try:
                    d = datetime.strptime(
                        entry['date'], '%d-%m-%Y'
                    )
                    nav_dict[d] = float(entry['nav'])
                except:
                    pass

            return {
                'code': code,
                'name': meta.get('scheme_name', 'Unknown'),
                'amc': meta.get('fund_house', 'Unknown'),
                'category': normalize_scheme_category(meta.get('scheme_category', 'Other'), meta.get('scheme_name', '')),
                'allocation': item['allocation_pct'],
                'nav_dict': nav_dict,
                'latest_nav': float(nav_list[0]['nav']) if nav_list else 0,
                'latest_nav_date': nav_list[0]['date'] if nav_list else '',
                'latest_date': nav_list[0]['date'] 
                               if nav_list else 'N/A',
                'rating': rating
            }
        
        fund_data = []
        errors = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=6
        ) as ex:
            futures = {
                ex.submit(fetch_fund_data, item): item
                for item in portfolio_items
            }
            for fut in concurrent.futures.as_completed(futures):
                try:
                    fund_data.append(fut.result())
                except Exception as e:
                    errors.append(str(e))
        
        if errors:
            return jsonify({
                'error': f'Failed to fetch: {errors[0]}'
            }), 500

        # ── Step 2: Date alignment (Forward fill missing NAVs) ────────
        all_dates = set()
        for f in fund_data:
            all_dates.update(f['nav_dict'].keys())
        all_dates = sorted(list(all_dates))
        
        if len(all_dates) < 30:
            return jsonify({'error': 'Insufficient history (< 30 days).'}), 400
            
        target_start_date = all_dates[-1] - timedelta(days=duration_years*365)
        filtered_dates = [d for d in all_dates if d >= target_start_date]
        if not filtered_dates:
            filtered_dates = all_dates
            
        for f in fund_data:
            f_dates = sorted(f['nav_dict'].keys())
            ff_navs = {}
            current_nav = None
            f_idx = 0
            n_fdates = len(f_dates)
            for d in filtered_dates:
                while f_idx < n_fdates and f_dates[f_idx] <= d:
                    current_nav = f['nav_dict'][f_dates[f_idx]]
                    f_idx += 1
                ff_navs[d] = current_nav
            f['ff_nav_dict'] = ff_navs

        valid_dates = []
        for d in filtered_dates:
            if all(f['ff_nav_dict'][d] is not None for f in fund_data):
                valid_dates.append(d)
                
        if not valid_dates:
            return jsonify({'error': 'Funds do not overlap in the given timeframe.'}), 400
            
        sorted_dates = valid_dates
        
        # ── Step 3: Weighted portfolio timeline ───────────────
        portfolio_values = []
        total_invested_timeline = []
        current_invested = 0
        cash_flows = []
        
        if investment_type == 'sip':
            fund_units = {f['code']: 0.0 for f in fund_data}
            last_invest_month = None
            for d in sorted_dates:
                month_key = (d.year, d.month)
                if month_key != last_invest_month:
                    current_invested += investment_amount
                    cash_flows.append((d, -investment_amount))
                    for f in fund_data:
                        nav = f['ff_nav_dict'][d]
                        allocated_amt = investment_amount * f['allocation']
                        fund_units[f['code']] += allocated_amt / nav
                    last_invest_month = month_key
                
                pv = sum(fund_units[f['code']] * f['ff_nav_dict'][d] for f in fund_data)
                portfolio_values.append(pv)
                total_invested_timeline.append(current_invested)
                
            total_invested_final = current_invested
            cash_flows.append((sorted_dates[-1], portfolio_values[-1]))
        else:
            base_navs = {f['code']: f['ff_nav_dict'][sorted_dates[0]] for f in fund_data}
            total_invested_final = investment_amount
            for d in sorted_dates:
                pv = sum((f['ff_nav_dict'][d] / base_navs[f['code']]) * f['allocation'] * investment_amount for f in fund_data)
                portfolio_values.append(pv)
                total_invested_timeline.append(investment_amount)
            cash_flows = [(sorted_dates[0], -investment_amount), (sorted_dates[-1], portfolio_values[-1])]
        
        # ── Step 4: CAGR & XIRR calculations ─────────────────────────
        def get_cagr(values, dates, years):
            target = dates[-1] - timedelta(days=int(years*365.25))
            closest_idx = min(range(len(dates)), key=lambda i: abs(dates[i] - target))
            actual_yrs = (dates[-1] - dates[closest_idx]).days / 365.25
            if actual_yrs < 0.4: return None
            sv, ev = values[closest_idx], values[-1]
            if sv <= 0: return None
            return round(((ev / sv) ** (1 / actual_yrs) - 1) * 100, 2)
            
        def calc_xirr(cfs, guess=0.1, max_iter=100, tol=1e-6):
            if not cfs: return None
            def xnpv(rate):
                if rate <= -1.0: return float('inf')
                return sum([cf / (1 + rate)**((d - cfs[0][0]).days / 365.25) for d, cf in cfs])
            def dxnpv(rate):
                if rate <= -1.0: return 0
                return sum([-cf * ((d - cfs[0][0]).days / 365.25) / (1 + rate)**(((d - cfs[0][0]).days / 365.25) + 1) for d, cf in cfs])
            rate = guess
            for _ in range(max_iter):
                f_val = xnpv(rate)
                f_deriv = dxnpv(rate)
                if abs(f_val) < tol: return rate
                if f_deriv == 0: return None
                rate -= f_val / f_deriv
            return rate
        
        import math
        def s_float(v):
            if v is None: return None
            try:
                v = float(v)
                if math.isnan(v) or math.isinf(v): return None
                return v
            except:
                return None

        cagr_1y = s_float(get_cagr(portfolio_values, sorted_dates, 1))
        cagr_3y = s_float(get_cagr(portfolio_values, sorted_dates, 3))
        cagr_5y = s_float(get_cagr(portfolio_values, sorted_dates, 5))
        
        xirr_val = None
        if len(cash_flows) > 1:
            try:
                x = calc_xirr(cash_flows)
                if x is not None: xirr_val = round(x * 100, 2)
            except: pass

        current_value = s_float(round(portfolio_values[-1], 2))
        abs_return = s_float(round(((current_value / total_invested_final) - 1.0) * 100, 2)) if total_invested_final > 0 else 0
        abs_gain = round(current_value - total_invested_final, 2)
        
        # ── Step 5: Advanced Risk Metrics ─────────────────────
        pv_arr = np.array(portfolio_values)
        with np.errstate(divide='ignore', invalid='ignore'):
            daily_returns = np.diff(pv_arr) / pv_arr[:-1]
            volatility = float(np.std(daily_returns) * np.sqrt(252) * 100)
            volatility = s_float(round(volatility, 2)) if volatility is not None else None
        
        risk_free = 0.06
        port_return_ann = xirr_val/100 if xirr_val is not None else (cagr_3y/100 if cagr_3y else 0)
        
        if volatility and volatility > 0:
            sharpe = s_float(round((port_return_ann - risk_free) / (volatility / 100), 2))
        else:
            sharpe = None
            
        peak = pv_arr[0]
        max_dd = 0.0
        for v in pv_arr:
            if v > peak: peak = v
            if peak > 0:
                dd = (peak - v) / peak
                if dd > max_dd: max_dd = dd
        max_drawdown = s_float(round(max_dd * 100, 2))
        
        # ── Step 6: Per-fund risk/return scatter data ─────────
        scatter_data = []
        for f in fund_data:
            f_dates = sorted(f['nav_dict'].keys())
            f_vals = [f['nav_dict'][d] for d in f_dates]
            
            # 3Y CAGR for this fund
            f_cagr = s_float(get_cagr(f_vals, f_dates, 3))
            
            # Volatility for this fund
            f_arr = np.array(f_vals)
            f_vol = None
            if len(f_arr) > 2:
                with np.errstate(divide='ignore', invalid='ignore'):
                    f_dr = np.diff(f_arr) / f_arr[:-1]
                    f_vol_raw = float(np.std(f_dr) * np.sqrt(252) * 100)
                    f_vol = s_float(round(f_vol_raw, 2))
            
            scatter_data.append({
                'code': f['code'],
                'name': f['name'],
                'allocation': round(f['allocation'] * 100),
                'risk': f_vol,
                'return_3y': f_cagr,
                'category': f['category']
            })
        
        # ── Step 7: Asset Allocation & Scheme Category ────────
        asset_map = {'Equity': 0.0, 'Debt': 0.0, 'Other': 0.0}
        scheme_map = {}
        weighted_expense_ratio = 0.0
        
        for f in fund_data:
            c = normalize_scheme_category(f['category'], f['name'])
            cat = c.lower()
            alloc_pct = f['allocation'] * 100
            
            scheme_map[c] = round(scheme_map.get(c, 0) + alloc_pct, 2)
            
            # Asset Allocation (underlying)
            eq_exp = 0.0
            dt_exp = 0.0
            ot_exp = 0.0
            
            # Default heuristics if underlying data unavailable
            if 'equity' in cat or 'elss' in cat or 'index' in cat or 'etf' in cat:
                eq_exp = 100.0
            elif 'debt' in cat or 'liquid' in cat or 'overnight' in cat or 'gilt' in cat:
                dt_exp = 100.0
            elif 'gold' in cat or 'commodity' in cat or 'silver' in cat:
                ot_exp = 100.0
            elif 'hybrid' in cat or 'balanced' in cat or 'aggressive' in cat:
                eq_exp = 65.0
                dt_exp = 35.0
            else:
                eq_exp = 100.0
            
            asset_map['Equity'] += (eq_exp / 100.0) * alloc_pct
            asset_map['Debt'] += (dt_exp / 100.0) * alloc_pct
            asset_map['Other'] += (ot_exp / 100.0) * alloc_pct
            
            # Expense Ratio (fallback if missing)
            er = f.get('expense_ratio') or 0.0
            weighted_expense_ratio += (er * f['allocation'])

        # Normalize Asset Map just in case
        total_asset = sum(asset_map.values())
        if total_asset > 0:
            for k in asset_map:
                asset_map[k] = round((asset_map[k] / total_asset) * 100, 2)
        
        # Risk Calculation
        equity_exposure = asset_map.get('Equity', 0)
        risk_label = "Moderate"
        if equity_exposure > 80:
            risk_label = "High"
            if scheme_map.get('Small Cap', 0) > 20 or scheme_map.get('Mid Cap', 0) > 30:
                risk_label = "Very High"
        elif equity_exposure > 60:
            risk_label = "Moderately High"
        elif equity_exposure < 30:
            risk_label = "Low"
        elif equity_exposure < 50:
            risk_label = "Low to Moderate"
            
        risk_explanation = "Risk is driven primarily by equity exposure and capitalization allocation."
        
        # Portfolio Health
        health_observations = []
        if len(fund_data) >= 3:
            health_observations.append("✓ Good diversification across funds")
        else:
            health_observations.append("⚠ Consider adding more funds for diversification")
        
        if equity_exposure > 85:
            health_observations.append("⚠ High equity exposure")
        
        if scheme_map.get('Hybrid', 0) > 0:
            health_observations.append("⚠ Hybrid fund exposure needs underlying allocation analysis")
            
        portfolio_health = "Good" if len(fund_data) >= 3 and equity_exposure <= 85 else "Review Required"
        
        overlap_statement = "Overlap data unavailable"
        # ── Step 8: Sample timeline (max 365 points) ─────────
        step = max(1, len(sorted_dates) // 365)
        sampled_dates = sorted_dates[::step]
        sampled_values = portfolio_values[::step]
        
        # Ensure last point is included
        if sampled_dates[-1] != sorted_dates[-1]:
            sampled_dates.append(sorted_dates[-1])
            sampled_values.append(portfolio_values[-1])
        
        timeline = [
            {
                'date': d.strftime('%d-%m-%Y'),
                'value': round(v, 4)
            }
            for d, v in zip(sampled_dates, sampled_values)
        ]
        
        # ── Step 9: Per-fund individual CAGR ─────────────────
        funds_detail = []
        amc_map = {}
        for f in fund_data:
            amc_name = f.get('amc', 'Unknown AMC')
            amc_map[amc_name] = round(amc_map.get(amc_name, 0) + f['allocation'] * 100, 2)
            
            f_dates = sorted(f['nav_dict'].keys())
            f_vals = [f['nav_dict'][d] for d in f_dates]
            funds_detail.append({
                'code': f['code'],
                'name': f['name'],
                'amc': amc_name,
                'category': f['category'],
                'allocation_pct': round(f['allocation'] * 100),
                'allocation_inr': round(
                    investment_amount * f['allocation'], 2
                ),
                'latest_nav': f['latest_nav'],
                'latest_nav_date': f.get('latest_nav_date', ''),
                'rating': f.get('rating', 0),
                'cagr_1y': get_cagr(f_vals, f_dates, 1),
                'cagr_3y': get_cagr(f_vals, f_dates, 3),
                'cagr_5y': get_cagr(f_vals, f_dates, 5),
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_invested': total_invested_final,
                'current_value': current_value,
                'absolute_gain': abs_gain,
                'absolute_return': abs_return,
                'xirr': xirr_val,
                'cagr_1y': cagr_1y,
                'cagr_3y': cagr_3y,
                'cagr_5y': cagr_5y,
                'volatility': volatility,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'fund_count': len(fund_data),
                'total_amcs': len(amc_map),
                'expense_ratio': 'Data unavailable' if weighted_expense_ratio == 0 else round(weighted_expense_ratio, 2),
                'market_cap_allocation': 'Data unavailable',
                'risk_label': risk_label,
                'risk_explanation': risk_explanation,
                'health_status': portfolio_health,
                'health_observations': health_observations,
                'overlap': overlap_statement,
                'date_range': {
                    'start': sorted_dates[0].strftime('%d-%b-%Y'),
                    'end': sorted_dates[-1].strftime('%d-%b-%Y'),
                    'days': (sorted_dates[-1]-sorted_dates[0]).days
                }
            },
            'timeline': timeline,
            'asset_allocation': asset_map,
            'scheme_category': scheme_map,
            'amc_allocation': amc_map,
            'funds_detail': funds_detail,
            'scatter_data': scatter_data
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


PORTFOLIOS_FILE = 'saved_portfolios.json'

@app.route('/api/portfolio/save', methods=['POST'])
def save_portfolio():
    try:
        data = request.get_json()
        import json
        if os.path.exists(PORTFOLIOS_FILE):
            with open(PORTFOLIOS_FILE, 'r') as f:
                portfolios = json.load(f)
        else:
            portfolios = []
        
        new_portfolio = {
            'id': len(portfolios) + 1,
            'name': data.get('name', f'Portfolio {len(portfolios)+1}'),
            'created_at': datetime.now().strftime('%d %b %Y, %H:%M'),
            'investment_amount': data.get('investment_amount', 100000),
            'funds': data.get('funds', []),
            'summary': data.get('summary', {})
        }
        
        portfolios.insert(0, new_portfolio)
        # Keep max 20 saved portfolios
        portfolios = portfolios[:20]
        
        with open(PORTFOLIOS_FILE, 'w') as f:
            json.dump(portfolios, f, indent=2)
        
        return jsonify({
            'success': True, 
            'portfolio_id': new_portfolio['id'],
            'message': 'Portfolio saved successfully!'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio/list', methods=['GET'])
def list_portfolios():
    try:
        import json
        if not os.path.exists(PORTFOLIOS_FILE):
            return jsonify({'portfolios': []})
        with open(PORTFOLIOS_FILE, 'r') as f:
            portfolios = json.load(f)
        for p in portfolios:
            p.pop('timeline', None)
        return jsonify({'portfolios': portfolios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/delete/<int:pid>', methods=['DELETE'])
def delete_portfolio(pid):
    try:
        import json
        if not os.path.exists(PORTFOLIOS_FILE):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        with open(PORTFOLIOS_FILE, 'r') as f:
            portfolios = json.load(f)
        
        initial_len = len(portfolios)
        portfolios = [p for p in portfolios if p.get('id') != pid]
        
        if len(portfolios) == initial_len:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
            
        with open(PORTFOLIOS_FILE, 'w') as f:
            json.dump(portfolios, f, indent=2)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def run_ai_task(task_id, api_key, inv_type, inv_amt, duration_years, risk_level):
    import requests, json, re
    try:
        # Emit started event
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'AI analysis started...'})
        
        prompt = f"""You are an expert financial advisor. The user wants an optimal, HIGHLY DIVERSIFIED mutual fund portfolio.
The user is planning a {inv_type.upper()} investment of ₹{inv_amt} for a duration of {duration_years} years.
Their risk tolerance is {risk_level.upper()}.
If risk tolerance is LOW, heavily favor Debt and Hybrid funds.
If risk tolerance is HIGH, heavily favor pure Equity funds (Small/Mid/Flexi Cap).
If risk tolerance is MEDIUM, balance between Large Cap/Flexi Cap Equity and Hybrid funds.

CRITICAL RULE on number of funds based on investment amount:
- If investment amount is less than ₹5000, select ONLY 3 to 4 funds.
- If investment amount is between ₹5000 and ₹15000, select 5 to 7 funds.
- If investment amount is above ₹15000, select 7 to 9 funds.

Based on this profile, suggest a portfolio of top-performing DIRECT PLAN mutual funds in India.
Use your own knowledge of the Indian mutual fund market to pick the best funds. 
Assign percentage weights (must total exactly 100).
Respond ONLY with a valid JSON array. Do not include any other text, markdown formatting, or explanation.
Format: [{{"name": "Parag Parikh Flexi Cap Fund Direct Growth", "category": "Flexi Cap", "weight": 40}}, ...]
"""
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'Sending prompt to Cohere...'})
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'model': 'command-r-plus-08-2024',
            'message': prompt,
            'temperature': 0.7
        }
        resp = requests.post('https://api.cohere.com/v1/chat', headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            TASKS[task_id] = {'state': 'FAILURE', 'error': f"Cohere API Error: {resp.text}"}
            socketio.emit('task_update', {'task_id': task_id, 'state': 'FAILURE', 'error': f"Cohere API Error: {resp.text}"})
            return
            
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'Processing AI response & searching fund codes...'})
        result_text = resp.json().get('text', '').strip()
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'\[.*\]', result_text, re.DOTALL)
        if match:
            result_text = match.group(0)
            
        ai_funds = json.loads(result_text)
        
        funds = []
        for f in ai_funds:
            try:
                search_q = f['name'].replace(' ', '%20')
                search_resp = requests.get(f"https://api.mfapi.in/mf/search?q={search_q}", timeout=5)
                results = search_resp.json()
                if results:
                    best = results[0]
                    funds.append({
                        'code': str(best['schemeCode']),
                        'name': best['schemeName'],
                        'weight': f.get('weight', 0),
                        'category': f.get('category', 'Equity'),
                        'allocation_pct': f.get('weight', 0) / 100
                    })
            except Exception as e:
                print("Failed to search fund:", f['name'], e)
                
        if not funds:
            raise Exception("AI did not return any valid fund names that could be found in the API.")
                
        TASKS[task_id] = {'state': 'SUCCESS', 'funds': funds}
        socketio.emit('task_update', {'task_id': task_id, 'state': 'SUCCESS', 'funds': funds})
    except Exception as e:
        TASKS[task_id] = {'state': 'FAILURE', 'error': str(e)}
        socketio.emit('task_update', {'task_id': task_id, 'state': 'FAILURE', 'error': str(e)})

@app.route('/api/portfolio/ai-generate', methods=['POST'])
def ai_generate_portfolio():
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        if not api_key:
            return jsonify({'success': False, 'error': 'Cohere API Key is required.'}), 400
            
        task_id = str(uuid.uuid4())
        TASKS[task_id] = {'state': 'PENDING'}
        
        thread = threading.Thread(target=run_ai_task, args=(
            task_id, api_key, data.get('type', 'lumpsum'), 
            data.get('amount', 100000), data.get('years', 5), data.get('risk', 'medium')
        ))
        thread.start()
        
        return jsonify({'success': True, 'task_id': task_id}), 202
    except Exception as e:
        return jsonify({'success': False, 'error': f"AI generation enqueue failed: {str(e)}"}), 500

@app.route('/api/portfolio/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'state': 'FAILURE', 'success': False, 'error': 'Task not found'}), 404
        
    if task['state'] == 'PENDING':
        return jsonify({'state': 'PENDING', 'status': 'Pending...'})
    elif task['state'] == 'SUCCESS':
        return jsonify({'state': 'SUCCESS', 'success': True, 'funds': task['funds'], 'name': 'AI Optimal Growth Portfolio'})
    else:
        return jsonify({'state': 'FAILURE', 'success': False, 'error': task.get('error', 'Unknown error')})


@app.route('/api/quote/<code>')
@require_api_key
def get_quote(code):
    try:
        # Avoid AMFI block on Vercel by fetching from mfapi.in via get_scheme_historical_nav
        history = mf.get_scheme_historical_nav(code)
        if not history or 'data' not in history or not history['data']:
            return jsonify({"error": "Scheme not found"}), 404
            
        latest_data = history['data'][0]
        quote = {
            "scheme_code": code,
            "scheme_name": history.get('scheme_name', ''),
            "nav": latest_data.get('nav', '0'),
            "date": latest_data.get('date', '')
        }
        details = history
        
        scraped_data = {}
        try:
            import urllib.parse, requests, json
            from bs4 import BeautifulSoup
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://groww.in",
                "Referer": "https://groww.in/"
            }
            
            scheme_name = quote.get('scheme_name', '')
            # Clean up the name for a better search match (take everything before the first hyphen)
            search_query = scheme_name.split('-')[0].strip()
            if not search_query:
                search_query = scheme_name.strip()
            
            # 1. Get search_id
            search_url = f"https://groww.in/v1/api/search/v1/entity?app=false&entity_type=scheme&page=0&query={urllib.parse.quote(search_query)}&size=5"
            r_search = requests.get(search_url, headers=headers, timeout=4)
            search_id = None
            if r_search.status_code == 200:
                data = r_search.json()
                
                ignore_words = {'fund', 'plan', 'direct', 'growth', 'regular', 'option', 'scheme'}
                q_words = [w.lower() for w in search_query.split() if len(w) > 2 and w.lower() not in ignore_words]
                
                for item in data.get('content', []):
                    if item.get('entity_type') == 'Scheme':
                        title = item.get('title', item.get('scheme_name', '')).lower()
                        if q_words:
                            # Require at least the first significant word (usually AMC) to match
                            if q_words[0] in title:
                                search_id = item.get('search_id')
                                break
                        else:
                            search_id = item.get('search_id')
                            break
            
            # 2. Fetch from new Groww API
            if search_id:
                api_url = f"https://groww.in/v1/api/data/mf/web/v1/scheme/search/{search_id}"
                r_api = requests.get(api_url, headers=headers, timeout=4)
                if r_api.status_code == 200:
                    page_data = r_api.json()
                    
                    scraped_data['expense_ratio'] = page_data.get('expense_ratio')
                    scraped_data['aum'] = page_data.get('aum')
                    scraped_data['fund_manager'] = page_data.get('fund_manager')
                    
                    # Manual overrides for known stale third-party data
                    if 'Sundaram Small Cap' in scheme_name:
                        scraped_data['fund_manager'] = 'Rohit Seksaria'
                    
                    if 'HDFC Balanced Advantage' in scheme_name:
                        scraped_data['fund_manager'] = ['Anil Bamboli (Debt)', 'Gopal Agrawal & Srinivasan Ramamurthy (Equity)', 'Arun Agarwal', 'Nandita Menezes', 'Dhruv Muchhal']
                        scraped_data['aum'] = '107295'
                        if 'Regular' in scheme_name:
                            scraped_data['expense_ratio'] = '1.30'
                        
                    scraped_data['exit_load'] = page_data.get('exit_load')
                    scraped_data['risk'] = page_data.get('risk')
                    scraped_data['min_sip'] = page_data.get('min_sip_investment')
                    scraped_data['min_lum'] = page_data.get('min_investment_amount')
                    scraped_data['rating'] = page_data.get('groww_rating')
                    
                    # Normalize holdings data (handles both array and dict formats from Groww API)
                    raw_holdings = page_data.get('holdings') or []
                    clean_holdings = []
                    for h_item in raw_holdings:
                        if isinstance(h_item, (list, tuple)) and len(h_item) >= 3:
                            h_name = str(h_item[2]).strip() if h_item[2] else ''
                            h_weight = h_item[8] if len(h_item) > 8 else (h_item[7] if len(h_item) > 7 else '')
                            h_sector = str(h_item[3]).strip() if len(h_item) > 3 and h_item[3] else ''
                            if h_name and h_name.lower() not in ('none', 'null', 'stock', 'unknown', ''):
                                clean_holdings.append({'company_name': h_name, 'corpus_per': h_weight, 'sector': h_sector})
                        elif isinstance(h_item, dict):
                            h_name = (h_item.get('company_name') or h_item.get('companyName') or h_item.get('stock_name') or h_item.get('name') or '').strip()
                            h_weight = h_item.get('corpus_per') if h_item.get('corpus_per') is not None else (h_item.get('corpusPer') or h_item.get('weight') or h_item.get('allocation'))
                            h_sector = (h_item.get('sector_name') or h_item.get('sectorName') or h_item.get('sector') or '').strip()
                            if h_name and h_name.lower() not in ('none', 'null', 'stock', 'unknown', ''):
                                clean_holdings.append({'company_name': h_name, 'corpus_per': h_weight, 'sector': h_sector})
                    scraped_data['holdings'] = clean_holdings
                    scraped_data['sectors'] = page_data.get('sectors')
        except Exception as e:
            print("Scraping Error:", e)
            pass
            
        return jsonify({"quote": quote, "details": details, "scraped": scraped_data})
    except Exception as e:
        import traceback
        print("Backend Error:", traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/all-funds')
@require_api_key
def get_all_funds():
    import json
    try:
        with open('scheme_codes.json', 'r') as f:
            data = json.load(f)
        # Format for Power BI: list of objects instead of a dictionary
        funds_list = [{"code": k, "name": v} for k, v in data.items()]
        return jsonify(funds_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<code>')
@require_api_key
def get_history(code):
    history = mf.get_scheme_historical_nav(code)
    if not history or 'data' not in history: return jsonify({"error": "History not found"}), 404
    return jsonify(history)

@app.route('/api/advanced/<code>')
@require_api_key
def get_advanced(code):
    try:
        import numpy as np
        history = mf.get_scheme_historical_nav(code)
        if not history or 'data' not in history or not isinstance(history['data'], list): return jsonify({})
        data = history['data']
        if len(data) == 0: return jsonify({})

        parsed_data = []
        for row in data:
            try:
                d = datetime.strptime(row['date'], '%d-%m-%Y')
                nav = float(row['nav'])
                parsed_data.append((d, nav))
            except: pass
                
        if not parsed_data: return jsonify({})
        parsed_data.sort(key=lambda x: x[0], reverse=True) # newest first
        current_date, current_nav = parsed_data[0]
        
        def get_return(years):
            target_date = current_date - timedelta(days=365 * years)
            closest_nav = next((nav for d, nav in parsed_data if d <= target_date), None)
            if closest_nav and closest_nav > 0:
                ret = (current_nav / closest_nav - 1) * 100 if years == 1 else ((current_nav / closest_nav) ** (1 / years) - 1) * 100
                return round(ret, 2)
            return None

        r1, r3, r5 = get_return(1), get_return(3), get_return(5)
        
        high_52 = history.get('52_week_high')
        low_52 = history.get('52_week_low')
        if not high_52 or not low_52:
            one_year_ago = current_date - timedelta(days=365)
            last_year_navs = [nav for d, nav in parsed_data if d >= one_year_ago]
            if last_year_navs: high_52, low_52 = max(last_year_navs), min(last_year_navs)

        oldest_date = parsed_data[-1][0]
        age_years = round((current_date - oldest_date).days / 365.25, 1)

        # Chronological order (oldest to newest) for risk metric calculations
        chrono_navs = [nav for _, nav in reversed(parsed_data)]
        volatility = None
        sharpe_ratio = None
        sortino_ratio = None
        max_drawdown = 0.0
        beta = 1.0

        if len(chrono_navs) >= 15:
            # 1. Volatility (Annualized standard deviation of daily log returns over past year / available)
            prices = np.array(chrono_navs[-365:]) if len(chrono_navs) >= 365 else np.array(chrono_navs)
            daily_returns = np.diff(prices) / prices[:-1]
            std_daily = float(np.std(daily_returns))
            if std_daily > 0:
                volatility = round(std_daily * np.sqrt(252) * 100, 2)
                
                # 2. Sharpe Ratio (using India risk-free rate 6.5%)
                rf = 6.5
                cagr_baseline = r1 if r1 is not None else (r3 if r3 is not None else 12.0)
                sharpe_ratio = round((cagr_baseline - rf) / volatility, 2)
                
                # 3. Sortino Ratio (downside deviation)
                neg_returns = daily_returns[daily_returns < 0]
                if len(neg_returns) > 0:
                    downside_std = float(np.std(neg_returns)) * np.sqrt(252) * 100
                    if downside_std > 0:
                        sortino_ratio = round((cagr_baseline - rf) / downside_std, 2)
                if sortino_ratio is None and sharpe_ratio is not None:
                    sortino_ratio = round(sharpe_ratio * 1.3, 2)
                    
                # 4. Beta (normalized vs broad market Nifty 50 avg annual volatility ~14.2%)
                beta = round(volatility / 14.2, 2)

            # 5. Maximum Drawdown across the entire historical period
            peak = chrono_navs[0]
            max_dd = 0.0
            for p in chrono_navs:
                if p > peak: peak = p
                if peak > 0:
                    dd = (peak - p) / peak
                    if dd > max_dd: max_dd = dd
            max_drawdown = round(max_dd * 100, 2)

        return jsonify({
            "return_1yr": r1,
            "return_3yr": r3,
            "return_5yr": r5,
            "high_52": round(high_52, 2) if high_52 else None,
            "low_52": round(low_52, 2) if low_52 else None,
            "fund_age": age_years,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "sortino_ratio": sortino_ratio,
            "beta": beta
        })
    except Exception as e:
        print("Advanced Error:", e)
        return jsonify({"error": str(e)}), 404

@app.route('/api/all-in-one/<code>')
@require_api_key
def get_all_in_one(code):
    try:
        # Fetch the base quote and details
        quote_response = get_quote(code).get_json()
        if "error" in quote_response:
            return jsonify(quote_response), 404
            
        # Fetch history
        history_response = get_history(code).get_json()
        
        # Fetch advanced metrics
        advanced_response = get_advanced(code).get_json()
        
        # Combine everything into a single JSON object
        return jsonify({
            "quote": quote_response.get("quote", {}),
            "scraped": quote_response.get("scraped", {}),
            "advanced": advanced_response,
            "history": history_response.get("data", [])
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/all-in-one/bulk')
@require_api_key
def get_all_in_one_bulk():
    codes_str = request.args.get('codes', '')
    if not codes_str:
        return jsonify({"error": "Please provide comma-separated codes in the URL like ?codes=122639,120586&api_key=..."}), 400
        
    codes = [c.strip() for c in codes_str.split(',') if c.strip()]
    if len(codes) > 20:
        return jsonify({"error": "Please request a maximum of 20 funds at a time to prevent server timeouts."}), 400
        
    results = []
    for code in codes:
        try:
            q_res = get_quote(code).get_json()
            if "error" in q_res: continue
            
            h_res = get_history(code).get_json()
            a_res = get_advanced(code).get_json()
            
            results.append({
                "code": code,
                "quote": q_res.get("quote", {}),
                "scraped": q_res.get("scraped", {}),
                "advanced": a_res,
                "history": h_res.get("data", [])
            })
        except Exception as e:
            print(f"Error fetching {code}: {e}")
            pass
            
    return jsonify(results)

    # The old portfolio endpoint is removed.

@app.route('/api/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    from services.portfolio import calculate_portfolio_metrics
    data = request.json
    funds = data.get('funds', [])
    allocation = data.get('allocation', {})
    investment_details = data.get('investment_details', {})
    
    result = calculate_portfolio_metrics(funds, allocation, investment_details)
    return jsonify(result)

@app.route('/portfolio/report/<int:pid>')
def portfolio_report(pid):
    try:
        import json
        if not os.path.exists(PORTFOLIOS_FILE):
            return "No portfolios found", 404
        with open(PORTFOLIOS_FILE, 'r') as f:
            portfolios = json.load(f)
        
        portfolio = next((p for p in portfolios if p.get('id') == pid), None)
        if not portfolio:
            return "Portfolio not found", 404
            
        return render_template('portfolio_report.html', portfolio=portfolio)
    except Exception as e:
        return str(e), 500

AI_INTERVIEWER_PREAMBLE = """
You are Aria, a friendly and professional AI financial advisor 
for Pro Mutual Fund Analytics. Your ONLY job right now is to 
conduct a quick 4-question onboarding interview to understand 
the user's investment profile, then build them a personalized 
mutual fund portfolio.

## YOUR PERSONALITY:
- Warm, encouraging, and professional
- Use simple language — avoid jargon
- Celebrate when user provides information (e.g., "Great choice!")
- Keep responses SHORT (2-3 lines max per message)
- Add relevant emojis to make it feel friendly

## THE 4 DATA POINTS YOU MUST COLLECT:
1. Investment TYPE → SIP (monthly) or Lumpsum (one-time)
2. Investment AMOUNT → In Indian Rupees (₹)
3. Investment HORIZON → Number of years (1-40)
4. Risk APPETITE → Conservative / Moderate / Aggressive

## CONVERSATION FLOW — Follow this EXACTLY:

### Opening Message (when user first opens chat):
"Hi! I'm Aria, your personal portfolio advisor 👋

I'll help you build a customized mutual fund portfolio in just 
4 quick questions. Ready to get started? 🚀"

### Step 1 — Ask Investment Type:
"First question: Would you prefer to invest a 
**fixed amount every month** (SIP) or make a 
**one-time large investment** (Lumpsum)?

💡 SIP is great for salaried individuals — builds discipline!
Lumpsum works well if you have a windfall or bonus."

### Step 2 — Ask Amount:
Based on their choice, ask appropriately:
- If SIP: "How much can you invest monthly? 
  Common amounts: ₹1,000 / ₹5,000 / ₹10,000 / ₹25,000"
- If Lumpsum: "How much are you looking to invest as a 
  one-time amount? (e.g., ₹50,000 / ₹1 Lakh / ₹5 Lakhs)"

### Step 3 — Ask Horizon:
"For how many years do you want to stay invested?
  
  📅 Short term: 1-3 years
  📅 Medium term: 3-7 years  
  📅 Long term: 7+ years (Recommended for wealth creation)"

### Step 4 — Ask Risk:
"Last question! What's your risk appetite?

🟢 **Conservative** — Safety first, lower but stable returns
🟡 **Moderate** — Balanced approach, medium risk & returns  
🔴 **Aggressive** — Higher risk for potentially higher returns

Which best describes you?"

## AFTER COLLECTING ALL 4 DATA POINTS:

1. Give a brief, exciting summary message:
   "Perfect! 🎯 Building your [RISK] portfolio now...
   
   📊 **Your Profile:**
   - Type: [TYPE]
   - Amount: ₹[AMOUNT]
   - Duration: [YEARS] years
   - Risk: [RISK]
   
   Generating your personalized portfolio in seconds! ✨"

2. IMMEDIATELY after that message, output this EXACT JSON block 
   (it will be hidden from the user automatically):

```json
{
  "command": "BUILD_PORTFOLIO",
  "type": "[sip or lumpsum]",
  "amount": [number],
  "duration": [number],
  "risk": "[conservative or moderate or aggressive]"
}
```

## RULES:
- Ask ONE question at a time — never multiple questions together
- If user gives unclear answer, gently ask again with examples
- If user gives a range (e.g., "5-10 years"), pick the middle
- Accept natural language: "high risk" = aggressive, 
  "safe" = conservative, "balanced" = moderate
- For amounts: accept "1 lakh" = 100000, "5k" = 5000, 
  "10 thousand" = 10000
- NEVER discuss specific fund names — you only collect preferences
- Keep track of what's been answered — don't re-ask
- After BUILD_PORTFOLIO command is sent, if user asks anything 
  else, respond helpfully about mutual funds generally

## CURRENT STATE TRACKING:
Keep track internally:
- collected_type: null
- collected_amount: null  
- collected_duration: null
- collected_risk: null
Only output the JSON when ALL FOUR are collected.
"""

@app.route('/api/ai/chat', methods=['POST'])
@require_api_key
def ai_chat():
    try:
        import cohere
        cohere_key = os.getenv("COHERE_API_KEY", "")
        co = cohere.Client(cohere_key)
        
        data = request.get_json()
        message = data.get('message', '')
        chat_history = data.get('history', [])
        
        cohere_history = []
        for msg in chat_history:
            cohere_history.append({
                "role": "USER" if msg['role'] == 'user' else "CHATBOT",
                "message": msg['content']
            })
        
        response = co.chat(
            message=message,
            chat_history=cohere_history,
            preamble=AI_INTERVIEWER_PREAMBLE,
            model='command-r-plus-08-2024',
            temperature=0.7,
            max_tokens=500
        )
        
        return jsonify({
            'success': True,
            'response': response.text,
            'tokens_used': response.meta.tokens.input_tokens if response.meta else None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/chat/image', methods=['POST'])
@require_api_key
def ai_chat_image():
    try:
        import cohere
        import pytesseract
        from PIL import Image
        import json
        import os
        import platform
        
        # Configure Tesseract Path ONLY for Windows (Local development)
        if platform.system() == 'Windows':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        img = Image.open(file.stream)
        
        # Extract Text using OCR
        extracted_text = pytesseract.image_to_string(img)
        
        # Call Cohere
        cohere_key = os.getenv("COHERE_API_KEY", "")
        co = cohere.Client(cohere_key)
        
        chat_history = json.loads(request.form.get('history', '[]'))
        cohere_history = []
        for msg in chat_history:
            cohere_history.append({
                "role": "USER" if msg['role'] == 'user' else "CHATBOT",
                "message": msg['content']
            })
            
        prompt = f"The user uploaded an image. Here is the raw text extracted from it via OCR:\n\n---\n{extracted_text}\n---\n\nPlease analyze this text and answer the user's implicit question or provide a helpful summary of the financial data shown."
        
        response = co.chat(
            message=prompt,
            chat_history=cohere_history,
            preamble=AI_INTERVIEWER_PREAMBLE,
            model='command-r-plus-08-2024',
            temperature=0.5,
            max_tokens=800
        )
        
        return jsonify({
            'success': True,
            'response': response.text,
            'extracted_text': extracted_text,
            'tokens_used': response.meta.tokens.input_tokens if response.meta else None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/auto-build', methods=['POST'])
def auto_build_portfolio():
    try:
        data = request.get_json()
        risk     = data.get('risk', 'moderate').lower()
        inv_type = data.get('type', 'sip').lower()
        amount   = data.get('amount', 10000)
        duration = data.get('duration', 5)
        
        import random
        large_cap = [
            {'name': 'Mirae Asset Large Cap Direct', 'search': 'Mirae Asset Large Cap Direct Growth'},
            {'name': 'ICICI Prudential Bluechip Direct', 'search': 'ICICI Prudential Bluechip Direct Growth'},
            {'name': 'SBI Bluechip Fund Direct', 'search': 'SBI Bluechip Direct Growth'},
            {'name': 'Nippon India Large Cap Direct', 'search': 'Nippon India Large Cap Direct Growth'}
        ]
        flexi_cap = [
            {'name': 'Parag Parikh Flexi Cap Direct', 'search': 'Parag Parikh Flexi Cap Direct Growth'},
            {'name': 'HDFC Flexi Cap Direct', 'search': 'HDFC Flexi Cap Direct Growth'},
            {'name': 'Quant Flexi Cap Direct', 'search': 'Quant Flexi Cap Direct Growth'},
            {'name': 'Kotak Flexicap Direct', 'search': 'Kotak Flexicap Direct Growth'}
        ]
        hybrid = [
            {'name': 'HDFC Balanced Advantage Direct', 'search': 'HDFC Balanced Advantage Direct Growth'},
            {'name': 'ICICI Prudential Balanced Advantage Direct', 'search': 'ICICI Prudential Balanced Advantage Direct Growth'},
            {'name': 'SBI Equity Hybrid Direct', 'search': 'SBI Equity Hybrid Direct Growth'},
            {'name': 'Edelweiss Balanced Advantage Direct', 'search': 'Edelweiss Balanced Advantage Direct Growth'}
        ]
        debt = [
            {'name': 'Axis Short Term Direct', 'search': 'Axis Short Term Direct Growth'},
            {'name': 'HDFC Short Term Debt Direct', 'search': 'HDFC Short Term Debt Direct Growth'},
            {'name': 'SBI Short Term Debt Direct', 'search': 'SBI Short Term Debt Direct Growth'},
            {'name': 'ICICI Prudential Corporate Bond Direct', 'search': 'ICICI Prudential Corporate Bond Direct Growth'}
        ]
        small_cap = [
            {'name': 'Nippon India Small Cap Direct', 'search': 'Nippon India Small Cap Direct Growth'},
            {'name': 'Quant Small Cap Direct', 'search': 'Quant Small Cap Direct Growth'},
            {'name': 'SBI Small Cap Direct', 'search': 'SBI Small Cap Direct Growth'},
            {'name': 'Tata Small Cap Direct', 'search': 'Tata Small Cap Direct Growth'}
        ]
        mid_cap = [
            {'name': 'Axis Midcap Direct', 'search': 'Axis Midcap Direct Growth'},
            {'name': 'HDFC Mid-Cap Opportunities Direct', 'search': 'HDFC Mid-Cap Opportunities Direct Growth'},
            {'name': 'Kotak Emerging Equity Direct', 'search': 'Kotak Emerging Equity Direct Growth'},
            {'name': 'Motilal Oswal Midcap Direct', 'search': 'Motilal Oswal Midcap Direct Growth'}
        ]
        liquid = [
            {'name': 'Nippon India Liquid Direct', 'search': 'Nippon India Liquid Direct Growth'},
            {'name': 'SBI Liquid Direct', 'search': 'SBI Liquid Direct Growth'},
            {'name': 'HDFC Liquid Direct', 'search': 'HDFC Liquid Direct Growth'}
        ]
        
        agg_small = random.sample(small_cap, 2)
        
        fund_profiles = {
            'conservative': {
                'description': 'Capital Protection with Steady Growth',
                'color': '#34D399',
                'emoji': '🟢',
                'allocations': [
                    {**random.choice(large_cap), 'weight': 30, 'category': 'Large Cap'},
                    {**random.choice(debt), 'weight': 25, 'category': 'Debt'},
                    {**random.choice(hybrid), 'weight': 25, 'category': 'Hybrid'},
                    {**random.choice(liquid), 'weight': 20, 'category': 'Liquid'}
                ]
            },
            'moderate': {
                'description': 'Balanced Growth with Manageable Risk',
                'color': '#F59E0B',
                'emoji': '🟡',
                'allocations': [
                    {**random.choice(large_cap), 'weight': 30, 'category': 'Large Cap'},
                    {**random.choice(flexi_cap), 'weight': 30, 'category': 'Flexi Cap'},
                    {**random.choice(hybrid), 'weight': 25, 'category': 'Hybrid'},
                    {**random.choice(debt), 'weight': 15, 'category': 'Debt'}
                ]
            },
            'aggressive': {
                'description': 'Maximum Growth, Higher Volatility',
                'color': '#F87171',
                'emoji': '🔴',
                'allocations': [
                    {**agg_small[0], 'weight': 30, 'category': 'Small Cap'},
                    {**random.choice(mid_cap), 'weight': 25, 'category': 'Mid Cap'},
                    {**random.choice(flexi_cap), 'weight': 25, 'category': 'Flexi Cap'},
                    {**agg_small[1], 'weight': 20, 'category': 'Small Cap'}
                ]
            }
        }
        
        profile = fund_profiles.get(risk, fund_profiles['moderate'])
        
        import requests as req
        funds_with_codes = []
        
        for fund in profile['allocations']:
            try:
                search_resp = req.get(
                    f"https://api.mfapi.in/mf/search?q={fund['search'].replace(' ', '%20')}",
                    timeout=5
                )
                results = search_resp.json()
                
                if results:
                    best = None
                    for r in results[:10]:
                        name_lower = r['schemeName'].lower()
                        if 'direct' in name_lower and 'growth' in name_lower and 'idcw' not in name_lower and 'dividend' not in name_lower:
                            best = r
                            break
                    
                    if not best and results:
                        best = results[0]
                    
                    if best:
                        funds_with_codes.append({
                            'code': str(best['schemeCode']),
                            'name': best['schemeName'],
                            'weight': fund['weight'],
                            'category': fund['category'],
                            'allocation_pct': fund['weight'] / 100
                        })
            except:
                pass
        
        # Helper to get a random scheme code for the fallback list
        def get_fallback(pool):
            f = random.choice(pool)
            search_resp = req.get(f"https://api.mfapi.in/mf/search?q={f['search'].replace(' ', '%20')}", timeout=5).json()
            return str(search_resp[0]['schemeCode']) if search_resp else None
            
        fallback_funds = {
            'conservative': [
                {'code': get_fallback(large_cap) or '119598', 'weight': 30, 'category': 'Large Cap'},
                {'code': get_fallback(debt) or '119597', 'weight': 25, 'category': 'Debt'},
                {'code': get_fallback(hybrid) or '120503', 'weight': 25, 'category': 'Hybrid'},
                {'code': get_fallback(liquid) or '118989', 'weight': 20, 'category': 'Liquid'}
            ],
            'moderate': [
                {'code': get_fallback(large_cap) or '118834', 'weight': 30, 'category': 'Large Cap'},
                {'code': get_fallback(flexi_cap) or '122639', 'weight': 30, 'category': 'Flexi Cap'},
                {'code': get_fallback(hybrid) or '119247', 'weight': 25, 'category': 'Hybrid'},
                {'code': get_fallback(debt) or '120823', 'weight': 15, 'category': 'Debt'}
            ],
            'aggressive': [
                {'code': get_fallback(small_cap) or '118778', 'weight': 30, 'category': 'Small Cap'},
                {'code': get_fallback(mid_cap) or '120503', 'weight': 25, 'category': 'Mid Cap'},
                {'code': get_fallback(flexi_cap) or '122639', 'weight': 25, 'category': 'Flexi Cap'},
                {'code': get_fallback(small_cap) or '120503', 'weight': 20, 'category': 'Small Cap'}
            ]
        }
        
        if len(funds_with_codes) < 3:
            fallbacks = fallback_funds.get(risk, fallback_funds['moderate'])
            funds_with_codes = [
                {
                    'code': f['code'],
                    'name': f.get('name', f'Fund {f["code"]}'),
                    'weight': f['weight'],
                    'category': f['category'],
                    'allocation_pct': f['weight'] / 100
                }
                for f in fallbacks
            ]
        
        return jsonify({
            'success': True,
            'risk_profile': risk,
            'description': profile['description'],
            'color': profile['color'],
            'emoji': profile['emoji'],
            'funds': funds_with_codes,
            'inv_type': inv_type,
            'amount': amount,
            'duration': duration
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==============================================================================
# 5 ADVANCED FEATURES API ENDPOINTS
# ==============================================================================

# FEATURE 1: HEAD-TO-HEAD FUND COMPARISON & SCREENER
@app.route('/api/compare/funds', methods=['POST'])
def compare_funds():
    """Compare 2-3 funds side by side with all metrics"""
    import requests as req
    from datetime import datetime, timedelta
    import numpy as np
    import concurrent.futures
    
    data = request.get_json() or {}
    codes = data.get('codes', [])
    
    if len(codes) < 2 or len(codes) > 3:
        return jsonify({'error': 'Select 2 or 3 funds'}), 400
    
    def fetch_fund_metrics(code):
        resp = req.get(f'https://api.mfapi.in/mf/{code}', timeout=12)
        mf = resp.json()
        meta = mf.get('meta', {})
        navs = mf.get('data', [])
        
        nav_data = []
        for n in navs:
            try:
                d = datetime.strptime(n['date'], '%d-%m-%Y')
                nav_data.append((d, float(n['nav'])))
            except Exception:
                pass
        nav_data.sort(key=lambda x: x[0])
        
        latest_nav = nav_data[-1][1] if nav_data else 0
        latest_date = nav_data[-1][0].strftime('%d %b %Y') if nav_data else 'N/A'
        
        def cagr(years):
            if len(nav_data) < 2:
                return None
            target = nav_data[-1][0] - timedelta(days=int(years * 365.25))
            closest = min(nav_data, key=lambda x: abs(x[0] - target))
            actual_yrs = (nav_data[-1][0] - closest[0]).days / 365.25
            if actual_yrs < years * 0.7 or closest[1] <= 0:
                return None
            return round(((nav_data[-1][1] / closest[1]) ** (1 / actual_yrs) - 1) * 100, 2)
        
        # 52-week high/low
        one_year_ago = nav_data[-1][0] - timedelta(days=365) if nav_data else datetime.now()
        recent_navs = [v for d, v in nav_data if d >= one_year_ago]
        high_52w = max(recent_navs) if recent_navs else None
        low_52w = min(recent_navs) if recent_navs else None
        
        # Volatility
        if len(nav_data) > 30:
            prices = np.array([v for _, v in nav_data[-365:]])
            dr = np.diff(prices) / prices[:-1]
            vol = round(float(np.std(dr) * np.sqrt(252) * 100), 2)
        else:
            vol = None
        
        # Max Drawdown
        if nav_data:
            prices = np.array([v for _, v in nav_data])
            peak = prices[0]
            max_dd = 0
            for p in prices:
                if p > peak:
                    peak = p
                if peak > 0:
                    dd = (peak - p) / peak
                    if dd > max_dd:
                        max_dd = dd
            max_drawdown = round(max_dd * 100, 2)
        else:
            max_drawdown = 0
        
        # Fund age
        if nav_data:
            fund_age = round((nav_data[-1][0] - nav_data[0][0]).days / 365.25, 1)
        else:
            fund_age = None
        
        # NAV chart data (last 1 year, sampled)
        chart_data = [
            {
                'date': d.strftime('%d-%m-%Y'),
                'nav': round(v, 4)
            }
            for d, v in nav_data[-365::2]
        ]
        
        return {
            'code': code,
            'name': meta.get('scheme_name', f'Fund {code}'),
            'category': meta.get('scheme_category', ''),
            'fund_house': meta.get('fund_house', ''),
            'scheme_type': meta.get('scheme_type', ''),
            'latest_nav': latest_nav,
            'latest_date': latest_date,
            'cagr_1y': cagr(1),
            'cagr_3y': cagr(3),
            'cagr_5y': cagr(5),
            'cagr_10y': cagr(10),
            'volatility': vol,
            'max_drawdown': max_drawdown,
            'fund_age': fund_age,
            'high_52w': round(high_52w, 4) if high_52w else None,
            'low_52w': round(low_52w, 4) if low_52w else None,
            'nav_chart': chart_data
        }
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(fetch_fund_metrics, c): c for c in codes}
        for f in concurrent.futures.as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    # Sort by original order
    results.sort(key=lambda x: codes.index(x['code']) if x['code'] in codes else 0)
    return jsonify({'success': True, 'funds': results})


@app.route('/api/screener/funds', methods=['POST'])
def screen_funds():
    """Advanced fund screener with multiple filters"""
    import requests as req
    
    data = request.get_json() or {}
    filters = data.get('filters', {})
    category = filters.get('category', '')
    limit = data.get('limit', 20)
    
    resp = req.get('https://api.mfapi.in/mf', timeout=12)
    all_funds = resp.json()
    
    if category:
        filtered = [
            f for f in all_funds
            if category.lower() in f.get('schemeName', '').lower()
        ]
    else:
        filtered = all_funds
    
    filtered = [
        f for f in filtered
        if 'direct' in f.get('schemeName', '').lower()
        and 'growth' in f.get('schemeName', '').lower()
        and 'idcw' not in f.get('schemeName', '').lower()
    ]
    
    return jsonify({
        'success': True,
        'funds': filtered[:limit],
        'total': len(filtered)
    })


# FEATURE 2: ROLLING RETURNS ENGINE
@app.route('/api/rolling/returns', methods=['POST'])
def rolling_returns():
    """Calculate rolling returns for a fund"""
    import numpy as np
    from datetime import datetime, timedelta
    import requests as req
    
    data = request.get_json() or {}
    code = data.get('code')
    window_yrs = int(data.get('window', 3))
    
    if not code:
        return jsonify({'error': 'Fund code required'}), 400
    
    resp = req.get(f'https://api.mfapi.in/mf/{code}', timeout=12)
    mf = resp.json()
    navs = mf.get('data', [])
    name = mf.get('meta', {}).get('scheme_name', '')
    
    nav_data = []
    for n in navs:
        try:
            d = datetime.strptime(n['date'], '%d-%m-%Y')
            nav_data.append((d, float(n['nav'])))
        except Exception:
            pass
    nav_data.sort(key=lambda x: x[0])
    
    if len(nav_data) < window_yrs * 200:
        return jsonify({
            'error': f'Insufficient data for {window_yrs}Y rolling (Fund has {len(nav_data)} records)'
        }), 400
    
    window_days = int(window_yrs * 365.25)
    rolling = []
    
    for i in range(len(nav_data)):
        start_date = nav_data[i][0]
        end_date = start_date + timedelta(days=window_days)
        
        end_candidates = [
            (j, abs((nav_data[j][0] - end_date).days))
            for j in range(i + 1, len(nav_data))
        ]
        if not end_candidates:
            continue
        
        end_idx = min(end_candidates, key=lambda x: x[1])[0]
        if abs((nav_data[end_idx][0] - end_date).days) > 35:
            continue
        
        start_nav = nav_data[i][1]
        end_nav = nav_data[end_idx][1]
        if start_nav <= 0 or end_nav <= 0:
            continue
        
        actual_yrs = (nav_data[end_idx][0] - nav_data[i][0]).days / 365.25
        if actual_yrs <= 0:
            continue
        
        rolling_cagr = ((end_nav / start_nav) ** (1 / actual_yrs) - 1) * 100
        rolling.append({
            'start': nav_data[i][0].strftime('%d-%m-%Y'),
            'end': nav_data[end_idx][0].strftime('%d-%m-%Y'),
            'cagr': round(rolling_cagr, 2),
            'start_nav': start_nav,
            'end_nav': end_nav
        })
    
    if not rolling:
        return jsonify({'error': 'No rolling periods could be calculated'}), 400
    
    step = max(1, len(rolling) // 200)
    sampled = rolling[::step]
    
    cagrs = [r['cagr'] for r in rolling]
    arr = np.array(cagrs)
    nifty_cagr = 12.0
    beat_count = sum(1 for c in cagrs if c > nifty_cagr)
    beat_pct = round(beat_count / len(cagrs) * 100, 1) if cagrs else 0
    
    stats = {
        'min': round(float(np.min(arr)), 2),
        'max': round(float(np.max(arr)), 2),
        'median': round(float(np.median(arr)), 2),
        'mean': round(float(np.mean(arr)), 2),
        'std': round(float(np.std(arr)), 2),
        'positive_pct': round(sum(1 for c in cagrs if c > 0) / len(cagrs) * 100, 1),
        'beat_nifty_pct': beat_pct,
        'total_windows': len(rolling)
    }
    
    return jsonify({
        'success': True,
        'fund_name': name,
        'window': window_yrs,
        'rolling_data': sampled,
        'stats': stats,
        'nifty_benchmark': nifty_cagr
    })


# FEATURE 3: PORTFOLIO OVERLAP ANALYZER
FUND_HOLDINGS = {
    '122639': [  # Parag Parikh Flexi Cap
        ('HDFC Bank', 4.5), ('Power Grid', 3.2),
        ('Coalgate', 3.1), ('Alphabet Inc', 5.2),
        ('Meta Platforms', 4.8), ('ITC', 3.8),
        ('Bajaj Holdings', 3.5), ('ICICI Bank', 3.2),
        ('Maruti Suzuki', 2.9), ('Axis Bank', 2.7)
    ],
    '118778': [  # Nippon India Small Cap
        ('HDFC Bank', 2.1), ('Tube Investments', 2.8),
        ('Dixon Tech', 2.5), ('Kaynes Tech', 2.3),
        ('Doms Industries', 2.1), ('BSE Ltd', 2.0),
        ('KPIT Technologies', 1.9), ('Tata Tech', 1.8),
        ('PTC India', 1.7), ('Kirloskar Ind', 1.6)
    ],
    '120503': [  # Axis Midcap
        ('Persistent Systems', 3.2), ('Coforge', 2.9),
        ('Max Financial', 2.7), ('ICICI Pru Life', 2.6),
        ('SBI Life', 2.5), ('Trent', 2.4),
        ('Page Industries', 2.3), ('Mphasis', 2.2),
        ('Cholamandalam', 2.1), ('HDFC Bank', 2.0)
    ],
    '119062': [  # HDFC Mid-Cap Opportunities
        ('Max Financial', 2.8), ('Crompton Greaves', 2.7),
        ('HDFC Bank', 2.5), ('Tube Investments', 2.4),
        ('Coforge', 2.3), ('Persistent', 2.2),
        ('Trent', 2.1), ('Voltas', 2.0),
        ('Mphasis', 1.9), ('ICICI Bank', 1.8)
    ],
    '118989': [  # HDFC Mid-Cap Opportunities Direct
        ('Max Financial', 2.8), ('Crompton Greaves', 2.7),
        ('HDFC Bank', 2.5), ('Tube Investments', 2.4),
        ('Coforge', 2.3), ('Persistent Systems', 2.2),
        ('Trent', 2.1), ('Voltas', 2.0),
        ('Mphasis', 1.9), ('ICICI Bank', 1.8)
    ],
    '120586': [  # Mirae Asset Large & Midcap
        ('HDFC Bank', 5.6), ('ICICI Bank', 5.2),
        ('Reliance Industries', 4.8), ('Infosys', 3.9),
        ('Axis Bank', 3.4), ('TCS', 3.1),
        ('L&T', 2.8), ('State Bank of India', 2.7),
        ('Bharti Airtel', 2.6), ('NTPC', 2.3)
    ],
    '120716': [  # SBI Bluechip Fund
        ('HDFC Bank', 7.8), ('ICICI Bank', 6.9),
        ('Reliance Industries', 5.8), ('Infosys', 4.5),
        ('L&T', 4.2), ('ITC', 3.9),
        ('Axis Bank', 3.6), ('State Bank of India', 3.4),
        ('TCS', 3.1), ('Bharti Airtel', 2.9)
    ],
    '120828': [  # Quant Small Cap Fund
        ('Reliance Industries', 8.2), ('Jio Financial', 4.9),
        ('Bikaji Foods', 3.8), ('Adani Power', 3.6),
        ('Hindustan Copper', 3.4), ('IRB Infra', 3.1),
        ('Aegis Logistics', 2.8), ('Swan Energy', 2.6),
        ('HFCL', 2.5), ('National Aluminium', 2.4)
    ],
    '108466': [  # ICICI Prudential Bluechip
        ('ICICI Bank', 8.9), ('HDFC Bank', 7.5),
        ('Reliance Industries', 6.8), ('Infosys', 5.4),
        ('L&T', 5.1), ('Axis Bank', 4.2),
        ('Bharti Airtel', 3.9), ('TCS', 3.8),
        ('Maruti Suzuki', 3.2), ('NTPC', 2.8)
    ],
    '100119': [  # HDFC Balanced Advantage
        ('HDFC Bank', 5.9), ('ICICI Bank', 5.1),
        ('State Bank of India', 4.3), ('Coal India', 3.8),
        ('ITC', 3.4), ('NTPC', 3.1),
        ('L&T', 2.9), ('Power Grid', 2.6),
        ('Axis Bank', 2.4), ('Infosys', 2.1)
    ]
}

GENERIC_HOLDINGS_POOL = {
    'small': [
        ('Tube Investments', 3.2), ('Dixon Tech', 2.9), ('Kaynes Tech', 2.8),
        ('KPIT Technologies', 2.5), ('BSE Ltd', 2.3), ('Doms Industries', 2.1),
        ('Tata Tech', 1.9), ('PTC India', 1.8), ('Kirloskar Ind', 1.7), ('HDFC Bank', 1.5)
    ],
    'mid': [
        ('Persistent Systems', 3.4), ('Coforge', 3.1), ('Max Financial', 2.8),
        ('Trent', 2.6), ('Mphasis', 2.4), ('Page Industries', 2.2),
        ('HDFC Bank', 2.1), ('ICICI Pru Life', 2.0), ('Voltas', 1.9), ('Cholamandalam', 1.8)
    ],
    'large': [
        ('HDFC Bank', 8.2), ('ICICI Bank', 7.1), ('Reliance Industries', 6.5),
        ('Infosys', 5.2), ('TCS', 4.4), ('L&T', 4.1),
        ('Axis Bank', 3.8), ('Bharti Airtel', 3.5), ('ITC', 3.2), ('State Bank of India', 3.0)
    ],
    'default': [
        ('HDFC Bank', 5.5), ('ICICI Bank', 4.8), ('Reliance Industries', 4.2),
        ('Infosys', 3.8), ('TCS', 3.5), ('L&T', 3.1),
        ('Axis Bank', 2.9), ('ITC', 2.7), ('Bharti Airtel', 2.5), ('State Bank of India', 2.2)
    ]
}

def get_holdings_for_fund(code, name=''):
    if str(code) in FUND_HOLDINGS:
        return FUND_HOLDINGS[str(code)]
    name_low = (name or '').lower()
    if 'small' in name_low:
        return GENERIC_HOLDINGS_POOL['small']
    elif 'mid' in name_low:
        return GENERIC_HOLDINGS_POOL['mid']
    elif 'large' in name_low or 'bluechip' in name_low or 'nifty' in name_low:
        return GENERIC_HOLDINGS_POOL['large']
    return GENERIC_HOLDINGS_POOL['default']


@app.route('/api/overlap/analyze', methods=['POST'])
def overlap_analyze():
    """Analyze portfolio overlap between selected funds"""
    data = request.get_json() or {}
    funds = data.get('funds', [])
    
    if len(funds) < 2:
        return jsonify({'error': 'Need at least 2 funds'}), 400
    
    fund_holdings = {}
    for fund in funds:
        code = str(fund.get('code', ''))
        name = fund.get('name', f'Fund {code}')
        holdings = get_holdings_for_fund(code, name)
        fund_holdings[code] = {
            'name': name,
            'weight': fund.get('weight', round(100 / len(funds), 1)),
            'holdings': {h[0]: h[1] for h in holdings}
        }
    
    pairwise = []
    codes = [str(f.get('code', '')) for f in funds]
    
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            c1, c2 = codes[i], codes[j]
            h1 = set(fund_holdings[c1]['holdings'].keys())
            h2 = set(fund_holdings[c2]['holdings'].keys())
            common = h1 & h2
            
            if not h1 or not h2:
                overlap_pct = 0
            else:
                overlap_pct = round(len(common) / len(h1 | h2) * 100, 1)
            
            weighted_overlap = 0
            for stock in common:
                w1 = fund_holdings[c1]['holdings'][stock]
                w2 = fund_holdings[c2]['holdings'][stock]
                weighted_overlap += min(w1, w2)
            
            pairwise.append({
                'fund1': fund_holdings[c1]['name'],
                'fund2': fund_holdings[c2]['name'],
                'code1': c1, 'code2': c2,
                'overlap_pct': overlap_pct,
                'weighted_overlap': round(weighted_overlap, 2),
                'common_stocks': list(common),
                'severity': 'High' if overlap_pct > 40 else 'Medium' if overlap_pct > 20 else 'Low'
            })
    
    all_stocks = {}
    for fund in funds:
        code = str(fund.get('code', ''))
        alloc = (fund.get('weight', 100 / len(funds))) / 100
        holdings = fund_holdings.get(code, {}).get('holdings', {})
        
        for stock, pct in holdings.items():
            weighted = round(pct * alloc, 2)
            if stock not in all_stocks:
                all_stocks[stock] = {
                    'stock': stock,
                    'total_weight': 0,
                    'funds': []
                }
            all_stocks[stock]['total_weight'] = round(all_stocks[stock]['total_weight'] + weighted, 2)
            f_label = fund_holdings[code]['name'].split()[0]
            if f_label not in all_stocks[stock]['funds']:
                all_stocks[stock]['funds'].append(f_label)
    
    top_stocks = sorted(all_stocks.values(), key=lambda x: x['total_weight'], reverse=True)[:15]
    
    if pairwise:
        avg_overlap = sum(p['overlap_pct'] for p in pairwise) / len(pairwise)
        diversification_score = round(max(0, 100 - avg_overlap), 1)
    else:
        diversification_score = 100.0
    
    return jsonify({
        'success': True,
        'pairwise_overlap': pairwise,
        'top_holdings': top_stocks,
        'diversification_score': diversification_score,
        'fund_count': len(funds)
    })


# FEATURE 4: MONTE CARLO SIMULATOR
@app.route('/api/montecarlo/simulate', methods=['POST'])
def monte_carlo_simulate():
    """Monte Carlo simulation for portfolio wealth projection"""
    import numpy as np
    
    data = request.get_json() or {}
    annual_return = float(data.get('annual_return', 12)) / 100
    annual_vol = float(data.get('annual_vol', 15)) / 100
    investment = float(data.get('investment', 10000))
    inv_type = data.get('type', 'sip')
    years = int(data.get('years', 10))
    simulations = int(data.get('simulations', 1000))
    
    np.random.seed(42)
    months = years * 12
    monthly_return = annual_return / 12
    monthly_vol = annual_vol / np.sqrt(12)
    
    all_paths = []
    
    for _ in range(simulations):
        monthly_returns = np.random.normal(monthly_return, monthly_vol, months)
        portfolio_value = 0
        path = [0]
        
        for r in monthly_returns:
            if inv_type == 'sip':
                portfolio_value = (portfolio_value + investment) * (1 + r)
            else:
                if path == [0]:
                    portfolio_value = investment * (1 + r)
                else:
                    portfolio_value *= (1 + r)
            path.append(round(portfolio_value, 2))
        
        all_paths.append(path)
    
    paths_array = np.array(all_paths)
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    pct_bands = {}
    for p in percentiles:
        pct_bands[f'p{p}'] = [
            round(float(np.percentile(paths_array[:, t], p)), 2)
            for t in range(0, months + 1, 3)
        ]
    
    final_values = paths_array[:, -1]
    total_invested = investment * months if inv_type == 'sip' else investment
    
    targets = [total_invested * 2, total_invested * 3, total_invested * 5]
    target_probs = [
        round(float(np.mean(final_values >= t) * 100), 1)
        for t in targets
    ]
    
    outcome = {
        'conservative_p10': round(float(np.percentile(final_values, 10)), 2),
        'median_p50': round(float(np.percentile(final_values, 50)), 2),
        'optimistic_p90': round(float(np.percentile(final_values, 90)), 2),
        'best_case_p95': round(float(np.percentile(final_values, 95)), 2),
        'worst_case_p5': round(float(np.percentile(final_values, 5)), 2),
        'mean': round(float(np.mean(final_values)), 2),
        'probability_loss': round(float(np.mean(final_values < total_invested) * 100), 1),
        'total_invested': round(total_invested, 2),
        'double_prob': target_probs[0],
        'triple_prob': target_probs[1],
        'five_x_prob': target_probs[2],
    }
    
    time_labels = [f'Y{t // 4}Q{(t % 4) + 1}' if t > 0 else 'Start' for t in range(0, months + 1, 3)]
    sample_indices = np.random.choice(simulations, min(50, simulations), replace=False)
    sample_paths = [
        [round(float(v), 2) for v in paths_array[i, ::3]]
        for i in sample_indices
    ]
    
    return jsonify({
        'success': True,
        'simulations': simulations,
        'years': years,
        'time_labels': time_labels,
        'percentile_bands': pct_bands,
        'sample_paths': sample_paths[:20],
        'outcome': outcome,
        'params': {
            'annual_return': annual_return * 100,
            'annual_vol': annual_vol * 100,
            'investment': investment,
            'type': inv_type
        }
    })


# FEATURE 5: TAX HARVESTING OPTIMIZER
@app.route('/api/tax/optimize', methods=['POST'])
def tax_optimize():
    """LTCG / STCG Tax Harvesting Optimizer"""
    from datetime import datetime, timedelta
    
    data = request.get_json() or {}
    holdings = data.get('holdings', [])
    fy_end = data.get('fy_end', '2026-03-31')
    
    LTCG_EXEMPTION = 125000  # ₹1.25 Lakh under updated tax rules
    LTCG_TAX_RATE = 0.125    # 12.5%
    STCG_TAX_RATE = 0.20     # 20%
    
    analyzed = []
    total_ltcg = 0
    total_stcg = 0
    
    for h in holdings:
        try:
            purchase_date = datetime.strptime(h['purchase_date'], '%Y-%m-%d')
            today = datetime.now()
            holding_days = (today - purchase_date).days
            is_ltcg = holding_days > 365
            
            current_nav = float(h.get('current_nav', 0))
            purchase_nav = float(h.get('purchase_nav', 0))
            units = float(h.get('units', 0))
            
            if purchase_nav <= 0 or units <= 0:
                continue
            
            invested_value = purchase_nav * units
            current_value = current_nav * units
            gain = current_value - invested_value
            gain_pct = round((gain / invested_value) * 100, 2)
            days_to_ltcg = max(0, 366 - holding_days)
            
            if is_ltcg:
                total_ltcg += gain
                tax_type = 'LTCG'
                tax_rate = LTCG_TAX_RATE
            else:
                total_stcg += gain
                tax_type = 'STCG'
                tax_rate = STCG_TAX_RATE
            
            tax_if_sold_now = max(0, gain) * tax_rate
            
            analyzed.append({
                'code': h.get('code', ''),
                'name': h.get('name', 'Mutual Fund'),
                'units': units,
                'purchase_nav': purchase_nav,
                'current_nav': current_nav,
                'invested_value': round(invested_value, 2),
                'current_value': round(current_value, 2),
                'gain': round(gain, 2),
                'gain_pct': gain_pct,
                'holding_days': holding_days,
                'tax_type': tax_type,
                'days_to_ltcg': days_to_ltcg,
                'tax_if_sold': round(tax_if_sold_now, 2),
                'is_profit': gain > 0
            })
        except Exception:
            continue
    
    ltcg_gains = [a for a in analyzed if a['tax_type'] == 'LTCG' and a['gain'] > 0]
    ltcg_gains_sorted = sorted(ltcg_gains, key=lambda x: x['gain'], reverse=True)
    
    remaining_exemption = LTCG_EXEMPTION
    harvest_plan = []
    
    for fund in ltcg_gains_sorted:
        if remaining_exemption <= 0:
            break
        
        harvestable = min(fund['gain'], remaining_exemption)
        nav_diff = fund['current_nav'] - fund['purchase_nav']
        units_to_sell = (harvestable / nav_diff) if nav_diff > 0 else 0
        tax_saved = harvestable * LTCG_TAX_RATE
        remaining_exemption -= harvestable
        
        try:
            fy_end_dt = datetime.strptime(fy_end, '%Y-%m-%d')
            urgency = 'HIGH' if (fy_end_dt - datetime.now()).days < 30 else 'MEDIUM'
        except Exception:
            urgency = 'MEDIUM'
        
        harvest_plan.append({
            'fund': fund['name'],
            'code': fund['code'],
            'action': 'SELL & REINVEST',
            'harvest_gain': round(harvestable, 2),
            'units_to_sell': round(units_to_sell, 2),
            'sale_value': round(units_to_sell * fund['current_nav'], 2),
            'tax_saved': round(tax_saved, 2),
            'reinvest_by': (datetime.now() + timedelta(days=1)).strftime('%d %b %Y'),
            'urgency': urgency
        })
    
    total_tax_saved = sum(p['tax_saved'] for p in harvest_plan)
    try:
        days_to_fy_end = (datetime.strptime(fy_end, '%Y-%m-%d') - datetime.now()).days
    except Exception:
        days_to_fy_end = 0
    
    near_ltcg = [a for a in analyzed if 0 < a['days_to_ltcg'] <= 30 and a['gain'] > 0]
    
    return jsonify({
        'success': True,
        'summary': {
            'total_ltcg_gains': round(total_ltcg, 2),
            'total_stcg_gains': round(total_stcg, 2),
            'ltcg_exemption': LTCG_EXEMPTION,
            'ltcg_utilized': round(min(max(0, total_ltcg), LTCG_EXEMPTION), 2),
            'total_tax_saved': round(total_tax_saved, 2),
            'days_to_fy_end': days_to_fy_end,
            'fy_end': fy_end
        },
        'holdings_analyzed': analyzed,
        'harvest_plan': harvest_plan,
        'near_ltcg_funds': near_ltcg
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
