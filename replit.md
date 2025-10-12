# Indian Stock Market Portfolio Analyzer

## Overview

This is a comprehensive Indian stock market portfolio analysis application built with Streamlit. It provides investors with detailed insights into their portfolio performance, including sector analysis, benchmark comparisons, historical tracking, and AI-driven investment recommendations. The application supports both value and growth investment perspectives, helping users make informed decisions about their stock holdings.

The system analyzes uploaded portfolio data, fetches real-time market information from Yahoo Finance, and generates actionable insights through multiple analytical lenses including individual stock performance, sector allocation, benchmark comparisons, and rebalancing suggestions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Problem:** Need an interactive, data-rich interface for portfolio analysis  
**Solution:** Streamlit-based web application with modular component architecture  
**Rationale:** Streamlit provides rapid development of data applications with built-in state management and easy integration with Python data science libraries

- **Main Application (app.py):** Entry point handling file uploads, session state management, and component orchestration
- **Component-Based UI:** Separate modules for each analytical view (dashboard, sector analysis, stock performance, benchmark comparison, recommendations, customer profile, rebalancing, historical performance)
- **Interactive Visualizations:** Plotly charts for dynamic, interactive data visualization including pie charts, bar graphs, line charts, and multi-panel subplots

**Design Pattern:** Modular component architecture where each UI component is a self-contained class with a `render()` method

### Backend Architecture  

**Problem:** Need to analyze portfolio data with real-time market information and generate recommendations  
**Solution:** Service-oriented architecture with specialized utility classes  
**Rationale:** Separation of concerns allows independent development and testing of data fetching, analysis, and recommendation logic

#### Core Services:

1. **Data Fetcher (utils/data_fetcher.py)**
   - Fetches real-time stock prices from Yahoo Finance API
   - Retrieves historical price data for performance tracking
   - Maintains mappings for stock categories (Large/Mid/Small Cap) and sectors
   - Provides market index data (NIFTY50, NIFTY_MIDCAP_100, NIFTY_SMALLCAP_100)
   - Handles both NSE (.NS) and BSE (.BO) stock symbols

2. **Portfolio Analyzer (utils/portfolio_analyzer.py)**
   - Calculates portfolio metrics (gains/losses, returns, allocation percentages)
   - Performs sector and category-wise analysis
   - Computes all-time highs since purchase date for each stock
   - Aggregates portfolio-level statistics (total investment, current value, profitable vs loss-making stocks)

3. **Recommendation Engine (utils/recommendation_engine.py)**
   - Dual-perspective analysis: Value investing and Growth investing viewpoints
   - Generates BUY/HOLD/SELL recommendations based on multiple factors
   - Analyzes fundamental data (P/E ratios, market cap, beta)
   - Provides alternative stock suggestions for diversification
   - Considers price performance, ATH comparisons, and risk metrics

4. **PDF Report Generator (utils/pdf_generator.py)**
   - Creates comprehensive portfolio reports using ReportLab
   - Includes tables, charts, and formatted analysis summaries
   - Exports portfolio snapshots for offline review

**Alternatives Considered:** Could have used Flask/Django for more control, but Streamlit's built-in features for data apps made it the optimal choice

**Pros:**
- Rapid development and iteration
- Built-in state management
- Excellent integration with data science libraries
- No frontend JavaScript required

**Cons:**
- Limited customization compared to full web frameworks
- Session-based architecture may have scalability limitations

### Data Storage Solutions

**Problem:** Need to process and analyze user portfolio data  
**Solution:** In-memory data processing with CSV file uploads  
**Rationale:** Lightweight approach suitable for personal portfolio analysis without need for persistent storage

- **Input Format:** CSV files with columns: Stock Name, Buy Price, Buy Date, Quantity
- **Data Processing:** Pandas DataFrames for all data manipulation and analysis
- **Session Storage:** Streamlit session_state for maintaining analysis results during user session
- **No Database:** Application is stateless; data persists only during active session

**Alternatives Considered:** Could implement database storage (SQLite/PostgreSQL) for historical tracking, but adds complexity for single-user analysis tool

