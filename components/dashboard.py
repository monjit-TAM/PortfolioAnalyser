import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class Dashboard:
    def render(self, analysis_results, portfolio_data, current_data):
        """Render the main dashboard"""
        
        # Key Metrics Row - in a card
        summary = analysis_results['portfolio_summary']
        
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📊 Key Performance Metrics</h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Investment",
                value=f"₹{summary['total_investment']:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Current Value",
                value=f"₹{summary['current_value']:,.2f}",
                delta=f"₹{summary['total_gain_loss']:,.2f}"
            )
        
        with col3:
            st.metric(
                label="Total Gain/Loss",
                value=f"₹{summary['total_gain_loss']:,.2f}",
                delta=f"{summary['total_gain_loss_percentage']:,.2f}%"
            )
        
        with col4:
            st.metric(
                label="Portfolio Return",
                value=f"{summary['total_gain_loss_percentage']:,.2f}%",
                delta=None
            )
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close metrics card
        
        # Portfolio Composition Charts - in a card
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📈 Performance Overview</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Profit/Loss Distribution
            profit_stocks = summary['profitable_stocks']
            loss_stocks = summary['loss_making_stocks']
            
            fig_performance = go.Figure(data=[
                go.Bar(
                    x=['Profitable', 'Loss-making'],
                    y=[profit_stocks, loss_stocks],
                    marker_color=['green', 'red'],
                    text=[profit_stocks, loss_stocks],
                    textposition='auto'
                )
            ])
            
            fig_performance.update_layout(
                title="Stock Performance Distribution",
                xaxis_title="Performance Category",
                yaxis_title="Number of Stocks",
                height=400
            )
            
            st.plotly_chart(fig_performance, use_container_width=True)
        
        with col2:
            # Investment vs Current Value
            fig_value = go.Figure()
            
            fig_value.add_trace(go.Bar(
                x=['Investment', 'Current Value'],
                y=[summary['total_investment'], summary['current_value']],
                marker_color=['lightblue', 'darkblue'],
                text=[f"₹{summary['total_investment']:,.0f}", f"₹{summary['current_value']:,.0f}"],
                textposition='auto'
            ))
            
            fig_value.update_layout(
                title="Investment vs Current Portfolio Value",
                yaxis_title="Amount (₹)",
                height=400
            )
            
            st.plotly_chart(fig_value, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close performance overview card
        
        # Top Performers and Worst Performers - in a card
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>🏆 Stock Performance Highlights</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close highlights card
        
        # Portfolio Allocation Table - in a card
        st.markdown("""
        <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; 
                    padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);'>
            <h3 style='color: #FF6B35; margin-bottom: 15px; margin-top: 0;'>📋 Portfolio Holdings Summary</h3>
        """, unsafe_allow_html=True)
        
        display_df = stock_performance[['Stock Name', 'Sector', 'Category', 'Quantity', 'Buy Price', 'Current Price', 
                                      'Investment Value', 'Current Value', 'Absolute Gain/Loss', 'Percentage Gain/Loss']].copy()
        
        # Format currency columns
        currency_cols = ['Buy Price', 'Current Price', 'Investment Value', 'Current Value', 'Absolute Gain/Loss']
        for col in currency_cols:
            display_df.loc[:, col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
        
        display_df.loc[:, 'Percentage Gain/Loss'] = display_df['Percentage Gain/Loss'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close holdings table card
        
        # AI Assistant Quick Access Card
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 12px; padding: 25px; margin-bottom: 20px; 
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);'>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <span style='font-size: 40px; margin-right: 15px;'>🤖</span>
                <div>
                    <h3 style='color: white; margin: 0; font-size: 22px;'>AI Portfolio Assistant</h3>
                    <p style='color: rgba(255,255,255,0.85); margin: 5px 0 0 0; font-size: 14px;'>Get personalized insights about your portfolio</p>
                </div>
            </div>
            <p style='color: rgba(255,255,255,0.9); font-size: 15px; line-height: 1.6; margin-bottom: 15px;'>
                Ask questions about your holdings, sector allocation, recommendations, and get AI-powered investment guidance based on your actual portfolio data.
            </p>
            <p style='color: rgba(255,255,255,0.7); font-size: 13px; margin: 0;'>
                💡 <strong>Tip:</strong> Click the "🤖 AI Assistant" tab above to start chatting!
            </p>
        </div>
        """, unsafe_allow_html=True)
