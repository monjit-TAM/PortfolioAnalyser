import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher
from utils.corporate_actions import CorporateActionsManager

class PortfolioAnalyzer:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.corporate_actions = CorporateActionsManager()
    
    def _normalize_date(self, date_value):
        """Convert various date formats to Python date object"""
        if date_value is None or pd.isna(date_value):
            return None
        
        if isinstance(date_value, pd.Timestamp):
            return date_value.date()
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif hasattr(date_value, 'date'):
            return date_value.date()
        elif isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return pd.to_datetime(date_value).date()
                except:
                    return None
        return date_value
    
    def apply_corporate_action_adjustments(self, portfolio_df):
        """Apply bonus, split, and dividend adjustments to portfolio"""
        adjusted_df = portfolio_df.copy()
        
        adjusted_df['Original Buy Price'] = adjusted_df['Buy Price']
        adjusted_df['Original Quantity'] = adjusted_df['Quantity']
        adjusted_df['Adjustment Factor'] = 1.0
        adjusted_df['Corporate Actions'] = ''
        
        for idx, row in adjusted_df.iterrows():
            stock_name = row['Stock Name']
            buy_date = self._normalize_date(row['Buy Date'])
            original_price = row['Buy Price']
            original_qty = row['Quantity']
            
            if buy_date is None:
                continue
            
            try:
                details = self.corporate_actions.get_adjustment_details(stock_name, buy_date)
                
                if details['actions_applied']:
                    factor = details['total_adjustment_factor']
                    adjusted_df.at[idx, 'Buy Price'] = original_price / factor
                    adjusted_df.at[idx, 'Quantity'] = int(original_qty * factor)
                    adjusted_df.at[idx, 'Adjustment Factor'] = factor
                    
                    action_descriptions = [a['description'] for a in details['actions_applied']]
                    adjusted_df.at[idx, 'Corporate Actions'] = '; '.join(action_descriptions)
            except Exception as e:
                print(f"Error applying corporate actions for {stock_name}: {e}")
                continue
        
        return adjusted_df
    
    def analyze_portfolio(self, portfolio_df, current_data, historical_data):
        """Perform comprehensive portfolio analysis"""
        results = {}
        
        portfolio_df = portfolio_df.copy()
        
        portfolio_df = self.apply_corporate_action_adjustments(portfolio_df)
        
        portfolio_df['Current Price'] = portfolio_df['Stock Name'].map(current_data)
        
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
