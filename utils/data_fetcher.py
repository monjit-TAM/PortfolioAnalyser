import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import os

class DataFetcher:
    def __init__(self, use_database=True):
        self.nse_suffix = ".NS"
        self.bse_suffix = ".BO"
        self.use_database = use_database and os.environ.get('DATABASE_URL') is not None
        
        self._symbol_aliases = None
        self._indices = None
        self._stock_categories = None
        self._sector_mapping = None
        self._stock_info = None
        
        self._truedata_client = None
        self._truedata_initialized = False
        
        self._alpha_vantage_client = None
        self._alpha_vantage_initialized = False
        
        self._twelve_data_client = None
        self._twelve_data_initialized = False
    
    @property
    def symbol_aliases(self):
        if self._symbol_aliases is None:
            self._load_data()
        return self._symbol_aliases
    
    @property
    def indices(self):
        if self._indices is None:
            self._load_data()
        return self._indices
    
    @property
    def stock_categories(self):
        if self._stock_categories is None:
            self._load_data()
        return self._stock_categories
    
    @property
    def sector_mapping(self):
        if self._sector_mapping is None:
            self._load_data()
        return self._sector_mapping
    
    def _load_data(self):
        if self.use_database:
            try:
                from utils.database import Database
                db = Database()
                
                self._symbol_aliases = db.get_symbol_aliases()
                self._indices = db.get_market_indices()
                stock_info = db.get_stock_symbols()
                
                self._stock_categories = {}
                self._sector_mapping = {}
                for symbol, info in stock_info.items():
                    self._stock_categories[symbol] = info.get('category', 'Mid Cap')
                    self._sector_mapping[symbol] = info.get('sector', 'Others')
                
                self._stock_info = stock_info
                return
            except Exception as e:
                print(f"Database load failed, using defaults: {e}")
        
        self._symbol_aliases = {
            'RIL': 'RELIANCE',
            'ICICI': 'ICICIBANK',
            'HDFC': 'HDFCBANK',
            'KOTAK': 'KOTAKBANK',
            'SBI': 'SBIN',
            'BHARTI': 'BHARTIARTL',
            'HINDUNILEVER': 'HINDUNILVR',
            'HUL': 'HINDUNILVR',
            'M&M': 'M&M',
            'BAJAJFINSV': 'BAJAJFINSV',
            'ADANI': 'ADANIENT',
            'ADANIPORTS': 'ADANIPORTS',
            'ONGC': 'ONGC',
            'NTPC': 'NTPC',
            'POWERGRID': 'POWERGRID',
            'TATAMOTORS': 'TATAMOTORS',
            'TATAPOWER': 'TATAPOWER',
            'TATASTEEL': 'TATASTEEL',
        }
        
        self._indices = {
            'NIFTY50': '^NSEI',
            'NIFTY_MIDCAP_100': '^NSEMDCP50',
            'NIFTY_SMALLCAP_100': '^NSESMLCAP'
        }
        
        self._stock_categories = {
            'RELIANCE': 'Large Cap',
            'TCS': 'Large Cap',
            'HDFCBANK': 'Large Cap',
            'INFY': 'Large Cap',
            'ICICIBANK': 'Large Cap',
            'KOTAKBANK': 'Large Cap',
            'HINDUNILVR': 'Large Cap',
            'SBIN': 'Large Cap',
            'BHARTIARTL': 'Large Cap',
            'ITC': 'Large Cap',
            'ASIANPAINT': 'Large Cap',
            'MARUTI': 'Large Cap',
            'AXISBANK': 'Large Cap',
            'LT': 'Large Cap',
            'SUNPHARMA': 'Large Cap',
            'TITAN': 'Large Cap',
            'ULTRACEMCO': 'Large Cap',
            'NESTLEIND': 'Large Cap',
            'WIPRO': 'Large Cap',
            'HCLTECH': 'Large Cap',
        }
        
        self._sector_mapping = {
            'RELIANCE': 'Energy',
            'TCS': 'Technology',
            'HDFCBANK': 'Banking',
            'INFY': 'Technology',
            'ICICIBANK': 'Banking',
            'KOTAKBANK': 'Banking',
            'HINDUNILVR': 'FMCG',
            'SBIN': 'Banking',
            'BHARTIARTL': 'Telecom',
            'ITC': 'FMCG',
            'ASIANPAINT': 'Paints',
            'MARUTI': 'Automobile',
            'AXISBANK': 'Banking',
            'LT': 'Construction',
            'SUNPHARMA': 'Pharmaceuticals',
            'TITAN': 'Jewellery',
            'ULTRACEMCO': 'Cement',
            'NESTLEIND': 'FMCG',
            'WIPRO': 'Technology',
            'HCLTECH': 'Technology',
        }
    
    def init_truedata(self, symbols=None):
        if self._truedata_initialized:
            return True
        
        try:
            from utils.truedata_client import TrueDataPriceFetcher
            self._truedata_client = TrueDataPriceFetcher()
            
            if self._truedata_client.is_available():
                if symbols:
                    self._truedata_client.initialize(symbols)
                self._truedata_initialized = True
                return True
        except Exception as e:
            print(f"TrueData initialization failed: {e}")
        
        return False
    
    def get_live_price(self, symbol):
        if self._truedata_client and self._truedata_initialized:
            price = self._truedata_client.get_price(symbol)
            if price:
                return price
        return None
    
    def get_stock_symbol(self, stock_name):
        stock_name = stock_name.upper().strip()
        
        if stock_name.endswith(self.nse_suffix) or stock_name.endswith(self.bse_suffix):
            return stock_name
        
        if stock_name in self.symbol_aliases:
            original_name = stock_name
            stock_name = self.symbol_aliases[stock_name]
            print(f"Symbol alias: {original_name} → {stock_name}")
        
        nse_symbol = f"{stock_name}{self.nse_suffix}"
        try:
            ticker = yf.Ticker(nse_symbol)
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                return nse_symbol
        except:
            pass
        
        bse_symbol = f"{stock_name}{self.bse_suffix}"
        try:
            ticker = yf.Ticker(bse_symbol)
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                return bse_symbol
        except:
            pass
        
        return nse_symbol
    
    def get_stock_data(self, stock_name, start_date):
        symbol = self.get_stock_symbol(stock_name)
        
        live_price = self.get_live_price(symbol)
        
        try:
            end_date = datetime.now()
            
            historical_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            if historical_data.empty:
                historical_data = yf.download(symbol, period="1mo", progress=False)
                if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                    historical_data.index = historical_data.index.tz_localize(None)
            
            if historical_data.empty:
                raise ValueError(f"No data available for {stock_name}")
            
            if live_price:
                current_price = float(live_price)
            else:
                current_price = float(historical_data['Close'].iloc[-1])
            
            return current_price, historical_data
            
        except Exception as e:
            st.error(f"Could not fetch data for {stock_name} ({symbol}): {str(e)}")
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = live_price or info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
                
                if current_price:
                    st.warning(f"Using fallback price for {stock_name}: ₹{current_price}")
                    
                    try:
                        end_date = datetime.now()
                        historical_data = ticker.history(start=start_date, end=end_date)
                        
                        if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                            historical_data.index = historical_data.index.tz_localize(None)
                        
                        if not historical_data.empty:
                            return float(current_price), historical_data
                        else:
                            historical_data = ticker.history(period="1y")
                            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                                historical_data.index = historical_data.index.tz_localize(None)
                            return float(current_price), historical_data
                    except:
                        return float(current_price), pd.DataFrame()
            except:
                pass
            
            st.error(f"Unable to fetch any price data for {stock_name}. Please check the stock symbol.")
            return None, pd.DataFrame()
    
    def get_index_data(self, index_name, start_date):
        if index_name not in self.indices:
            return pd.DataFrame()
        
        symbol = self.indices[index_name]
        
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            historical_data = ticker.history(start=start_date, end=end_date)
            
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            return historical_data
        except Exception as e:
            st.warning(f"Could not fetch index data for {index_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_category(self, stock_name):
        stock_name = stock_name.upper().strip()
        base_name = stock_name.replace(self.nse_suffix, '').replace(self.bse_suffix, '')
        if base_name in self.symbol_aliases:
            base_name = self.symbol_aliases[base_name]
        return self.stock_categories.get(base_name, 'Mid Cap')
    
    def get_stock_sector(self, stock_name):
        stock_name = stock_name.upper().strip()
        base_name = stock_name.replace(self.nse_suffix, '').replace(self.bse_suffix, '')
        if base_name in self.symbol_aliases:
            base_name = self.symbol_aliases[base_name]
        return self.sector_mapping.get(base_name, 'Others')
    
    def _init_twelve_data(self):
        if self._twelve_data_initialized:
            return self._twelve_data_client
        
        try:
            from utils.twelve_data import TwelveDataClient
            self._twelve_data_client = TwelveDataClient()
            self._twelve_data_initialized = True
            return self._twelve_data_client
        except Exception as e:
            print(f"Twelve Data initialization failed: {e}")
            return None
    
    def _init_alpha_vantage(self):
        if self._alpha_vantage_initialized:
            return self._alpha_vantage_client
        
        try:
            from utils.alpha_vantage import AlphaVantageClient
            self._alpha_vantage_client = AlphaVantageClient()
            self._alpha_vantage_initialized = True
            return self._alpha_vantage_client
        except Exception as e:
            print(f"Alpha Vantage initialization failed: {e}")
            return None
    
    def get_stock_fundamentals(self, stock_name):
        symbol = self.get_stock_symbol(stock_name)
        base_name = stock_name.upper().strip().replace(self.nse_suffix, '').replace(self.bse_suffix, '')
        
        td_client = self._init_twelve_data()
        if td_client and td_client.is_available():
            try:
                td_fundamentals = td_client.get_fundamentals(base_name)
                if td_fundamentals and (td_fundamentals.get('pe_ratio') is not None or td_fundamentals.get('market_cap') is not None):
                    print(f"Using Twelve Data fundamentals for {stock_name}")
                    return td_fundamentals
            except Exception as e:
                print(f"Twelve Data fetch failed for {stock_name}: {e}")
        
        av_client = self._init_alpha_vantage()
        if av_client and av_client.is_available():
            try:
                av_fundamentals = av_client.get_full_fundamentals(base_name)
                if av_fundamentals and av_fundamentals.get('pe_ratio') is not None:
                    print(f"Using Alpha Vantage fundamentals for {stock_name}")
                    return av_fundamentals
            except Exception as e:
                print(f"Alpha Vantage fetch failed for {stock_name}: {e}")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fundamentals = {
                'pe_ratio': info.get('forwardPE') or info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'market_cap': info.get('marketCap'),
                'dividend_yield': info.get('dividendYield'),
                'roe': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'source': 'yahoo_finance'
            }
            
            return fundamentals
            
        except Exception as e:
            st.warning(f"Could not fetch fundamentals for {stock_name}: {str(e)}")
            return {}
    
    def add_stock_to_database(self, symbol, name=None, sector=None, category=None):
        if not self.use_database:
            return False
        
        try:
            from utils.database import Database
            db = Database()
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO stock_symbols (symbol, name, sector, category) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (symbol) DO UPDATE SET 
                    name = COALESCE(EXCLUDED.name, stock_symbols.name),
                    sector = COALESCE(EXCLUDED.sector, stock_symbols.sector),
                    category = COALESCE(EXCLUDED.category, stock_symbols.category),
                    updated_at = CURRENT_TIMESTAMP
            ''', (symbol.upper(), name, sector, category))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self._symbol_aliases = None
            self._stock_categories = None
            self._sector_mapping = None
            self._stock_info = None
            
            return True
        except Exception as e:
            print(f"Failed to add stock to database: {e}")
            return False
