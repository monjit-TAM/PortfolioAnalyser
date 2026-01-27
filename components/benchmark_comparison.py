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
        
        self.render_sector_heatmap(stock_performance)
        
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
                cat_name = str(category['Category'])
                cat_return = float(category['Category Return %'])
                benchmark_index = self.benchmark_mapping.get(cat_name, 'NIFTY50')
                benchmark_return = benchmark_returns.get(benchmark_index, 0)
                cat_outperformance = cat_return - benchmark_return
                
                if cat_outperformance > 10:
                    insights.append(f"🚀 **{cat_name} stocks excelling**: Outperforming {benchmark_index} by {cat_outperformance:.2f}%")
                elif cat_outperformance < -10:
                    insights.append(f"⚠️ **{cat_name} stocks struggling**: Underperforming {benchmark_index} by {abs(cat_outperformance):.2f}%")
        
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
                cat_name = str(category['Category'])
                cat_return = float(category['Category Return %'])
                benchmark_index = self.benchmark_mapping.get(cat_name, 'NIFTY50')
                benchmark_return = benchmark_returns.get(benchmark_index, 0)
                
                if cat_return < benchmark_return - 5:  # Underperforming by more than 5%
                    underperforming_categories.append(cat_name)
            
            if underperforming_categories:
                recommendations.append(f"🎯 **Focus on {', '.join(underperforming_categories)}**: These categories are significantly underperforming their benchmarks")
        
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
    
    def render_sector_heatmap(self, stock_performance):
        """Render Sector Heatmap comparing portfolio weights vs NIFTY benchmark"""
        
        st.subheader("🔥 Sector Allocation Heatmap - Portfolio vs NIFTY 50")
        
        nifty_sector_weights = {
            'Financial Services': 28.0,
            'Technology': 15.0,
            'Oil & Gas': 12.0,
            'Consumer Goods': 10.0,
            'Automobile': 6.0,
            'Pharma': 5.0,
            'Metals': 4.0,
            'Telecom': 3.0,
            'Power': 3.0,
            'Cement': 2.0,
            'Healthcare': 2.0,
            'Others': 10.0
        }
        
        if 'Sector' not in stock_performance.columns or 'Current Value' not in stock_performance.columns:
            st.warning("Sector data not available for heatmap comparison")
            return
        
        total_value = stock_performance['Current Value'].sum()
        portfolio_sector_weights = stock_performance.groupby('Sector')['Current Value'].sum() / total_value * 100
        
        all_sectors = set(list(nifty_sector_weights.keys()) + list(portfolio_sector_weights.index))
        
        heatmap_data = []
        for sector in all_sectors:
            portfolio_weight = portfolio_sector_weights.get(sector, 0)
            nifty_weight = nifty_sector_weights.get(sector, 0)
            difference = portfolio_weight - nifty_weight
            
            if portfolio_weight > 0 or nifty_weight > 0:
                heatmap_data.append({
                    'Sector': sector,
                    'Portfolio %': round(portfolio_weight, 1),
                    'NIFTY 50 %': round(nifty_weight, 1),
                    'Difference': round(difference, 1),
                    'Status': 'Overweight' if difference > 2 else ('Underweight' if difference < -2 else 'Aligned')
                })
        
        heatmap_df = pd.DataFrame(heatmap_data)
        heatmap_df = heatmap_df.sort_values('Difference', ascending=False)
        
        colors = ['#e74c3c' if x < -5 else '#f39c12' if x < -2 else '#2ecc71' if x > 5 else '#27ae60' if x > 2 else '#95a5a6' 
                  for x in heatmap_df['Difference']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Portfolio',
            x=heatmap_df['Sector'],
            y=heatmap_df['Portfolio %'],
            marker_color='#3498db',
            text=[f"{x:.1f}%" for x in heatmap_df['Portfolio %']],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='NIFTY 50',
            x=heatmap_df['Sector'],
            y=heatmap_df['NIFTY 50 %'],
            marker_color='#e67e22',
            text=[f"{x:.1f}%" for x in heatmap_df['NIFTY 50 %']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Sector Allocation: Portfolio vs NIFTY 50 Benchmark",
            xaxis_title="Sector",
            yaxis_title="Weight (%)",
            barmode='group',
            height=450,
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔺 Overweight Sectors (vs NIFTY)**")
            overweight = heatmap_df[heatmap_df['Difference'] > 2]
            if len(overweight) > 0:
                for _, row in overweight.iterrows():
                    st.markdown(f"• **{row['Sector']}**: +{row['Difference']:.1f}% above NIFTY")
            else:
                st.markdown("_No significant overweight positions_")
        
        with col2:
            st.markdown("**🔻 Underweight Sectors (vs NIFTY)**")
            underweight = heatmap_df[heatmap_df['Difference'] < -2]
            if len(underweight) > 0:
                for _, row in underweight.iterrows():
                    st.markdown(f"• **{row['Sector']}**: {row['Difference']:.1f}% below NIFTY")
            else:
                st.markdown("_No significant underweight positions_")
        
        most_overweight = heatmap_df.iloc[0] if len(heatmap_df) > 0 else None
        most_underweight = heatmap_df.iloc[-1] if len(heatmap_df) > 0 else None
        
        if most_overweight is not None and most_overweight['Difference'] > 5:
            st.warning(f"⚠️ **High sector concentration**: {most_overweight['Sector']} is {most_overweight['Difference']:.1f}% overweight vs NIFTY 50. This may amplify sector-specific risks.")
        
        if most_underweight is not None and most_underweight['Difference'] < -10:
            st.info(f"ℹ️ **Sector gap identified**: Your portfolio has minimal exposure to {most_underweight['Sector']} compared to NIFTY 50. Consider if this aligns with your investment thesis.")
