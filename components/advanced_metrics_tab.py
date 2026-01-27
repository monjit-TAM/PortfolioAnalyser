import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_advanced_metrics_tab(advanced_metrics):
    if not advanced_metrics:
        st.warning("No advanced metrics available. Please analyze your portfolio first.")
        return
    
    st.markdown("### 📊 Advanced Portfolio Metrics")
    st.markdown("Select the metrics categories you want to explore:")
    
    metric_categories = [
        "Portfolio Health Score",
        "Risk Radar",
        "Structural Diagnostics",
        "Style Analysis",
        "Concentration Risk",
        "Volatility & Drawdown",
        "Behavior Analysis",
        "Drift Analysis",
        "Overlap Detection",
        "Return Attribution",
        "Liquidity Risk",
        "Tail Risk",
        "Tax Impact",
        "Macro Sensitivity",
        "Scenario Analysis"
    ]
    
    selected_categories = st.multiselect(
        "Select Metric Categories",
        metric_categories,
        default=["Portfolio Health Score", "Risk Radar", "Return Attribution"]
    )
    
    st.markdown("---")
    
    for category in selected_categories:
        if category == "Portfolio Health Score":
            render_health_score(advanced_metrics.get('health_score', {}))
        elif category == "Risk Radar":
            render_risk_radar(advanced_metrics)
        elif category == "Structural Diagnostics":
            render_structural_diagnostics(advanced_metrics.get('structural', {}))
        elif category == "Style Analysis":
            render_style_analysis(advanced_metrics.get('style', {}))
        elif category == "Concentration Risk":
            render_concentration_risk(advanced_metrics.get('concentration', {}))
        elif category == "Volatility & Drawdown":
            render_volatility_metrics(advanced_metrics.get('volatility', {}))
        elif category == "Behavior Analysis":
            render_behavior_score(advanced_metrics.get('behavior', {}))
        elif category == "Drift Analysis":
            render_drift_analysis(advanced_metrics.get('drift', {}))
        elif category == "Overlap Detection":
            render_overlap_detection(advanced_metrics.get('overlap', {}))
        elif category == "Return Attribution":
            render_return_attribution(advanced_metrics.get('attribution', {}))
        elif category == "Liquidity Risk":
            render_liquidity_risk(advanced_metrics.get('liquidity', {}))
        elif category == "Tail Risk":
            render_tail_risk(advanced_metrics.get('tail_risk', {}))
        elif category == "Tax Impact":
            render_tax_impact(advanced_metrics.get('tax_impact', {}))
        elif category == "Macro Sensitivity":
            render_macro_sensitivity(advanced_metrics.get('macro', {}))
        elif category == "Scenario Analysis":
            render_scenario_analysis(advanced_metrics.get('scenario', {}))

