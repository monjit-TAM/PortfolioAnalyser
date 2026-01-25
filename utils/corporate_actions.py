import os
import psycopg2
from datetime import datetime, date
from decimal import Decimal

class CorporateActionsManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self._actions_cache = None
        self._cache_loaded = False
    
    def _get_connection(self):
        if not self.database_url:
            return None
        return psycopg2.connect(self.database_url)
    
    def _load_all_actions(self):
        if self._cache_loaded:
            return self._actions_cache
        
        self._actions_cache = {}
        
        try:
            conn = self._get_connection()
            if not conn:
                return self._actions_cache
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, action_type, action_date, ratio_from, ratio_to, dividend_amount, ex_date
                FROM corporate_actions
                ORDER BY action_date ASC
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                symbol = row[0].upper()
                if symbol not in self._actions_cache:
                    self._actions_cache[symbol] = []
                
                self._actions_cache[symbol].append({
                    'symbol': symbol,
                    'action_type': row[1],
                    'action_date': row[2],
                    'ratio_from': row[3],
                    'ratio_to': row[4],
                    'dividend_amount': float(row[5]) if row[5] else 0,
                    'ex_date': row[6]
                })
            
            cursor.close()
            conn.close()
            self._cache_loaded = True
            
        except Exception as e:
            print(f"Error loading corporate actions: {e}")
        
        return self._actions_cache
    
    def _normalize_symbol(self, symbol):
        symbol = symbol.upper().strip()
        symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        aliases = {
            'RELIANCE': 'RELIANCE',
            'RIL': 'RELIANCE',
            'RELIANCEINDUSTRIES': 'RELIANCE',
            'HDFC': 'HDFCBANK',
            'HDFCBANK': 'HDFCBANK',
            'GODFREY': 'GODFRYPHLP',
            'GODFRYPHLP': 'GODFRYPHLP',
            'GODFREYPHILLIPS': 'GODFRYPHLP',
            'GODFREYPHILIP': 'GODFRYPHLP',
            'GODFREY PHILLIPS': 'GODFRYPHLP',
            'TCS': 'TCS',
            'TATA CONSULTANCY': 'TCS',
            'INFY': 'INFY',
            'INFOSYS': 'INFY',
            'WIPRO': 'WIPRO',
        }
        
        return aliases.get(symbol, symbol)
    
    def get_actions_for_symbol(self, symbol, after_date=None):
        actions = self._load_all_actions()
        normalized = self._normalize_symbol(symbol)
        
        symbol_actions = actions.get(normalized, [])
        
        if after_date:
            if isinstance(after_date, str):
                after_date = datetime.strptime(after_date, '%Y-%m-%d').date()
            elif isinstance(after_date, datetime):
                after_date = after_date.date()
            
            symbol_actions = [a for a in symbol_actions if a['action_date'] >= after_date]
        
        return symbol_actions
    
    def calculate_adjustment_factor(self, symbol, buy_date):
        actions = self.get_actions_for_symbol(symbol, after_date=buy_date)
        
        adjustment_factor = 1.0
        
        for action in actions:
            if action['action_type'] == 'BONUS':
                bonus_ratio = action['ratio_from'] / action['ratio_to']
                adjustment_factor *= (1 + bonus_ratio)
            
            elif action['action_type'] == 'SPLIT':
                split_ratio = action['ratio_to'] / action['ratio_from']
                adjustment_factor *= split_ratio
        
        return adjustment_factor
    
    def get_adjusted_buy_price(self, symbol, original_buy_price, buy_date):
        adjustment_factor = self.calculate_adjustment_factor(symbol, buy_date)
        
        if adjustment_factor > 1:
            adjusted_price = original_buy_price / adjustment_factor
            return adjusted_price
        
        return original_buy_price
    
    def get_adjusted_quantity(self, symbol, original_quantity, buy_date):
        adjustment_factor = self.calculate_adjustment_factor(symbol, buy_date)
        
        if adjustment_factor > 1:
            adjusted_quantity = original_quantity * adjustment_factor
            return int(adjusted_quantity)
        
        return original_quantity
    
    def get_adjustment_details(self, symbol, buy_date):
        actions = self.get_actions_for_symbol(symbol, after_date=buy_date)
        
        details = {
            'symbol': symbol,
            'buy_date': buy_date,
            'actions_applied': [],
            'total_adjustment_factor': 1.0
        }
        
        for action in actions:
            action_detail = {
                'type': action['action_type'],
                'date': action['action_date'],
                'description': ''
            }
            
            if action['action_type'] == 'BONUS':
                ratio = f"{action['ratio_from']}:{action['ratio_to']}"
                factor = 1 + (action['ratio_from'] / action['ratio_to'])
                action_detail['description'] = f"Bonus {ratio} - Quantity multiplied by {factor:.0f}"
                action_detail['factor'] = factor
                details['total_adjustment_factor'] *= factor
            
            elif action['action_type'] == 'SPLIT':
                ratio = f"{action['ratio_from']}:{action['ratio_to']}"
                factor = action['ratio_to'] / action['ratio_from']
                action_detail['description'] = f"Split {ratio} - Quantity multiplied by {factor:.0f}"
                action_detail['factor'] = factor
                details['total_adjustment_factor'] *= factor
            
            details['actions_applied'].append(action_detail)
        
        return details
    
    def apply_adjustments_to_portfolio(self, portfolio_df):
        import pandas as pd
        
        if portfolio_df is None or portfolio_df.empty:
            return portfolio_df
        
        adjusted_df = portfolio_df.copy()
        
        if 'adjusted_buy_price' not in adjusted_df.columns:
            adjusted_df['adjusted_buy_price'] = adjusted_df['buy_price']
        if 'adjusted_quantity' not in adjusted_df.columns:
            adjusted_df['adjusted_quantity'] = adjusted_df['quantity']
        if 'adjustment_factor' not in adjusted_df.columns:
            adjusted_df['adjustment_factor'] = 1.0
        if 'corporate_actions' not in adjusted_df.columns:
            adjusted_df['corporate_actions'] = ''
        
        for idx, row in adjusted_df.iterrows():
            symbol = row.get('stock_name', row.get('symbol', ''))
            buy_date = row.get('buy_date')
            original_price = row.get('buy_price', 0)
            original_qty = row.get('quantity', 0)
            
            if pd.isna(buy_date):
                continue
            
            if isinstance(buy_date, str):
                try:
                    buy_date = datetime.strptime(buy_date, '%Y-%m-%d').date()
                except:
                    continue
            elif isinstance(buy_date, datetime):
                buy_date = buy_date.date()
            
            details = self.get_adjustment_details(symbol, buy_date)
            
            if details['actions_applied']:
                factor = details['total_adjustment_factor']
                adjusted_df.at[idx, 'adjusted_buy_price'] = original_price / factor
                adjusted_df.at[idx, 'adjusted_quantity'] = int(original_qty * factor)
                adjusted_df.at[idx, 'adjustment_factor'] = factor
                
                action_descriptions = [a['description'] for a in details['actions_applied']]
                adjusted_df.at[idx, 'corporate_actions'] = '; '.join(action_descriptions)
        
        return adjusted_df
