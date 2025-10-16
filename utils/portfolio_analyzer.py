import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher

class PortfolioAnalyzer:
    def __init__(self):
        self.data_fetcher = DataFetcher()
    
    def analyze_portfolio(self, portfolio_df, current_data, historical_data):
        """Perform comprehensive portfolio analysis"""
        results = {}
        
        # Calculate basic portfolio metrics
        portfolio_df = portfolio_df.copy()
        
        # Add current prices and calculations
        portfolio_df['Current Price'] = portfolio_df['Stock Name'].map(current_data)
        
        # Handle missing prices (fill with 0 or buy price as fallback)
        portfolio_df['Current Price'] = portfolio_df['Current Price'].fillna(portfolio_df['Buy Price'])
        
        portfolio_df['Investment Value'] = portfolio_df['Buy Price'] * portfolio_df['Quantity']
        portfolio_df['Current Value'] = portfolio_df['Current Price'] * portfolio_df['Quantity']
        portfolio_df['Absolute Gain/Loss'] = portfolio_df['Current Value'] - portfolio_df['Investment Value']
        
        # Safely calculate percentage with division by zero protection
        portfolio_df['Percentage Gain/Loss'] = portfolio_df.apply(
            lambda row: (row['Absolute Gain/Loss'] / row['Investment Value'] * 100) if row['Investment Value'] != 0 else 0,
            axis=1
        )
        
        # Add stock categories and sectors
        portfolio_df['Category'] = portfolio_df['Stock Name'].apply(self.data_fetcher.get_stock_category)
        portfolio_df['Sector'] = portfolio_df['Stock Name'].apply(self.data_fetcher.get_stock_sector)
        
        # Calculate all-time highs since purchase
        portfolio_df['All Time High Since Purchase'] = self.calculate_ath_since_purchase(portfolio_df, historical_data)
        portfolio_df['Potential Gain from ATH'] = ((portfolio_df['All Time High Since Purchase'] - portfolio_df['Buy Price']) / portfolio_df['Buy Price']) * 100
        
        # Portfolio summary
        results['portfolio_summary'] = {
            'total_investment': portfolio_df['Investment Value'].sum(),
            'current_value': portfolio_df['Current Value'].sum(),
            'total_gain_loss': portfolio_df['Absolute Gain/Loss'].sum(),
            'total_gain_loss_percentage': (portfolio_df['Absolute Gain/Loss'].sum() / portfolio_df['Investment Value'].sum()) * 100,
            'number_of_stocks': len(portfolio_df),
            'profitable_stocks': len(portfolio_df[portfolio_df['Absolute Gain/Loss'] > 0]),
            'loss_making_stocks': len(portfolio_df[portfolio_df['Absolute Gain/Loss'] < 0])
        }
        
        # Sector analysis
        results['sector_analysis'] = self.analyze_sectors(portfolio_df)
        
        # Category analysis
        results['category_analysis'] = self.analyze_categories(portfolio_df)
        
        # Stock performance
        results['stock_performance'] = portfolio_df.to_dict('records')
        
        # Correlation analysis
        results['correlation_matrix'] = self.calculate_correlation_matrix(historical_data)
        
        return results
    
    def calculate_ath_since_purchase(self, portfolio_df, historical_data):
        """Calculate all-time high for each stock since purchase date"""
        ath_values = []
        
        for _, stock in portfolio_df.iterrows():
            stock_name = stock['Stock Name']
            buy_date = pd.to_datetime(stock['Buy Date']).tz_localize(None)  # Make timezone-naive
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                stock_hist = historical_data[stock_name]
                # Normalize stock_hist index to be timezone-naive
                if hasattr(stock_hist.index, 'tz') and stock_hist.index.tz is not None:
                    stock_hist = stock_hist.copy()
                    stock_hist.index = stock_hist.index.tz_localize(None)
                post_buy_data = stock_hist[stock_hist.index >= buy_date]
                
                if not post_buy_data.empty:
                    ath = post_buy_data['High'].max()
                    ath_values.append(ath)
                else:
                    ath_values.append(stock['Current Price'])
            else:
                ath_values.append(stock['Current Price'])
        
        return ath_values
    
    def analyze_sectors(self, portfolio_df):
        """Analyze portfolio by sectors"""
        sector_analysis = portfolio_df.groupby('Sector').agg({
            'Investment Value': 'sum',
            'Current Value': 'sum',
            'Absolute Gain/Loss': 'sum',
            'Stock Name': 'count'
        }).reset_index()
        
        sector_analysis['Percentage of Portfolio'] = (sector_analysis['Current Value'] / sector_analysis['Current Value'].sum()) * 100
        sector_analysis['Sector Return %'] = (sector_analysis['Absolute Gain/Loss'] / sector_analysis['Investment Value']) * 100
        sector_analysis.rename(columns={'Stock Name': 'Number of Stocks'}, inplace=True)
        
        return sector_analysis.to_dict('records')
    
    def analyze_categories(self, portfolio_df):
        """Analyze portfolio by market cap categories"""
        category_analysis = portfolio_df.groupby('Category').agg({
            'Investment Value': 'sum',
            'Current Value': 'sum',
            'Absolute Gain/Loss': 'sum',
            'Stock Name': 'count'
        }).reset_index()
        
        category_analysis['Percentage of Portfolio'] = (category_analysis['Current Value'] / category_analysis['Current Value'].sum()) * 100
        category_analysis['Category Return %'] = (category_analysis['Absolute Gain/Loss'] / category_analysis['Investment Value']) * 100
        category_analysis.rename(columns={'Stock Name': 'Number of Stocks'}, inplace=True)
        
        return category_analysis.to_dict('records')
    
    def calculate_correlation_matrix(self, historical_data):
        """Calculate correlation matrix between stocks"""
        try:
            if len(historical_data) < 2:
                return {}
            
            # Prepare returns data
            returns_df = pd.DataFrame()
            
            for stock_name, stock_hist in historical_data.items():
                if not stock_hist.empty and len(stock_hist) > 1:
                    returns = stock_hist['Close'].pct_change().dropna()
                    returns_df[stock_name] = returns
            
            if returns_df.empty:
                return {}
            
            # Calculate correlation matrix
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix.to_dict()
        
        except Exception as e:
            return {}
