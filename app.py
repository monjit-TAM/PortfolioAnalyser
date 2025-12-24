import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import os

from utils.data_fetcher import DataFetcher
from utils.portfolio_analyzer import PortfolioAnalyzer
from utils.recommendation_engine import RecommendationEngine
from components.dashboard import Dashboard
from components.sector_analysis import SectorAnalysis
from components.stock_performance import StockPerformance
from components.benchmark_comparison import BenchmarkComparison
from components.recommendations import Recommendations
from components.customer_profile import CustomerProfile
from components.rebalancing import PortfolioRebalancing
from components.historical_performance import HistoricalPerformance
from utils.pdf_generator import PDFReportGenerator

def init_database():
    if os.environ.get('DATABASE_URL'):
        try:
            from utils.database import Database
            db = Database()
            db.init_tables()
            db.seed_initial_data()
            return True
        except Exception as e:
            print(f"Database initialization failed: {e}")
    return False

def main():
    st.set_page_config(
        page_title="Alphalens Portfolio Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = init_database()
    
    st.markdown("""
    <style>
        .block-container {
            padding-top: 0.2rem;
            padding-bottom: 1rem;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        h2, h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        .stImage {
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
        .content-section {
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .hero-header {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            margin-bottom: 15px;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .hero-header .logo-row {
            width: 100%;
            display: flex;
            justify-content: flex-end;
            margin-bottom: 10px;
        }
        .hero-header .heading-row {
            text-align: center;
            width: 100%;
        }
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .auth-header {
            text-align: center;
            color: #FF6B35;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'show_admin' not in st.session_state:
        st.session_state.show_admin = False
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
    
    if st.session_state.show_admin and st.session_state.authenticated and st.session_state.user.get('is_admin'):
        display_admin_panel()
    elif st.session_state.portfolio_data is not None and st.session_state.analysis_complete:
        display_analysis()
    elif st.session_state.portfolio_data is not None:
        display_portfolio_preview()
    else:
        display_welcome_screen()
    
    add_footer()

def render_top_header():
    """Render top header with logo left and auth buttons right"""
    col_logo, col_spacer, col_auth = st.columns([1, 2, 1])
    
    with col_logo:
        st.image("attached_assets/Alphalens_1760976199318.png", width=180)
    
    with col_auth:
        if st.session_state.authenticated:
            user_name = st.session_state.user.get('full_name') or st.session_state.user.get('email', 'User')
            col_user, col_actions = st.columns([1, 1])
            with col_user:
                st.markdown(f"""
                <div style='text-align: right; padding-top: 15px;'>
                    <span style='color: #28a745; font-weight: 500;'>✅ {user_name[:15]}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_actions:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.session_state.user.get('is_admin'):
                        if st.button("📊 Admin", key="admin_top"):
                            st.session_state.show_admin = True
                            st.rerun()
                with btn_col2:
                    if st.button("Logout", key="logout_top"):
                        st.session_state.authenticated = False
                        st.session_state.user = None
                        st.session_state.portfolio_data = None
                        st.session_state.analysis_complete = False
                        st.session_state.show_admin = False
                        st.rerun()
        else:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔐 Login", key="login_top", type="primary"):
                    st.session_state.show_login = True
                    st.rerun()
            with col_btn2:
                if st.button("📝 Register", key="register_top"):
                    st.session_state.show_signup = True
                    st.rerun()
    
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

def render_auth_header():
    with st.sidebar:
        st.image("attached_assets/Alphalens_1760976199318.png", width=200)
        st.markdown("---")
        
        if st.session_state.authenticated:
            user_name = st.session_state.user.get('full_name') or st.session_state.user.get('email', 'User')
            st.success(f"✅ Logged in as **{user_name[:20]}**")
            
            if st.session_state.user.get('is_admin'):
                if st.button("📊 Admin Panel", key="admin_btn", use_container_width=True):
                    st.session_state.show_admin = True
                    st.rerun()
            
            if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.portfolio_data = None
                st.session_state.analysis_complete = False
                st.session_state.show_admin = False
                st.rerun()
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #FF6B35 0%, #ff8c5a 100%); padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                <h3 style='color: white; margin: 0 0 10px 0;'>🔐 Sign In Required</h3>
                <p style='color: white; font-size: 13px; margin: 0;'>Login or Register to analyze your portfolio</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 LOGIN", key="login_btn", use_container_width=True, type="primary"):
                st.session_state.show_login = True
                st.rerun()
            
            if st.button("📝 CREATE ACCOUNT", key="register_btn", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        st.markdown("---")

def display_login_modal():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background: #fff5f2; padding: 20px; border-radius: 10px; border: 2px solid #FF6B35;'>
        <h3 style='color: #FF6B35; text-align: center;'>Login to Your Account</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_email = st.text_input("Email", placeholder="Enter your email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            with col_b:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.show_login = False
                st.rerun()
            
            if login_submitted:
                if login_email and login_password:
                    try:
                        from utils.auth import AuthManager
                        auth = AuthManager()
                        result = auth.login(login_email, login_password)
                        
                        if result['success']:
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'id': result['user_id'],
                                'email': result['email'],
                                'full_name': result.get('full_name', ''),
                                'is_admin': result.get('is_admin', False)
                            }
                            st.session_state.show_login = False
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result['message'])
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.warning("Please enter both email and password")

def display_signup_modal():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background: #fff5f2; padding: 20px; border-radius: 10px; border: 2px solid #FF6B35;'>
        <h3 style='color: #FF6B35; text-align: center;'>Create Your Account</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            signup_name = st.text_input("Full Name", placeholder="Enter your full name")
            signup_email = st.text_input("Email", placeholder="Enter your email")
            signup_phone = st.text_input("Phone (optional)", placeholder="Enter your phone number")
            signup_password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                signup_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            with col_b:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.show_signup = False
                st.rerun()
            
            if signup_submitted:
                if not signup_email or not signup_password:
                    st.warning("Please enter email and password")
                elif len(signup_password) < 6:
                    st.warning("Password must be at least 6 characters")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        from utils.auth import AuthManager
                        auth = AuthManager()
                        result = auth.signup(signup_email, signup_password, signup_name, signup_phone)
                        
                        if result['success']:
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'id': result['user_id'],
                                'email': result['email'],
                                'full_name': result.get('full_name', ''),
                                'is_admin': False
                            }
                            st.session_state.show_signup = False
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error(result['message'])
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")

def display_admin_panel():
    render_auth_header()
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FF6B35 0%, #ff8c5a 100%); padding: 20px; border-radius: 10px; margin: 20px 0;'>
        <h2 style='color: white; text-align: center; margin: 0;'>Admin Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.show_admin = False
            st.rerun()
    
    try:
        from utils.database import Database
        db = Database()
        
        stats = db.get_admin_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", stats['total_users'])
        with col2:
            st.metric("Total Analyses", stats['total_analyses'])
        with col3:
            st.metric("Active Users", stats['active_users'])
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["Users", "Portfolio History", "Activity Log"])
        
        with tab1:
            st.subheader("Registered Users")
            users = db.get_all_users()
            if users:
                users_df = pd.DataFrame(users)
                users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                users_df['last_login'] = pd.to_datetime(users_df['last_login']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(users_df[['email', 'full_name', 'phone', 'is_admin', 'created_at', 'last_login']], use_container_width=True)
            else:
                st.info("No users registered yet")
        
        with tab2:
            st.subheader("Portfolio Evaluations")
            portfolios = db.get_all_portfolio_history()
            if portfolios:
                portfolios_df = pd.DataFrame(portfolios)
                portfolios_df['created_at'] = pd.to_datetime(portfolios_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                portfolios_df['total_investment'] = portfolios_df['total_investment'].apply(lambda x: f"₹{float(x):,.2f}" if x else "N/A")
                portfolios_df['current_value'] = portfolios_df['current_value'].apply(lambda x: f"₹{float(x):,.2f}" if x else "N/A")
                portfolios_df['total_gain_loss'] = portfolios_df['total_gain_loss'].apply(lambda x: f"₹{float(x):,.2f}" if x else "N/A")
                st.dataframe(portfolios_df[['email', 'full_name', 'file_name', 'stock_count', 'total_investment', 'current_value', 'total_gain_loss', 'created_at']], use_container_width=True)
            else:
                st.info("No portfolio analyses recorded yet")
        
        with tab3:
            st.subheader("User Activity Log")
            activities = db.get_user_activity(50)
            if activities:
                activities_df = pd.DataFrame(activities)
                activities_df['created_at'] = pd.to_datetime(activities_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(activities_df[['email', 'activity_type', 'details', 'created_at']], use_container_width=True)
            else:
                st.info("No activity recorded yet")
    except Exception as e:
        st.error(f"Error loading admin data: {str(e)}")

def analyze_portfolio():
    """Perform comprehensive portfolio analysis"""
    try:
        portfolio_df = st.session_state.portfolio_data
        
        # Initialize analyzers
        data_fetcher = DataFetcher()
        portfolio_analyzer = PortfolioAnalyzer()
        recommendation_engine = RecommendationEngine()
        
        # Fetch current market data
        progress_bar = st.progress(0)
        st.text("Fetching current stock prices...")
        
        current_data = {}
        historical_data = {}
        
        for idx, (_, stock) in enumerate(portfolio_df.iterrows()):
            stock_name = stock['Stock Name']
            buy_date = stock['Buy Date']
            
            # Fetch current price and historical data
            current_price, hist_data = data_fetcher.get_stock_data(stock_name, buy_date)
            
            # Only add to current_data if price was successfully fetched
            if current_price is not None:
                current_data[stock_name] = current_price
                historical_data[stock_name] = hist_data
            else:
                st.error(f"⚠️ Skipping {stock_name} due to data fetch failure")
            
            progress_bar.progress((idx + 1) / len(portfolio_df))
        
        st.text("Analyzing portfolio performance...")
        
        # Perform analysis
        analysis_results = portfolio_analyzer.analyze_portfolio(
            portfolio_df, current_data, historical_data
        )
        
        # Create enriched portfolio DataFrame from analysis results
        enriched_portfolio_df = pd.DataFrame(analysis_results['stock_performance'])
        
        # Generate recommendations using enriched data
        recommendations = recommendation_engine.generate_recommendations(
            enriched_portfolio_df, current_data, historical_data, analysis_results
        )
        
        # Store results in session state
        st.session_state.analysis_results = analysis_results
        st.session_state.recommendations = recommendations
        st.session_state.current_data = current_data
        st.session_state.historical_data = historical_data
        st.session_state.analysis_complete = True
        
        progress_bar.progress(1.0)
        st.success("Analysis complete!")
        
        try:
            from utils.database import Database
            db = Database()
            user_id = st.session_state.user.get('id') if st.session_state.user else None
            if user_id:
                file_name = st.session_state.get('uploaded_file_name', 'Unknown')
                stock_count = len(portfolio_df)
                total_investment = analysis_results.get('total_investment', 0)
                current_value = analysis_results.get('current_value', 0)
                total_gain_loss = analysis_results.get('total_gain_loss', 0)
                
                stocks_list = [{'name': stock['Stock Name'], 'qty': int(stock['Quantity'])} 
                              for _, stock in portfolio_df.iterrows()]
                
                db.save_portfolio_history(
                    user_id, file_name, stock_count, total_investment,
                    current_value, total_gain_loss, stocks_list
                )
                db.log_activity(user_id, 'portfolio_analysis', f'Analyzed {stock_count} stocks')
        except Exception as e:
            pass
        
        # Auto-rerun to display results
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        st.session_state.analysis_complete = False

def refresh_prices():
    """Refresh stock prices with latest market data"""
    try:
        portfolio_df = st.session_state.portfolio_data
        data_fetcher = DataFetcher()
        portfolio_analyzer = PortfolioAnalyzer()
        recommendation_engine = RecommendationEngine()
        
        # Fetch updated prices
        current_data = {}
        historical_data = st.session_state.historical_data  # Keep existing historical data
        
        for _, stock in portfolio_df.iterrows():
            stock_name = stock['Stock Name']
            buy_date = stock['Buy Date']
            
            # Fetch current price only
            current_price, _ = data_fetcher.get_stock_data(stock_name, buy_date)
            
            # Only add if price was successfully fetched
            if current_price is not None:
                current_data[stock_name] = current_price
        
        # Re-analyze with updated prices
        analysis_results = portfolio_analyzer.analyze_portfolio(
            portfolio_df, current_data, historical_data
        )
        
        # Create enriched portfolio DataFrame from analysis results
        enriched_portfolio_df = pd.DataFrame(analysis_results['stock_performance'])
        
        recommendations = recommendation_engine.generate_recommendations(
            enriched_portfolio_df, current_data, historical_data, analysis_results
        )
        
        # Update session state
        st.session_state.current_data = current_data
        st.session_state.analysis_results = analysis_results
        st.session_state.recommendations = recommendations
        
        st.success("Prices updated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error refreshing prices: {str(e)}")

def display_analysis():
    """Display comprehensive portfolio analysis"""
    
    render_auth_header()
    
    # Apply global styling for margins and card-based sections
    st.markdown("""
    <style>
    /* Add margins to main container */
    .main .block-container {
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }
    
    /* Style for section cards */
    .section-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    /* Header card styling */
    .header-card {
        background: linear-gradient(135deg, #fff5f2 0%, #ffffff 100%);
        border: 2px solid #FF6B35;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.1);
    }
    
    /* Tab content styling */
    div[data-testid="stTabs"] > div {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Professional header with card styling
    st.markdown("""
    <div class="header-card">
        <div style='text-align: center;'>
            <h1 style='color: #FF6B35; margin-bottom: 10px; font-size: 32px; font-weight: 600;'>📊 Portfolio Analysis Report</h1>
            <p style='color: #666; font-size: 16px; margin-bottom: 0;'>Comprehensive analysis of your investment portfolio</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 0.5])
    
    with col1:
        user_name = ""
        if st.session_state.user:
            user_name = st.session_state.user.get('full_name') or st.session_state.user.get('email', '')
        st.markdown(f"**📅 Analysis Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | **User:** {user_name}")
    
    with col2:
        if st.button("🔄 Refresh Prices", type="secondary", help="Update with latest stock prices", use_container_width=True):
            with st.spinner("Refreshing prices..."):
                refresh_prices()
    
    with col3:
        # Generate PDF report
        if st.button("📄 Download Report", type="primary", help="Generate comprehensive PDF report", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_gen = PDFReportGenerator()
                    filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf_gen.generate_report(
                        st.session_state.analysis_results,
                        st.session_state.portfolio_data,
                        st.session_state.recommendations,
                        filename,
                        st.session_state.historical_data,
                        st.session_state.current_data
                    )
                    
                    # Read the generated PDF
                    with open(filename, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    st.success("PDF report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    with col4:
        if st.button("🏠 New Analysis", type="secondary", help="Start a new portfolio analysis", use_container_width=True):
            st.session_state.portfolio_data = None
            st.session_state.analysis_complete = False
            st.rerun()
    
    with col5:
        if st.button("Logout", key="logout_analysis"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.portfolio_data = None
            st.session_state.analysis_complete = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Dashboard", 
        "🏭 Sector Analysis", 
        "📈 Stock Performance", 
        "📊 Benchmark Comparison", 
        "💡 Recommendations",
        "⚖️ Rebalancing",
        "📅 Historical Performance",
        "👤 Customer Profile"
    ])
    
    with tab1:
        dashboard = Dashboard()
        dashboard.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.current_data
        )
    
    with tab2:
        sector_analysis = SectorAnalysis()
        sector_analysis.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data
        )
    
    with tab3:
        stock_performance = StockPerformance()
        stock_performance.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.current_data,
            st.session_state.historical_data
        )
    
    with tab4:
        benchmark_comparison = BenchmarkComparison()
        benchmark_comparison.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data
        )
    
    with tab5:
        recommendations = Recommendations()
        recommendations.render(
            st.session_state.recommendations,
            st.session_state.analysis_results
        )
    
    with tab6:
        rebalancing = PortfolioRebalancing()
        rebalancing.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.current_data
        )
    
    with tab7:
        historical_performance = HistoricalPerformance()
        historical_performance.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.historical_data
        )
    
    with tab8:
        customer_profile = CustomerProfile()
        customer_profile.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.recommendations
        )

