import sqlite3
import os
from datetime import datetime

DB_FILE = "mutual_funds.db"

def get_db_connection():
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

# Initialize database on module load
init_db()
