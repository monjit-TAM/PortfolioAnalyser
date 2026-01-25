import streamlit as st

class Methodology:
    def render(self):
        """Render comprehensive methodology and formulas documentation"""
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px;'>
            <h1 style='color: #FF6B35; margin: 0; font-size: 28px;'>📐 Analysis Methodology & Formulas</h1>
            <p style='color: rgba(255,255,255,0.85); margin: 10px 0 0 0; font-size: 15px;'>
                Complete documentation of all calculations, theories, and recommendation frameworks used in Alphalens Portfolio Analyzer
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Table of Contents
        st.markdown("""
        <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px;'>
            <h3 style='color: #333; margin-top: 0;'>📋 Table of Contents</h3>
            <ol style='color: #555; line-height: 2;'>
                <li><a href='#basic-metrics' style='color: #667eea;'>Basic Portfolio Metrics & Calculations</a></li>
                <li><a href='#sector-category' style='color: #667eea;'>Sector & Category Analysis</a></li>
                <li><a href='#benchmark' style='color: #667eea;'>Benchmark Comparison Methodology</a></li>
                <li><a href='#value-investing' style='color: #667eea;'>Value Investing Framework</a></li>
                <li><a href='#growth-investing' style='color: #667eea;'>Growth Investing Framework</a></li>
                <li><a href='#recommendation-engine' style='color: #667eea;'>Recommendation Engine Logic</a></li>
                <li><a href='#portfolio-score' style='color: #667eea;'>Portfolio Score Calculation</a></li>
                <li><a href='#rebalancing' style='color: #667eea;'>Rebalancing Strategy</a></li>
                <li><a href='#risk-metrics' style='color: #667eea;'>Risk Metrics & Correlation</a></li>
                <li><a href='#limitations' style='color: #667eea;'>Limitations & Disclaimers</a></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 1: Basic Portfolio Metrics
        st.markdown('<a id="basic-metrics"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #667eea; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #667eea; margin-top: 0;'>1. Basic Portfolio Metrics & Calculations</h2>
            
            <h4 style='color: #333;'>1.1 Investment Value</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Investment Value = Buy Price × Quantity
            </div>
            <p style='color: #555;'>The total amount invested in a particular stock at the time of purchase.</p>
            
            <h4 style='color: #333;'>1.2 Current Value</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Current Value = Current Market Price × Quantity
            </div>
            <p style='color: #555;'>The present market value of your holdings based on live/delayed prices.</p>
            
            <h4 style='color: #333;'>1.3 Absolute Gain/Loss</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Absolute Gain/Loss = Current Value - Investment Value
            </div>
            <p style='color: #555;'>The rupee amount of profit or loss on each holding. Positive values indicate profit, negative values indicate loss.</p>
            
            <h4 style='color: #333;'>1.4 Percentage Gain/Loss (Return)</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Percentage Gain/Loss = (Absolute Gain/Loss ÷ Investment Value) × 100
            </div>
            <p style='color: #555;'>The percentage return on your investment. This is the most important metric for comparing performance across different investments regardless of their size.</p>
            
            <h4 style='color: #333;'>1.5 Total Portfolio Return</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Portfolio Return % = (Total Gain/Loss ÷ Total Investment) × 100<br><br>
                Where:<br>
                • Total Gain/Loss = Σ (Absolute Gain/Loss of all stocks)<br>
                • Total Investment = Σ (Investment Value of all stocks)
            </div>
            <p style='color: #555;'>This is the weighted average return of your entire portfolio, reflecting the actual rupee-weighted performance.</p>
            
            <h4 style='color: #333;'>1.6 All-Time High Since Purchase</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                ATH Since Purchase = MAX(High Prices from Buy Date to Today)
            </div>
            <p style='color: #555;'>The highest price the stock reached since you purchased it. Useful for understanding missed profit-taking opportunities.</p>
            
            <h4 style='color: #333;'>1.7 Potential Gain from ATH</h4>
            <div style='background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Potential Gain % = ((ATH Since Purchase - Buy Price) ÷ Buy Price) × 100
            </div>
            <p style='color: #555;'>What your return would have been if you had sold at the all-time high.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 2: Sector & Category Analysis
        st.markdown('<a id="sector-category"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #28a745; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #28a745; margin-top: 0;'>2. Sector & Category Analysis</h2>
            
            <h4 style='color: #333;'>2.1 Sector Allocation Percentage</h4>
            <div style='background: #f0fff4; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Sector Allocation % = (Sector Current Value ÷ Total Portfolio Value) × 100
            </div>
            <p style='color: #555;'>Shows what percentage of your portfolio is invested in each sector (Banking, Technology, FMCG, etc.). Used for diversification analysis.</p>
            
            <h4 style='color: #333;'>2.2 Sector Return</h4>
            <div style='background: #f0fff4; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Sector Return % = (Sector Total Gain/Loss ÷ Sector Total Investment) × 100
            </div>
            <p style='color: #555;'>The combined return of all stocks within a particular sector.</p>
            
            <h4 style='color: #333;'>2.3 Market Cap Categories</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #f0fff4;'>
                    <th style='padding: 12px; border: 1px solid #ddd; text-align: left;'>Category</th>
                    <th style='padding: 12px; border: 1px solid #ddd; text-align: left;'>Market Capitalization</th>
                    <th style='padding: 12px; border: 1px solid #ddd; text-align: left;'>Characteristics</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Large Cap</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Top 100 companies by market cap</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Stable, lower risk, established businesses</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Mid Cap</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>101-250 ranked companies</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Moderate risk, growth potential</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Small Cap</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Beyond top 250</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Higher risk, higher potential returns</td>
                </tr>
            </table>
            
            <h4 style='color: #333;'>2.4 Ideal Diversification Guidelines</h4>
            <ul style='color: #555; line-height: 1.8;'>
                <li><strong>Sector Concentration:</strong> No single sector should exceed 30-35% of portfolio</li>
                <li><strong>Stock Concentration:</strong> No single stock should exceed 15-20% of portfolio</li>
                <li><strong>Category Mix (Conservative):</strong> 60% Large Cap, 30% Mid Cap, 10% Small Cap</li>
                <li><strong>Category Mix (Aggressive):</strong> 40% Large Cap, 35% Mid Cap, 25% Small Cap</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 3: Benchmark Comparison
        st.markdown('<a id="benchmark"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #17a2b8; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #17a2b8; margin-top: 0;'>3. Benchmark Comparison Methodology</h2>
            
            <h4 style='color: #333;'>3.1 Benchmark Indices Used</h4>
            <ul style='color: #555; line-height: 1.8;'>
                <li><strong>NIFTY 50:</strong> Top 50 companies on NSE - primary benchmark for Indian equities</li>
                <li><strong>SENSEX:</strong> Top 30 companies on BSE</li>
                <li><strong>NIFTY Bank:</strong> Banking sector benchmark</li>
            </ul>
            
            <h4 style='color: #333;'>3.2 Alpha (Outperformance)</h4>
            <div style='background: #f0f9ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Alpha = Portfolio Return % - Benchmark Return %
            </div>
            <p style='color: #555;'><strong>Interpretation:</strong></p>
            <ul style='color: #555;'>
                <li><span style='color: green;'>Positive Alpha:</span> Your portfolio is OUTPERFORMING the market</li>
                <li><span style='color: red;'>Negative Alpha:</span> Your portfolio is UNDERPERFORMING the market</li>
                <li><span style='color: gray;'>Zero Alpha:</span> Your portfolio is matching market returns (could have used index fund)</li>
            </ul>
            
            <h4 style='color: #333;'>3.3 Benchmark Period Calculation</h4>
            <div style='background: #f0f9ff; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Benchmark Return = ((Current Index Value - Index Value 1 Year Ago) ÷ Index Value 1 Year Ago) × 100
            </div>
            <p style='color: #555;'>We use trailing 1-year returns for benchmark comparison as it provides a meaningful time frame for equity investments.</p>
            
            <h4 style='color: #333;'>3.4 Why Benchmark Comparison Matters</h4>
            <div style='background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <p style='margin: 0; color: #856404;'>
                    <strong>Key Insight:</strong> If your portfolio consistently underperforms the benchmark, you may be better off investing in a low-cost index fund (like NIFTY 50 ETF) rather than actively managing individual stocks.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 4: Value Investing Framework
        st.markdown('<a id="value-investing"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #6f42c1; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #6f42c1; margin-top: 0;'>4. Value Investing Framework</h2>
            
            <p style='color: #555; font-size: 15px; margin-bottom: 20px;'>
                <strong>Philosophy:</strong> Value investing, pioneered by Benjamin Graham and Warren Buffett, focuses on finding stocks trading below their intrinsic value. The goal is to buy "₹1 worth of assets for ₹0.50."
            </p>
            
            <h4 style='color: #333;'>4.1 Value Investing Scoring Parameters</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #f3f0ff;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Parameter</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Favorable Range</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Score Impact</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Rationale</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>P/E Ratio</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>< 15 (Good)<br>> 25 (Concerning)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+2 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Low P/E suggests undervaluation relative to earnings</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>P/B Ratio</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>< 1.5 (Good)<br>> 3 (Concerning)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+2 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Low P/B means stock trades near/below book value</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Dividend Yield</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>> 3%</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Provides steady income, indicates mature company</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Debt-to-Equity</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>< 0.5 (Good)<br>> 2 (Risky)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Low debt indicates financial stability</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Current Loss > 20%</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Yes</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Significant decline may present value opportunity</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Current Gain > 50%</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Yes</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>-1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Substantial gains may indicate overvaluation</td>
                </tr>
            </table>
            
            <h4 style='color: #333;'>4.2 Value Score Interpretation</h4>
            <div style='background: #f3f0ff; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <ul style='margin: 0; color: #555;'>
                    <li><strong>Score ≥ 3:</strong> <span style='color: green;'>BUY</span> - Stock appears undervalued</li>
                    <li><strong>Score -2 to 2:</strong> <span style='color: orange;'>HOLD</span> - Fairly valued, maintain position</li>
                    <li><strong>Score ≤ -2:</strong> <span style='color: red;'>SELL</span> - Stock appears overvalued</li>
                </ul>
            </div>
            
            <h4 style='color: #333;'>4.3 Key Value Metrics Explained</h4>
            
            <p style='color: #555;'><strong>P/E Ratio (Price-to-Earnings):</strong></p>
            <div style='background: #f3f0ff; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                P/E Ratio = Current Stock Price ÷ Earnings Per Share (EPS)
            </div>
            <p style='color: #555; margin-bottom: 15px;'>Indicates how much investors pay for each rupee of earnings. Lower P/E suggests the stock is cheaper relative to its earnings.</p>
            
            <p style='color: #555;'><strong>P/B Ratio (Price-to-Book):</strong></p>
            <div style='background: #f3f0ff; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                P/B Ratio = Market Price per Share ÷ Book Value per Share
            </div>
            <p style='color: #555; margin-bottom: 15px;'>Compares market value to the company's net assets. P/B < 1 means stock trades below its liquidation value.</p>
            
            <p style='color: #555;'><strong>Dividend Yield:</strong></p>
            <div style='background: #f3f0ff; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                Dividend Yield = (Annual Dividend per Share ÷ Stock Price) × 100
            </div>
            <p style='color: #555;'>Percentage return from dividends alone, regardless of capital appreciation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 5: Growth Investing Framework
        st.markdown('<a id="growth-investing"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #fd7e14; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #fd7e14; margin-top: 0;'>5. Growth Investing Framework</h2>
            
            <p style='color: #555; font-size: 15px; margin-bottom: 20px;'>
                <strong>Philosophy:</strong> Growth investing focuses on companies with strong revenue and earnings growth potential, even if they appear expensive by traditional metrics. The goal is to identify future market leaders before the market fully recognizes their potential.
            </p>
            
            <h4 style='color: #333;'>5.1 Growth Investing Scoring Parameters</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #fff5eb;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Parameter</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Favorable Range</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Score Impact</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Rationale</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Revenue Growth</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>> 15% YoY (Good)<br>< 0% (Concerning)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+2 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>High revenue growth indicates expanding business</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Earnings Growth</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>> 20% YoY (Good)<br>< 0% (Concerning)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+2 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Strong earnings growth shows profitability scaling</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>ROE (Return on Equity)</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>> 20% (Good)<br>< 10% (Low)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Measures efficiency of shareholder capital use</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>52-Week High Proximity</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>> 90% of high (Good)<br>< 70% of high (Weak)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1 / -1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Momentum indicator - strong stocks stay near highs</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Current Gain > 30%</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Yes</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>+1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Strong performance indicates growth momentum</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Current Loss > 30%</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Yes</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>-1</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Poor performance may indicate growth challenges</td>
                </tr>
            </table>
            
            <h4 style='color: #333;'>5.2 Growth Score Interpretation</h4>
            <div style='background: #fff5eb; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <ul style='margin: 0; color: #555;'>
                    <li><strong>Score ≥ 3:</strong> <span style='color: green;'>BUY</span> - Strong growth characteristics</li>
                    <li><strong>Score -2 to 2:</strong> <span style='color: orange;'>HOLD</span> - Average growth, monitor closely</li>
                    <li><strong>Score ≤ -2:</strong> <span style='color: red;'>SELL</span> - Weak growth indicators</li>
                </ul>
            </div>
            
            <h4 style='color: #333;'>5.3 Key Growth Metrics Explained</h4>
            
            <p style='color: #555;'><strong>Revenue Growth (Year-over-Year):</strong></p>
            <div style='background: #fff5eb; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                Revenue Growth % = ((Current Year Revenue - Previous Year Revenue) ÷ Previous Year Revenue) × 100
            </div>
            
            <p style='color: #555;'><strong>ROE (Return on Equity):</strong></p>
            <div style='background: #fff5eb; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                ROE = (Net Income ÷ Shareholder's Equity) × 100
            </div>
            <p style='color: #555;'>ROE above 20% indicates the company efficiently generates profits from shareholder investments.</p>
            
            <p style='color: #555;'><strong>52-Week High Proximity:</strong></p>
            <div style='background: #fff5eb; padding: 10px 15px; border-radius: 8px; font-family: monospace; margin-bottom: 10px;'>
                Proximity % = (Current Price ÷ 52-Week High Price) × 100
            </div>
            <p style='color: #555;'>Stocks near their 52-week highs typically have strong momentum and investor confidence.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 6: Recommendation Engine
        st.markdown('<a id="recommendation-engine"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #dc3545; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #dc3545; margin-top: 0;'>6. Recommendation Engine Logic</h2>
            
            <h4 style='color: #333;'>6.1 Combined Scoring System</h4>
            <p style='color: #555;'>The overall recommendation combines both Value and Growth perspectives:</p>
            
            <div style='background: #fff5f5; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Action Scores: BUY = 2, HOLD = 1, SELL = 0<br><br>
                Combined Score = (Value Action Score + Growth Action Score) ÷ 2<br><br>
                Final Recommendation:<br>
                • Combined Score ≥ 1.5 → <strong style='color: green;'>BUY</strong><br>
                • Combined Score 1.0 to 1.49 → <strong style='color: orange;'>HOLD</strong><br>
                • Combined Score < 1.0 → <strong style='color: red;'>SELL</strong>
            </div>
            
            <h4 style='color: #333;'>6.2 Confidence Levels</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #fff5f5;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Scenario</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Confidence</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Meaning</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Both perspectives agree on BUY</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>High</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Strong conviction - stock is attractive from multiple angles</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Both perspectives agree on SELL</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>High</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Strong conviction - consider exiting</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Mixed signals (e.g., Value=BUY, Growth=SELL)</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Medium</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Conflicting indicators - proceed with caution</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Both suggest HOLD</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong>Medium</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Neutral stance - maintain position, monitor</td>
                </tr>
            </table>
            
            <h4 style='color: #333;'>6.3 Alternative Stock Suggestions</h4>
            <p style='color: #555;'>When a stock receives a SELL recommendation, we suggest alternative stocks from the same sector that may offer better value or growth characteristics. Alternatives are sourced from a curated database of quality stocks in each sector.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 7: Portfolio Score
        st.markdown('<a id="portfolio-score"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #20c997; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #20c997; margin-top: 0;'>7. Portfolio Score Calculation</h2>
            
            <h4 style='color: #333;'>7.1 Overall Portfolio Health Score (0-100)</h4>
            <p style='color: #555;'>The portfolio score is a composite metric that evaluates multiple dimensions:</p>
            
            <div style='background: #f0fff8; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Portfolio Score = Weighted Average of:<br><br>
                1. Performance Score (30%): Based on overall return %<br>
                2. Diversification Score (25%): Sector and stock concentration<br>
                3. Risk Score (20%): Volatility and drawdown metrics<br>
                4. Recommendation Score (25%): Weighted BUY/HOLD/SELL distribution
            </div>
            
            <h4 style='color: #333;'>7.2 Score Components</h4>
            
            <p style='color: #555;'><strong>Performance Score:</strong></p>
            <ul style='color: #555;'>
                <li>Return > 25%: 100 points</li>
                <li>Return 15-25%: 80 points</li>
                <li>Return 5-15%: 60 points</li>
                <li>Return 0-5%: 40 points</li>
                <li>Return < 0%: 20 points (scaled by loss magnitude)</li>
            </ul>
            
            <p style='color: #555;'><strong>Diversification Score:</strong></p>
            <ul style='color: #555;'>
                <li>No sector > 30% and no stock > 15%: 100 points</li>
                <li>Minor concentration: 70-90 points</li>
                <li>High concentration in one sector/stock: 30-50 points</li>
            </ul>
            
            <h4 style='color: #333;'>7.3 Score Interpretation</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #f0fff8;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Score Range</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Rating</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Interpretation</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>80-100</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong style='color: green;'>Excellent</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Well-diversified, strong returns, minimal risk</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>60-79</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong style='color: #28a745;'>Good</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Solid portfolio with minor improvement areas</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>40-59</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong style='color: orange;'>Average</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Needs attention - consider rebalancing</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Below 40</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><strong style='color: red;'>Needs Work</strong></td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Significant issues - review and rebalance</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 8: Rebalancing Strategy
        st.markdown('<a id="rebalancing"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #6610f2; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #6610f2; margin-top: 0;'>8. Rebalancing Strategy Framework</h2>
            
            <h4 style='color: #333;'>8.1 When to Rebalance</h4>
            <p style='color: #555;'>The system triggers rebalancing suggestions when:</p>
            <ul style='color: #555; line-height: 1.8;'>
                <li><strong>Sector Drift:</strong> Any sector exceeds 35% of portfolio</li>
                <li><strong>Stock Concentration:</strong> Any single stock exceeds 20% of portfolio</li>
                <li><strong>Category Imbalance:</strong> Market cap allocation deviates significantly from target</li>
                <li><strong>Underperformance:</strong> Multiple stocks with >25% losses</li>
            </ul>
            
            <h4 style='color: #333;'>8.2 Rebalancing Rules</h4>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #f5f0ff;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Condition</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Action</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>Target</th>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Sector > 35% allocation</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Reduce exposure</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Bring to ≤ 30%</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Single stock > 20%</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Partial profit booking</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Bring to ≤ 15%</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Large Cap < 40%</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Add stable large caps</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Increase to 50-60%</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Small Cap > 30%</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Reduce small cap exposure</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Bring to ≤ 20%</td>
                </tr>
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Multiple SELL recommendations</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Exit weak positions</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'>Reinvest in BUY-rated stocks</td>
                </tr>
            </table>
            
            <h4 style='color: #333;'>8.3 Value vs Growth Rebalancing Approach</h4>
            
            <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
                <div style='flex: 1; min-width: 280px; background: #f3f0ff; padding: 15px; border-radius: 8px;'>
                    <h5 style='color: #6f42c1; margin-top: 0;'>Value Investor Rebalancing</h5>
                    <ul style='color: #555; margin: 0; padding-left: 20px;'>
                        <li>Buy more of underperforming quality stocks (averaging down)</li>
                        <li>Trim winners that become overvalued (P/E > 30)</li>
                        <li>Focus on dividend yield and book value</li>
                        <li>Ignore short-term price momentum</li>
                        <li>Hold for 3-5+ years</li>
                    </ul>
                </div>
                <div style='flex: 1; min-width: 280px; background: #fff5eb; padding: 15px; border-radius: 8px;'>
                    <h5 style='color: #fd7e14; margin-top: 0;'>Growth Investor Rebalancing</h5>
                    <ul style='color: #555; margin: 0; padding-left: 20px;'>
                        <li>Cut losers quickly (stop-loss at -15% to -20%)</li>
                        <li>Let winners run (ride momentum)</li>
                        <li>Focus on revenue and earnings growth trends</li>
                        <li>Favor stocks near 52-week highs</li>
                        <li>More active portfolio turnover</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 9: Risk Metrics
        st.markdown('<a id="risk-metrics"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #ffffff; border: 2px solid #e83e8c; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #e83e8c; margin-top: 0;'>9. Risk Metrics & Correlation</h2>
            
            <h4 style='color: #333;'>9.1 Correlation Matrix</h4>
            <div style='background: #fff0f6; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Correlation = Covariance(Stock A Returns, Stock B Returns) ÷ (StdDev A × StdDev B)<br><br>
                Range: -1 to +1
            </div>
            <ul style='color: #555;'>
                <li><strong>+1:</strong> Perfect positive correlation - stocks move together</li>
                <li><strong>0:</strong> No correlation - independent movement</li>
                <li><strong>-1:</strong> Perfect negative correlation - move opposite</li>
            </ul>
            <p style='color: #555;'><strong>Diversification Benefit:</strong> Lower correlation between holdings reduces overall portfolio volatility. Aim for average correlation < 0.5 across portfolio.</p>
            
            <h4 style='color: #333;'>9.2 Volatility Measurement</h4>
            <div style='background: #fff0f6; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Daily Volatility = Standard Deviation of Daily Returns<br>
                Annualized Volatility = Daily Volatility × √252
            </div>
            <p style='color: #555;'>Higher volatility means greater price swings. While this can lead to higher returns, it also increases risk of losses.</p>
            
            <h4 style='color: #333;'>9.3 Maximum Drawdown</h4>
            <div style='background: #fff0f6; padding: 15px; border-radius: 8px; font-family: monospace; margin-bottom: 15px;'>
                Max Drawdown = (Trough Value - Peak Value) ÷ Peak Value × 100
            </div>
            <p style='color: #555;'>The largest percentage drop from a peak to subsequent low. Important for understanding worst-case scenarios.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 10: Limitations
        st.markdown('<a id="limitations"></a>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #fff3cd; border: 2px solid #856404; border-radius: 12px; padding: 25px; margin-bottom: 25px;'>
            <h2 style='color: #856404; margin-top: 0;'>⚠️ 10. Limitations & Disclaimers</h2>
            
            <h4 style='color: #333;'>10.1 Data Limitations</h4>
            <ul style='color: #555; line-height: 1.8;'>
                <li><strong>Price Data:</strong> Live prices via TrueData (if configured), otherwise Yahoo Finance with 15-20 minute delay</li>
                <li><strong>Fundamental Data:</strong> Sourced from Yahoo Finance - may not reflect latest quarterly results</li>
                <li><strong>Historical Data:</strong> Limited to available data from Yahoo Finance API</li>
            </ul>
            
            <h4 style='color: #333;'>10.2 Model Limitations</h4>
            <ul style='color: #555; line-height: 1.8;'>
                <li>Recommendations are <strong>rule-based</strong>, not AI/ML predictive models</li>
                <li>Past performance does not guarantee future results</li>
                <li>Fundamental data may be outdated (quarterly lag)</li>
                <li>Does not account for macroeconomic factors, news events, or market sentiment</li>
                <li>Sector classifications are simplified and may not reflect all nuances</li>
            </ul>
            
            <h4 style='color: #333;'>10.3 Important Disclaimer</h4>
            <div style='background: #fff; padding: 20px; border-radius: 8px; border: 2px solid #dc3545;'>
                <p style='color: #dc3545; font-weight: bold; margin: 0 0 10px 0;'>
                    THIS IS NOT FINANCIAL ADVICE
                </p>
                <p style='color: #555; margin: 0;'>
                    Alphalens Portfolio Analyzer is an <strong>educational and informational tool</strong> only. 
                    The analysis, recommendations, and insights provided should not be construed as professional 
                    financial advice. Always consult with a SEBI-registered investment advisor before making 
                    investment decisions. Past performance is not indicative of future results. 
                    Investing in stocks involves risk of capital loss.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; padding: 20px; color: #888; font-size: 13px;'>
            <p>Alphalens Portfolio Analyzer by Edhaz Financial Services</p>
            <p>Methodology Version 1.0 | Last Updated: January 2026</p>
        </div>
        """, unsafe_allow_html=True)
