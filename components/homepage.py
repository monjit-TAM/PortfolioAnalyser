import streamlit as st
import pandas as pd

def render_modern_homepage(authenticated, show_login_callback, show_signup_callback, analyze_callback):
    """Render minimalist, bold homepage design"""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        .alpha-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* Hero Section */
        .hero-minimal {
            text-align: center;
            padding: 80px 20px 60px 20px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .hero-headline {
            font-size: clamp(40px, 7vw, 72px);
            font-weight: 900;
            color: #0f172a;
            line-height: 1.05;
            letter-spacing: -2px;
            margin-bottom: 24px;
        }
        
        .hero-subtext {
            font-size: 20px;
            color: #64748b;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto 40px auto;
            font-weight: 400;
        }
        
        .hero-cta-btn {
            display: inline-block;
            background: #0f172a;
            color: white;
            padding: 18px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
        }
        
        .hero-cta-btn:hover {
            background: #1e293b;
            transform: translateY(-2px);
        }
        
        /* Hero Image */
        .hero-image-container {
            max-width: 1000px;
            margin: 0 auto 80px auto;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 25px 80px rgba(0,0,0,0.12);
        }
        
        .hero-image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        /* Separator Text */
        .separator-section {
            text-align: center;
            padding: 80px 20px;
            max-width: 800px;
            margin: 0 auto;
            border-top: 1px solid #e2e8f0;
        }
        
        .separator-text {
            font-size: 28px;
            font-weight: 600;
            color: #334155;
            line-height: 1.5;
            margin-bottom: 16px;
        }
        
        .separator-subtext {
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
        }
        
        /* Process Section */
        .process-section {
            padding: 80px 20px;
            background: #f8fafc;
            margin: 0 -100vw;
            padding-left: calc(100vw - 50%);
            padding-right: calc(100vw - 50%);
        }
        
        .section-label {
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 12px;
            text-align: center;
        }
        
        .section-title {
            font-size: 40px;
            font-weight: 800;
            color: #0f172a;
            text-align: center;
            margin-bottom: 60px;
            letter-spacing: -1px;
        }
        
        .process-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .process-grid {
                grid-template-columns: 1fr;
                gap: 32px;
            }
        }
        
        .process-card {
            text-align: center;
            padding: 20px;
        }
        
        .process-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        
        .process-title {
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 12px;
        }
        
        .process-desc {
            font-size: 16px;
            color: #64748b;
            line-height: 1.6;
        }
        
        /* Features Section */
        .features-section {
            padding: 100px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .features-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .feature-card-minimal {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 32px;
            transition: all 0.2s ease;
        }
        
        .feature-card-minimal:hover {
            border-color: #cbd5e1;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }
        
        .feature-card-title {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
        }
        
        .feature-card-desc {
            font-size: 15px;
            color: #64748b;
            line-height: 1.6;
        }
        
        /* CTA Section */
        .cta-minimal {
            text-align: center;
            padding: 100px 20px;
            background: #0f172a;
            margin: 60px -100vw 0 -100vw;
            padding-left: calc(100vw - 50%);
            padding-right: calc(100vw - 50%);
        }
        
        .cta-title {
            font-size: 32px;
            font-weight: 700;
            color: white;
            margin-bottom: 24px;
        }
        
        .cta-btn {
            display: inline-block;
            background: white;
            color: #0f172a;
            padding: 16px 36px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        
        .cta-btn:hover {
            background: #f1f5f9;
            transform: translateY(-2px);
        }
        
        /* Footer */
        .footer-minimal {
            text-align: center;
            padding: 40px 20px;
            color: #94a3b8;
            font-size: 14px;
            background: #0f172a;
            margin: 0 -100vw;
            padding-left: calc(100vw - 50%);
            padding-right: calc(100vw - 50%);
        }
        
        .footer-brand {
            font-size: 20px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-minimal">
        <h1 class="hero-headline">Investing is Chaotic.<br>Find Your Focus.</h1>
        <p class="hero-subtext">
            Alphalens brings professional-grade portfolio analysis to individual investors. 
            See what others miss.
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
    
    # Hero Image
    st.markdown("""
    <div class="hero-image-container">
        <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=600&fit=crop" 
             alt="Financial data visualization" />
    </div>
    """, unsafe_allow_html=True)
    
    # Separator Section
    st.markdown("""
    <div class="separator-section">
        <p class="separator-text">Most portfolios are a black box. You own stocks, but do you understand your exposure?</p>
        <p class="separator-subtext">Alphalens clears the fog.</p>
    </div>
    """, unsafe_allow_html=True)
    
    return None


def render_features_section():
    """Render the features section with minimal design"""
    
    st.markdown("""
    <div class="features-section">
        <div class="section-label">Capabilities</div>
        <h2 class="section-title">Powerful Features</h2>
        <div class="features-grid">
            <div class="feature-card-minimal">
                <div class="feature-card-title">Risk Heatmaps</div>
                <div class="feature-card-desc">Visualize portfolio risk across sectors and assets in real-time.</div>
            </div>
            <div class="feature-card-minimal">
                <div class="feature-card-title">Sector Allocation</div>
                <div class="feature-card-desc">Understand your exposure distribution across market sectors.</div>
            </div>
            <div class="feature-card-minimal">
                <div class="feature-card-title">Dividend Tracking</div>
                <div class="feature-card-desc">Monitor income streams and reinvestment opportunities.</div>
            </div>
            <div class="feature-card-minimal">
                <div class="feature-card-title">Performance Analytics</div>
                <div class="feature-card-desc">Track returns, volatility, and benchmark comparisons.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_insights_section():
    """Render insights section - simplified"""
    pass


def render_how_it_works_section():
    """Render the how it works section with minimal design"""
    
    st.markdown("""
    <div class="process-section" id="how-it-works">
        <div class="section-label">The Process</div>
        <h2 class="section-title">How It Works</h2>
        <div class="process-grid">
            <div class="process-card">
                <div class="process-icon">📤</div>
                <div class="process-title">Upload</div>
                <div class="process-desc">Upload your portfolio CSV with your stock holdings.</div>
            </div>
            <div class="process-card">
                <div class="process-icon">🔍</div>
                <div class="process-title">X-Ray</div>
                <div class="process-desc">Our algorithms scan for hidden risks and correlations.</div>
            </div>
            <div class="process-card">
                <div class="process-icon">📊</div>
                <div class="process-title">Optimize</div>
                <div class="process-desc">Get actionable insights to rebalance and grow.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_methodology_section():
    """Render methodology section - simplified for minimal design"""
    pass


def render_metrics_section():
    """Render metrics section - simplified for minimal design"""
    pass


def render_upload_section(authenticated, analyze_callback):
    """Render upload section - simplified"""
    pass


def render_cta_section(authenticated, show_signup_callback):
    """Render CTA section with minimal design"""
    
    st.markdown("""
    <div class="cta-minimal">
        <h2 class="cta-title">Ready to see the full picture?</h2>
        <p style="color: #94a3b8; font-size: 18px; margin-bottom: 32px;">Start your free analysis today.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if not authenticated:
            if st.button("Get Started Free", type="secondary", use_container_width=True, key="cta_signup"):
                show_signup_callback()


def render_footer():
    """Render footer with minimal design"""
    
    st.markdown("""
    <div class="footer-minimal">
        <div class="footer-brand">Alphalens</div>
        <p>Professional Portfolio Intelligence for Indian Investors</p>
        <p style="margin-top: 20px; font-size: 12px;">
            © 2026 Edhaz Financial Services. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_csv_requirements():
    """Render CSV requirements section - simplified"""
    
    st.markdown("""
    <div style="max-width: 600px; margin: 40px auto; padding: 32px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 16px;">CSV Format Requirements</h3>
        <p style="font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
            Your CSV file should contain the following columns:
        </p>
        <ul style="font-size: 14px; color: #475569; line-height: 2; padding-left: 20px;">
            <li><strong>Stock Name</strong> - Name or symbol of the stock</li>
            <li><strong>Buy Date</strong> - Purchase date (DD-MM-YYYY)</li>
            <li><strong>Buy Price</strong> - Price per share at purchase</li>
            <li><strong>Quantity</strong> - Number of shares</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
