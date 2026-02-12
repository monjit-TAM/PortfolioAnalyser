import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from openai import OpenAI
from utils.page_explanations import SUPPORTED_LANGUAGES, translate_text


def _fmt(val, prefix="₹"):
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 10000000:
            return f"{prefix}{v/10000000:,.2f} Cr"
        elif abs(v) >= 100000:
            return f"{prefix}{v/100000:,.2f} L"
        else:
            return f"{prefix}{v:,.0f}"
    except:
        return str(val)


def _pct(val):
    if val is None:
        return "N/A"
    try:
        return f"{float(val):+.2f}%"
    except:
        return str(val)


def _safe(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d if d is not None else default


def generate_summary_text(analysis_results, advanced_metrics, recommendations):
    summary = analysis_results.get('portfolio_summary', {})
    stock_perf = analysis_results.get('stock_performance', [])
    dividend_metrics = analysis_results.get('dividend_metrics', {})
    sector_analysis = analysis_results.get('sector_analysis', {})

    total_investment = summary.get('total_investment', 0)
    current_value = summary.get('current_value', 0)
    total_gain = summary.get('total_gain_loss', 0)
    total_gain_pct = summary.get('total_gain_loss_percentage', 0)
    num_stocks = summary.get('number_of_stocks', 0)
    profitable = summary.get('profitable_stocks', 0)
    loss_making = summary.get('loss_making_stocks', 0)

    df = pd.DataFrame(stock_perf) if stock_perf else pd.DataFrame()

    sections = []

    sections.append("PORTFOLIO OVERVIEW")
    sections.append(f"You invested {_fmt(total_investment)} across {num_stocks} stocks.")
    sections.append(f"Your portfolio is now worth {_fmt(current_value)}.")
    if total_gain >= 0:
        sections.append(f"You have made a profit of {_fmt(total_gain)} ({_pct(total_gain_pct)}).")
    else:
        sections.append(f"You have a loss of {_fmt(abs(total_gain))} ({_pct(total_gain_pct)}).")
    sections.append(f"Out of {num_stocks} stocks, {profitable} are in profit and {loss_making} are in loss.")
    sections.append("")

    if not df.empty and 'Percentage Gain/Loss' in df.columns:
        top = df.nlargest(3, 'Percentage Gain/Loss')
        bottom = df.nsmallest(3, 'Percentage Gain/Loss')

        sections.append("TOP PERFORMERS")
        for _, row in top.iterrows():
            name = row.get('Stock Name', 'Unknown')
            pct = row.get('Percentage Gain/Loss', 0)
            gain = row.get('Absolute Gain/Loss', 0)
            sections.append(f"  {name}: {_pct(pct)} ({_fmt(gain)} profit)")
        sections.append("")

        sections.append("STOCKS NEEDING ATTENTION")
        for _, row in bottom.iterrows():
            name = row.get('Stock Name', 'Unknown')
            pct = row.get('Percentage Gain/Loss', 0)
            gain = row.get('Absolute Gain/Loss', 0)
            if pct < 0:
                sections.append(f"  {name}: {_pct(pct)} ({_fmt(abs(gain))} loss)")
            else:
                sections.append(f"  {name}: {_pct(pct)} (lowest gain)")
        sections.append("")

    if sector_analysis:
        sectors = sector_analysis if isinstance(sector_analysis, list) else []
        if not sectors and isinstance(sector_analysis, dict):
            sectors = sector_analysis.get('sectors', [])
        if sectors:
            sections.append("SECTOR BREAKDOWN")
            for s in sectors[:5]:
                if isinstance(s, dict):
                    sname = s.get('sector', s.get('Sector', 'Unknown'))
                    sweight = s.get('weight', s.get('allocation', s.get('Allocation', 0)))
                    sections.append(f"  {sname}: {float(sweight):.1f}% of portfolio")
            sections.append("")

    if not df.empty and 'Current Value' in df.columns:
        total_val = df['Current Value'].sum()
        if total_val > 0:
            df_sorted = df.sort_values('Current Value', ascending=False)
            top_stock = df_sorted.iloc[0]
            top_weight = (top_stock['Current Value'] / total_val * 100)
            if top_weight > 25:
                sections.append("CONCENTRATION ALERT")
                sections.append(f"  {top_stock['Stock Name']} makes up {top_weight:.1f}% of your portfolio. Consider spreading your investment more evenly to reduce risk.")
                sections.append("")

    if advanced_metrics:
        health = advanced_metrics.get('health_score', {})
        overall_score = health.get('overall_score', 0)
        grade = health.get('grade', 'N/A')
        health_summary = health.get('summary', '')

        sections.append("PORTFOLIO HEALTH")
        sections.append(f"  Health Score: {overall_score}/100 (Grade: {grade})")
        if health_summary:
            sections.append(f"  {health_summary}")

        component_scores = health.get('component_scores', {})
        if component_scores:
            sections.append("  Component Scores:")
            for comp, score in component_scores.items():
                label = comp.replace('_', ' ').title()
                sections.append(f"    {label}: {score}/100")
        sections.append("")

        vol = advanced_metrics.get('volatility', {})
        hist_vol = vol.get('historical_volatility', None)
        if hist_vol is not None:
            risk_level = "High" if hist_vol > 30 else "Moderate" if hist_vol > 20 else "Low"
            sections.append("RISK LEVEL")
            sections.append(f"  Portfolio volatility: {hist_vol:.1f}% ({risk_level} risk)")
            max_dd = vol.get('max_drawdown', None)
            if max_dd is not None:
                sections.append(f"  Maximum drawdown: {_pct(max_dd)} (worst-case drop from peak)")
            sections.append("")

        tax = advanced_metrics.get('tax_impact', {})
        if tax:
            stcg_count = tax.get('stcg_count', 0)
            ltcg_count = tax.get('ltcg_count', 0)
            if stcg_count or ltcg_count:
                sections.append("TAX IMPACT")
                sections.append(f"  Short-term capital gains (STCG) stocks: {stcg_count} (taxed at 20%)")
                sections.append(f"  Long-term capital gains (LTCG) stocks: {ltcg_count} (taxed at 12.5% above ₹1.25L)")
                total_stcg = tax.get('total_stcg', 0)
                total_ltcg = tax.get('total_ltcg', 0)
                if total_stcg > 0:
                    sections.append(f"  Estimated STCG: {_fmt(total_stcg)}")
                if total_ltcg > 0:
                    sections.append(f"  Estimated LTCG: {_fmt(total_ltcg)}")
                sections.append("")

    if dividend_metrics:
        annual_div = dividend_metrics.get('total_annual_dividend', 0)
        div_yield = dividend_metrics.get('portfolio_dividend_yield', 0)
        if annual_div > 0:
            sections.append("DIVIDEND INCOME")
            sections.append(f"  You earn approximately {_fmt(annual_div)} per year in dividends.")
            sections.append(f"  Portfolio dividend yield: {div_yield:.2f}%")
            highest_stock = dividend_metrics.get('highest_yield_stock', 'N/A')
            highest_val = dividend_metrics.get('highest_yield_value', 0)
            if highest_stock != 'N/A':
                sections.append(f"  Best dividend payer: {highest_stock} ({highest_val:.2f}% yield)")
            sections.append("")

    if recommendations:
        buy_recs = [r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'BUY']
        hold_recs = [r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'HOLD']
        sell_recs = [r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'SELL']

        sections.append("WHAT SHOULD YOU DO?")
        if sell_recs:
            sections.append(f"  Consider Selling ({len(sell_recs)} stocks):")
            for r in sell_recs:
                reason = r.get('overall_recommendation', {}).get('rationale', '')
                sections.append(f"    {r['stock_name']}: {reason}")
        if buy_recs:
            sections.append(f"  Keep Adding ({len(buy_recs)} stocks):")
            for r in buy_recs:
                reason = r.get('overall_recommendation', {}).get('rationale', '')
                sections.append(f"    {r['stock_name']}: {reason}")
        if hold_recs:
            sections.append(f"  Hold Steady ({len(hold_recs)} stocks):")
            for r in hold_recs[:5]:
                sections.append(f"    {r['stock_name']}")
            if len(hold_recs) > 5:
                sections.append(f"    ...and {len(hold_recs) - 5} more")
        sections.append("")

    sections.append("IMPORTANT DISCLAIMER")
    sections.append("This analysis is for informational purposes only and should not be considered as financial advice. Always consult a SEBI-registered financial advisor before making investment decisions. Past performance does not guarantee future results.")

    return "\n".join(sections)


def generate_tts_audio(text, lang_code="en"):
    try:
        client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        )

        lang_names = {v: k.split(" (")[0] if " (" in k else k for k, v in SUPPORTED_LANGUAGES.items()}
        lang_name = lang_names.get(lang_code, "English")

        if lang_code != "en":
            tts_prompt = f"Read the following portfolio analysis report in {lang_name}. Speak clearly and at a moderate pace, as if you are a friendly financial advisor explaining to a client. Keep financial terms like Nifty 50, P/E ratio, Alpha, Beta, STCG, LTCG in English. Here is the report:\n\n{text}"
        else:
            tts_prompt = f"Read the following portfolio analysis report aloud. Speak clearly and at a moderate pace, as if you are a friendly financial advisor explaining to a client. Here is the report:\n\n{text}"

        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-audio",
            modalities=["text", "audio"],
            audio={"voice": "nova", "format": "wav"},
            messages=[
                {"role": "system", "content": f"You are a professional financial advisor narrating a portfolio analysis report in {lang_name}. Read the content naturally and clearly. Do not add any commentary or extra content beyond what is provided."},
                {"role": "user", "content": tts_prompt},
            ],
        )

        audio_data = getattr(response.choices[0].message, "audio", None)
        if audio_data and hasattr(audio_data, "data"):
            return base64.b64decode(audio_data.data)
        return None
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)[:100]}")
        return None


