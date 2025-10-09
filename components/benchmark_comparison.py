import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher

class BenchmarkComparison:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        
        # Benchmark mapping based on stock categories
        self.benchmark_mapping = {
            'Large Cap': 'NIFTY50',
            'Mid Cap': 'NIFTY_MIDCAP_100',
            'Small Cap': 'NIFTY_SMALLCAP_100'
        }
    
    def render(self, analysis_results, portfolio_data):
        """Render benchmark comparison analysis"""
        
        st.header("📊 Benchmark Comparison")
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
        if stock_performance.empty:
            st.warning("No stock performance data available.")
            return
        
        # Portfolio vs Benchmark Overview
        st.subheader("🎯 Portfolio vs Market Indices")
        
        # Calculate portfolio-level benchmark comparison
        portfolio_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        
        # Get benchmark data for comparison
        benchmark_returns = self.get_benchmark_returns(stock_performance)
        
        # Display benchmark comparison cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Portfolio Return",
                value=f"{portfolio_return:+.2f}%",
                delta=None
            )
        
        with col2:
            nifty50_return = benchmark_returns.get('NIFTY50', 0)
            portfolio_vs_nifty50 = portfolio_return - nifty50_return
            st.metric(
                label="NIFTY 50 Return",
                value=f"{nifty50_return:+.2f}%",
                delta=f"{portfolio_vs_nifty50:+.2f}% vs Portfolio"
            )
        
        with col3:
            midcap_return = benchmark_returns.get('NIFTY_MIDCAP_100', 0)
            portfolio_vs_midcap = portfolio_return - midcap_return
            st.metric(
                label="NIFTY Midcap 100",
                value=f"{midcap_return:+.2f}%",
                delta=f"{portfolio_vs_midcap:+.2f}% vs Portfolio"
            )
        
        with col4:
            smallcap_return = benchmark_returns.get('NIFTY_SMALLCAP_100', 0)
            portfolio_vs_smallcap = portfolio_return - smallcap_return
            st.metric(
                label="NIFTY Smallcap 100",
                value=f"{smallcap_return:+.2f}%",
                delta=f"{portfolio_vs_smallcap:+.2f}% vs Portfolio"
            )
        
        st.markdown("---")
        
        # Category-wise Benchmark Comparison
        st.subheader("📈 Category-wise Benchmark Analysis")
        
        category_analysis = pd.DataFrame(analysis_results['category_analysis'])
        
        if not category_analysis.empty:
            # Create comparison chart
            categories = category_analysis['Category'].tolist()
            portfolio_returns = category_analysis['Category Return %'].tolist()
            benchmark_returns_list = []
            
            for category in categories:
                benchmark_index = self.benchmark_mapping.get(category, 'NIFTY50')
                benchmark_return = benchmark_returns.get(benchmark_index, 0)
                benchmark_returns_list.append(benchmark_return)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Portfolio Performance',
                x=categories,
                y=portfolio_returns,
                marker_color='lightblue',
                text=[f"{x:+.2f}%" for x in portfolio_returns],
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Benchmark Performance',
                x=categories,
                y=benchmark_returns_list,
                marker_color='orange',
                text=[f"{x:+.2f}%" for x in benchmark_returns_list],
                textposition='auto'
            ))
            
            fig.update_layout(
                title='Portfolio vs Benchmark Returns by Category',
                xaxis_title='Stock Category',
                yaxis_title='Return (%)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis table
            comparison_df = pd.DataFrame({
                'Category': categories,
                'Portfolio Return %': portfolio_returns,
                'Benchmark Return %': benchmark_returns_list,
                'Outperformance': [p - b for p, b in zip(portfolio_returns, benchmark_returns_list)],
                'Benchmark Index': [self.benchmark_mapping.get(cat, 'NIFTY50') for cat in categories]
            })
            
            # Format for display
            display_df = comparison_df.copy()
            for col in ['Portfolio Return %', 'Benchmark Return %', 'Outperformance']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(display_df, use_container_width=True)
        
        st.markdown("---")
        
        # Individual Stock Benchmark Comparison
        st.subheader("🔍 Individual Stock vs Benchmark")
        
        # Select stock for detailed comparison
        selected_stock = st.selectbox(
            "Select stock for benchmark comparison:",
            options=stock_performance['Stock Name'].tolist()
        )
        
        stock_data = stock_performance[stock_performance['Stock Name'] == selected_stock].iloc[0]
        stock_category = stock_data['Category']
        benchmark_index = self.benchmark_mapping.get(stock_category, 'NIFTY50')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 {selected_stock} Performance")
            
            stock_return = stock_data['Percentage Gain/Loss']
            benchmark_return = benchmark_returns.get(benchmark_index, 0)
            outperformance = stock_return - benchmark_return
            
            st.metric(
                label="Stock Return",
                value=f"{stock_return:+.2f}%",
                delta=f"{outperformance:+.2f}% vs {benchmark_index}"
            )
            
            performance_data = {
                "Stock": stock_data['Stock Name'],
                "Category": stock_category,
                "Benchmark": benchmark_index,
                "Buy Price": f"₹{stock_data['Buy Price']:.2f}",
                "Current Price": f"₹{stock_data['Current Price']:.2f}",
                "Stock Return": f"{stock_return:+.2f}%",
                "Benchmark Return": f"{benchmark_return:+.2f}%",
                "Outperformance": f"{outperformance:+.2f}%"
            }
            
            for key, value in performance_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("📈 Performance Comparison Chart")
            
            # Create comparison chart for individual stock
            fig_stock = go.Figure()
            
            categories_stock = [selected_stock, benchmark_index]
            returns_stock = [stock_return, benchmark_return]
            colors = ['green' if stock_return >= benchmark_return else 'red', 'blue']
            
            fig_stock.add_trace(go.Bar(
                x=categories_stock,
                y=returns_stock,
                marker_color=colors,
                text=[f"{x:+.2f}%" for x in returns_stock],
                textposition='auto'
            ))
            
            fig_stock.update_layout(
                title=f'{selected_stock} vs {benchmark_index}',
                yaxis_title='Return (%)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_stock, use_container_width=True)
        
        st.markdown("---")
        
        # Performance Insights
        st.subheader("💡 Benchmark Analysis Insights")
        
        # Calculate overall portfolio performance vs benchmarks
        insights = []
        
        portfolio_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        
        # Compare with each benchmark
        for benchmark_name, benchmark_return in benchmark_returns.items():
            outperformance = portfolio_return - benchmark_return
            
            if outperformance > 5:
                insights.append(f"🎯 **Strong outperformance vs {benchmark_name}**: Portfolio beat the index by {outperformance:.2f}%")
            elif outperformance > 0:
                insights.append(f"✅ **Modest outperformance vs {benchmark_name}**: Portfolio ahead by {outperformance:.2f}%")
            elif outperformance > -5:
                insights.append(f"📊 **Close to {benchmark_name}**: Portfolio trailing by {abs(outperformance):.2f}%")
            else:
                insights.append(f"📉 **Underperformance vs {benchmark_name}**: Portfolio behind by {abs(outperformance):.2f}%")
        
        # Category-specific insights
        if not category_analysis.empty:
            for _, category in category_analysis.iterrows():
                cat_name = category['Category']
                cat_return = category['Category Return %']
                benchmark_index = self.benchmark_mapping.get(cat_name, 'NIFTY50')
                benchmark_return = benchmark_returns.get(benchmark_index, 0)
                cat_outperformance = cat_return - benchmark_return
                
                if cat_outperformance > 10:
                    insights.append(f"🚀 **{cat_name} stocks excelling**: Outperforming {benchmark_index} by {cat_outperformance:.2f}%")
                elif cat_outperformance < -10:
                    insights.append(f"⚠️ **{cat_name} stocks struggling**: Underperforming {benchmark_index} by {abs(cat_outperformance):.2f}%")
        
        # Risk-adjusted performance
        portfolio_volatility = analysis_results['risk_metrics']['portfolio_volatility']
        sharpe_ratio = analysis_results['risk_metrics']['sharpe_ratio']
        
        if sharpe_ratio > 1:
            insights.append(f"✨ **Excellent risk-adjusted returns**: Sharpe ratio of {sharpe_ratio:.2f} indicates strong performance per unit of risk")
        elif sharpe_ratio > 0.5:
            insights.append(f"👍 **Good risk-adjusted returns**: Sharpe ratio of {sharpe_ratio:.2f} shows decent risk compensation")
        elif sharpe_ratio > 0:
            insights.append(f"📊 **Moderate risk-adjusted returns**: Sharpe ratio of {sharpe_ratio:.2f} suggests room for improvement")
        else:
            insights.append(f"⚠️ **Poor risk-adjusted returns**: Negative Sharpe ratio of {sharpe_ratio:.2f} indicates inadequate compensation for risk taken")
        
        for insight in insights:
            st.markdown(insight)
        
        # Recommendations based on benchmark analysis
        st.markdown("---")
        st.subheader("📋 Benchmark-Based Recommendations")
        
        recommendations = []
        
        # Overall portfolio recommendations
        if portfolio_return > max(benchmark_returns.values(), default=0):
            recommendations.append("✅ **Continue current strategy**: Your portfolio is outperforming major indices")
        elif portfolio_return < min(benchmark_returns.values(), default=0):
            recommendations.append("🔄 **Review strategy**: Consider index investing or strategy revision as portfolio is underperforming")
        
        # Category-specific recommendations
        if not category_analysis.empty:
            underperforming_categories = []
            for _, category in category_analysis.iterrows():
                cat_name = category['Category']
                cat_return = category['Category Return %']
                benchmark_index = self.benchmark_mapping.get(cat_name, 'NIFTY50')
                benchmark_return = benchmark_returns.get(benchmark_index, 0)
                
                if cat_return < benchmark_return - 5:  # Underperforming by more than 5%
                    underperforming_categories.append(cat_name)
            
            if underperforming_categories:
                recommendations.append(f"🎯 **Focus on {', '.join(underperforming_categories)}**: These categories are significantly underperforming their benchmarks")
        
        # Risk-based recommendations
        if portfolio_volatility > 0.25:  # High volatility
            recommendations.append("⚖️ **Consider risk management**: High portfolio volatility suggests need for diversification or position sizing review")
        
        for rec in recommendations:
            st.markdown(rec)
    
    def get_benchmark_returns(self, stock_performance):
        """Calculate benchmark returns for comparison"""
        benchmark_returns = {}
        
        # Get earliest buy date for benchmark comparison period
        earliest_date = pd.to_datetime(stock_performance['Buy Date']).min()
        
        for benchmark_name, benchmark_symbol in self.data_fetcher.indices.items():
            try:
                # Fetch benchmark data
                benchmark_data = self.data_fetcher.get_index_data(benchmark_name, earliest_date)
                
                if not benchmark_data.empty:
                    start_price = benchmark_data['Close'].iloc[0]
                    end_price = benchmark_data['Close'].iloc[-1]
                    benchmark_return = ((end_price - start_price) / start_price) * 100
                    benchmark_returns[benchmark_name] = benchmark_return
                else:
                    # Fallback dummy data for demonstration
                    if benchmark_name == 'NIFTY50':
                        benchmark_returns[benchmark_name] = 12.5  # Typical NIFTY return
                    elif benchmark_name == 'NIFTY_MIDCAP_100':
                        benchmark_returns[benchmark_name] = 15.2
                    else:
                        benchmark_returns[benchmark_name] = 18.7
                        
            except Exception as e:
                st.warning(f"Could not fetch {benchmark_name} data: {str(e)}")
                # Use fallback data
                if benchmark_name == 'NIFTY50':
                    benchmark_returns[benchmark_name] = 12.5
                elif benchmark_name == 'NIFTY_MIDCAP_100':
                    benchmark_returns[benchmark_name] = 15.2
                else:
                    benchmark_returns[benchmark_name] = 18.7
        
        return benchmark_returns