**Pros:**
- Simple deployment with no database dependencies
- Fast in-memory processing
- Easy data import/export

**Cons:**
- No persistent storage of analysis history
- Cannot track portfolio changes over time without re-upload

### Authentication and Authorization

**Problem:** Not applicable for current implementation  
**Solution:** No authentication system implemented  
**Rationale:** Designed as a personal analysis tool for local use

- Application assumes single-user, local execution
- No user accounts or multi-tenancy
- Portfolio data is session-specific and temporary

**Future Consideration:** If deployed as multi-user service, would need to implement user authentication and portfolio data isolation

## External Dependencies

### Third-Party APIs

1. **Yahoo Finance (yfinance library)**
   - **Purpose:** Real-time and historical stock price data
   - **Integration:** Python yfinance library for NSE/BSE Indian stocks
   - **Data Retrieved:** Current prices, historical OHLCV data, fundamental metrics
   - **Symbols:** Supports .NS (NSE) and .BO (BSE) suffixed stock symbols

2. **Market Indices**
   - NIFTY50 (^NSEI)
   - NIFTY_MIDCAP_100 (^NSEMDCP50)  
   - NIFTY_SMALLCAP_100 (^NSESMLCAP)

### Python Libraries

**Data Processing:**
- pandas: DataFrame operations and data manipulation
- numpy: Numerical calculations and array operations

**Visualization:**
- plotly.express & plotly.graph_objects: Interactive charting
- matplotlib: Static chart generation for PDF reports

**Web Framework:**
- streamlit: Web application framework and UI components

**PDF Generation:**
- reportlab: PDF document creation with tables and formatting

**Date/Time:**
- datetime: Date calculations for buy dates and historical analysis

### External Services

**Problem:** Need reliable financial market data for Indian stocks  
**Solution:** Yahoo Finance API through yfinance library  
**Rationale:** Free, reliable, and comprehensive data source for Indian equity markets

**Pros:**
- No API key required
- Covers NSE and BSE stocks
- Includes fundamental data and indices
- Well-maintained Python library

**Cons:**
- Rate limiting may occur with high-frequency requests
- Dependent on Yahoo Finance uptime
- Limited to publicly available data
- No direct access to real-time Level 2 data

**Alternative Considered:** Alpha Vantage, NSE/BSE official APIs (require authentication and have limited free tiers)

## Recent Changes

### Bug Fixes (October 2025)

1. **Timezone Comparison Error Fix**
   - **Issue:** Application crashed with "Invalid comparison between dtype=datetime64[ns, Asia/Kolkata] and Timestamp" error
   - **Root Cause:** yfinance returns timezone-aware datetime objects (Asia/Kolkata) which couldn't be compared with timezone-naive buy dates from CSV
   - **Solution:** Normalized all datetime objects to timezone-naive format across the application:
     - `utils/data_fetcher.py`: Strip timezone from historical data and index data
     - `utils/portfolio_analyzer.py`: Normalize buy_date before comparison in ATH calculation
     - `components/historical_performance.py`: Normalize dates in portfolio history calculation
   - **Impact:** All datetime comparisons now work correctly without timezone conflicts

2. **Percentage Gain/Loss KeyError Fix**
   - **Issue:** Recommendation engine crashed with KeyError: 'Percentage Gain/Loss'
   - **Root Cause:** `analyze_portfolio()` works on a copy of portfolio_df and doesn't modify the original. When the original portfolio_df was passed to recommendation_engine, it lacked computed columns like 'Percentage Gain/Loss'
   - **Solution:** Create enriched_portfolio_df from analysis_results['stock_performance'] before passing to recommendation engine
   - **Files Changed:** `app.py` in both `analyze_portfolio()` and `refresh_prices()` functions
   - **Impact:** Recommendation engine now receives all computed metrics and works correctly

3. **Plotly API Parameter Fix**
   - **Issue:** Stock Performance tab crashed with "make_subplots() got unexpected keyword argument 'shared_xaxis'"
   - **Root Cause:** Incorrect parameter name - should be 'shared_xaxes' not 'shared_xaxis'
   - **Solution:** Updated `components/stock_performance.py` to use correct parameter
   - **Impact:** Price and volume charts now render correctly

