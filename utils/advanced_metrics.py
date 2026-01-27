import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedMetricsCalculator:
    def __init__(self):
        self.market_cap_thresholds = {
            'large_cap': 20000,
            'mid_cap': 5000,
            'small_cap': 0
        }
        
        self.risk_thresholds = {
            'single_stock_max': 15,
            'sector_max': 30,
            'top3_max': 40,
            'top5_max': 60
        }
    
    def calculate_all_metrics(self, portfolio_df, historical_data, benchmark_data=None):
        results = {}
        
        results['structural'] = self.calculate_structural_diagnostics(portfolio_df)
        results['style'] = self.calculate_style_analysis(portfolio_df, historical_data)
        results['concentration'] = self.calculate_concentration_risk(portfolio_df)
        results['volatility'] = self.calculate_volatility_metrics(portfolio_df, historical_data, benchmark_data)
        results['behavior'] = self.calculate_behavior_score(portfolio_df)
        results['drift'] = self.calculate_drift_analysis(portfolio_df, benchmark_data)
        results['overlap'] = self.calculate_overlap_detection(portfolio_df)
        results['attribution'] = self.calculate_return_attribution(portfolio_df)
        results['liquidity'] = self.calculate_liquidity_risk(portfolio_df, historical_data)
        results['tail_risk'] = self.calculate_tail_risk(portfolio_df, historical_data)
        results['macro'] = self.calculate_macro_sensitivity(portfolio_df)
        results['tax_impact'] = self.calculate_tax_impact(portfolio_df)
        results['health_score'] = self.calculate_health_score(results)
        results['scenario'] = self.calculate_scenario_analysis(portfolio_df, historical_data, benchmark_data)
        
        return results
    
    def calculate_structural_diagnostics(self, portfolio_df):
        if portfolio_df is None or portfolio_df.empty:
            return {
                'market_cap_allocation': {'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0},
                'sector_allocation': {},
                'industry_concentration': {'top_sector': 'N/A', 'top_sector_pct': 0, 'is_concentrated': False},
                'thematic_clusters': ['Empty Portfolio'],
                'total_stocks': 0,
                'total_value': 0
            }
        
        total_value = portfolio_df['Current Value'].sum()
        total_stocks = len(portfolio_df)
        
        if total_stocks == 0 or total_value == 0:
            return {
                'market_cap_allocation': {'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0},
                'sector_allocation': {},
                'industry_concentration': {'top_sector': 'N/A', 'top_sector_pct': 0, 'is_concentrated': False},
                'thematic_clusters': ['Empty Portfolio'],
                'total_stocks': 0,
                'total_value': 0
            }
        
        market_cap_allocation = {'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0}
        if 'Category' in portfolio_df.columns:
            for cat in portfolio_df['Category'].unique():
                cat_value = portfolio_df[portfolio_df['Category'] == cat]['Current Value'].sum()
                pct = (cat_value / total_value * 100) if total_value > 0 else 0
                if 'Large' in str(cat):
                    market_cap_allocation['Large Cap'] += pct
                elif 'Mid' in str(cat):
                    market_cap_allocation['Mid Cap'] += pct
                else:
                    market_cap_allocation['Small Cap'] += pct
        
        sector_allocation = {}
        if 'Sector' in portfolio_df.columns:
            for sector in portfolio_df['Sector'].unique():
                sector_value = portfolio_df[portfolio_df['Sector'] == sector]['Current Value'].sum()
                sector_allocation[sector] = (sector_value / total_value * 100) if total_value > 0 else 0
        
        industry_concentration = {}
        if 'Sector' in portfolio_df.columns:
            top_sector = max(sector_allocation.items(), key=lambda x: x[1]) if sector_allocation else ('N/A', 0)
            industry_concentration = {
                'top_sector': top_sector[0],
                'top_sector_pct': top_sector[1],
                'is_concentrated': top_sector[1] > 30
            }
        
        thematic_clusters = []
        psu_stocks = ['ONGC', 'NTPC', 'POWERGRID', 'COALINDIA', 'BPCL', 'IOC', 'GAIL', 'NHPC', 'RECLTD', 'PFC']
        tech_stocks = ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'MPHASIS', 'COFORGE', 'PERSISTENT']
        banking_stocks = ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'BANKBARODA']
        
        psu_count = sum(1 for s in portfolio_df['Stock Name'] if any(p in str(s).upper() for p in psu_stocks))
        tech_count = sum(1 for s in portfolio_df['Stock Name'] if any(t in str(s).upper() for t in tech_stocks))
        banking_count = sum(1 for s in portfolio_df['Stock Name'] if any(b in str(s).upper() for b in banking_stocks))
        
        if psu_count / total_stocks > 0.3:
            thematic_clusters.append('PSU-Heavy')
        if tech_count / total_stocks > 0.3:
            thematic_clusters.append('Tech-Heavy')
        if banking_count / total_stocks > 0.3:
            thematic_clusters.append('Banking-Heavy')
        
        return {
            'market_cap_allocation': market_cap_allocation,
            'sector_allocation': sector_allocation,
            'industry_concentration': industry_concentration,
            'thematic_clusters': thematic_clusters if thematic_clusters else ['Diversified'],
            'total_stocks': total_stocks,
            'total_value': total_value
        }
    
    def calculate_style_analysis(self, portfolio_df, historical_data):
        if portfolio_df is None or portfolio_df.empty:
            return {
                'value_tilt': 50,
                'growth_tilt': 50,
                'momentum_exposure': 0,
                'quality_factor': 'N/A',
                'volatility_tilt': 'Neutral',
                'style_label': 'Blend'
            }
        
        value_score = 0
        growth_score = 0
        momentum_score = 0
        quality_score = 0
        volatility_tilt = 'Neutral'
        
        high_beta_count = 0
        low_vol_count = 0
        
        quality_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'HDFC', 'ICICIBANK', 'KOTAKBANK', 
                         'HINDUNILVR', 'ITC', 'BHARTIARTL', 'ASIANPAINT', 'BAJFINANCE', 'MARUTI',
                         'TITAN', 'NESTLEIND', 'BRITANNIA', 'PIDILITIND', 'DABUR']
        
        for _, row in portfolio_df.iterrows():
            stock_name = row['Stock Name']
            gain_pct = row.get('Percentage Gain/Loss', 0)
            
            if gain_pct > 20:
                momentum_score += 1
                growth_score += 1
            if gain_pct < -10:
                value_score += 1
            
            stock_upper = str(stock_name).upper().replace('.NS', '').replace('.BO', '')
            if any(q in stock_upper for q in quality_stocks):
                quality_score += 1
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                hist = historical_data[stock_name]
                if len(hist) > 20:
                    returns = hist['Close'].pct_change().dropna()
                    vol = float(returns.std() * np.sqrt(252) * 100)
                    if vol > 35:
                        high_beta_count += 1
                    elif vol < 20:
                        low_vol_count += 1
        
        total = len(portfolio_df)
        if total > 0:
            if high_beta_count / total > 0.5:
                volatility_tilt = 'High-Beta'
            elif low_vol_count / total > 0.5:
                volatility_tilt = 'Low-Volatility'
        
        value_pct = (value_score / total * 100) if total > 0 else 0
        growth_pct = 100 - value_pct
        
        quality_factor = 'High' if quality_score > total * 0.4 else ('Medium' if quality_score > total * 0.2 else 'Low')
        
        return {
            'value_tilt': round(value_pct, 1),
            'growth_tilt': round(growth_pct, 1),
            'momentum_exposure': round((momentum_score / total * 100) if total > 0 else 0, 1),
            'quality_factor': quality_factor,
            'volatility_tilt': volatility_tilt,
            'style_label': 'Value' if value_pct > 60 else ('Growth' if growth_pct > 60 else 'Blend')
        }
    
    def calculate_concentration_risk(self, portfolio_df):
        total_value = portfolio_df['Current Value'].sum()
        
        sorted_df = portfolio_df.sort_values('Current Value', ascending=False)
        
        top1_pct = (sorted_df.iloc[0]['Current Value'] / total_value * 100) if len(sorted_df) > 0 and total_value > 0 else 0
        top3_pct = (sorted_df.head(3)['Current Value'].sum() / total_value * 100) if len(sorted_df) >= 3 and total_value > 0 else 0
        top5_pct = (sorted_df.head(5)['Current Value'].sum() / total_value * 100) if len(sorted_df) >= 5 and total_value > 0 else 0
        
        single_stock_flags = []
        for _, row in sorted_df.iterrows():
            pct = (row['Current Value'] / total_value * 100) if total_value > 0 else 0
            if pct > self.risk_thresholds['single_stock_max']:
                single_stock_flags.append({
                    'stock': row['Stock Name'],
                    'percentage': round(pct, 1)
                })
        
        sector_flags = []
        if 'Sector' in portfolio_df.columns:
            sector_values = portfolio_df.groupby('Sector')['Current Value'].sum()
            for sector, value in sector_values.items():
                pct = (value / total_value * 100) if total_value > 0 else 0
                if pct > self.risk_thresholds['sector_max']:
                    sector_flags.append({
                        'sector': sector,
                        'percentage': round(pct, 1)
                    })
        
        concentration_score = 100
        if top1_pct > 20:
            concentration_score -= 20
        if top3_pct > 50:
            concentration_score -= 15
        if top5_pct > 70:
            concentration_score -= 15
        if len(single_stock_flags) > 0:
            concentration_score -= 10 * len(single_stock_flags)
        if len(sector_flags) > 0:
            concentration_score -= 10 * len(sector_flags)
        
        return {
            'top1_exposure': round(top1_pct, 1),
            'top3_exposure': round(top3_pct, 1),
            'top5_exposure': round(top5_pct, 1),
            'single_stock_flags': single_stock_flags,
            'sector_overexposure_flags': sector_flags,
            'concentration_score': max(0, concentration_score),
            'risk_level': 'High' if concentration_score < 50 else ('Medium' if concentration_score < 75 else 'Low')
        }
    
    def calculate_volatility_metrics(self, portfolio_df, historical_data, benchmark_data=None):
        portfolio_returns = []
        stock_volatilities = []
        stock_betas = []
        
        benchmark_returns = None
        if benchmark_data is not None and len(benchmark_data) > 20:
            benchmark_returns = benchmark_data['Close'].pct_change().dropna()
        
        for _, row in portfolio_df.iterrows():
            stock_name = row['Stock Name']
            weight = row['Current Value'] / portfolio_df['Current Value'].sum()
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                hist = historical_data[stock_name]
                if len(hist) > 20:
                    returns = hist['Close'].pct_change().dropna()
                    vol = float(returns.std() * np.sqrt(252) * 100)
                    stock_volatilities.append({'stock': stock_name, 'volatility': vol, 'weight': weight})
                    
                    if benchmark_returns is not None and len(returns) > 0:
                        aligned_returns = returns.reindex(benchmark_returns.index).dropna()
                        aligned_benchmark = benchmark_returns.reindex(aligned_returns.index).dropna()
                        if len(aligned_returns) > 10 and len(aligned_benchmark) > 10:
                            covariance = np.cov(aligned_returns, aligned_benchmark)[0][1]
                            benchmark_var = aligned_benchmark.var()
                            if benchmark_var > 0:
                                beta = covariance / benchmark_var
                                stock_betas.append({'stock': stock_name, 'beta': beta, 'weight': weight})
        
        avg_volatility = sum(s['volatility'] * s['weight'] for s in stock_volatilities) if stock_volatilities else 0
        
        portfolio_beta = sum(s['beta'] * s['weight'] for s in stock_betas) if stock_betas else 1.0
        
        max_drawdown = 0
        downside_deviation = 0
        sortino_ratio = 0
        
        if historical_data:
            portfolio_values = []
            for _, row in portfolio_df.iterrows():
                stock_name = row['Stock Name']
                if stock_name in historical_data and not historical_data[stock_name].empty:
                    hist = historical_data[stock_name].copy()
                    hist['portfolio_contribution'] = hist['Close'] * row['Quantity']
                    portfolio_values.append(hist['portfolio_contribution'])
            
            if portfolio_values:
                combined = pd.concat(portfolio_values, axis=1).sum(axis=1)
                if len(combined) > 0:
                    peak = combined.expanding().max()
                    drawdown = (combined - peak) / peak * 100
                    max_drawdown = float(abs(drawdown.min()))
                    
                    returns = combined.pct_change().dropna()
                    negative_returns = returns[returns < 0]
                    if len(negative_returns) > 0:
                        downside_deviation = float(negative_returns.std() * np.sqrt(252) * 100)
                        
                        avg_return = float(returns.mean() * 252)
                        risk_free_rate = 0.06
                        if downside_deviation > 0:
                            sortino_ratio = (avg_return - risk_free_rate) / (downside_deviation / 100)
        
        sharpe_ratio = 0
        risk_free_rate = 0.06
        if historical_data:
            portfolio_values = []
            for _, row in portfolio_df.iterrows():
                stock_name = row['Stock Name']
                if stock_name in historical_data and not historical_data[stock_name].empty:
                    hist = historical_data[stock_name].copy()
                    hist['contribution'] = hist['Close'] * row['Quantity']
                    portfolio_values.append(hist['contribution'])
            
            if portfolio_values:
                combined_vals = pd.concat(portfolio_values, axis=1).sum(axis=1)
                if len(combined_vals) > 1:
                    port_returns = combined_vals.pct_change().dropna()
                    if len(port_returns) > 0:
                        annual_return = float(port_returns.mean() * 252)
                        annual_std = float(port_returns.std() * np.sqrt(252))
                        if annual_std > 0:
                            sharpe_ratio = (annual_return - risk_free_rate) / annual_std
        
        return {
            'historical_volatility': round(avg_volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'downside_deviation': round(downside_deviation, 2),
            'portfolio_beta': round(portfolio_beta, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'stock_volatilities': sorted(stock_volatilities, key=lambda x: x['volatility'], reverse=True)[:5],
            'risk_classification': 'High Risk' if avg_volatility > 30 else ('Moderate Risk' if avg_volatility > 20 else 'Low Risk')
        }
    
    def calculate_behavior_score(self, portfolio_df):
        holding_periods = []
        today = datetime.now()
        
        for _, row in portfolio_df.iterrows():
            buy_date = row.get('Buy Date')
            if pd.notna(buy_date):
                if isinstance(buy_date, str):
                    try:
                        buy_date = pd.to_datetime(buy_date)
                    except:
                        continue
                days_held = (today - buy_date).days
                holding_periods.append({
                    'stock': row['Stock Name'],
                    'days_held': days_held
                })
        
        avg_holding_period = np.mean([h['days_held'] for h in holding_periods]) if holding_periods else 0
        
        short_term_count = sum(1 for h in holding_periods if h['days_held'] < 90)
        long_term_count = sum(1 for h in holding_periods if h['days_held'] > 365)
        
        total = len(holding_periods)
        overtrading_flag = (short_term_count / total > 0.5) if total > 0 else False
        
        behavior_score = 100
        if avg_holding_period < 180:
            behavior_score -= 20
        if overtrading_flag:
            behavior_score -= 25
        if short_term_count / total > 0.3 if total > 0 else False:
            behavior_score -= 15
        
        if avg_holding_period > 365:
            behavior_label = 'Patient Investor'
        elif avg_holding_period > 180:
            behavior_label = 'Medium-Term Holder'
        elif avg_holding_period > 90:
            behavior_label = 'Active Trader'
        else:
            behavior_label = 'High Churn Pattern'
        
        return {
            'average_holding_days': round(avg_holding_period, 0),
            'short_term_holdings': short_term_count,
            'long_term_holdings': long_term_count,
            'overtrading_detected': overtrading_flag,
            'behavior_score': max(0, behavior_score),
            'behavior_pattern': behavior_label,
            'holding_distribution': {
                '<3 months': short_term_count,
                '3-12 months': total - short_term_count - long_term_count,
                '>12 months': long_term_count
            }
        }
    
    def calculate_drift_analysis(self, portfolio_df, benchmark_data=None):
        nifty50_sectors = {
            'Financial Services': 37,
            'IT': 13,
            'Oil & Gas': 12,
            'Consumer Goods': 10,
            'Automobile': 8,
            'Pharma': 5,
            'Metals': 5,
            'Telecom': 4,
            'Others': 6
        }
        
        sector_allocation = {}
        total_value = portfolio_df['Current Value'].sum()
        if 'Sector' in portfolio_df.columns:
            for sector in portfolio_df['Sector'].unique():
                sector_value = portfolio_df[portfolio_df['Sector'] == sector]['Current Value'].sum()
                sector_allocation[sector] = (sector_value / total_value * 100) if total_value > 0 else 0
        
        sector_drifts = []
        for sector, benchmark_pct in nifty50_sectors.items():
            portfolio_pct = 0
            for p_sector, p_pct in sector_allocation.items():
                if sector.lower() in p_sector.lower() or p_sector.lower() in sector.lower():
                    portfolio_pct = p_pct
                    break
            
            drift = portfolio_pct - benchmark_pct
            if abs(drift) > 5:
                sector_drifts.append({
                    'sector': sector,
                    'portfolio_pct': round(portfolio_pct, 1),
                    'benchmark_pct': benchmark_pct,
                    'drift': round(drift, 1)
                })
        
        total_drift = sum(abs(d['drift']) for d in sector_drifts)
        alignment_score = max(0, 100 - total_drift)
        
        return {
            'sector_drifts': sorted(sector_drifts, key=lambda x: abs(x['drift']), reverse=True),
            'alignment_score': round(alignment_score, 1),
            'benchmark_used': 'Nifty 50',
            'deviation_level': 'High' if alignment_score < 50 else ('Moderate' if alignment_score < 75 else 'Low'),
            'portfolio_sector_allocation': sector_allocation
        }
    
    def calculate_overlap_detection(self, portfolio_df):
        overlaps = []
        
        business_groups = {
            'Tata Group': ['TCS', 'TATASTEEL', 'TATAPOWER', 'TATAMOTORS', 'TITAN', 'TATACONSUM', 'TATACOMM'],
            'Reliance Group': ['RELIANCE', 'RELIANCEINFRA'],
            'Adani Group': ['ADANIENT', 'ADANIPORTS', 'ADANIGREEN', 'ADANITRANS', 'ADANIPOWER'],
            'HDFC Group': ['HDFCBANK', 'HDFC', 'HDFCLIFE', 'HDFCAMC'],
            'ICICI Group': ['ICICIBANK', 'ICICIGI', 'ICICIPRULI'],
            'Bajaj Group': ['BAJFINANCE', 'BAJAJFINSV', 'BAJAJ-AUTO'],
            'Aditya Birla': ['HINDALCO', 'ULTRACEMCO', 'GRASIM', 'ABFRL'],
            'L&T Group': ['LT', 'LTIM', 'LTTS', 'LTF']
        }
        
        for group_name, stocks in business_groups.items():
            group_stocks = []
            for _, row in portfolio_df.iterrows():
                stock_name = str(row['Stock Name']).upper().replace('.NS', '').replace('.BO', '')
                if any(s in stock_name for s in stocks):
                    group_stocks.append({
                        'stock': row['Stock Name'],
                        'value': row['Current Value']
                    })
            
            if len(group_stocks) > 1:
                total_exposure = sum(s['value'] for s in group_stocks)
                overlaps.append({
                    'group': group_name,
                    'stocks': group_stocks,
                    'count': len(group_stocks),
                    'total_exposure': total_exposure
                })
        
        if 'Sector' in portfolio_df.columns:
            sector_counts = portfolio_df['Sector'].value_counts()
            for sector, count in sector_counts.items():
                if count >= 4:
                    sector_stocks = portfolio_df[portfolio_df['Sector'] == sector]['Stock Name'].tolist()
                    overlaps.append({
                        'group': f'{sector} Concentration',
                        'stocks': [{'stock': s, 'value': 0} for s in sector_stocks],
                        'count': count,
                        'type': 'sector'
                    })
        
        return {
            'overlaps': overlaps,
            'total_overlap_groups': len(overlaps),
            'has_significant_overlaps': len(overlaps) > 0,
            'overlap_risk': 'High' if len(overlaps) > 3 else ('Moderate' if len(overlaps) > 1 else 'Low')
        }
    
    def calculate_return_attribution(self, portfolio_df):
        total_gain = portfolio_df['Absolute Gain/Loss'].sum()
        
        stock_contributions = []
        for _, row in portfolio_df.iterrows():
            contribution = row['Absolute Gain/Loss']
            contribution_pct = (contribution / abs(total_gain) * 100) if total_gain != 0 else 0
            stock_contributions.append({
                'stock': row['Stock Name'],
                'absolute_contribution': contribution,
                'contribution_pct': contribution_pct
            })
        
        stock_contributions = sorted(stock_contributions, key=lambda x: x['absolute_contribution'], reverse=True)
        
        top_gainers = [s for s in stock_contributions if s['absolute_contribution'] > 0][:5]
        top_losers = [s for s in stock_contributions if s['absolute_contribution'] < 0]
        top_losers = sorted(top_losers, key=lambda x: x['absolute_contribution'])[:5]
        
        sector_attribution = {}
        if 'Sector' in portfolio_df.columns:
            for sector in portfolio_df['Sector'].unique():
                sector_gain = portfolio_df[portfolio_df['Sector'] == sector]['Absolute Gain/Loss'].sum()
                sector_attribution[sector] = {
                    'absolute': sector_gain,
                    'contribution_pct': (sector_gain / abs(total_gain) * 100) if total_gain != 0 else 0
                }
        
        return {
            'total_portfolio_gain': total_gain,
            'top_contributors': top_gainers,
            'bottom_contributors': top_losers,
            'sector_attribution': sector_attribution,
            'gainers_count': len([s for s in stock_contributions if s['absolute_contribution'] > 0]),
            'losers_count': len([s for s in stock_contributions if s['absolute_contribution'] < 0])
        }
    
    def calculate_liquidity_risk(self, portfolio_df, historical_data):
        liquidity_scores = []
        
        for _, row in portfolio_df.iterrows():
            stock_name = row['Stock Name']
            position_value = row['Current Value']
            
            avg_volume = 0
            avg_traded_value = 0
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                hist = historical_data[stock_name]
                if 'Volume' in hist.columns:
                    avg_volume = float(hist['Volume'].tail(20).mean())
                    avg_price = float(hist['Close'].tail(20).mean())
                    avg_traded_value = avg_volume * avg_price
            
            days_to_liquidate = 0.0
            if avg_traded_value > 0:
                days_to_liquidate = float(position_value / (avg_traded_value * 0.1))
            
            liquidity_scores.append({
                'stock': stock_name,
                'position_value': position_value,
                'avg_daily_volume': avg_volume,
                'avg_traded_value': avg_traded_value,
                'days_to_liquidate': round(days_to_liquidate, 1),
                'liquidity_grade': 'High' if days_to_liquidate < 1 else ('Medium' if days_to_liquidate < 5 else 'Low')
            })
        
        illiquid_positions = [s for s in liquidity_scores if s['liquidity_grade'] == 'Low']
        
        portfolio_liquidity_score = 100
        if len(illiquid_positions) > 0:
            portfolio_liquidity_score -= 10 * len(illiquid_positions)
        
        return {
            'stock_liquidity': liquidity_scores,
            'illiquid_positions': illiquid_positions,
            'illiquid_count': len(illiquid_positions),
            'portfolio_liquidity_score': max(0, portfolio_liquidity_score),
            'liquidity_risk': 'High' if portfolio_liquidity_score < 50 else ('Moderate' if portfolio_liquidity_score < 75 else 'Low')
        }
    
    def calculate_tail_risk(self, portfolio_df, historical_data):
        high_vol_stocks = []
        
        asm_gsm_keywords = ['ASM', 'GSM', 'SURVEILLANCE']
        
        for _, row in portfolio_df.iterrows():
            stock_name = row['Stock Name']
            
            if stock_name in historical_data and not historical_data[stock_name].empty:
                hist = historical_data[stock_name]
                if len(hist) > 20:
                    returns = hist['Close'].pct_change().dropna()
                    vol = float(returns.std() * np.sqrt(252) * 100)
                    
                    if vol > 40:
                        high_vol_stocks.append({
                            'stock': stock_name,
                            'volatility': round(vol, 1),
                            'value': row['Current Value']
                        })
        
        total_value = portfolio_df['Current Value'].sum()
        high_vol_exposure = sum(s['value'] for s in high_vol_stocks)
        high_vol_pct = (high_vol_exposure / total_value * 100) if total_value > 0 else 0
        
        small_cap_exposure = 0
        if 'Category' in portfolio_df.columns:
            small_caps = portfolio_df[portfolio_df['Category'].str.contains('Small', case=False, na=False)]
            small_cap_exposure = (small_caps['Current Value'].sum() / total_value * 100) if total_value > 0 else 0
        
        tail_risk_score = 100
        if high_vol_pct > 30:
            tail_risk_score -= 25
        if small_cap_exposure > 40:
            tail_risk_score -= 20
        if len(high_vol_stocks) > 5:
            tail_risk_score -= 15
        
        return {
            'high_volatility_stocks': high_vol_stocks,
            'high_vol_exposure_pct': round(high_vol_pct, 1),
            'small_cap_exposure_pct': round(small_cap_exposure, 1),
            'tail_risk_score': max(0, tail_risk_score),
            'tail_risk_level': 'High' if tail_risk_score < 50 else ('Moderate' if tail_risk_score < 75 else 'Low')
        }
    
    def calculate_macro_sensitivity(self, portfolio_df):
        banking_stocks = ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'BANKBARODA', 'PNB', 'CANBK', 'UNIONBANK']
        nbfc_stocks = ['BAJFINANCE', 'BAJAJFINSV', 'LICHSGFIN', 'MUTHOOTFIN', 'CHOLAFIN']
        
        commodity_stocks = {
            'crude': ['ONGC', 'BPCL', 'IOC', 'HINDPETRO', 'GAIL', 'PETRONET'],
            'metals': ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'NMDC', 'COALINDIA'],
            'gold': ['TITAN']
        }
        
        export_stocks = ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'SUNPHARMA', 'DRREDDY', 'CIPLA']
        
        total_value = portfolio_df['Current Value'].sum()
        
        banking_exposure = 0
        nbfc_exposure = 0
        crude_exposure = 0
        metals_exposure = 0
        export_exposure = 0
        
        for _, row in portfolio_df.iterrows():
            stock = str(row['Stock Name']).upper().replace('.NS', '').replace('.BO', '')
            value = row['Current Value']
            
            if any(b in stock for b in banking_stocks):
                banking_exposure += value
            if any(n in stock for n in nbfc_stocks):
                nbfc_exposure += value
            if any(c in stock for c in commodity_stocks['crude']):
                crude_exposure += value
            if any(m in stock for m in commodity_stocks['metals']):
                metals_exposure += value
            if any(e in stock for e in export_stocks):
                export_exposure += value
        
        return {
            'interest_rate_sensitivity': {
                'banking_exposure_pct': round((banking_exposure / total_value * 100) if total_value > 0 else 0, 1),
                'nbfc_exposure_pct': round((nbfc_exposure / total_value * 100) if total_value > 0 else 0, 1),
                'total_rate_sensitive_pct': round(((banking_exposure + nbfc_exposure) / total_value * 100) if total_value > 0 else 0, 1),
                'sensitivity_flag': (banking_exposure + nbfc_exposure) / total_value > 0.3 if total_value > 0 else False
            },
            'commodity_exposure': {
                'crude_sensitive_pct': round((crude_exposure / total_value * 100) if total_value > 0 else 0, 1),
                'metals_exposure_pct': round((metals_exposure / total_value * 100) if total_value > 0 else 0, 1)
            },
            'currency_exposure': {
                'export_oriented_pct': round((export_exposure / total_value * 100) if total_value > 0 else 0, 1),
                'inr_sensitivity': 'High' if export_exposure / total_value > 0.25 else 'Low' if total_value > 0 else 'Low'
            }
        }
    
    def calculate_health_score(self, all_metrics):
        weights = {
            'diversification': 25,
            'risk': 25,
            'liquidity': 20,
            'behavior': 15,
            'style_balance': 15
        }
        
        diversification_score = all_metrics.get('concentration', {}).get('concentration_score', 50)
        
        vol_metrics = all_metrics.get('volatility', {})
        historical_vol = vol_metrics.get('historical_volatility', 25)
        risk_score = max(0, 100 - historical_vol * 2)
        
        liquidity_score = all_metrics.get('liquidity', {}).get('portfolio_liquidity_score', 50)
        
        behavior_score = all_metrics.get('behavior', {}).get('behavior_score', 50)
        
        style = all_metrics.get('style', {})
        value_tilt = style.get('value_tilt', 50)
        style_balance_score = 100 - abs(50 - value_tilt) * 2
        
        weighted_score = (
            diversification_score * weights['diversification'] / 100 +
            risk_score * weights['risk'] / 100 +
            liquidity_score * weights['liquidity'] / 100 +
            behavior_score * weights['behavior'] / 100 +
            style_balance_score * weights['style_balance'] / 100
        )
        
        return {
            'overall_score': round(weighted_score, 0),
            'component_scores': {
                'diversification': round(diversification_score, 0),
                'risk': round(risk_score, 0),
                'liquidity': round(liquidity_score, 0),
                'behavior': round(behavior_score, 0),
                'style_balance': round(style_balance_score, 0)
            },
            'grade': 'A' if weighted_score >= 80 else ('B' if weighted_score >= 65 else ('C' if weighted_score >= 50 else 'D')),
            'summary': self._generate_health_summary(weighted_score, all_metrics)
        }
    
    def _generate_health_summary(self, score, metrics):
        summary_parts = []
        
        style = metrics.get('style', {})
        summary_parts.append(f"a {style.get('style_label', 'balanced').lower()} investment style")
        
        concentration = metrics.get('concentration', {})
        if concentration.get('risk_level') == 'High':
            summary_parts.append("elevated concentration risk")
        elif concentration.get('risk_level') == 'Medium':
            summary_parts.append("moderate concentration")
        else:
            summary_parts.append("good diversification")
        
        volatility = metrics.get('volatility', {})
        if volatility.get('historical_volatility', 0) > 30:
            summary_parts.append("higher than average volatility")
        
        behavior = metrics.get('behavior', {})
        summary_parts.append(f"{behavior.get('behavior_pattern', 'unknown')} behavior pattern")
        
        return f"Your portfolio shows {', '.join(summary_parts)}."
    
    def calculate_scenario_analysis(self, portfolio_df, historical_data, benchmark_data=None):
        scenarios = []
        
        current_value = portfolio_df['Current Value'].sum()
        
        stock_betas = {}
        if benchmark_data is not None and len(benchmark_data) > 20:
            benchmark_returns = benchmark_data['Close'].pct_change().dropna()
            
            for _, row in portfolio_df.iterrows():
                stock_name = row['Stock Name']
                if stock_name in historical_data and not historical_data[stock_name].empty:
                    hist = historical_data[stock_name]
                    if len(hist) > 20:
                        returns = hist['Close'].pct_change().dropna()
                        aligned = returns.reindex(benchmark_returns.index).dropna()
                        aligned_bench = benchmark_returns.reindex(aligned.index).dropna()
                        if len(aligned) > 10:
                            cov = np.cov(aligned, aligned_bench)[0][1]
                            var = aligned_bench.var()
                            if var > 0:
                                stock_betas[stock_name] = cov / var
        
        for scenario_name, market_drop in [('Nifty -10%', -10), ('Midcap -20%', -20), ('Banking -15%', -15)]:
            projected_loss = 0
            
            for _, row in portfolio_df.iterrows():
                stock_name = row['Stock Name']
                value = row['Current Value']
                beta = stock_betas.get(stock_name, 1.0)
                
                if 'Banking' in scenario_name:
                    if 'Sector' in portfolio_df.columns and 'Banking' in str(row.get('Sector', '')):
                        projected_loss += value * (market_drop / 100)
                    else:
                        projected_loss += value * (market_drop / 100) * 0.3
                else:
                    projected_loss += value * (market_drop / 100) * beta
            
            scenarios.append({
                'scenario': scenario_name,
                'market_move': market_drop,
                'projected_portfolio_impact_pct': round((projected_loss / current_value * 100) if current_value > 0 else 0, 1),
                'projected_loss_amount': round(projected_loss, 0)
            })
        
        return {
            'scenarios': scenarios,
            'current_portfolio_value': current_value,
            'stress_test_note': 'These projections are based on historical correlations and may not reflect actual outcomes.'
        }
    
    def calculate_tax_impact(self, portfolio_df):
        """Calculate tax impact of unrealized gains/losses"""
        if portfolio_df is None or portfolio_df.empty:
            return {
                'total_unrealized_gain': 0,
                'total_unrealized_loss': 0,
                'short_term_gains': 0,
                'long_term_gains': 0,
                'short_term_losses': 0,
                'long_term_losses': 0,
                'estimated_stcg_tax': 0,
                'estimated_ltcg_tax': 0,
                'stock_breakdown': []
            }
        
        today = datetime.now()
        short_term_gains = 0
        long_term_gains = 0
        short_term_losses = 0
        long_term_losses = 0
        stock_breakdown = []
        
        for _, row in portfolio_df.iterrows():
            stock_name = row.get('Stock Name', 'Unknown')
            buy_date = row.get('Buy Date')
            gain_loss = row.get('Absolute Gain/Loss', 0)
            
            is_long_term = False
            holding_days = 0
            
            if pd.notna(buy_date):
                try:
                    if isinstance(buy_date, str):
                        buy_date = pd.to_datetime(buy_date)
                    holding_days = (today - buy_date).days
                    is_long_term = holding_days >= 365
                except:
                    pass
            
            if gain_loss >= 0:
                if is_long_term:
                    long_term_gains += gain_loss
                else:
                    short_term_gains += gain_loss
            else:
                if is_long_term:
                    long_term_losses += abs(gain_loss)
                else:
                    short_term_losses += abs(gain_loss)
            
            stock_breakdown.append({
                'stock': stock_name,
                'gain_loss': round(gain_loss, 2),
                'holding_days': holding_days,
                'term': 'Long-term' if is_long_term else 'Short-term',
                'tax_implication': 'LTCG' if is_long_term and gain_loss > 0 else ('STCG' if gain_loss > 0 else 'Loss')
            })
        
        stcg_tax_rate = 0.15
        ltcg_tax_rate = 0.10
        ltcg_exemption = 100000
        
        estimated_stcg_tax = short_term_gains * stcg_tax_rate
        taxable_ltcg = max(0, long_term_gains - ltcg_exemption)
        estimated_ltcg_tax = taxable_ltcg * ltcg_tax_rate
        
        return {
            'total_unrealized_gain': round(short_term_gains + long_term_gains, 2),
            'total_unrealized_loss': round(short_term_losses + long_term_losses, 2),
            'short_term_gains': round(short_term_gains, 2),
            'long_term_gains': round(long_term_gains, 2),
            'short_term_losses': round(short_term_losses, 2),
            'long_term_losses': round(long_term_losses, 2),
            'estimated_stcg_tax': round(estimated_stcg_tax, 2),
            'estimated_ltcg_tax': round(estimated_ltcg_tax, 2),
            'total_estimated_tax': round(estimated_stcg_tax + estimated_ltcg_tax, 2),
            'ltcg_exemption_remaining': round(max(0, ltcg_exemption - long_term_gains), 2),
            'stock_breakdown': stock_breakdown,
            'tax_note': 'Tax calculations are estimates based on current Indian tax laws. STCG: 15%, LTCG: 10% above ₹1L exemption.'
        }
