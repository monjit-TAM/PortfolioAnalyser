import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import os

def _flatten_yf_columns(df):
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df


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
        
        self._zerodha_kite = None
        self._zerodha_initialized = False
        self._zerodha_instruments = None
    
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
            'RIL': 'RELIANCE', 'ICICI': 'ICICIBANK', 'HDFC': 'HDFCBANK',
            'KOTAK': 'KOTAKBANK', 'SBI': 'SBIN', 'BHARTI': 'BHARTIARTL',
            'HINDUNILEVER': 'HINDUNILVR', 'HUL': 'HINDUNILVR',
            'M&M': 'M&M', 'BAJAJFINSV': 'BAJAJFINSV',
            'ADANI': 'ADANIENT', 'ADANIPORTS': 'ADANIPORTS',
            'ONGC': 'ONGC', 'NTPC': 'NTPC', 'POWERGRID': 'POWERGRID',
            'TATAMOTORS': 'TATAMOTORS', 'TATAPOWER': 'TATAPOWER',
            'TATASTEEL': 'TATASTEEL', 'HERO': 'HEROMOTOCO',
            'EICHER': 'EICHERMOT', 'INDIGO': 'INTERGLOBE',
            'INDUSIND': 'INDUSINDBK', 'BOB': 'BANKBARODA',
            'MCDOWELL': 'UBL', 'DMART': 'DMART', 'TATACONS': 'TATACONSUM',
            'NYKAA': 'NYKAA', 'PAYTM': 'PAYTM', 'ZOMATO': 'ZOMATO',
            'POLICYBAZAAR': 'POLICYBZR', 'LIC': 'LICI',
            'MOTHERSUMI': 'MOTHERSON', 'MAPMYINDIA': 'MAPMYINDIA',
            'JSWSTL': 'JSWSTEEL', 'LODHA': 'LODHA',
            'LTIMINDTREE': 'LTIM', 'MINDTREE': 'LTIM',
        }
        
        self._indices = {
            'NIFTY50': '^NSEI',
            'NIFTY_MIDCAP_100': '^NSEMDCP50',
            'NIFTY_SMALLCAP_100': '^NSESMLCAP'
        }
        
        self._stock_categories = {
            'RELIANCE': 'Large Cap', 'TCS': 'Large Cap', 'HDFCBANK': 'Large Cap',
            'INFY': 'Large Cap', 'ICICIBANK': 'Large Cap', 'KOTAKBANK': 'Large Cap',
            'HINDUNILVR': 'Large Cap', 'SBIN': 'Large Cap', 'BHARTIARTL': 'Large Cap',
            'ITC': 'Large Cap', 'ASIANPAINT': 'Large Cap', 'MARUTI': 'Large Cap',
            'AXISBANK': 'Large Cap', 'LT': 'Large Cap', 'SUNPHARMA': 'Large Cap',
            'TITAN': 'Large Cap', 'ULTRACEMCO': 'Large Cap', 'NESTLEIND': 'Large Cap',
            'WIPRO': 'Large Cap', 'HCLTECH': 'Large Cap', 'BAJFINANCE': 'Large Cap',
            'BAJAJFINSV': 'Large Cap', 'ADANIENT': 'Large Cap', 'ADANIPORTS': 'Large Cap',
            'TATAMOTORS': 'Large Cap', 'M&M': 'Large Cap', 'BAJAJ-AUTO': 'Large Cap',
            'HEROMOTOCO': 'Large Cap', 'EICHERMOT': 'Large Cap', 'TVSMOTOR': 'Large Cap',
            'INDUSINDBK': 'Large Cap', 'BANKBARODA': 'Large Cap', 'PNB': 'Large Cap',
            'JSWSTEEL': 'Large Cap', 'HINDALCO': 'Large Cap', 'VEDL': 'Large Cap',
            'COALINDIA': 'Large Cap', 'DLF': 'Large Cap', 'GODREJPROP': 'Large Cap',
            'HAL': 'Large Cap', 'BEL': 'Large Cap', 'INTERGLOBE': 'Large Cap',
            'APOLLOHOSP': 'Large Cap', 'MAXHEALTH': 'Large Cap', 'DMART': 'Large Cap',
            'TRENT': 'Large Cap', 'LICI': 'Large Cap', 'SBILIFE': 'Large Cap',
            'HDFCLIFE': 'Large Cap', 'ICICIGI': 'Large Cap', 'CHOLAFIN': 'Large Cap',
            'SHRIRAMFIN': 'Large Cap', 'POLYCAB': 'Large Cap', 'SIEMENS': 'Large Cap',
            'ABB': 'Large Cap', 'HAVELLS': 'Large Cap', 'PIDILITIND': 'Large Cap',
            'SRF': 'Large Cap', 'GRASIM': 'Large Cap', 'INDUSTOWER': 'Large Cap',
            'VBL': 'Large Cap', 'TATACONSUM': 'Large Cap', 'DABUR': 'Large Cap',
            'MARICO': 'Large Cap', 'GODREJCP': 'Large Cap', 'COLPAL': 'Large Cap',
            'DIVISLAB': 'Large Cap', 'DRREDDY': 'Large Cap', 'CIPLA': 'Large Cap',
            'GAIL': 'Large Cap', 'IOC': 'Large Cap', 'BPCL': 'Large Cap',
            'HINDPETRO': 'Large Cap', 'NTPC': 'Large Cap', 'POWERGRID': 'Large Cap',
            'TATAPOWER': 'Mid Cap', 'SHREECEM': 'Large Cap', 'AMBUJACEM': 'Large Cap',
            'ACC': 'Large Cap', 'BERGEPAINT': 'Large Cap', 'PAGEIND': 'Large Cap',
            'INDHOTEL': 'Large Cap', 'LODHA': 'Large Cap', 'ZOMATO': 'Large Cap',
            'LTIM': 'Large Cap', 'BOSCHLTD': 'Large Cap', 'MRF': 'Large Cap',
            'MOTHERSON': 'Large Cap', 'UPL': 'Large Cap', 'PFC': 'Large Cap',
            'RECLTD': 'Large Cap', 'IRFC': 'Large Cap', 'ADANIGREEN': 'Large Cap',
            'ADANIPOWER': 'Large Cap', 'HINDZINC': 'Large Cap',
        }
        
        self._sector_mapping = {
            'RELIANCE': 'Energy', 'TCS': 'Technology', 'HDFCBANK': 'Banking',
            'INFY': 'Technology', 'ICICIBANK': 'Banking', 'KOTAKBANK': 'Banking',
            'HINDUNILVR': 'FMCG', 'SBIN': 'Banking', 'BHARTIARTL': 'Telecom',
            'ITC': 'FMCG', 'ASIANPAINT': 'Paints', 'MARUTI': 'Automobile',
            'AXISBANK': 'Banking', 'LT': 'Construction', 'SUNPHARMA': 'Pharmaceuticals',
            'TITAN': 'Jewellery', 'ULTRACEMCO': 'Cement', 'NESTLEIND': 'FMCG',
            'WIPRO': 'Technology', 'HCLTECH': 'Technology',
            'BAJFINANCE': 'Finance', 'BAJAJFINSV': 'Finance',
            'ADANIENT': 'Conglomerate', 'ADANIPORTS': 'Infrastructure',
            'TATAMOTORS': 'Automobile', 'M&M': 'Automobile', 'BAJAJ-AUTO': 'Automobile',
            'HEROMOTOCO': 'Automobile', 'EICHERMOT': 'Automobile', 'TVSMOTOR': 'Automobile',
            'ASHOKLEY': 'Automobile', 'BALKRISIND': 'Automobile',
            'MOTHERSON': 'Auto Ancillary', 'BOSCHLTD': 'Auto Ancillary',
            'MRF': 'Auto Ancillary', 'APOLLOTYRE': 'Auto Ancillary',
            'CEATLTD': 'Auto Ancillary', 'EXIDEIND': 'Auto Ancillary',
            'AMARAJABAT': 'Auto Ancillary',
            'BANKBARODA': 'Banking', 'PNB': 'Banking', 'CANBK': 'Banking',
            'UNIONBANK': 'Banking', 'INDIANB': 'Banking', 'IDFCFIRSTB': 'Banking',
            'BANDHANBNK': 'Banking', 'FEDERALBNK': 'Banking', 'RBLBANK': 'Banking',
            'AUBANK': 'Banking', 'INDUSINDBK': 'Banking', 'YESBANK': 'Banking',
            'MUTHOOTFIN': 'Finance', 'MANAPPURAM': 'Finance', 'CHOLAFIN': 'Finance',
            'SHRIRAMFIN': 'Finance', 'M&MFIN': 'Finance', 'POONAWALLA': 'Finance',
            'LICHSGFIN': 'Finance', 'PFC': 'Finance', 'RECLTD': 'Finance',
            'CANFINHOME': 'Finance', 'SBICARD': 'Finance', 'HDFCAMC': 'Finance',
            'IRFC': 'Finance', 'HUDCO': 'Finance',
            'ICICIGI': 'Insurance', 'ICICIPRULI': 'Insurance', 'SBILIFE': 'Insurance',
            'HDFCLIFE': 'Insurance', 'LICI': 'Insurance', 'NIACL': 'Insurance',
            'STARHEALTH': 'Insurance',
            'LTIM': 'Technology', 'MPHASIS': 'Technology', 'COFORGE': 'Technology',
            'PERSISTENT': 'Technology', 'LTTS': 'Technology', 'TATAELXSI': 'Technology',
            'CYIENT': 'Technology', 'ZENSAR': 'Technology', 'BIRLASOFT': 'Technology',
            'HAPPSTMNDS': 'Technology', 'ROUTE': 'Technology', 'MASTEK': 'Technology',
            'SONATSOFTW': 'Technology', 'KPITTECH': 'Technology', 'OFSS': 'Technology',
            'INTELLECT': 'Technology', 'NEWGEN': 'Technology', 'TANLA': 'Technology',
            'TECHM': 'Technology', 'MAPMYINDIA': 'Technology',
            'DIVISLAB': 'Pharmaceuticals', 'DRREDDY': 'Pharmaceuticals',
            'CIPLA': 'Pharmaceuticals', 'LUPIN': 'Pharmaceuticals',
            'AUROPHARMA': 'Pharmaceuticals', 'BIOCON': 'Pharmaceuticals',
            'TORNTPHARM': 'Pharmaceuticals', 'ALKEM': 'Pharmaceuticals',
            'IPCALAB': 'Pharmaceuticals', 'GLENMARK': 'Pharmaceuticals',
            'ABBOTINDIA': 'Pharmaceuticals', 'SANOFI': 'Pharmaceuticals',
            'PFIZER': 'Pharmaceuticals', 'LAURUSLABS': 'Pharmaceuticals',
            'NATCOPHARM': 'Pharmaceuticals', 'GRANULES': 'Pharmaceuticals',
            'AJANTPHARM': 'Pharmaceuticals',
            'APOLLOHOSP': 'Healthcare', 'MAXHEALTH': 'Healthcare',
            'FORTIS': 'Healthcare', 'METROPOLIS': 'Healthcare',
            'LALPATHLAB': 'Healthcare', 'MEDANTA': 'Healthcare',
            'DABUR': 'FMCG', 'MARICO': 'FMCG', 'GODREJCP': 'FMCG',
            'COLPAL': 'FMCG', 'TATACONSUM': 'FMCG', 'EMAMILTD': 'FMCG',
            'JYOTHYLAB': 'FMCG', 'VBL': 'FMCG', 'UBL': 'FMCG',
            'PGHH': 'FMCG', 'BIKAJI': 'FMCG', 'BRITANNIA': 'FMCG',
            'GAIL': 'Energy', 'IOC': 'Energy', 'BPCL': 'Energy',
            'HINDPETRO': 'Energy', 'ONGC': 'Energy', 'PETRONET': 'Energy',
            'MGL': 'Energy', 'IGL': 'Energy', 'GSPL': 'Energy',
            'GUJGASLTD': 'Energy', 'OIL': 'Energy', 'CASTROLIND': 'Energy',
            'ADANIGREEN': 'Energy',
            'NTPC': 'Power', 'POWERGRID': 'Power', 'TATAPOWER': 'Power',
            'ADANITRANS': 'Power', 'NHPC': 'Power', 'SJVN': 'Power',
            'TORNTPOWER': 'Power', 'CESC': 'Power', 'JSWENERGY': 'Power',
            'IREDA': 'Power', 'ADANIPOWER': 'Power',
            'JSWSTEEL': 'Metals', 'HINDALCO': 'Metals', 'VEDL': 'Metals',
            'COALINDIA': 'Metals', 'NMDC': 'Metals', 'SAIL': 'Metals',
            'NATIONALUM': 'Metals', 'JINDALSTEL': 'Metals', 'TATASTEEL': 'Metals',
            'RATNAMANI': 'Metals', 'APLAPOLLO': 'Metals', 'HINDZINC': 'Metals',
            'SHREECEM': 'Cement', 'AMBUJACEM': 'Cement', 'ACC': 'Cement',
            'DALMIACBHRT': 'Cement', 'RAMCOCEM': 'Cement', 'JKCEMENT': 'Cement',
            'BIRLACEM': 'Cement', 'JKLAKSHMI': 'Cement', 'STARCEMENT': 'Cement',
            'BEL': 'Defence', 'HAL': 'Defence', 'BDL': 'Defence',
            'COCHINSHIP': 'Defence', 'GRSE': 'Defence', 'MAZAGON': 'Defence',
            'DATAPATTNS': 'Defence', 'MAZDOCK': 'Defence',
            'PIDILITIND': 'Chemicals', 'SRF': 'Chemicals', 'ATUL': 'Chemicals',
            'DEEPAKNTR': 'Chemicals', 'NAVINFLUOR': 'Chemicals', 'CLEAN': 'Chemicals',
            'FLUOROCHEM': 'Chemicals', 'FINEORG': 'Chemicals', 'TATACHEM': 'Chemicals',
            'UPL': 'Chemicals', 'PI': 'Chemicals', 'SUMICHEM': 'Chemicals',
            'BASF': 'Chemicals', 'AARTI': 'Chemicals', 'ALKYLAMINE': 'Chemicals',
            'GALAXYSURF': 'Chemicals',
            'SIEMENS': 'Capital Goods', 'ABB': 'Capital Goods', 'HAVELLS': 'Capital Goods',
            'VOLTAS': 'Capital Goods', 'CROMPTON': 'Capital Goods', 'POLYCAB': 'Capital Goods',
            'CUMMINSIND': 'Capital Goods', 'THERMAX': 'Capital Goods',
            'KEI': 'Capital Goods', 'HONAUT': 'Capital Goods', 'BHEL': 'Capital Goods',
            'TIINDIA': 'Capital Goods', 'SCHAEFFLER': 'Capital Goods',
            'SKFINDIA': 'Capital Goods', 'TIMKEN': 'Capital Goods',
            'TITAGARH': 'Capital Goods', 'ELGIEQUIP': 'Capital Goods',
            'DLF': 'Real Estate', 'GODREJPROP': 'Real Estate', 'OBEROIRLTY': 'Real Estate',
            'PRESTIGE': 'Real Estate', 'BRIGADE': 'Real Estate', 'PHOENIXLTD': 'Real Estate',
            'LODHA': 'Real Estate', 'SOBHA': 'Real Estate', 'SUNTECK': 'Real Estate',
            'PAGEIND': 'Textiles', 'RAYMOND': 'Textiles', 'ARVIND': 'Textiles',
            'WELSPUNLIV': 'Textiles', 'KPR': 'Textiles', 'TRIDENT': 'Textiles',
            'BERGEPAINT': 'Paints', 'KANSAINER': 'Paints', 'AKZOINDIA': 'Paints',
            'IDEA': 'Telecom', 'TATACOMM': 'Telecom', 'INDUSTOWER': 'Telecom',
            'HFCL': 'Telecom',
            'DMART': 'Retail', 'TRENT': 'Retail', 'SHOPERSTOP': 'Retail', 'NYKAA': 'Retail',
            'ZOMATO': 'Consumer Services', 'DEVYANI': 'Consumer Services',
            'JUBLFOOD': 'Consumer Services', 'WESTLIFE': 'Consumer Services',
            'CONCOR': 'Logistics', 'DELHIVERY': 'Logistics', 'BLUEDART': 'Logistics',
            'IRCTC': 'Transport', 'RVNL': 'Infrastructure', 'IRB': 'Infrastructure',
            'NCC': 'Infrastructure', 'NBCC': 'Infrastructure', 'GMRINFRA': 'Infrastructure',
            'INTERGLOBE': 'Aviation', 'SPICEJET': 'Aviation',
            'INDHOTEL': 'Hotels', 'LEMON': 'Hotels', 'CHALET': 'Hotels', 'EIH': 'Hotels',
            'SUNTV': 'Media & Entertainment', 'ZEEL': 'Media & Entertainment',
            'PVR': 'Media & Entertainment', 'NAZARA': 'Media & Entertainment',
            'WHIRLPOOL': 'Consumer Durables', 'BATAINDIA': 'Consumer Durables',
            'RELAXO': 'Consumer Durables',
            'DIXON': 'Consumer Electronics', 'AMBER': 'Consumer Electronics',
            'IEX': 'Exchange', 'BSE': 'Exchange', 'CDSL': 'Exchange',
            'MCX': 'Exchange', 'CAMS': 'Exchange', 'ANGELONE': 'Exchange',
            'CHAMBALFERT': 'Fertilizers', 'COROMANDEL': 'Fertilizers',
            'GNFC': 'Fertilizers', 'GSFC': 'Fertilizers',
            'DEEPAKFERT': 'Fertilizers', 'RCF': 'Fertilizers',
            'ASTRAL': 'Building Materials', 'SUPREMEIND': 'Building Materials',
            'PRINCEPIPE': 'Building Materials', 'CENTURYPLY': 'Building Materials',
            'SUZLON': 'Renewable Energy', 'INOXWIND': 'Renewable Energy',
            'BAYER': 'Agriculture', 'RALLIS': 'Agriculture',
            'PAYTM': 'Fintech', 'POLICYBZR': 'Fintech',
            'GRASIM': 'Conglomerate', 'GODREJIND': 'Conglomerate',
            'KALYANKJIL': 'Jewellery', 'RAJESHEXPO': 'Jewellery',
            'BALRAMCHIN': 'Sugar', 'EIDPARRY': 'Sugar',
        }
    
    def init_zerodha(self):
        """Initialize Zerodha Kite API client"""
        if self._zerodha_initialized:
            return True
        
        try:
            api_key = os.environ.get('ZERODHA_API_KEY')
            api_secret = os.environ.get('ZERODHA_API_SECRET')
            access_token = os.environ.get('ZERODHA_ACCESS_TOKEN')
            
            if not api_key or not api_secret:
                return False
            
            from kiteconnect import KiteConnect
            self._zerodha_kite = KiteConnect(api_key=api_key)
            
            if access_token:
                self._zerodha_kite.set_access_token(access_token)
                self._zerodha_initialized = True
                self._load_zerodha_instruments()
                print("Zerodha Kite API initialized successfully")
                return True
            else:
                print("Zerodha access token not set. Login required.")
                return False
                
        except Exception as e:
            print(f"Zerodha initialization failed: {e}")
            return False
    
    def _load_zerodha_instruments(self):
        """Load NSE instruments for symbol lookup"""
        try:
            if self._zerodha_kite and self._zerodha_initialized:
                instruments = self._zerodha_kite.instruments("NSE")
                self._zerodha_instruments = {i['tradingsymbol']: i for i in instruments}
                print(f"Loaded {len(self._zerodha_instruments)} Zerodha instruments")
        except Exception as e:
            print(f"Failed to load Zerodha instruments: {e}")
            self._zerodha_instruments = {}
    
    def get_zerodha_price(self, symbol):
        """Get live price from Zerodha Kite API"""
        if not self._zerodha_initialized:
            self.init_zerodha()
        
        if not self._zerodha_kite or not self._zerodha_initialized:
            return None
            
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '').replace('-', '')
            
            if self._zerodha_instruments and clean_symbol in self._zerodha_instruments:
                instrument_token = self._zerodha_instruments[clean_symbol]['instrument_token']
                quote = self._zerodha_kite.quote(f"NSE:{clean_symbol}")
                if quote and f"NSE:{clean_symbol}" in quote:
                    return quote[f"NSE:{clean_symbol}"]['last_price']
            
            quote = self._zerodha_kite.quote(f"NSE:{clean_symbol}")
            if quote and f"NSE:{clean_symbol}" in quote:
                return quote[f"NSE:{clean_symbol}"]['last_price']
                
        except Exception as e:
            print(f"Zerodha price fetch error for {symbol}: {e}")
        
        return None
    
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
        """Get live price - Priority: Zerodha → TrueData → None (fallback to Yahoo)"""
        zerodha_price = self.get_zerodha_price(symbol)
        if zerodha_price:
            return zerodha_price
        
        if self._truedata_client and self._truedata_initialized:
            price = self._truedata_client.get_price(symbol)
            if price:
                return price
        return None
    
    def get_stock_symbol(self, stock_name):
        stock_name = stock_name.upper().strip()
        
        if stock_name.endswith(self.nse_suffix) or stock_name.endswith(self.bse_suffix):
            return stock_name
        
        # Check alias with original name (including spaces)
        if stock_name in self.symbol_aliases:
            original_name = stock_name
            stock_name = self.symbol_aliases[stock_name]
            print(f"Symbol alias: {original_name} → {stock_name}")
        else:
            # Try normalized name (remove spaces only, keep hyphens for Yahoo Finance)
            normalized_name = stock_name.replace(' ', '')
            if normalized_name in self.symbol_aliases:
                original_name = stock_name
                stock_name = self.symbol_aliases[normalized_name]
                print(f"Symbol alias (normalized): {original_name} → {stock_name}")
            elif normalized_name != stock_name:
                # Use normalized name as symbol if different
                stock_name = normalized_name
        
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
            
            historical_data = _flatten_yf_columns(yf.download(symbol, start=start_date, end=end_date, progress=False))
            
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            if historical_data.empty:
                historical_data = _flatten_yf_columns(yf.download(symbol, period="1mo", progress=False))
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
        sector = self.sector_mapping.get(base_name)
        if sector:
            return sector
        if not hasattr(self, '_sector_lookup_failed'):
            self._sector_lookup_failed = set()
        if base_name in self._sector_lookup_failed:
            return 'Others'
        try:
            symbol = self.get_stock_symbol(stock_name)
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info if hasattr(ticker, 'fast_info') else {}
            try:
                info = ticker.info
            except Exception:
                self._sector_lookup_failed.add(base_name)
                self._sector_mapping[base_name] = 'Others'
                return 'Others'
            yf_sector = info.get('sector', '')
            yf_industry = info.get('industry', '')
            if yf_sector:
                sector_map = {
                    'Financial Services': 'Finance',
                    'Consumer Cyclical': 'Consumer Durables',
                    'Consumer Defensive': 'FMCG',
                    'Basic Materials': 'Chemicals',
                    'Industrials': 'Capital Goods',
                    'Communication Services': 'Telecom',
                    'Real Estate': 'Real Estate',
                    'Healthcare': 'Healthcare',
                    'Utilities': 'Power',
                    'Energy': 'Energy',
                    'Technology': 'Technology',
                }
                mapped = sector_map.get(yf_sector, yf_sector)
                if yf_industry:
                    industry_lower = yf_industry.lower()
                    if 'bank' in industry_lower:
                        mapped = 'Banking'
                    elif 'insurance' in industry_lower:
                        mapped = 'Insurance'
                    elif 'pharma' in industry_lower or 'drug' in industry_lower:
                        mapped = 'Pharmaceuticals'
                    elif 'auto' in industry_lower and 'part' in industry_lower:
                        mapped = 'Auto Ancillary'
                    elif 'auto' in industry_lower or 'vehicle' in industry_lower:
                        mapped = 'Automobile'
                    elif 'cement' in industry_lower:
                        mapped = 'Cement'
                    elif 'steel' in industry_lower or 'metal' in industry_lower or 'mining' in industry_lower or 'aluminum' in industry_lower:
                        mapped = 'Metals'
                    elif 'oil' in industry_lower or 'gas' in industry_lower or 'refin' in industry_lower:
                        mapped = 'Energy'
                    elif 'telecom' in industry_lower:
                        mapped = 'Telecom'
                    elif 'hotel' in industry_lower or 'hospitality' in industry_lower:
                        mapped = 'Hotels'
                    elif 'fertil' in industry_lower:
                        mapped = 'Fertilizers'
                    elif 'textile' in industry_lower or 'apparel' in industry_lower:
                        mapped = 'Textiles'
                    elif 'paint' in industry_lower:
                        mapped = 'Paints'
                    elif 'jewel' in industry_lower or 'gold' in industry_lower:
                        mapped = 'Jewellery'
                    elif 'defense' in industry_lower or 'defence' in industry_lower or 'aerospace' in industry_lower:
                        mapped = 'Defence'
                    elif 'construct' in industry_lower or 'infra' in industry_lower:
                        mapped = 'Infrastructure'
                    elif 'retail' in industry_lower:
                        mapped = 'Retail'
                    elif 'media' in industry_lower or 'entertainment' in industry_lower:
                        mapped = 'Media & Entertainment'
                    elif 'chemical' in industry_lower:
                        mapped = 'Chemicals'
                    elif 'food' in industry_lower or 'beverage' in industry_lower or 'consumer' in industry_lower:
                        mapped = 'FMCG'
                    elif 'power' in industry_lower or 'electric' in industry_lower or 'utility' in industry_lower:
                        mapped = 'Power'
                    elif 'logistic' in industry_lower or 'shipping' in industry_lower:
                        mapped = 'Logistics'
                    elif 'real estate' in industry_lower or 'property' in industry_lower:
                        mapped = 'Real Estate'
                    elif 'renewable' in industry_lower or 'solar' in industry_lower or 'wind' in industry_lower:
                        mapped = 'Renewable Energy'
                    elif 'sugar' in industry_lower:
                        mapped = 'Sugar'
                    elif 'paper' in industry_lower:
                        mapped = 'Paper'
                    elif 'software' in industry_lower or 'it ' in industry_lower:
                        mapped = 'Technology'
                self._sector_mapping[base_name] = mapped
                return mapped
        except Exception:
            self._sector_lookup_failed.add(base_name)
        self._sector_mapping[base_name] = 'Others'
        return 'Others'
    
    def get_dividend_yield(self, stock_name):
        """Get dividend yield for a stock from yfinance. Returns yield as percentage (e.g. 2.5 means 2.5%)"""
        try:
            symbol = self.get_stock_symbol(stock_name)
            ticker = yf.Ticker(symbol)
            info = ticker.info

            dividend_rate = info.get('dividendRate', 0) or info.get('trailingAnnualDividendRate', 0)
            current_price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
            if dividend_rate and current_price and dividend_rate > 0 and current_price > 0:
                return round((dividend_rate / current_price) * 100, 2)

            trailing_yield = info.get('trailingAnnualDividendYield', 0)
            if trailing_yield and 0 < trailing_yield < 1:
                return round(trailing_yield * 100, 2)

            forward_yield = info.get('dividendYield', 0)
            if forward_yield:
                if forward_yield > 1:
                    return round(forward_yield, 2)
                else:
                    return round(forward_yield * 100, 2)

            return 0.0
        except Exception as e:
            print(f"Error fetching dividend for {stock_name}: {e}")
            return 0.0
    
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
