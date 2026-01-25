import streamlit as st

class Methodology:
    def render(self):
        """Render comprehensive methodology and formulas documentation"""
        
        st.header("📐 Analysis Methodology & Formulas")
        st.write("Complete documentation of all calculations, theories, and recommendation frameworks used in Alphalens Portfolio Analyzer")
        
        st.divider()
        
        # Table of Contents
        st.subheader("📋 Table of Contents")
        st.markdown("""
1. Basic Portfolio Metrics & Calculations
2. Sector & Category Analysis
3. Benchmark Comparison Methodology
4. Value Investing Framework
5. Growth Investing Framework
6. Recommendation Engine Logic
7. Portfolio Score Calculation
8. Rebalancing Strategy Framework
9. Risk Metrics & Correlation
10. Limitations & Disclaimers
11. **Advanced Portfolio Metrics** (NEW)
    - Structural Diagnostics
    - Style Analysis
    - Concentration Risk
    - Volatility & Drawdown
    - Behavior Analysis
    - Drift Analysis
    - Overlap Detection
    - Return Attribution
    - Liquidity Risk
    - Tail Risk
    - Macro Sensitivity
    - Health Score
    - Scenario Analysis
        """)
        
        st.divider()
        
        # Section 1: Basic Portfolio Metrics
        st.subheader("1. Basic Portfolio Metrics & Calculations")
        
        st.markdown("**1.1 Investment Value**")
        st.code("Investment Value = Buy Price × Quantity", language=None)
        st.write("The total amount invested in a particular stock at the time of purchase.")
        
        st.markdown("**1.2 Current Value**")
        st.code("Current Value = Current Market Price × Quantity", language=None)
        st.write("The present market value of your holdings based on live/delayed prices.")
        
        st.markdown("**1.3 Absolute Gain/Loss**")
        st.code("Absolute Gain/Loss = Current Value - Investment Value", language=None)
        st.write("The rupee amount of profit or loss on each holding. Positive values indicate profit, negative values indicate loss.")
        
        st.markdown("**1.4 Percentage Gain/Loss (Return)**")
        st.code("Percentage Gain/Loss = (Absolute Gain/Loss ÷ Investment Value) × 100", language=None)
        st.write("The percentage return on your investment. This is the most important metric for comparing performance across different investments regardless of their size.")
        
        st.markdown("**1.5 Total Portfolio Return**")
        st.code("""Portfolio Return % = (Total Gain/Loss ÷ Total Investment) × 100

Where:
  Total Gain/Loss = Sum of Absolute Gain/Loss of all stocks
  Total Investment = Sum of Investment Value of all stocks""", language=None)
        st.write("This is the weighted average return of your entire portfolio, reflecting the actual rupee-weighted performance.")
        
        st.markdown("**1.6 All-Time High Since Purchase**")
        st.code("ATH Since Purchase = Maximum High Price from Buy Date to Today", language=None)
        st.write("The highest price the stock reached since you purchased it. Useful for understanding missed profit-taking opportunities.")
        
        st.markdown("**1.7 Potential Gain from ATH**")
        st.code("Potential Gain % = ((ATH Since Purchase - Buy Price) ÷ Buy Price) × 100", language=None)
        st.write("What your return would have been if you had sold at the all-time high.")
        
        st.divider()
        
        # Section 2: Sector & Category Analysis
        st.subheader("2. Sector & Category Analysis")
        
        st.markdown("**2.1 Sector Allocation Percentage**")
        st.code("Sector Allocation % = (Sector Current Value ÷ Total Portfolio Value) × 100", language=None)
        st.write("Shows what percentage of your portfolio is invested in each sector (Banking, Technology, FMCG, etc.). Used for diversification analysis.")
        
        st.markdown("**2.2 Sector Return**")
        st.code("Sector Return % = (Sector Total Gain/Loss ÷ Sector Total Investment) × 100", language=None)
        st.write("The combined return of all stocks within a particular sector.")
        
        st.markdown("**2.3 Market Cap Categories**")
        st.markdown("""
| Category | Market Capitalization | Characteristics |
|----------|----------------------|-----------------|
| **Large Cap** | Top 100 companies by market cap | Stable, lower risk, established businesses |
| **Mid Cap** | 101-250 ranked companies | Moderate risk, growth potential |
| **Small Cap** | Beyond top 250 | Higher risk, higher potential returns |
        """)
        
        st.markdown("**2.4 Ideal Diversification Guidelines**")
        st.markdown("""
- **Sector Concentration:** No single sector should exceed 30-35% of portfolio
- **Stock Concentration:** No single stock should exceed 15-20% of portfolio
- **Category Mix (Conservative):** 60% Large Cap, 30% Mid Cap, 10% Small Cap
- **Category Mix (Aggressive):** 40% Large Cap, 35% Mid Cap, 25% Small Cap
        """)
        
        st.divider()
        
        # Section 3: Benchmark Comparison
        st.subheader("3. Benchmark Comparison Methodology")
        
        st.markdown("**3.1 Benchmark Indices Used**")
        st.markdown("""
- **NIFTY 50:** Top 50 companies on NSE - primary benchmark for Indian equities
- **SENSEX:** Top 30 companies on BSE
- **NIFTY Bank:** Banking sector benchmark
        """)
        
        st.markdown("**3.2 Alpha (Outperformance)**")
        st.code("Alpha = Portfolio Return % - Benchmark Return %", language=None)
        
        st.markdown("**Interpretation:**")
        st.markdown("""
- :green[**Positive Alpha:**] Your portfolio is OUTPERFORMING the market
- :red[**Negative Alpha:**] Your portfolio is UNDERPERFORMING the market
- **Zero Alpha:** Your portfolio is matching market returns (could have used index fund)
        """)
        
        st.markdown("**3.3 Benchmark Period Calculation**")
        st.code("Benchmark Return = ((Current Index Value - Index Value 1 Year Ago) ÷ Index Value 1 Year Ago) × 100", language=None)
        st.write("We use trailing 1-year returns for benchmark comparison as it provides a meaningful time frame for equity investments.")
        
        st.markdown("**3.4 Why Benchmark Comparison Matters**")
        st.info("**Key Insight:** If your portfolio consistently underperforms the benchmark, you may be better off investing in a low-cost index fund (like NIFTY 50 ETF) rather than actively managing individual stocks.")
        
        st.divider()
        
        # Section 4: Value Investing Framework
        st.subheader("4. Value Investing Framework")
        
        st.write("**Philosophy:** Value investing, pioneered by Benjamin Graham and Warren Buffett, focuses on finding stocks trading below their intrinsic value. The goal is to buy '₹1 worth of assets for ₹0.50.'")
        
        st.markdown("**4.1 Value Investing Scoring Parameters**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
| Parameter | Favorable Range | Score |
|-----------|-----------------|-------|
| **P/E Ratio** | < 15 (Good) | +2 |
| **P/E Ratio** | > 25 (Concerning) | -1 |
| **P/B Ratio** | < 1.5 (Good) | +2 |
| **P/B Ratio** | > 3 (Concerning) | -1 |
| **Dividend Yield** | > 3% | +1 |
            """)
        with col2:
            st.markdown("""
| Parameter | Favorable Range | Score |
|-----------|-----------------|-------|
| **Debt-to-Equity** | < 0.5 (Good) | +1 |
| **Debt-to-Equity** | > 2 (Risky) | -1 |
| **Current Loss > 20%** | Yes | +1 |
| **Current Gain > 50%** | Yes | -1 |
            """)
        
        st.markdown("**4.2 Value Score Interpretation**")
        st.markdown("""
- **Score ≥ 3:** :green[**BUY**] - Stock appears undervalued
- **Score -2 to 2:** :orange[**HOLD**] - Fairly valued, maintain position
- **Score ≤ -2:** :red[**SELL**] - Stock appears overvalued
        """)
        
        st.markdown("**4.3 Key Value Metrics Explained**")
        
        st.markdown("**P/E Ratio (Price-to-Earnings):**")
        st.code("P/E Ratio = Current Stock Price ÷ Earnings Per Share (EPS)", language=None)
        st.write("Indicates how much investors pay for each rupee of earnings. Lower P/E suggests the stock is cheaper relative to its earnings.")
        
        st.markdown("**P/B Ratio (Price-to-Book):**")
        st.code("P/B Ratio = Market Price per Share ÷ Book Value per Share", language=None)
        st.write("Compares market value to the company's net assets. P/B < 1 means stock trades below its liquidation value.")
        
        st.markdown("**Dividend Yield:**")
        st.code("Dividend Yield = (Annual Dividend per Share ÷ Stock Price) × 100", language=None)
        st.write("Percentage return from dividends alone, regardless of capital appreciation.")
        
        st.divider()
        
        # Section 5: Growth Investing Framework
        st.subheader("5. Growth Investing Framework")
        
        st.write("**Philosophy:** Growth investing focuses on companies with strong revenue and earnings growth potential, even if they appear expensive by traditional metrics. The goal is to identify future market leaders before the market fully recognizes their potential.")
        
        st.markdown("**5.1 Growth Investing Scoring Parameters**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
| Parameter | Favorable Range | Score |
|-----------|-----------------|-------|
| **Revenue Growth** | > 15% YoY | +2 |
| **Revenue Growth** | < 0% | -1 |
| **Earnings Growth** | > 20% YoY | +2 |
| **Earnings Growth** | < 0% | -1 |
            """)
        with col2:
            st.markdown("""
| Parameter | Favorable Range | Score |
|-----------|-----------------|-------|
| **ROE** | > 20% | +1 |
| **ROE** | < 10% | -1 |
| **Near 52-Week High** | > 90% of high | +1 |
| **Far from High** | < 70% of high | -1 |
| **Current Gain > 30%** | Yes | +1 |
| **Current Loss > 30%** | Yes | -1 |
            """)
        
        st.markdown("**5.2 Growth Score Interpretation**")
        st.markdown("""
- **Score ≥ 3:** :green[**BUY**] - Strong growth characteristics
- **Score -2 to 2:** :orange[**HOLD**] - Average growth, monitor closely
- **Score ≤ -2:** :red[**SELL**] - Weak growth indicators
        """)
        
        st.markdown("**5.3 Key Growth Metrics Explained**")
        
        st.markdown("**Revenue Growth (Year-over-Year):**")
        st.code("Revenue Growth % = ((Current Year Revenue - Previous Year Revenue) ÷ Previous Year Revenue) × 100", language=None)
        
        st.markdown("**ROE (Return on Equity):**")
        st.code("ROE = (Net Income ÷ Shareholder's Equity) × 100", language=None)
        st.write("ROE above 20% indicates the company efficiently generates profits from shareholder investments.")
        
        st.markdown("**52-Week High Proximity:**")
        st.code("Proximity % = (Current Price ÷ 52-Week High Price) × 100", language=None)
        st.write("Stocks near their 52-week highs typically have strong momentum and investor confidence.")
        
        st.divider()
        
        # Section 6: Recommendation Engine
        st.subheader("6. Recommendation Engine Logic")
        
        st.markdown("**6.1 Combined Scoring System**")
        st.write("The overall recommendation combines both Value and Growth perspectives:")
        
        st.code("""Action Scores: BUY = 2, HOLD = 1, SELL = 0

Combined Score = (Value Action Score + Growth Action Score) ÷ 2

Final Recommendation:
  Combined Score ≥ 1.5  →  BUY
  Combined Score 1.0 to 1.49  →  HOLD
  Combined Score < 1.0  →  SELL""", language=None)
        
        st.markdown("**6.2 Confidence Levels**")
        st.markdown("""
| Scenario | Confidence | Meaning |
|----------|------------|---------|
| Both perspectives agree on BUY | **High** | Strong conviction - stock is attractive from multiple angles |
| Both perspectives agree on SELL | **High** | Strong conviction - consider exiting |
| Mixed signals (e.g., Value=BUY, Growth=SELL) | **Medium** | Conflicting indicators - proceed with caution |
| Both suggest HOLD | **Medium** | Neutral stance - maintain position, monitor |
        """)
        
        st.markdown("**6.3 Alternative Stock Suggestions**")
        st.write("When a stock receives a SELL recommendation, we suggest alternative stocks from the same sector that may offer better value or growth characteristics. Alternatives are sourced from a curated database of quality stocks in each sector.")
        
        st.divider()
        
        # Section 7: Portfolio Score
        st.subheader("7. Portfolio Score Calculation")
        
        st.markdown("**7.1 Overall Portfolio Health Score (0-100)**")
        st.write("The portfolio score is a composite metric that evaluates multiple dimensions:")
        
        st.code("""Portfolio Score = Weighted Average of:

1. Performance Score (30%): Based on overall return %
2. Diversification Score (25%): Sector and stock concentration
3. Risk Score (20%): Volatility and drawdown metrics
4. Recommendation Score (25%): Weighted BUY/HOLD/SELL distribution""", language=None)
        
        st.markdown("**7.2 Performance Score Breakdown**")
        st.markdown("""
- Return > 25%: 100 points
- Return 15-25%: 80 points
- Return 5-15%: 60 points
- Return 0-5%: 40 points
- Return < 0%: 20 points (scaled by loss magnitude)
        """)
        
        st.markdown("**7.3 Diversification Score Breakdown**")
        st.markdown("""
- No sector > 30% and no stock > 15%: 100 points
- Minor concentration: 70-90 points
- High concentration in one sector/stock: 30-50 points
        """)
        
        st.markdown("**7.4 Score Interpretation**")
        st.markdown("""
| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 80-100 | :green[**Excellent**] | Well-diversified, strong returns, minimal risk |
| 60-79 | :green[**Good**] | Solid portfolio with minor improvement areas |
| 40-59 | :orange[**Average**] | Needs attention - consider rebalancing |
| Below 40 | :red[**Needs Work**] | Significant issues - review and rebalance |
        """)
        
        st.divider()
        
        # Section 8: Rebalancing Strategy
        st.subheader("8. Rebalancing Strategy Framework")
        
        st.markdown("**8.1 When to Rebalance**")
        st.write("The system triggers rebalancing suggestions when:")
        st.markdown("""
- **Sector Drift:** Any sector exceeds 35% of portfolio
- **Stock Concentration:** Any single stock exceeds 20% of portfolio
- **Category Imbalance:** Market cap allocation deviates significantly from target
- **Underperformance:** Multiple stocks with >25% losses
        """)
        
        st.markdown("**8.2 Rebalancing Rules**")
        st.markdown("""
| Condition | Action | Target |
|-----------|--------|--------|
| Sector > 35% allocation | Reduce exposure | Bring to ≤ 30% |
| Single stock > 20% | Partial profit booking | Bring to ≤ 15% |
| Large Cap < 40% | Add stable large caps | Increase to 50-60% |
| Small Cap > 30% | Reduce small cap exposure | Bring to ≤ 20% |
| Multiple SELL recommendations | Exit weak positions | Reinvest in BUY-rated stocks |
        """)
        
        st.markdown("**8.3 Value vs Growth Rebalancing Approach**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Value Investor Rebalancing:**")
            st.markdown("""
- Buy more of underperforming quality stocks (averaging down)
- Trim winners that become overvalued (P/E > 30)
- Focus on dividend yield and book value
- Ignore short-term price momentum
- Hold for 3-5+ years
            """)
        with col2:
            st.markdown("**Growth Investor Rebalancing:**")
            st.markdown("""
- Cut losers quickly (stop-loss at -15% to -20%)
- Let winners run (ride momentum)
- Focus on revenue and earnings growth trends
- Favor stocks near 52-week highs
- More active portfolio turnover
            """)
        
        st.divider()
        
        # Section 9: Risk Metrics
        st.subheader("9. Risk Metrics & Correlation")
        
        st.markdown("**9.1 Correlation Matrix**")
        st.code("""Correlation = Covariance(Stock A Returns, Stock B Returns) ÷ (StdDev A × StdDev B)

Range: -1 to +1""", language=None)
        st.markdown("""
- **+1:** Perfect positive correlation - stocks move together
- **0:** No correlation - independent movement
- **-1:** Perfect negative correlation - move opposite
        """)
        st.write("**Diversification Benefit:** Lower correlation between holdings reduces overall portfolio volatility. Aim for average correlation < 0.5 across portfolio.")
        
        st.markdown("**9.2 Volatility Measurement**")
        st.code("""Daily Volatility = Standard Deviation of Daily Returns
Annualized Volatility = Daily Volatility × √252""", language=None)
        st.write("Higher volatility means greater price swings. While this can lead to higher returns, it also increases risk of losses.")
        
        st.markdown("**9.3 Maximum Drawdown**")
        st.code("Max Drawdown = (Trough Value - Peak Value) ÷ Peak Value × 100", language=None)
        st.write("The largest percentage drop from a peak to subsequent low. Important for understanding worst-case scenarios.")
        
        st.divider()
        
        # Section 10: Limitations
        st.subheader("10. Limitations & Disclaimers")
        
        st.markdown("**Model Limitations:**")
        st.markdown("""
- Recommendations are **rule-based**, not AI/ML predictive models
- Past performance does not guarantee future results
- Does not account for macroeconomic factors, news events, or market sentiment
- Sector classifications are simplified and may not reflect all nuances
        """)
        
        st.divider()
        
        # Section 11: Advanced Metrics
        st.subheader("11. Advanced Portfolio Metrics")
        
        st.write("The Advanced Metrics module provides institutional-grade portfolio analysis across 10 layers.")
        
        st.markdown("**11.1 Structural Diagnostics**")
        st.markdown("""
- **Market Cap Allocation:** Percentage of portfolio in Large/Mid/Small cap stocks
- **Sector Allocation:** Distribution across different sectors
- **Industry Concentration:** Flag if any single sector exceeds 30% allocation
- **Thematic Clusters:** Detection of PSU-heavy, Tech-heavy, or Banking-heavy portfolios
        """)
        
        st.markdown("**11.2 Style Analysis**")
        st.code("""Value Tilt % = (Underperforming stocks / Total stocks) × 100
Growth Tilt % = 100 - Value Tilt %
Momentum Exposure = (Stocks with >20% gain / Total stocks) × 100""", language=None)
        st.markdown("""
- **Value Style:** Stocks trading below intrinsic value
- **Growth Style:** Stocks with high earnings/revenue growth
- **Blend:** Balanced mix of value and growth
        """)
        
        st.markdown("**11.3 Concentration Risk**")
        st.code("""Top N Exposure % = (Sum of Top N stock values / Total Portfolio Value) × 100

Risk Thresholds:
- Single stock > 15% = Flag
- Single sector > 30% = Flag
- Top 3 stocks > 50% = High concentration""", language=None)
        
        st.markdown("**11.4 Volatility & Drawdown Metrics**")
        st.code("""Historical Volatility = Standard Deviation of Returns × √252 × 100

Max Drawdown = ((Peak Value - Trough Value) / Peak Value) × 100

Downside Deviation = Std Dev of Negative Returns × √252 × 100

Beta = Covariance(Stock, Benchmark) / Variance(Benchmark)

Sortino Ratio = (Portfolio Return - Risk-Free Rate) / Downside Deviation""", language=None)
        st.markdown("""
- **Sortino Ratio Interpretation:** Higher is better (measures return per unit of downside risk)
- **Beta Interpretation:** Beta > 1 means more volatile than market, Beta < 1 means less volatile
        """)
        
        st.markdown("**11.5 Behavior Analysis**")
        st.code("""Average Holding Period = Mean(Days held for each stock)

Behavior Score Components:
- Short-term holdings (<90 days) penalty
- Overtrading detection (>50% short-term)
- Long-term holdings bonus""", language=None)
        st.markdown("""
| Pattern | Holding Period | Interpretation |
|---------|---------------|----------------|
| Patient Investor | >365 days | Long-term wealth builder |
| Medium-Term Holder | 180-365 days | Balanced approach |
| Active Trader | 90-180 days | Moderate churning |
| High Churn | <90 days | Potential overtrading |
        """)
        
        st.markdown("**11.6 Drift Analysis (Alignment Score)**")
        st.code("""Sector Drift = Portfolio Sector % - Benchmark Sector %
Alignment Score = 100 - Sum of |Sector Drifts|""", language=None)
        st.write("Compares your portfolio's sector allocation against Nifty 50's sector weights.")
        
        st.markdown("**11.7 Overlap Detection**")
        st.markdown("""
Identifies duplicate exposure through:
- Same business group holdings (Tata Group, Reliance Group, etc.)
- Same sector concentration (>4 stocks in one sector)
- Correlated stock movements
        """)
        
        st.markdown("**11.8 Return Attribution**")
        st.code("""Stock Contribution = Stock's Absolute Gain/Loss
Contribution % = (Stock Contribution / Total Portfolio Gain) × 100

Sector Attribution = Sum of stock contributions within sector""", language=None)
        st.write("Shows which stocks and sectors contributed most to your gains or losses.")
        
        st.markdown("**11.9 Liquidity Risk**")
        st.code("""Average Traded Value = Average Volume × Average Price
Days to Liquidate = Position Value / (Average Traded Value × 10%)

Liquidity Grades:
- High: <1 day to liquidate
- Medium: 1-5 days
- Low: >5 days""", language=None)
        
        st.markdown("**11.10 Tail Risk Exposure**")
        st.code("""High Volatility Exposure = Sum of (stocks with >40% volatility) / Total Value
Small Cap Exposure = Sum of Small Cap stocks / Total Value

Tail Risk Score = 100 - penalties for high-vol and small-cap exposure""", language=None)
        
        st.markdown("**11.11 Macro Sensitivity**")
        st.markdown("""
| Sensitivity Type | Stocks Tracked | Impact |
|-----------------|----------------|--------|
| Interest Rate | Banking, NBFC stocks | Rate hikes hurt valuations |
| Crude Oil | Oil & Gas, Refineries | Import costs, margins |
| Currency (INR) | IT, Pharma exporters | INR weakness = benefit |
| Metals | Steel, Aluminum companies | Global commodity cycles |
        """)
        
        st.markdown("**11.12 Portfolio Health Score**")
        st.code("""Health Score = Weighted Average of:
- Diversification Score (25%)
- Risk Score (25%)
- Liquidity Score (20%)
- Behavior Score (15%)
- Style Balance Score (15%)

Grades: A (≥80), B (65-79), C (50-64), D (<50)""", language=None)
        
        st.markdown("**11.13 Scenario Analysis (Stress Testing)**")
        st.code("""Projected Impact = Σ(Stock Value × Beta × Market Move %)

Scenarios:
- Nifty falls 10%
- Midcaps correct 20%
- Banking drops 15%""", language=None)
        st.info("Scenario analysis uses historical betas to project potential losses. Actual results may differ.")
        
        st.divider()
        
        st.markdown("**Important Disclaimer:**")
        st.error("""
**THIS IS NOT FINANCIAL ADVICE**

Alphalens Portfolio Analyzer is an **educational and informational tool** only. 
The analysis, recommendations, and insights provided should not be construed as professional 
financial advice. Always consult with a SEBI-registered investment advisor before making 
investment decisions. Past performance is not indicative of future results. 
Investing in stocks involves risk of capital loss.
        """)
        
        st.divider()
        
        # Footer
        st.caption("Alphalens Portfolio Analyzer by Edhaz Financial Services")
        st.caption("Methodology Version 2.0 | Last Updated: January 2026")
