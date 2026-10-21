import os
import json
import random
import math
from datetime import datetime, timedelta
import concurrent.futures
import numpy as np
import requests

from core.config import get_data_path
from core.extensions import normalize_scheme_category
from services.market_data import get_fund_raw_data

PORTFOLIOS_FILE = get_data_path('saved_portfolios.json')

def get_cagr(values, dates, years):
    target = dates[-1] - timedelta(days=int(years * 365.25))
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

def s_float(v):
    if v is None: return None
    try:
        v = float(v)
        if math.isnan(v) or math.isinf(v): return None
        return v
    except:
        return None

def build_generated_portfolio(portfolio_items, investment_amount=100000, investment_type='lumpsum', duration_years=5):
    """
    Core engine to compute portfolio simulation, timeline, returns, risk, and correlation matrix.
    """
    if not portfolio_items or len(portfolio_items) < 1:
        return {"error": "Add at least 1 fund"}, 400

    total_alloc = sum(f.get('allocation_pct', 0) for f in portfolio_items)
    if abs(total_alloc - 1.0) > 0.02:
        return {"error": f"Allocations must sum to 100%. Got {total_alloc*100:.1f}%"}, 400

    # Step 1: Parallel fetch NAV data
    def fetch_fund_data(item):
        code = str(item['code'])
        mf_data, rating = get_fund_raw_data(code)
        meta = mf_data.get('meta', {})
        nav_list = mf_data.get('data', [])
        nav_dict = {}
        for entry in nav_list:
            try:
                d = datetime.strptime(entry['date'], '%d-%m-%Y')
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
            'latest_date': nav_list[0]['date'] if nav_list else 'N/A',
            'rating': rating
        }

    fund_data = []
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_fund_data, item): item for item in portfolio_items}
        for fut in concurrent.futures.as_completed(futures):
            try:
                fund_data.append(fut.result())
            except Exception as e:
                errors.append(str(e))

    if errors:
        return {"error": f"Failed to fetch: {errors[0]}"}, 500

    # Step 2: Date alignment (Forward fill)
    all_dates = set()
    for f in fund_data:
        all_dates.update(f['nav_dict'].keys())
    all_dates = sorted(list(all_dates))

    if len(all_dates) < 30:
        return {"error": "Insufficient history (< 30 days)."}, 400

    target_start_date = all_dates[-1] - timedelta(days=duration_years * 365)
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

    valid_dates = [d for d in filtered_dates if all(f['ff_nav_dict'][d] is not None for f in fund_data)]
    if not valid_dates:
        return {"error": "Funds do not overlap in the given timeframe."}, 400

    sorted_dates = valid_dates

    # Step 3: Portfolio timeline
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

    # Step 4: CAGR & XIRR
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

    # Step 5: Advanced Risk Metrics
    pv_arr = np.array(portfolio_values)
    with np.errstate(divide='ignore', invalid='ignore'):
        daily_returns = np.diff(pv_arr) / pv_arr[:-1]
        volatility = float(np.std(daily_returns) * np.sqrt(252) * 100)
        volatility = s_float(round(volatility, 2)) if volatility is not None else None

    risk_free = 0.06
    port_return_ann = xirr_val/100 if xirr_val is not None else (cagr_3y/100 if cagr_3y else 0)
    sharpe = s_float(round((port_return_ann - risk_free) / (volatility / 100), 2)) if (volatility and volatility > 0) else None

    peak = pv_arr[0]
    max_dd = 0.0
    for v in pv_arr:
        if v > peak: peak = v
        if peak > 0:
            dd = (peak - v) / peak
            if dd > max_dd: max_dd = dd
    max_drawdown = s_float(round(max_dd * 100, 2))

    # Step 6: Per-fund scatter data
    scatter_data = []
    for f in fund_data:
        f_dates = sorted(f['nav_dict'].keys())
        f_vals = [f['nav_dict'][d] for d in f_dates]
        f_cagr = s_float(get_cagr(f_vals, f_dates, 3))
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

    # Step 7: Asset Allocation
    asset_map = {'Equity': 0.0, 'Debt': 0.0, 'Other': 0.0}
    scheme_map = {}
    weighted_expense_ratio = 0.0

    for f in fund_data:
        c = normalize_scheme_category(f['category'], f['name'])
        cat = c.lower()
        alloc_pct = f['allocation'] * 100
        scheme_map[c] = round(scheme_map.get(c, 0) + alloc_pct, 2)

        if 'equity' in cat or 'elss' in cat or 'index' in cat or 'etf' in cat:
            eq_exp, dt_exp, ot_exp = 100.0, 0.0, 0.0
        elif 'debt' in cat or 'liquid' in cat or 'overnight' in cat or 'gilt' in cat:
            eq_exp, dt_exp, ot_exp = 0.0, 100.0, 0.0
        elif 'gold' in cat or 'commodity' in cat or 'silver' in cat:
            eq_exp, dt_exp, ot_exp = 0.0, 0.0, 100.0
        elif 'hybrid' in cat or 'balanced' in cat or 'aggressive' in cat:
            eq_exp, dt_exp, ot_exp = 65.0, 35.0, 0.0
        else:
            eq_exp, dt_exp, ot_exp = 100.0, 0.0, 0.0

        asset_map['Equity'] += (eq_exp / 100.0) * alloc_pct
        asset_map['Debt'] += (dt_exp / 100.0) * alloc_pct
        asset_map['Other'] += (ot_exp / 100.0) * alloc_pct

        er = f.get('expense_ratio') or 0.0
        weighted_expense_ratio += (er * f['allocation'])

    total_asset = sum(asset_map.values())
    if total_asset > 0:
        for k in asset_map:
            asset_map[k] = round((asset_map[k] / total_asset) * 100, 2)

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

    # Step 8: Sample timeline
    step = max(1, len(sorted_dates) // 365)
    sampled_dates = sorted_dates[::step]
    sampled_values = portfolio_values[::step]
    if sampled_dates[-1] != sorted_dates[-1]:
        sampled_dates.append(sorted_dates[-1])
        sampled_values.append(portfolio_values[-1])

    timeline = [{'date': d.strftime('%d-%m-%Y'), 'value': round(v, 4)} for d, v in zip(sampled_dates, sampled_values)]

    # Step 9: Per-fund details
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
            'allocation_inr': round(investment_amount * f['allocation'], 2),
            'latest_nav': f['latest_nav'],
            'latest_nav_date': f.get('latest_nav_date', ''),
            'rating': f.get('rating', 0),
            'cagr_1y': get_cagr(f_vals, f_dates, 1),
            'cagr_3y': get_cagr(f_vals, f_dates, 3),
            'cagr_5y': get_cagr(f_vals, f_dates, 5),
        })

    # Step 10: Multi-Asset Correlation Matrix
    correlation_matrix = []
    corr_funds = []
    corr_insights = []
    avg_correlation = 1.0
    pdi_score = 100.0

    if len(fund_data) >= 2 and len(sorted_dates) > 5:
        try:
            returns_series = []
            for f in fund_data:
                navs = [f['ff_nav_dict'][d] for d in sorted_dates]
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
            correlation_matrix = [[round(float(raw_corr[i, j]), 2) for j in range(n_funds)] for i in range(n_funds)]
            corr_funds = [{'code': f['code'], 'name': f['name'], 'category': f['category'], 'weight': round(f['allocation'] * 100)} for f in fund_data]
            
            pairwise_corrs = []
            for i in range(n_funds):
                for j in range(i + 1, n_funds):
                    c_val = correlation_matrix[i][j]
                    pairwise_corrs.append(c_val)
                    if c_val >= 0.85:
                        severity, badge_color = 'High Redundancy', '#EF4444'
                        msg = 'High correlation (>85%). Both funds move in close lockstep with high common market risk.'
                    elif c_val >= 0.60:
                        severity, badge_color = 'Moderate', '#F59E0B'
                        msg = 'Moderate correlation. Shared equity market beta with partial category differentiation.'
                    elif c_val >= 0.20:
                        severity, badge_color = 'Good Diversification', '#34D399'
                        msg = 'Low correlation. Healthy diversification benefit across different asset segments.'
                    else:
                        severity, badge_color = 'Strong Hedge', '#00D2FF'
                        msg = 'Negative or near-zero correlation! Excellent hedge that stabilizes portfolio drawdown.'
                        
                    corr_insights.append({
                        'fund1': fund_data[i]['name'],
                        'fund2': fund_data[j]['name'],
                        'correlation': c_val,
                        'severity': severity,
                        'badge_color': badge_color,
                        'message': msg
                    })
                    
            if pairwise_corrs:
                avg_correlation = round(float(np.mean(pairwise_corrs)), 2)
                pdi_score = round(max(0.0, min(100.0, (1.0 - avg_correlation) * 100)), 1)
        except Exception as corr_err:
            print("Correlation computation warning:", corr_err)

    return {
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
            'overlap': "Overlap data unavailable",
            'date_range': {
                'start': sorted_dates[0].strftime('%d-%b-%Y'),
                'end': sorted_dates[-1].strftime('%d-%b-%Y'),
                'days': (sorted_dates[-1] - sorted_dates[0]).days
            }
        },
        'timeline': timeline,
        'asset_allocation': asset_map,
        'scheme_category': scheme_map,
        'amc_allocation': amc_map,
        'funds_detail': funds_detail,
        'scatter_data': scatter_data,
        'correlation': {
            'matrix': correlation_matrix,
            'funds': corr_funds,
            'avg_correlation': avg_correlation,
            'pdi_score': pdi_score,
            'insights': corr_insights
        }
    }, 200

