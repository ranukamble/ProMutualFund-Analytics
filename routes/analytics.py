from flask import Blueprint, jsonify, request
from services.analytics import (
    compare_funds_metrics,
    screen_funds_list,
    calculate_rolling_returns,
    analyze_portfolio_overlap,
    simulate_monte_carlo,
    optimize_tax_harvesting,
    calculate_interfund_correlation
)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/compare/funds', methods=['POST'])
def compare_funds():
    data = request.get_json() or {}
    codes = data.get('codes', [])
    results, err = compare_funds_metrics(codes)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'success': True, 'funds': results})

@analytics_bp.route('/api/screener/funds', methods=['POST'])
def screen_funds():
    data = request.get_json() or {}
    filters = data.get('filters', {})
    limit = data.get('limit', 20)
    funds, total = screen_funds_list(filters=filters, limit=limit)
    return jsonify({'success': True, 'funds': funds, 'total': total})

@analytics_bp.route('/api/rolling/returns', methods=['POST'])
def rolling_returns():
    data = request.get_json() or {}
    code = data.get('code')
    window_yrs = int(data.get('window', 3))
    if not code:
        return jsonify({'error': 'Fund code required'}), 400
    res, err = calculate_rolling_returns(code=code, window_yrs=window_yrs)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'success': True, **res})

@analytics_bp.route('/api/overlap/analyze', methods=['POST'])
def overlap_analyze():
    data = request.get_json() or {}
    funds = data.get('funds', [])
    res, err = analyze_portfolio_overlap(funds)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'success': True, **res})

@analytics_bp.route('/api/montecarlo/simulate', methods=['POST'])
def monte_carlo_simulate():
    data = request.get_json() or {}
    res = simulate_monte_carlo(
        annual_return=data.get('annual_return', 12),
        annual_vol=data.get('annual_vol', 15),
        investment=data.get('investment', 10000),
        inv_type=data.get('type', 'sip'),
        years=data.get('years', 10),
        simulations=data.get('simulations', 1000)
    )
    return jsonify({'success': True, **res})

@analytics_bp.route('/api/tax/optimize', methods=['POST'])
def tax_optimize():
    data = request.get_json() or {}
    holdings = data.get('holdings', [])
    fy_end = data.get('fy_end', '2026-03-31')
    res = optimize_tax_harvesting(holdings=holdings, fy_end=fy_end)
    return jsonify({'success': True, **res})

@analytics_bp.route('/api/portfolio/correlation', methods=['POST'])
def portfolio_correlation():
    try:
        data = request.get_json() or {}
        portfolio_items = data.get('funds', []) or data.get('portfolio', [])
        duration_years = int(data.get('duration_years', 3))
        res, err = calculate_interfund_correlation(portfolio_items, duration_years)
        if err:
            return jsonify({'error': err}), 400
        return jsonify({'success': True, **res})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
