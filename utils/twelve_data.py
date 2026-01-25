import os
import requests
import time

class TwelveDataClient:
    def __init__(self):
        self.api_key = os.environ.get('TWELVE_DATA_API_KEY')
        self.base_url = "https://api.twelvedata.com"
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 3600
    
    def is_available(self):
        return self.api_key is not None and len(self.api_key) > 0
    
    def _get_cached(self, key):
        if key in self._cache:
            if time.time() - self._cache_time.get(key, 0) < self._cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key, value):
        self._cache[key] = value
        self._cache_time[key] = time.time()
    
    def _convert_symbol(self, symbol):
        symbol = symbol.upper().strip()
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            base = symbol.replace('.NS', '').replace('.BO', '')
            return base
        return symbol
    
    def get_quote(self, symbol):
        if not self.is_available():
            return None
        
        td_symbol = self._convert_symbol(symbol)
        cache_key = f"quote_{td_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': td_symbol,
                'exchange': 'NSE',
                'apikey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'code' in data and data['code'] == 400:
                params['exchange'] = 'BSE'
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
            
            if 'code' in data:
                return None
            
            quote_data = {
                'symbol': data.get('symbol'),
                'name': data.get('name'),
                'exchange': data.get('exchange'),
                'currency': data.get('currency'),
                'open': self._safe_float(data.get('open')),
                'high': self._safe_float(data.get('high')),
                'low': self._safe_float(data.get('low')),
                'close': self._safe_float(data.get('close')),
                'previous_close': self._safe_float(data.get('previous_close')),
                'change': self._safe_float(data.get('change')),
                'percent_change': self._safe_float(data.get('percent_change')),
                'volume': self._safe_float(data.get('volume')),
                'fifty_two_week_high': self._safe_float(data.get('fifty_two_week', {}).get('high')),
                'fifty_two_week_low': self._safe_float(data.get('fifty_two_week', {}).get('low')),
            }
            
            self._set_cache(cache_key, quote_data)
            return quote_data
            
        except Exception as e:
            print(f"Twelve Data quote error for {symbol}: {e}")
            return None
    
    def _safe_float(self, value):
        try:
            if value is not None and value != '' and value != 'null':
                return float(value)
        except (ValueError, TypeError):
            pass
        return None
    
    def get_statistics(self, symbol):
        if not self.is_available():
            return None
        
        td_symbol = self._convert_symbol(symbol)
        cache_key = f"stats_{td_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/statistics"
            params = {
                'symbol': td_symbol,
                'exchange': 'NSE',
                'apikey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'code' in data and data['code'] == 400:
                params['exchange'] = 'BSE'
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
            
            if 'code' in data or 'statistics' not in data:
                return None
            
            stats = data.get('statistics', {})
            valuations = stats.get('valuations_metrics', {})
            financials = stats.get('financials', {})
            stock_stats = stats.get('stock_statistics', {})
            
            statistics_data = {
                'market_cap': self._safe_float(valuations.get('market_capitalization')),
                'pe_ratio': self._safe_float(valuations.get('trailing_pe')),
                'forward_pe': self._safe_float(valuations.get('forward_pe')),
                'peg_ratio': self._safe_float(valuations.get('peg_ratio')),
                'pb_ratio': self._safe_float(valuations.get('price_to_book_mrq')),
                'ps_ratio': self._safe_float(valuations.get('price_to_sales_ttm')),
                'enterprise_value': self._safe_float(valuations.get('enterprise_value')),
                
                'profit_margin': self._safe_float(financials.get('profit_margin')),
                'operating_margin': self._safe_float(financials.get('operating_margin')),
                'roe': self._safe_float(financials.get('return_on_equity_ttm')),
                'roa': self._safe_float(financials.get('return_on_assets_ttm')),
                'revenue': self._safe_float(financials.get('revenue_ttm')),
                'revenue_per_share': self._safe_float(financials.get('revenue_per_share_ttm')),
                'quarterly_revenue_growth': self._safe_float(financials.get('quarterly_revenue_growth')),
                'gross_profit': self._safe_float(financials.get('gross_profit_ttm')),
                'ebitda': self._safe_float(financials.get('ebitda')),
                'net_income': self._safe_float(financials.get('net_income_to_common_ttm')),
                'eps': self._safe_float(financials.get('diluted_eps_ttm')),
                'quarterly_earnings_growth': self._safe_float(financials.get('quarterly_earnings_growth_yoy')),
                
                'total_cash': self._safe_float(financials.get('total_cash_mrq')),
                'total_debt': self._safe_float(financials.get('total_debt_mrq')),
                'debt_to_equity': self._safe_float(financials.get('total_debt_to_equity_mrq')),
                'current_ratio': self._safe_float(financials.get('current_ratio_mrq')),
                'book_value_per_share': self._safe_float(financials.get('book_value_per_share_mrq')),
                
                'beta': self._safe_float(stock_stats.get('beta')),
                'shares_outstanding': self._safe_float(stock_stats.get('shares_outstanding')),
                'float_shares': self._safe_float(stock_stats.get('float_shares')),
                'avg_volume': self._safe_float(stock_stats.get('average_volume')),
                'dividend_per_share': self._safe_float(stock_stats.get('dividend_per_share_annual')),
                'dividend_yield': self._safe_float(stock_stats.get('dividend_yield')),
                
                'source': 'twelve_data'
            }
            
            self._set_cache(cache_key, statistics_data)
            return statistics_data
            
        except Exception as e:
            print(f"Twelve Data statistics error for {symbol}: {e}")
            return None
    
    def get_fundamentals(self, symbol):
        fundamentals = {}
        
        stats = self.get_statistics(symbol)
        if stats:
            fundamentals.update(stats)
        
        quote = self.get_quote(symbol)
        if quote:
            fundamentals['current_price'] = quote.get('close')
            fundamentals['fifty_two_week_high'] = quote.get('fifty_two_week_high')
            fundamentals['fifty_two_week_low'] = quote.get('fifty_two_week_low')
            fundamentals['name'] = quote.get('name')
            fundamentals['exchange'] = quote.get('exchange')
        
        if fundamentals.get('quarterly_revenue_growth') is not None:
            fundamentals['revenue_growth'] = fundamentals['quarterly_revenue_growth']
        
        if fundamentals.get('quarterly_earnings_growth') is not None:
            fundamentals['earnings_growth'] = fundamentals['quarterly_earnings_growth']
        
        return fundamentals if fundamentals else None
    
    def get_price(self, symbol):
        if not self.is_available():
            return None
        
        td_symbol = self._convert_symbol(symbol)
        
        try:
            url = f"{self.base_url}/price"
            params = {
                'symbol': td_symbol,
                'exchange': 'NSE',
                'apikey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'code' in data and data['code'] == 400:
                params['exchange'] = 'BSE'
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
            
            if 'price' in data:
                return self._safe_float(data['price'])
            
            return None
            
        except Exception as e:
            print(f"Twelve Data price error for {symbol}: {e}")
            return None
