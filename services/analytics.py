import os
from datetime import datetime, timedelta
import concurrent.futures
import numpy as np
import requests as req

from core.extensions import normalize_scheme_category
from services.market_data import get_fund_raw_data

# ==============================================================================
# FEATURE 1: HEAD-TO-HEAD FUND COMPARISON & SCREENER
# ==============================================================================
def compare_funds_metrics(codes):
    """Compare 2-3 funds side by side with all metrics"""
    if len(codes) < 2 or len(codes) > 3:
        return None, "Select 2 or 3 funds"
    
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
            if len(nav_data) < 2: return None
            target = nav_data[-1][0] - timedelta(days=int(years * 365.25))
            closest = min(nav_data, key=lambda x: abs(x[0] - target))
            actual_yrs = (nav_data[-1][0] - closest[0]).days / 365.25
            if actual_yrs < years * 0.7 or closest[1] <= 0: return None
            return round(((nav_data[-1][1] / closest[1]) ** (1 / actual_yrs) - 1) * 100, 2)
        
        one_year_ago = nav_data[-1][0] - timedelta(days=365) if nav_data else datetime.now()
        recent_navs = [v for d, v in nav_data if d >= one_year_ago]
        high_52w = max(recent_navs) if recent_navs else None
        low_52w = min(recent_navs) if recent_navs else None
        
        if len(nav_data) > 30:
            prices = np.array([v for _, v in nav_data[-365:]])
            dr = np.diff(prices) / prices[:-1]
            vol = round(float(np.std(dr) * np.sqrt(252) * 100), 2)
        else:
            vol = None
        
        if nav_data:
            prices = np.array([v for _, v in nav_data])
            peak = prices[0]
            max_dd = 0
            for p in prices:
                if p > peak: peak = p
                if peak > 0:
                    dd = (peak - p) / peak
                    if dd > max_dd: max_dd = dd
            max_drawdown = round(max_dd * 100, 2)
            fund_age = round((nav_data[-1][0] - nav_data[0][0]).days / 365.25, 1)
        else:
            max_drawdown = 0
            fund_age = None
        
        chart_data = [{'date': d.strftime('%d-%m-%Y'), 'nav': round(v, 4)} for d, v in nav_data[-365::2]]
        
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
            results.append(f.result())
    
    results.sort(key=lambda x: codes.index(x['code']) if x['code'] in codes else 0)
    return results, None

def screen_funds_list(filters=None, limit=20):
    filters = filters or {}
    category = filters.get('category', '')
    resp = req.get('https://api.mfapi.in/mf', timeout=12)
    all_funds = resp.json()
    
    if category:
        filtered = [f for f in all_funds if category.lower() in f.get('schemeName', '').lower()]
    else:
        filtered = all_funds
        
    filtered = [
        f for f in filtered
        if 'direct' in f.get('schemeName', '').lower()
        and 'growth' in f.get('schemeName', '').lower()
        and 'idcw' not in f.get('schemeName', '').lower()
    ]
    return filtered[:limit], len(filtered)

# ==============================================================================
# FEATURE 2: ROLLING RETURNS ENGINE
# ==============================================================================
def calculate_rolling_returns(code, window_yrs=3):
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
        return None, f'Insufficient data for {window_yrs}Y rolling (Fund has {len(nav_data)} records)'
        
    window_days = int(window_yrs * 365.25)
    rolling = []
    
    for i in range(len(nav_data)):
        start_date = nav_data[i][0]
        end_date = start_date + timedelta(days=window_days)
        end_candidates = [(j, abs((nav_data[j][0] - end_date).days)) for j in range(i + 1, len(nav_data))]
        if not end_candidates: continue
        end_idx = min(end_candidates, key=lambda x: x[1])[0]
        if abs((nav_data[end_idx][0] - end_date).days) > 35: continue
        
        start_nav = nav_data[i][1]
        end_nav = nav_data[end_idx][1]
        if start_nav <= 0 or end_nav <= 0: continue
        actual_yrs = (nav_data[end_idx][0] - nav_data[i][0]).days / 365.25
        if actual_yrs <= 0: continue
        
        rolling_cagr = ((end_nav / start_nav) ** (1 / actual_yrs) - 1) * 100
        rolling.append({
            'start': nav_data[i][0].strftime('%d-%m-%Y'),
            'end': nav_data[end_idx][0].strftime('%d-%m-%Y'),
            'cagr': round(rolling_cagr, 2),
            'start_nav': start_nav,
            'end_nav': end_nav
        })
        
    if not rolling:
        return None, 'No rolling periods could be calculated'
        
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
    return {
        'fund_name': name,
        'window': window_yrs,
        'rolling_data': sampled,
        'stats': stats,
        'nifty_benchmark': nifty_cagr
    }, None

