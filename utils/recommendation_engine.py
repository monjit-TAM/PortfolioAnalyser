import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher
import os

class RecommendationEngine:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self._alternative_stocks = None
    
    @property
    def alternative_stocks(self):
        if self._alternative_stocks is None:
            self._load_alternatives()
        return self._alternative_stocks
    
    def _load_alternatives(self):
        if os.environ.get('DATABASE_URL'):
            try:
                from utils.database import Database
                db = Database()
                self._alternative_stocks = db.get_alternative_stocks()
                if self._alternative_stocks:
                    if 'Others' not in self._alternative_stocks:
                        self._alternative_stocks['Others'] = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
                    return
            except Exception as e:
                print(f"Database load failed for alternatives: {e}")
        
        self._alternative_stocks = {
            'Banking': ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'SBIN', 'AXISBANK'],
            'Technology': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
            'Energy': ['RELIANCE', 'ONGC', 'IOC', 'BPCL'],
            'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA'],
            'Automobile': ['MARUTI', 'TATAMOTORS', 'BAJAJ-AUTO', 'M&M'],
            'Pharmaceuticals': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'LUPIN'],
            'Others': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
        }
    
    def generate_recommendations(self, portfolio_df, current_data, historical_data, analysis_results):
        """Generate comprehensive investment recommendations"""
        recommendations = []
        
        for _, stock in portfolio_df.iterrows():
            stock_name = stock['Stock Name']
            
            # Get fundamental data
            fundamentals = self.data_fetcher.get_stock_fundamentals(stock_name)
            
            # Analyze from value investing perspective
            value_analysis = self.analyze_value_perspective(stock, fundamentals, historical_data.get(stock_name))
            
            # Analyze from growth investing perspective
            growth_analysis = self.analyze_growth_perspective(stock, fundamentals, historical_data.get(stock_name))
            
            # Generate overall recommendation
            overall_recommendation = self.generate_overall_recommendation(
                stock, value_analysis, growth_analysis, fundamentals
            )
            
            # Get alternative suggestions if sell is recommended
            alternatives = []
            if overall_recommendation['action'] == 'SELL':
                alternatives = self.get_alternative_stocks(stock['Sector'], stock_name)
            
            recommendation = {
                'stock_name': stock_name,
                'current_price': stock['Current Price'],
                'buy_price': stock['Buy Price'],
                'gain_loss_percentage': stock['Percentage Gain/Loss'],
                'value_analysis': value_analysis,
                'growth_analysis': growth_analysis,
                'overall_recommendation': overall_recommendation,
                'alternatives': alternatives,
                'fundamentals': fundamentals
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_value_perspective(self, stock, fundamentals, historical_data):
        """Analyze stock from value investing perspective"""
        analysis = {
            'score': 0,
            'factors': [],
            'recommendation': 'HOLD',
            'rationale': []
        }
        
        try:
            # P/E Ratio analysis
            pe_ratio = fundamentals.get('pe_ratio')
            if pe_ratio:
                if pe_ratio < 15:
                    analysis['score'] += 2
                    analysis['factors'].append(f"Low P/E ratio: {pe_ratio:.2f}")
                    analysis['rationale'].append("Potentially undervalued based on earnings")
                elif pe_ratio > 25:
                    analysis['score'] -= 1
                    analysis['factors'].append(f"High P/E ratio: {pe_ratio:.2f}")
                    analysis['rationale'].append("May be overvalued based on earnings")
                else:
                    analysis['factors'].append(f"Moderate P/E ratio: {pe_ratio:.2f}")
            
            # P/B Ratio analysis
            pb_ratio = fundamentals.get('pb_ratio')
            if pb_ratio:
                if pb_ratio < 1.5:
                    analysis['score'] += 2
                    analysis['factors'].append(f"Low P/B ratio: {pb_ratio:.2f}")
                    analysis['rationale'].append("Trading below book value - good value")
                elif pb_ratio > 3:
                    analysis['score'] -= 1
                    analysis['factors'].append(f"High P/B ratio: {pb_ratio:.2f}")
            
            # Dividend Yield analysis
            dividend_yield = fundamentals.get('dividend_yield')
            if dividend_yield:
                if dividend_yield > 0.03:  # > 3%
                    analysis['score'] += 1
                    analysis['factors'].append(f"Good dividend yield: {dividend_yield*100:.2f}%")
                    analysis['rationale'].append("Provides steady income through dividends")
            
            # Debt to Equity analysis
            debt_to_equity = fundamentals.get('debt_to_equity')
            if debt_to_equity:
                if debt_to_equity < 0.5:
                    analysis['score'] += 1
                    analysis['factors'].append(f"Low debt-to-equity: {debt_to_equity:.2f}")
                    analysis['rationale'].append("Conservative debt levels")
                elif debt_to_equity > 2:
                    analysis['score'] -= 1
                    analysis['factors'].append(f"High debt-to-equity: {debt_to_equity:.2f}")
                    analysis['rationale'].append("High debt levels may be risky")
            
            # Current performance vs buy price
            gain_loss = stock['Percentage Gain/Loss']
            if gain_loss < -20:
                analysis['score'] += 1
                analysis['rationale'].append("Significant decline may present value opportunity")
            elif gain_loss > 50:
                analysis['score'] -= 1
                analysis['rationale'].append("Substantial gains - may be overvalued")
            
            # Final recommendation based on score
            if analysis['score'] >= 3:
                analysis['recommendation'] = 'BUY'
            elif analysis['score'] <= -2:
                analysis['recommendation'] = 'SELL'
            else:
                analysis['recommendation'] = 'HOLD'
            
        except Exception as e:
            analysis['rationale'].append("Limited fundamental data available")
        
        return analysis
    
    def analyze_growth_perspective(self, stock, fundamentals, historical_data):
        """Analyze stock from growth investing perspective"""
        analysis = {
            'score': 0,
            'factors': [],
            'recommendation': 'HOLD',
            'rationale': []
        }
        
        try:
            # Revenue Growth analysis
            revenue_growth = fundamentals.get('revenue_growth')
            if revenue_growth is not None:
                if revenue_growth > 0.15:  # > 15%
                    analysis['score'] += 2
                    analysis['factors'].append(f"High revenue growth: {revenue_growth*100:.2f}%")
                    analysis['rationale'].append("Strong revenue growth indicates business expansion")
                elif revenue_growth > 0.05:  # 5-15% moderate growth
                    analysis['rationale'].append(f"Moderate revenue growth of {revenue_growth*100:.1f}%")
                elif revenue_growth >= 0:  # 0-5% low growth
                    analysis['rationale'].append("Stable but low revenue growth")
                else:  # Negative
                    analysis['score'] -= 1
                    analysis['factors'].append(f"Negative revenue growth: {revenue_growth*100:.2f}%")
                    analysis['rationale'].append("Revenue decline signals business contraction")
            
            # Earnings Growth analysis
            earnings_growth = fundamentals.get('earnings_growth')
            if earnings_growth is not None:
                if earnings_growth > 0.20:  # > 20%
                    analysis['score'] += 2
                    analysis['factors'].append(f"High earnings growth: {earnings_growth*100:.2f}%")
                    analysis['rationale'].append("Excellent earnings growth potential")
                elif earnings_growth > 0.10:  # 10-20% moderate
                    analysis['rationale'].append(f"Solid earnings growth of {earnings_growth*100:.1f}%")
                elif earnings_growth >= 0:  # 0-10%
                    analysis['rationale'].append("Modest earnings growth trajectory")
                else:  # Negative
                    analysis['score'] -= 1
                    analysis['factors'].append(f"Negative earnings growth: {earnings_growth*100:.2f}%")
                    analysis['rationale'].append("Declining earnings raises growth concerns")
            
            # ROE analysis
            roe = fundamentals.get('roe')
            if roe is not None:
                if roe > 0.20:  # > 20%
                    analysis['score'] += 1
                    analysis['factors'].append(f"High ROE: {roe*100:.2f}%")
                    analysis['rationale'].append("Efficient use of shareholder equity")
                elif roe > 0.12:  # 12-20% moderate
                    analysis['rationale'].append(f"Acceptable ROE of {roe*100:.1f}%")
                elif roe >= 0.10:  # 10-12%
                    analysis['rationale'].append("ROE below industry average")
                else:  # < 10%
                    analysis['score'] -= 1
                    analysis['factors'].append(f"Low ROE: {roe*100:.2f}%")
                    analysis['rationale'].append("Poor capital efficiency limits growth")
            
            # Price momentum analysis
            fifty_two_week_high = fundamentals.get('fifty_two_week_high')
            current_price = stock['Current Price']
            
            if fifty_two_week_high and current_price:
                price_from_high = (current_price / fifty_two_week_high) * 100
                if price_from_high > 90:  # Within 10% of 52-week high
                    analysis['score'] += 1
                    analysis['factors'].append("Near 52-week high - strong momentum")
                    analysis['rationale'].append("Stock showing strong price momentum")
                elif price_from_high > 75:  # 75-90%
                    analysis['rationale'].append(f"Trading at {price_from_high:.0f}% of 52-week high")
                elif price_from_high < 70:  # More than 30% below 52-week high
                    analysis['score'] -= 1
                    analysis['factors'].append("Significantly below 52-week high")
                    analysis['rationale'].append("Weak momentum - trading well below 52-week high")
            
            # Current performance analysis
            gain_loss = stock['Percentage Gain/Loss']
            if gain_loss > 30:
                analysis['score'] += 1
                analysis['rationale'].append("Strong performance indicates growth potential")
            elif gain_loss > 10:
                analysis['rationale'].append(f"Positive return of {gain_loss:.1f}% shows steady growth")
            elif gain_loss >= 0:
                analysis['rationale'].append("Flat performance - monitor for catalysts")
            elif gain_loss > -30:
                analysis['rationale'].append(f"Underperforming with {gain_loss:.1f}% loss")
            else:
                analysis['score'] -= 1
                analysis['rationale'].append("Poor performance may indicate growth challenges")
            
            # Final recommendation based on score
            if analysis['score'] >= 3:
                analysis['recommendation'] = 'BUY'
            elif analysis['score'] <= -2:
                analysis['recommendation'] = 'SELL'
            else:
                analysis['recommendation'] = 'HOLD'
            
        except Exception as e:
            analysis['rationale'].append("Limited growth data available")
        
        return analysis
    
    def generate_overall_recommendation(self, stock, value_analysis, growth_analysis, fundamentals):
        """Generate overall recommendation combining both perspectives"""
        
        # Scoring system
        action_scores = {'BUY': 2, 'HOLD': 1, 'SELL': 0}
        
        value_score = action_scores[value_analysis['recommendation']]
        growth_score = action_scores[growth_analysis['recommendation']]
        
        # Weight the perspectives (can be adjusted based on preference)
        combined_score = (value_score + growth_score) / 2
        
        # Determine action
        if combined_score >= 1.5:
            action = 'BUY'
            confidence = 'High' if combined_score >= 1.8 else 'Medium'
        elif combined_score >= 1:
            action = 'HOLD'
            confidence = 'Medium'
        else:
            action = 'SELL'
            confidence = 'High' if combined_score <= 0.5 else 'Medium'
        
        # Generate rationale
        rationale = []
        
        if value_analysis['recommendation'] == growth_analysis['recommendation']:
            rationale.append(f"Both value and growth perspectives agree on {action}")
        else:
            rationale.append(f"Mixed signals: Value suggests {value_analysis['recommendation']}, Growth suggests {growth_analysis['recommendation']}")
        
        # Add performance-based rationale
        gain_loss = stock['Percentage Gain/Loss']
        if gain_loss > 0:
            rationale.append(f"Currently profitable with {gain_loss:.2f}% gains")
        else:
            rationale.append(f"Currently in loss with {abs(gain_loss):.2f}% decline")
        
        return {
            'action': action,
            'confidence': confidence,
            'rationale': rationale,
            'combined_score': combined_score
        }
    
    def get_alternative_stocks(self, sector, current_stock):
        """Get alternative stock suggestions for the given sector"""
        if sector not in self.alternative_stocks:
            sector = 'Others'
        
        alternatives = [stock for stock in self.alternative_stocks[sector] if stock != current_stock.upper()]
        
        # Return top 3 alternatives with basic rationale
        alternative_recommendations = []
        for alt_stock in alternatives[:3]:
            alternative_recommendations.append({
                'stock_name': alt_stock,
                'sector': sector,
                'rationale': f"Alternative {sector} stock with potentially better fundamentals"
            })
        
        return alternative_recommendations
