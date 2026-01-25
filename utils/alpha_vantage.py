import os
import requests
import time

class AlphaVantageClient:
    def __init__(self):
        self.api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
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
            return f"{base}.BSE"
        return f"{symbol}.BSE"
    
    def get_company_overview(self, symbol):
        if not self.is_available():
            return None
        
        av_symbol = self._convert_symbol(symbol)
        cache_key = f"overview_{av_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': av_symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Note' in data or 'Information' in data:
                print(f"Alpha Vantage rate limit or error: {data.get('Note', data.get('Information', ''))}")
                return None
            
            if not data or 'Symbol' not in data:
                return None
            
            fundamentals = self._parse_overview(data)
            self._set_cache(cache_key, fundamentals)
            return fundamentals
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    def _parse_overview(self, data):
        def safe_float(value, divisor=1):
            try:
                if value and value != 'None' and value != '-':
                    return float(value) / divisor
            except (ValueError, TypeError):
                pass
            return None
        
        return {
            'pe_ratio': safe_float(data.get('PERatio')),
            'peg_ratio': safe_float(data.get('PEGRatio')),
            'pb_ratio': safe_float(data.get('PriceToBookRatio')),
            'market_cap': safe_float(data.get('MarketCapitalization')),
            'dividend_yield': safe_float(data.get('DividendYield')),
            'dividend_per_share': safe_float(data.get('DividendPerShare')),
            'eps': safe_float(data.get('EPS')),
            'roe': safe_float(data.get('ReturnOnEquityTTM')),
            'roa': safe_float(data.get('ReturnOnAssetsTTM')),
            'revenue_ttm': safe_float(data.get('RevenueTTM')),
            'gross_profit_ttm': safe_float(data.get('GrossProfitTTM')),
            'ebitda': safe_float(data.get('EBITDA')),
            'profit_margin': safe_float(data.get('ProfitMargin')),
            'operating_margin': safe_float(data.get('OperatingMarginTTM')),
            'revenue_per_share': safe_float(data.get('RevenuePerShareTTM')),
            'quarterly_earnings_growth': safe_float(data.get('QuarterlyEarningsGrowthYOY')),
            'quarterly_revenue_growth': safe_float(data.get('QuarterlyRevenueGrowthYOY')),
            'analyst_target_price': safe_float(data.get('AnalystTargetPrice')),
            'book_value': safe_float(data.get('BookValue')),
            'fifty_two_week_high': safe_float(data.get('52WeekHigh')),
            'fifty_two_week_low': safe_float(data.get('52WeekLow')),
            'fifty_day_ma': safe_float(data.get('50DayMovingAverage')),
            'two_hundred_day_ma': safe_float(data.get('200DayMovingAverage')),
            'shares_outstanding': safe_float(data.get('SharesOutstanding')),
            'beta': safe_float(data.get('Beta')),
            'sector': data.get('Sector'),
            'industry': data.get('Industry'),
            'description': data.get('Description'),
            'name': data.get('Name'),
            'exchange': data.get('Exchange'),
            'currency': data.get('Currency'),
            'source': 'alpha_vantage'
        }
    
    def get_earnings(self, symbol):
        if not self.is_available():
            return None
        
        av_symbol = self._convert_symbol(symbol)
        cache_key = f"earnings_{av_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'function': 'EARNINGS',
                'symbol': av_symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Note' in data or 'Information' in data:
                return None
            
            if 'annualEarnings' not in data:
                return None
            
            earnings_data = {
                'annual_earnings': data.get('annualEarnings', [])[:5],
                'quarterly_earnings': data.get('quarterlyEarnings', [])[:8]
            }
            
            if len(earnings_data['annual_earnings']) >= 2:
                current_eps = float(earnings_data['annual_earnings'][0].get('reportedEPS', 0) or 0)
                prev_eps = float(earnings_data['annual_earnings'][1].get('reportedEPS', 0) or 0)
                if prev_eps != 0:
                    earnings_data['earnings_growth'] = (current_eps - prev_eps) / abs(prev_eps)
            
            self._set_cache(cache_key, earnings_data)
            return earnings_data
            
        except Exception as e:
            print(f"Alpha Vantage earnings error for {symbol}: {e}")
            return None
    
    def get_balance_sheet(self, symbol):
        if not self.is_available():
            return None
        
        av_symbol = self._convert_symbol(symbol)
        cache_key = f"balance_{av_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'function': 'BALANCE_SHEET',
                'symbol': av_symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Note' in data or 'Information' in data:
                return None
            
            if 'annualReports' not in data:
                return None
            
            latest = data['annualReports'][0] if data['annualReports'] else {}
            
            def safe_float(value):
                try:
                    if value and value != 'None':
                        return float(value)
                except:
                    pass
                return None
            
            total_debt = safe_float(latest.get('totalLiabilities')) or 0
            total_equity = safe_float(latest.get('totalShareholderEquity')) or 0
            
            balance_data = {
                'total_assets': safe_float(latest.get('totalAssets')),
                'total_liabilities': safe_float(latest.get('totalLiabilities')),
                'total_equity': total_equity,
                'current_assets': safe_float(latest.get('totalCurrentAssets')),
                'current_liabilities': safe_float(latest.get('totalCurrentLiabilities')),
                'long_term_debt': safe_float(latest.get('longTermDebt')),
                'short_term_debt': safe_float(latest.get('shortTermDebt')),
                'cash_and_equivalents': safe_float(latest.get('cashAndCashEquivalentsAtCarryingValue')),
                'debt_to_equity': total_debt / total_equity if total_equity > 0 else None
            }
            
            self._set_cache(cache_key, balance_data)
            return balance_data
            
        except Exception as e:
            print(f"Alpha Vantage balance sheet error for {symbol}: {e}")
            return None
    
    def get_income_statement(self, symbol):
        if not self.is_available():
            return None
        
        av_symbol = self._convert_symbol(symbol)
        cache_key = f"income_{av_symbol}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'function': 'INCOME_STATEMENT',
                'symbol': av_symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Note' in data or 'Information' in data:
                return None
            
            if 'annualReports' not in data:
                return None
            
            reports = data['annualReports'][:3]
            
            def safe_float(value):
                try:
                    if value and value != 'None':
                        return float(value)
                except:
                    pass
                return None
            
            latest = reports[0] if reports else {}
            
            income_data = {
                'total_revenue': safe_float(latest.get('totalRevenue')),
                'gross_profit': safe_float(latest.get('grossProfit')),
                'operating_income': safe_float(latest.get('operatingIncome')),
                'net_income': safe_float(latest.get('netIncome')),
                'ebitda': safe_float(latest.get('ebitda')),
            }
            
            if len(reports) >= 2:
                current_rev = safe_float(reports[0].get('totalRevenue')) or 0
                prev_rev = safe_float(reports[1].get('totalRevenue')) or 0
                if prev_rev > 0:
                    income_data['revenue_growth'] = (current_rev - prev_rev) / prev_rev
            
            self._set_cache(cache_key, income_data)
            return income_data
            
        except Exception as e:
            print(f"Alpha Vantage income statement error for {symbol}: {e}")
            return None
    
    def get_full_fundamentals(self, symbol):
        fundamentals = {}
        
        overview = self.get_company_overview(symbol)
        if overview:
            fundamentals.update(overview)
        
        return fundamentals if fundamentals else None