# ==============================================================================
# FEATURE 3: PORTFOLIO OVERLAP ANALYZER
# ==============================================================================
FUND_HOLDINGS = {
    '122639': [('HDFC Bank', 4.5), ('Power Grid', 3.2), ('Coalgate', 3.1), ('Alphabet Inc', 5.2), ('Meta Platforms', 4.8), ('ITC', 3.8), ('Bajaj Holdings', 3.5), ('ICICI Bank', 3.2), ('Maruti Suzuki', 2.9), ('Axis Bank', 2.7)],
    '118778': [('HDFC Bank', 2.1), ('Tube Investments', 2.8), ('Dixon Tech', 2.5), ('Kaynes Tech', 2.3), ('Doms Industries', 2.1), ('BSE Ltd', 2.0), ('KPIT Technologies', 1.9), ('Tata Tech', 1.8), ('PTC India', 1.7), ('Kirloskar Ind', 1.6)],
    '120503': [('Persistent Systems', 3.2), ('Coforge', 2.9), ('Max Financial', 2.7), ('ICICI Pru Life', 2.6), ('SBI Life', 2.5), ('Trent', 2.4), ('Page Industries', 2.3), ('Mphasis', 2.2), ('Cholamandalam', 2.1), ('HDFC Bank', 2.0)],
    '119062': [('Max Financial', 2.8), ('Crompton Greaves', 2.7), ('HDFC Bank', 2.5), ('Tube Investments', 2.4), ('Coforge', 2.3), ('Persistent', 2.2), ('Trent', 2.1), ('Voltas', 2.0), ('Mphasis', 1.9), ('ICICI Bank', 1.8)],
    '118989': [('Max Financial', 2.8), ('Crompton Greaves', 2.7), ('HDFC Bank', 2.5), ('Tube Investments', 2.4), ('Coforge', 2.3), ('Persistent Systems', 2.2), ('Trent', 2.1), ('Voltas', 2.0), ('Mphasis', 1.9), ('ICICI Bank', 1.8)],
    '120586': [('HDFC Bank', 5.6), ('ICICI Bank', 5.2), ('Reliance Industries', 4.8), ('Infosys', 3.9), ('Axis Bank', 3.4), ('TCS', 3.1), ('L&T', 2.8), ('State Bank of India', 2.7), ('Bharti Airtel', 2.6), ('NTPC', 2.3)],
    '120716': [('HDFC Bank', 7.8), ('ICICI Bank', 6.9), ('Reliance Industries', 5.8), ('Infosys', 4.5), ('L&T', 4.2), ('ITC', 3.9), ('Axis Bank', 3.6), ('State Bank of India', 3.4), ('TCS', 3.1), ('Bharti Airtel', 2.9)],
    '120828': [('Reliance Industries', 8.2), ('Jio Financial', 4.9), ('Bikaji Foods', 3.8), ('Adani Power', 3.6), ('Hindustan Copper', 3.4), ('IRB Infra', 3.1), ('Aegis Logistics', 2.8), ('Swan Energy', 2.6), ('HFCL', 2.5), ('National Aluminium', 2.4)],
    '108466': [('ICICI Bank', 8.9), ('HDFC Bank', 7.5), ('Reliance Industries', 6.8), ('Infosys', 5.4), ('L&T', 5.1), ('Axis Bank', 4.2), ('Bharti Airtel', 3.9), ('TCS', 3.8), ('Maruti Suzuki', 3.2), ('NTPC', 2.8)],
    '100119': [('HDFC Bank', 5.9), ('ICICI Bank', 5.1), ('State Bank of India', 4.3), ('Coal India', 3.8), ('ITC', 3.4), ('NTPC', 3.1), ('L&T', 2.9), ('Power Grid', 2.6), ('Axis Bank', 2.4), ('Infosys', 2.1)]
}

