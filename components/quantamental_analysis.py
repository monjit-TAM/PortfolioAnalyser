import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def _fmt(val):
    if val >= 10000000:
        return f"₹{val/10000000:.2f} Cr"
    elif val >= 100000:
        return f"₹{val/100000:.2f} L"
    else:
        return f"₹{val:,.0f}"


METRIC_EXPLANATIONS = {
    'composite_score': {
        'title': 'Composite Score',
        'description': 'A combined score (0-100) blending fundamental quality (55% weight) and technical momentum (45% weight). Higher scores indicate stronger overall investment attractiveness.',
        'interpretation': '70+ = Strong BUY | 55-70 = BUY | 40-55 = HOLD | 25-40 = SELL | Below 25 = Strong SELL'
    },
    'fundamental_signal': {
        'title': 'Fundamental Signal',
        'description': 'Evaluates a stock\'s intrinsic value using key financial ratios: P/E Ratio (valuation), P/B Ratio (asset value), ROE (profitability), Debt-to-Equity (financial health), Earnings Growth (growth trajectory), and Dividend Yield (income).',
        'interpretation': 'Strong = Excellent fundamentals | Good = Above average | Moderate = Average | Fair = Below average | Weak = Poor fundamentals'
    },
    'technical_signal': {
        'title': 'Technical Signal',
        'description': 'Measures price momentum and trend strength using: 3M/6M/12M Price Momentum (direction of price movement), RSI-14 (overbought/oversold levels), 20 & 50-day Moving Averages (trend confirmation), and Annualized Volatility (risk level).',
        'interpretation': 'Strong Bullish = Clear uptrend | Bullish = Positive momentum | Neutral = No clear direction | Bearish = Negative momentum | Strong Bearish = Clear downtrend'
    },
    'signal_label': {
        'title': 'Signal Classification',
        'description': 'Combines fundamental and technical signals into one label to identify conviction level. When both signals agree, conviction is highest. When they disagree, it warns of potential risks like value traps or momentum-only plays.',
        'interpretation': 'High Conviction BUY = Both strong | Value Trap Risk = Good fundamentals but poor technicals | Momentum Only = Good technicals but weak fundamentals | High Conviction SELL = Both weak'
    },
    'momentum_3m': {
        'title': '3-Month Momentum',
        'description': 'Percentage price change over the last ~63 trading days. Measures short-term price direction.',
        'interpretation': 'Above +10% = Strong positive momentum | 0 to +10% = Mildly positive | -10% to 0 = Weak | Below -10% = Negative momentum'
    },
    'momentum_6m': {
        'title': '6-Month Momentum',
        'description': 'Percentage price change over the last ~126 trading days. Captures medium-term trend strength.',
        'interpretation': 'Above +15% = Strong | Below -15% = Weak'
    },
    'momentum_12m': {
        'title': '12-Month Momentum',
        'description': 'Percentage price change over the last ~252 trading days (1 year). Indicates long-term trend and is a key factor in momentum investing strategies.',
        'interpretation': 'Above +20% = Strong bullish trend | Below -20% = Strong bearish trend'
    },
    'rsi': {
        'title': 'RSI (Relative Strength Index)',
        'description': 'A momentum oscillator (0-100) that measures the speed and magnitude of recent price changes. Developed by J. Welles Wilder, calculated over 14 periods.',
        'interpretation': 'Above 70 = Overbought (potential pullback) | 30-70 = Normal range | Below 30 = Oversold (potential bounce)'
    },
    'ma_trend': {
        'title': 'Moving Average Trend',
        'description': 'Compares the stock price with its 20-day and 50-day Simple Moving Averages (SMA). When price is above both MAs and the shorter MA is above the longer, it signals a bullish trend.',
        'interpretation': 'Bullish = Price above 50-day MA, 20-day MA above 50-day MA | Bearish = Price below both MAs | Mixed = Conflicting signals'
    },
    'volatility': {
        'title': 'Annualized Volatility',
        'description': 'Measures how much a stock\'s price fluctuates, expressed as an annualized percentage. Calculated from daily return standard deviation × √252. Higher volatility means higher risk but also potentially higher returns.',
        'interpretation': 'Below 20% = Low volatility (stable) | 20-40% = Moderate | Above 40% = High volatility (risky)'
    },
    'pe_ratio': {
        'title': 'P/E Ratio (Price-to-Earnings)',
        'description': 'The stock price divided by its earnings per share. Shows how much investors are willing to pay per rupee of earnings. Lower P/E may suggest undervaluation; higher P/E may suggest growth expectations.',
        'interpretation': 'Below 15 = Potentially undervalued (+2 score) | 15-25 = Fair value (+1) | Above 40 = Expensive (-1)'
    },
    'pb_ratio': {
        'title': 'P/B Ratio (Price-to-Book)',
        'description': 'The stock price divided by its book value per share. Compares market value to the company\'s net asset value. Useful for asset-heavy industries like banking and manufacturing.',
        'interpretation': 'Below 1.5 = Undervalued (+1 score) | Above 4 = Expensive (-1)'
    },
    'roe': {
        'title': 'ROE (Return on Equity)',
        'description': 'Net income divided by shareholders\' equity. Measures how effectively a company uses its equity to generate profit. Consistently high ROE indicates management quality.',
        'interpretation': 'Above 20% = Excellent (+2 score) | 12-20% = Good (+1) | Below 5% = Weak (-1)'
    },
    'debt_to_equity': {
        'title': 'Debt-to-Equity Ratio',
        'description': 'Total debt divided by shareholders\' equity. Indicates how much debt a company uses to finance its assets relative to equity. Lower ratios suggest more conservative financing.',
        'interpretation': 'Below 0.5 = Low debt, financially strong (+1 score) | Above 2.0 = High leverage, risky (-1)'
    },
    'earnings_growth': {
        'title': 'Earnings Growth',
        'description': 'Year-over-year growth rate of the company\'s earnings. Positive growth indicates improving profitability; negative growth signals declining performance.',
        'interpretation': 'Above 15% = Strong growth (+1 score) | Below -10% = Declining earnings (-1)'
    },
    'dividend_yield': {
        'title': 'Dividend Yield',
        'description': 'Annual dividend per share divided by the stock price. Shows the income return on investment. Consistent dividends often indicate stable, mature companies.',
        'interpretation': 'Above 2% = Good dividend income (+1 score)'
    },
    'factor_exposure': {
        'title': 'Factor Exposure Radar',
        'description': 'A radar chart showing your portfolio\'s exposure to 5 key investment factors: Value (cheap stocks), Quality (profitable companies), Momentum (trending stocks), Low Volatility (stable stocks), and Growth (growing companies). The shape reveals your portfolio\'s investment style.',
        'interpretation': 'Balanced shape = Well-diversified style | Skewed shape = Concentrated in certain factors'
    },
    'rebalancing': {
        'title': 'Quantamental Rebalancing',
        'description': 'Suggests portfolio weight adjustments based on composite scores. Stocks with higher scores deserve more capital allocation; stocks with lower scores should be reduced. Target weights are proportional to each stock\'s composite score.',
        'interpretation': 'Green = Increase allocation | Red = Reduce allocation | Grey = No change needed (within 1% of target)'
    },
    'risk_adjusted': {
        'title': 'Risk-Adjusted Score',
        'description': 'Combines actual portfolio returns with the composite score, adjusted for volatility. Formula: (Return ÷ Volatility) + Score Bonus. This identifies stocks delivering the best returns relative to their risk and quality.',
        'interpretation': 'Above 0.5 = Excellent risk-reward | 0 to 0.5 = Acceptable | Below 0 = Poor risk-reward'
    },
    'avg_score': {
        'title': 'Average Portfolio Score',
        'description': 'The mean composite score across all stocks in your portfolio. Indicates the overall quantamental health of your portfolio.',
        'interpretation': 'Above 55 = Portfolio has strong fundamentals + technicals | 40-55 = Average | Below 40 = Portfolio needs attention'
    }
}