# ==============================================================================
# PORTFOLIO PERSISTENCE (Save, List, Delete)
# ==============================================================================
def save_portfolio_entry(data):
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
    portfolios = portfolios[:20]
    
    os.makedirs(os.path.dirname(PORTFOLIOS_FILE), exist_ok=True)
    with open(PORTFOLIOS_FILE, 'w') as f:
        json.dump(portfolios, f, indent=2)
    return new_portfolio['id']

def list_saved_portfolios():
    if not os.path.exists(PORTFOLIOS_FILE):
        return []
    with open(PORTFOLIOS_FILE, 'r') as f:
        portfolios = json.load(f)
    for p in portfolios:
        p.pop('timeline', None)
    return portfolios

def delete_saved_portfolio(pid):
    if not os.path.exists(PORTFOLIOS_FILE):
        return False
    with open(PORTFOLIOS_FILE, 'r') as f:
        portfolios = json.load(f)
    initial_len = len(portfolios)
    portfolios = [p for p in portfolios if p.get('id') != pid]
    if len(portfolios) == initial_len:
        return False
    with open(PORTFOLIOS_FILE, 'w') as f:
        json.dump(portfolios, f, indent=2)
    return True

# ==============================================================================
# AUTO-BUILD PORTFOLIO
# ==============================================================================
def auto_build_portfolio_by_risk(risk='moderate', inv_type='sip', amount=10000, duration=5):
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
            'color': '#34D399', 'emoji': '🟢',
            'allocations': [
                {**random.choice(large_cap), 'weight': 30, 'category': 'Large Cap'},
                {**random.choice(debt), 'weight': 25, 'category': 'Debt'},
                {**random.choice(hybrid), 'weight': 25, 'category': 'Hybrid'},
                {**random.choice(liquid), 'weight': 20, 'category': 'Liquid'}
            ]
        },
        'moderate': {
            'description': 'Balanced Growth with Manageable Risk',
            'color': '#F59E0B', 'emoji': '🟡',
            'allocations': [
                {**random.choice(large_cap), 'weight': 30, 'category': 'Large Cap'},
                {**random.choice(flexi_cap), 'weight': 30, 'category': 'Flexi Cap'},
                {**random.choice(hybrid), 'weight': 25, 'category': 'Hybrid'},
                {**random.choice(debt), 'weight': 15, 'category': 'Debt'}
            ]
        },
        'aggressive': {
            'description': 'Maximum Growth, Higher Volatility',
            'color': '#F87171', 'emoji': '🔴',
            'allocations': [
                {**agg_small[0], 'weight': 30, 'category': 'Small Cap'},
                {**random.choice(mid_cap), 'weight': 25, 'category': 'Mid Cap'},
                {**random.choice(flexi_cap), 'weight': 25, 'category': 'Flexi Cap'},
                {**agg_small[1], 'weight': 20, 'category': 'Small Cap'}
            ]
        }
    }
    
    profile = fund_profiles.get(risk, fund_profiles['moderate'])
    funds_with_codes = []
    
    for fund in profile['allocations']:
        try:
            search_resp = requests.get(f"https://api.mfapi.in/mf/search?q={fund['search'].replace(' ', '%20')}", timeout=5).json()
            if search_resp:
                best = None
                for r in search_resp[:10]:
                    name_lower = r['schemeName'].lower()
                    if 'direct' in name_lower and 'growth' in name_lower and 'idcw' not in name_lower and 'dividend' not in name_lower:
                        best = r
                        break
                if not best and search_resp:
                    best = search_resp[0]
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

    def get_fallback(pool):
        try:
            f = random.choice(pool)
            res = requests.get(f"https://api.mfapi.in/mf/search?q={f['search'].replace(' ', '%20')}", timeout=5).json()
            return str(res[0]['schemeCode']) if res else None
        except:
            return None

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
        funds_with_codes = [{
            'code': f['code'],
            'name': f.get('name', f'Fund {f["code"]}'),
            'weight': f['weight'],
            'category': f['category'],
            'allocation_pct': f['weight'] / 100
        } for f in fallbacks]

    return {
        'success': True,
        'risk_profile': risk,
        'description': profile['description'],
        'color': profile['color'],
        'emoji': profile['emoji'],
        'funds': funds_with_codes,
        'inv_type': inv_type,
        'amount': amount,
        'duration': duration
    }
