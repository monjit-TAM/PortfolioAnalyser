import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CustomerProfile:
    def render(self, analysis_results, portfolio_data, recommendations):
        """Render customer profile and investment style analysis"""
        
        st.header("👤 Customer Investment Profile")
        
        # Portfolio Summary Overview
        st.subheader("📊 Portfolio Overview")
        
        summary = analysis_results['portfolio_summary']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Portfolio Size",
                value=f"₹{summary['current_value']:,.2f}",
                help="Total current value of portfolio"
            )
            
            # Portfolio size category
            portfolio_size = summary['current_value']
            if portfolio_size >= 10000000:  # 1 Crore+
                size_category = "High Net Worth"
                size_color = "green"
            elif portfolio_size >= 2500000:  # 25 Lakh+
                size_category = "Affluent Investor"
                size_color = "blue"
            elif portfolio_size >= 500000:  # 5 Lakh+
                size_category = "Moderate Investor"
                size_color = "orange"
            else:
                size_category = "Emerging Investor"
                size_color = "gray"
            
            st.markdown(f"**Category:** <span style='color:{size_color}'>{size_category}</span>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.metric(
                label="Investment Experience",
                value=f"{summary['number_of_stocks']} stocks",
                help="Number of different stocks in portfolio"
            )
            
            # Experience level based on number of stocks and diversification
            num_stocks = summary['number_of_stocks']
            if num_stocks >= 15:
                experience_level = "Experienced"
                exp_color = "green"
            elif num_stocks >= 8:
                experience_level = "Intermediate"
                exp_color = "blue"
            elif num_stocks >= 4:
                experience_level = "Beginner+"
                exp_color = "orange"
            else:
                experience_level = "Beginner"
                exp_color = "red"
            
            st.markdown(f"**Level:** <span style='color:{exp_color}'>{experience_level}</span>", 
                       unsafe_allow_html=True)
        
        with col3:
            overall_return = summary['total_gain_loss_percentage']
            st.metric(
                label="Performance Track Record",
                value=f"{overall_return:+.2f}%",
                help="Overall portfolio return"
            )
            
            # Performance category
            if overall_return > 25:
                perf_category = "Excellent"
                perf_color = "green"
            elif overall_return > 10:
                perf_category = "Good"
                perf_color = "blue"
            elif overall_return > 0:
                perf_category = "Positive"
                perf_color = "lightgreen"
            elif overall_return > -10:
                perf_category = "Moderate Loss"
                perf_color = "orange"
            else:
                perf_category = "High Loss"
                perf_color = "red"
            
            st.markdown(f"**Status:** <span style='color:{perf_color}'>{perf_category}</span>", 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Investment Style Analysis
        st.subheader("🎯 Investment Style Analysis")
        
        # Analyze investment style based on recommendations and portfolio composition
        style_analysis = self.analyze_investment_style(analysis_results, recommendations)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Style Preference")
            
            # Create style preference chart
            style_scores = style_analysis['style_scores']
            
            fig_style = go.Figure(data=[
                go.Bar(
                    x=list(style_scores.keys()),
                    y=list(style_scores.values()),
                    marker_color=['lightblue', 'lightgreen', 'orange', 'red'],
                    text=[f"{v:.1f}" for v in style_scores.values()],
                    textposition='auto'
                )
            ])
            
            fig_style.update_layout(
                title="Investment Style Preferences",
                yaxis_title="Style Score",
                height=400
            )
            
            st.plotly_chart(fig_style, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Risk Profile")
            
            risk_profile = self.assess_risk_profile(analysis_results, style_analysis)
            
            # Risk assessment display
            st.write(f"**Risk Tolerance:** {risk_profile['risk_tolerance']}")
            st.write(f"**Risk Level:** {risk_profile['risk_level']}")
            st.write(f"**Diversification:** {risk_profile['diversification_status']}")
            
            # Risk factors
            st.write("**Key Risk Factors:**")
            for factor in risk_profile['risk_factors']:
                st.write(f"• {factor}")
            
            # Risk score visualization
            risk_score = risk_profile['risk_score']
            risk_color = 'red' if risk_score > 70 else 'orange' if risk_score > 40 else 'green'
            
            st.markdown(f"**Overall Risk Score:** <span style='color:{risk_color}; font-size:24px'>{risk_score}/100</span>", 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sector and Category Preferences
        st.subheader("🏭 Investment Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Sector Allocation Preference")
            
            sector_data = pd.DataFrame(analysis_results['sector_analysis'])
            if not sector_data.empty:
                # Create sector preference chart
                fig_sector = px.pie(
                    sector_data,
                    values='Percentage of Portfolio',
                    names='Sector',
                    title="Current Sector Preferences"
                )
                fig_sector.update_traces(textposition='inside', textinfo='percent+label')
                fig_sector.update_layout(height=300)
                st.plotly_chart(fig_sector, use_container_width=True)
                
                # Top sector preferences
                top_sectors = sector_data.nlargest(3, 'Percentage of Portfolio')
                st.write("**Preferred Sectors:**")
                for _, sector in top_sectors.iterrows():
                    st.write(f"• {sector['Sector']}: {sector['Percentage of Portfolio']:.1f}%")
        
        with col2:
            st.write("#### Market Cap Preference")
            
            category_data = pd.DataFrame(analysis_results['category_analysis'])
            if not category_data.empty:
                # Create category preference chart
                fig_category = px.pie(
                    category_data,
                    values='Percentage of Portfolio',
                    names='Category',
                    title="Market Cap Allocation"
                )
                fig_category.update_traces(textposition='inside', textinfo='percent+label')
                fig_category.update_layout(height=300)
                st.plotly_chart(fig_category, use_container_width=True)
                
                # Determine market cap preference
                max_category = category_data.loc[category_data['Percentage of Portfolio'].idxmax()]
                st.write("**Primary Preference:**")
                st.write(f"• {max_category['Category']}: {max_category['Percentage of Portfolio']:.1f}%")
                
                cap_preference = self.determine_cap_preference(category_data)
                st.write(f"**Investment Style:** {cap_preference}")
        
        st.markdown("---")
        
        # Investment Behavior Analysis
        st.subheader("🧠 Investment Behavior Profile")
        
        behavior_analysis = self.analyze_investment_behavior(analysis_results, recommendations)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("#### Decision Making Style")
            decision_style = behavior_analysis['decision_style']
            style_color = {
                'Conservative': 'blue',
                'Moderate': 'orange',
                'Aggressive': 'red',
                'Balanced': 'green'
            }.get(decision_style, 'gray')
            
            st.markdown(f"**Style:** <span style='color:{style_color}; font-weight:bold'>{decision_style}</span>", 
                       unsafe_allow_html=True)
            
            st.write("**Characteristics:**")
            for char in behavior_analysis['decision_characteristics']:
                st.write(f"• {char}")
        
        with col2:
            st.write("#### Performance Orientation")
            
            perf_orientation = behavior_analysis['performance_orientation']
            st.write(f"**Focus:** {perf_orientation}")
            
            st.write("**Indicators:**")
            for indicator in behavior_analysis['performance_indicators']:
                st.write(f"• {indicator}")
        
        with col3:
            st.write("#### Investment Horizon")
            
            investment_horizon = behavior_analysis['investment_horizon']
            horizon_color = {
                'Short-term': 'red',
                'Medium-term': 'orange',
                'Long-term': 'green',
                'Mixed': 'blue'
            }.get(investment_horizon, 'gray')
            
            st.markdown(f"**Horizon:** <span style='color:{horizon_color}; font-weight:bold'>{investment_horizon}</span>", 
                       unsafe_allow_html=True)
            
            st.write("**Time Preferences:**")
            for pref in behavior_analysis['time_preferences']:
                st.write(f"• {pref}")
        
        st.markdown("---")
        
        # Personalized Recommendations
        st.subheader("🎯 Personalized Investment Strategy")
        
        strategy_recommendations = self.generate_strategy_recommendations(
            analysis_results, style_analysis, risk_profile, behavior_analysis
        )
        
        for rec_type, recommendations_list in strategy_recommendations.items():
            st.write(f"#### {rec_type}")
            for rec in recommendations_list:
                st.markdown(f"• {rec}")
        
        st.markdown("---")
        
        # Portfolio Health Score
        st.subheader("💚 Portfolio Health Score")
        
        health_score = self.calculate_portfolio_health_score(analysis_results, risk_profile)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Health score gauge
            health_color = 'green' if health_score >= 80 else 'orange' if health_score >= 60 else 'red'
            
            st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="color: {health_color}; font-size: 48px;">{health_score}/100</h1>
                <p style="font-size: 18px;">Portfolio Health Score</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Health category
            if health_score >= 80:
                health_status = "Excellent"
                health_emoji = "🟢"
            elif health_score >= 60:
                health_status = "Good"
                health_emoji = "🟡"
            else:
                health_status = "Needs Improvement"
                health_emoji = "🔴"
            
            st.markdown(f"**Status:** {health_emoji} {health_status}")
        
        with col2:
            st.write("**Health Factors Contributing to Score:**")
            
            health_factors = [
                f"Diversification: {min(analysis_results['portfolio_summary']['number_of_stocks'] * 5, 25)}/25 points",
                f"Performance: {min(max(analysis_results['portfolio_summary']['total_gain_loss_percentage'], 0) * 2, 25)}/25 points",
                f"Risk Management: {min(max(100 - risk_profile['risk_score'], 0) * 0.25, 25)}/25 points",
                f"Sector Balance: {min(len(analysis_results['sector_analysis']) * 3, 25)}/25 points"
            ]
            
            for factor in health_factors:
                st.write(f"• {factor}")
            
            st.write("**Improvement Areas:**")
            improvement_areas = []
            
            if analysis_results['portfolio_summary']['number_of_stocks'] < 10:
                improvement_areas.append("Increase portfolio diversification")
            
            if analysis_results['portfolio_summary']['total_gain_loss_percentage'] < 0:
                improvement_areas.append("Focus on performance improvement")
            
            if risk_profile['risk_score'] > 70:
                improvement_areas.append("Implement better risk management")
            
            if len(analysis_results['sector_analysis']) < 5:
                improvement_areas.append("Improve sector diversification")
            
            if improvement_areas:
                for area in improvement_areas:
                    st.write(f"• {area}")
            else:
                st.success("✅ Portfolio is well-balanced across key metrics")
    
    def analyze_investment_style(self, analysis_results, recommendations):
        """Analyze investment style based on portfolio composition and recommendations"""
        
        style_scores = {
            'Value Investor': 0,
            'Growth Investor': 0,
            'Balanced Investor': 0,
            'Speculative Investor': 0
        }
        
        # Analyze based on recommendations
        value_signals = sum(1 for rec in recommendations if rec['value_analysis']['recommendation'] == 'BUY')
        growth_signals = sum(1 for rec in recommendations if rec['growth_analysis']['recommendation'] == 'BUY')
        total_stocks = len(recommendations)
        
        if total_stocks > 0:
            # Value score
            style_scores['Value Investor'] = float((value_signals / total_stocks) * 100)
            
            # Growth score
            style_scores['Growth Investor'] = float((growth_signals / total_stocks) * 100)
            
            # Balanced score (based on diversification and mixed signals)
            sector_count = len(analysis_results['sector_analysis'])
            diversification_score = min(sector_count * 10, 50)  # Max 50 for 5+ sectors
            mixed_signals = abs(value_signals - growth_signals)
            balance_score = diversification_score + (mixed_signals * 10)
            style_scores['Balanced Investor'] = float(min(balance_score, 100))
            
            # Speculative score (based on performance volatility)
            performance_variance = abs(analysis_results['portfolio_summary']['total_gain_loss_percentage'])
            speculative_score = min(performance_variance * 1.5, 100)  # Simplified without volatility
            style_scores['Speculative Investor'] = float(speculative_score)
        
        return {
            'style_scores': style_scores,
            'primary_style': max(style_scores.items(), key=lambda x: x[1])[0],
            'style_confidence': max(style_scores.values())
        }
    
    def assess_risk_profile(self, analysis_results, style_analysis):
        """Assess investor's risk profile"""
        
        risk_factors = []
        risk_score = 0
        
        # Portfolio concentration risk (calculate from portfolio data)
        portfolio_df = pd.DataFrame(analysis_results['stock_performance'])
        if not portfolio_df.empty:
            total_value = portfolio_df['Current Value'].sum()
            max_stock_weight = portfolio_df['Current Value'].max() / total_value if total_value > 0 else 0
            if max_stock_weight > 0.3:  # More than 30% in one stock
                risk_factors.append(f"High concentration: {max_stock_weight*100:.1f}% in single stock")
                risk_score += 20
        
        # Sector concentration
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        if not sector_data.empty:
            max_sector_allocation = sector_data['Percentage of Portfolio'].max()
            if max_sector_allocation > 40:
                risk_factors.append(f"Sector concentration: {max_sector_allocation:.1f}% in one sector")
                risk_score += 15
        
        # Note: Volatility assessment removed as advanced risk metrics are no longer calculated
        
        # Number of stocks (diversification)
        num_stocks = analysis_results['portfolio_summary']['number_of_stocks']
        if num_stocks < 5:
            risk_factors.append(f"Limited diversification: Only {num_stocks} stocks")
            risk_score += 25
        
        # Performance volatility
        total_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        if abs(total_return) > 30:  # High absolute returns (positive or negative)
            risk_factors.append(f"High performance volatility: {total_return:+.1f}%")
            risk_score += 10
        
        # Determine risk tolerance and level
        if risk_score <= 20:
            risk_tolerance = "Conservative"
            risk_level = "Low Risk"
        elif risk_score <= 40:
            risk_tolerance = "Moderate"
            risk_level = "Medium Risk"
        elif risk_score <= 60:
            risk_tolerance = "Aggressive"
            risk_level = "High Risk"
        else:
            risk_tolerance = "Very Aggressive"
            risk_level = "Very High Risk"
        
        # Diversification status
        if num_stocks >= 15:
            diversification_status = "Well Diversified"
        elif num_stocks >= 8:
            diversification_status = "Adequately Diversified"
        elif num_stocks >= 4:
            diversification_status = "Moderately Diversified"
        else:
            diversification_status = "Under Diversified"
        
        return {
            'risk_score': min(risk_score, 100),
            'risk_tolerance': risk_tolerance,
            'risk_level': risk_level,
            'diversification_status': diversification_status,
            'risk_factors': risk_factors if risk_factors else ["Well-managed risk profile"]
        }
    
    def determine_cap_preference(self, category_data):
        """Determine market cap preference based on allocation"""
        
        large_cap_pct = category_data[category_data['Category'] == 'Large Cap']['Percentage of Portfolio'].sum()
        mid_cap_pct = category_data[category_data['Category'] == 'Mid Cap']['Percentage of Portfolio'].sum()
        small_cap_pct = category_data[category_data['Category'] == 'Small Cap']['Percentage of Portfolio'].sum()
        
        if large_cap_pct > 60:
            return "Conservative (Large Cap Focus)"
        elif small_cap_pct > 40:
            return "Aggressive (Small Cap Focus)"
        elif mid_cap_pct > 40:
            return "Growth-Oriented (Mid Cap Focus)"
        elif large_cap_pct > 40 and mid_cap_pct > 20:
            return "Balanced Conservative"
        elif mid_cap_pct > 30 and small_cap_pct > 20:
            return "Balanced Aggressive"
        else:
            return "Well Balanced"
    
    def analyze_investment_behavior(self, analysis_results, recommendations):
        """Analyze investment behavior patterns"""
        
        # Decision making style
        profitable_stocks = analysis_results['portfolio_summary']['profitable_stocks']
        total_stocks = analysis_results['portfolio_summary']['number_of_stocks']
        success_rate = profitable_stocks / total_stocks if total_stocks > 0 else 0
        
        avg_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        
        if success_rate > 0.7 and avg_return > 0 and avg_return < 15:
            decision_style = "Conservative"
            decision_characteristics = ["Risk-averse", "Steady performance", "Stable returns preference"]
        elif success_rate > 0.5 and abs(avg_return) < 20:
            decision_style = "Moderate"
            decision_characteristics = ["Balanced approach", "Moderate risk tolerance", "Diversified thinking"]
        elif abs(avg_return) > 30:
            decision_style = "Aggressive"
            decision_characteristics = ["High risk tolerance", "Growth-focused", "Performance-driven"]
        else:
            decision_style = "Balanced"
            decision_characteristics = ["Mixed approach", "Adaptive strategy", "Risk-aware"]
        
        # Performance orientation
        if avg_return > 15:
            performance_orientation = "Growth-focused"
            performance_indicators = ["Above-average returns", "Growth stock preference", "Performance-driven decisions"]
        elif avg_return > 0:
            performance_orientation = "Income & Growth"
            performance_indicators = ["Positive returns", "Balanced approach", "Steady growth preference"]
        elif avg_return > -10:
            performance_orientation = "Capital Preservation"
            performance_indicators = ["Conservative approach", "Loss minimization", "Stability-focused"]
        else:
            performance_orientation = "Recovery-focused"
            performance_indicators = ["Loss recovery mode", "Portfolio restructuring needed", "Risk reassessment required"]
        
        # Investment horizon (simplified analysis)
        sector_diversity = len(analysis_results['sector_analysis'])
        stock_diversity = total_stocks
        
        if stock_diversity >= 10 and sector_diversity >= 6:
            investment_horizon = "Long-term"
            time_preferences = ["Patient investing", "Diversification focus", "Compound growth strategy"]
        elif stock_diversity >= 5 and sector_diversity >= 3:
            investment_horizon = "Medium-term"
            time_preferences = ["Balanced time horizon", "Moderate diversification", "Growth with stability"]
        elif abs(avg_return) > 30:
            investment_horizon = "Short-term"
            time_preferences = ["Quick returns focus", "High performance acceptance", "Active trading mindset"]
        else:
            investment_horizon = "Mixed"
            time_preferences = ["Flexible time horizon", "Adaptive strategy", "Opportunity-based decisions"]
        
        return {
            'decision_style': decision_style,
            'decision_characteristics': decision_characteristics,
            'performance_orientation': performance_orientation,
            'performance_indicators': performance_indicators,
            'investment_horizon': investment_horizon,
            'time_preferences': time_preferences
        }
    
    def generate_strategy_recommendations(self, analysis_results, style_analysis, risk_profile, behavior_analysis):
        """Generate personalized strategy recommendations"""
        
        recommendations = {
            "🎯 Portfolio Strategy": [],
            "⚖️ Risk Management": [],
            "📈 Performance Enhancement": [],
            "🔄 Rebalancing Actions": []
        }
        
        # Portfolio Strategy
        primary_style = style_analysis['primary_style']
        
        if primary_style == "Value Investor":
            recommendations["🎯 Portfolio Strategy"].append(
                "Focus on undervalued stocks with strong fundamentals and low P/E ratios"
            )
            recommendations["🎯 Portfolio Strategy"].append(
                "Consider dividend-paying stocks for steady income"
            )
        elif primary_style == "Growth Investor":
            recommendations["🎯 Portfolio Strategy"].append(
                "Target companies with high revenue and earnings growth potential"
            )
            recommendations["🎯 Portfolio Strategy"].append(
                "Focus on sectors with strong growth prospects"
            )
        elif primary_style == "Balanced Investor":
            recommendations["🎯 Portfolio Strategy"].append(
                "Maintain balanced allocation between value and growth stocks"
            )
            recommendations["🎯 Portfolio Strategy"].append(
                "Regular rebalancing to maintain desired asset allocation"
            )
        
        # Risk Management
        risk_score = risk_profile['risk_score']
        
        if risk_score > 60:
            recommendations["⚖️ Risk Management"].append(
                "Immediate diversification needed to reduce concentration risk"
            )
            recommendations["⚖️ Risk Management"].append(
                "Consider reducing position sizes in high-risk holdings"
            )
        
        num_stocks = analysis_results['portfolio_summary']['number_of_stocks']
        if num_stocks < 8:
            recommendations["⚖️ Risk Management"].append(
                f"Increase diversification - add {8 - num_stocks} more stocks from different sectors"
            )
        
        # Performance Enhancement
        avg_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        
        if avg_return < 0:
            recommendations["📈 Performance Enhancement"].append(
                "Review underperforming stocks for potential exit opportunities"
            )
            recommendations["📈 Performance Enhancement"].append(
                "Focus on fundamental analysis before adding new positions"
            )
        
        profitable_ratio = (analysis_results['portfolio_summary']['profitable_stocks'] / 
                           analysis_results['portfolio_summary']['number_of_stocks'])
        
        if profitable_ratio < 0.5:
            recommendations["📈 Performance Enhancement"].append(
                "Improve stock selection process with better research and analysis"
            )
        
        # Rebalancing Actions
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        if not sector_data.empty:
            max_sector_allocation = sector_data['Percentage of Portfolio'].max()
            if max_sector_allocation > 35:
                max_sector = sector_data.loc[sector_data['Percentage of Portfolio'].idxmax(), 'Sector']
                recommendations["🔄 Rebalancing Actions"].append(
                    f"Reduce exposure to {max_sector} sector (currently {max_sector_allocation:.1f}%)"
                )
        
        # Behavior-based recommendations
        if behavior_analysis['decision_style'] == "Aggressive" and risk_score > 70:
            recommendations["⚖️ Risk Management"].append(
                "Your aggressive style needs better risk controls - implement stop-losses"
            )
        
        if behavior_analysis['investment_horizon'] == "Short-term" and avg_return < 10:
            recommendations["🎯 Portfolio Strategy"].append(
                "Consider shifting to longer-term investment horizon for better returns"
            )
        
        return recommendations
    
    def calculate_portfolio_health_score(self, analysis_results, risk_profile):
        """Calculate overall portfolio health score"""
        
        score = 0
        
        # Diversification (25 points)
        num_stocks = analysis_results['portfolio_summary']['number_of_stocks']
        diversification_score = min(num_stocks * 2.5, 25)  # Max 25 points for 10+ stocks
        score += diversification_score
        
        # Performance (25 points)
        performance = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        performance_score = min(max(performance * 1.25, 0), 25)  # Max 25 points for 20%+ returns
        score += performance_score
        
        # Risk Management (25 points)
        risk_management_score = min(max(100 - risk_profile['risk_score'], 0) * 0.25, 25)
        score += risk_management_score
        
        # Sector Balance (25 points)
        sector_count = len(analysis_results['sector_analysis'])
        sector_balance_score = min(sector_count * 5, 25)  # Max 25 points for 5+ sectors
        score += sector_balance_score
        
        return int(score)
