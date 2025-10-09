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
        portfolio_df['Investment Value'] = portfolio_df['Buy Price'] * portfolio_df['Quantity']
        portfolio_df['Current Value'] = portfolio_df['Current Price'] * portfolio_df['Quantity']
        portfolio_df['Absolute Gain/Loss'] = portfolio_df['Current Value'] - portfolio_df['Investment Value']
        portfolio_df['Percentage Gain/Loss'] = (portfolio_df['Absolute Gain/Loss'] / portfolio_df['Investment Value']) * 100
        
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
        
        # Risk metrics
        results['risk_metrics'] = self.calculate_risk_metrics(portfolio_df, historical_data)
        
        # Correlation analysis
        results['correlation_matrix'] = self.calculate_correlation_matrix(historical_data)
        
        return results
    
    def calculate_ath_since_purchase(self, portfolio_df, historical_data):
        """Calculate all-time high for each stock since purchase date"""
        ath_values = []
        
        for _, stock in portfolio_df.iterrows():
            stock_name = stock['Stock Name']
            buy_date = stock['Buy Date']
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                stock_hist = historical_data[stock_name]
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
    
    def calculate_risk_metrics(self, portfolio_df, historical_data):
        """Calculate portfolio risk metrics"""
        try:
            # Calculate portfolio weights
            weights = portfolio_df['Current Value'] / portfolio_df['Current Value'].sum()
            
            # Calculate individual stock volatilities
            volatilities = []
            returns_data = []
            
            for _, stock in portfolio_df.iterrows():
                stock_name = stock['Stock Name']
                
                if stock_name in historical_data and not historical_data[stock_name].empty:
                    stock_hist = historical_data[stock_name]
                    if len(stock_hist) > 1:
                        returns = stock_hist['Close'].pct_change().dropna()
                        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                        volatilities.append(volatility)
                        returns_data.append(returns)
                    else:
                        volatilities.append(0)
                        returns_data.append(pd.Series([0]))
                else:
                    volatilities.append(0)
                    returns_data.append(pd.Series([0]))
            
            # Portfolio volatility (simplified - assuming zero correlation)
            portfolio_volatility = np.sqrt(np.sum((weights ** 2) * np.array(volatilities) ** 2))
            
            # Sharpe ratio (simplified - assuming risk-free rate of 6%)
            risk_free_rate = 0.06
            portfolio_return = (portfolio_df['Absolute Gain/Loss'].sum() / portfolio_df['Investment Value'].sum())
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            return {
                'portfolio_volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_stock_weight': weights.max(),
                'min_stock_weight': weights.min(),
                'diversification_ratio': len(portfolio_df) / portfolio_df['Current Value'].sum() * 1000000  # Stocks per million
            }
        
        except Exception as e:
            return {
                'portfolio_volatility': 0,
                'sharpe_ratio': 0,
                'max_stock_weight': 0,
                'min_stock_weight': 0,
                'diversification_ratio': 0
            }
    
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
