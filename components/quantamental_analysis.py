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
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; border-left: 4px solid {score_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>Avg Score</div>
            <div style='font-size: 28px; font-weight: 700; color: {score_color}; margin-top: 5px;'>{avg_score:.0f}/100</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    st.markdown("### 📊 Signal Matrix")
    st.markdown("""
    <p style='color: #666; font-size: 13px; margin-bottom: 15px;'>
        Each stock is classified by combining its fundamental quality with technical momentum.
        The strongest conviction comes when both align.
    </p>
    """, unsafe_allow_html=True)

    for r in results:
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

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🎯 Composite Score Breakdown")
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
                name='Fundamental', orientation='h',
                marker_color='#3498db', opacity=0.85
            ))
            fig.add_trace(go.Bar(
                y=df_scores['Stock'], x=df_scores['Technical'],
                name='Technical', orientation='h',
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
        st.markdown("### 📈 Factor Exposure")
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

    st.markdown("### ⚖️ Quantamental Rebalancing Suggestions")
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

    st.markdown("### 🏆 Risk-Adjusted Rankings")
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

    with st.expander("📋 Detailed Factor Analysis Per Stock", expanded=False):
        for r in results:
            st.markdown(f"**{r['stock_name']}** — Composite: {r['composite_score']:.0f} | Action: {r['action']}")
            fc1, fc2 = st.columns(2)
            with fc1:
                st.markdown("**Fundamental Factors:**")
                for f in r['fund_factors']:
                    st.markdown(f"- {f}")
                if not r['fund_factors']:
                    st.markdown("- *No data available*")
            with fc2:
                st.markdown("**Technical Factors:**")
                for f in r['tech_factors']:
                    st.markdown(f"- {f}")
                if not r['tech_factors']:
                    st.markdown("- *No data available*")
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
