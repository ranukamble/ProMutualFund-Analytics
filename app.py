import os
from flask import Flask

from core.config import config_by_name
from core.extensions import cache, socketio
from services.market_data import start_background_amfi_sync, start_popular_funds_scheduler

# Import Blueprints
from routes.auth import auth_bp
from routes.views import views_bp
from routes.funds import funds_bp
from routes.portfolio import portfolio_bp
from routes.analytics import analytics_bp
from routes.market import market_bp
from routes.ai import ai_bp

def create_app(config_name=None):
    """
    Application Factory Pattern for Pro Mutual Fund Analytics.
    Initializes Flask application, registers configurations, extensions,
    and modular blueprints.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize Extensions
    cache.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(funds_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(ai_bp)

    # Register WebSocket Event Listeners & Start Real-Time Streamer
    from services.websocket_streamer import register_socket_events, start_realtime_streamer
    register_socket_events(app)
    start_realtime_streamer()

    # Start Background Schedulers
    start_background_amfi_sync()
    start_popular_funds_scheduler()

    return app

# WSGI Application Entry Point
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Pro Mutual Fund Analytics on port {port}...")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