def render_metric_info(metric_key, inline=False):
    info = METRIC_EXPLANATIONS.get(metric_key, {})
    if not info:
        return

    title = info.get('title', '')
    desc = info.get('description', '')
    interp = info.get('interpretation', '')

    if inline:
        return f"""<div style='background: #f0f4ff; border-radius: 8px; padding: 10px 14px; margin: 6px 0; border-left: 3px solid #667eea; font-size: 12px;'>
            <strong style='color: #333;'>ℹ️ {title}</strong><br>
            <span style='color: #555;'>{desc}</span><br>
            <span style='color: #667eea; font-style: italic;'>{interp}</span>
        </div>"""

    with st.popover(f"ℹ️", use_container_width=False):
        st.markdown(f"**{title}**")
        st.markdown(desc)
        if interp:
            st.markdown(f"*{interp}*")


def compute_technical_signals(stock, historical_data):
    signals = {
        'momentum_3m': None,
        'momentum_6m': None,
        'momentum_12m': None,
        'rsi': None,
        'ma_trend': None,
        'volatility': None,
        'technical_score': 0,
        'technical_signal': 'Neutral',
        'factors': []
    }

    stock_name = stock.get('Stock Name', '')
    hist = historical_data.get(stock_name) if historical_data else None

    if hist is None or (hasattr(hist, 'empty') and hist.empty):
        signals['factors'].append("No historical data available")
        return signals

    try:
        if isinstance(hist, pd.DataFrame):
            close_col = None
            for c in ['Close', 'close', 'Adj Close']:
                if c in hist.columns:
                    close_col = c
                    break
            if close_col is None:
                signals['factors'].append("No price column found")
                return signals
            prices = hist[close_col].dropna()
        elif isinstance(hist, pd.Series):
            prices = hist.dropna()
        else:
            signals['factors'].append("Unrecognized data format")
            return signals

        if len(prices) < 20:
            signals['factors'].append("Insufficient price history")
            return signals

        current = prices.iloc[-1]

        if len(prices) >= 63:
            p_3m = prices.iloc[-63]
            mom_3m = ((current - p_3m) / p_3m) * 100
            signals['momentum_3m'] = round(mom_3m, 2)
            if mom_3m > 10:
                signals['technical_score'] += 2
                signals['factors'].append(f"Strong 3M momentum: +{mom_3m:.1f}%")
            elif mom_3m > 0:
                signals['technical_score'] += 1
                signals['factors'].append(f"Positive 3M momentum: +{mom_3m:.1f}%")
            elif mom_3m > -10:
                signals['factors'].append(f"Weak 3M momentum: {mom_3m:.1f}%")
            else:
                signals['technical_score'] -= 1
                signals['factors'].append(f"Negative 3M momentum: {mom_3m:.1f}%")

        if len(prices) >= 126:
            p_6m = prices.iloc[-126]
            mom_6m = ((current - p_6m) / p_6m) * 100
            signals['momentum_6m'] = round(mom_6m, 2)
            if mom_6m > 15:
                signals['technical_score'] += 1
            elif mom_6m < -15:
                signals['technical_score'] -= 1

        if len(prices) >= 252:
            p_12m = prices.iloc[-252]
            mom_12m = ((current - p_12m) / p_12m) * 100
            signals['momentum_12m'] = round(mom_12m, 2)
            if mom_12m > 20:
                signals['technical_score'] += 1
                signals['factors'].append(f"Strong 12M return: +{mom_12m:.1f}%")
            elif mom_12m < -20:
                signals['technical_score'] -= 1
                signals['factors'].append(f"Poor 12M return: {mom_12m:.1f}%")

        if len(prices) >= 14:
            delta = prices.diff().dropna()
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta.where(delta < 0, 0.0))
            avg_gain = gain.rolling(14).mean().iloc[-1]
            avg_loss = loss.rolling(14).mean().iloc[-1]
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 100
            signals['rsi'] = round(rsi, 1)
            if rsi > 70:
                signals['technical_score'] -= 1
                signals['factors'].append(f"RSI overbought: {rsi:.0f}")
            elif rsi < 30:
                signals['technical_score'] += 1
                signals['factors'].append(f"RSI oversold: {rsi:.0f} (potential bounce)")
            else:
                signals['factors'].append(f"RSI neutral: {rsi:.0f}")

        if len(prices) >= 50:
            ma50 = prices.rolling(50).mean().iloc[-1]
            ma20 = prices.rolling(20).mean().iloc[-1]
            if current > ma50 and ma20 > ma50:
                signals['ma_trend'] = 'Bullish'
                signals['technical_score'] += 1
                signals['factors'].append("Price above 50-day MA — bullish trend")
            elif current < ma50 and ma20 < ma50:
                signals['ma_trend'] = 'Bearish'
                signals['technical_score'] -= 1
                signals['factors'].append("Price below 50-day MA — bearish trend")
            else:
                signals['ma_trend'] = 'Mixed'
                signals['factors'].append("Mixed moving average signals")

        if len(prices) >= 30:
            daily_returns = prices.pct_change().dropna()
            vol = daily_returns.std() * np.sqrt(252) * 100
            signals['volatility'] = round(vol, 1)
            if vol > 40:
                signals['technical_score'] -= 1
                signals['factors'].append(f"High volatility: {vol:.0f}% annualized")
            elif vol < 20:
                signals['technical_score'] += 1
                signals['factors'].append(f"Low volatility: {vol:.0f}% annualized")

        score = signals['technical_score']
        if score >= 3:
            signals['technical_signal'] = 'Strong Bullish'
        elif score >= 1:
            signals['technical_signal'] = 'Bullish'
        elif score <= -3:
            signals['technical_signal'] = 'Strong Bearish'
        elif score <= -1:
            signals['technical_signal'] = 'Bearish'
        else:
            signals['technical_signal'] = 'Neutral'

    except Exception as e:
        signals['factors'].append(f"Technical analysis limited")

    return signals


