import os
from datetime import timedelta, timezone

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Timezone
IST = timezone(timedelta(hours=5, minutes=30))

# Automatically load .env if present
def _load_env_file():
    env_file = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

def get_data_path(filename):
    """
    Returns absolute path for data files, checking data/ directory first,
    then root directory as fallback.
    """
    path_in_data = os.path.join(DATA_DIR, filename)
    if os.path.exists(path_in_data):
        return path_in_data
    path_in_root = os.path.join(BASE_DIR, filename)
    if os.path.exists(path_in_root):
        return path_in_root
    # Default to data dir if neither exists yet
    return path_in_data

# Global Constants
API_KEY = os.getenv("API_KEY", "POWER_BI_KEY_2026")
PORTFOLIOS_FILE = get_data_path("saved_portfolios.json")
ACTIVE_FUNDS_FILE = get_data_path("active_funds.json")
SCHEME_CODES_FILE = get_data_path("scheme_codes.json")

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "pro-mutual-fund-analytics-secret-key-2026")
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 86400  # 24 hours

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig if os.getenv('FLASK_ENV') == 'production' else DevelopmentConfig
}
