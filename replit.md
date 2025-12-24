# Indian Stock Market Portfolio Analyzer

## Overview

This Streamlit application provides comprehensive Indian stock market portfolio analysis, offering investors detailed insights into performance, including sector analysis, benchmark comparisons, historical tracking, and AI-driven investment recommendations. It supports both value and growth investment perspectives, aiding informed decision-making based on uploaded portfolio data and real-time market information. The system generates actionable insights across individual stock performance, sector allocation, benchmark comparisons, and rebalancing suggestions. The project's ambition is to provide a robust, data-driven tool for individual investors to optimize their Indian stock portfolios.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### System Design

The application employs a modular, service-oriented architecture. It integrates user authentication with PostgreSQL, dynamic stock data loading from a database, and real-time price feeds via TrueData API with Yahoo Finance as a fallback. All charts for PDF generation are rendered using Matplotlib to ensure reliability in various environments.

### Frontend Architecture

The frontend is built with Streamlit, providing an interactive, single-page user interface. The UI/UX prioritizes a clean, professional design with minimal whitespace, a compact layout, and integrated functionality. Key visual elements include the Alphalens logo, a hero banner, and a professional footer.

### Backend Architecture

The backend consists of core services:
1.  **Data Fetcher:** Retrieves real-time and historical stock data from TrueData (primary) and Yahoo Finance (fallback), and market indices.
2.  **Portfolio Analyzer:** Calculates performance metrics, allocation, and aggregates statistics.
3.  **Recommendation Engine:** Provides dual-perspective (Value/Growth) BUY/HOLD/SELL recommendations and alternative stock suggestions.
4.  **PDF Report Generator:** Creates comprehensive reports with embedded Matplotlib charts using ReportLab.
5.  **Authentication Manager:** Handles user login, signup, and session management using PostgreSQL for user data.

### Data Storage Solutions

User authentication details, dynamic stock symbols, aliases, market indices, sectors, alternative stock suggestions, and rebalancing strategies are stored in a PostgreSQL database. User portfolio data for analysis is processed in-memory using Pandas DataFrames and Streamlit's `session_state`.

### Technical Implementations

-   **Authentication:** Secure password hashing (PBKDF2-SHA256) and session management.
-   **Dynamic Data:** Database-driven configuration for stock symbols, sectors, and investment strategies.
-   **Real-time Data:** WebSocket client for TrueData API, with fallback to Yahoo Finance.
-   **PDF Generation:** Matplotlib-based chart rendering using the Agg backend for reliable PDF embedding.
-   **Symbol Aliases:** Intelligent mapping system for common stock abbreviations to correct Yahoo Finance symbols.
-   **CSV Support:** Accepts stock names in base names, full symbols, or common abbreviations.

## External Dependencies

### Third-Party APIs

1.  **TrueData API:** WebSocket-based for real-time stock price streaming.
2.  **Yahoo Finance (via `yfinance` library):** Used for historical and end-of-day stock price data, fundamental metrics, and market indices, also serves as a fallback for live prices.

### Databases

1.  **PostgreSQL:** Used for user authentication, storing stock symbols, aliases, market indices, sectors, alternative stocks, and rebalancing strategies.

### Python Libraries

*   **Data Processing:** `pandas`, `numpy`
*   **Visualization:** `plotly.express`, `plotly.graph_objects`, `matplotlib`
*   **Web Framework:** `streamlit`
*   **PDF Generation:** `reportlab`
*   **Date/Time:** `datetime`
*   **Database Interaction:** `psycopg2`
*   **Authentication Hashing:** `hashlib`