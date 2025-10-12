# Indian Stock Market Portfolio Analyzer

## Overview

This Streamlit application offers comprehensive Indian stock market portfolio analysis, providing investors with detailed insights into performance, including sector analysis, benchmark comparisons, historical tracking, and AI-driven investment recommendations. It supports both value and growth investment perspectives, helping users make informed decisions based on uploaded portfolio data and real-time market information from Yahoo Finance. The system generates actionable insights across individual stock performance, sector allocation, benchmark comparisons, and rebalancing suggestions.

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

The application features a premium, professional design with a focus on a single-page experience. The sidebar has been removed, and all functionality, including file upload, is integrated into the main page. It utilizes a gradient purple background for the upload card, professional typography, and a clean layout with feature cards highlighting dual investment perspectives, advanced analytics, and smart recommendations. The Alphamarket logo and #FF6B35 accent color are consistently used for branding. Informational content, such as CSV format requirements and features, is presented concisely or in expandable sections.

## External Dependencies

### Third-Party APIs

1.  **Yahoo Finance (via `yfinance` library):** Used for fetching real-time and historical stock price data, including OHLCV data, fundamental metrics, and market indices (^NSEI, ^NSEMDCP50, ^NSESMLCAP) for Indian stocks (.NS and .BO suffixes).

### Python Libraries

*   **Data Processing:** `pandas`, `numpy`
*   **Visualization:** `plotly.express`, `plotly.graph_objects`, `matplotlib`
*   **Web Framework:** `streamlit`
*   **PDF Generation:** `reportlab`
*   **Date/Time:** `datetime`