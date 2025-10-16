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
    
    def calculate_risk_metrics(self, portfolio_df, historical_data):
        """Calculate comprehensive portfolio risk metrics including Beta, VaR, and Sharpe Ratio"""
        try:
            # Debug logging
            print(f"[DEBUG] Calculating risk metrics for {len(portfolio_df)} stocks")
            print(f"[DEBUG] Historical data keys: {list(historical_data.keys())}")
            print(f"[DEBUG] Portfolio stock names: {portfolio_df['Stock Name'].tolist()}")
            
            # Calculate portfolio weights
            weights = portfolio_df['Current Value'] / portfolio_df['Current Value'].sum()
            
            # Calculate individual stock volatilities and collect returns
            volatilities = []
            returns_data = []
            betas = []
            
            # Skip NIFTY beta calculation for now - focus on getting risk metrics working
            # All betas default to 1.0
            
            for _, stock in portfolio_df.iterrows():
                stock_name = stock['Stock Name']
                
                print(f"[DEBUG] Checking stock: '{stock_name}' - In hist_data: {stock_name in historical_data}, Empty: {historical_data.get(stock_name, pd.DataFrame()).empty if stock_name in historical_data else 'N/A'}")
                
                if stock_name in historical_data and not historical_data[stock_name].empty:
                    stock_hist = historical_data[stock_name]
                    if len(stock_hist) > 1:
                        returns = stock_hist['Close'].pct_change().dropna()
                        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                        volatilities.append(volatility)
                        returns_data.append(returns)
                        betas.append(1.0)  # Default beta
                    else:
                        volatilities.append(0)
                        returns_data.append(pd.Series(dtype=float))  # Empty series
                        betas.append(1.0)
                else:
                    volatilities.append(0)
                    returns_data.append(pd.Series(dtype=float))  # Empty series
                    betas.append(1.0)
            
            # Portfolio volatility (simplified - assuming zero correlation)
            portfolio_volatility = np.sqrt(np.sum((weights ** 2) * np.array(volatilities) ** 2))
            
            # Portfolio Beta (weighted average)
            portfolio_beta = np.sum(weights * np.array(betas))
            
            # Calculate portfolio returns for VaR
            portfolio_return_annualized = (portfolio_df['Absolute Gain/Loss'].sum() / portfolio_df['Investment Value'].sum())
            
            # Sharpe ratio (assuming risk-free rate of 6%)
            risk_free_rate = 0.06
            sharpe_ratio = (portfolio_return_annualized - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Value at Risk (VaR) - 95% confidence level
            # Using parametric method: VaR = mean - (z_score * std_dev)
            if returns_data and len([r for r in returns_data if len(r) > 0]) > 0:
                # Calculate portfolio daily returns
                portfolio_daily_returns = []
                for i in range(len(returns_data)):
                    if len(returns_data[i]) > 0:
                        weighted_return = returns_data[i] * weights.iloc[i]
                        portfolio_daily_returns.append(weighted_return)
                
                if portfolio_daily_returns:
                    # Sum weighted returns
                    combined_returns = pd.concat(portfolio_daily_returns, axis=1).sum(axis=1)
                    mean_return = combined_returns.mean()
                    std_return = combined_returns.std()
                    
                    # 95% VaR (1.65 for 95% confidence)
                    var_95 = abs(mean_return - 1.65 * std_return)
                    
                    # 99% VaR (2.33 for 99% confidence)
                    var_99 = abs(mean_return - 2.33 * std_return)
                else:
                    var_95 = 0
                    var_99 = 0
            else:
                var_95 = 0
                var_99 = 0
            
            # Sortino Ratio (focuses on downside risk)
            downside_returns = [r for returns_series in returns_data for r in returns_series if r < 0]
            if downside_returns:
                downside_std = np.std(downside_returns) * np.sqrt(252)
                sortino_ratio = (portfolio_return_annualized - risk_free_rate) / downside_std if downside_std > 0 else 0
            else:
                sortino_ratio = sharpe_ratio  # If no downside, use Sharpe
            
            # Maximum Drawdown
            max_drawdown = 0
            if returns_data and len([r for r in returns_data if len(r) > 0]) > 0 and 'combined_returns' in locals():
                cumulative_returns = (1 + combined_returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0
            
            return {
                'portfolio_volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'portfolio_beta': portfolio_beta,
                'var_95': var_95,
                'var_99': var_99,
                'max_drawdown': max_drawdown,
                'max_stock_weight': weights.max(),
                'min_stock_weight': weights.min(),
                'diversification_ratio': len(portfolio_df) / portfolio_df['Current Value'].sum() * 1000000  # Stocks per million
            }
        
        except Exception as e:
            import traceback
            print(f"🔍 DEBUG: Risk metrics calculation failed: {str(e)}")
            print(f"DEBUG: Portfolio shape: {portfolio_df.shape if portfolio_df is not None else 'None'}")
            print(f"DEBUG: Historical data keys: {list(historical_data.keys()) if historical_data else 'None'}")
            print(f"DEBUG Traceback: {traceback.format_exc()}")
            return {
                'portfolio_volatility': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'portfolio_beta': 1.0,
                'var_95': 0,
                'var_99': 0,
                'max_drawdown': 0,
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
