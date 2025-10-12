import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class HistoricalPerformance:
    def render(self, analysis_results, portfolio_data, historical_data):
        """Render historical portfolio performance tracking"""
        
        st.header("📈 Historical Portfolio Performance")
        
        # Calculate portfolio value over time
        portfolio_history = self.calculate_portfolio_history(portfolio_data, historical_data)
        
        if portfolio_history.empty:
            st.warning("Insufficient historical data to display performance tracking.")
            return
        
        # Performance summary metrics
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        initial_value = portfolio_history['Portfolio_Value'].iloc[0]
        current_value = portfolio_history['Portfolio_Value'].iloc[-1]
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Calculate peak and drawdown
        peak_value = portfolio_history['Portfolio_Value'].max()
        peak_date = portfolio_history.loc[portfolio_history['Portfolio_Value'].idxmax(), 'Date']
        
        current_drawdown = ((current_value - peak_value) / peak_value) * 100
        
        # Calculate volatility
        daily_returns = portfolio_history['Portfolio_Value'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
        
        with col1:
            st.metric(
                label="Total Return",
                value=f"{total_return:+.2f}%",
                delta=f"₹{current_value - initial_value:+,.2f}",
                help="Total portfolio return since inception"
            )
        
        with col2:
            st.metric(
                label="Peak Portfolio Value",
                value=f"₹{peak_value:,.2f}",
                delta=peak_date.strftime('%d %b %Y'),
                help="Highest portfolio value achieved"
            )
        
        with col3:
            drawdown_color = "inverse" if current_drawdown < 0 else "normal"
            st.metric(
                label="Current Drawdown",
                value=f"{current_drawdown:.2f}%",
                delta=None,
                delta_color=drawdown_color,
                help="Decline from peak value"
            )
        
        with col4:
            st.metric(
                label="Annualized Volatility",
                value=f"{volatility:.2f}%",
                delta=None,
                help="Portfolio volatility (risk measure)"
            )
        
        st.markdown("---")
        
        # Portfolio value chart over time
        st.subheader("💰 Portfolio Value Over Time")
        
        fig = go.Figure()
        
        # Portfolio value line
        fig.add_trace(go.Scatter(
            x=portfolio_history['Date'],
            y=portfolio_history['Portfolio_Value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 100, 255, 0.1)'
        ))
        
        # Investment value line (cost basis)
        fig.add_trace(go.Scatter(
            x=portfolio_history['Date'],
            y=portfolio_history['Investment_Value'],
            mode='lines',
            name='Investment (Cost Basis)',
            line=dict(color='gray', width=1, dash='dash')
        ))
        
        # Mark peak
        fig.add_trace(go.Scatter(
            x=[peak_date],
            y=[peak_value],
            mode='markers',
            name='Peak Value',
            marker=dict(color='red', size=12, symbol='star')
        ))
        
        fig.update_layout(
            title='Portfolio Value Progression',
            xaxis_title='Date',
            yaxis_title='Value (₹)',
            height=500,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Returns chart
        st.subheader("📊 Cumulative Returns Over Time")
        
        # Calculate cumulative returns
        portfolio_history['Cumulative_Return'] = ((portfolio_history['Portfolio_Value'] - initial_value) / initial_value) * 100
        
        fig_returns = go.Figure()
        
        # Color based on positive/negative
        colors = ['green' if x >= 0 else 'red' for x in portfolio_history['Cumulative_Return']]
        
        fig_returns.add_trace(go.Bar(
            x=portfolio_history['Date'],
            y=portfolio_history['Cumulative_Return'],
            marker_color=colors,
            name='Cumulative Return %',
            opacity=0.7
        ))
        
        # Add zero line
        fig_returns.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
        
        fig_returns.update_layout(
            title='Cumulative Returns (%)',
            xaxis_title='Date',
            yaxis_title='Return (%)',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_returns, use_container_width=True)
        
        st.markdown("---")
        
        # Drawdown chart
        st.subheader("📉 Drawdown Analysis")
        
        # Calculate drawdown from peak
        running_max = portfolio_history['Portfolio_Value'].expanding().max()
        drawdown = ((portfolio_history['Portfolio_Value'] - running_max) / running_max) * 100
        portfolio_history['Drawdown'] = drawdown
        
        fig_drawdown = go.Figure()
        
        fig_drawdown.add_trace(go.Scatter(
            x=portfolio_history['Date'],
            y=portfolio_history['Drawdown'],
            mode='lines',
            name='Drawdown from Peak',
            line=dict(color='red', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.1)'
        ))
        
        # Max drawdown
        max_drawdown = drawdown.min()
        max_drawdown_date = portfolio_history.loc[drawdown.idxmin(), 'Date']
        
        fig_drawdown.add_trace(go.Scatter(
            x=[max_drawdown_date],
            y=[max_drawdown],
            mode='markers',
            name=f'Max Drawdown ({max_drawdown:.2f}%)',
            marker=dict(color='darkred', size=12, symbol='x')
        ))
        
        fig_drawdown.update_layout(
            title=f'Drawdown from Peak (Max: {max_drawdown:.2f}%)',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_drawdown, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly/Period returns
        st.subheader("📅 Period-wise Returns")
        
        period = st.radio(
            "Select Period:",
            options=['Daily', 'Weekly', 'Monthly'],
            horizontal=True
        )
        
        period_returns = self.calculate_period_returns(portfolio_history, period)
        
        if not period_returns.empty:
            fig_period = go.Figure()
            
            colors_period = ['green' if x >= 0 else 'red' for x in period_returns['Return']]
            
            fig_period.add_trace(go.Bar(
                x=period_returns['Period'],
                y=period_returns['Return'],
                marker_color=colors_period,
                text=[f"{x:+.2f}%" for x in period_returns['Return']],
                textposition='auto'
            ))
            
            fig_period.update_layout(
                title=f'{period} Returns',
                xaxis_title='Period',
                yaxis_title='Return (%)',
                height=400
            )
            
            st.plotly_chart(fig_period, use_container_width=True)
            
            # Period statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_return = period_returns['Return'].mean()
                st.metric(
                    label=f"Average {period} Return",
                    value=f"{avg_return:+.2f}%"
                )
            
            with col2:
                positive_periods = len(period_returns[period_returns['Return'] > 0])
                total_periods = len(period_returns)
                win_rate = (positive_periods / total_periods * 100) if total_periods > 0 else 0
                st.metric(
                    label="Win Rate",
                    value=f"{win_rate:.1f}%",
                    delta=f"{positive_periods}/{total_periods} periods"
                )
            
            with col3:
                best_period = period_returns.loc[period_returns['Return'].idxmax()]
                st.metric(
                    label="Best Period",
                    value=f"{best_period['Return']:+.2f}%",
                    delta=str(best_period['Period'])
                )
        
        st.markdown("---")
        
        # Performance insights
        st.subheader("💡 Performance Insights")
        
        insights = self.generate_performance_insights(portfolio_history, total_return, max_drawdown, volatility)
        
        for insight in insights:
            if 'warning' in insight.lower() or 'high' in insight.lower() or 'concern' in insight.lower():
                st.warning(insight)
            elif 'excellent' in insight.lower() or 'strong' in insight.lower():
                st.success(insight)
            else:
                st.info(insight)
    
    def calculate_portfolio_history(self, portfolio_data, historical_data):
        """Calculate portfolio value over time"""
        
        # Find the common date range across all stocks
        all_dates = []
        
        for stock_name, hist_data in historical_data.items():
            if not hist_data.empty:
                all_dates.extend(hist_data.index.tolist())
        
        if not all_dates:
            return pd.DataFrame()
        
        # Create date range
        all_dates = sorted(set(all_dates))
        
        # Calculate portfolio value for each date
        portfolio_values = []
        investment_values = []
        
        for date in all_dates:
            total_value = 0
            total_investment = 0
            
            for _, stock in portfolio_data.iterrows():
                stock_name = stock['Stock Name']
                buy_date = pd.to_datetime(stock['Buy Date']).tz_localize(None)  # Make timezone-naive
                quantity = stock['Quantity']
                buy_price = stock['Buy Price']
                
                # Normalize date for comparison (remove timezone if present)
                compare_date = date.tz_localize(None) if hasattr(date, 'tz_localize') else date
                
                # Only include stock if we've bought it by this date
                if compare_date >= buy_date:
                    if stock_name in historical_data and not historical_data[stock_name].empty:
                        hist = historical_data[stock_name]
                        
                        # Get price on this date (or closest available)
                        available_dates = hist.index[hist.index <= date]
                        if len(available_dates) > 0:
                            closest_date = available_dates[-1]
                            price = hist.loc[closest_date, 'Close']
                            # Convert to scalar if Series
                            if isinstance(price, pd.Series):
                                price = float(price.iloc[0]) if len(price) > 0 else 0.0
                            else:
                                price = float(price) if not pd.isna(price) else 0.0
                            total_value += price * quantity
                            total_investment += buy_price * quantity
            
            if total_value > 0:  # Only add if we have data
                portfolio_values.append({
                    'Date': date,
                    'Portfolio_Value': total_value,
                    'Investment_Value': total_investment
                })
        
        if not portfolio_values:
            return pd.DataFrame()
        
        df = pd.DataFrame(portfolio_values)
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
    
    def calculate_period_returns(self, portfolio_history, period):
        """Calculate returns for specified period"""
        
        if portfolio_history.empty:
            return pd.DataFrame()
        
        df = portfolio_history.copy()
        df = df.set_index('Date')
        
        if period == 'Daily':
            df['Return'] = df['Portfolio_Value'].pct_change() * 100
            df = df.dropna()
            result = pd.DataFrame({
                'Period': df.index.strftime('%d %b %Y'),
                'Return': df['Return'].values
            })
        elif period == 'Weekly':
            weekly = df['Portfolio_Value'].resample('W').last()
            weekly_returns = weekly.pct_change() * 100
            weekly_returns = weekly_returns.dropna()
            result = pd.DataFrame({
                'Period': weekly_returns.index.strftime('Week of %d %b'),
                'Return': weekly_returns.values
            })
        else:  # Monthly
            monthly = df['Portfolio_Value'].resample('M').last()
            monthly_returns = monthly.pct_change() * 100
            monthly_returns = monthly_returns.dropna()
            result = pd.DataFrame({
                'Period': monthly_returns.index.strftime('%b %Y'),
                'Return': monthly_returns.values
            })
        
        return result.reset_index(drop=True)
    
    def generate_performance_insights(self, portfolio_history, total_return, max_drawdown, volatility):
        """Generate insights from performance data"""
        
        insights = []
        
        # Return insights
        if total_return > 30:
            insights.append(f"🚀 **Excellent Performance**: Portfolio has delivered strong returns of {total_return:.2f}%")
        elif total_return > 15:
            insights.append(f"✅ **Good Performance**: Portfolio shows healthy returns of {total_return:.2f}%")
        elif total_return > 0:
            insights.append(f"📊 **Positive Performance**: Portfolio has modest gains of {total_return:.2f}%")
        else:
            insights.append(f"📉 **Underperformance**: Portfolio is down {abs(total_return):.2f}%. Review holdings and strategy")
        
        # Drawdown insights
        if max_drawdown < -30:
            insights.append(f"⚠️ **High Drawdown Risk**: Maximum drawdown of {abs(max_drawdown):.2f}% indicates high volatility. Consider risk management")
        elif max_drawdown < -20:
            insights.append(f"📊 **Moderate Drawdown**: Maximum drawdown of {abs(max_drawdown):.2f}% is within acceptable range")
        else:
            insights.append(f"✅ **Low Drawdown**: Maximum drawdown of {abs(max_drawdown):.2f}% shows good downside protection")
        
        # Volatility insights
        if volatility > 30:
            insights.append(f"⚠️ **High Volatility**: Annualized volatility of {volatility:.2f}% suggests aggressive portfolio")
        elif volatility > 20:
            insights.append(f"📊 **Moderate Volatility**: {volatility:.2f}% volatility is typical for equity portfolios")
        else:
            insights.append(f"✅ **Low Volatility**: {volatility:.2f}% volatility indicates conservative portfolio")
        
        # Trend insights
        if not portfolio_history.empty and len(portfolio_history) > 30:
            recent_30d = portfolio_history.tail(30)
            recent_return = ((recent_30d['Portfolio_Value'].iloc[-1] - recent_30d['Portfolio_Value'].iloc[0]) / recent_30d['Portfolio_Value'].iloc[0]) * 100
            
            if recent_return > 5:
                insights.append(f"📈 **Positive Momentum**: Portfolio up {recent_return:.2f}% in last 30 days")
            elif recent_return < -5:
                insights.append(f"📉 **Negative Momentum**: Portfolio down {abs(recent_return):.2f}% in last 30 days")
        
        return insights
