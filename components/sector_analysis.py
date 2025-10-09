import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class SectorAnalysis:
    def render(self, analysis_results, portfolio_data):
        """Render sector analysis section"""
        
        st.header("🏭 Sector Analysis")
        
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        
        if sector_data.empty:
            st.warning("No sector data available.")
            return
        
        # Sector Allocation Pie Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Sector Allocation by Value")
            
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
            st.subheader("📈 Sector Performance")
            
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
        
        # Detailed Sector Table
        st.subheader("📋 Detailed Sector Analysis")
        
        # Format the data for display
        display_sector_data = sector_data.copy()
        display_sector_data['Investment Value'] = display_sector_data['Investment Value'].apply(lambda x: f"₹{x:,.2f}")
        display_sector_data['Current Value'] = display_sector_data['Current Value'].apply(lambda x: f"₹{x:,.2f}")
        display_sector_data['Absolute Gain/Loss'] = display_sector_data['Absolute Gain/Loss'].apply(lambda x: f"₹{x:+,.2f}")
        display_sector_data['Sector Return %'] = display_sector_data['Sector Return %'].apply(lambda x: f"{x:+.2f}%")
        display_sector_data['Percentage of Portfolio'] = display_sector_data['Percentage of Portfolio'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_sector_data, use_container_width=True)
        
        st.markdown("---")
        
        # Sector Insights and Recommendations
        st.subheader("💡 Sector Insights")
        
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
        
        # Diversification Analysis
        st.markdown("---")
        st.subheader("🎯 Diversification Analysis")
        
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
        
        # Sector Recommendations
        st.markdown("---")
        st.subheader("📝 Sector Recommendations")
        
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