def render_portfolio_summary(analysis_results, advanced_metrics, recommendations):
    lang_options = list(SUPPORTED_LANGUAGES.keys())

    if 'summary_language' not in st.session_state:
        st.session_state.summary_language = "English"

    summary = analysis_results.get('portfolio_summary', {})
    total_investment = summary.get('total_investment', 0)
    current_value = summary.get('current_value', 0)
    total_gain = summary.get('total_gain_loss', 0)
    total_gain_pct = summary.get('total_gain_loss_percentage', 0)
    num_stocks = summary.get('number_of_stocks', 0)
    profitable = summary.get('profitable_stocks', 0)
    gain_color = "#2ecc71" if total_gain >= 0 else "#e74c3c"
    gain_icon = "▲" if total_gain >= 0 else "▼"

    health = {}
    if advanced_metrics:
        health = advanced_metrics.get('health_score', {})
    health_score = health.get('overall_score', 0)
    health_grade = health.get('grade', '-')
    grade_color = "#2ecc71" if health_grade == "A" else "#27ae60" if health_grade == "B" else "#f39c12" if health_grade == "C" else "#e74c3c"

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 30px; margin-bottom: 25px; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;'>
            <div>
                <h2 style='margin: 0 0 5px 0; font-size: 26px; color: white;'>Portfolio Summary</h2>
                <p style='margin: 0; opacity: 0.9; font-size: 15px;'>Everything you need to know at a glance</p>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 36px; font-weight: 700; color: white;'>{_fmt(current_value)}</div>
                <div style='font-size: 16px; color: {"#90EE90" if total_gain >= 0 else "#FFB3B3"};'>{gain_icon} {_pct(total_gain_pct)} ({_fmt(total_gain)})</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "Total Invested", _fmt(total_investment), "#3498db"),
        (c2, "Stocks", f"{num_stocks} ({profitable} in profit)", "#2ecc71"),
        (c3, "Health Score", f"{health_score}/100 ({health_grade})", grade_color),
        (c4, "Dividend Income", _fmt(analysis_results.get('dividend_metrics', {}).get('total_annual_dividend', 0)) + "/yr", "#9b59b6"),
    ]
    for col, label, value, color in metrics:
        with col:
            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 18px; text-align: center; 
                        border-left: 4px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <div style='font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;'>{label}</div>
                <div style='font-size: 20px; font-weight: 700; color: #333; margin-top: 5px;'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    stock_perf = analysis_results.get('stock_performance', [])
    df = pd.DataFrame(stock_perf) if stock_perf else pd.DataFrame()

    left_col, right_col = st.columns(2)

    with left_col:
        if not df.empty and 'Percentage Gain/Loss' in df.columns:
            st.markdown("""
            <div style='background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <h4 style='margin: 0 0 15px 0; color: #333;'>Winners & Losers</h4>
            """, unsafe_allow_html=True)

            top3 = df.nlargest(3, 'Percentage Gain/Loss')
            for _, row in top3.iterrows():
                name = row.get('Stock Name', '')
                pct = row.get('Percentage Gain/Loss', 0)
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;'>
                    <span style='color: #333;'>{name}</span>
                    <span style='color: #2ecc71; font-weight: 600;'>▲ {pct:+.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            bottom3 = df.nsmallest(3, 'Percentage Gain/Loss')
            for _, row in bottom3.iterrows():
                name = row.get('Stock Name', '')
                pct = row.get('Percentage Gain/Loss', 0)
                color = "#e74c3c" if pct < 0 else "#f39c12"
                icon = "▼" if pct < 0 else "▬"
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;'>
                    <span style='color: #333;'>{name}</span>
                    <span style='color: {color}; font-weight: 600;'>{icon} {pct:+.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        if recommendations:
            buy_count = len([r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'BUY'])
            hold_count = len([r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'HOLD'])
            sell_count = len([r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'SELL'])

            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <h4 style='margin: 0 0 15px 0; color: #333;'>Action Summary</h4>
                <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
                    <div style='flex: 1; background: #e8f5e9; border-radius: 8px; padding: 12px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: 700; color: #2e7d32;'>{buy_count}</div>
                        <div style='font-size: 11px; color: #388e3c; text-transform: uppercase;'>Buy/Add</div>
                    </div>
                    <div style='flex: 1; background: #fff3e0; border-radius: 8px; padding: 12px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: 700; color: #e65100;'>{hold_count}</div>
                        <div style='font-size: 11px; color: #f57c00; text-transform: uppercase;'>Hold</div>
                    </div>
                    <div style='flex: 1; background: #ffebee; border-radius: 8px; padding: 12px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: 700; color: #c62828;'>{sell_count}</div>
                        <div style='font-size: 11px; color: #d32f2f; text-transform: uppercase;'>Sell</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            sell_recs = [r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'SELL']
            if sell_recs:
                st.markdown("<div style='font-size: 13px; color: #c62828; font-weight: 600; margin-bottom: 5px;'>Consider Selling:</div>", unsafe_allow_html=True)
                for r in sell_recs[:3]:
                    rationale = r.get('overall_recommendation', {}).get('rationale', '')
                    st.markdown(f"<div style='font-size: 12px; color: #666; padding: 3px 0;'>• {r['stock_name']}: {rationale[:60]}</div>", unsafe_allow_html=True)

            buy_recs = [r for r in recommendations if r.get('overall_recommendation', {}).get('action') == 'BUY']
            if buy_recs:
                st.markdown("<div style='font-size: 13px; color: #2e7d32; font-weight: 600; margin-top: 8px; margin-bottom: 5px;'>Consider Adding:</div>", unsafe_allow_html=True)
                for r in buy_recs[:3]:
                    rationale = r.get('overall_recommendation', {}).get('rationale', '')
                    st.markdown(f"<div style='font-size: 12px; color: #666; padding: 3px 0;'>• {r['stock_name']}: {rationale[:60]}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if advanced_metrics:
        risk_col, tax_col = st.columns(2)

        with risk_col:
            vol = advanced_metrics.get('volatility', {})
            hist_vol = vol.get('historical_volatility', 0)
            risk_level = "High" if hist_vol > 30 else "Moderate" if hist_vol > 20 else "Low"
            risk_color = "#e74c3c" if risk_level == "High" else "#f39c12" if risk_level == "Moderate" else "#2ecc71"
            max_dd = vol.get('max_drawdown', 0)

            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <h4 style='margin: 0 0 15px 0; color: #333;'>Risk Assessment</h4>
                <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 12px;'>
                    <div style='background: {risk_color}20; color: {risk_color}; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 14px;'>{risk_level} Risk</div>
                    <span style='color: #888; font-size: 13px;'>Volatility: {hist_vol:.1f}%</span>
                </div>
                <div style='font-size: 13px; color: #666;'>
                    Maximum drawdown: {_pct(max_dd)}<br>
                    <span style='color: #999; font-size: 12px;'>This means your portfolio has dropped at most {abs(max_dd):.1f}% from a peak value in the past.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tax_col:
            tax = advanced_metrics.get('tax_impact', {})
            stcg_count = tax.get('stcg_count', 0)
            ltcg_count = tax.get('ltcg_count', 0)
            total_stcg = tax.get('total_stcg', 0)
            total_ltcg = tax.get('total_ltcg', 0)

            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                <h4 style='margin: 0 0 15px 0; color: #333;'>Tax Overview</h4>
                <div style='display: flex; gap: 15px; margin-bottom: 12px;'>
                    <div style='flex: 1;'>
                        <div style='font-size: 12px; color: #888;'>Short-Term (STCG)</div>
                        <div style='font-size: 18px; font-weight: 600; color: #e74c3c;'>{stcg_count} stocks</div>
                        <div style='font-size: 12px; color: #999;'>Gains: {_fmt(total_stcg)}</div>
                    </div>
                    <div style='flex: 1;'>
                        <div style='font-size: 12px; color: #888;'>Long-Term (LTCG)</div>
                        <div style='font-size: 18px; font-weight: 600; color: #2ecc71;'>{ltcg_count} stocks</div>
                        <div style='font-size: 12px; color: #999;'>Gains: {_fmt(total_ltcg)}</div>
                    </div>
                </div>
                <div style='font-size: 12px; color: #999;'>STCG taxed at 20% | LTCG taxed at 12.5% above ₹1.25L exemption</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%); border-radius: 12px; padding: 20px; 
                border: 1px solid #e0e7ff; margin-bottom: 15px;'>
        <h4 style='margin: 0 0 10px 0; color: #4a5568;'>Listen to Your Analysis or Read in Your Language</h4>
        <p style='margin: 0; color: #718096; font-size: 13px;'>Choose your preferred language below. You can read the full summary or listen to an audio version.</p>
    </div>
    """, unsafe_allow_html=True)

    lang_col, action_col = st.columns([1, 2])

    with lang_col:
        current_idx = lang_options.index(st.session_state.summary_language) if st.session_state.summary_language in lang_options else 0
        selected_lang = st.selectbox(
            "Choose Language",
            options=lang_options,
            index=current_idx,
            key="summary_lang_selector"
        )
        if selected_lang != st.session_state.summary_language:
            st.session_state.summary_language = selected_lang
            if 'summary_text_translated' in st.session_state:
                del st.session_state['summary_text_translated']
            if 'summary_audio' in st.session_state:
                del st.session_state['summary_audio']
            st.rerun()

    lang_code = SUPPORTED_LANGUAGES.get(st.session_state.summary_language, "en")

    summary_text = generate_summary_text(analysis_results, advanced_metrics, recommendations)

    if lang_code != "en":
        cache_key = f"summary_translated_{lang_code}"
        if cache_key not in st.session_state:
            with st.spinner(f"Translating summary to {st.session_state.summary_language}..."):
                st.session_state[cache_key] = translate_text(summary_text, lang_code)
        display_text = st.session_state[cache_key]
    else:
        display_text = summary_text

    with action_col:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            show_text = st.button("📖 Read Full Summary", use_container_width=True, key="show_summary_text")
        with btn_col2:
            generate_audio = st.button("🔊 Listen to Analysis", use_container_width=True, key="generate_audio_btn")

    if show_text or st.session_state.get('show_summary_detail', False):
        st.session_state.show_summary_detail = True
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); 
                    border: 1px solid #e2e8f0; white-space: pre-line; font-size: 14px; line-height: 1.8; color: #333;'>
{display_text}
        </div>
        """, unsafe_allow_html=True)

    if generate_audio:
        audio_cache_key = f"summary_audio_{lang_code}"
        if audio_cache_key not in st.session_state:
            with st.spinner(f"Generating audio in {st.session_state.summary_language}... This may take a moment."):
                text_for_audio = display_text if lang_code != "en" else summary_text
                audio_bytes = generate_tts_audio(text_for_audio, lang_code)
                if audio_bytes:
                    st.session_state[audio_cache_key] = audio_bytes
                    st.session_state.show_audio_player = True
                    st.rerun()
        else:
            st.session_state.show_audio_player = True

    audio_cache_key = f"summary_audio_{lang_code}"
    if st.session_state.get('show_audio_player', False) and audio_cache_key in st.session_state:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 15px; margin-top: 15px;'>
            <p style='color: white; margin: 0 0 10px 0; font-weight: 600;'>Your Portfolio Analysis Audio</p>
        </div>
        """, unsafe_allow_html=True)
        st.audio(st.session_state[audio_cache_key], format="audio/wav")

    st.markdown("""
    <div style='background: #fff3cd; border-radius: 8px; padding: 12px; margin-top: 20px; border-left: 4px solid #ffc107;'>
        <p style='margin: 0; font-size: 12px; color: #856404;'>
            <strong>Disclaimer:</strong> This analysis is for informational purposes only and should not be considered as financial advice. 
            Always consult a SEBI-registered financial advisor before making investment decisions. Past performance does not guarantee future results.
        </p>
    </div>
    """, unsafe_allow_html=True)
