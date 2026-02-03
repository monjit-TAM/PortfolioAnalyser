import streamlit as st
import pandas as pd

def render_modern_homepage(authenticated, show_login_callback, show_signup_callback, analyze_callback):
    """Render minimalist, bold homepage design with proper spacing"""
    
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
            font-size: 48px;
            font-weight: 800;
            color: #111827;
            line-height: 1.1;
            letter-spacing: -1.5px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .hero-title-bold {
                font-size: 32px;
            }
        }
        
        .hero-subtitle-light {
            font-size: 18px;
            color: #6b7280;
            line-height: 1.6;
            max-width: 500px;
            margin: 0 auto 32px auto;
            font-weight: 400;
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
            max-width: 600px;
            margin: 0 auto;
        }
        
        .tagline-text {
            font-size: 20px;
            color: #4b5563;
            line-height: 1.5;
            margin-bottom: 12px;
            font-weight: 400;
        }
        
        .tagline-bold {
            font-size: 22px;
            font-weight: 700;
            color: #111827;
        }
        
        /* Section Styling */
        .section-wrapper {
            padding: 60px 24px;
            background: #f9fafb;
        }
        
        .section-wrapper-white {
            padding: 60px 24px;
            background: #ffffff;
        }
        
        .section-label-small {
            font-size: 12px;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 12px;
            text-align: center;
        }
        
        .section-heading {
            font-size: 32px;
            font-weight: 700;
            color: #111827;
            text-align: center;
            margin-bottom: 48px;
            letter-spacing: -0.5px;
        }
        
        /* Process Cards */
        .process-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 32px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .process-cards {
                grid-template-columns: 1fr;
                gap: 24px;
            }
        }
        
        .process-card-item {
            text-align: center;
        }
        
        .process-card-icon {
            width: 56px;
            height: 56px;
            background: #e5e7eb;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px auto;
            font-size: 24px;
        }
        
        .process-card-title {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }
        
        .process-card-desc {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.5;
        }
        
        /* Feature Cards */
        .feature-cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 700px;
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
            border-radius: 10px;
            padding: 24px;
        }
        
        .feature-card-heading {
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 6px;
        }
        
        .feature-card-text {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.5;
        }
        
        /* CTA Section */
        .cta-section-dark {
            text-align: center;
            padding: 60px 24px;
            background: #111827;
            border-radius: 0;
        }
        
        .cta-heading {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 12px;
        }
        
        .cta-subtext {
            font-size: 16px;
            color: #9ca3af;
            margin-bottom: 28px;
        }
        
        .cta-button-wrapper {
            text-align: center;
        }
        
        .cta-btn-light {
            display: inline-block;
            background: #ffffff;
            color: #111827;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: none;
        }
        
        /* Footer */
        .footer-section {
            text-align: center;
            padding: 32px 24px;
            background: #111827;
        }
        
        .footer-brand {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        }
        
        .footer-text {
            font-size: 13px;
            color: #6b7280;
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
    
    # CTA Button
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if authenticated:
            if st.button("Analyze My Portfolio", type="primary", use_container_width=True, key="hero_analyze"):
                analyze_callback()
        else:
            if st.button("Analyze My Portfolio", type="primary", use_container_width=True, key="hero_start"):
                show_signup_callback()
    
    # Hero Image - Smaller and more proportionate
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
    """Not used in minimal design"""
    pass


def render_how_it_works_section():
    """Render the how it works section"""
    
    st.markdown("""
    <div class="section-wrapper" id="how-it-works">
        <div class="section-label-small">The Process</div>
        <h2 class="section-heading">How It Works</h2>
        <div class="process-cards">
            <div class="process-card-item">
                <div class="process-card-icon">🔗</div>
                <div class="process-card-title">Connect</div>
                <div class="process-card-desc">Securely link your brokerage account.</div>
            </div>
            <div class="process-card-item">
                <div class="process-card-icon">🔍</div>
                <div class="process-card-title">X-Ray</div>
                <div class="process-card-desc">Our algorithms scan for hidden risks and correlations.</div>
            </div>
            <div class="process-card-item">
                <div class="process-card-icon">📈</div>
                <div class="process-card-title">Optimize</div>
                <div class="process-card-desc">Get actionable insights to rebalance and grow.</div>
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
    """Render CTA section with button inside dark area"""
    
    # CTA with button inside the dark section using HTML
    if not authenticated:
        st.markdown("""
        <div class="cta-section-dark">
            <h2 class="cta-heading">Ready to see the full picture?</h2>
            <p class="cta-subtext">Start your free analysis today.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            if st.button("Get Started Free", type="primary", use_container_width=True, key="cta_signup"):
                show_signup_callback()
    else:
        st.markdown("""
        <div class="cta-section-dark">
            <h2 class="cta-heading">Ready to analyze your portfolio?</h2>
            <p class="cta-subtext">Upload your holdings to get started.</p>
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    """Render footer"""
    
    st.markdown("""
    <div class="footer-section">
        <div class="footer-brand">Alphalens</div>
        <p class="footer-text">© 2026 Edhaz Financial Services. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


def render_csv_requirements():
    """Render CSV requirements section"""
    
    st.markdown("""
    <div style="max-width: 550px; margin: 40px auto; padding: 28px; background: #f9fafb; border-radius: 10px; border: 1px solid #e5e7eb;">
        <h3 style="font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 14px;">CSV Format Requirements</h3>
        <p style="font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 14px;">
            Your CSV file should contain the following columns:
        </p>
        <ul style="font-size: 13px; color: #4b5563; line-height: 1.8; padding-left: 18px; margin: 0;">
            <li><strong>Stock Name</strong> - Name or symbol of the stock</li>
            <li><strong>Buy Date</strong> - Purchase date (DD-MM-YYYY)</li>
            <li><strong>Buy Price</strong> - Price per share at purchase</li>
            <li><strong>Quantity</strong> - Number of shares</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
