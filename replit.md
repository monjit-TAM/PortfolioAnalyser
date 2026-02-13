# Indian Stock Market Portfolio Analyzer

## Overview

This Streamlit application provides comprehensive Indian stock market portfolio analysis, offering investors detailed insights into performance, including sector analysis, benchmark comparisons, historical tracking, and AI-driven investment recommendations. It supports value, growth, and quantamental (fundamental + technical) investment perspectives, aiding informed decision-making based on uploaded portfolio data and real-time market information. The system generates actionable insights across individual stock performance, sector allocation, benchmark comparisons, and rebalancing suggestions. The project's ambition is to provide a robust, data-driven tool for individual investors to optimize their Indian stock portfolios.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### System Design

The application employs a modular, service-oriented architecture. It integrates user authentication with PostgreSQL, dynamic stock data loading from a database, and real-time price feeds via TrueData API with Yahoo Finance as a fallback. All charts for PDF generation are rendered using Matplotlib to ensure reliability in various environments.

### Frontend Architecture

The frontend is built with Streamlit, providing an interactive, single-page user interface. The UI/UX follows a modern, portfoliosmith-inspired design with:

**Homepage Design (components/homepage.py):**
- Hero section with gradient background (purple/indigo), stats row, and CTA button
- Feature cards grid showcasing 6 key capabilities (Performance Analytics, Risk Assessment, Behavioral Insights, Expert Recommendations, Portfolio Rebalancing, Tax Impact)
- Insights alternating sections highlighting Post-Analysis, Behavioral Biases, and Actionable Insights
- "How It Works" section with 3 numbered steps (Upload → Analyze → Insights)
- CTA section with gradient background for signup conversion
- CSV requirements section for user guidance
- Professional footer with disclaimer

**Visual Design:**
- Color scheme: Primary gradient (#667eea to #764ba2), white backgrounds, subtle shadows
- Typography: Inter font family via Google Fonts
- Cards with hover effects, rounded corners (16-24px), and subtle borders
- Mobile-responsive grid layouts for feature cards and insights sections

### Backend Architecture

The backend consists of core services:
1.  **Data Fetcher:** Retrieves real-time and historical stock data from Twelve Data (primary) → Alpha Vantage → Yahoo Finance (fallback), and market indices.
2.  **Portfolio Analyzer:** Calculates performance metrics, allocation, and aggregates statistics. Includes corporate actions adjustments (bonus, splits).
3.  **Recommendation Engine:** Provides dual-perspective (Value/Growth) BUY/HOLD/SELL recommendations and alternative stock suggestions.
4.  **PDF Report Generator:** Creates comprehensive reports with embedded Matplotlib charts using ReportLab.
5.  **Authentication Manager:** Handles user login, signup, and session management using PostgreSQL for user data.
6.  **Portfolio Advisor:** Interactive advisor module that answers questions about portfolio metrics, recommendations, sector analysis, benchmark comparisons, and rebalancing strategies.
7.  **Advanced Metrics Calculator:** Provides 10-layer institutional-grade analysis including structural diagnostics, style analysis, concentration risk, volatility metrics, behavior analysis, drift analysis, overlap detection, return attribution, liquidity risk, tail risk, macro sensitivity, health score, and scenario analysis.
8.  **Corporate Actions Manager:** Adjusts buy prices and quantities for bonus issues and stock splits to ensure accurate performance calculations.
9.  **Portfolio Summary (components/portfolio_summary.py):** One-page layman-friendly summary with key metrics, winners/losers, action items, risk/tax overview, multi-language support (13 Indian languages), and text-to-speech audio generation using OpenAI gpt-audio model.

### REST API Architecture (FastAPI)

The FastAPI REST API provides programmatic access for broker platform integration:

**API Location:** `/api/` directory, runs on port 8000
**Documentation:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

**Router Modules:**
- `api/routers/auth.py` - Authentication endpoints (login, signup, token refresh, API keys)
- `api/routers/portfolio.py` - Portfolio analysis (upload CSV, analyze, quick-analyze)
- `api/routers/recommendations.py` - Investment recommendations (value/growth analysis)
- `api/routers/advanced_metrics.py` - 10-layer metrics, health score, risk radar, tax impact
- `api/routers/rebalancing.py` - Rebalancing suggestions, concentration alerts
- `api/routers/websocket.py` - Real-time portfolio price updates (JWT authenticated)

**Authentication:**
- JWT Bearer tokens for user sessions (30-minute expiry)
- API keys for programmatic access by broker platforms
- WebSocket connections require JWT token as query parameter

**Key Endpoints:**
- `POST /api/v1/auth/login` - User login, returns JWT token
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/portfolio/analyze` - Full portfolio analysis
- `GET /api/v1/recommendations/{portfolio_id}` - Get recommendations
- `GET /api/v1/metrics/{portfolio_id}/full` - All 10 layers of analysis
- `GET /api/v1/metrics/{portfolio_id}/tax-impact` - Tax classification
- `WS /api/v1/ws/portfolio/{client_id}?token=<jwt>` - Real-time updates

**Scalability Notes:**
- Designed for 1000+ daily users
- For horizontal scaling, integrate Redis pub/sub for WebSocket connections
- Rate limiting: 100 req/min standard, 1000 req/min premium

### Data Storage Solutions

User authentication details, dynamic stock symbols, aliases, market indices, sectors, alternative stock suggestions, and rebalancing strategies are stored in a PostgreSQL database. User portfolio data for analysis is processed in-memory using Pandas DataFrames and Streamlit's `session_state`.

### Technical Implementations

-   **Authentication:** Secure password hashing (PBKDF2-SHA256) and session management.
-   **Dynamic Data:** Database-driven configuration for stock symbols, sectors, and investment strategies.
-   **Real-time Data:** WebSocket client for TrueData API, with fallback to Yahoo Finance.
-   **PDF Generation:** Matplotlib-based chart rendering using the Agg backend for reliable PDF embedding.
-   **Symbol Aliases:** Intelligent mapping system for common stock abbreviations to correct Yahoo Finance symbols.
-   **CSV Support:** Accepts stock names in base names, full symbols, or common abbreviations.

## Payment Gateway

-   **Status:** Razorpay integration in place but API keys need verification
-   **Subscription requirement:** Temporarily disabled pending payment gateway fix
-   **Alternative options:** Cashfree, PayU (both work well in India)
-   **Price:** ₹499/month (discounted from ₹999)
-   **Note:** User dismissed Stripe integration (not available in India)

## External Dependencies

### Third-Party APIs

1.  **TrueData API:** WebSocket-based for real-time stock price streaming.
2.  **Yahoo Finance (via `yfinance` library):** Used for historical and end-of-day stock price data, fundamental metrics, and market indices, also serves as a fallback for live prices.
3.  **Razorpay:** Payment gateway for subscriptions (needs API key verification).

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