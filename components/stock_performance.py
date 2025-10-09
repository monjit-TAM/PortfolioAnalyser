import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

class StockPerformance:
    def render(self, analysis_results, portfolio_data, current_data, historical_data):
        """Render individual stock performance analysis"""
        
        st.header("📈 Individual Stock Performance")
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
        # Stock Selection
        selected_stock = st.selectbox(
            "Select a stock for detailed analysis:",
            options=stock_performance['Stock Name'].tolist(),
            index=0
        )
        
        # Get selected stock data
        stock_data = stock_performance[stock_performance['Stock Name'] == selected_stock].iloc[0]
        stock_history = historical_data.get(selected_stock, pd.DataFrame())
        
        # Stock Overview Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            gain_loss = stock_data['Absolute Gain/Loss']
            delta_color = "normal" if gain_loss >= 0 else "inverse"
            st.metric(
                label="Current Price",
                value=f"₹{stock_data['Current Price']:.2f}",
                delta=f"₹{gain_loss:+.2f}",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                label="Buy Price",
                value=f"₹{stock_data['Buy Price']:.2f}",
                delta=None
            )
        
        with col3:
            percentage_gain = stock_data['Percentage Gain/Loss']
            delta_color = "normal" if percentage_gain >= 0 else "inverse"
            st.metric(
                label="Total Return",
                value=f"{percentage_gain:+.2f}%",
                delta=None,
                delta_color=delta_color
            )
        
        with col4:
            st.metric(
                label="All-Time High Since Purchase",
                value=f"₹{stock_data['All Time High Since Purchase']:.2f}",
                delta=f"{stock_data['Potential Gain from ATH']:+.2f}%"
            )
        
        st.markdown("---")
        
        # Stock Details
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Stock Information")
            info_data = {
                "Stock Name": stock_data['Stock Name'],
                "Sector": stock_data['Sector'],
                "Category": stock_data['Category'],
                "Quantity Held": f"{stock_data['Quantity']:,}",
                "Investment Value": f"₹{stock_data['Investment Value']:,.2f}",
                "Current Value": f"₹{stock_data['Current Value']:,.2f}",
                "Buy Date": stock_data['Buy Date'].strftime('%d %b, %Y') if pd.notna(stock_data['Buy Date']) else 'N/A'
            }
            
            for key, value in info_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("📈 Performance Metrics")
            
            # Calculate additional metrics if historical data is available
            if not stock_history.empty and len(stock_history) > 1:
                # Volatility calculation
                returns = stock_history['Close'].pct_change().dropna()
                volatility = returns.std() * (252**0.5) * 100  # Annualized volatility
                
                # Max drawdown since purchase
                running_max = stock_history['Close'].expanding().max()
                drawdown = (stock_history['Close'] - running_max) / running_max * 100
                max_drawdown = drawdown.min()
                
                # Average trading volume
                avg_volume = stock_history['Volume'].mean() if 'Volume' in stock_history.columns else 0
                
                metrics_data = {
                    "Volatility (Annualized)": f"{volatility:.2f}%",
                    "Max Drawdown": f"{max_drawdown:.2f}%",
                    "Days Held": f"{(datetime.now() - pd.to_datetime(stock_data['Buy Date'])).days:,}",
                    "Avg. Daily Volume": f"{avg_volume:,.0f}" if avg_volume > 0 else "N/A"
                }
                
                for key, value in metrics_data.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write("**Historical data limited**")
        
        st.markdown("---")
        
        # Price Chart
        if not stock_history.empty:
            st.subheader(f"📈 Price Chart - {selected_stock}")
            
            # Create price chart with buy price line and ATH marker
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxis=True,
                vertical_spacing=0.1,
                subplot_titles=('Price Movement', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # Price line
            fig.add_trace(
                go.Scatter(
                    x=stock_history.index,
                    y=stock_history['Close'],
                    mode='lines',
                    name='Price',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
            
            # Buy price line
            fig.add_hline(
                y=stock_data['Buy Price'],
                line_dash="dash",
                line_color="green",
                annotation_text=f"Buy Price: ₹{stock_data['Buy Price']:.2f}",
                annotation_position="top left",
                row=1, col=1
            )
            
            # All-time high line
            fig.add_hline(
                y=stock_data['All Time High Since Purchase'],
                line_dash="dot",
                line_color="red",
                annotation_text=f"ATH: ₹{stock_data['All Time High Since Purchase']:.2f}",
                annotation_position="top right",
                row=1, col=1
            )
            
            # Volume bars
            if 'Volume' in stock_history.columns:
                fig.add_trace(
                    go.Bar(
                        x=stock_history.index,
                        y=stock_history['Volume'],
                        name='Volume',
                        marker_color='lightgray',
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            fig.update_layout(
                title=f"{selected_stock} - Price and Volume Analysis",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=600,
                showlegend=True
            )
            
            fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning(f"No historical data available for {selected_stock}")
        
        st.markdown("---")
        
        # Performance Analysis
        st.subheader("🎯 Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Current Position Analysis")
            
            if stock_data['Percentage Gain/Loss'] > 0:
                st.success(f"✅ **Profitable Position**")
                st.write(f"• Gained ₹{stock_data['Absolute Gain/Loss']:,.2f} ({stock_data['Percentage Gain/Loss']:+.2f}%)")
                st.write(f"• Current value: ₹{stock_data['Current Value']:,.2f}")
                
                if stock_data['Percentage Gain/Loss'] > 20:
                    st.info("💡 Consider taking partial profits or reviewing position size")
                elif stock_data['Percentage Gain/Loss'] > 50:
                    st.warning("⚠️ Substantial gains - consider profit booking strategy")
            
            else:
                st.error(f"❌ **Loss Position**")
                st.write(f"• Lost ₹{abs(stock_data['Absolute Gain/Loss']):,.2f} ({stock_data['Percentage Gain/Loss']:+.2f}%)")
                st.write(f"• Current value: ₹{stock_data['Current Value']:,.2f}")
                
                if stock_data['Percentage Gain/Loss'] < -20:
                    st.warning("⚠️ Significant loss - review fundamentals")
                elif stock_data['Percentage Gain/Loss'] < -40:
                    st.error("🚨 Major loss - consider exit strategy")
        
        with col2:
            st.write("#### Potential vs Reality")
            
            potential_gain_ath = stock_data['Potential Gain from ATH']
            current_vs_ath = ((stock_data['Current Price'] - stock_data['All Time High Since Purchase']) / stock_data['All Time High Since Purchase']) * 100
            
            st.write(f"• **Potential gain from ATH:** {potential_gain_ath:+.2f}%")
            st.write(f"• **Current vs ATH:** {current_vs_ath:+.2f}%")
            
            if current_vs_ath > -10:
                st.success("🎯 Trading near all-time high")
            elif current_vs_ath > -25:
                st.info("📊 Moderate correction from ATH")
            else:
                st.warning("📉 Significant correction from ATH")
            
            # Time-based analysis
            if pd.notna(stock_data['Buy Date']):
                days_held = (datetime.now() - pd.to_datetime(stock_data['Buy Date'])).days
                annualized_return = (stock_data['Percentage Gain/Loss'] / 100) * (365 / days_held) * 100 if days_held > 0 else 0
                
                st.write(f"• **Days held:** {days_held:,}")
                st.write(f"• **Annualized return:** {annualized_return:+.2f}%")
        
        # Quick Action Recommendations
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if stock_data['Percentage Gain/Loss'] > 30:
                st.info("📈 **Consider**: Taking partial profits")
            elif stock_data['Percentage Gain/Loss'] < -30:
                st.warning("📉 **Consider**: Reviewing position")
            else:
                st.success("💎 **Consider**: Holding position")
        
        with action_col2:
            if stock_data['Category'] == 'Large Cap':
                st.info("🏛️ **Stability**: Large cap stock - lower volatility")
            elif stock_data['Category'] == 'Mid Cap':
                st.warning("⚖️ **Balanced**: Mid cap stock - moderate risk")
            else:
                st.error("🎲 **High Risk**: Small cap stock - higher volatility")
        
        with action_col3:
            sector_performance = analysis_results['sector_analysis']
            sector_df = pd.DataFrame(sector_performance)
            
            if not sector_df.empty:
                stock_sector_data = sector_df[sector_df['Sector'] == stock_data['Sector']]
                if not stock_sector_data.empty:
                    sector_return = stock_sector_data.iloc[0]['Sector Return %']
                    if sector_return > 10:
                        st.success(f"🏭 **Sector**: Performing well ({sector_return:+.1f}%)")
                    elif sector_return < -10:
                        st.error(f"🏭 **Sector**: Underperforming ({sector_return:+.1f}%)")
                    else:
                        st.info(f"🏭 **Sector**: Stable ({sector_return:+.1f}%)")