4. **Graceful Error Handling for Missing Data**
   - **Issue:** Application could crash if stock price data fetch failed
   - **Solution:** Added fallback mechanisms:
     - Use `fillna(buy_price)` when current_price is NaN
     - Safe division for percentage calculations to prevent division by zero
   - **Files Changed:** `utils/portfolio_analyzer.py`
   - **Impact:** Application now handles missing data gracefully without crashes

### UI Redesign (October 2025)

**Goal:** Create a clean, professional, and centered UI with Alphamarket branding

1. **Alphamarket Logo Integration**
   - **Asset:** `attached_assets/Alphamarket Logo without Background_1760262013341.png`
   - **Implementation:** Logo displayed prominently at the top of the page in centered layout
   - **Impact:** Professional branding throughout the application

2. **Homepage Redesign**
   - **Previous:** Cluttered with extensive text about features, how it works, and supported analysis
   - **New Design:**
     - Clean, centered layout with minimal content
     - Prominent heading: "Comprehensive Indian Stock Market Analysis"
     - Centered upload card with dashed border (#FF6B35 brand color)
     - Simple call-to-action directing users to sidebar upload
   - **Impact:** Improved user experience with cleaner, more focused interface

3. **Informational Content Reorganization**
   - **Moved Content:** "How It Works", "Features Included", and "Supported Analysis" sections
   - **New Location:** Expandable "About & Features" section in sidebar
   - **Benefit:** Homepage remains uncluttered while information stays accessible
   - **Content Included:**
     - CSV format requirements
     - Step-by-step workflow explanation
     - Complete feature list
     - Supported analysis types

4. **Enhanced UI Elements**
   - **Sidebar:** Clean portfolio upload section with improved button styling
   - **Notifications:** Professional styling for success messages with brand colors
   - **Spacing:** Consistent vertical and horizontal spacing throughout
   - **Buttons:** Full-width buttons for better mobile experience
   - **Colors:** Consistent use of #FF6B35 (Alphamarket orange) for primary actions and highlights

5. **Design Philosophy**
   - **Minimalist Approach:** Focus on essential actions (upload and analyze)
   - **Progressive Disclosure:** Information available through expandable sections
   - **Visual Hierarchy:** Clear distinction between primary actions and secondary information
   - **Brand Consistency:** Alphamarket colors and logo integrated throughout

### Layout Refinement (October 2025)

**Goal:** Move informational content from sidebar to main page for better visibility

1. **Sidebar Simplification**
   - **Removed:** "About & Features" expandable section from sidebar
   - **Kept:** Portfolio Upload and Sample CSV Download sections only
   - **Impact:** Cleaner, more focused sidebar with essential upload functionality

2. **Main Page Content Enhancement**
   - **Updated Heading:** "Portfolio Analysis - Comprehensive Analysis of Your Stock Portfolio based on both Value and Growth Investing"
   - **Informational Sections Added to Welcome Screen:**
     - CSV Format Required (column descriptions)
     - How It Works (4-step process)
     - Features Included (all 8 features listed)
     - Dual Investment Perspectives (Value & Growth investing explanations)
     - Advanced Risk Metrics description
     - Call-to-action message
   - **Layout:** Two-column design for CSV Format and Features, full-width for Investment Perspectives
   - **Impact:** All essential information visible on main page before analysis

3. **Application Flow**
   - **Welcome Screen:** Shows all informational content and upload instructions
   - **After Upload:** Portfolio preview displayed with call-to-action to analyze
   - **After Analysis:** Welcome screen replaced by Dashboard with 8 analytical tabs
   - **Design Rationale:** Progressive disclosure - users see getting started info first, then analysis results

### Testing Status
- **End-to-End Testing:** PASSED (October 2025)
- All 8 analytical tabs verified working correctly
- Portfolio upload, analysis, refresh, and PDF export functional
- Real-time price updates working
- Rebalancing and historical performance features operational
- **UI/UX Testing:** PASSED - Clean, centered design with Alphamarket branding verified