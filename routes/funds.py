import os
import json
from flask import Blueprint, jsonify, request
from core.extensions import cache, require_api_key, mf
from core.config import get_data_path
from services.market_data import (
    get_all_schemes_list, 
    get_quote_data, 
    get_advanced_metrics
)

funds_bp = Blueprint('funds', __name__)

@funds_bp.route('/api/schemes')
@require_api_key
@cache.cached(timeout=86400)
def get_all_schemes():
    schemes = get_all_schemes_list()
    return jsonify(schemes)

@funds_bp.route('/api/all-funds')
@require_api_key
def get_all_funds():
    try:
        scheme_path = get_data_path('scheme_codes.json')
        with open(scheme_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        funds_list = [{"code": k, "name": v} for k, v in data.items()]
        return jsonify(funds_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@funds_bp.route('/api/quote/<code>')
@require_api_key
def get_quote(code):
    try:
        result, err = get_quote_data(code)
        if err:
            return jsonify({"error": err}), 404
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@funds_bp.route('/api/history/<code>')
@require_api_key
def get_history(code):
    history = None
    try:
        history = mf.get_scheme_historical_nav(code)
    except Exception:
        history = None
    if not history or 'data' not in history or not isinstance(history.get('data'), list) or len(history.get('data', [])) == 0:
        try:
            import requests
            resp = requests.get(f'https://api.mfapi.in/mf/{code}', timeout=8)
            if resp.ok:
                history = resp.json()
        except Exception:
            pass
    if not history or 'data' not in history:
        return jsonify({"error": "History not found"}), 404
    return jsonify(history)

@funds_bp.route('/api/advanced/<code>')
@require_api_key
def get_advanced(code):
    try:
        metrics = get_advanced_metrics(code)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@funds_bp.route('/api/all-in-one/<code>')
@require_api_key
def get_all_in_one(code):
    try:
        quote_res, err = get_quote_data(code)
        if err:
            return jsonify({"error": err}), 404
            
        history_res = None
        try:
            history_res = mf.get_scheme_historical_nav(code)
        except Exception:
            pass
        if not history_res or 'data' not in history_res:
            try:
                import requests
                resp = requests.get(f'https://api.mfapi.in/mf/{code}', timeout=8)
                if resp.ok: history_res = resp.json()
            except Exception: pass
            
        advanced_res = get_advanced_metrics(code)
        
        return jsonify({
            "quote": quote_res.get("quote", {}),
            "scraped": quote_res.get("scraped", {}),
            "advanced": advanced_res,
            "history": history_res.get("data", []) if history_res else []
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@funds_bp.route('/api/all-in-one/bulk')
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
            q_res, err = get_quote_data(code)
            if err: continue
            
            h_res = None
            try: h_res = mf.get_scheme_historical_nav(code)
            except Exception: pass
            
            a_res = get_advanced_metrics(code)
            
            results.append({
                "code": code,
                "quote": q_res.get("quote", {}),
                "scraped": q_res.get("scraped", {}),
                "advanced": a_res,
                "history": h_res.get("data", []) if h_res else []
            })
        except Exception:
            pass
            
    return jsonify(results)
