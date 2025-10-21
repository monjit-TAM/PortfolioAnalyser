# Indian Stock Market Portfolio Analyzer

## Overview

This Streamlit application offers comprehensive Indian stock market portfolio analysis, providing investors with detailed insights into performance, including sector analysis, benchmark comparisons, historical tracking, and AI-driven investment recommendations. It supports both value and growth investment perspectives, helping users make informed decisions based on uploaded portfolio data and real-time market information from Yahoo Finance. The system generates actionable insights across individual stock performance, sector allocation, benchmark comparisons, and rebalancing suggestions.

## Recent Changes (October 2025)

### Bug Fixes Completed:
1. **Double Suffix Bug** (CRITICAL): Fixed data_fetcher.py to prevent duplicate .NS/.BO suffixes when stock names already include exchange identifiers (e.g., TCS.NS was becoming TCS.NS.NS)
2. **Series Formatting Errors**: Resolved multiple pandas Series-to-scalar conversion issues in stock_performance.py for metrics like volatility, ATH, max drawdown, and potential gains
3. **Historical Performance ValueError**: Fixed "Series is ambiguous" error in historical_performance.py by ensuring price values are scalars before calculations
4. **Price Fetching**: Uses yf.download() method for reliable end-of-day price data from Yahoo Finance
5. **UI/UX**: Removed gradient background from upload section for cleaner, more professional appearance
6. **Symbol Alias System** (NEW): Implemented intelligent stock symbol mapping to automatically convert common abbreviations to correct Yahoo Finance symbols
7. **Advanced Risk Metrics Removed**: Removed the Advanced Risk Metrics section from both the dashboard and PDF report due to calculation issues. The application now focuses on core portfolio analysis features including performance tracking, sector analysis, and recommendations.
8. **Branding Update**: Updated logo from Alphamarket to Alphalens across all pages (web interface and PDF reports)
9. **Compact Layout Update**: Redesigned homepage layout to be more compact and fit within one screen without scrolling. Logo repositioned to top-right corner (enlarged to 250px width), reduced whitespace throughout, and optimized spacing between sections.
10. **Footer Addition**: Added professional footer with disclaimer and company details (Edhaz Financial Services Private Limited, registered office address, email, and phone number)
11. **Hero Banner Addition**: Added full-width edge-to-edge hero banner image showcasing portfolio analysis concepts (VALUE, GROWTH, BUY, HOLD, SELL)
12. **Ultra-Compact Spacing**: Further optimized vertical spacing - reduced gap between logo and Portfolio Analysis heading to ~40px, minimized all section margins for tighter layout

### Symbol Alias Support:
The application now intelligently handles common stock abbreviations:
- **RIL** → RELIANCE (Reliance Industries)
- **ICICI** → ICICIBANK (ICICI Bank)
- **HDFC** → HDFCBANK (HDFC Bank)
- **SBI** → SBIN (State Bank of India)
- **KOTAK** → KOTAKBANK (Kotak Mahindra Bank)
- And many more common abbreviations

### CSV Format Support:
The application now accepts stock names in three formats:
- Base names without suffix (e.g., TCS, RELIANCE) - system automatically adds .NS/.BO
- Full symbols with suffix (e.g., TCS.NS, RELIANCE.NS) - system uses as-is without modification
- Common abbreviations (e.g., RIL, ICICI, HDFC) - system automatically converts to correct symbols

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

The application uses Streamlit to create an interactive, data-rich interface for portfolio analysis. It employs a modular component architecture where each UI component is a self-contained class. Plotly is used for dynamic and interactive data visualizations.

### Backend Architecture

The backend utilizes a service-oriented architecture with specialized utility classes for data fetching, analysis, and recommendations.

#### Core Services:

1.  **Data Fetcher:** Retrieves real-time and historical stock prices, market index data (NIFTY50, NIFTY_MIDCAP_100, NIFTY_SMALLCAP_100), and stock category mappings from Yahoo Finance API for both NSE (.NS) and BSE (.BO) symbols.
2.  **Portfolio Analyzer:** Calculates portfolio metrics (gains/losses, returns, allocation), performs sector and category analysis, computes all-time highs, and aggregates portfolio-level statistics.
3.  **Recommendation Engine:** Provides dual-perspective (Value/Growth) BUY/HOLD/SELL recommendations based on fundamental data, price performance, and risk metrics, including alternative stock suggestions for diversification.
4.  **PDF Report Generator:** Creates comprehensive portfolio reports with tables, charts, and analysis summaries using ReportLab.

### Data Storage Solutions

The application processes user portfolio data in-memory using Pandas DataFrames. It relies on CSV file uploads (Stock Name, Buy Price, Buy Date, Quantity) and Streamlit's `session_state` for maintaining analysis results during a user session, without persistent database storage.

### Authentication and Authorization

The current implementation does not include an authentication system, as it is designed as a personal analysis tool for local, single-user execution.

### UI/UX Design

The application features a premium, professional design with a focus on a single-page experience. The sidebar has been removed, and all functionality, including file upload, is integrated into the main page. It utilizes clean, professional styling with the Alphalens logo (250px width) positioned in the top-right corner for branding. The layout is optimized for compactness with minimal whitespace to fit the entire homepage within one screen view. The upload section features a streamlined design without background gradients for a more refined appearance. Informational content, such as CSV format requirements and features, is presented concisely or in expandable sections. A professional footer displays disclaimer text and company details including registered office, email (hello@thealphamarket.com), and phone (+91-91089 67788).

## External Dependencies

### Third-Party APIs

1.  **Yahoo Finance (via `yfinance` library):** Used for fetching real-time and historical stock price data, including OHLCV data, fundamental metrics, and market indices (^NSEI, ^NSEMDCP50, ^NSESMLCAP) for Indian stocks (.NS and .BO suffixes).

### Python Libraries

*   **Data Processing:** `pandas`, `numpy`
*   **Visualization:** `plotly.express`, `plotly.graph_objects`, `matplotlib`
*   **Web Framework:** `streamlit`
*   **PDF Generation:** `reportlab`
*   **Date/Time:** `datetime`