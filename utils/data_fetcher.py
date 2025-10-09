import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataFetcher:
    def __init__(self):
        self.nse_suffix = ".NS"
        self.bse_suffix = ".BO"
        
        # Indian market indices
        self.indices = {
            'NIFTY50': '^NSEI',
            'NIFTY_MIDCAP_100': '^NSEMDCP50',
            'NIFTY_SMALLCAP_100': '^NSESMLCAP'
        }
        
        # Stock categorization (simplified - in production, use a comprehensive database)
        self.stock_categories = {
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
            # Add more stocks as needed
        }
        
        # Sector mapping
        self.sector_mapping = {
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
    
    def get_stock_symbol(self, stock_name):
        """Convert stock name to Yahoo Finance symbol"""
        stock_name = stock_name.upper().strip()
        
        # Try NSE first
        nse_symbol = f"{stock_name}{self.nse_suffix}"
        try:
            ticker = yf.Ticker(nse_symbol)
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                return nse_symbol
        except:
            pass
        
        # Try BSE
        bse_symbol = f"{stock_name}{self.bse_suffix}"
        try:
            ticker = yf.Ticker(bse_symbol)
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                return bse_symbol
        except:
            pass
        
        # Return NSE symbol as default
        return nse_symbol
    
    def get_stock_data(self, stock_name, start_date):
        """Fetch stock data including current price and historical data"""
        symbol = self.get_stock_symbol(stock_name)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current price
            info = ticker.info
            current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            
            if current_price is None:
                # Fallback: get latest price from history
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                else:
                    raise ValueError(f"Could not fetch price for {stock_name}")
            
            # Get historical data from buy date
            end_date = datetime.now()
            historical_data = ticker.history(start=start_date, end=end_date)
            
            # Normalize index to timezone-naive to prevent comparison issues
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            return current_price, historical_data
            
        except Exception as e:
            st.warning(f"Could not fetch data for {stock_name}: {str(e)}")
            # Return dummy data to prevent crashes
            return 100.0, pd.DataFrame()
    
    def get_index_data(self, index_name, start_date):
        """Fetch index data for benchmark comparison"""
        if index_name not in self.indices:
            return pd.DataFrame()
        
        symbol = self.indices[index_name]
        
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            historical_data = ticker.history(start=start_date, end=end_date)
            
            # Normalize index to timezone-naive to prevent comparison issues
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            return historical_data
        except Exception as e:
            st.warning(f"Could not fetch index data for {index_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_category(self, stock_name):
        """Get stock category (Large Cap, Mid Cap, Small Cap)"""
        stock_name = stock_name.upper().strip()
        return self.stock_categories.get(stock_name, 'Mid Cap')  # Default to Mid Cap
    
    def get_stock_sector(self, stock_name):
        """Get stock sector"""
        stock_name = stock_name.upper().strip()
        return self.sector_mapping.get(stock_name, 'Others')  # Default to Others
    
    def get_stock_fundamentals(self, stock_name):
        """Get basic fundamental data for the stock"""
        symbol = self.get_stock_symbol(stock_name)
        
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
            }
            
            return fundamentals
            
        except Exception as e:
            st.warning(f"Could not fetch fundamentals for {stock_name}: {str(e)}")
            return {}
