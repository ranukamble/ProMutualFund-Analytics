import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from core.config import IST
from services.market_data import (
    AMFI_SYNC_STATE,
    sync_amfi_nav_data,
    get_real_market_mood,
    get_real_market_ticker,
    get_live_news_feed,
    _news_cache
)

market_bp = Blueprint('market', __name__)

@market_bp.route('/api/sync/status', methods=['GET'])
def get_sync_status():
    global AMFI_SYNC_STATE
    enabled = os.getenv("ENABLE_BACKGROUND_SYNC", "false").strip().lower() in ("true", "1", "yes")
    AMFI_SYNC_STATE["enabled"] = enabled
    
    if not AMFI_SYNC_STATE["next_sync"]:
        sync_hour = int(os.getenv("AMFI_SYNC_HOUR_IST", "21"))
        sync_minute = int(os.getenv("AMFI_SYNC_MINUTE_IST", "0"))
        now_ist = datetime.now(IST)
        target_ist = now_ist.replace(hour=sync_hour, minute=sync_minute, second=0, microsecond=0)
        if now_ist >= target_ist:
            target_ist += timedelta(days=1)
        AMFI_SYNC_STATE["next_sync"] = target_ist.strftime("%d-%m-%Y %I:%M:%S %p IST")
        
    return jsonify({
        "success": True,
        "sync_state": AMFI_SYNC_STATE,
        "schedule": "Daily at 9:00 PM IST (21:00 IST)"
    })

@market_bp.route('/api/sync/trigger', methods=['POST'])
def trigger_manual_sync():
    result = sync_amfi_nav_data(manual=True)
    return jsonify(result)

@market_bp.route('/api/market-mood')
def get_market_mood_route():
    try:
        return jsonify(get_real_market_mood())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@market_bp.route('/api/market-ticker')
def get_market_ticker_route():
    try:
        return jsonify(get_real_market_ticker())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@market_bp.route('/api/news')
def get_news_route():
    try:
        import importlib
        import services.market_data as smd
        importlib.reload(smd)
        if hasattr(smd, '_news_cache') and isinstance(smd._news_cache, dict):
            smd._news_cache.get("data", {}).clear()
            smd._news_cache.get("timestamp", {}).clear()
        cat = request.args.get('category', 'all').lower().strip()
        mode = request.args.get('mode', 'financial').lower().strip()
        city = request.args.get('city', 'all').lower().strip()
        query = request.args.get('q', '').strip() or None
        lang = request.args.get('lang', 'en').lower().strip()
        data = smd.get_live_news_feed(category=cat, custom_query=query, mode=mode, city=city, lang=lang)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "articles": []}), 500

@market_bp.route('/api/stream/stats')
def get_stream_stats():
    try:
        from services.websocket_streamer import CONNECTED_CLIENTS, _last_broadcast_ticker
        return jsonify({
            "status": "online",
            "protocol": "WebSocket / Socket.IO",
            "active_connected_clients": len(CONNECTED_CLIENTS),
            "broadcaster": "Active (Daemon Thread)",
            "last_broadcast": (_last_broadcast_ticker or {}).get("payload", {}).get("timestamp", "Pending")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


