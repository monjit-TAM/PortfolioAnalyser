import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import hashlib
import secrets

class Database:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
    
    def get_connection(self):
        return psycopg2.connect(self.database_url)
    
    def init_tables(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                phone VARCHAR(20),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        cur.execute('''
            ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                file_name VARCHAR(255),
                stock_count INTEGER,
                total_investment DECIMAL(15,2),
                current_value DECIMAL(15,2),
                total_gain_loss DECIMAL(15,2),
                stocks_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                activity_type VARCHAR(50),
                details VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stock_symbols (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255),
                sector VARCHAR(100),
                category VARCHAR(50),
                exchange VARCHAR(10) DEFAULT 'NSE',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS symbol_aliases (
                id SERIAL PRIMARY KEY,
                alias VARCHAR(50) UNIQUE NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS market_indices (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sectors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description VARCHAR(255),
                target_allocation DECIMAL(5,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alternative_stocks (
                id SERIAL PRIMARY KEY,
                sector VARCHAR(100) NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sector, symbol)
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS rebalancing_strategies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description VARCHAR(255),
                large_cap_target DECIMAL(5,2),
                mid_cap_target DECIMAL(5,2),
                small_cap_target DECIMAL(5,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
    
    def seed_initial_data(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM stock_symbols")
        if cur.fetchone()[0] == 0:
            stocks = [
                ('RELIANCE', 'Reliance Industries Ltd', 'Energy', 'Large Cap', 'NSE'),
                ('TCS', 'Tata Consultancy Services', 'Technology', 'Large Cap', 'NSE'),
                ('HDFCBANK', 'HDFC Bank Ltd', 'Banking', 'Large Cap', 'NSE'),
                ('INFY', 'Infosys Ltd', 'Technology', 'Large Cap', 'NSE'),
                ('ICICIBANK', 'ICICI Bank Ltd', 'Banking', 'Large Cap', 'NSE'),
                ('KOTAKBANK', 'Kotak Mahindra Bank', 'Banking', 'Large Cap', 'NSE'),
                ('HINDUNILVR', 'Hindustan Unilever', 'FMCG', 'Large Cap', 'NSE'),
                ('SBIN', 'State Bank of India', 'Banking', 'Large Cap', 'NSE'),
                ('BHARTIARTL', 'Bharti Airtel Ltd', 'Telecom', 'Large Cap', 'NSE'),
                ('ITC', 'ITC Ltd', 'FMCG', 'Large Cap', 'NSE'),
                ('ASIANPAINT', 'Asian Paints Ltd', 'Paints', 'Large Cap', 'NSE'),
                ('MARUTI', 'Maruti Suzuki India', 'Automobile', 'Large Cap', 'NSE'),
                ('AXISBANK', 'Axis Bank Ltd', 'Banking', 'Large Cap', 'NSE'),
                ('LT', 'Larsen & Toubro', 'Construction', 'Large Cap', 'NSE'),
                ('SUNPHARMA', 'Sun Pharmaceutical', 'Pharmaceuticals', 'Large Cap', 'NSE'),
                ('TITAN', 'Titan Company Ltd', 'Jewellery', 'Large Cap', 'NSE'),
                ('ULTRACEMCO', 'UltraTech Cement', 'Cement', 'Large Cap', 'NSE'),
                ('NESTLEIND', 'Nestle India Ltd', 'FMCG', 'Large Cap', 'NSE'),
                ('WIPRO', 'Wipro Ltd', 'Technology', 'Large Cap', 'NSE'),
                ('HCLTECH', 'HCL Technologies', 'Technology', 'Large Cap', 'NSE'),
                ('BAJFINANCE', 'Bajaj Finance Ltd', 'Finance', 'Large Cap', 'NSE'),
                ('BAJAJFINSV', 'Bajaj Finserv Ltd', 'Finance', 'Large Cap', 'NSE'),
                ('ADANIENT', 'Adani Enterprises', 'Conglomerate', 'Large Cap', 'NSE'),
                ('ADANIPORTS', 'Adani Ports', 'Infrastructure', 'Large Cap', 'NSE'),
                ('ONGC', 'Oil & Natural Gas Corp', 'Energy', 'Large Cap', 'NSE'),
                ('NTPC', 'NTPC Ltd', 'Power', 'Large Cap', 'NSE'),
                ('POWERGRID', 'Power Grid Corp', 'Power', 'Large Cap', 'NSE'),
                ('TATAMOTORS', 'Tata Motors Ltd', 'Automobile', 'Large Cap', 'NSE'),
                ('TATAPOWER', 'Tata Power Company', 'Power', 'Mid Cap', 'NSE'),
                ('TATASTEEL', 'Tata Steel Ltd', 'Metals', 'Large Cap', 'NSE'),
                ('TECHM', 'Tech Mahindra Ltd', 'Technology', 'Large Cap', 'NSE'),
                ('DRREDDY', 'Dr Reddys Labs', 'Pharmaceuticals', 'Large Cap', 'NSE'),
                ('CIPLA', 'Cipla Ltd', 'Pharmaceuticals', 'Large Cap', 'NSE'),
                ('LUPIN', 'Lupin Ltd', 'Pharmaceuticals', 'Mid Cap', 'NSE'),
                ('BRITANNIA', 'Britannia Industries', 'FMCG', 'Large Cap', 'NSE'),
                ('IOC', 'Indian Oil Corp', 'Energy', 'Large Cap', 'NSE'),
                ('BPCL', 'Bharat Petroleum', 'Energy', 'Large Cap', 'NSE'),
                ('BAJAJ-AUTO', 'Bajaj Auto Ltd', 'Automobile', 'Large Cap', 'NSE'),
                ('M&M', 'Mahindra & Mahindra', 'Automobile', 'Large Cap', 'NSE'),
            ]
            
            for stock in stocks:
                cur.execute('''
                    INSERT INTO stock_symbols (symbol, name, sector, category, exchange) 
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (symbol) DO NOTHING
                ''', stock)
        
        cur.execute("SELECT COUNT(*) FROM symbol_aliases")
        if cur.fetchone()[0] == 0:
            aliases = [
                ('RIL', 'RELIANCE'),
                ('ICICI', 'ICICIBANK'),
                ('HDFC', 'HDFCBANK'),
                ('KOTAK', 'KOTAKBANK'),
                ('SBI', 'SBIN'),
                ('BHARTI', 'BHARTIARTL'),
                ('HINDUNILEVER', 'HINDUNILVR'),
                ('HUL', 'HINDUNILVR'),
                ('ADANI', 'ADANIENT'),
            ]
            
            for alias, symbol in aliases:
                cur.execute('''
                    INSERT INTO symbol_aliases (alias, symbol) 
                    VALUES (%s, %s) ON CONFLICT (alias) DO NOTHING
                ''', (alias, symbol))
        
        cur.execute("SELECT COUNT(*) FROM market_indices")
        if cur.fetchone()[0] == 0:
            indices = [
                ('NIFTY50', '^NSEI', 'NSE Nifty 50 Index'),
                ('NIFTY_MIDCAP_100', '^NSEMDCP50', 'NSE Nifty Midcap 100 Index'),
                ('NIFTY_SMALLCAP_100', '^NSESMLCAP', 'NSE Nifty Smallcap 100 Index'),
                ('SENSEX', '^BSESN', 'BSE Sensex Index'),
            ]
            
            for name, symbol, desc in indices:
                cur.execute('''
                    INSERT INTO market_indices (name, symbol, description) 
                    VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING
                ''', (name, symbol, desc))
        
        cur.execute("SELECT COUNT(*) FROM sectors")
        if cur.fetchone()[0] == 0:
            sectors = [
                ('Banking', 'Financial sector including banks', 15),
                ('Technology', 'IT and software services', 15),
                ('Energy', 'Oil, gas and energy companies', 10),
                ('FMCG', 'Fast moving consumer goods', 10),
                ('Pharmaceuticals', 'Healthcare and pharma', 10),
                ('Automobile', 'Auto manufacturers', 10),
                ('Telecom', 'Telecommunications', 5),
                ('Construction', 'Infrastructure and construction', 5),
                ('Paints', 'Paint and coatings', 3),
                ('Jewellery', 'Gems and jewellery', 3),
                ('Cement', 'Cement manufacturers', 4),
                ('Metals', 'Steel and metals', 5),
                ('Power', 'Power generation and distribution', 5),
            ]
            
            for name, desc, target in sectors:
                cur.execute('''
                    INSERT INTO sectors (name, description, target_allocation) 
                    VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING
                ''', (name, desc, target))
        
        cur.execute("SELECT COUNT(*) FROM alternative_stocks")
        if cur.fetchone()[0] == 0:
            alternatives = [
                ('Banking', 'HDFCBANK', 1), ('Banking', 'ICICIBANK', 2), ('Banking', 'KOTAKBANK', 3), ('Banking', 'SBIN', 4), ('Banking', 'AXISBANK', 5),
                ('Technology', 'TCS', 1), ('Technology', 'INFY', 2), ('Technology', 'WIPRO', 3), ('Technology', 'HCLTECH', 4), ('Technology', 'TECHM', 5),
                ('Energy', 'RELIANCE', 1), ('Energy', 'ONGC', 2), ('Energy', 'IOC', 3), ('Energy', 'BPCL', 4),
                ('FMCG', 'HINDUNILVR', 1), ('FMCG', 'ITC', 2), ('FMCG', 'NESTLEIND', 3), ('FMCG', 'BRITANNIA', 4),
                ('Automobile', 'MARUTI', 1), ('Automobile', 'TATAMOTORS', 2), ('Automobile', 'BAJAJ-AUTO', 3), ('Automobile', 'M&M', 4),
                ('Pharmaceuticals', 'SUNPHARMA', 1), ('Pharmaceuticals', 'DRREDDY', 2), ('Pharmaceuticals', 'CIPLA', 3), ('Pharmaceuticals', 'LUPIN', 4),
            ]
            
            for sector, symbol, priority in alternatives:
                cur.execute('''
                    INSERT INTO alternative_stocks (sector, symbol, priority) 
                    VALUES (%s, %s, %s) ON CONFLICT (sector, symbol) DO NOTHING
                ''', (sector, symbol, priority))
        
        cur.execute("SELECT COUNT(*) FROM rebalancing_strategies")
        if cur.fetchone()[0] == 0:
            strategies = [
                ('Conservative', 'Low risk strategy for capital preservation', 70, 20, 10),
                ('Balanced', 'Balanced approach for moderate growth', 50, 30, 20),
                ('Aggressive', 'High risk strategy for maximum growth', 30, 40, 30),
            ]
            
            for name, desc, large, mid, small in strategies:
                cur.execute('''
                    INSERT INTO rebalancing_strategies (name, description, large_cap_target, mid_cap_target, small_cap_target) 
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (name) DO NOTHING
                ''', (name, desc, large, mid, small))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_stock_symbols(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT symbol, name, sector, category FROM stock_symbols WHERE is_active = TRUE")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return {row['symbol']: {'name': row['name'], 'sector': row['sector'], 'category': row['category']} for row in results}
    
    def get_symbol_aliases(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT alias, symbol FROM symbol_aliases")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return {row['alias']: row['symbol'] for row in results}
    
    def get_market_indices(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, symbol FROM market_indices WHERE is_active = TRUE")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return {row['name']: row['symbol'] for row in results}
    
    def get_sectors(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, target_allocation FROM sectors")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return {row['name']: float(row['target_allocation']) for row in results}
    
    def get_alternative_stocks(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT sector, symbol FROM alternative_stocks ORDER BY sector, priority")
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        alternatives = {}
        for row in results:
            sector = row['sector']
            if sector not in alternatives:
                alternatives[sector] = []
            alternatives[sector].append(row['symbol'])
        return alternatives
    
    def get_rebalancing_strategies(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, large_cap_target, mid_cap_target, small_cap_target FROM rebalancing_strategies WHERE is_active = TRUE")
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return {row['name']: {
            'Large Cap': float(row['large_cap_target']),
            'Mid Cap': float(row['mid_cap_target']),
            'Small Cap': float(row['small_cap_target'])
        } for row in results}
    
    def save_portfolio_history(self, user_id, file_name, stock_count, total_investment, current_value, total_gain_loss, stocks_data):
        try:
            import json
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO portfolio_history (user_id, file_name, stock_count, total_investment, current_value, total_gain_loss, stocks_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, file_name, stock_count, total_investment, current_value, total_gain_loss, json.dumps(stocks_data)))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving portfolio history: {e}")
            return False
    
    def log_activity(self, user_id, activity_type, details=None):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO user_activity (user_id, activity_type, details)
                VALUES (%s, %s, %s)
            ''', (user_id, activity_type, details))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_all_users(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT id, email, full_name, phone, is_admin, created_at, last_login 
            FROM users ORDER BY created_at DESC
        ''')
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    
    def get_all_portfolio_history(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT ph.*, u.email, u.full_name 
            FROM portfolio_history ph
            JOIN users u ON ph.user_id = u.id
            ORDER BY ph.created_at DESC
            LIMIT 100
        ''')
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    
    def get_user_activity(self, limit=100):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT ua.*, u.email, u.full_name 
            FROM user_activity ua
            JOIN users u ON ua.user_id = u.id
            ORDER BY ua.created_at DESC
            LIMIT %s
        ''', (limit,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    
    def get_admin_stats(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT COUNT(*) as count FROM users")
        total_users = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM portfolio_history")
        total_analyses = cur.fetchone()['count']
        cur.execute("SELECT COUNT(DISTINCT user_id) as count FROM portfolio_history")
        active_users = cur.fetchone()['count']
        cur.close()
        conn.close()
        return {
            'total_users': total_users,
            'total_analyses': total_analyses,
            'active_users': active_users
        }
    
    def make_admin(self, email):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET is_admin = TRUE WHERE email = %s", (email.lower(),))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except:
            return False
