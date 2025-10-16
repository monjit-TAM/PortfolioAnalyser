import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataFetcher:
    def __init__(self):
        self.nse_suffix = ".NS"
        self.bse_suffix = ".BO"
        
        # Symbol aliases - maps common abbreviations to correct Yahoo Finance symbols
        self.symbol_aliases = {
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
        
        # If stock_name already has a suffix (.NS or .BO), return it as-is
        if stock_name.endswith(self.nse_suffix) or stock_name.endswith(self.bse_suffix):
            return stock_name
        
        # Check if this is a common abbreviation and convert to correct symbol
        if stock_name in self.symbol_aliases:
            original_name = stock_name
            stock_name = self.symbol_aliases[stock_name]
            # Quiet logging - avoid UI clutter for large portfolios
            print(f"Symbol alias: {original_name} → {stock_name}")
        
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
        """Fetch stock data including current price and historical data using EOD data"""
        symbol = self.get_stock_symbol(stock_name)
        
        try:
            # Use yf.download for more reliable EOD price data
            end_date = datetime.now()
            
            # Download historical data from start_date to today
            historical_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            # Normalize index to timezone-naive to prevent comparison issues
            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                historical_data.index = historical_data.index.tz_localize(None)
            
            if historical_data.empty:
                # If no historical data, try to get recent data
                historical_data = yf.download(symbol, period="1mo", progress=False)
                if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                    historical_data.index = historical_data.index.tz_localize(None)
            
            if historical_data.empty:
                raise ValueError(f"No data available for {stock_name}")
            
            # Get current price from the most recent closing price
            current_price = float(historical_data['Close'].iloc[-1])
            
            return current_price, historical_data
            
        except Exception as e:
            st.error(f"❌ Could not fetch data for {stock_name} ({symbol}): {str(e)}")
            # Try fallback with ticker.info and ticker.history
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
                
                if current_price:
                    st.warning(f"⚠️ Using fallback price for {stock_name}: ₹{current_price}")
                    
                    # Try to get historical data using ticker.history() method
                    try:
                        end_date = datetime.now()
                        historical_data = ticker.history(start=start_date, end=end_date)
                        
                        # Normalize index
                        if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                            historical_data.index = historical_data.index.tz_localize(None)
                        
                        if not historical_data.empty:
                            return float(current_price), historical_data
                        else:
                            # Try shorter period if full history fails
                            historical_data = ticker.history(period="1y")
                            if hasattr(historical_data.index, 'tz') and historical_data.index.tz is not None:
                                historical_data.index = historical_data.index.tz_localize(None)
                            return float(current_price), historical_data
                    except:
                        # If historical data fetch fails, return price with empty history
                        return float(current_price), pd.DataFrame()
            except:
                pass
            
            st.error(f"❌ Unable to fetch any price data for {stock_name}. Please check the stock symbol.")
            return None, pd.DataFrame()
    
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
        # Remove suffix for lookup
        base_name = stock_name.replace(self.nse_suffix, '').replace(self.bse_suffix, '')
        # Check if this is an alias
        if base_name in self.symbol_aliases:
            base_name = self.symbol_aliases[base_name]
        return self.stock_categories.get(base_name, 'Mid Cap')  # Default to Mid Cap
    
    def get_stock_sector(self, stock_name):
        """Get stock sector"""
        stock_name = stock_name.upper().strip()
        # Remove suffix for lookup
        base_name = stock_name.replace(self.nse_suffix, '').replace(self.bse_suffix, '')
        # Check if this is an alias
        if base_name in self.symbol_aliases:
            base_name = self.symbol_aliases[base_name]
        return self.sector_mapping.get(base_name, 'Others')  # Default to Others
    
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
