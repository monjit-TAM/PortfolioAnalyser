import streamlit as st
import pandas as pd

def render_modern_homepage(authenticated, show_login_callback, show_signup_callback, analyze_callback):
    """Render modern, sleek homepage design"""
    
    st.markdown("""
    <style>
        .hero-section {
            text-align: center;
            padding: 60px 20px 40px 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .hero-title {
            font-size: 48px;
            font-weight: 800;
            color: #1a1a1a;
            line-height: 1.2;
            margin-bottom: 20px;
            letter-spacing: -1px;
        }
        .hero-subtitle {
            font-size: 18px;
            color: #666;
            line-height: 1.6;
            max-width: 500px;
            margin: 0 auto 30px auto;
        }
        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            text-align: center;
            margin-bottom: 10px;
        }
        .section-subtitle {
            font-size: 16px;
            color: #888;
            text-align: center;
            margin-bottom: 40px;
        }
        .feature-card {
            background: #fff;
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: left;
            min-height: 200px;
        }
        .feature-card:hover {
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        }
        .feature-icon {
            width: 48px;
            height: 48px;
            background: #f5f5f5;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .feature-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 10px;
        }
        .feature-desc {
            font-size: 14px;
            color: #666;
            line-height: 1.6;
        }
        .step-number {
            width: 40px;
            height: 40px;
            background: #1a1a1a;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            margin: 0 auto 20px auto;
        }
        .step-icon {
            font-size: 32px;
            margin-bottom: 15px;
            color: #1a1a1a;
        }
        .step-title {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        .step-desc {
            font-size: 14px;
            color: #888;
            line-height: 1.5;
        }
        .cta-section {
            background: #fafafa;
            padding: 60px 20px;
            text-align: center;
            border-radius: 16px;
            margin: 40px 0;
        }
        .cta-title {
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 15px;
        }
        .cta-subtitle {
            font-size: 16px;
            color: #666;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Analyze Your Portfolio.<br>Generate Alpha.</h1>
        <p class="hero-subtitle">
            Upload your Indian stock portfolio and get instant insights on performance, risk analysis, and actionable recommendations to maximize returns.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if authenticated:
            st.button("Go to Dashboard", type="primary", use_container_width=True, key="hero_dashboard")
        else:
            if st.button("Get Started", type="primary", use_container_width=True, key="hero_start"):
                show_signup_callback()
    
    return None


def render_upload_section(authenticated, analyze_callback):
    """Render the upload section for authenticated users"""
    if authenticated:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            st.markdown("""
            <div style='background: #f0f9f0; padding: 20px; border-radius: 12px; border: 1px solid #c3e6c3; margin-bottom: 20px;'>
                <p style='color: #1a7431; margin: 0; font-size: 16px; text-align: center;'>
                    You're logged in! Upload your portfolio CSV below to begin analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Drag and drop your CSV file here or click to browse",
                type=['csv'],
                help="Upload a CSV file with columns: Stock Name, Buy Price, Buy Date, Quantity"
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
                            st.success(f"Successfully loaded {len(portfolio_df)} stocks")
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
                    label="Download Sample CSV",
                    data=csv,
                    file_name="portfolio_sample.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    return None


def render_features_section():
    """Render the Smart Portfolio Intelligence features section"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <h2 class="section-title">Smart Portfolio Intelligence</h2>
    <p class="section-subtitle">Professional-grade analysis tools to help you make informed investment decisions</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Performance Tracking</div>
            <p class="feature-desc">
                Real-time portfolio valuation with detailed performance metrics across NSE and BSE stocks.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Risk Analysis</div>
            <p class="feature-desc">
                Identify overexposed positions and understand sector concentration risks in your holdings.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Alpha Generation</div>
            <p class="feature-desc">
                Get personalized recommendations on which stocks to hold, sell, or add to beat the market.
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_how_it_works_section():
    """Render the How It Works section"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
    <h2 class="section-title">How It Works</h2>
    <p class="section-subtitle">Three simple steps to smarter investing</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div class="step-number">1</div>
            <div class="step-icon">📤</div>
            <div class="step-title">Upload Portfolio</div>
            <p class="step-desc">Import your holdings via CSV from any broker or trading platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div class="step-number">2</div>
            <div class="step-icon">📊</div>
            <div class="step-title">Analyze Performance</div>
            <p class="step-desc">Get instant insights on winners, losers, and portfolio health metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div class="step-number">3</div>
            <div class="step-icon">✓</div>
            <div class="step-title">Take Action</div>
            <p class="step-desc">Follow data-driven recommendations to optimize your portfolio</p>
        </div>
        """, unsafe_allow_html=True)


def render_cta_section(authenticated, show_signup_callback):
    """Render the Call-to-Action section"""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Optimize Your Portfolio?</h2>
        <p class="cta-subtitle">Join thousands of investors using data-driven insights to make better investment decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if not authenticated:
            if st.button("Get Started Free", type="primary", use_container_width=True, key="cta_start"):
                show_signup_callback()


def render_csv_requirements():
    """Render the CSV format requirements expander"""
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("CSV Format & Requirements"):
        col_x, col_y = st.columns(2)
        with col_x:
            st.markdown("""
            **Required Columns:**
            - Stock Name (e.g., RELIANCE, TCS, INFY)
            - Buy Price (in ₹)
            - Buy Date (YYYY-MM-DD format)
            - Quantity (number of shares)
            """)
        with col_y:
            st.markdown("""
            **Supported Stock Names:**
            - NSE symbols (e.g., RELIANCE, TCS)
            - Common abbreviations (e.g., HDFC for HDFCBANK)
            - Full names mapped automatically
            """)