def display_welcome_screen():
    """Display sleek welcome screen with top-right auth and rich content"""
    
    if st.session_state.show_login:
        render_top_header()
        display_login_modal()
        return
    
    if st.session_state.show_signup:
        render_top_header()
        display_signup_modal()
        return
    
    # Top header with logo left and auth buttons right
    render_top_header()
    
    # Hero section with gradient background
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 60px 40px; margin: -20px -100px 30px -100px; text-align: center;'>
        <h1 style='color: #FF6B35; font-size: 48px; font-weight: 700; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            Alphalens Portfolio Analyzer
        </h1>
        <p style='color: #e8e8e8; font-size: 20px; max-width: 700px; margin: 0 auto 25px auto; line-height: 1.6;'>
            Unlock the full potential of your Indian stock portfolio with AI-powered analysis, 
            dual investment perspectives, and actionable recommendations.
        </p>
        <p style='color: #FF6B35; font-size: 16px; font-weight: 500;'>
            Powered by Edhaz Financial Services
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats bar
    st.markdown("""
    <div style='display: flex; justify-content: center; gap: 60px; padding: 25px 0; margin-bottom: 30px; background: #f8f9fa; border-radius: 10px;'>
        <div style='text-align: center;'>
            <div style='font-size: 32px; font-weight: 700; color: #FF6B35;'>500+</div>
            <div style='font-size: 14px; color: #666;'>NSE Stocks Covered</div>
        </div>
        <div style='text-align: center;'>
            <div style='font-size: 32px; font-weight: 700; color: #FF6B35;'>Real-time</div>
            <div style='font-size: 14px; color: #666;'>Market Data</div>
        </div>
        <div style='text-align: center;'>
            <div style='font-size: 32px; font-weight: 700; color: #FF6B35;'>8+</div>
            <div style='font-size: 14px; color: #666;'>Analysis Reports</div>
        </div>
        <div style='text-align: center;'>
            <div style='font-size: 32px; font-weight: 700; color: #FF6B35;'>Free</div>
            <div style='font-size: 14px; color: #666;'>To Get Started</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload section
    col1, col2, col3 = st.columns([0.3, 2, 0.3])
    with col2:
        st.markdown("""
        <h2 style='color: #1a1a2e; text-align: center; margin-bottom: 20px; font-size: 28px;'>
            Get Started in Seconds
        </h2>
        """, unsafe_allow_html=True)
        
        if not st.session_state.authenticated:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #fff5f2 0%, #ffe8e0 100%); padding: 40px; border-radius: 20px; border: 2px solid #FF6B35; text-align: center; margin: 20px 0; box-shadow: 0 10px 40px rgba(255, 107, 53, 0.15);'>
                <div style='font-size: 50px; margin-bottom: 15px;'>🔐</div>
                <h3 style='color: #FF6B35; margin-bottom: 10px; font-size: 24px;'>Sign In to Analyze Your Portfolio</h3>
                <p style='color: #666; font-size: 16px; margin-bottom: 25px; max-width: 400px; margin-left: auto; margin-right: auto;'>
                    Create a free account or login to upload your portfolio and get comprehensive analysis with actionable insights.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_space, col_btn2 = st.columns([1, 0.2, 1])
            with col_btn1:
                if st.button("🔐 LOGIN", key="login_cta", type="primary", use_container_width=True):
                    st.session_state.show_login = True
                    st.rerun()
            with col_btn2:
                if st.button("📝 CREATE FREE ACCOUNT", key="register_cta", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()
        else:
            st.markdown("""
            <div style='background: #f0f8f0; padding: 15px 20px; border-radius: 10px; border-left: 4px solid #28a745; margin-bottom: 20px;'>
                <p style='color: #155724; margin: 0; font-size: 16px;'>✅ You're logged in! Upload your portfolio CSV to begin analysis.</p>
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
                        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    else:
                        portfolio_df['Buy Date'] = pd.to_datetime(portfolio_df['Buy Date'])
                        portfolio_df['Buy Price'] = pd.to_numeric(portfolio_df['Buy Price'], errors='coerce')
                        portfolio_df['Quantity'] = pd.to_numeric(portfolio_df['Quantity'], errors='coerce')
                        portfolio_df = portfolio_df.dropna()
                        
                        if len(portfolio_df) == 0:
                            st.error("❌ No valid data found in the uploaded file.")
                        else:
                            st.success(f"✅ Successfully loaded {len(portfolio_df)} stocks")
                            st.session_state.portfolio_data = portfolio_df
                            st.session_state.uploaded_file_name = uploaded_file.name
                            
                            if st.button("🚀 Analyze My Portfolio", type="primary", use_container_width=True):
                                st.session_state.analysis_complete = False
                                with st.spinner("🔄 Fetching market data and analyzing portfolio..."):
                                    analyze_portfolio()
                                
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        # Sample CSV download
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
                file_name="portfolio_sample.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # Feature cards section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h2 style='text-align: center; color: #1a1a2e; margin-bottom: 30px; font-size: 28px;'>
        Comprehensive Portfolio Analysis
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>📊</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Dual Perspectives</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Get insights from both Value and Growth investing viewpoints for balanced decisions
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>📈</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Sector Analysis</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Understand your portfolio allocation across different sectors and industries
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>🎯</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>NIFTY Benchmark</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Compare your portfolio performance against NIFTY 50 and sectoral indices
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>💡</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Smart Recommendations</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Get BUY/HOLD/SELL signals with rebalancing suggestions
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>📋</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>PDF Reports</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Download comprehensive PDF reports with charts and recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>🔄</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Rebalancing</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Get personalized rebalancing strategies based on your risk profile
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>📉</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Historical Tracking</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Track your portfolio performance over time with detailed charts
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); height: 200px;'>
            <div style='font-size: 40px; margin-bottom: 12px;'>🔍</div>
            <h4 style='color: #FF6B35; margin-bottom: 10px; font-size: 16px;'>Alternative Stocks</h4>
            <p style='color: #666; font-size: 13px; line-height: 1.5;'>
                Discover better alternatives for underperforming stocks in your portfolio
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #1a1a2e; padding: 40px; border-radius: 20px; margin: 20px 0;'>
        <h2 style='text-align: center; color: #FF6B35; margin-bottom: 30px; font-size: 28px;'>
            How It Works
        </h2>
        <div style='display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;'>
            <div style='text-align: center; flex: 1; min-width: 200px;'>
                <div style='background: #FF6B35; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; font-size: 24px; font-weight: bold;'>1</div>
                <h4 style='color: white; margin-bottom: 8px;'>Create Account</h4>
                <p style='color: #aaa; font-size: 14px;'>Sign up for free in seconds</p>
            </div>
            <div style='text-align: center; flex: 1; min-width: 200px;'>
                <div style='background: #FF6B35; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; font-size: 24px; font-weight: bold;'>2</div>
                <h4 style='color: white; margin-bottom: 8px;'>Upload Portfolio</h4>
                <p style='color: #aaa; font-size: 14px;'>Upload your holdings as CSV</p>
            </div>
            <div style='text-align: center; flex: 1; min-width: 200px;'>
                <div style='background: #FF6B35; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; font-size: 24px; font-weight: bold;'>3</div>
                <h4 style='color: white; margin-bottom: 8px;'>Get Analysis</h4>
                <p style='color: #aaa; font-size: 14px;'>Receive comprehensive insights</p>
            </div>
            <div style='text-align: center; flex: 1; min-width: 200px;'>
                <div style='background: #FF6B35; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; font-size: 24px; font-weight: bold;'>4</div>
                <h4 style='color: white; margin-bottom: 8px;'>Take Action</h4>
                <p style='color: #aaa; font-size: 14px;'>Make informed investment decisions</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CSV Format info
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 CSV Format & Requirements"):
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

