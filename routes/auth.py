import os
from flask import Blueprint, render_template, jsonify, send_from_directory, current_app, Response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login():
    return render_template('login.html')

@auth_bp.route('/manifest.json')
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

@auth_bp.route('/sw.js')
def service_worker():
    sw = '''
    self.addEventListener('install', function(e) {
      self.skipWaiting();
    });
    self.addEventListener('fetch', function(e) {
      // Empty fetch handler to satisfy PWA install requirements
    });
    '''
    return Response(sw, mimetype='application/javascript')

@auth_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'logo.png', mimetype='image/png')
