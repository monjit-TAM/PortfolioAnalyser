import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from utils.data_fetcher import DataFetcher
from utils.portfolio_analyzer import PortfolioAnalyzer
from utils.recommendation_engine import RecommendationEngine
from components.dashboard import Dashboard
from components.sector_analysis import SectorAnalysis
from components.stock_performance import StockPerformance
from components.benchmark_comparison import BenchmarkComparison
from components.recommendations import Recommendations
from components.customer_profile import CustomerProfile

def main():
    st.set_page_config(
        page_title="Indian Stock Market Portfolio Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Indian Stock Market Portfolio Analyzer")
    st.markdown("### Comprehensive Portfolio Analysis with Value & Growth Investment Perspectives")
    
    # Initialize session state
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("📁 Portfolio Upload")
        st.markdown("Upload your portfolio CSV file with the following columns:")
        st.markdown("- **Stock Name** (e.g., RELIANCE, TCS, INFY)")
        st.markdown("- **Buy Price** (in ₹)")
        st.markdown("- **Buy Date** (YYYY-MM-DD)")
        st.markdown("- **Quantity** (number of shares)")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload a CSV file with your portfolio data"
        )
        
        if uploaded_file is not None:
            try:
                # Read and validate CSV
                portfolio_df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['Stock Name', 'Buy Price', 'Buy Date', 'Quantity']
                missing_columns = [col for col in required_columns if col not in portfolio_df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    # Data validation and cleaning
                    portfolio_df['Buy Date'] = pd.to_datetime(portfolio_df['Buy Date'])
                    portfolio_df['Buy Price'] = pd.to_numeric(portfolio_df['Buy Price'], errors='coerce')
                    portfolio_df['Quantity'] = pd.to_numeric(portfolio_df['Quantity'], errors='coerce')
                    
                    # Remove rows with invalid data
                    portfolio_df = portfolio_df.dropna()
                    
                    if len(portfolio_df) == 0:
                        st.error("No valid data found in the uploaded file.")
                    else:
                        st.success(f"Successfully loaded {len(portfolio_df)} stocks")
                        st.session_state.portfolio_data = portfolio_df
                        
                        # Analysis button
                        if st.button("🔍 Analyze Portfolio", type="primary"):
                            st.session_state.analysis_complete = False
                            with st.spinner("Fetching market data and analyzing portfolio..."):
                                analyze_portfolio()
                            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Sample CSV download
        st.markdown("---")
        st.subheader("📥 Sample CSV Format")
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
            mime="text/csv"
        )
    
    # Main content area
    if st.session_state.portfolio_data is not None and st.session_state.analysis_complete:
        display_analysis()
    elif st.session_state.portfolio_data is not None:
        st.info("👆 Click 'Analyze Portfolio' in the sidebar to start the analysis.")
        st.subheader("📋 Uploaded Portfolio Preview")
        st.dataframe(st.session_state.portfolio_data, use_container_width=True)
    else:
        # Welcome screen
        display_welcome_screen()

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
            current_data[stock_name] = current_price
            historical_data[stock_name] = hist_data
            
            progress_bar.progress((idx + 1) / len(portfolio_df))
        
        st.text("Analyzing portfolio performance...")
        
        # Perform analysis
        analysis_results = portfolio_analyzer.analyze_portfolio(
            portfolio_df, current_data, historical_data
        )
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            portfolio_df, current_data, historical_data, analysis_results
        )
        
        # Store results in session state
        st.session_state.analysis_results = analysis_results
        st.session_state.recommendations = recommendations
        st.session_state.current_data = current_data
        st.session_state.historical_data = historical_data
        st.session_state.analysis_complete = True
        
        progress_bar.progress(1.0)
        st.success("Analysis complete!")
        
        # Auto-rerun to display results
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        st.session_state.analysis_complete = False

def display_analysis():
    """Display comprehensive portfolio analysis"""
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "🏭 Sector Analysis", 
        "📈 Stock Performance", 
        "📊 Benchmark Comparison", 
        "💡 Recommendations", 
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
        customer_profile = CustomerProfile()
        customer_profile.render(
            st.session_state.analysis_results,
            st.session_state.portfolio_data,
            st.session_state.recommendations
        )

def display_welcome_screen():
    """Display welcome screen with instructions"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🚀 Welcome to Portfolio Analyzer
        
        ### How it works:
        
        1. **📁 Upload Portfolio**: Upload a CSV file with your stock holdings
        2. **🔍 Analyze**: Our system fetches real-time data and analyzes your portfolio
        3. **📊 Review**: Get comprehensive insights across multiple perspectives
        4. **💡 Act**: Receive personalized investment recommendations
        
        ### Features Include:
        
        - **📊 Portfolio Dashboard**: Current value, gains/losses, returns
        - **🏭 Sector Analysis**: Diversification and allocation insights
        - **📈 Stock Performance**: Individual stock tracking and metrics
        - **📊 Benchmark Comparison**: Compare against NIFTY indices
        - **💡 Smart Recommendations**: Value & Growth investment perspectives
        - **👤 Investor Profile**: Personalized investment style analysis
        
        ### Supported Analysis:
        
        - **Value Investing Perspective**: Focus on undervalued stocks with strong fundamentals
        - **Growth Investing Perspective**: Emphasis on growth potential and momentum
        - **Risk Assessment**: Portfolio risk analysis and diversification metrics
        - **Alternative Suggestions**: Better investment opportunities when sell is recommended
        
        ---
        
        **Ready to start?** Upload your portfolio CSV file using the sidebar! 👈
        """)

if __name__ == "__main__":
    main()