GENERIC_HOLDINGS_POOL = {
    'small': [('Tube Investments', 3.2), ('Dixon Tech', 2.9), ('Kaynes Tech', 2.8), ('KPIT Technologies', 2.5), ('BSE Ltd', 2.3), ('Doms Industries', 2.1), ('Tata Tech', 1.9), ('PTC India', 1.8), ('Kirloskar Ind', 1.7), ('HDFC Bank', 1.5)],
    'mid': [('Persistent Systems', 3.4), ('Coforge', 3.1), ('Max Financial', 2.8), ('Trent', 2.6), ('Mphasis', 2.4), ('Page Industries', 2.2), ('HDFC Bank', 2.1), ('ICICI Pru Life', 2.0), ('Voltas', 1.9), ('Cholamandalam', 1.8)],
    'large': [('HDFC Bank', 8.2), ('ICICI Bank', 7.1), ('Reliance Industries', 6.5), ('Infosys', 5.2), ('TCS', 4.4), ('L&T', 4.1), ('Axis Bank', 3.8), ('Bharti Airtel', 3.5), ('ITC', 3.2), ('State Bank of India', 3.0)],
    'default': [('HDFC Bank', 5.5), ('ICICI Bank', 4.8), ('Reliance Industries', 4.2), ('Infosys', 3.8), ('TCS', 3.5), ('L&T', 3.1), ('Axis Bank', 2.9), ('ITC', 2.7), ('Bharti Airtel', 2.5), ('State Bank of India', 2.2)]
}

def get_holdings_for_fund(code, name=''):
    if str(code) in FUND_HOLDINGS:
        return FUND_HOLDINGS[str(code)]
    name_low = (name or '').lower()
    if 'small' in name_low: return GENERIC_HOLDINGS_POOL['small']
    elif 'mid' in name_low: return GENERIC_HOLDINGS_POOL['mid']
    elif 'large' in name_low or 'bluechip' in name_low or 'nifty' in name_low: return GENERIC_HOLDINGS_POOL['large']
    return GENERIC_HOLDINGS_POOL['default']

def analyze_portfolio_overlap(funds):
    if len(funds) < 2:
        return None, 'Need at least 2 funds'
        
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
            overlap_pct = round(len(common) / len(h1 | h2) * 100, 1) if (h1 and h2) else 0
            weighted_overlap = sum(min(fund_holdings[c1]['holdings'][s], fund_holdings[c2]['holdings'][s]) for s in common)
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
                all_stocks[stock] = {'stock': stock, 'total_weight': 0, 'funds': []}
            all_stocks[stock]['total_weight'] = round(all_stocks[stock]['total_weight'] + weighted, 2)
            f_label = fund_holdings[code]['name'].split()[0]
            if f_label not in all_stocks[stock]['funds']:
                all_stocks[stock]['funds'].append(f_label)
                
    top_stocks = sorted(all_stocks.values(), key=lambda x: x['total_weight'], reverse=True)[:15]
    avg_overlap = sum(p['overlap_pct'] for p in pairwise) / len(pairwise) if pairwise else 0
    diversification_score = round(max(0, 100 - avg_overlap), 1)
    
    return {
        'pairwise_overlap': pairwise,
        'top_holdings': top_stocks,
        'diversification_score': diversification_score,
        'fund_count': len(funds)
    }, None