def display_portfolio_preview():
    """Display portfolio preview after upload"""
    
    render_auth_header()
    
    if st.session_state.show_login:
        display_login_modal()
        return
    
    if st.session_state.show_signup:
        display_signup_modal()
        return
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("""
        <div style='
            background-color: #e8f4f8;
            border-left: 5px solid #FF6B35;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            margin-bottom: 15px;
            margin-top: 10px;
        '>
            <p style='color: #333; font-size: 18px; margin: 0;'>
                ✅ Portfolio uploaded successfully! Click <strong>'Analyze Portfolio'</strong> to continue
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 Portfolio Preview")
        st.dataframe(st.session_state.portfolio_data, use_container_width=True)
        
        if st.button("🔍 Analyze Portfolio", type="primary", use_container_width=True):
            if not st.session_state.authenticated:
                st.warning("Please login or register to analyze your portfolio")
                st.session_state.show_login = True
                st.rerun()
            else:
                st.session_state.analysis_complete = False
                with st.spinner("🔄 Fetching market data and analyzing portfolio..."):
                    analyze_portfolio()
    st.markdown('</div>', unsafe_allow_html=True)

def add_footer():
    """Add footer with disclaimer and company details"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 8px;'>
        <p style='font-size: 12px; color: #666; margin-bottom: 10px;'>
            <strong>Disclaimer:</strong> The information provided in this portfolio analysis is for informational purposes only 
            and should not be considered as financial advice. Investment decisions should be made after careful consideration 
            of your financial situation and in consultation with a qualified financial advisor. Past performance is not 
            indicative of future results.
        </p>
        <hr style='margin: 15px 0; border: 0; border-top: 1px solid #ddd;'>
        <p style='font-size: 13px; color: #333; margin-bottom: 5px;'>
            <strong>Alphalens</strong> is a product of <strong>Edhaz Financial Services Private Limited</strong>
        </p>
        <p style='font-size: 12px; color: #666; margin-bottom: 5px;'>
            Registered Office: Alpine Eco, Doddenekkundi, K R Puram Hobli, Bangalore 560037
        </p>
        <p style='font-size: 12px; color: #666;'>
            📧 <a href='mailto:hello@thealphamarket.com' style='color: #FF6B35; text-decoration: none;'>hello@thealphamarket.com</a> | 
            📞 <a href='tel:+919108967788' style='color: #FF6B35; text-decoration: none;'>+91-91089 67788</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
