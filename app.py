import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

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
from components.rebalancing import PortfolioRebalancing
from components.historical_performance import HistoricalPerformance
from utils.pdf_generator import PDFReportGenerator

def main():
    st.set_page_config(
        page_title="Alphalens Portfolio Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for compact layout and full-width banner
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
        /* Full width image container */
        .stImage {
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
        /* Add padding back for content sections */
        .content-section {
            padding-left: 5rem;
            padding-right: 5rem;
        }
        /* Hero header flexbox container for tight logo+heading layout */
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
    </style>
    """, unsafe_allow_html=True)
    
    
    # Initialize session state
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Main content area
    if st.session_state.portfolio_data is not None and st.session_state.analysis_complete:
        display_analysis()
    elif st.session_state.portfolio_data is not None:
        display_portfolio_preview()
    else:
        # Welcome screen with integrated upload
        display_welcome_screen()
    
    # Footer with disclaimer and company details
    add_footer()

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
    
    # Add controls for refresh and PDF download
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col2:
        if st.button("🔄 Refresh Prices", type="secondary", help="Update with latest stock prices"):
            with st.spinner("Refreshing prices..."):
                refresh_prices()
    
    with col3:
        # Generate PDF report
        if st.button("📄 Download Report", type="primary", help="Generate comprehensive PDF report"):
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_gen = PDFReportGenerator()
                    filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf_gen.generate_report(
                        st.session_state.analysis_results,
                        st.session_state.portfolio_data,
                        st.session_state.recommendations,
                        filename
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
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh", value=False, help="Auto-refresh every 5 minutes")
        if auto_refresh:
            import time
            time.sleep(300)  # 5 minutes
            st.rerun()
    
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
    """Display clean welcome screen with integrated file upload"""
    
    # Logo in top-right with reduced spacing
    col1, col2 = st.columns([2.5, 1])
    with col2:
        st.image("attached_assets/Alphalens_1760976199318.png", width=250)
    
    # Heading section - minimal spacing
    st.markdown("""
    <div class="content-section" style='text-align: center; margin-top: -15px; padding-top: 0px; margin-bottom: 8px;'>
        <h2 style='color: #FF6B35; margin-bottom: 5px; margin-top: 0px; font-size: 26px; font-weight: 600;'>
            Portfolio Analysis
        </h2>
        <p style='font-size: 15px; color: #666; margin-bottom: 0px;'>
            Comprehensive Analysis of Your Stock Portfolio based on both Value and Growth Investing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero banner image with targeted CSS
    st.markdown("""
    <style>
    /* Target hero banner by image index */
    div[data-testid="stImage"]:nth-of-type(2) img {
        max-height: 125px !important;
        object-fit: cover !important;
        object-position: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load and display hero banner
    try:
        hero_image = Image.open("attached_assets/PortfolioAnalysisherobanner_1761113423621.png")
        st.image(hero_image, use_container_width=True)
    except:
        # Fallback to old banner if new one fails
        st.image("attached_assets/BzIo2GnlaVnXUEmTRTUqs_1760986532963.png", use_container_width=True)
    
    # Upload section - clean and integrated into main page (with padding)
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("""
        <h3 style='color: #FF6B35; text-align: center; margin-bottom: 10px; margin-top: 10px; font-size: 20px;'>
            📁 Upload Your Portfolio
        </h3>
        """, unsafe_allow_html=True)
        
        # File uploader integrated
        uploaded_file = st.file_uploader(
            "Drag and drop your CSV file here or browse",
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
                        
                        if st.button("🔍 Analyze Portfolio", type="primary", use_container_width=True):
                            st.session_state.analysis_complete = False
                            with st.spinner("🔄 Fetching market data and analyzing portfolio..."):
                                analyze_portfolio()
                            
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        # Sample CSV download
        col_a, col_b, col_c = st.columns([1, 2, 1])
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
    
    # Key features - clean and concise
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 12px; background-color: #f8f9fa; border-radius: 6px; height: 100%;'>
            <h3 style='color: #FF6B35; margin-bottom: 8px; font-size: 16px;'>📊 Dual Perspectives</h3>
            <p style='color: #666; font-size: 13px; margin: 0;'>
                Get insights from both <strong>Value</strong> and <strong>Growth</strong> investing viewpoints
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 12px; background-color: #f8f9fa; border-radius: 6px; height: 100%;'>
            <h3 style='color: #FF6B35; margin-bottom: 8px; font-size: 16px;'>📈 Advanced Analytics</h3>
            <p style='color: #666; font-size: 13px; margin: 0;'>
                Sector analysis, benchmark comparison, and performance tracking
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 12px; background-color: #f8f9fa; border-radius: 6px; height: 100%;'>
            <h3 style='color: #FF6B35; margin-bottom: 8px; font-size: 16px;'>💡 Smart Recommendations</h3>
            <p style='color: #666; font-size: 13px; margin: 0;'>
                Actionable insights with rebalancing suggestions and alternative stock picks
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # CSV Format info - minimal
    with st.expander("📋 CSV Format & Requirements"):
        col_x, col_y = st.columns(2)
        with col_x:
            st.markdown("""
            **Required Columns:**
            - Stock Name (e.g., RELIANCE, TCS)
            - Buy Price (in ₹)
            - Buy Date (YYYY-MM-DD)
            - Quantity (number of shares)
            """)
        with col_y:
            st.markdown("""
            **Analysis Features:**
            - Portfolio Dashboard & Performance
            - Sector & Category Breakdown
            - Benchmark Comparison (NIFTY)
            - Stock Recommendations & Rebalancing
            """)
    st.markdown('</div>', unsafe_allow_html=True)

def display_portfolio_preview():
    """Display portfolio preview after upload"""
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
