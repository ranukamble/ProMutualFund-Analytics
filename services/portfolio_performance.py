"""
Portfolio Performance Tracking vs Benchmark Service Layer.

Handles:
- Recording daily portfolio snapshots
- Fetching benchmark index fund NAVs (Nifty 50, Sensex, etc.)
- Calculating returns (CAGR, volatility, Sharpe ratio, max drawdown)
- Comparing portfolio performance against benchmarks
"""

import os
import math
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.extensions import mf
from core.config import IST
from database import (
    save_portfolio_snapshot,
    get_portfolio_snapshots,
    get_latest_portfolio_snapshot,
)
from services.portfolio_builder import get_cagr
from services.market_data import get_fund_raw_data


# Benchmark index fund scheme codes (mfapi.in)
BENCHMARKS = {
    "nifty_50": {
        "name": "Nifty 50",
        "scheme_code": "119598",
        "scheme_name": "UTI Nifty 50 Index Fund - Direct Plan - Growth",
    },
    "sensex": {
        "name": "Sensex (BSE 30)",
        "scheme_code": "119597",
        "scheme_name": "SBI Sensex Index Fund - Direct Plan - Growth",
    },
    "nifty_100": {
        "name": "Nifty 100",
        "scheme_code": "120503",
        "scheme_name": "ICICI Pru Nifty 100 Index Fund - Direct Plan - Growth",
    },
    "nifty_midcap_150": {
        "name": "Nifty Midcap 150",
        "scheme_code": "118778",
        "scheme_name": "HDFC Nifty Midcap 150 Index Fund - Direct Plan - Growth",
    },
}


def get_benchmark_nav_history(scheme_code, days=365):
    """
    Fetch historical NAV data for a benchmark index fund from mfapi.in.
    Returns list of {'date': 'dd-mm-yyyy', 'nav': float} sorted ascending.
    """
    try:
        resp = requests.get(f'https://api.mfapi.in/mf/{scheme_code}', timeout=12)
        resp.raise_for_status()
        data = resp.json()
        nav_list = data.get('data', [])

        parsed = []
        for entry in nav_list:
            try:
                d = datetime.strptime(entry['date'], '%d-%m-%Y')
                nav = float(entry['nav'])
                parsed.append({'date': entry['date'], 'nav': nav, '_dt': d})
            except Exception:
                pass

        parsed.sort(key=lambda x: x['_dt'])

        if days and parsed:
            cutoff = datetime.now(IST).replace(tzinfo=None) - timedelta(days=days)
            parsed = [p for p in parsed if p['_dt'] >= cutoff]

        return [{'date': p['date'], 'nav': p['nav']} for p in parsed]
    except Exception as e:
        print(f"[Benchmark] Error fetching {scheme_code}: {e}")
        return []


def get_all_benchmark_histories(days=365):
    """Fetch NAV history for all configured benchmarks."""
    results = {}
    for key, info in BENCHMARKS.items():
        results[key] = {
            'name': info['name'],
            'scheme_code': info['scheme_code'],
            'scheme_name': info['scheme_name'],
            'history': get_benchmark_nav_history(info['scheme_code'], days=days),
        }
    return results


def calculate_returns_from_navs(nav_list):
    """
    Calculate returns metrics from a sorted NAV list (ascending by date).
    """
    if not nav_list or len(nav_list) < 2:
        return {
            'absolute_return': None,
            'cagr': None,
            'volatility': None,
            'sharpe_ratio': None,
            'max_drawdown': None,
            'start_nav': None,
            'end_nav': None,
        }

    navs = [float(n['nav']) for n in nav_list]
    start_nav = navs[0]
    end_nav = navs[-1]

    absolute_return = round(((end_nav - start_nav) / start_nav) * 100, 2)

    start_date = datetime.strptime(nav_list[0]['date'], '%d-%m-%Y')
    end_date = datetime.strptime(nav_list[-1]['date'], '%d-%m-%Y')
    years = (end_date - start_date).days / 365.25
    cagr = None
    if years > 0 and start_nav > 0:
        cagr = round(((end_nav / start_nav) ** (1 / years) - 1) * 100, 2)

    volatility = None
    if len(navs) > 30:
        daily_returns = [
            (navs[i] - navs[i - 1]) / navs[i - 1]
            for i in range(1, len(navs))
            if navs[i - 1] != 0
        ]
        if daily_returns:
            mean_daily = sum(daily_returns) / len(daily_returns)
            variance = sum((r - mean_daily) ** 2 for r in daily_returns) / len(daily_returns)
            volatility = round(math.sqrt(variance) * math.sqrt(252) * 100, 2)

    sharpe_ratio = None
    if cagr is not None and volatility is not None and volatility > 0:
        sharpe_ratio = round((cagr - 6) / volatility, 2)

    max_drawdown = 0
    peak = navs[0]
    for nav in navs:
        if nav > peak:
            peak = nav
        if peak > 0:
            dd = (peak - nav) / peak
            if dd > max_drawdown:
                max_drawdown = dd
    max_drawdown = round(max_drawdown * 100, 2)

    return {
        'absolute_return': absolute_return,
        'cagr': cagr,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'start_nav': round(start_nav, 4),
        'end_nav': round(end_nav, 4),
    }