def render_health_score(health_data):
    st.markdown("## 🏥 Portfolio Health Score")
    
    if not health_data:
        st.info("Health score data not available")
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        overall_score = health_data.get('overall_score', 0)
        grade = health_data.get('grade', 'N/A')
        
        color = '#28a745' if overall_score >= 75 else ('#ffc107' if overall_score >= 50 else '#dc3545')
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={'text': f"Overall Score (Grade: {grade})"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 75], 'color': "#fef3c7"},
                    {'range': [75, 100], 'color': "#d1fae5"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Component Scores**")
        components = health_data.get('component_scores', {})
        for component, score in components.items():
            st.progress(score / 100, text=f"{component.replace('_', ' ').title()}: {score}")
    
    with col3:
        st.markdown("**Summary**")
        st.info(health_data.get('summary', 'No summary available'))
    
    st.markdown("---")

def render_risk_radar(advanced_metrics):
    """Render Risk Radar spider chart showing factor exposures"""
    st.markdown("## 🎯 Risk Radar - Factor Exposure Analysis")
    
    def normalize_score(value, min_val=0, max_val=100):
        """Ensure score is clamped between 0 and 100"""
        if value is None or pd.isna(value):
            return 50
        return max(0, min(100, float(value)))
    
    volatility = advanced_metrics.get('volatility', {})
    concentration = advanced_metrics.get('concentration', {})
    liquidity = advanced_metrics.get('liquidity', {})
    behavior = advanced_metrics.get('behavior', {})
    style = advanced_metrics.get('style', {})
    tail_risk = advanced_metrics.get('tail_risk', {})
    
    hist_vol = volatility.get('historical_volatility', 25)
    if hist_vol is None or pd.isna(hist_vol):
        hist_vol = 25
    volatility_score = normalize_score(100 - float(hist_vol) * 2)
    
    raw_concentration = concentration.get('concentration_score', 50)
    if raw_concentration is None or pd.isna(raw_concentration):
        raw_concentration = 50
    concentration_score = normalize_score(float(raw_concentration))
    
    raw_liquidity = liquidity.get('portfolio_liquidity_score', 70)
    if raw_liquidity is None or pd.isna(raw_liquidity):
        raw_liquidity = 70
    liquidity_score = normalize_score(float(raw_liquidity))
    
    raw_behavior = behavior.get('behavior_score', 60)
    if raw_behavior is None or pd.isna(raw_behavior):
        raw_behavior = 60
    behavior_score = normalize_score(float(raw_behavior))
    
    value_tilt = style.get('value_tilt', 50)
    if value_tilt is None or pd.isna(value_tilt):
        value_tilt = 50
    style_balance = normalize_score(100 - abs(50 - float(value_tilt)))
    
    raw_tail = tail_risk.get('tail_risk_score', 70)
    if raw_tail is None or pd.isna(raw_tail):
        raw_tail = 70
    tail_score = normalize_score(float(raw_tail))
    
    beta = volatility.get('portfolio_beta', 1.0)
    if beta is None or pd.isna(beta):
        beta = 1.0
    market_sensitivity = normalize_score(100 - abs(1 - float(beta)) * 50)
    
    categories = ['Volatility Control', 'Diversification', 'Liquidity', 
                  'Investment Discipline', 'Style Balance', 'Tail Risk Mgmt', 'Market Sensitivity']
    values = [volatility_score, concentration_score, liquidity_score, 
              behavior_score, style_balance, tail_score, market_sensitivity]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(99, 110, 250, 0.3)',
        line=dict(color='#636EFA', width=2),
        name='Your Portfolio'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[70, 70, 70, 70, 70, 70, 70, 70],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='#2ecc71', width=1, dash='dash'),
        name='Target (Good)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='',
                tickfont=dict(size=10)
            )
        ),
        showlegend=True,
        height=450,
        title="Risk Factor Exposure Radar"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Factor Scores:**")
        for cat, val in zip(categories, values):
            color = '#2ecc71' if val >= 70 else '#f39c12' if val >= 50 else '#e74c3c'
            icon = '🟢' if val >= 70 else '🟡' if val >= 50 else '🔴'
            st.markdown(f"{icon} **{cat}**: {val:.0f}/100")
    
    with col2:
        st.markdown("**💡 Key Insights:**")
        weak_factors = [(cat, val) for cat, val in zip(categories, values) if val < 60]
        strong_factors = [(cat, val) for cat, val in zip(categories, values) if val >= 80]
        
        if strong_factors:
            st.success(f"**Strengths**: {', '.join([f[0] for f in strong_factors])}")
        if weak_factors:
            st.warning(f"**Areas to improve**: {', '.join([f[0] for f in weak_factors])}")
        if not weak_factors and not strong_factors:
            st.info("Your portfolio shows balanced risk across all factors.")
    
    st.markdown("---")

