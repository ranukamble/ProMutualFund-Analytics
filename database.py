import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "mutual_funds.db") if os.path.exists(os.path.join(DATA_DIR, "mutual_funds.db")) else os.path.join(BASE_DIR, "mutual_funds.db")

def get_db_connection():
    if not os.path.exists(os.path.dirname(DB_FILE)):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Table for fund metadata
    c.execute('''
        CREATE TABLE IF NOT EXISTS funds (
            code TEXT PRIMARY KEY,
            name TEXT,
            amc TEXT,
            category TEXT,
            rating INTEGER,
            last_updated TIMESTAMP
        )
    ''')
    # Table for historical NAV data
    c.execute('''
        CREATE TABLE IF NOT EXISTS nav_history (
            code TEXT,
            date TEXT,
            nav REAL,
            PRIMARY KEY (code, date)
        )
    ''')
    conn.commit()
    conn.close()

def save_fund_data(code, meta, nav_list, rating=0):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Save or update metadata
    c.execute('''
        INSERT OR REPLACE INTO funds (code, name, amc, category, rating, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        code, 
        meta.get('scheme_name', ''), 
        meta.get('fund_house', ''), 
        meta.get('scheme_category', ''), 
        rating, 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    # Batch insert NAV data
    # nav_list is typically [{'date': 'dd-mm-yyyy', 'nav': '12.34'}]
    records = []
    for entry in nav_list:
        try:
            # Convert dd-mm-yyyy to yyyy-mm-dd for better sorting in DB
            d = datetime.strptime(entry['date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            nav_val = float(entry['nav'])
            records.append((code, d, nav_val))
        except:
            pass
            
    c.executemany('''
        INSERT OR IGNORE INTO nav_history (code, date, nav)
        VALUES (?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()

def get_fund_from_db(code):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if fund exists and was updated recently
    c.execute("SELECT * FROM funds WHERE code = ?", (code,))
    fund = c.fetchone()
    
    if not fund:
        conn.close()
        return None
        
    # Check if it was updated today
    last_updated = datetime.strptime(fund['last_updated'], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_updated).days >= 1:
        # Data is older than 1 day, let's fetch fresh data
        conn.close()
        return None
        
    # Get NAV history
    c.execute("SELECT date, nav FROM nav_history WHERE code = ? ORDER BY date DESC", (code,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None
        
    # Reconstruct the mfapi.in response structure so app.py doesn't break
    meta = {
        'scheme_name': fund['name'],
        'fund_house': fund['amc'],
        'scheme_category': fund['category']
    }
    
    nav_list = []
    for r in rows:
        # Convert back to dd-mm-yyyy
        d = datetime.strptime(r['date'], '%Y-%m-%d').strftime('%d-%m-%Y')
        nav_list.append({'date': d, 'nav': str(r['nav'])})
        
    mf_data = {'meta': meta, 'data': nav_list}
    return mf_data, fund['rating']


def init_portfolio_snapshots_table():
    """Create portfolio_snapshots table for performance tracking."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            snapshot_date DATE NOT NULL,
            total_value REAL NOT NULL,
            total_invested REAL NOT NULL,
            cagr_1y REAL,
            cagr_3y REAL,
            benchmark_nifty_50 REAL,
            benchmark_sensex REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    ''')
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_pid_date
        ON portfolio_snapshots (portfolio_id, snapshot_date)
    ''')
    conn.commit()
    conn.close()


def save_portfolio_snapshot(portfolio_id, snapshot_date, total_value, total_invested,
                            cagr_1y=None, cagr_3y=None, benchmark_nifty_50=None,
                            benchmark_sensex=None):
    """Save a daily portfolio performance snapshot."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO portfolio_snapshots
        (portfolio_id, snapshot_date, total_value, total_invested, cagr_1y, cagr_3y,
         benchmark_nifty_50, benchmark_sensex)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (portfolio_id, snapshot_date, total_value, total_invested, cagr_1y, cagr_3y,
          benchmark_nifty_50, benchmark_sensex))
    snapshot_id = c.lastrowid
    conn.commit()
    conn.close()
    return snapshot_id


def get_portfolio_snapshots(portfolio_id, days=365):
    """Get performance snapshots for a portfolio over the last N days."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT snapshot_date, total_value, total_invested, cagr_1y, cagr_3y,
               benchmark_nifty_50, benchmark_sensex, created_at
        FROM portfolio_snapshots
        WHERE portfolio_id = ?
        ORDER BY snapshot_date DESC
        LIMIT ?
    ''', (portfolio_id, days))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_portfolio_snapshot(portfolio_id):
    """Get the most recent snapshot for a portfolio."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT snapshot_date, total_value, total_invested, cagr_1y, cagr_3y,
               benchmark_nifty_50, benchmark_sensex, created_at
        FROM portfolio_snapshots
        WHERE portfolio_id = ?
        ORDER BY snapshot_date DESC
        LIMIT 1
    ''', (portfolio_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# Initialize database on module load
init_db()
init_portfolio_snapshots_table()
