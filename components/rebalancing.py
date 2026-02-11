import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
from utils.page_explanations import render_section_explainer

class PortfolioRebalancing:
    def __init__(self):
        self._strategies = None
        self._sector_targets = None
    
    @property
    def strategies(self):
        if self._strategies is None:
            self._load_data()
        return self._strategies
    
    @property
    def sector_targets(self):
        if self._sector_targets is None:
            self._load_data()
        return self._sector_targets
    
    def _load_data(self):
        if os.environ.get('DATABASE_URL'):
            try:
                from utils.database import Database
                db = Database()
                self._strategies = db.get_rebalancing_strategies()
                self._sector_targets = db.get_sectors()
                
                if self._strategies and self._sector_targets:
                    return
            except Exception as e:
                print(f"Database load failed for rebalancing: {e}")
        
        self._strategies = {
            'Conservative': {
                'Large Cap': 70,
                'Mid Cap': 20,
                'Small Cap': 10
            },
            'Balanced': {
                'Large Cap': 50,
                'Mid Cap': 30,
                'Small Cap': 20
            },
            'Aggressive': {
                'Large Cap': 30,
                'Mid Cap': 40,
                'Small Cap': 30
            }
        }
        
        self._sector_targets = {
            'Banking': 15,
            'Technology': 15,
            'Energy': 10,
            'FMCG': 10,
            'Pharmaceuticals': 10,
            'Automobile': 10,
            'Others': 30
        }
    
    def render(self, analysis_results, portfolio_data, current_data, lang_code="en"):
        """Render portfolio rebalancing recommendations"""
        
        st.header("⚖️ Portfolio Rebalancing Suggestions")
        
        render_section_explainer("Select Your Investment Strategy", "rebalancing_strategy", lang_code=lang_code, analysis_results=analysis_results, icon="📊")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            strategy = st.selectbox(
                "Choose Strategy:",
                options=list(self.strategies.keys()),
                help="Select investment strategy based on your risk tolerance"
            )
        
        with col2:
            st.info(f"""
            **{strategy} Strategy:**
            - Large Cap: {self.strategies[strategy]['Large Cap']}%
            - Mid Cap: {self.strategies[strategy]['Mid Cap']}%
            - Small Cap: {self.strategies[strategy]['Small Cap']}%
            """)
        
        st.markdown("---")
        
        # Current vs Target Allocation
        render_section_explainer("Current vs Target Allocation", "concentration_alerts", lang_code=lang_code, analysis_results=analysis_results, icon="📈")
        
        current_allocation = self.calculate_current_allocation(analysis_results)
        target_allocation = self.strategies[strategy]
        
        # Create comparison chart
        fig = go.Figure()
        
        categories = list(target_allocation.keys())
        current_values = [current_allocation.get(cat, 0) for cat in categories]
        target_values = [target_allocation[cat] for cat in categories]
        
        fig.add_trace(go.Bar(
            name='Current Allocation',
            x=categories,
            y=current_values,
            marker_color='lightblue',
            text=[f"{v:.1f}%" for v in current_values],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Target Allocation',
            x=categories,
            y=target_values,
            marker_color='darkblue',
            text=[f"{v:.1f}%" for v in target_values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Portfolio Allocation: Current vs Target',
            xaxis_title='Stock Category',
            yaxis_title='Allocation (%)',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Rebalancing Actions
        render_section_explainer("Recommended Rebalancing Actions", "overweight_positions", lang_code=lang_code, analysis_results=analysis_results, icon="💡")
        
        portfolio_value = analysis_results['portfolio_summary']['current_value']
        rebalancing_actions = self.generate_rebalancing_actions(
            current_allocation, target_allocation, portfolio_value, analysis_results, current_data
        )
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_buy = sum(action['amount'] for action in rebalancing_actions if action['action'] == 'BUY')
        total_sell = sum(abs(action['amount']) for action in rebalancing_actions if action['action'] == 'SELL')
        
        with col1:
            st.metric(
                label="Total to Invest",
                value=f"₹{total_buy:,.2f}",
                help="Amount to invest in underweight categories"
            )
        
        with col2:
            st.metric(
                label="Total to Divest",
                value=f"₹{total_sell:,.2f}",
                help="Amount to reduce from overweight categories"
            )
        
        with col3:
            rebalancing_magnitude = (total_buy + total_sell) / portfolio_value * 100
            st.metric(
                label="Rebalancing Magnitude",
                value=f"{rebalancing_magnitude:.1f}%",
                help="Percentage of portfolio affected"
            )
        
        # Detailed actions
        st.subheader("📋 Detailed Action Plan")
        
        # Group by action type
        buy_actions = [a for a in rebalancing_actions if a['action'] == 'BUY']
        sell_actions = [a for a in rebalancing_actions if a['action'] == 'SELL']
        hold_actions = [a for a in rebalancing_actions if a['action'] == 'HOLD']
        
        if buy_actions:
            st.success("🟢 **Stocks to Buy / Increase Position**")
            for action in buy_actions:
                with st.expander(f"📈 {action['stock']} - Invest ₹{action['amount']:,.2f}"):
                    st.write(f"**Category:** {action['category']}")
                    st.write(f"**Current Allocation:** {action['current_allocation']:.1f}%")
                    st.write(f"**Target Allocation:** {action['target_allocation']:.1f}%")
                    st.write(f"**Gap:** {action['gap']:+.1f}%")
                    st.write(f"**Current Price:** ₹{action['current_price']:.2f}")
                    st.write(f"**Suggested Shares to Buy:** {int(action['shares'])}")
                    st.write(f"**Rationale:** {action['rationale']}")
        
        if sell_actions:
            st.error("🔴 **Stocks to Sell / Reduce Position**")
            for action in sell_actions:
                with st.expander(f"📉 {action['stock']} - Reduce ₹{abs(action['amount']):,.2f}"):
                    st.write(f"**Category:** {action['category']}")
                    st.write(f"**Current Allocation:** {action['current_allocation']:.1f}%")
                    st.write(f"**Target Allocation:** {action['target_allocation']:.1f}%")
                    st.write(f"**Gap:** {action['gap']:+.1f}%")
                    st.write(f"**Current Price:** ₹{action['current_price']:.2f}")
                    st.write(f"**Suggested Shares to Sell:** {int(abs(action['shares']))}")
                    st.write(f"**Rationale:** {action['rationale']}")
        
        if hold_actions:
            st.info("🟡 **Stocks to Hold (Well-Allocated)**")
            for action in hold_actions:
                st.write(f"• **{action['stock']}** ({action['category']}): Current {action['current_allocation']:.1f}% vs Target {action['target_allocation']:.1f}%")
        
        st.markdown("---")
        
        # Sector Rebalancing
        render_section_explainer("Sector Rebalancing Recommendations", "underweight_positions", lang_code=lang_code, analysis_results=analysis_results, icon="🏭")
        
        current_sector_allocation = self.calculate_sector_allocation(analysis_results)
        sector_actions = self.generate_sector_recommendations(current_sector_allocation)
        
        # Sector allocation chart
        fig_sector = go.Figure()
        
        sectors = list(current_sector_allocation.keys())
        current_sector_values = list(current_sector_allocation.values())
        target_sector_values = [self.sector_targets.get(s, 0) for s in sectors]
        
        fig_sector.add_trace(go.Bar(
            name='Current',
            x=sectors,
            y=current_sector_values,
            marker_color='lightgreen',
            text=[f"{v:.1f}%" for v in current_sector_values],
            textposition='auto'
        ))
        
        fig_sector.add_trace(go.Bar(
            name='Ideal',
            x=sectors,
            y=target_sector_values,
            marker_color='darkgreen',
            text=[f"{v:.1f}%" for v in target_sector_values],
            textposition='auto'
        ))
        
        fig_sector.update_layout(
            title='Sector Allocation: Current vs Ideal',
            xaxis_title='Sector',
            yaxis_title='Allocation (%)',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig_sector, use_container_width=True)
        
        # Sector recommendations
        for recommendation in sector_actions:
            if recommendation['action'] == 'REDUCE':
                st.warning(f"⚠️ **{recommendation['sector']}**: Over-allocated at {recommendation['current']:.1f}% (Target: {recommendation['target']:.1f}%). Consider reducing exposure.")
            elif recommendation['action'] == 'INCREASE':
                st.info(f"📈 **{recommendation['sector']}**: Under-allocated at {recommendation['current']:.1f}% (Target: {recommendation['target']:.1f}%). Consider increasing exposure.")
            else:
                st.success(f"✅ **{recommendation['sector']}**: Well-balanced at {recommendation['current']:.1f}%")
        
        st.markdown("---")
        
        # Implementation Tips
        st.subheader("💭 Implementation Tips")
        
        st.markdown("""
        **Best Practices for Rebalancing:**
        
        1. **Gradual Approach**: Don't rebalance all at once. Spread trades over time to reduce market impact.
        
        2. **Tax Considerations**: Be mindful of capital gains tax. Consider holding period before selling profitable positions.
        
        3. **Transaction Costs**: Factor in brokerage and other costs. Small adjustments may not be worth the fees.
        
        4. **Market Conditions**: Consider current market conditions. Avoid panic selling or FOMO buying.
        
        5. **Regular Review**: Rebalance quarterly or semi-annually, not daily. Avoid over-trading.
        
        6. **Dollar-Cost Averaging**: For buy recommendations, consider spreading purchases over multiple transactions.
        
        7. **Use New Funds First**: When adding new money, direct it toward underweight categories.
        """)
    
    def calculate_current_allocation(self, analysis_results):
        """Calculate current portfolio allocation by category"""
        category_analysis = pd.DataFrame(analysis_results['category_analysis'])
        
        if category_analysis.empty:
            return {}
        
        allocation = {}
        for _, row in category_analysis.iterrows():
            allocation[row['Category']] = row['Percentage of Portfolio']
        
        return allocation
    
    def calculate_sector_allocation(self, analysis_results):
        """Calculate current sector allocation"""
        sector_analysis = pd.DataFrame(analysis_results['sector_analysis'])
        
        if sector_analysis.empty:
            return {}
        
        allocation = {}
        for _, row in sector_analysis.iterrows():
            allocation[row['Sector']] = row['Percentage of Portfolio']
        
        return allocation
    
    def generate_rebalancing_actions(self, current_allocation, target_allocation, portfolio_value, analysis_results, current_data):
        """Generate specific rebalancing actions for stocks"""
        actions = []
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
        for category, target_pct in target_allocation.items():
            current_pct = current_allocation.get(category, 0)
            gap = target_pct - current_pct
            
            # Filter stocks in this category
            category_stocks = stock_performance[stock_performance['Category'] == category]
            
            if abs(gap) < 2:  # Threshold for rebalancing
                # HOLD - within tolerance
                for _, stock in category_stocks.iterrows():
                    actions.append({
                        'stock': stock['Stock Name'],
                        'category': category,
                        'action': 'HOLD',
                        'current_allocation': current_pct,
                        'target_allocation': target_pct,
                        'gap': gap,
                        'amount': 0,
                        'shares': 0,
                        'current_price': stock['Current Price'],
                        'rationale': 'Well-balanced allocation, no action needed'
                    })
            elif gap > 0:
                # BUY - category is underweight
                amount_to_invest = (gap / 100) * portfolio_value
                
                # Distribute across stocks in category (or suggest best performers)
                if not category_stocks.empty:
                    # Prefer stocks with positive returns
                    best_stock = category_stocks.nlargest(1, 'Percentage Gain/Loss').iloc[0]
                    current_price = best_stock['Current Price']
                    shares = amount_to_invest / current_price
                    
                    actions.append({
                        'stock': best_stock['Stock Name'],
                        'category': category,
                        'action': 'BUY',
                        'current_allocation': current_pct,
                        'target_allocation': target_pct,
                        'gap': gap,
                        'amount': amount_to_invest,
                        'shares': shares,
                        'current_price': current_price,
                        'rationale': f'Category is underweight by {gap:.1f}%. This stock is a top performer in the category.'
                    })
            else:
                # SELL - category is overweight
                amount_to_divest = (abs(gap) / 100) * portfolio_value
                
                # Suggest selling worst performers or overweight stocks
                if not category_stocks.empty:
                    worst_stock = category_stocks.nsmallest(1, 'Percentage Gain/Loss').iloc[0]
                    current_price = worst_stock['Current Price']
                    shares = -(amount_to_divest / current_price)
                    
                    actions.append({
                        'stock': worst_stock['Stock Name'],
                        'category': category,
                        'action': 'SELL',
                        'current_allocation': current_pct,
                        'target_allocation': target_pct,
                        'gap': gap,
                        'amount': -amount_to_divest,
                        'shares': shares,
                        'current_price': current_price,
                        'rationale': f'Category is overweight by {abs(gap):.1f}%. Consider reducing underperforming positions.'
                    })
        
        return actions
    
    def generate_sector_recommendations(self, current_sector_allocation):
        """Generate sector rebalancing recommendations"""
        recommendations = []
        
        for sector, current_pct in current_sector_allocation.items():
            target_pct = self.sector_targets.get(sector, 0)
            gap = current_pct - target_pct
            
            if gap > 10:
                recommendations.append({
                    'sector': sector,
                    'current': current_pct,
                    'target': target_pct,
                    'gap': gap,
                    'action': 'REDUCE'
                })
            elif gap < -10:
                recommendations.append({
                    'sector': sector,
                    'current': current_pct,
                    'target': target_pct,
                    'gap': gap,
                    'action': 'INCREASE'
                })
            else:
                recommendations.append({
                    'sector': sector,
                    'current': current_pct,
                    'target': target_pct,
                    'gap': gap,
                    'action': 'HOLD'
                })
        
        return recommendations