def render_structural_diagnostics(structural_data):
    st.markdown("## 📊 Structural Diagnostics")
    
    if not structural_data:
        st.info("Structural data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Market Cap Allocation")
        market_cap = structural_data.get('market_cap_allocation', {})
        if market_cap:
            fig = px.pie(
                values=list(market_cap.values()),
                names=list(market_cap.keys()),
                title="Market Cap Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Sector Allocation")
        sectors = structural_data.get('sector_allocation', {})
        if sectors:
            sorted_sectors = dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:8])
            fig = px.bar(
                x=list(sorted_sectors.values()),
                y=list(sorted_sectors.keys()),
                orientation='h',
                title="Top Sectors by Allocation",
                color=list(sorted_sectors.values()),
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Industry Concentration")
        concentration = structural_data.get('industry_concentration', {})
        if concentration:
            st.metric("Top Sector", concentration.get('top_sector', 'N/A'))
            st.metric("Top Sector %", f"{concentration.get('top_sector_pct', 0):.1f}%")
            if concentration.get('is_concentrated'):
                st.warning("⚠️ High concentration in single sector")
    
    with col4:
        st.markdown("### Thematic Clusters")
        clusters = structural_data.get('thematic_clusters', [])
        for cluster in clusters:
            st.badge(cluster, icon="🏷️")
        
        st.metric("Total Stocks", structural_data.get('total_stocks', 0))
        st.metric("Total Value", f"₹{structural_data.get('total_value', 0):,.0f}")
    
    st.markdown("---")

def render_style_analysis(style_data):
    st.markdown("## 🎯 Style Analysis")
    
    if not style_data:
        st.info("Style data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        value_tilt = style_data.get('value_tilt', 50)
        growth_tilt = style_data.get('growth_tilt', 50)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Value', 'Growth'],
            y=[value_tilt, growth_tilt],
            marker_color=['#3b82f6', '#22c55e']
        ))
        fig.update_layout(
            title="Value vs Growth Tilt",
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Style Metrics")
        st.metric("Style Label", style_data.get('style_label', 'N/A'))
        st.metric("Momentum Exposure", f"{style_data.get('momentum_exposure', 0):.1f}%")
        st.metric("Quality Factor", style_data.get('quality_factor', 'N/A'))
    
    with col3:
        st.markdown("### Volatility Tilt")
        vol_tilt = style_data.get('volatility_tilt', 'Neutral')
        
        if vol_tilt == 'High-Beta':
            st.error(f"🔥 {vol_tilt}")
        elif vol_tilt == 'Low-Volatility':
            st.success(f"🛡️ {vol_tilt}")
        else:
            st.info(f"⚖️ {vol_tilt}")
    
    st.markdown("---")

def render_concentration_risk(concentration_data):
    st.markdown("## ⚠️ Concentration Risk")
    
    if not concentration_data:
        st.info("Concentration data not available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Top 1 Stock", f"{concentration_data.get('top1_exposure', 0):.1f}%")
    with col2:
        st.metric("Top 3 Stocks", f"{concentration_data.get('top3_exposure', 0):.1f}%")
    with col3:
        st.metric("Top 5 Stocks", f"{concentration_data.get('top5_exposure', 0):.1f}%")
    with col4:
        risk_level = concentration_data.get('risk_level', 'N/A')
        color = 'inverse' if risk_level == 'High' else ('off' if risk_level == 'Medium' else 'normal')
        st.metric("Risk Level", risk_level)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### Single Stock Flags")
        flags = concentration_data.get('single_stock_flags', [])
        if flags:
            for flag in flags:
                st.warning(f"⚠️ {flag['stock']}: {flag['percentage']:.1f}% (above 15% threshold)")
        else:
            st.success("✅ No single stock exceeds 15% threshold")
    
    with col6:
        st.markdown("### Sector Overexposure")
        sector_flags = concentration_data.get('sector_overexposure_flags', [])
        if sector_flags:
            for flag in sector_flags:
                st.warning(f"⚠️ {flag['sector']}: {flag['percentage']:.1f}% (above 30% threshold)")
        else:
            st.success("✅ No sector exceeds 30% threshold")
    
    score = concentration_data.get('concentration_score', 0)
    st.progress(score / 100, text=f"Concentration Score: {score}/100")
    
    st.markdown("---")

def render_volatility_metrics(volatility_data):
    st.markdown("## 📉 Volatility & Drawdown Metrics")
    
    if not volatility_data:
        st.info("Volatility data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Historical Volatility", f"{volatility_data.get('historical_volatility', 0):.1f}%")
        st.metric("Max Drawdown", f"{volatility_data.get('max_drawdown', 0):.1f}%")
    with col2:
        st.metric("Downside Deviation", f"{volatility_data.get('downside_deviation', 0):.1f}%")
        st.metric("Portfolio Beta", f"{volatility_data.get('portfolio_beta', 1.0):.2f}")
    with col3:
        sharpe = volatility_data.get('sharpe_ratio', 0)
        sortino = volatility_data.get('sortino_ratio', 0)
        st.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Risk-adjusted return vs risk-free rate")
        st.metric("Sortino Ratio", f"{sortino:.2f}", help="Risk-adjusted return vs downside risk")
    
    st.markdown("### Risk Classification")
    risk_class = volatility_data.get('risk_classification', 'Unknown')
    if risk_class == 'High Risk':
        st.error(f"🔴 {risk_class}")
    elif risk_class == 'Moderate Risk':
        st.warning(f"🟡 {risk_class}")
    else:
        st.success(f"🟢 {risk_class}")
    
    st.markdown("### Most Volatile Stocks")
    vol_stocks = volatility_data.get('stock_volatilities', [])
    if vol_stocks:
        df = pd.DataFrame(vol_stocks)
        df['volatility'] = df['volatility'].round(1)
        df['weight'] = (df['weight'] * 100).round(1)
        df.columns = ['Stock', 'Volatility (%)', 'Weight (%)']
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("---")

def render_behavior_score(behavior_data):
    st.markdown("## 🧠 Portfolio Behavior Pattern")
    
    if not behavior_data:
        st.info("Behavior data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pattern = behavior_data.get('behavior_pattern', 'Unknown')
        score = behavior_data.get('behavior_score', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': pattern},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#3b82f6'},
                'steps': [
                    {'range': [0, 40], 'color': "#fee2e2"},
                    {'range': [40, 70], 'color': "#fef3c7"},
                    {'range': [70, 100], 'color': "#d1fae5"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Avg Holding Period", f"{behavior_data.get('average_holding_days', 0):.0f} days")
        st.metric("Short-term Holdings", behavior_data.get('short_term_holdings', 0))
        st.metric("Long-term Holdings", behavior_data.get('long_term_holdings', 0))
    
    with col3:
        st.markdown("### Holding Distribution")
        dist = behavior_data.get('holding_distribution', {})
        for period, count in dist.items():
            st.write(f"**{period}:** {count} stocks")
        
        if behavior_data.get('overtrading_detected'):
            st.warning("⚠️ Overtrading pattern detected")
    
    st.markdown("---")

def render_drift_analysis(drift_data):
    st.markdown("## 📍 Benchmark Drift Analysis")
    
    if not drift_data:
        st.info("Drift data not available")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        alignment = drift_data.get('alignment_score', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=alignment,
            title={'text': "Alignment Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#22c55e'},
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 75], 'color': "#fef3c7"},
                    {'range': [75, 100], 'color': "#d1fae5"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"Benchmark: {drift_data.get('benchmark_used', 'Nifty 50')}")
        st.caption(f"Deviation Level: {drift_data.get('deviation_level', 'Unknown')}")
    
    with col2:
        st.markdown("### Sector Drifts from Benchmark")
        drifts = drift_data.get('sector_drifts', [])
        if drifts:
            df = pd.DataFrame(drifts)
            df.columns = ['Sector', 'Portfolio %', 'Benchmark %', 'Drift']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Portfolio',
                x=df['Sector'],
                y=df['Portfolio %'],
                marker_color='#3b82f6'
            ))
            fig.add_trace(go.Bar(
                name='Benchmark',
                x=df['Sector'],
                y=df['Benchmark %'],
                marker_color='#94a3b8'
            ))
            fig.update_layout(
                barmode='group',
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ Portfolio closely aligned with benchmark")
    
    st.markdown("---")

def render_overlap_detection(overlap_data):
    st.markdown("## 🔍 Overlap Detection")
    
    if not overlap_data:
        st.info("Overlap data not available")
        return
    
    overlaps = overlap_data.get('overlaps', [])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overlap Groups", overlap_data.get('total_overlap_groups', 0))
    with col2:
        st.metric("Overlap Risk", overlap_data.get('overlap_risk', 'Low'))
    with col3:
        has_overlaps = overlap_data.get('has_significant_overlaps', False)
        if has_overlaps:
            st.warning("⚠️ Significant overlaps detected")
        else:
            st.success("✅ No significant overlaps")
    
    if overlaps:
        st.markdown("### Detected Overlaps")
        for overlap in overlaps:
            with st.expander(f"🏢 {overlap['group']} ({overlap['count']} stocks)"):
                stocks = overlap.get('stocks', [])
                for stock in stocks:
                    if isinstance(stock, dict):
                        st.write(f"• {stock.get('stock', 'Unknown')}")
                    else:
                        st.write(f"• {stock}")
    
    st.markdown("---")

def render_return_attribution(attribution_data):
    st.markdown("## 💰 Return Attribution")
    
    if not attribution_data:
        st.info("Attribution data not available")
        return
    
    total_gain = attribution_data.get('total_portfolio_gain', 0)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color = "normal" if total_gain >= 0 else "inverse"
        st.metric("Total Portfolio Gain/Loss", f"₹{total_gain:,.0f}")
    with col2:
        st.metric("Gainers", attribution_data.get('gainers_count', 0))
    with col3:
        st.metric("Losers", attribution_data.get('losers_count', 0))
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("### Top Contributors (Gainers)")
        top = attribution_data.get('top_contributors', [])
        if top:
            df = pd.DataFrame(top)
            df['absolute_contribution'] = df['absolute_contribution'].apply(lambda x: f"₹{x:,.0f}")
            df['contribution_pct'] = df['contribution_pct'].apply(lambda x: f"{x:.1f}%")
            df.columns = ['Stock', 'Contribution', 'Share']
            st.dataframe(df, hide_index=True, use_container_width=True)
    
    with col5:
        st.markdown("### Bottom Contributors (Losers)")
        bottom = attribution_data.get('bottom_contributors', [])
        if bottom:
            df = pd.DataFrame(bottom)
            df['absolute_contribution'] = df['absolute_contribution'].apply(lambda x: f"₹{x:,.0f}")
            df['contribution_pct'] = df['contribution_pct'].apply(lambda x: f"{x:.1f}%")
            df.columns = ['Stock', 'Contribution', 'Share']
            st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("### Sector Attribution")
    sector_attr = attribution_data.get('sector_attribution', {})
    if sector_attr:
        sectors = list(sector_attr.keys())
        values = [v['absolute'] for v in sector_attr.values()]
        
        fig = go.Figure(go.Bar(
            x=values,
            y=sectors,
            orientation='h',
            marker_color=['#22c55e' if v >= 0 else '#ef4444' for v in values]
        ))
        fig.update_layout(
            title="Sector Contribution to Returns",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

def render_liquidity_risk(liquidity_data):
    st.markdown("## 🔎 Liquidity Risk")
    
    if not liquidity_data:
        st.info("Liquidity data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = liquidity_data.get('portfolio_liquidity_score', 0)
        st.metric("Liquidity Score", f"{score}/100")
    with col2:
        st.metric("Illiquid Positions", liquidity_data.get('illiquid_count', 0))
    with col3:
        risk = liquidity_data.get('liquidity_risk', 'Low')
        if risk == 'High':
            st.error(f"🔴 {risk} Risk")
        elif risk == 'Moderate':
            st.warning(f"🟡 {risk} Risk")
        else:
            st.success(f"🟢 {risk} Risk")
    
    illiquid = liquidity_data.get('illiquid_positions', [])
    if illiquid:
        st.markdown("### Illiquid Positions")
        df = pd.DataFrame(illiquid)
        df = df[['stock', 'position_value', 'days_to_liquidate', 'liquidity_grade']]
        df['position_value'] = df['position_value'].apply(lambda x: f"₹{x:,.0f}")
        df.columns = ['Stock', 'Value', 'Days to Liquidate', 'Grade']
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("---")

def render_tail_risk(tail_data):
    st.markdown("## 💣 Tail Risk Exposure")
    
    if not tail_data:
        st.info("Tail risk data not available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("High Volatility Exposure", f"{tail_data.get('high_vol_exposure_pct', 0):.1f}%")
    with col2:
        st.metric("Small Cap Exposure", f"{tail_data.get('small_cap_exposure_pct', 0):.1f}%")
    with col3:
        st.metric("Tail Risk Score", f"{tail_data.get('tail_risk_score', 0)}/100")
    with col4:
        level = tail_data.get('tail_risk_level', 'Low')
        if level == 'High':
            st.error(f"🔴 {level}")
        elif level == 'Moderate':
            st.warning(f"🟡 {level}")
        else:
            st.success(f"🟢 {level}")
    
    high_vol = tail_data.get('high_volatility_stocks', [])
    if high_vol:
        st.markdown("### High Volatility Stocks (>40% annual volatility)")
        df = pd.DataFrame(high_vol)
        df['value'] = df['value'].apply(lambda x: f"₹{x:,.0f}")
        df.columns = ['Stock', 'Volatility %', 'Value']
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("---")

def render_tax_impact(tax_data):
    st.markdown("## 💰 Tax Impact Analysis")
    
    if not tax_data:
        st.info("Tax impact data not available")
        return
    
    st.info(tax_data.get('tax_note', 'Tax calculations are estimates based on current Indian tax laws.'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Short-term Gains", f"₹{tax_data.get('short_term_gains', 0):,.0f}")
        st.metric("Short-term Losses", f"₹{tax_data.get('short_term_losses', 0):,.0f}")
    
    with col2:
        st.metric("Long-term Gains", f"₹{tax_data.get('long_term_gains', 0):,.0f}")
        st.metric("Long-term Losses", f"₹{tax_data.get('long_term_losses', 0):,.0f}")
    
    with col3:
        st.metric("Est. STCG Tax (15%)", f"₹{tax_data.get('estimated_stcg_tax', 0):,.0f}")
        st.metric("Est. LTCG Tax (10%)", f"₹{tax_data.get('estimated_ltcg_tax', 0):,.0f}")
    
    with col4:
        total_tax = tax_data.get('total_estimated_tax', 0)
        st.metric("Total Estimated Tax", f"₹{total_tax:,.0f}")
        remaining_exemption = tax_data.get('ltcg_exemption_remaining', 100000)
        if remaining_exemption > 0:
            st.success(f"LTCG Exemption Remaining: ₹{remaining_exemption:,.0f}")
        else:
            st.warning("LTCG Exemption: Fully Used")
    
    stock_breakdown = tax_data.get('stock_breakdown', [])
    if stock_breakdown:
        st.markdown("### Stock-wise Tax Classification")
        
        stcg_stocks = [s for s in stock_breakdown if s['tax_implication'] == 'STCG']
        ltcg_stocks = [s for s in stock_breakdown if s['tax_implication'] == 'LTCG']
        loss_stocks = [s for s in stock_breakdown if s['tax_implication'] == 'Loss']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if stcg_stocks:
                st.markdown("#### 📊 Short-term Capital Gains (STCG)")
                df_stcg = pd.DataFrame(stcg_stocks)
                df_stcg['gain_loss'] = df_stcg['gain_loss'].apply(lambda x: f"₹{x:,.0f}")
                df_stcg = df_stcg[['stock', 'gain_loss', 'holding_days']]
                df_stcg.columns = ['Stock', 'Gain', 'Days Held']
                st.dataframe(df_stcg, hide_index=True, use_container_width=True)
            
            if ltcg_stocks:
                st.markdown("#### 📈 Long-term Capital Gains (LTCG)")
                df_ltcg = pd.DataFrame(ltcg_stocks)
                df_ltcg['gain_loss'] = df_ltcg['gain_loss'].apply(lambda x: f"₹{x:,.0f}")
                df_ltcg = df_ltcg[['stock', 'gain_loss', 'holding_days']]
                df_ltcg.columns = ['Stock', 'Gain', 'Days Held']
                st.dataframe(df_ltcg, hide_index=True, use_container_width=True)
        
        with col2:
            if loss_stocks:
                st.markdown("#### 📉 Capital Losses")
                df_loss = pd.DataFrame(loss_stocks)
                df_loss['gain_loss'] = df_loss['gain_loss'].apply(lambda x: f"₹{x:,.0f}")
                df_loss = df_loss[['stock', 'gain_loss', 'holding_days', 'term']]
                df_loss.columns = ['Stock', 'Loss', 'Days Held', 'Term']
                st.dataframe(df_loss, hide_index=True, use_container_width=True)
            
            st.markdown("#### ℹ️ Tax Harvest Tips")
            if stcg_stocks:
                st.info(f"Consider holding {len(stcg_stocks)} stocks for 365+ days to qualify for lower LTCG rates.")
            if loss_stocks:
                st.info("Consider tax-loss harvesting to offset gains before year-end.")
    
    st.markdown("---")

def render_macro_sensitivity(macro_data):
    st.markdown("## 🌍 Macro Sensitivity")
    
    if not macro_data:
        st.info("Macro sensitivity data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Interest Rate Sensitivity")
        rate_data = macro_data.get('interest_rate_sensitivity', {})
        st.metric("Banking Exposure", f"{rate_data.get('banking_exposure_pct', 0):.1f}%")
        st.metric("NBFC Exposure", f"{rate_data.get('nbfc_exposure_pct', 0):.1f}%")
        st.metric("Total Rate-Sensitive", f"{rate_data.get('total_rate_sensitive_pct', 0):.1f}%")
        if rate_data.get('sensitivity_flag'):
            st.warning("⚠️ High interest rate sensitivity")
    
    with col2:
        st.markdown("### Commodity Exposure")
        commodity = macro_data.get('commodity_exposure', {})
        st.metric("Crude Sensitive", f"{commodity.get('crude_sensitive_pct', 0):.1f}%")
        st.metric("Metals Exposure", f"{commodity.get('metals_exposure_pct', 0):.1f}%")
    
    with col3:
        st.markdown("### Currency Exposure")
        currency = macro_data.get('currency_exposure', {})
        st.metric("Export Oriented", f"{currency.get('export_oriented_pct', 0):.1f}%")
        sensitivity = currency.get('inr_sensitivity', 'Low')
        if sensitivity == 'High':
            st.warning(f"⚠️ {sensitivity} INR Sensitivity")
        else:
            st.success(f"✅ {sensitivity} INR Sensitivity")
    
    st.markdown("---")

def render_scenario_analysis(scenario_data):
    st.markdown("## 🔥 Scenario Analysis (Stress Testing)")
    
    if not scenario_data:
        st.info("Scenario data not available")
        return
    
    st.caption(scenario_data.get('stress_test_note', ''))
    
    scenarios = scenario_data.get('scenarios', [])
    current_value = scenario_data.get('current_portfolio_value', 0)
    
    if scenarios:
        cols = st.columns(len(scenarios))
        
        for i, scenario in enumerate(scenarios):
            with cols[i]:
                st.markdown(f"### {scenario['scenario']}")
                impact = scenario['projected_portfolio_impact_pct']
                loss = scenario['projected_loss_amount']
                
                if impact < 0:
                    st.error(f"📉 {impact:.1f}%")
                    st.metric("Projected Loss", f"₹{abs(loss):,.0f}")
                else:
                    st.success(f"📈 +{impact:.1f}%")
                    st.metric("Projected Gain", f"₹{loss:,.0f}")
    
    st.markdown("---")
