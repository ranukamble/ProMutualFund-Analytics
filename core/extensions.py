from functools import wraps
from flask import request, jsonify
from flask_caching import Cache
from flask_socketio import SocketIO
from mftool import Mftool
from core.config import API_KEY

# Application Extensions
cache = Cache()
socketio = SocketIO(cors_allowed_origins="*")
mf = Mftool()

# In-memory store for async background tasks
TASKS = {}

def require_api_key(f):
    """
    Decorator to protect API routes with API key, referer check, or local address whitelist.
    """
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
            
        # Allow direct local requests (e.g., testing in browser address bar or local scripts)
        client_ip = request.remote_addr or ''
        host_name = request.host.split(':')[0]
        if client_ip in ('127.0.0.1', 'localhost', '::1') or host_name in ('127.0.0.1', 'localhost') or client_ip.startswith('192.168.') or host_name.startswith(('127.0.0.1', 'localhost', '192.168.')):
            return f(*args, **kwargs)
            
        return jsonify({"error": "Unauthorized. Please provide ?api_key= in the URL."}), 401
    return decorated_function


def normalize_scheme_category(raw_category, scheme_name):
    """
    Standardize varied mutual fund category names based on raw category and scheme name keywords.
    """
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
