import streamlit as st
import pandas as pd

def render_modern_homepage(authenticated, show_login_callback, show_signup_callback, analyze_callback):
    """Render minimalist, bold homepage design"""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .stApp {
            background: #ffffff;
        }
        
        /* Hero Section */
        .hero-section-minimal {
            text-align: center;
            padding: 60px 24px 40px 24px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .hero-title-bold {
            font-size: 52px;
            font-weight: 800;
            color: #111827;
            line-height: 1.1;
            letter-spacing: -1.5px;
            margin-bottom: 24px;
        }
        
        @media (max-width: 768px) {
            .hero-title-bold {
                font-size: 36px;
            }
        }
        
        .hero-subtitle-light {
            font-size: 20px;
            color: #6b7280;
            line-height: 1.6;
            max-width: 520px;
            margin: 0 auto 36px auto;
            font-weight: 400;
            text-align: center;
        }
        
        /* Hero Image */
        .hero-image-wrapper {
            max-width: 900px;
            margin: 40px auto 0 auto;
            padding: 0 24px;
        }
        
        .hero-image-wrapper img {
            width: 100%;
            max-height: 300px;
            height: 300px;
            object-fit: cover;
            object-position: center;
            border-radius: 12px;
            display: block;
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.12);
        }
        
        /* Tagline Section */
        .tagline-section {
            text-align: center;
            padding: 60px 24px;
            max-width: 650px;
            margin: 0 auto;
        }
        
        .tagline-text {
            font-size: 22px;
            color: #4b5563;
            line-height: 1.5;
            margin-bottom: 16px;
            font-weight: 400;
        }
        
        .tagline-bold {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        }
        
        /* Section Styling */
        .section-wrapper {
            padding: 80px 24px;
            background: #fafafa;
        }
        
        .section-wrapper-white {
            padding: 60px 24px;
            background: #ffffff;
        }
        
        .section-label-small {
            font-size: 13px;
            font-weight: 600;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 14px;
            text-align: center;
        }
        
        .section-heading {
            font-size: 36px;
            font-weight: 700;
            color: #111827;
            text-align: center;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }
        
        .section-subheading {
            font-size: 18px;
            color: #6b7280;
            text-align: center;
            margin-bottom: 60px;
        }
        
        /* Process Steps - With numbered circles */
        .process-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 48px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .process-steps {
                grid-template-columns: 1fr;
                gap: 40px;
            }
        }
        
        .process-step {
            text-align: center;
        }
        
        .step-number {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
            margin: 0 auto 20px auto;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        }
        
        .step-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .step-title {
            font-size: 20px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 10px;
        }
        
        .step-desc {
            font-size: 15px;
            color: #6b7280;
            line-height: 1.6;
        }
        
        /* Investment Guidance Section */
        .guidance-section {
            padding: 80px 24px;
            background: #ffffff;
        }
        
        .guidance-heading {
            font-size: 32px;
            font-weight: 700;
            color: #111827;
            text-align: center;
            margin-bottom: 12px;
        }
        
        .guidance-subheading {
            font-size: 18px;
            color: #6b7280;
            text-align: center;
            margin-bottom: 48px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .guidance-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .guidance-cards {
                grid-template-columns: 1fr;
            }
        }
        
        .guidance-card {
            background: linear-gradient(135deg, #c9726c 0%, #b85c55 100%);
            border-radius: 16px;
            padding: 40px 28px;
            text-align: center;
            color: white;
        }
        
        .guidance-icon {
            font-size: 40px;
            margin-bottom: 20px;
        }
        
        .guidance-card-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .guidance-card-desc {
            font-size: 14px;
            opacity: 0.9;
        }
        
        /* Feature Cards */
        .feature-cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            max-width: 750px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .feature-cards-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .feature-card-item {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 28px;
        }
        
        .feature-card-heading {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }
        
        .feature-card-text {
            font-size: 15px;
            color: #6b7280;
            line-height: 1.6;
        }
        
        /* Red button styling for Streamlit */
        .stButton > button[kind="primary"] {
            background-color: #dc2626 !important;
            border-color: #dc2626 !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: #b91c1c !important;
            border-color: #b91c1c !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section-minimal">
        <h1 class="hero-title-bold">Investing is Chaotic.<br>Find Your Focus.</h1>
        <p class="hero-subtitle-light">
            Alphalens brings professional-grade portfolio analysis to individual investors. See what others miss.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button - Now Red
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if authenticated:
            if st.button("Analyze My Portfolio", type="primary", use_container_width=True, key="hero_analyze"):
                analyze_callback()
        else:
            if st.button("Analyze My Portfolio", type="primary", use_container_width=True, key="hero_start"):
                show_signup_callback()
    
    # Hero Image
    st.markdown("""
    <div class="hero-image-wrapper">
        <img src="https://images.unsplash.com/photo-1666537072157-440346cea066?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200" 
             alt="Financial data visualization" />
    </div>
    """, unsafe_allow_html=True)
    
    # Tagline Section
    st.markdown("""
    <div class="tagline-section">
        <p class="tagline-text">Most portfolios are a black box. You own stocks, but do you understand your exposure?</p>
        <p class="tagline-bold">Alphalens clears the fog.</p>
    </div>
    """, unsafe_allow_html=True)
    
    return None


def render_features_section():
    """Render the features section"""
    
    st.markdown("""
    <div class="section-wrapper-white">
        <div class="section-label-small">Capabilities</div>
        <h2 class="section-heading">Powerful Features</h2>
        <div class="feature-cards-grid">
            <div class="feature-card-item">
                <div class="feature-card-heading">Risk Heatmaps</div>
                <div class="feature-card-text">Visualize portfolio risk across sectors and assets in real-time.</div>
            </div>
            <div class="feature-card-item">
                <div class="feature-card-heading">Sector Allocation</div>
                <div class="feature-card-text">Understand your exposure distribution.</div>
            </div>
            <div class="feature-card-item">
                <div class="feature-card-heading">Dividend Tracking</div>
                <div class="feature-card-text">Monitor income streams and reinvestment opportunities.</div>
            </div>
            <div class="feature-card-item">
                <div class="feature-card-heading">Fee Analyzer</div>
                <div class="feature-card-text">Identify hidden costs eating your returns.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_insights_section():
    """Render Investment Guidance section with 3 coral/red cards"""
    
    st.markdown("""
    <div class="guidance-section">
        <h2 class="guidance-heading">Get Clear Investment Guidance</h2>
        <p class="guidance-subheading">Know exactly what to buy, hold, or sell based on comprehensive value and growth analysis.</p>
        <div class="guidance-cards">
            <div class="guidance-card">
                <div class="guidance-icon">💎</div>
                <div class="guidance-card-title">Value Investing</div>
                <div class="guidance-card-desc">Fundamental analysis</div>
            </div>
            <div class="guidance-card">
                <div class="guidance-icon">🚀</div>
                <div class="guidance-card-title">Growth Investing</div>
                <div class="guidance-card-desc">Momentum signals</div>
            </div>
            <div class="guidance-card">
                <div class="guidance-icon">💡</div>
                <div class="guidance-card-title">Recommendations</div>
                <div class="guidance-card-desc">BUY/HOLD/SELL signals</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_how_it_works_section():
    """Render the how it works section with numbered circles and icons"""
    
    st.markdown("""
    <div class="section-wrapper" id="how-it-works">
        <div class="section-label-small">How It Works</div>
        <h2 class="section-heading">It's Simple and Easy to Use</h2>
        <p class="section-subheading">Get started in minutes with just 3 simple steps</p>
        <div class="process-steps">
            <div class="process-step">
                <div class="step-number">1</div>
                <div class="step-icon">📤</div>
                <div class="step-title">Upload Portfolio</div>
                <div class="step-desc">Upload your portfolio CSV file with stock names, buy prices, dates, and quantities</div>
            </div>
            <div class="process-step">
                <div class="step-number">2</div>
                <div class="step-icon">⚡</div>
                <div class="step-title">Instant Analysis</div>
                <div class="step-desc">Our engine fetches live prices and runs 10+ layers of comprehensive analysis</div>
            </div>
            <div class="process-step">
                <div class="step-number">3</div>
                <div class="step-icon">📊</div>
                <div class="step-title">Get Insights</div>
                <div class="step-desc">View detailed reports, recommendations, and download comprehensive PDF reports</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_methodology_section():
    """Not used in minimal design"""
    pass


def render_metrics_section():
    """Not used in minimal design"""
    pass


def render_upload_section(authenticated, analyze_callback):
    """Not used in minimal design"""
    pass


def render_cta_section(authenticated, show_signup_callback):
    """Render CTA section as a dark card"""
    
    st.markdown("""
    <div style="max-width: 800px; margin: 60px auto; padding: 60px 40px; background: #111827; border-radius: 16px; text-align: center;">
        <h2 style="font-size: 32px; font-weight: 700; color: #ffffff; margin: 0 0 14px 0;">Ready to see the full picture?</h2>
        <p style="font-size: 18px; color: #9ca3af; margin: 0 0 32px 0;">Start your free analysis today.</p>
        <a href="#" onclick="window.scrollTo(0,0); return false;" style="display: inline-block; background: #dc2626; color: #ffffff; padding: 16px 36px; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; transition: all 0.2s;">Get Started Free</a>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render footer"""
    
    st.markdown("""
    <div style="text-align: center; padding: 40px 24px; margin-top: 40px; border-top: 1px solid #e5e7eb;">
        <div style="font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 8px;">Alphalens</div>
        <p style="font-size: 14px; color: #6b7280; margin: 0;">© 2026 Edhaz Financial Services. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


def render_csv_requirements():
    """Render CSV requirements section"""
    
    st.markdown("""
    <div style="max-width: 550px; margin: 40px auto; padding: 28px; background: #ffffff; border-radius: 10px; border: 1px solid #e5e7eb;">
        <h3 style="font-size: 18px; font-weight: 700; color: #111827; margin-bottom: 14px;">CSV Format Requirements</h3>
        <p style="font-size: 14px; color: #6b7280; line-height: 1.5; margin-bottom: 14px;">
            Your CSV file should contain the following columns:
        </p>
        <ul style="font-size: 14px; color: #4b5563; line-height: 1.8; padding-left: 18px; margin: 0;">
            <li><strong>Stock Name</strong> - Name or symbol of the stock</li>
            <li><strong>Buy Date</strong> - Purchase date (DD-MM-YYYY)</li>
            <li><strong>Buy Price</strong> - Price per share at purchase</li>
            <li><strong>Quantity</strong> - Number of shares</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
