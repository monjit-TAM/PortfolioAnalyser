import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class Dashboard:
    def render(self, analysis_results, portfolio_data, current_data):
        """Render the main dashboard"""
        
        st.header("📊 Portfolio Dashboard")
        
        # Key Metrics Row
        summary = analysis_results['portfolio_summary']
        
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
        
        st.markdown("---")
        
        # Portfolio Composition Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Portfolio Performance Overview")
            
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
            st.subheader("💰 Investment vs Current Value")
            
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
        
        st.markdown("---")
        
        # Top Performers and Worst Performers
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
        
        st.markdown("---")
        
        # Risk Metrics
        st.subheader("⚠️ Risk Metrics")
        
        risk_metrics = analysis_results['risk_metrics']
        
        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
        
        with risk_col1:
            st.metric(
                label="Portfolio Volatility",
                value=f"{risk_metrics['portfolio_volatility']*100:.2f}%",
                help="Annualized portfolio volatility"
            )
        
        with risk_col2:
            st.metric(
                label="Sharpe Ratio",
                value=f"{risk_metrics['sharpe_ratio']:.2f}",
                help="Risk-adjusted return metric"
            )
        
        with risk_col3:
            st.metric(
                label="Max Stock Weight",
                value=f"{risk_metrics['max_stock_weight']*100:.2f}%",
                help="Largest stock allocation"
            )
        
        with risk_col4:
            diversification_score = "High" if summary['number_of_stocks'] >= 10 else "Medium" if summary['number_of_stocks'] >= 5 else "Low"
            st.metric(
                label="Diversification",
                value=diversification_score,
                help=f"Based on {summary['number_of_stocks']} stocks"
            )
        
        # Portfolio Allocation Table
        st.markdown("---")
        st.subheader("📋 Portfolio Holdings Summary")
        
        display_df = stock_performance[['Stock Name', 'Sector', 'Category', 'Quantity', 'Buy Price', 'Current Price', 
                                      'Investment Value', 'Current Value', 'Absolute Gain/Loss', 'Percentage Gain/Loss']].copy()
        
        # Format currency columns
        currency_cols = ['Buy Price', 'Current Price', 'Investment Value', 'Current Value', 'Absolute Gain/Loss']
        for col in currency_cols:
            display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
        
        display_df['Percentage Gain/Loss'] = display_df['Percentage Gain/Loss'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(display_df, use_container_width=True, height=400)