def calculate_portfolio_value(portfolio_items):
    """
    Calculate current total value of a portfolio from live NAVs.
    portfolio_items: list of {'code': str, 'allocation_pct': float, 'amount': float}
    Returns (total_value, total_invested, fund_details)
    """
    total_value = 0.0
    total_invested = 0.0
    fund_details = []

    def fetch_and_calc(item):
        code = str(item['code']).strip()
        allocation_pct = float(item.get('allocation_pct', 0))
        amount = float(item.get('amount', 0))

        try:
            mf_data, rating = get_fund_raw_data(code)
            nav_list = mf_data.get('data', [])
            meta = mf_data.get('meta', {})
            latest_nav = float(nav_list[0]['nav']) if nav_list else 0
            units = amount / latest_nav if latest_nav > 0 else 0
            current_value = units * latest_nav

            return {
                'code': code,
                'name': meta.get('scheme_name', f'Fund {code}'),
                'amc': meta.get('fund_house', 'Unknown'),
                'allocation_pct': allocation_pct,
                'amount_invested': amount,
                'latest_nav': latest_nav,
                'units': units,
                'current_value': current_value,
                'gain': current_value - amount,
                'gain_pct': round(((current_value - amount) / amount) * 100, 2) if amount > 0 else 0,
            }
        except Exception as e:
            print(f"[Performance] Error fetching {code}: {e}")
            return {
                'code': code,
                'name': f'Fund {code}',
                'amc': 'Unknown',
                'allocation_pct': allocation_pct,
                'amount_invested': amount,
                'latest_nav': 0,
                'units': 0,
                'current_value': 0,
                'gain': 0,
                'gain_pct': 0,
                'error': str(e),
            }

    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_and_calc, item): item for item in portfolio_items}
        for fut in as_completed(futures):
            result = fut.result()
            total_value += result['current_value']
            total_invested += result['amount_invested']
            fund_details.append(result)

    fund_details.sort(key=lambda x: x['current_value'], reverse=True)
    return round(total_value, 2), round(total_invested, 2), fund_details


def record_daily_snapshot(portfolio_id, portfolio_items, benchmark='nifty_50'):
    """
    Record today's portfolio performance snapshot including benchmark comparison.
    """
    from datetime import date

    today = date.today().isoformat()

    total_value, total_invested, fund_details = calculate_portfolio_value(portfolio_items)

    benchmark_info = BENCHMARKS.get(benchmark, BENCHMARKS['nifty_50'])
    benchmark_history = get_benchmark_nav_history(
        benchmark_info['scheme_code'], days=365 * 3
    )

    benchmark_nifty_50 = None
    benchmark_sensex = None

    if benchmark == 'nifty_50' and benchmark_history:
        benchmark_nifty_50 = benchmark_history[-1]['nav'] if benchmark_history else None
    if benchmark == 'sensex' and benchmark_history:
        benchmark_sensex = benchmark_history[-1]['nav'] if benchmark_history else None

    snapshot_id = save_portfolio_snapshot(
        portfolio_id=portfolio_id,
        snapshot_date=today,
        total_value=total_value,
        total_invested=total_invested,
        cagr_1y=None,
        cagr_3y=None,
        benchmark_nifty_50=benchmark_nifty_50,
        benchmark_sensex=benchmark_sensex,
    )

    return {
        'snapshot_id': snapshot_id,
        'date': today,
        'total_value': total_value,
        'total_invested': total_invested,
        'gain': round(total_value - total_invested, 2),
        'gain_pct': round(((total_value - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0,
        'funds': fund_details,
        'benchmark': {
            'key': benchmark,
            'name': benchmark_info['name'],
            'scheme_code': benchmark_info['scheme_code'],
            'latest_nav': benchmark_nifty_50 or benchmark_sensex,
        },
    }


def get_performance_comparison(portfolio_id, days=365, benchmark='nifty_50'):
    """
    Get portfolio performance history compared against a benchmark.
    """
    snapshots = get_portfolio_snapshots(portfolio_id, days=days)
    snapshots.sort(key=lambda x: x['snapshot_date'])

    benchmark_info = BENCHMARKS.get(benchmark, BENCHMARKS['nifty_50'])
    benchmark_history = get_benchmark_nav_history(
        benchmark_info['scheme_code'], days=days
    )

    portfolio_metrics = None
    if snapshots:
        first_val = snapshots[0]['total_value']
        last_val = snapshots[-1]['total_value']
        first_inv = snapshots[0]['total_invested']
        last_inv = snapshots[-1]['total_invested']

        portfolio_metrics = {
            'start_value': first_val,
            'end_value': last_val,
            'start_invested': first_inv,
            'end_invested': last_inv,
            'absolute_return': round(((last_val - first_inv) / first_inv) * 100, 2) if first_inv > 0 else 0,
            'total_gain': round(last_val - last_inv, 2),
        }

    benchmark_metrics = calculate_returns_from_navs(benchmark_history)

    chart_data = []
    for snap in snapshots:
        chart_data.append({
            'date': snap['snapshot_date'],
            'portfolio_value': snap['total_value'],
            'portfolio_invested': snap['total_invested'],
        })

    return {
        'portfolio_id': portfolio_id,
        'benchmark': {
            'key': benchmark,
            'name': benchmark_info['name'],
            'scheme_code': benchmark_info['scheme_code'],
        },
        'portfolio_metrics': portfolio_metrics,
        'benchmark_metrics': benchmark_metrics,
        'snapshots': snapshots,
        'chart_data': chart_data,
        'benchmark_history': benchmark_history,
    }


def get_available_benchmarks():
    """Return list of available benchmarks."""
    return [
        {
            'key': key,
            'name': info['name'],
            'scheme_code': info['scheme_code'],
            'scheme_name': info['scheme_name'],
        }
        for key, info in BENCHMARKS.items()
    ]