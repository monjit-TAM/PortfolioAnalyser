import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.page_explanations import render_section_explainer

class Recommendations:
    def render(self, recommendations, analysis_results, lang_code="en"):
        """Render investment recommendations section"""
        
        st.header("💡 Investment Recommendations")
        
        if not recommendations:
            st.warning("No recommendations available.")
            return
        
        # Summary of recommendations
        render_section_explainer("Recommendation Summary", "buy_hold_sell", lang_code=lang_code, analysis_results=analysis_results, icon="📊")
        
        # Count recommendations by action
        buy_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY')
        hold_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'HOLD')
        sell_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🟢 BUY Recommendations",
                value=buy_count,
                help="Stocks recommended for purchase or accumulation"
            )
        
        with col2:
            st.metric(
                label="🟡 HOLD Recommendations",
                value=hold_count,
                help="Stocks recommended to maintain current position"
            )
        
        with col3:
            st.metric(
                label="🔴 SELL Recommendations",
                value=sell_count,
                help="Stocks recommended for sale or position reduction"
            )
        
        # Recommendation distribution chart
        if buy_count + hold_count + sell_count > 0:
            fig_rec = px.pie(
                values=[buy_count, hold_count, sell_count],
                names=['BUY', 'HOLD', 'SELL'],
                title="Recommendation Distribution",
                color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red'}
            )
            
            fig_rec.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_rec, use_container_width=True)
        
        st.markdown("---")
        
        # Investment Perspective Tabs
        tab1, tab2, tab3 = st.tabs(["📈 Overall Recommendations", "💰 Value Perspective", "🚀 Growth Perspective"])
        
        with tab1:
            self.render_overall_recommendations(recommendations)
        
        with tab2:
            self.render_value_perspective(recommendations, lang_code=lang_code, analysis_results=analysis_results)
        
        with tab3:
            self.render_growth_perspective(recommendations, lang_code=lang_code, analysis_results=analysis_results)
    
    def render_overall_recommendations(self, recommendations):
        """Render overall recommendations combining both perspectives"""
        
        st.subheader("🎯 Overall Investment Recommendations")
        
        # Group recommendations by action
        buy_recs = [rec for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY']
        hold_recs = [rec for rec in recommendations if rec['overall_recommendation']['action'] == 'HOLD']
        sell_recs = [rec for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL']
        
        # BUY Recommendations
        if buy_recs:
            st.success("🟢 **BUY RECOMMENDATIONS**")
            
            for rec in buy_recs:
                with st.expander(f"📈 {rec['stock_name']} - BUY ({rec['overall_recommendation']['confidence']} Confidence)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Status:**")
                        st.write(f"• Current Price: ₹{rec['current_price']:.2f}")
                        st.write(f"• Buy Price: ₹{rec['buy_price']:.2f}")
                        st.write(f"• Current Return: {rec['gain_loss_percentage']:+.2f}%")
                        
                        # Fundamental metrics if available
                        if rec['fundamentals']:
                            st.write("**Key Metrics:**")
                            pe_ratio = rec['fundamentals'].get('pe_ratio')
                            if pe_ratio:
                                st.write(f"• P/E Ratio: {pe_ratio:.2f}")
                            
                            pb_ratio = rec['fundamentals'].get('pb_ratio')
                            if pb_ratio:
                                st.write(f"• P/B Ratio: {pb_ratio:.2f}")
                    
                    with col2:
                        st.write("**Recommendation Rationale:**")
                        for rationale in rec['overall_recommendation']['rationale']:
                            st.write(f"• {rationale}")
                        
                        st.write("**Action Plan:**")
                        st.write("• ✅ Consider accumulating more shares")
                        st.write("• 📊 Monitor fundamentals regularly")
                        st.write("• ⏰ Good entry point for long-term investors")
        
        # HOLD Recommendations
        if hold_recs:
            st.info("🟡 **HOLD RECOMMENDATIONS**")
            
            for rec in hold_recs:
                with st.expander(f"📊 {rec['stock_name']} - HOLD ({rec['overall_recommendation']['confidence']} Confidence)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Status:**")
                        st.write(f"• Current Price: ₹{rec['current_price']:.2f}")
                        st.write(f"• Buy Price: ₹{rec['buy_price']:.2f}")
                        st.write(f"• Current Return: {rec['gain_loss_percentage']:+.2f}%")
                    
                    with col2:
                        st.write("**Hold Rationale:**")
                        for rationale in rec['overall_recommendation']['rationale']:
                            st.write(f"• {rationale}")
                        
                        st.write("**Action Plan:**")
                        st.write("• 💎 Maintain current position")
                        st.write("• 👀 Watch for better entry/exit opportunities")
                        st.write("• 📈 Monitor quarterly results")
        
        # SELL Recommendations
        if sell_recs:
            st.error("🔴 **SELL RECOMMENDATIONS**")
            
            for rec in sell_recs:
                with st.expander(f"📉 {rec['stock_name']} - SELL ({rec['overall_recommendation']['confidence']} Confidence)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Status:**")
                        st.write(f"• Current Price: ₹{rec['current_price']:.2f}")
                        st.write(f"• Buy Price: ₹{rec['buy_price']:.2f}")
                        st.write(f"• Current Return: {rec['gain_loss_percentage']:+.2f}%")
                        
                        if rec['gain_loss_percentage'] < 0:
                            st.write("• ⚠️ Currently in loss")
                        else:
                            st.write("• ✅ Currently profitable")
                    
                    with col2:
                        st.write("**Sell Rationale:**")
                        for rationale in rec['overall_recommendation']['rationale']:
                            st.write(f"• {rationale}")
                        
                        st.write("**Action Plan:**")
                        st.write("• 🔄 Consider exiting position")
                        st.write("• ⏰ Look for better exit timing")
                        st.write("• 🔍 Review alternative investments")
                    
                    # Show alternatives if available
                    if rec['alternatives']:
                        st.write("**Alternative Investment Suggestions:**")
                        for alt in rec['alternatives']:
                            st.success(f"💡 **{alt['stock_name']}** ({alt['sector']}): {alt['rationale']}")
    
    def render_value_perspective(self, recommendations, lang_code="en", analysis_results=None):
        """Render recommendations from value investing perspective"""
        
        render_section_explainer("Value Investing Perspective", "value_analysis", lang_code=lang_code, analysis_results=analysis_results, icon="💰")
        st.write("*Analysis based on fundamental metrics like P/E, P/B ratios, dividend yield, and financial health*")
        
        # Sort by value score (higher is better for value investing)
        value_sorted = sorted(recommendations, key=lambda x: x['value_analysis']['score'], reverse=True)
        
        for rec in value_sorted:
            value_analysis = rec['value_analysis']
            
            # Color coding based on recommendation
            if value_analysis['recommendation'] == 'BUY':
                color = "green"
                emoji = "🟢"
            elif value_analysis['recommendation'] == 'SELL':
                color = "red"
                emoji = "🔴"
            else:
                color = "orange"
                emoji = "🟡"
            
            with st.expander(f"{emoji} {rec['stock_name']} - Value Score: {value_analysis['score']} ({value_analysis['recommendation']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Value Factors:**")
                    if value_analysis['factors']:
                        for factor in value_analysis['factors']:
                            st.write(f"• {factor}")
                    else:
                        st.write("• Limited fundamental data available")
                    
                    # Display key value metrics
                    if rec['fundamentals']:
                        st.write("**Key Value Metrics:**")
                        
                        pe_ratio = rec['fundamentals'].get('pe_ratio')
                        if pe_ratio:
                            pe_color = "green" if pe_ratio < 15 else "red" if pe_ratio > 25 else "orange"
                            st.markdown(f"• P/E Ratio: <span style='color:{pe_color}'>{pe_ratio:.2f}</span>", unsafe_allow_html=True)
                        
                        pb_ratio = rec['fundamentals'].get('pb_ratio')
                        if pb_ratio:
                            pb_color = "green" if pb_ratio < 1.5 else "red" if pb_ratio > 3 else "orange"
                            st.markdown(f"• P/B Ratio: <span style='color:{pb_color}'>{pb_ratio:.2f}</span>", unsafe_allow_html=True)
                        
                        dividend_yield = rec['fundamentals'].get('dividend_yield')
                        if dividend_yield:
                            div_color = "green" if dividend_yield > 0.03 else "orange"
                            st.markdown(f"• Dividend Yield: <span style='color:{div_color}'>{dividend_yield*100:.2f}%</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write("**Value Investment Rationale:**")
                    if value_analysis['rationale']:
                        for rationale in value_analysis['rationale']:
                            st.write(f"• {rationale}")
                    
                    st.write(f"**Value Recommendation: <span style='color:{color}'>{value_analysis['recommendation']}</span>**", unsafe_allow_html=True)
                    
                    # Value investing tips
                    if value_analysis['recommendation'] == 'BUY':
                        st.success("💡 **Value Tip**: This stock appears undervalued based on fundamentals")
                    elif value_analysis['recommendation'] == 'SELL':
                        st.error("💡 **Value Tip**: Current valuation may be stretched")
                    else:
                        st.info("💡 **Value Tip**: Fair valuation - monitor for better entry points")
    
    def render_growth_perspective(self, recommendations, lang_code="en", analysis_results=None):
        """Render recommendations from growth investing perspective"""
        
        render_section_explainer("Growth Investing Perspective", "growth_analysis", lang_code=lang_code, analysis_results=analysis_results, icon="🚀")
        st.write("*Analysis based on revenue growth, earnings growth, ROE, and price momentum*")
        
        # Sort by growth score (higher is better for growth investing)
        growth_sorted = sorted(recommendations, key=lambda x: x['growth_analysis']['score'], reverse=True)
        
        for rec in growth_sorted:
            growth_analysis = rec['growth_analysis']
            
            # Color coding based on recommendation
            if growth_analysis['recommendation'] == 'BUY':
                color = "green"
                emoji = "🟢"
            elif growth_analysis['recommendation'] == 'SELL':
                color = "red"
                emoji = "🔴"
            else:
                color = "orange"
                emoji = "🟡"
            
            with st.expander(f"{emoji} {rec['stock_name']} - Growth Score: {growth_analysis['score']} ({growth_analysis['recommendation']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Growth Factors:**")
                    if growth_analysis['factors']:
                        for factor in growth_analysis['factors']:
                            st.write(f"• {factor}")
                    else:
                        st.write("• Limited growth data available")
                    
                    # Display key growth metrics
                    if rec['fundamentals']:
                        st.write("**Key Growth Metrics:**")
                        
                        revenue_growth = rec['fundamentals'].get('revenue_growth')
                        if revenue_growth:
                            rev_color = "green" if revenue_growth > 0.15 else "red" if revenue_growth < 0 else "orange"
                            st.markdown(f"• Revenue Growth: <span style='color:{rev_color}'>{revenue_growth*100:.2f}%</span>", unsafe_allow_html=True)
                        
                        earnings_growth = rec['fundamentals'].get('earnings_growth')
                        if earnings_growth:
                            earn_color = "green" if earnings_growth > 0.20 else "red" if earnings_growth < 0 else "orange"
                            st.markdown(f"• Earnings Growth: <span style='color:{earn_color}'>{earnings_growth*100:.2f}%</span>", unsafe_allow_html=True)
                        
                        roe = rec['fundamentals'].get('roe')
                        if roe:
                            roe_color = "green" if roe > 0.20 else "red" if roe < 0.10 else "orange"
                            st.markdown(f"• ROE: <span style='color:{roe_color}'>{roe*100:.2f}%</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write("**Growth Investment Rationale:**")
                    if growth_analysis['rationale']:
                        for rationale in growth_analysis['rationale']:
                            st.write(f"• {rationale}")
                    
                    st.write(f"**Growth Recommendation: <span style='color:{color}'>{growth_analysis['recommendation']}</span>**", unsafe_allow_html=True)
                    
                    # Growth investing tips
                    if growth_analysis['recommendation'] == 'BUY':
                        st.success("💡 **Growth Tip**: Strong growth potential identified")
                    elif growth_analysis['recommendation'] == 'SELL':
                        st.error("💡 **Growth Tip**: Growth momentum appears to be slowing")
                    else:
                        st.info("💡 **Growth Tip**: Moderate growth prospects - watch quarterly results")
        
        st.markdown("---")
        
        # Growth vs Value Analysis Summary
        render_section_explainer("Value vs Growth Analysis Summary", "alternative_suggestions", lang_code=lang_code, analysis_results=analysis_results, icon="⚖️")
        
        value_buy = sum(1 for rec in recommendations if rec['value_analysis']['recommendation'] == 'BUY')
        growth_buy = sum(1 for rec in recommendations if rec['growth_analysis']['recommendation'] == 'BUY')
        
        value_sell = sum(1 for rec in recommendations if rec['value_analysis']['recommendation'] == 'SELL')
        growth_sell = sum(1 for rec in recommendations if rec['growth_analysis']['recommendation'] == 'SELL')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Value-Based BUY Signals",
                value=value_buy,
                delta=f"{value_buy - value_sell:+d} (vs SELL signals)"
            )
        
        with col2:
            st.metric(
                label="Growth-Based BUY Signals", 
                value=growth_buy,
                delta=f"{growth_buy - growth_sell:+d} (vs SELL signals)"
            )
        
        # Investment style recommendation
        if value_buy > growth_buy:
            st.info("📊 **Portfolio Tendency**: Your portfolio shows more value opportunities than growth")
        elif growth_buy > value_buy:
            st.info("🚀 **Portfolio Tendency**: Your portfolio shows more growth opportunities than value")
        else:
            st.info("⚖️ **Portfolio Balance**: Equal mix of value and growth opportunities")