def compute_fundamental_signals(stock, recommendation):
    signals = {
        'fundamental_score': 0,
        'fundamental_signal': 'Neutral',
        'factors': []
    }

    try:
        fundamentals = recommendation.get('fundamentals', {}) if recommendation else {}

        pe = fundamentals.get('pe_ratio')
        if pe:
            if pe < 15:
                signals['fundamental_score'] += 2
                signals['factors'].append(f"Attractive P/E: {pe:.1f}")
            elif pe < 25:
                signals['fundamental_score'] += 1
                signals['factors'].append(f"Fair P/E: {pe:.1f}")
            elif pe > 40:
                signals['fundamental_score'] -= 1
                signals['factors'].append(f"Expensive P/E: {pe:.1f}")
            else:
                signals['factors'].append(f"P/E: {pe:.1f}")

        pb = fundamentals.get('pb_ratio')
        if pb:
            if pb < 1.5:
                signals['fundamental_score'] += 1
                signals['factors'].append(f"Low P/B: {pb:.1f}")
            elif pb > 4:
                signals['fundamental_score'] -= 1
                signals['factors'].append(f"High P/B: {pb:.1f}")

        roe = fundamentals.get('roe')
        if roe:
            if roe > 0.20:
                signals['fundamental_score'] += 2
                signals['factors'].append(f"Excellent ROE: {roe*100:.1f}%")
            elif roe > 0.12:
                signals['fundamental_score'] += 1
                signals['factors'].append(f"Good ROE: {roe*100:.1f}%")
            elif roe < 0.05:
                signals['fundamental_score'] -= 1
                signals['factors'].append(f"Weak ROE: {roe*100:.1f}%")

        de = fundamentals.get('debt_to_equity')
        if de:
            if de < 0.5:
                signals['fundamental_score'] += 1
                signals['factors'].append(f"Low debt: D/E {de:.2f}")
            elif de > 2:
                signals['fundamental_score'] -= 1
                signals['factors'].append(f"High debt: D/E {de:.2f}")

        eg = fundamentals.get('earnings_growth')
        if eg is not None:
            if eg > 0.15:
                signals['fundamental_score'] += 1
                signals['factors'].append(f"Strong earnings growth: {eg*100:.1f}%")
            elif eg < -0.10:
                signals['fundamental_score'] -= 1
                signals['factors'].append(f"Earnings decline: {eg*100:.1f}%")

        dy = fundamentals.get('dividend_yield')
        if dy and dy > 0.02:
            signals['fundamental_score'] += 1
            signals['factors'].append(f"Good dividend: {dy*100:.1f}%")

        score = signals['fundamental_score']
        if score >= 4:
            signals['fundamental_signal'] = 'Strong'
        elif score >= 2:
            signals['fundamental_signal'] = 'Good'
        elif score <= -2:
            signals['fundamental_signal'] = 'Weak'
        elif score <= 0:
            signals['fundamental_signal'] = 'Fair'
        else:
            signals['fundamental_signal'] = 'Moderate'

    except Exception:
        signals['factors'].append("Limited fundamental data")

    return signals


