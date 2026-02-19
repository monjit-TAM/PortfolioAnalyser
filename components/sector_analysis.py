import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.page_explanations import render_section_explainer

class SectorAnalysis:
    def render(self, analysis_results, portfolio_data, lang_code="en"):
        """Render sector analysis section"""
        
        st.header("🏭 Sector Analysis")
        
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        
        if sector_data.empty:
            st.warning("No sector data available.")
            return
        
        # Sector Allocation Pie Chart
        col1, col2 = st.columns(2)
        
        with col1:
            render_section_explainer("Sector Allocation by Value", "sector_allocation_pie", lang_code, analysis_results, icon="📊")
            
            fig_pie = px.pie(
                sector_data,
                values='Current Value',
                names='Sector',
                title="Portfolio Distribution by Sector",
                hover_data=['Number of Stocks'],
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            render_section_explainer("Sector Performance", "sector_performance", lang_code, analysis_results, icon="📈")
            
            # Create color map based on returns
            colors = ['green' if x >= 0 else 'red' for x in sector_data['Sector Return %']]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=sector_data['Sector'],
                    y=sector_data['Sector Return %'],
                    marker_color=colors,
                    text=[f"{x:+.2f}%" for x in sector_data['Sector Return %']],
                    textposition='auto'
                )
            ])
            
            fig_bar.update_layout(
                title="Sector-wise Returns (%)",
                xaxis_title="Sector",
                yaxis_title="Return %",
                height=400
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")

        self.render_market_cap_chart(analysis_results, lang_code)

        st.markdown("---")
        
        render_section_explainer("Detailed Sector Analysis", "sector_insights", lang_code=lang_code, analysis_results=analysis_results, icon="📋")
        
        # Format the data for display
        display_sector_data = sector_data.copy()
        display_sector_data['Investment Value'] = display_sector_data['Investment Value'].apply(lambda x: f"₹{x:,.2f}")
        display_sector_data['Current Value'] = display_sector_data['Current Value'].apply(lambda x: f"₹{x:,.2f}")
        display_sector_data['Absolute Gain/Loss'] = display_sector_data['Absolute Gain/Loss'].apply(lambda x: f"₹{x:+,.2f}")
        display_sector_data['Sector Return %'] = display_sector_data['Sector Return %'].apply(lambda x: f"{x:+.2f}%")
        display_sector_data['Percentage of Portfolio'] = display_sector_data['Percentage of Portfolio'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_sector_data, use_container_width=True)
        
        st.markdown("---")
        
        render_section_explainer("Sector Insights", "sector_insights", lang_code, analysis_results, icon="💡")
        
        # Find best and worst performing sectors
        best_sector = sector_data.loc[sector_data['Sector Return %'].idxmax()]
        worst_sector = sector_data.loc[sector_data['Sector Return %'].idxmin()]
        most_allocated = sector_data.loc[sector_data['Percentage of Portfolio'].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success(f"**Best Performing Sector**\n\n"
                      f"🏆 {best_sector['Sector']}\n\n"
                      f"Return: {best_sector['Sector Return %']:+.2f}%\n\n"
                      f"Allocation: {best_sector['Percentage of Portfolio']:.1f}%")
        
        with col2:
            st.error(f"**Worst Performing Sector**\n\n"
                    f"📉 {worst_sector['Sector']}\n\n"
                    f"Return: {worst_sector['Sector Return %']:+.2f}%\n\n"
                    f"Allocation: {worst_sector['Percentage of Portfolio']:.1f}%")
        
        with col3:
            st.info(f"**Largest Allocation**\n\n"
                   f"📊 {most_allocated['Sector']}\n\n"
                   f"Allocation: {most_allocated['Percentage of Portfolio']:.1f}%\n\n"
                   f"Return: {most_allocated['Sector Return %']:+.2f}%")
        
        st.markdown("---")
        render_section_explainer("Diversification Analysis", "diversification_analysis", lang_code, analysis_results, icon="🎯")
        
        total_sectors = len(sector_data)
        concentration_risk = sector_data['Percentage of Portfolio'].max()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Number of Sectors",
                value=total_sectors,
                help="Total number of sectors in portfolio"
            )
            
            # Diversification score
            if total_sectors >= 8:
                diversification_level = "Excellent"
                diversification_color = "green"
            elif total_sectors >= 5:
                diversification_level = "Good"
                diversification_color = "orange"
            else:
                diversification_level = "Needs Improvement"
                diversification_color = "red"
            
            st.markdown(f"**Diversification Level:** <span style='color:{diversification_color}'>{diversification_level}</span>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.metric(
                label="Concentration Risk",
                value=f"{concentration_risk:.1f}%",
                help="Percentage of portfolio in largest sector"
            )
            
            # Concentration risk assessment
            if concentration_risk > 40:
                concentration_level = "High Risk"
                concentration_color = "red"
                concentration_advice = "Consider reducing exposure to dominant sector"
            elif concentration_risk > 25:
                concentration_level = "Moderate Risk"
                concentration_color = "orange"
                concentration_advice = "Monitor sector concentration"
            else:
                concentration_level = "Low Risk"
                concentration_color = "green"
                concentration_advice = "Well-balanced sector allocation"
            
            st.markdown(f"**Risk Level:** <span style='color:{concentration_color}'>{concentration_level}</span>", 
                       unsafe_allow_html=True)
            st.caption(concentration_advice)
        
        st.markdown("---")
        render_section_explainer("Sector Recommendations", "sector_recommendations", lang_code, analysis_results, icon="📝")
        
        recommendations = []
        
        # Over-concentration warning
        if concentration_risk > 30:
            recommendations.append(
                f"⚠️ **Reduce concentration in {most_allocated['Sector']}**: "
                f"This sector represents {concentration_risk:.1f}% of your portfolio, which may increase risk."
            )
        
        # Underperforming sectors
        underperforming = sector_data[sector_data['Sector Return %'] < -10]
        if not underperforming.empty:
            for _, sector in underperforming.iterrows():
                recommendations.append(
                    f"📉 **Review {sector['Sector']} holdings**: "
                    f"This sector is down {abs(sector['Sector Return %']):.1f}%. "
                    f"Consider individual stock analysis for potential rebalancing."
                )
        
        # Strong performers
        strong_performers = sector_data[sector_data['Sector Return %'] > 20]
        if not strong_performers.empty:
            for _, sector in strong_performers.iterrows():
                recommendations.append(
                    f"🚀 **{sector['Sector']} performing well**: "
                    f"Up {sector['Sector Return %']:.1f}%. Consider taking some profits or "
                    f"maintaining position based on your investment strategy."
                )
        
        # Diversification recommendations
        if total_sectors < 5:
            recommendations.append(
                "🎯 **Improve diversification**: Consider adding stocks from different sectors "
                "to reduce risk and improve portfolio balance."
            )
        
        if recommendations:
            for rec in recommendations:
                st.markdown(rec)
        else:
            st.success("✅ Your sector allocation appears well-balanced with no immediate concerns.")

    def render_market_cap_chart(self, analysis_results, lang_code="en"):
        """Render Market Cap allocation pie chart"""
        
        stock_performance = pd.DataFrame(analysis_results.get('stock_performance', []))
        
        if stock_performance.empty or 'Market Cap' not in stock_performance.columns:
            return
        
        render_section_explainer("Market Cap Allocation", "market_cap_allocation", lang_code=lang_code, analysis_results=analysis_results, icon="🏢")
        
        df = stock_performance[stock_performance['Market Cap'] > 0].copy()
        
        if df.empty:
            st.info("Market cap data not available for portfolio stocks.")
            return

        def classify_market_cap(mc):
            if mc >= 200_000_000_000:
                return 'Large Cap (₹20,000Cr+)'
            elif mc >= 50_000_000_000:
                return 'Mid Cap (₹5,000-20,000Cr)'
            elif mc >= 10_000_000_000:
                return 'Small Cap (₹1,000-5,000Cr)'
            else:
                return 'Micro Cap (<₹1,000Cr)'

        df['Market Cap Category'] = df['Market Cap'].apply(classify_market_cap)

        col1, col2 = st.columns(2)

        with col1:
            cap_allocation = df.groupby('Market Cap Category')['Current Value'].sum().reset_index()
            cap_allocation.columns = ['Category', 'Value']
            
            color_map = {
                'Large Cap (₹20,000Cr+)': '#2563eb',
                'Mid Cap (₹5,000-20,000Cr)': '#7c3aed',
                'Small Cap (₹1,000-5,000Cr)': '#db2777',
                'Micro Cap (<₹1,000Cr)': '#ea580c'
            }
            
            fig_cap = px.pie(
                cap_allocation,
                values='Value',
                names='Category',
                title='Portfolio by Market Cap',
                color='Category',
                color_discrete_map=color_map
            )
            fig_cap.update_traces(textposition='inside', textinfo='percent+label')
            fig_cap.update_layout(height=420)
            st.plotly_chart(fig_cap, use_container_width=True)

        with col2:
            cap_detail = df.groupby('Market Cap Category').agg(
                Stocks=('Stock Name', 'count'),
                Investment=('Investment Value', 'sum'),
                Current_Value=('Current Value', 'sum')
            ).reset_index()
            cap_detail.columns = ['Market Cap Category', 'No. of Stocks', 'Investment', 'Current Value']
            cap_detail['Gain/Loss'] = cap_detail['Current Value'] - cap_detail['Investment']
            cap_detail['Return %'] = ((cap_detail['Current Value'] - cap_detail['Investment']) / cap_detail['Investment'] * 100)
            cap_detail['Allocation %'] = (cap_detail['Current Value'] / cap_detail['Current Value'].sum() * 100)

            display_cap = cap_detail.copy()
            display_cap['Investment'] = display_cap['Investment'].apply(lambda x: f"₹{x:,.0f}")
            display_cap['Current Value'] = display_cap['Current Value'].apply(lambda x: f"₹{x:,.0f}")
            display_cap['Gain/Loss'] = display_cap['Gain/Loss'].apply(lambda x: f"₹{x:+,.0f}")
            display_cap['Return %'] = display_cap['Return %'].apply(lambda x: f"{x:+.2f}%")
            display_cap['Allocation %'] = display_cap['Allocation %'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_cap, use_container_width=True, hide_index=True)

            st.markdown("")
            top_stock = df.loc[df['Market Cap'].idxmax()]
            st.info(f"🏆 Largest company: **{top_stock['Stock Name']}** (Market Cap: ₹{top_stock['Market Cap']/10_000_000:,.0f} Cr)")
