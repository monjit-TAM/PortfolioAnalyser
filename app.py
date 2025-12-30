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
from components.homepage import (
    render_modern_homepage, render_upload_section, render_features_section,
    render_how_it_works_section, render_cta_section, render_csv_requirements
)

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
    """Render compact top header with logo left and auth buttons far right"""
    col_logo, col_spacer, col_auth = st.columns([1.2, 2.5, 1.3])
    
    with col_logo:
        st.image("attached_assets/AlphaMarket_(2)_1767079367380.png", width=280)
    
    with col_auth:
        st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)
        if st.session_state.authenticated:
            user_name = st.session_state.user.get('full_name') or st.session_state.user.get('email', 'User')
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"<div style='text-align: right; padding-top: 5px; color: #28a745; font-weight: 600;'>✅ {user_name[:12]}</div>", unsafe_allow_html=True)
            with c2:
                if st.session_state.user.get('is_admin'):
                    if st.button("📊 Admin", key="admin_top", use_container_width=True):
                        st.session_state.show_admin = True
                        st.rerun()
            with c3:
                if st.button("🚪 Logout", key="logout_top", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.session_state.portfolio_data = None
                    st.session_state.analysis_complete = False
                    st.session_state.show_admin = False
                    st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Login", key="login_top", use_container_width=True):
                    st.session_state.show_login = True
                    st.rerun()
            with c2:
                if st.button("SignUp", key="register_top", type="primary", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()
    
    st.markdown("<hr style='margin: 5px 0 15px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

def render_auth_header():
    with st.sidebar:
        st.image("attached_assets/AlphaMarket_(2)_1767079367380.png", width=250)
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
    """Display modern, sleek welcome screen"""
    
    if st.session_state.show_login:
        render_top_header()
        display_login_modal()
        return
    
    if st.session_state.show_signup:
        render_top_header()
        display_signup_modal()
        return
    
    render_top_header()
    
    st.markdown("""
    <style>
        .hero-section { text-align: center; padding: 60px 20px 40px 20px; max-width: 800px; margin: 0 auto; }
        .hero-title { font-size: 48px; font-weight: 800; color: #1a1a1a; line-height: 1.2; margin-bottom: 20px; letter-spacing: -1px; }
        .hero-subtitle { font-size: 18px; color: #666; line-height: 1.6; max-width: 600px; margin: 0 auto 30px auto; text-align: center; }
        .section-title { font-size: 32px; font-weight: 700; color: #1a1a1a; text-align: center; margin-bottom: 10px; }
        .section-subtitle { font-size: 16px; color: #888; text-align: center; margin-bottom: 40px; }
        .feature-card { background: #fff; border: 1px solid #e8e8e8; border-radius: 12px; padding: 30px 20px; text-align: left; min-height: 200px; }
        .feature-icon { width: 48px; height: 48px; background: #f5f5f5; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; font-size: 24px; }
        .feature-title { font-size: 18px; font-weight: 600; color: #1a1a1a; margin-bottom: 10px; }
        .feature-desc { font-size: 14px; color: #666; line-height: 1.6; }
        .step-number { width: 40px; height: 40px; background: #1a1a1a; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; margin: 0 auto 20px auto; }
        .step-icon { font-size: 32px; margin-bottom: 15px; color: #1a1a1a; }
        .step-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 8px; }
        .step-desc { font-size: 14px; color: #888; line-height: 1.5; }
        .cta-section { background: #fafafa; padding: 60px 20px; text-align: center; border-radius: 16px; margin: 40px 0; }
        .cta-title { font-size: 28px; font-weight: 700; color: #1a1a1a; margin-bottom: 15px; }
        .cta-subtitle { font-size: 16px; color: #666; margin-bottom: 30px; }
        .stButton > button[kind="primary"] { background-color: #e31837 !important; border-color: #e31837 !important; }
        .stButton > button[kind="primary"]:hover { background-color: #c41530 !important; border-color: #c41530 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Analyze Your Portfolio.<br>Generate Alpha.</h1>
        <p class="hero-subtitle">
            Upload your Stock Portfolio and get instant insight on performance, risk analysis and actionable recommendations to maximize returns.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if not st.session_state.authenticated:
            if st.button("Get Started", type="primary", use_container_width=True, key="hero_start"):
                st.session_state.show_signup = True
                st.rerun()
    
    if st.session_state.authenticated:
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Optimize Your Portfolio?</h2>
        <p class="cta-subtitle">Join thousands of investors using data-driven insights to make better investment decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if not st.session_state.authenticated:
            if st.button("Get Started Free", type="primary", use_container_width=True, key="cta_start"):
                st.session_state.show_signup = True
                st.rerun()
    
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