def compute_quantamental_score(fund_score, tech_score, fund_weight=0.55, tech_weight=0.45):
    norm_fund = max(min((fund_score + 5) / 10 * 100, 100), 0)
    norm_tech = max(min((tech_score + 5) / 10 * 100, 100), 0)
    composite = norm_fund * fund_weight + norm_tech * tech_weight
    return round(composite, 1), round(norm_fund, 1), round(norm_tech, 1)


def get_quantamental_action(composite_score):
    if composite_score >= 70:
        return 'BUY', 'High', '#2ecc71'
    elif composite_score >= 55:
        return 'BUY', 'Medium', '#27ae60'
    elif composite_score >= 40:
        return 'HOLD', 'Medium', '#f39c12'
    elif composite_score >= 25:
        return 'SELL', 'Medium', '#e67e22'
    else:
        return 'SELL', 'High', '#e74c3c'


def get_signal_label(fund_signal, tech_signal):
    bullish_tech = tech_signal in ('Strong Bullish', 'Bullish')
    bearish_tech = tech_signal in ('Strong Bearish', 'Bearish')
    strong_fund = fund_signal in ('Strong', 'Good')
    weak_fund = fund_signal in ('Weak',)

    if strong_fund and bullish_tech:
        return "High Conviction BUY", "#2ecc71"
    elif strong_fund and bearish_tech:
        return "Value Trap Risk", "#f39c12"
    elif weak_fund and bullish_tech:
        return "Momentum Only", "#3498db"
    elif weak_fund and bearish_tech:
        return "High Conviction SELL", "#e74c3c"
    elif strong_fund:
        return "Fundamental Strength", "#27ae60"
    elif bullish_tech:
        return "Technical Uptrend", "#3498db"
    elif bearish_tech:
        return "Technical Downtrend", "#e67e22"
    else:
        return "Neutral / Watch", "#95a5a6"


