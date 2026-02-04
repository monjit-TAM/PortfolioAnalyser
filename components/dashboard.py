import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class Dashboard:
    def render(self, analysis_results, portfolio_data, current_data):
        """Render the main dashboard"""
        
        summary = analysis_results['portfolio_summary']
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        dividend_metrics = analysis_results.get('dividend_metrics', {})
        
        self.render_executive_summary(summary, portfolio_data)
        self.render_dividend_and_tax_metrics(dividend_metrics, summary)
        self.render_concentration_alerts(portfolio_data, summary)
        self.render_contribution_waterfall(stock_performance)
        self.render_performance_charts(summary, stock_performance, analysis_results)
    
    def render_executive_summary(self, summary, portfolio_data):
        """Render Executive Summary with health score gauge"""
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border-radius: 12px; padding: 25px; margin-bottom: 20px; 
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);'>
            <h2 style='color: #fff; margin: 0 0 20px 0; font-size: 24px;'>📊 Executive Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col_health, col_metrics = st.columns([1, 2])
        
        with col_health:
            health_score = self.calculate_health_score(summary, portfolio_data)
            health_color = '#2ecc71' if health_score >= 75 else '#f39c12' if health_score >= 50 else '#e74c3c'
            grade = 'A' if health_score >= 85 else 'B' if health_score >= 70 else 'C' if health_score >= 55 else 'D'
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Portfolio Health Score", 'font': {'size': 16}},
                number={'suffix': f" ({grade})", 'font': {'size': 28}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': health_color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'steps': [
                        {'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 75], 'color': '#fff3e0'},
                        {'range': [75, 100], 'color': '#e8f5e9'}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': health_score
                    }
                }
            ))
            fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col_metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Investment", f"₹{summary['total_investment']:,.0f}")
                st.metric("Holdings", f"{summary.get('total_stocks', len(portfolio_data))} stocks")
            
            with col2:
                st.metric("Current Value", f"₹{summary['current_value']:,.0f}")
                profit_ratio = summary['profitable_stocks'] / max(1, summary.get('total_stocks', len(portfolio_data))) * 100
                st.metric("Win Rate", f"{profit_ratio:.0f}%")
            
            with col3:
                gain_color = "normal" if summary['total_gain_loss'] >= 0 else "inverse"
                st.metric("Total Gain/Loss", f"₹{summary['total_gain_loss']:,.0f}", 
                         delta=f"{summary['total_gain_loss_percentage']:+.2f}%")
                st.metric("Profitable", f"{summary['profitable_stocks']} / {summary.get('total_stocks', len(portfolio_data))}")
        
        st.markdown("---")
    
    def render_dividend_and_tax_metrics(self, dividend_metrics, summary):
        """Render Dividend Yield and Tax Implication metrics"""
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #0d4f36 0%, #1a7a52 100%); 
                    border-radius: 12px; padding: 25px; margin-bottom: 20px; 
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);'>
            <h2 style='color: #fff; margin: 0 0 20px 0; font-size: 24px;'>💰 Dividend & Tax Metrics</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col_div, col_tax = st.columns(2)
        
        with col_div:
            st.markdown("""
            <div style='background: #f0fdf4; border-radius: 10px; padding: 20px; border: 1px solid #86efac;'>
                <h3 style='color: #166534; margin: 0 0 15px 0; font-size: 18px;'>📈 Dividend Yield Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            portfolio_yield = dividend_metrics.get('portfolio_dividend_yield', 0)
            annual_dividend = dividend_metrics.get('total_annual_dividend', 0)
            highest_yield_stock = dividend_metrics.get('highest_yield_stock', 'N/A')
            highest_yield_value = dividend_metrics.get('highest_yield_value', 0)
            dividend_stocks = dividend_metrics.get('dividend_paying_stocks', 0)
            non_dividend = dividend_metrics.get('non_dividend_stocks', 0)
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Portfolio Yield", f"{portfolio_yield:.2f}%", 
                         help="Weighted average dividend yield of your portfolio")
                st.metric("Dividend Stocks", f"{dividend_stocks}", 
                         help="Number of stocks paying dividends")
            with c2:
                st.metric("Annual Dividend", f"₹{annual_dividend:,.0f}",
                         help="Expected annual dividend income")
                st.metric("Non-Dividend", f"{non_dividend}",
                         help="Stocks not paying dividends")
            
            if highest_yield_stock != 'N/A':
                st.info(f"🏆 Highest Yield: **{highest_yield_stock}** at **{highest_yield_value:.2f}%**")
        
        with col_tax:
            st.markdown("""
            <div style='background: #fef2f2; border-radius: 10px; padding: 20px; border: 1px solid #fecaca;'>
                <h3 style='color: #991b1b; margin: 0 0 15px 0; font-size: 18px;'>📋 Tax Implications (If Sold Today)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            from utils.advanced_metrics import AdvancedMetricsCalculator
            try:
                calculator = AdvancedMetricsCalculator()
                if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
                    stock_df = pd.DataFrame(st.session_state.analysis_results.get('stock_performance', []))
                    if not stock_df.empty:
                        tax_data = calculator.calculate_tax_impact(stock_df)
                    else:
                        tax_data = self._get_default_tax_data()
                else:
                    tax_data = self._get_default_tax_data()
            except Exception:
                tax_data = self._get_default_tax_data()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("STCG Tax (20%)", f"₹{tax_data.get('estimated_stcg_tax', 0):,.0f}",
                         help="Short-term capital gains tax on holdings < 1 year")
                st.metric("LTCG Tax (12.5%)", f"₹{tax_data.get('estimated_ltcg_tax', 0):,.0f}",
                         help="Long-term capital gains tax above ₹1.25L exemption")
            with c2:
                st.metric("STT on Sell", f"₹{tax_data.get('stt_on_sell', 0):,.0f}",
                         help="Securities Transaction Tax (0.1% on sell value)")
                st.metric("Total Tax Liability", f"₹{tax_data.get('total_tax_and_costs', 0):,.0f}",
                         help="Total estimated taxes and transaction costs if entire portfolio is sold")
            
            ltcg_remaining = tax_data.get('ltcg_exemption_remaining', 0)
            if ltcg_remaining > 0:
                st.success(f"✅ LTCG Exemption Available: ₹{ltcg_remaining:,.0f}")
            else:
                st.warning(f"⚠️ LTCG exemption fully utilized")
        
        st.caption("*Tax estimates assume full portfolio liquidation. Based on Union Budget 2024 rates. Consult a tax advisor for personalized advice.*")
        st.markdown("---")
    
    def _get_default_tax_data(self):
        """Return default tax data when calculation fails"""
        return {
            'short_term_gains': 0, 'long_term_gains': 0,
            'estimated_stcg_tax': 0, 'estimated_ltcg_tax': 0,
            'stt_on_sell': 0, 'total_tax_and_costs': 0,
            'ltcg_exemption_remaining': 125000
        }
    
    def calculate_health_score(self, summary, portfolio_data):
        """Calculate portfolio health score based on multiple factors"""
        score = 50
        
        total_stocks = len(portfolio_data) if portfolio_data is not None else 0
        if total_stocks >= 10:
            score += 15
        elif total_stocks >= 5:
            score += 10
        elif total_stocks >= 3:
            score += 5
        
        if 'Sector' in portfolio_data.columns:
            unique_sectors = portfolio_data['Sector'].nunique()
            if unique_sectors >= 5:
                score += 15
            elif unique_sectors >= 3:
                score += 10
            elif unique_sectors >= 2:
                score += 5
        
        profit_ratio = summary['profitable_stocks'] / max(1, total_stocks)
        score += int(profit_ratio * 10)
        
        if summary['total_gain_loss_percentage'] > 0:
            score += min(10, summary['total_gain_loss_percentage'] / 2)
        
        return min(100, max(0, int(score)))
    
    def render_concentration_alerts(self, portfolio_data, summary):
        """Render concentration alerts with traffic-light icons"""
        
        alerts = []
        
        if 'Sector' in portfolio_data.columns and 'Current Value' in portfolio_data.columns:
            total_value = portfolio_data['Current Value'].sum()
            sector_pcts = portfolio_data.groupby('Sector')['Current Value'].sum() / total_value * 100
            
            for sector, pct in sector_pcts.items():
                if pct > 40:
                    alerts.append({
                        'type': 'danger',
                        'icon': '🔴',
                        'message': f"Very high concentration in {sector}: {pct:.1f}% of portfolio",
                        'insight': f"Consider diversifying to reduce sector-specific risk"
                    })
                elif pct > 30:
                    alerts.append({
                        'type': 'warning',
                        'icon': '🟡',
                        'message': f"High allocation to {sector}: {pct:.1f}% of portfolio",
                        'insight': f"Monitor this sector closely for any market shifts"
                    })
        
        if 'Current Value' in portfolio_data.columns:
            total_value = portfolio_data['Current Value'].sum()
            stock_pcts = portfolio_data.set_index('Stock Name')['Current Value'] / total_value * 100
            
            top_stock = stock_pcts.idxmax()
            top_pct = stock_pcts.max()
            
            if top_pct > 25:
                alerts.append({
                    'type': 'danger',
                    'icon': '🔴',
                    'message': f"Single stock risk: {top_stock} = {top_pct:.1f}% of portfolio",
                    'insight': "High exposure to one stock increases volatility risk"
                })
            elif top_pct > 15:
                alerts.append({
                    'type': 'warning',
                    'icon': '🟡',
                    'message': f"Concentrated position: {top_stock} = {top_pct:.1f}% of portfolio",
                    'insight': "Consider if this aligns with your risk tolerance"
                })
            
            top3_pct = stock_pcts.nlargest(3).sum()
            if top3_pct > 60:
                alerts.append({
                    'type': 'warning',
                    'icon': '🟡',
                    'message': f"Top 3 stocks account for {top3_pct:.1f}% of portfolio",
                    'insight': "Portfolio returns heavily depend on a few stocks"
                })
        
        total_stocks = len(portfolio_data)
        if total_stocks < 5:
            alerts.append({
                'type': 'warning',
                'icon': '🟡',
                'message': f"Limited diversification: Only {total_stocks} stocks in portfolio",
                'insight': "Consider adding more holdings to spread risk"
            })
        
        if not alerts:
            alerts.append({
                'type': 'success',
                'icon': '🟢',
                'message': "Good diversification: No major concentration issues detected",
                'insight': "Your portfolio appears reasonably diversified"
            })
        
        if alerts:
            st.markdown("""
            <div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px;'>
                <h4 style='margin: 0 0 15px 0; color: #333;'>⚠️ Risk Alerts & Insights</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for alert in alerts[:5]:
                bg_color = '#fee2e2' if alert['type'] == 'danger' else '#fef3c7' if alert['type'] == 'warning' else '#d1fae5'
                border_color = '#ef4444' if alert['type'] == 'danger' else '#f59e0b' if alert['type'] == 'warning' else '#10b981'
                
                st.markdown(f"""
                <div style='background: {bg_color}; border-left: 4px solid {border_color}; 
                            padding: 12px 15px; margin-bottom: 10px; border-radius: 0 8px 8px 0;'>
                    <div style='font-weight: 600; color: #333;'>{alert['icon']} {alert['message']}</div>
                    <div style='font-size: 13px; color: #666; margin-top: 4px;'>💡 {alert['insight']}</div>
                </div>
                """, unsafe_allow_html=True)
        
    def render_contribution_waterfall(self, stock_performance):
        """Render Contribution Waterfall chart showing how each stock contributed to P&L"""
        
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📊 Contribution Waterfall - Stock Impact on Portfolio P&L</h3>
        """, unsafe_allow_html=True)
        
        sorted_df = stock_performance.sort_values('Absolute Gain/Loss', ascending=True)
        
        colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in sorted_df['Absolute Gain/Loss']]
        
        fig_waterfall = go.Figure(go.Bar(
            y=sorted_df['Stock Name'],
            x=sorted_df['Absolute Gain/Loss'],
            orientation='h',
            marker_color=colors,
            text=[f"₹{x:+,.0f}" for x in sorted_df['Absolute Gain/Loss']],
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>Contribution: ₹%{x:,.2f}<extra></extra>"
        ))
        
        fig_waterfall.update_layout(
            title="Stock Contribution to Portfolio Gain/Loss",
            xaxis_title="Contribution (₹)",
            yaxis_title="",
            height=max(300, len(sorted_df) * 35),
            showlegend=False,
            xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black')
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        total_gain = stock_performance['Absolute Gain/Loss'].sum()
        top_contributor = stock_performance.loc[stock_performance['Absolute Gain/Loss'].idxmax()]
        worst_contributor = stock_performance.loc[stock_performance['Absolute Gain/Loss'].idxmin()]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style='background: #e8f5e9; padding: 10px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Top Contributor</div>
                <div style='font-size: 16px; font-weight: bold; color: #2e7d32;'>{top_contributor['Stock Name']}</div>
                <div style='font-size: 14px; color: #388e3c;'>₹{top_contributor['Absolute Gain/Loss']:+,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            bg = '#e8f5e9' if total_gain >= 0 else '#ffebee'
            color = '#2e7d32' if total_gain >= 0 else '#c62828'
            st.markdown(f"""
            <div style='background: {bg}; padding: 10px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Net Portfolio P&L</div>
                <div style='font-size: 20px; font-weight: bold; color: {color};'>₹{total_gain:+,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style='background: #ffebee; padding: 10px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Worst Contributor</div>
                <div style='font-size: 16px; font-weight: bold; color: #c62828;'>{worst_contributor['Stock Name']}</div>
                <div style='font-size: 14px; color: #e53935;'>₹{worst_contributor['Absolute Gain/Loss']:+,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_performance_charts(self, summary, stock_performance, analysis_results):
        """Render performance overview charts"""
        
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📈 Performance Overview</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            profit_stocks = summary['profitable_stocks']
            loss_stocks = summary['loss_making_stocks']
            
            fig_performance = go.Figure(data=[
                go.Bar(
                    x=['Profitable', 'Loss-making'],
                    y=[profit_stocks, loss_stocks],
                    marker_color=['#2ecc71', '#e74c3c'],
                    text=[profit_stocks, loss_stocks],
                    textposition='auto'
                )
            ])
            
            fig_performance.update_layout(
                title="Stock Performance Distribution",
                xaxis_title="Performance Category",
                yaxis_title="Number of Stocks",
                height=350
            )
            
            st.plotly_chart(fig_performance, use_container_width=True)
        
        with col2:
            fig_value = go.Figure()
            
            fig_value.add_trace(go.Bar(
                x=['Investment', 'Current Value'],
                y=[summary['total_investment'], summary['current_value']],
                marker_color=['#3498db', '#2980b9'],
                text=[f"₹{summary['total_investment']:,.0f}", f"₹{summary['current_value']:,.0f}"],
                textposition='auto'
            ))
            
            fig_value.update_layout(
                title="Investment vs Current Portfolio Value",
                yaxis_title="Amount (₹)",
                height=350
            )
            
            st.plotly_chart(fig_value, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>🏆 Stock Performance Highlights</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Performers")
            top_performers = stock_performance.nlargest(5, 'Percentage Gain/Loss')[
                ['Stock Name', 'Percentage Gain/Loss', 'Absolute Gain/Loss']
            ].copy()
            
            for idx, row in top_performers.iterrows():
                gain_loss = row['Percentage Gain/Loss']
                color = "green" if gain_loss >= 0 else "red"
                
                st.markdown(
                    f"**{row['Stock Name']}**: "
                    f"<span style='color:{color}'>{gain_loss:+.2f}% (₹{row['Absolute Gain/Loss']:+,.2f})</span>",
                    unsafe_allow_html=True
                )
        
        with col2:
            st.subheader("📉 Worst Performers")
            worst_performers = stock_performance.nsmallest(5, 'Percentage Gain/Loss')[
                ['Stock Name', 'Percentage Gain/Loss', 'Absolute Gain/Loss']
            ].copy()
            
            for idx, row in worst_performers.iterrows():
                gain_loss = row['Percentage Gain/Loss']
                color = "green" if gain_loss >= 0 else "red"
                
                st.markdown(
                    f"**{row['Stock Name']}**: "
                    f"<span style='color:{color}'>{gain_loss:+.2f}% (₹{row['Absolute Gain/Loss']:+,.2f})</span>",
                    unsafe_allow_html=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📋 Portfolio Holdings Summary</h3>
        """, unsafe_allow_html=True)
        
        display_df = stock_performance[['Stock Name', 'Sector', 'Category', 'Quantity', 'Buy Price', 'Current Price', 
                                      'Investment Value', 'Current Value', 'Absolute Gain/Loss', 'Percentage Gain/Loss']].copy()
        
        currency_cols = ['Buy Price', 'Current Price', 'Investment Value', 'Current Value', 'Absolute Gain/Loss']
        for col in currency_cols:
            display_df.loc[:, col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
        
        display_df.loc[:, 'Percentage Gain/Loss'] = display_df['Percentage Gain/Loss'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 12px; padding: 25px; margin-bottom: 20px; 
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);'>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <span style='font-size: 40px; margin-right: 15px;'>✨</span>
                <div>
                    <h3 style='color: white; margin: 0; font-size: 22px;'>Portfolio Advisor</h3>
                    <p style='color: rgba(255,255,255,0.85); margin: 5px 0 0 0; font-size: 14px;'>Get personalized insights about your portfolio</p>
                </div>
            </div>
            <p style='color: rgba(255,255,255,0.9); font-size: 15px; line-height: 1.6; margin-bottom: 15px;'>
                Ask questions about your holdings, sector allocation, recommendations, and get expert investment guidance based on your actual portfolio data.
            </p>
            <p style='color: rgba(255,255,255,0.7); font-size: 13px; margin: 0;'>
                💡 <strong>Tip:</strong> Click the "✨ Portfolio Advisor" button above to start chatting!
            </p>
        </div>
        """, unsafe_allow_html=True)