# ==============================================================================
# FEATURE 4: MONTE CARLO SIMULATOR
# ==============================================================================
def simulate_monte_carlo(annual_return=12, annual_vol=15, investment=10000, inv_type='sip', years=10, simulations=1000):
    ann_ret = float(annual_return) / 100
    ann_v = float(annual_vol) / 100
    inv = float(investment)
    yrs = int(years)
    sims = int(simulations)
    
    np.random.seed(42)
    months = yrs * 12
    monthly_return = ann_ret / 12
    monthly_vol = ann_v / np.sqrt(12)
    
    all_paths = []
    for _ in range(sims):
        monthly_returns = np.random.normal(monthly_return, monthly_vol, months)
        portfolio_value = 0
        path = [0]
        for r in monthly_returns:
            if inv_type == 'sip':
                portfolio_value = (portfolio_value + inv) * (1 + r)
            else:
                portfolio_value = (inv * (1 + r)) if path == [0] else (portfolio_value * (1 + r))
            path.append(round(portfolio_value, 2))
        all_paths.append(path)
        
    paths_array = np.array(all_paths)
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    pct_bands = {
        f'p{p}': [round(float(np.percentile(paths_array[:, t], p)), 2) for t in range(0, months + 1, 3)]
        for p in percentiles
    }
    
    final_values = paths_array[:, -1]
    total_invested = inv * months if inv_type == 'sip' else inv
    targets = [total_invested * 2, total_invested * 3, total_invested * 5]
    target_probs = [round(float(np.mean(final_values >= t) * 100), 1) for t in targets]
    
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
    sample_indices = np.random.choice(sims, min(50, sims), replace=False)
    sample_paths = [[round(float(v), 2) for v in paths_array[i, ::3]] for i in sample_indices]
    
    return {
        'simulations': sims,
        'years': yrs,
        'time_labels': time_labels,
        'percentile_bands': pct_bands,
        'sample_paths': sample_paths[:20],
        'outcome': outcome,
        'params': {
            'annual_return': ann_ret * 100,
            'annual_vol': ann_v * 100,
            'investment': inv,
            'type': inv_type
        }
    }

# ==============================================================================
# FEATURE 5: TAX HARVESTING OPTIMIZER
# ==============================================================================
def optimize_tax_harvesting(holdings, fy_end='2026-03-31'):
    LTCG_EXEMPTION = 125000
    LTCG_TAX_RATE = 0.125
    STCG_TAX_RATE = 0.20
    
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
            if purchase_nav <= 0 or units <= 0: continue
            
            invested_value = purchase_nav * units
            current_value = current_nav * units
            gain = current_value - invested_value
            gain_pct = round((gain / invested_value) * 100, 2)
            days_to_ltcg = max(0, 366 - holding_days)
            
            if is_ltcg:
                total_ltcg += gain
                tax_type, tax_rate = 'LTCG', LTCG_TAX_RATE
            else:
                total_stcg += gain
                tax_type, tax_rate = 'STCG', STCG_TAX_RATE
                
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
        if remaining_exemption <= 0: break
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
    try: days_to_fy_end = (datetime.strptime(fy_end, '%Y-%m-%d') - datetime.now()).days
    except Exception: days_to_fy_end = 0
    near_ltcg = [a for a in analyzed if 0 < a['days_to_ltcg'] <= 30 and a['gain'] > 0]
    
    return {
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
    }

