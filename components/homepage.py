import streamlit as st
import pandas as pd

def render_modern_homepage(authenticated, show_login_callback, show_signup_callback, analyze_callback):
    """Render modern, portfoliosmith-style homepage design"""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .main-container {
            font-family: 'Inter', sans-serif;
        }
        
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            padding: 80px 40px;
            margin: 0 auto 60px auto;
            max-width: 1200px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 40px;
        }
        
        .hero-text {
            flex: 1;
            min-width: 300px;
            max-width: 550px;
        }
        
        .hero-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 20px;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 800;
            color: white;
            line-height: 1.15;
            margin-bottom: 24px;
            letter-spacing: -1px;
        }
        
        .hero-subtitle {
            font-size: 18px;
            color: rgba(255,255,255,0.9);
            line-height: 1.7;
            margin-bottom: 32px;
        }
        
        .hero-btn {
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            border: none;
        }
        
        .hero-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .hero-image {
            flex: 1;
            min-width: 300px;
            text-align: center;
        }
        
        .hero-image img {
            max-width: 100%;
            height: auto;
            filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));
        }
        
        .stats-row {
            display: flex;
            gap: 40px;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            color: white;
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 800;
        }
        
        .stat-label {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .section-header {
            text-align: center;
            max-width: 700px;
            margin: 0 auto 50px auto;
            padding: 0 20px;
        }
        
        .section-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        
        .section-title {
            font-size: 40px;
            font-weight: 800;
            color: #1a1a2e;
            line-height: 1.2;
            margin-bottom: 16px;
        }
        
        .section-subtitle {
            font-size: 18px;
            color: #666;
            line-height: 1.6;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .feature-card {
            background: #fff;
            border: 1px solid #eef2f7;
            border-radius: 20px;
            padding: 32px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
            border-color: #667eea;
        }
        
        .feature-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #f5f7ff 0%, #eef2ff 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 24px;
            font-size: 28px;
        }
        
        .feature-title {
            font-size: 20px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 12px;
        }
        
        .feature-desc {
            font-size: 15px;
            color: #666;
            line-height: 1.7;
        }
        
        .steps-section {
            background: linear-gradient(180deg, #f8faff 0%, #fff 100%);
            padding: 80px 20px;
            margin: 60px 0;
            border-radius: 24px;
        }
        
        .steps-container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 30px;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .step-card {
            flex: 1;
            min-width: 200px;
            max-width: 280px;
            text-align: center;
            position: relative;
        }
        
        .step-number-circle {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 24px;
            margin: 0 auto 20px auto;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .step-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .step-title {
            font-size: 18px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 10px;
        }
        
        .step-desc {
            font-size: 14px;
            color: #888;
            line-height: 1.6;
        }
        
        .step-arrow {
            color: #667eea;
            font-size: 24px;
            margin-top: 30px;
        }
        
        .insights-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            max-width: 1200px;
            margin: 60px auto;
            padding: 0 20px;
            align-items: center;
        }
        
        @media (max-width: 768px) {
            .insights-section {
                grid-template-columns: 1fr;
            }
        }
        
        .insight-content {
            padding: 20px;
        }
        
        .insight-tag {
            display: inline-block;
            background: #f0f4ff;
            color: #667eea;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        
        .insight-title {
            font-size: 32px;
            font-weight: 800;
            color: #1a1a2e;
            line-height: 1.25;
            margin-bottom: 16px;
        }
        
        .insight-desc {
            font-size: 16px;
            color: #666;
            line-height: 1.7;
            margin-bottom: 24px;
        }
        
        .insight-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .insight-list li {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            font-size: 15px;
            color: #444;
        }
        
        .insight-check {
            width: 24px;
            height: 24px;
            background: #e8f5e9;
            color: #4caf50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        
        .insight-image {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            padding: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
        }
        
        .insight-visual {
            background: white;
            border-radius: 16px;
            padding: 30px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        
        .cta-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            padding: 80px 40px;
            text-align: center;
            max-width: 1000px;
            margin: 60px auto;
        }
        
        .cta-title {
            font-size: 36px;
            font-weight: 800;
            color: white;
            margin-bottom: 16px;
        }
        
        .cta-subtitle {
            font-size: 18px;
            color: rgba(255,255,255,0.9);
            margin-bottom: 32px;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .footer-section {
            text-align: center;
            padding: 40px 20px;
            color: #888;
            font-size: 14px;
            border-top: 1px solid #eee;
            margin-top: 60px;
        }
        
        .footer-brand {
            font-size: 24px;
            font-weight: 800;
            color: #1a1a2e;
            margin-bottom: 8px;
        }
        
        .footer-tagline {
            color: #666;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-text">
                <span class="hero-badge">🚀 Professional Portfolio Intelligence</span>
                <h1 class="hero-title">Make Informed<br>Investing Decisions</h1>
                <p class="hero-subtitle">
                    Evaluate your portfolio performance with our smart, user-friendly analysis tool. 
                    Get actionable insights, risk analysis, and expert recommendations to achieve your financial goals.
                </p>
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-number">10+</div>
                        <div class="stat-label">Analysis Layers</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">50+</div>
                        <div class="stat-label">Metrics Tracked</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">Real-time</div>
                        <div class="stat-label">Market Data</div>
                    </div>
                </div>
            </div>
            <div class="hero-image">
                <div style="background: rgba(255,255,255,0.15); border-radius: 24px; padding: 40px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="width: 8px; height: 50px; background: #10b981; border-radius: 4px;"></div>
                            <div style="width: 8px; height: 80px; background: #3b82f6; border-radius: 4px;"></div>
                            <div style="width: 8px; height: 35px; background: #ef4444; border-radius: 4px;"></div>
                            <div style="width: 8px; height: 65px; background: #f59e0b; border-radius: 4px;"></div>
                            <div style="width: 8px; height: 45px; background: #8b5cf6; border-radius: 4px;"></div>
                        </div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 14px; text-align: center;">Portfolio Performance</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        if authenticated:
            if st.button("Go to Dashboard →", type="primary", use_container_width=True, key="hero_dashboard"):
                pass
        else:
            if st.button("Generate Insights →", type="primary", use_container_width=True, key="hero_start"):
                show_signup_callback()
    
    return None


def render_features_section():
    """Render the features section with modern cards using Streamlit columns"""
    
    st.markdown("""
    <div style="text-align: center; max-width: 700px; margin: 60px auto 50px auto; padding: 0 20px;">
        <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
            Why Choose Alphalens
        </div>
        <h2 style="font-size: 36px; font-weight: 800; color: #1a1a2e; line-height: 1.2; margin-bottom: 16px;">
            A Smart Tool To Optimize Your Investment Strategy
        </h2>
        <p style="font-size: 18px; color: #666; line-height: 1.6;">
            A quick scan detects any mistakes in your Stock Selection, 
            Behavioral Biases, and Capital Allocations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">📈</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Performance Analytics</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Track your portfolio's performance with detailed metrics including returns, 
                volatility, Sharpe ratio, and benchmark comparisons against NIFTY 50.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">🎯</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Risk Assessment</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Understand your risk exposure with concentration analysis, sector allocation, 
                and tail risk metrics to build a more resilient portfolio.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">🧠</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Behavioral Insights</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Identify behavioral biases affecting your investment decisions and get 
                personalized recommendations to overcome them.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">💡</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Expert Recommendations</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Receive data-driven BUY, HOLD, or SELL recommendations based on 
                Value and Growth investing frameworks.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">⚖️</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Portfolio Rebalancing</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Get intelligent suggestions to rebalance your portfolio based on your 
                risk tolerance and investment goals.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 32px; min-height: 220px;">
            <div style="font-size: 40px; margin-bottom: 16px;">💰</div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px;">Tax Impact Analysis</div>
            <div style="font-size: 15px; color: #666; line-height: 1.7;">
                Understand the tax implications of your holdings with STCG/LTCG 
                classification and estimated tax liability calculations.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_insights_section():
    """Render the insights alternating section using Streamlit columns"""
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="padding: 20px;">
            <span style="display: inline-block; background: #f0f4ff; color: #667eea; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 16px;">📊 Post-Analysis</span>
            <h3 style="font-size: 32px; font-weight: 800; color: #1a1a2e; line-height: 1.25; margin-bottom: 16px;">Automate Your Portfolio Review</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.7; margin-bottom: 24px;">
                A post-analysis of your investments is important as you look to refine 
                and update your trading strategies. Now you can streamline your analysis 
                and correct mistakes in your strategy.
            </p>
            <div style="font-size: 15px; color: #444;">
                <p style="margin: 10px 0;">✅ Track historical performance over time</p>
                <p style="margin: 10px 0;">✅ Identify winning and losing patterns</p>
                <p style="margin: 10px 0;">✅ Measure sector-wise contributions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 24px; padding: 50px; display: flex; align-items: center; justify-content: center; min-height: 260px;">
            <div style="text-align: center;">
                <div style="font-size: 72px; margin-bottom: 12px;">📈</div>
                <div style="color: rgba(255,255,255,0.95); font-size: 18px; font-weight: 600;">Performance Charts</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 24px; padding: 50px; display: flex; align-items: center; justify-content: center; min-height: 260px;">
            <div style="text-align: center;">
                <div style="font-size: 72px; margin-bottom: 12px;">🎯</div>
                <div style="color: rgba(255,255,255,0.95); font-size: 18px; font-weight: 600;">Risk Radar Analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="padding: 20px;">
            <span style="display: inline-block; background: #ecfdf5; color: #059669; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 16px;">🧠 Behavioral</span>
            <h3 style="font-size: 32px; font-weight: 800; color: #1a1a2e; line-height: 1.25; margin-bottom: 16px;">Know Your Investment Biases</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.7; margin-bottom: 24px;">
                Behavioral biases can lead to suboptimal decisions and eat away your returns. 
                With us, you get to know your biases and minimize their effects on your portfolio.
            </p>
            <div style="font-size: 15px; color: #444;">
                <p style="margin: 10px 0;">✅ Concentration bias detection</p>
                <p style="margin: 10px 0;">✅ Loss aversion analysis</p>
                <p style="margin: 10px 0;">✅ Recency bias identification</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("""
        <div style="padding: 20px;">
            <span style="display: inline-block; background: #fef3c7; color: #d97706; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 16px;">💡 Actionable</span>
            <h3 style="font-size: 32px; font-weight: 800; color: #1a1a2e; line-height: 1.25; margin-bottom: 16px;">Get Precise Investment Guidance</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.7; margin-bottom: 24px;">
                Our advanced algorithms diagnose your portfolio and provide solutions 
                to the problems. You also get precise guidance on What, When and How Much 
                to buy, sell or hold.
            </p>
            <div style="font-size: 15px; color: #444;">
                <p style="margin: 10px 0;">✅ Value & Growth perspectives</p>
                <p style="margin: 10px 0;">✅ Alternative stock suggestions</p>
                <p style="margin: 10px 0;">✅ Rebalancing recommendations</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 24px; padding: 50px; display: flex; align-items: center; justify-content: center; min-height: 260px;">
            <div style="text-align: center;">
                <div style="font-size: 72px; margin-bottom: 12px;">💡</div>
                <div style="color: rgba(255,255,255,0.95); font-size: 18px; font-weight: 600;">Expert Recommendations</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_how_it_works_section():
    """Render the how it works section with steps using Streamlit columns"""
    
    st.markdown("""
    <div style="background: linear-gradient(180deg, #f8faff 0%, #fff 100%); padding: 60px 20px; margin: 40px 0; border-radius: 24px;">
        <div style="text-align: center; max-width: 700px; margin: 0 auto 50px auto;">
            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
                How It Works
            </div>
            <h2 style="font-size: 36px; font-weight: 800; color: #1a1a2e; line-height: 1.2; margin-bottom: 16px;">
                It's Simple and Easy to Use
            </h2>
            <p style="font-size: 18px; color: #666; line-height: 1.6;">
                Get started in minutes with just 3 simple steps
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                font-weight: 800; font-size: 24px; margin: 0 auto 20px auto; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);">1</div>
            <div style="font-size: 48px; margin-bottom: 16px;">📤</div>
            <div style="font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 10px;">Upload Portfolio</div>
            <div style="font-size: 14px; color: #888; line-height: 1.6;">
                Upload your portfolio CSV file with stock names, buy prices, 
                dates, and quantities
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                font-weight: 800; font-size: 24px; margin: 0 auto 20px auto; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);">2</div>
            <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
            <div style="font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 10px;">Instant Analysis</div>
            <div style="font-size: 14px; color: #888; line-height: 1.6;">
                Our engine fetches live prices and runs 10+ layers of 
                comprehensive analysis
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                font-weight: 800; font-size: 24px; margin: 0 auto 20px auto; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);">3</div>
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <div style="font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 10px;">Get Insights</div>
            <div style="font-size: 14px; color: #888; line-height: 1.6;">
                View detailed reports, recommendations, and download 
                comprehensive PDF reports
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_methodology_section():
    """Render the methodology section showing analysis frameworks"""
    
    st.markdown("""
    <div style="text-align: center; max-width: 800px; margin: 60px auto 40px auto; padding: 0 20px;">
        <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
            Our Methodology
        </div>
        <h2 style="font-size: 36px; font-weight: 800; color: #1a1a2e; line-height: 1.2; margin-bottom: 16px;">
            Comprehensive Investment Analysis Framework
        </h2>
        <p style="font-size: 18px; color: #666; line-height: 1.6;">
            Our analysis combines Value Investing principles from Benjamin Graham and Warren Buffett 
            with Growth Investing methodologies using quantitative financial data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 28px; text-align: center;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
                <span style="font-size: 28px;">📊</span>
            </div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px;">Value Investing Framework</div>
            <div style="font-size: 14px; color: #666; line-height: 1.9; text-align: left;">
                <p style="margin: 6px 0;">• P/E Ratio Analysis (vs Industry & Historical)</p>
                <p style="margin: 6px 0;">• Price-to-Book Value Assessment</p>
                <p style="margin: 6px 0;">• Dividend Yield Evaluation</p>
                <p style="margin: 6px 0;">• Debt-to-Equity Ratio Check</p>
                <p style="margin: 6px 0;">• Margin of Safety Calculation</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 28px; text-align: center;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
                <span style="font-size: 28px;">🚀</span>
            </div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px;">Growth Investing Framework</div>
            <div style="font-size: 14px; color: #666; line-height: 1.9; text-align: left;">
                <p style="margin: 6px 0;">• Revenue Growth Rate Analysis</p>
                <p style="margin: 6px 0;">• EPS Growth Trajectory</p>
                <p style="margin: 6px 0;">• Price Momentum (52-week performance)</p>
                <p style="margin: 6px 0;">• Relative Strength vs Benchmark</p>
                <p style="margin: 6px 0;">• PEG Ratio Evaluation</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 28px; text-align: center;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
                <span style="font-size: 28px;">🎯</span>
            </div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px;">Recommendation Logic</div>
            <div style="font-size: 14px; color: #666; line-height: 1.9; text-align: left;">
                <p style="margin: 6px 0;">• Combined Value + Growth Scores</p>
                <p style="margin: 6px 0;">• BUY/HOLD/SELL Signal Generation</p>
                <p style="margin: 6px 0;">• Sector-Relative Comparison</p>
                <p style="margin: 6px 0;">• Risk-Adjusted Recommendations</p>
                <p style="margin: 6px 0;">• Alternative Stock Suggestions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 28px; text-align: center;">
            <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
                <span style="font-size: 28px;">⚖️</span>
            </div>
            <div style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px;">Rebalancing Strategy</div>
            <div style="font-size: 14px; color: #666; line-height: 1.9; text-align: left;">
                <p style="margin: 6px 0;">• Sector Allocation Optimization</p>
                <p style="margin: 6px 0;">• Risk Profile Matching</p>
                <p style="margin: 6px 0;">• Concentration Risk Reduction</p>
                <p style="margin: 6px 0;">• Target Weight Recommendations</p>
                <p style="margin: 6px 0;">• Tax-Efficient Rebalancing Tips</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_metrics_section():
    """Render the metrics section showing all available metrics"""
    
    st.markdown("""
    <div style="background: linear-gradient(180deg, #f8faff 0%, #fff 100%); padding: 60px 20px; margin: 40px 0; border-radius: 24px;">
        <div style="text-align: center; max-width: 800px; margin: 0 auto 40px auto;">
            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
                50+ Metrics
            </div>
            <h2 style="font-size: 36px; font-weight: 800; color: #1a1a2e; line-height: 1.2; margin-bottom: 16px;">
                Comprehensive Metrics You'll Get
            </h2>
            <p style="font-size: 18px; color: #666; line-height: 1.6;">
                10-layer institutional-grade analysis with detailed metrics across every dimension
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">📈 Performance Metrics</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• Total Portfolio Return %</p>
                <p style="margin: 4px 0;">• Absolute Gain/Loss (₹)</p>
                <p style="margin: 4px 0;">• Win Rate (% stocks profitable)</p>
                <p style="margin: 4px 0;">• Best & Worst Performers</p>
                <p style="margin: 4px 0;">• All-Time High Analysis</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">🎯 Risk Metrics</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• Portfolio Beta</p>
                <p style="margin: 4px 0;">• Sharpe Ratio</p>
                <p style="margin: 4px 0;">• Sortino Ratio</p>
                <p style="margin: 4px 0;">• Maximum Drawdown</p>
                <p style="margin: 4px 0;">• Historical Volatility</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">🏛️ Structural Analysis</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• Sector Allocation %</p>
                <p style="margin: 4px 0;">• Market Cap Distribution</p>
                <p style="margin: 4px 0;">• Concentration Risk Score</p>
                <p style="margin: 4px 0;">• Diversification Grade</p>
                <p style="margin: 4px 0;">• Single Stock Exposure</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">🧠 Behavioral Metrics</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• Behavior Score (0-100)</p>
                <p style="margin: 4px 0;">• Average Holding Period</p>
                <p style="margin: 4px 0;">• Recency Bias Detection</p>
                <p style="margin: 4px 0;">• Loss Aversion Analysis</p>
                <p style="margin: 4px 0;">• Investment Discipline</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">📊 Benchmark Comparison</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• Alpha vs NIFTY 50</p>
                <p style="margin: 4px 0;">• Sector Heatmap</p>
                <p style="margin: 4px 0;">• Overweight/Underweight</p>
                <p style="margin: 4px 0;">• Style Drift Analysis</p>
                <p style="margin: 4px 0;">• Relative Performance</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff; border: 1px solid #eef2f7; border-radius: 16px; padding: 24px;">
            <div style="font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 16px;">💰 Tax & Advanced</div>
            <div style="font-size: 14px; color: #666; line-height: 2;">
                <p style="margin: 4px 0;">• STCG/LTCG Classification</p>
                <p style="margin: 4px 0;">• Estimated Tax Liability</p>
                <p style="margin: 4px 0;">• Portfolio Health Score</p>
                <p style="margin: 4px 0;">• Tail Risk Exposure</p>
                <p style="margin: 4px 0;">• Scenario Analysis</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_upload_section(authenticated, analyze_callback):
    """Render the upload section for authenticated users"""
    if authenticated:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([0.3, 2, 0.3])
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%); 
                        padding: 24px; border-radius: 16px; border: 1px solid #c8e6c9; 
                        margin-bottom: 24px; text-align: center;'>
                <p style='color: #2e7d32; margin: 0; font-size: 18px; font-weight: 600;'>
                    ✅ You're logged in! Upload your portfolio to begin analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #fafbff; padding: 40px; border-radius: 20px; 
                        border: 2px dashed #667eea; text-align: center; margin-bottom: 24px;'>
                <div style='font-size: 48px; margin-bottom: 16px;'>📁</div>
                <p style='color: #444; font-size: 16px; margin-bottom: 8px;'>
                    Drag and drop your CSV file here
                </p>
                <p style='color: #888; font-size: 14px;'>or click to browse</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload CSV",
                type=['csv'],
                help="Upload a CSV file with columns: Stock Name, Buy Price, Buy Date, Quantity",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                try:
                    portfolio_df = pd.read_csv(uploaded_file)
                    required_columns = ['Stock Name', 'Buy Price', 'Buy Date', 'Quantity']
                    missing_columns = [col for col in required_columns if col not in portfolio_df.columns]
                    
                    if missing_columns:
                        st.error(f"Missing required columns: {', '.join(missing_columns)}")
                        return None
                    else:
                        portfolio_df['Buy Date'] = pd.to_datetime(portfolio_df['Buy Date'])
                        portfolio_df['Buy Price'] = pd.to_numeric(portfolio_df['Buy Price'], errors='coerce')
                        portfolio_df['Quantity'] = pd.to_numeric(portfolio_df['Quantity'], errors='coerce')
                        portfolio_df = portfolio_df.dropna()
                        
                        if len(portfolio_df) == 0:
                            st.error("No valid data found in the uploaded file.")
                            return None
                        else:
                            st.success(f"✅ Successfully loaded {len(portfolio_df)} stocks")
                            return portfolio_df, uploaded_file.name
                            
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    return None
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                sample_data = {
                    'Stock Name': ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK'],
                    'Buy Price': [2500, 3200, 1800, 1600],
                    'Buy Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05'],
                    'Quantity': [10, 15, 20, 25]
                }
                sample_df = pd.DataFrame(sample_data)
                csv = sample_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Sample CSV",
                    data=csv,
                    file_name="sample_portfolio.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    return None


def render_cta_section(authenticated, show_signup_callback):
    """Render the call-to-action section"""
    
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Optimize Your Portfolio?</h2>
        <p class="cta-subtitle">
            Join thousands of investors who are making smarter decisions with Alphalens
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if not authenticated:
            if st.button("Start Free Analysis →", type="primary", use_container_width=True, key="cta_signup"):
                show_signup_callback()


def render_footer():
    """Render the footer section"""
    
    st.markdown("""
    <div class="footer-section">
        <div class="footer-brand">Alphalens</div>
        <div class="footer-tagline">by Edhaz Financial Services</div>
        <p>© 2024 Alphalens. All rights reserved. | For educational purposes only.</p>
        <p style="font-size: 12px; margin-top: 16px; color: #aaa;">
            Investment advice is algorithmic and model-driven. Past performance does not guarantee future results.
            Always consult a qualified financial advisor before making investment decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_csv_requirements():
    """Render CSV requirements section"""
    
    st.markdown("""
    <div style='background: #f8faff; padding: 30px; border-radius: 16px; margin: 40px 0;'>
        <h3 style='color: #1a1a2e; margin-bottom: 20px; text-align: center;'>📋 CSV Format Requirements</h3>
        <div style='display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;'>
            <div style='background: white; padding: 16px 24px; border-radius: 12px; border: 1px solid #eee;'>
                <strong>Stock Name</strong>
                <p style='color: #888; font-size: 13px; margin: 4px 0 0 0;'>e.g., RELIANCE, TCS</p>
            </div>
            <div style='background: white; padding: 16px 24px; border-radius: 12px; border: 1px solid #eee;'>
                <strong>Buy Price</strong>
                <p style='color: #888; font-size: 13px; margin: 4px 0 0 0;'>Price per share in ₹</p>
            </div>
            <div style='background: white; padding: 16px 24px; border-radius: 12px; border: 1px solid #eee;'>
                <strong>Buy Date</strong>
                <p style='color: #888; font-size: 13px; margin: 4px 0 0 0;'>YYYY-MM-DD format</p>
            </div>
            <div style='background: white; padding: 16px 24px; border-radius: 12px; border: 1px solid #eee;'>
                <strong>Quantity</strong>
                <p style='color: #888; font-size: 13px; margin: 4px 0 0 0;'>Number of shares</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