def render_quantamental_tab(analysis_results, recommendations, historical_data):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); border-radius: 16px; padding: 30px; margin-bottom: 25px; color: white;'>
        <div style='display: flex; align-items: center; gap: 15px; flex-wrap: wrap;'>
            <div style='font-size: 40px;'>🔬</div>
            <div>
                <h2 style='margin: 0; color: white; font-size: 26px;'>Quantamental Analysis</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.85; font-size: 15px;'>
                    Fundamental Quality + Technical Momentum = Smarter Decisions
                </p>
            </div>
        </div>
        <div style='margin-top: 15px; padding: 12px 18px; background: rgba(255,255,255,0.08); border-radius: 10px; font-size: 13px; line-height: 1.6;'>
            <strong>What is Quantamental?</strong> It blends traditional fundamental analysis (P/E, ROE, debt, earnings) 
            with quantitative technical signals (momentum, RSI, moving averages, volatility) to give a complete picture. 
            A stock can look great fundamentally but be in a downtrend, or vice versa — this view catches both.
        </div>
    </div>
    """, unsafe_allow_html=True)

    stock_perf = analysis_results.get('stock_performance', [])
    if not stock_perf:
        st.warning("No stock performance data available.")
        return

    rec_map = {}
    if recommendations:
        for r in recommendations:
            rec_map[r.get('stock_name', '')] = r

    results = []
    for sp in stock_perf:
        name = sp.get('Stock Name', '')
        rec = rec_map.get(name, {})

        tech = compute_technical_signals(sp, historical_data)
        fund = compute_fundamental_signals(sp, rec)

        composite, norm_fund, norm_tech = compute_quantamental_score(
            fund['fundamental_score'], tech['technical_score']
        )
        action, confidence, color = get_quantamental_action(composite)
        signal_label, signal_color = get_signal_label(fund['fundamental_signal'], tech['technical_signal'])

        results.append({
            'stock_name': name,
            'sector': sp.get('Sector', 'N/A'),
            'current_price': sp.get('Current Price', 0),
            'gain_loss_pct': sp.get('Percentage Gain/Loss', 0),
            'current_value': sp.get('Current Value', 0),
            'investment': sp.get('Investment', 0),
            'composite_score': composite,
            'fundamental_score_norm': norm_fund,
            'technical_score_norm': norm_tech,
            'fundamental_signal': fund['fundamental_signal'],
            'technical_signal': tech['technical_signal'],
            'signal_label': signal_label,
            'signal_color': signal_color,
            'action': action,
            'confidence': confidence,
            'action_color': color,
            'fund_factors': fund['factors'],
            'tech_factors': tech['factors'],
            'momentum_3m': tech.get('momentum_3m'),
            'momentum_6m': tech.get('momentum_6m'),
            'rsi': tech.get('rsi'),
            'ma_trend': tech.get('ma_trend'),
            'volatility': tech.get('volatility'),
        })

    results.sort(key=lambda x: x['composite_score'], reverse=True)

    buy_stocks = [r for r in results if r['action'] == 'BUY']
    hold_stocks = [r for r in results if r['action'] == 'HOLD']
    sell_stocks = [r for r in results if r['action'] == 'SELL']

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; border-left: 4px solid #2ecc71; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>BUY</div>
            <div style='font-size: 28px; font-weight: 700; color: #2ecc71; margin-top: 5px;'>{len(buy_stocks)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; border-left: 4px solid #f39c12; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>HOLD</div>
            <div style='font-size: 28px; font-weight: 700; color: #f39c12; margin-top: 5px;'>{len(hold_stocks)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; border-left: 4px solid #e74c3c; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>SELL</div>
            <div style='font-size: 28px; font-weight: 700; color: #e74c3c; margin-top: 5px;'>{len(sell_stocks)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        avg_score = np.mean([r['composite_score'] for r in results]) if results else 0
        score_color = '#2ecc71' if avg_score >= 55 else '#f39c12' if avg_score >= 40 else '#e74c3c'
        col_metric, col_info = st.columns([5, 1])
        with col_metric:
            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; border-left: 4px solid {score_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>Avg Score</div>
                <div style='font-size: 28px; font-weight: 700; color: {score_color}; margin-top: 5px;'>{avg_score:.0f}/100</div>
            </div>
            """, unsafe_allow_html=True)
        with col_info:
            render_metric_info('avg_score')

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    hdr_col1, hdr_col2 = st.columns([10, 1])
    with hdr_col1:
        st.markdown("### 📊 Signal Matrix")
    with hdr_col2:
        render_metric_info('signal_label')

    st.markdown("""
    <p style='color: #666; font-size: 13px; margin-bottom: 15px;'>
        Each stock is classified by combining its fundamental quality with technical momentum.
        The strongest conviction comes when both align. Click ℹ️ on any metric for details.
    </p>
    """, unsafe_allow_html=True)

    for idx, r in enumerate(results):
        gain_color = "#2ecc71" if r['gain_loss_pct'] >= 0 else "#e74c3c"
        gain_icon = "▲" if r['gain_loss_pct'] >= 0 else "▼"

        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 18px 22px; margin-bottom: 12px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-left: 5px solid {r["action_color"]};'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;'>
                <div style='flex: 1; min-width: 150px;'>
                    <div style='font-size: 17px; font-weight: 700; color: #333;'>{r["stock_name"]}</div>
                    <div style='font-size: 12px; color: #888;'>{r["sector"]}</div>
                </div>
                <div style='text-align: center; min-width: 80px;'>
                    <div style='font-size: 12px; color: #888;'>Composite</div>
                    <div style='font-size: 22px; font-weight: 700; color: {r["action_color"]};'>{r["composite_score"]:.0f}</div>
                </div>
                <div style='text-align: center; min-width: 80px;'>
                    <div style='font-size: 12px; color: #888;'>Fund</div>
                    <div style='font-size: 14px; font-weight: 600; color: #555;'>{r["fundamental_signal"]}</div>
                </div>
                <div style='text-align: center; min-width: 80px;'>
                    <div style='font-size: 12px; color: #888;'>Tech</div>
                    <div style='font-size: 14px; font-weight: 600; color: #555;'>{r["technical_signal"]}</div>
                </div>
                <div style='text-align: center; min-width: 100px;'>
                    <span style='background: {r["signal_color"]}22; color: {r["signal_color"]}; padding: 4px 12px; 
                                border-radius: 20px; font-size: 12px; font-weight: 600;'>{r["signal_label"]}</span>
                </div>
                <div style='text-align: center; min-width: 70px;'>
                    <span style='background: {r["action_color"]}; color: white; padding: 6px 16px; 
                                border-radius: 8px; font-weight: 700; font-size: 14px;'>{r["action"]}</span>
                    <div style='font-size: 11px; color: #888; margin-top: 3px;'>{r["confidence"]} conf.</div>
                </div>
                <div style='text-align: right; min-width: 90px;'>
                    <div style='font-size: 14px; color: #333;'>₹{r["current_price"]:,.1f}</div>
                    <div style='font-size: 13px; color: {gain_color};'>{gain_icon} {r["gain_loss_pct"]:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"ℹ️ View metric details for {r['stock_name']}", expanded=False):
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**Composite Score**")
                st.markdown(f"Score: **{r['composite_score']:.0f}/100**")
                st.markdown(f"<span style='font-size:12px; color:#666;'>{METRIC_EXPLANATIONS['composite_score']['interpretation']}</span>", unsafe_allow_html=True)
            with d2:
                st.markdown("**Fundamental Signal**")
                st.markdown(f"Signal: **{r['fundamental_signal']}** (Normalized: {r['fundamental_score_norm']:.0f})")
                st.markdown(f"<span style='font-size:12px; color:#666;'>{METRIC_EXPLANATIONS['fundamental_signal']['description']}</span>", unsafe_allow_html=True)
            with d3:
                st.markdown("**Technical Signal**")
                st.markdown(f"Signal: **{r['technical_signal']}** (Normalized: {r['technical_score_norm']:.0f})")
                st.markdown(f"<span style='font-size:12px; color:#666;'>{METRIC_EXPLANATIONS['technical_signal']['description']}</span>", unsafe_allow_html=True)

            st.markdown("---")
            t1, t2, t3, t4, t5 = st.columns(5)
            with t1:
                mom3 = r.get('momentum_3m')
                st.metric("3M Momentum", f"{mom3:+.1f}%" if mom3 is not None else "N/A",
                         help=METRIC_EXPLANATIONS['momentum_3m']['description'])
            with t2:
                mom6 = r.get('momentum_6m')
                st.metric("6M Momentum", f"{mom6:+.1f}%" if mom6 is not None else "N/A",
                         help=METRIC_EXPLANATIONS['momentum_6m']['description'])
            with t3:
                rsi_val = r.get('rsi')
                st.metric("RSI (14)", f"{rsi_val:.0f}" if rsi_val is not None else "N/A",
                         help=METRIC_EXPLANATIONS['rsi']['description'])
            with t4:
                ma = r.get('ma_trend', 'N/A')
                st.metric("MA Trend", ma or "N/A",
                         help=METRIC_EXPLANATIONS['ma_trend']['description'])
            with t5:
                vol = r.get('volatility')
                st.metric("Volatility", f"{vol:.0f}%" if vol is not None else "N/A",
                         help=METRIC_EXPLANATIONS['volatility']['description'])

            st.markdown("---")
            ff1, ff2 = st.columns(2)
            with ff1:
                st.markdown("**Fundamental Factors:**")
                for f in r['fund_factors']:
                    st.markdown(f"- {f}")
                if not r['fund_factors']:
                    st.markdown("- *No data available*")
            with ff2:
                st.markdown("**Technical Factors:**")
                for f in r['tech_factors']:
                    st.markdown(f"- {f}")
                if not r['tech_factors']:
                    st.markdown("- *No data available*")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        hdr1, hdr1i = st.columns([8, 1])
        with hdr1:
            st.markdown("### 🎯 Composite Score Breakdown")
        with hdr1i:
            render_metric_info('composite_score')

        df_scores = pd.DataFrame([{
            'Stock': r['stock_name'],
            'Fundamental': r['fundamental_score_norm'],
            'Technical': r['technical_score_norm'],
            'Composite': r['composite_score']
        } for r in results])

        if not df_scores.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=df_scores['Stock'], x=df_scores['Fundamental'],
                name='Fundamental (55%)', orientation='h',
                marker_color='#3498db', opacity=0.85
            ))
            fig.add_trace(go.Bar(
                y=df_scores['Stock'], x=df_scores['Technical'],
                name='Technical (45%)', orientation='h',
                marker_color='#e74c3c', opacity=0.85
            ))
            fig.update_layout(
                barmode='group', height=max(300, len(results) * 45),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                xaxis_title='Score (0-100)', yaxis=dict(autorange='reversed'),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        hdr2, hdr2i = st.columns([8, 1])
        with hdr2:
            st.markdown("### 📈 Factor Exposure")
        with hdr2i:
            render_metric_info('factor_exposure')

        avg_fund = np.mean([r['fundamental_score_norm'] for r in results]) if results else 50
        avg_tech = np.mean([r['technical_score_norm'] for r in results]) if results else 50

        fund_tilt = sum(1 for r in results if r['fundamental_score_norm'] > r['technical_score_norm'])
        tech_tilt = len(results) - fund_tilt

        categories = ['Value', 'Quality', 'Momentum', 'Low Vol', 'Growth']
        value_score = np.mean([r['fundamental_score_norm'] for r in results if any('P/E' in f or 'P/B' in f for f in r['fund_factors'])]) if results else 50
        quality_score = np.mean([r['fundamental_score_norm'] for r in results if any('ROE' in f or 'debt' in f.lower() for f in r['fund_factors'])]) if results else 50
        momentum_score = avg_tech
        vol_scores = [100 - min(r.get('volatility', 25) or 25, 60) / 60 * 100 for r in results]
        low_vol_score = np.mean(vol_scores) if vol_scores else 50
        growth_score = np.mean([r['technical_score_norm'] for r in results if any('earnings' in f.lower() or 'growth' in f.lower() for f in r['fund_factors'])]) if results else 50

        values = [
            max(10, min(value_score, 100)),
            max(10, min(quality_score, 100)),
            max(10, min(momentum_score, 100)),
            max(10, min(low_vol_score, 100)),
            max(10, min(growth_score, 100))
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.2)',
            line=dict(color='#667eea', width=2),
            name='Your Portfolio'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False, height=350,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown(f"""
        <div style='background: #f8f9fa; border-radius: 10px; padding: 15px; font-size: 13px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                <span>Fundamental Tilt</span><strong>{fund_tilt} stocks</strong>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span>Technical/Momentum Tilt</span><strong>{tech_tilt} stocks</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    hdr3, hdr3i = st.columns([10, 1])
    with hdr3:
        st.markdown("### ⚖️ Quantamental Rebalancing Suggestions")
    with hdr3i:
        render_metric_info('rebalancing')

    st.markdown("""
    <p style='color: #666; font-size: 13px; margin-bottom: 15px;'>
        Based on composite scores, here's how to adjust your portfolio for optimal fundamental + technical alignment.
    </p>
    """, unsafe_allow_html=True)

    total_value = sum(r['current_value'] for r in results) or 1

    rebal_data = []
    for r in results:
        current_weight = (r['current_value'] / total_value) * 100
        score_weight = r['composite_score']
        total_score = sum(x['composite_score'] for x in results) or 1
        target_weight = (score_weight / total_score) * 100
        diff = target_weight - current_weight

        if abs(diff) < 1:
            rebal_action = "No Change"
            rebal_color = "#95a5a6"
        elif diff > 0:
            rebal_action = f"Increase by {abs(diff):.1f}%"
            rebal_color = "#2ecc71"
        else:
            rebal_action = f"Reduce by {abs(diff):.1f}%"
            rebal_color = "#e74c3c"

        rebal_data.append({
            'Stock': r['stock_name'],
            'Current Weight': f"{current_weight:.1f}%",
            'Target Weight': f"{target_weight:.1f}%",
            'Score': r['composite_score'],
            'Action': rebal_action,
            'diff': diff,
            'color': rebal_color
        })

    for rd in sorted(rebal_data, key=lambda x: abs(x['diff']), reverse=True):
        st.markdown(f"""
        <div style='background: white; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; 
                    box-shadow: 0 1px 5px rgba(0,0,0,0.04); display: flex; justify-content: space-between; 
                    align-items: center; flex-wrap: wrap; gap: 8px;'>
            <div style='min-width: 140px;'>
                <span style='font-weight: 600; color: #333;'>{rd["Stock"]}</span>
                <span style='margin-left: 8px; font-size: 12px; color: #888;'>Score: {rd["Score"]:.0f}</span>
            </div>
            <div style='font-size: 13px; color: #666;'>{rd["Current Weight"]} → {rd["Target Weight"]}</div>
            <span style='color: {rd["color"]}; font-weight: 600; font-size: 13px;'>{rd["Action"]}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    hdr4, hdr4i = st.columns([10, 1])
    with hdr4:
        st.markdown("### 🏆 Risk-Adjusted Rankings")
    with hdr4i:
        render_metric_info('risk_adjusted')

    st.markdown("""
    <p style='color: #666; font-size: 13px; margin-bottom: 15px;'>
        Stocks ranked by quality-adjusted return — combining your actual returns with the composite score 
        and volatility to identify the best risk-reward positions.
    </p>
    """, unsafe_allow_html=True)

    ranked = []
    for r in results:
        vol = r.get('volatility') or 25
        ret = r['gain_loss_pct']
        score_bonus = (r['composite_score'] - 50) / 10
        risk_adj = (ret / max(vol, 5)) + score_bonus
        ranked.append({
            'Stock': r['stock_name'],
            'Return': f"{ret:+.1f}%",
            'Volatility': f"{vol:.0f}%",
            'Composite': f"{r['composite_score']:.0f}",
            'Risk-Adj Score': round(risk_adj, 2),
            'Action': r['action'],
            'action_color': r['action_color'],
        })

    ranked.sort(key=lambda x: x['Risk-Adj Score'], reverse=True)

    for i, rk in enumerate(ranked):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        score_color = '#2ecc71' if rk['Risk-Adj Score'] > 0.5 else '#f39c12' if rk['Risk-Adj Score'] > 0 else '#e74c3c'

        st.markdown(f"""
        <div style='background: white; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; 
                    box-shadow: 0 1px 5px rgba(0,0,0,0.04); display: flex; justify-content: space-between; 
                    align-items: center; flex-wrap: wrap; gap: 8px;'>
            <div style='min-width: 40px; font-size: 18px; text-align: center;'>{medal}</div>
            <div style='min-width: 130px; font-weight: 600; color: #333;'>{rk["Stock"]}</div>
            <div style='font-size: 13px; color: #666;'>Ret: {rk["Return"]}</div>
            <div style='font-size: 13px; color: #666;'>Vol: {rk["Volatility"]}</div>
            <div style='font-size: 13px; color: #666;'>Score: {rk["Composite"]}</div>
            <div style='font-size: 15px; font-weight: 700; color: {score_color};'>{rk["Risk-Adj Score"]:.2f}</div>
            <span style='background: {rk["action_color"]}; color: white; padding: 4px 12px; 
                        border-radius: 6px; font-weight: 600; font-size: 12px;'>{rk["Action"]}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    with st.expander("📖 Metric Glossary — What does each metric mean?", expanded=False):
        for key in ['composite_score', 'fundamental_signal', 'technical_signal', 'signal_label',
                     'pe_ratio', 'pb_ratio', 'roe', 'debt_to_equity', 'earnings_growth', 'dividend_yield',
                     'momentum_3m', 'momentum_6m', 'momentum_12m', 'rsi', 'ma_trend', 'volatility',
                     'risk_adjusted', 'rebalancing']:
            info = METRIC_EXPLANATIONS.get(key, {})
            if info:
                st.markdown(f"**ℹ️ {info['title']}**")
                st.markdown(f"{info['description']}")
                st.markdown(f"*{info['interpretation']}*")
                st.markdown("---")

    st.markdown("""
    <div style='background: #e8f4f8; border-radius: 10px; padding: 15px; margin-top: 10px; border-left: 4px solid #3498db;'>
        <p style='margin: 0; font-size: 12px; color: #2c3e50;'>
            <strong>Methodology:</strong> Fundamental score (55% weight) uses P/E, P/B, ROE, D/E, earnings growth, and dividend yield. 
            Technical score (45% weight) uses 3M/6M/12M momentum, RSI(14), 20/50-day MA crossovers, and annualized volatility. 
            Both are normalized to 0-100 and combined into a composite score. This is not financial advice.
        </p>
    </div>
    """, unsafe_allow_html=True)