# ==============================================================================
# FEATURE 6: INTER-FUND CORRELATION MATRIX HEATMAP
# ==============================================================================
def calculate_interfund_correlation(portfolio_items, duration_years=3):
    if len(portfolio_items) < 2:
        return None, 'Need at least 2 funds for correlation analysis'
        
    codes = []
    weights = {}
    for item in portfolio_items:
        if isinstance(item, dict):
            c = str(item.get('code', ''))
            codes.append(c)
            weights[c] = float(item.get('weight', 0))
        else:
            c = str(item)
            codes.append(c)
            weights[c] = 0
            
    fund_data = []
    for c in codes:
        try:
            mf_data, rating = get_fund_raw_data(c)
            meta = mf_data.get('meta', {})
            nav_list = mf_data.get('data', [])
            nav_dict = {}
            for entry in nav_list:
                try:
                    d = datetime.strptime(entry['date'], '%d-%m-%Y')
                    nav_dict[d] = float(entry['nav'])
                except:
                    pass
            fund_data.append({
                'code': c,
                'name': meta.get('scheme_name', f'Fund {c}'),
                'category': meta.get('scheme_category', 'Equity'),
                'weight': weights.get(c, 0),
                'nav_dict': nav_dict
            })
        except Exception:
            pass
            
    if len(fund_data) < 2:
        return None, 'Could not fetch NAV history for selected funds'
        
    all_dates = set()
    for f in fund_data:
        all_dates.update(f['nav_dict'].keys())
    all_dates = sorted(list(all_dates))
    
    target_start = all_dates[-1] - timedelta(days=duration_years * 365)
    filtered_dates = [d for d in all_dates if d >= target_start]
    if len(filtered_dates) < 30:
        filtered_dates = all_dates[-120:] if len(all_dates) >= 120 else all_dates
        
    for f in fund_data:
        f_dates = sorted(f['nav_dict'].keys())
        ff_navs = {}
        curr = None
        idx = 0
        n_d = len(f_dates)
        for d in filtered_dates:
            while idx < n_d and f_dates[idx] <= d:
                curr = f['nav_dict'][f_dates[idx]]
                idx += 1
            ff_navs[d] = curr
        f['ff_navs'] = ff_navs
        
    valid_dates = [d for d in filtered_dates if all(f['ff_navs'][d] is not None for f in fund_data)]
    if len(valid_dates) < 10:
        return None, 'Insufficient overlapping dates for correlation'
        
    returns_series = []
    for f in fund_data:
        navs = [f['ff_navs'][d] for d in valid_dates]
        nav_arr = np.array(navs, dtype=float)
        denom = np.where(nav_arr[:-1] == 0, 1e-6, nav_arr[:-1])
        dr = np.diff(nav_arr) / denom
        returns_series.append(dr)
        
    returns_matrix = np.array(returns_series)
    with np.errstate(divide='ignore', invalid='ignore'):
        raw_corr = np.corrcoef(returns_matrix)
        raw_corr = np.nan_to_num(raw_corr, nan=0.0, posinf=1.0, neginf=-1.0)
    np.fill_diagonal(raw_corr, 1.0)
    
    n_funds = len(fund_data)
    matrix = [[round(float(raw_corr[i, j]), 2) for j in range(n_funds)] for i in range(n_funds)]
    pairwise = []
    for i in range(n_funds):
        for j in range(i + 1, n_funds):
            c_val = matrix[i][j]
            if c_val >= 0.85:
                sev, badge_color = 'High Redundancy', '#EF4444'
                msg = 'High correlation (>85%). Both funds move in close lockstep with high common market risk.'
            elif c_val >= 0.60:
                sev, badge_color = 'Moderate', '#F59E0B'
                msg = 'Moderate correlation. Shared equity market beta with partial category differentiation.'
            elif c_val >= 0.20:
                sev, badge_color = 'Good Diversification', '#34D399'
                msg = 'Low correlation. Healthy diversification benefit across different asset segments.'
            else:
                sev, badge_color = 'Strong Hedge', '#00D2FF'
                msg = 'Negative or near-zero correlation! Excellent hedge that stabilizes portfolio drawdown.'
                
            pairwise.append({
                'fund1': fund_data[i]['name'],
                'fund2': fund_data[j]['name'],
                'correlation': c_val,
                'severity': sev,
                'badge_color': badge_color,
                'message': msg
            })
            
    avg_corr = round(float(np.mean([p['correlation'] for p in pairwise])), 2) if pairwise else 1.0
    pdi = round(max(0.0, min(100.0, (1.0 - avg_corr) * 100)), 1)
    
    return {
        'funds': [{'code': f['code'], 'name': f['name'], 'category': f['category'], 'weight': f['weight']} for f in fund_data],
        'matrix': matrix,
        'avg_correlation': avg_corr,
        'pdi_score': pdi,
        'insights': pairwise
    }, None
