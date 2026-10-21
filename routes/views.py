import os
from flask import Blueprint, render_template, request, redirect, jsonify, Response, current_app
from services.market_data import get_fund_raw_data
from services.portfolio_builder import list_saved_portfolios

views_bp = Blueprint('views', __name__)

@views_bp.route('/dashboard')
def dashboard():
    template_path = os.path.join(current_app.root_path, 'templates', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    response = Response(html_content, mimetype='text/html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@views_bp.route('/news')
def news_page():
    template_path = os.path.join(current_app.root_path, 'templates', 'news.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        response = Response(html_content, mimetype='text/html')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return redirect('/dashboard?view=news')

@views_bp.route('/portfolio/report/<int:pid>')
def portfolio_report(pid):
    try:
        portfolios = list_saved_portfolios()
        portfolio = next((p for p in portfolios if p.get('id') == pid), None)
        if not portfolio:
            return "Portfolio not found", 404
        return render_template('portfolio_report.html', portfolio=portfolio)
    except Exception as e:
        return str(e), 500

@views_bp.route('/mf/<code>')
@views_bp.route('/scheme/<code>')
@views_bp.route('/fund/<code>')
def mf_direct_route(code):
    accept = request.headers.get('Accept', '')
    if request.args.get('json') or (accept.startswith('application/json') and not accept.startswith('text/html')):
        try:
            mf_data, rating = get_fund_raw_data(code)
            return jsonify(mf_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 404
    return redirect(f'/dashboard?fund={code}')

@views_bp.route('/verify')
@views_bp.route('/verify/<code>')
def verify_page(code=None):
    template_path = os.path.join(current_app.root_path, 'templates', 'verifier.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        response = Response(html_content, mimetype='text/html')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "Verification template not found", 404
