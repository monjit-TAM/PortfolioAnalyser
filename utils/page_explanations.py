import os
from openai import OpenAI

SUPPORTED_LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "मराठी (Marathi)": "mr",
    "ગુજરાતી (Gujarati)": "gu",
    "বাংলা (Bengali)": "bn",
    "తెలుగు (Telugu)": "te",
    "தமிழ் (Tamil)": "ta",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "ଓଡ଼ିଆ (Odia)": "or",
    "অসমীয়া (Assamese)": "as",
    "اردو (Urdu)": "ur"
}

EXPANDER_LABELS = {
    "en": "Understanding this page",
    "hi": "इस पेज को समझें",
    "mr": "हे पृष्ठ समजून घ्या",
    "gu": "આ પેજ સમજો",
    "bn": "এই পৃষ্ঠা বুঝুন",
    "te": "ఈ పేజీని అర్థం చేసుకోండి",
    "ta": "இந்த பக்கத்தைப் புரிந்துகொள்ளுங்கள்",
    "kn": "ಈ ಪುಟವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ",
    "ml": "ഈ പേജ് മനസ്സിലാക്കുക",
    "pa": "ਇਸ ਪੰਨੇ ਨੂੰ ਸਮਝੋ",
    "or": "ଏହି ପୃଷ୍ଠାକୁ ବୁଝନ୍ତୁ",
    "as": "এই পৃষ্ঠা বুজি লওক",
    "ur": "اس صفحے کو سمجھیں"
}


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
    try:
        return f"{float(val):+.2f}%"
    except:
        return "N/A"


def _safe_get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def _extract_portfolio_context(analysis_results=None, advanced_metrics=None, recommendations=None):
    import pandas as pd

    summary = _safe_get(analysis_results, 'portfolio_summary', default={}) if analysis_results else {}
    stock_perf = _safe_get(analysis_results, 'stock_performance', default=[]) if analysis_results else []
    sector_data = _safe_get(analysis_results, 'sector_analysis', default=[]) if analysis_results else []
    dividend_metrics = _safe_get(analysis_results, 'dividend_metrics', default={}) if analysis_results else {}

    total_inv = summary.get('total_investment', 0)
    current_val = summary.get('current_value', 0)
    total_gl = summary.get('total_gain_loss', 0)
    total_gl_pct = summary.get('total_gain_loss_percentage', 0)
    num_stocks = summary.get('number_of_stocks', 0)
    profitable = summary.get('profitable_stocks', 0)
    loss_making = summary.get('loss_making_stocks', 0)

    top_name = worst_name = "N/A"
    top_return = worst_return = 0

    if stock_perf:
        try:
            perf_df = pd.DataFrame(stock_perf) if not isinstance(stock_perf, pd.DataFrame) else stock_perf
            gl_col = None
            for col_candidate in ['Percentage Gain/Loss', 'Gain/Loss %', 'Percentage_Gain_Loss']:
                if col_candidate in perf_df.columns:
                    gl_col = col_candidate
                    break
            if gl_col:
                perf_df[gl_col] = pd.to_numeric(perf_df[gl_col], errors='coerce').fillna(0)
                top_stock = perf_df.loc[perf_df[gl_col].idxmax()]
                worst_stock = perf_df.loc[perf_df[gl_col].idxmin()]
                top_name = top_stock.get('Stock Name', 'N/A')
                top_return = top_stock.get(gl_col, 0)
                worst_name = worst_stock.get('Stock Name', 'N/A')
                worst_return = worst_stock.get(gl_col, 0)
        except:
            pass

    top_sector_name = "N/A"
    top_sector_pct = 0
    num_sectors = 0
    if sector_data:
        try:
            sec_df = pd.DataFrame(sector_data) if not isinstance(sector_data, pd.DataFrame) else sector_data
            if not sec_df.empty and 'Percentage of Portfolio' in sec_df.columns:
                top_sector = sec_df.loc[sec_df['Percentage of Portfolio'].idxmax()]
                top_sector_name = top_sector.get('Sector', 'N/A')
                top_sector_pct = top_sector.get('Percentage of Portfolio', 0)
                num_sectors = len(sec_df)
        except:
            pass

    profit_or_loss = "profit" if total_gl >= 0 else "loss"
    gain_word = "gained" if total_gl >= 0 else "lost"

    return {
        'total_inv': total_inv, 'current_val': current_val, 'total_gl': total_gl,
        'total_gl_pct': total_gl_pct, 'num_stocks': num_stocks, 'profitable': profitable,
        'loss_making': loss_making, 'top_name': top_name, 'top_return': top_return,
        'worst_name': worst_name, 'worst_return': worst_return, 'top_sector_name': top_sector_name,
        'top_sector_pct': top_sector_pct, 'num_sectors': num_sectors,
        'profit_or_loss': profit_or_loss, 'gain_word': gain_word,
        'sector_data': sector_data, 'dividend_metrics': dividend_metrics,
        'advanced_metrics': advanced_metrics or {}, 'stock_perf': stock_perf,
    }


METRIC_EXPLANATIONS = {}


def _build_all_explanations(ctx):
    import pandas as pd
    c = ctx
    total_inv, current_val, total_gl = c['total_inv'], c['current_val'], c['total_gl']
    total_gl_pct, num_stocks = c['total_gl_pct'], c['num_stocks']
    profitable, loss_making = c['profitable'], c['loss_making']
    top_name, top_return = c['top_name'], c['top_return']
    worst_name, worst_return = c['worst_name'], c['worst_return']
    top_sector_name, top_sector_pct = c['top_sector_name'], c['top_sector_pct']
    num_sectors = c['num_sectors']
    gain_word = c['gain_word']
    adv = c.get('advanced_metrics', {}) or {}
    stock_perf = c.get('stock_perf', []) or []
    win_rate = (profitable / num_stocks * 100) if num_stocks > 0 else 0

    health = _safe_get(adv, 'health_score', default={}) or {}
    health_val = health.get('overall_score', health.get('score', 'N/A')) if isinstance(health, dict) else 'N/A'
    health_grade = health.get('grade', 'N/A') if isinstance(health, dict) else 'N/A'
    health_components = health.get('component_scores', {}) if isinstance(health, dict) else {}
    health_summary = health.get('summary', '') if isinstance(health, dict) else ''
    concentration = _safe_get(adv, 'concentration', default={}) or {}
    top1 = concentration.get('top1_exposure', concentration.get('top1_pct', 0)) if isinstance(concentration, dict) else 0
    top3_exp = concentration.get('top3_exposure', 0) if isinstance(concentration, dict) else 0
    top5_exp = concentration.get('top5_exposure', 0) if isinstance(concentration, dict) else 0
    conc_score = concentration.get('concentration_score', 0) if isinstance(concentration, dict) else 0
    conc_risk_level = concentration.get('risk_level', 'N/A') if isinstance(concentration, dict) else 'N/A'
    single_stock_flags = concentration.get('single_stock_flags', []) if isinstance(concentration, dict) else []
    sector_overexposure = concentration.get('sector_overexposure_flags', []) if isinstance(concentration, dict) else []
    volatility = _safe_get(adv, 'volatility', default={}) or {}
    _sharpe_raw = volatility.get('sharpe_ratio', 0) if isinstance(volatility, dict) else 0
    sharpe = float(_sharpe_raw) if isinstance(_sharpe_raw, (int, float)) else 0.0
    _sortino_raw = volatility.get('sortino_ratio', 0) if isinstance(volatility, dict) else 0
    sortino = float(_sortino_raw) if isinstance(_sortino_raw, (int, float)) else 0.0
    max_dd = float(volatility.get('max_drawdown', 0)) if isinstance(volatility, dict) else 0.0
    hist_vol = float(volatility.get('historical_volatility', 0)) if isinstance(volatility, dict) else 0.0
    port_beta = float(volatility.get('portfolio_beta', 1.0)) if isinstance(volatility, dict) else 1.0
    downside_dev = float(volatility.get('downside_deviation', 0)) if isinstance(volatility, dict) else 0.0
    risk_class = volatility.get('risk_classification', 'N/A') if isinstance(volatility, dict) else 'N/A'
    tax_data = _safe_get(adv, 'tax_impact', default={}) or {}
    stcg_gains = tax_data.get('short_term_gains', 0) if isinstance(tax_data, dict) else 0
    ltcg_gains = tax_data.get('long_term_gains', 0) if isinstance(tax_data, dict) else 0
    stcg_losses = tax_data.get('short_term_losses', 0) if isinstance(tax_data, dict) else 0
    ltcg_losses = tax_data.get('long_term_losses', 0) if isinstance(tax_data, dict) else 0
    est_stcg_tax = tax_data.get('estimated_stcg_tax', 0) if isinstance(tax_data, dict) else 0
    est_ltcg_tax = tax_data.get('estimated_ltcg_tax', 0) if isinstance(tax_data, dict) else 0
    stt_sell = tax_data.get('stt_on_sell', 0) if isinstance(tax_data, dict) else 0
    total_tax_costs = tax_data.get('total_tax_and_costs', 0) if isinstance(tax_data, dict) else 0
    ltcg_exemption_rem = tax_data.get('ltcg_exemption_remaining', 0) if isinstance(tax_data, dict) else 0
    style_data = _safe_get(adv, 'style', default={}) or {}
    structural = _safe_get(adv, 'structural', default={}) or {}
    behavior = _safe_get(adv, 'behavior', default={}) or {}
    drift_data = _safe_get(adv, 'drift', default={}) or {}
    overlap_data = _safe_get(adv, 'overlap', default={}) or {}
    attribution = _safe_get(adv, 'attribution', default={}) or {}
    liquidity_data = _safe_get(adv, 'liquidity', default={}) or {}
    tail_risk_data = _safe_get(adv, 'tail_risk', default={}) or {}
    macro_data = _safe_get(adv, 'macro', default={}) or {}
    scenario_data = _safe_get(adv, 'scenario', default={}) or {}

    perf_list = []
    if stock_perf:
        try:
            perf_df = pd.DataFrame(stock_perf) if not isinstance(stock_perf, pd.DataFrame) else stock_perf
            for _, row in perf_df.iterrows():
                perf_list.append({
                    'name': row.get('Stock Name', 'Unknown'),
                    'buy': row.get('Buy Price', 0),
                    'cur': row.get('Current Price', 0),
                    'qty': row.get('Quantity', 0),
                    'inv': row.get('Investment Value', 0),
                    'curv': row.get('Current Value', 0),
                    'gl': row.get('Absolute Gain/Loss', 0),
                    'gl_pct': row.get('Percentage Gain/Loss', 0),
                    'sector': row.get('Sector', 'N/A'),
                    'category': row.get('Category', 'N/A'),
                    'div_yield': row.get('Dividend Yield', 0),
                    'annual_div': row.get('Annual Dividend', 0),
                })
        except:
            pass
    sorted_by_gl = sorted(perf_list, key=lambda x: float(x.get('gl_pct', 0) or 0), reverse=True)
    top3_stocks = sorted_by_gl[:3] if len(sorted_by_gl) >= 3 else sorted_by_gl
    bottom3_stocks = sorted_by_gl[-3:] if len(sorted_by_gl) >= 3 else sorted_by_gl

    top3_gainers_str = "; ".join([f"{s['name']}: {_pct(s['gl_pct'])} (Invested {_fmt(s['inv'])}, Now {_fmt(s['curv'])}, Gain {_fmt(s['gl'])})" for s in top3_stocks]) if top3_stocks else "N/A"
    bottom3_losers_str = "; ".join([f"{s['name']}: {_pct(s['gl_pct'])} (Invested {_fmt(s['inv'])}, Now {_fmt(s['curv'])}, Loss {_fmt(abs(s['gl']))})" for s in bottom3_stocks]) if bottom3_stocks else "N/A"

    sector_summary_parts = []
    sector_perf_parts = []
    all_sector_parts = []
    best_sector = {'name': 'N/A', 'ret': -999}
    worst_sector = {'name': 'N/A', 'ret': 999}
    if c.get('sector_data'):
        try:
            sec_df = pd.DataFrame(c['sector_data']) if not isinstance(c['sector_data'], pd.DataFrame) else c['sector_data']
            for _, row in sec_df.iterrows():
                sname = row.get('Sector', 'Unknown')
                spct = row.get('Percentage of Portfolio', 0)
                sinv = row.get('Investment Value', 0)
                scur = row.get('Current Value', 0)
                sret = row.get('Sector Return %', 0)
                sgl = row.get('Absolute Gain/Loss', 0)
                all_sector_parts.append(f"{sname}: {spct:.1f}% of portfolio, Invested {_fmt(sinv)}, Current {_fmt(scur)}, Return {_pct(sret)}, P&L {_fmt(sgl)}")
                if sret > best_sector['ret']:
                    best_sector = {'name': sname, 'ret': sret, 'pct': spct, 'gl': sgl}
                if sret < worst_sector['ret']:
                    worst_sector = {'name': sname, 'ret': sret, 'pct': spct, 'gl': sgl}
            for _, row in sec_df.head(3).iterrows():
                sector_summary_parts.append(f"{row.get('Sector', 'Unknown')} ({row.get('Percentage of Portfolio', 0):.1f}%)")
            for _, row in sec_df.iterrows():
                sector_perf_parts.append(f"{row.get('Sector', 'Unknown')}: {_pct(row.get('Sector Return %', 0))}")
        except:
            pass
    top_3_sectors = ", ".join(sector_summary_parts) if sector_summary_parts else "your various sectors"
    all_sectors_str = " | ".join(all_sector_parts) if all_sector_parts else "No sector data available"
    sector_perf_str = " | ".join(sector_perf_parts) if sector_perf_parts else "No sector performance data"

    d = c.get('dividend_metrics', {}) or {}
    div_yield = d.get('portfolio_dividend_yield', 0) or 0
    div_annual = d.get('total_annual_dividend', 0) or 0
    div_stock = d.get('highest_yield_stock', 'N/A')
    div_yield_val = d.get('highest_yield_value', 0) or 0
    div_paying = d.get('dividend_paying_stocks', 0) or 0
    non_div = d.get('non_dividend_stocks', 0) or 0
    stock_dividends = d.get('stock_dividends', []) or []

    div_stock_parts = []
    for sd in stock_dividends[:5]:
        if isinstance(sd, dict):
            div_stock_parts.append(f"{sd.get('stock', 'Unknown')}: Yield {sd.get('yield', 0):.2f}%, Annual ₹{sd.get('annual_dividend', 0):,.0f}")

    sample_stocks_str = ""
    if len(perf_list) >= 2:
        s1, s2 = perf_list[0], perf_list[1]
        sample_stocks_str = f"For example, {s1['name']}: {s1['qty']:.0f} shares × ₹{s1['buy']:,.0f} = {_fmt(s1['inv'])}, and {s2['name']}: {s2['qty']:.0f} shares × ₹{s2['buy']:,.0f} = {_fmt(s2['inv'])}."

    e = {}

    e["dashboard_summary"] = (
        f"Your portfolio of {num_stocks} stocks has a total investment of {_fmt(total_inv)} and is currently valued at {_fmt(current_val)}. "
        f"Calculation: Gain/Loss = Current Value − Investment = {_fmt(current_val)} − {_fmt(total_inv)} = {_fmt(total_gl)} ({_pct(total_gl_pct)}). "
        f"Win Rate: {profitable} out of {num_stocks} stocks are profitable ({win_rate:.1f}% win rate), while {loss_making} are in loss. "
        f"Top performer: {top_name} at {_pct(top_return)}; Worst performer: {worst_name} at {_pct(worst_return)}. "
        f"Your portfolio spans {num_sectors} sectors, led by {top_sector_name} at {top_sector_pct:.1f}% allocation. "
        f"Top 3 gainers: {top3_gainers_str}. "
        f"Portfolio Health Score: {health_val}/100 (Grade {health_grade})."
    )
    e["portfolio_health_score"] = (
        f"Your portfolio health score is {health_val}/100 (Grade {health_grade}). "
        f"The score is computed using a weighted formula: Score = Diversification(25%) + Risk(25%) + Liquidity(20%) + Behavior(15%) + Style Balance(15%). "
        f"Component breakdown — Diversification: {health_components.get('diversification', 'N/A')}/100, Risk: {health_components.get('risk', 'N/A')}/100, "
        f"Liquidity: {health_components.get('liquidity', 'N/A')}/100, Behavior: {health_components.get('behavior', 'N/A')}/100, Style Balance: {health_components.get('style_balance', 'N/A')}/100. "
        f"Weighted Score = ({health_components.get('diversification', 0)}×0.25) + ({health_components.get('risk', 0)}×0.25) + ({health_components.get('liquidity', 0)}×0.20) + ({health_components.get('behavior', 0)}×0.15) + ({health_components.get('style_balance', 0)}×0.15) = {health_val}. "
        f"{health_summary} "
        f"A score above 75 means your portfolio is healthy and well-structured; 50-75 means room for improvement; below 50 needs significant attention."
    )
    e["total_investment"] = (
        f"Your total investment (cost basis) across all {num_stocks} stocks is {_fmt(total_inv)}. "
        f"This is the sum of (Quantity × Buy Price) for each stock in your portfolio. "
        f"{sample_stocks_str} "
        f"This number represents your starting point — it only changes when you buy or sell stocks, not with daily market movements. "
        f"Your average investment per stock is approximately {_fmt(total_inv / num_stocks if num_stocks > 0 else 0)}."
    )
    e["current_value"] = (
        f"Your {num_stocks} stocks are currently worth {_fmt(current_val)} at today's market prices. "
        f"Calculation: Difference = {_fmt(current_val)} − {_fmt(total_inv)} = {_fmt(total_gl)} ({_pct(total_gl_pct)}). "
        + (f"You are sitting on an unrealized profit of {_fmt(abs(total_gl))}. If you sold everything today, you would receive approximately {_fmt(current_val)} before taxes and brokerage charges (estimated tax + costs: {_fmt(total_tax_costs)})."
           if current_val >= total_inv else
           f"You are currently at an unrealized loss of {_fmt(abs(total_gl))}. This loss is only 'on paper' — you haven't actually lost money until you sell. Markets recover over time; evaluate each stock's fundamentals before deciding.")
    )
    e["total_gain_loss"] = (
        f"Total P&L = Current Value − Investment = {_fmt(current_val)} − {_fmt(total_inv)} = {_fmt(total_gl)} ({_pct(total_gl_pct)}). "
        f"Top 3 gainers: {top3_gainers_str}. "
        f"Bottom 3 performers: {bottom3_losers_str}. "
        f"Out of {num_stocks} stocks, {profitable} are in profit and {loss_making} are in loss (win rate: {win_rate:.1f}%). "
        + (f"Tax note: STCG gains of {_fmt(stcg_gains)} taxed at 20%, LTCG gains of {_fmt(ltcg_gains)} taxed at 12.5% above ₹1.25L exemption. Losses ({_fmt(stcg_losses + ltcg_losses)}) can be set off against gains."
           if total_gl > 0 else
           f"Tax benefit: Your losses of {_fmt(abs(total_gl))} can be set off against any capital gains to reduce tax liability.")
    )
    e["return_percentage"] = (
        f"Your portfolio return is {_pct(total_gl_pct)}. Calculation: Return = (Current Value − Investment) / Investment × 100 = ({_fmt(current_val)} − {_fmt(total_inv)}) / {_fmt(total_inv)} × 100 = {_pct(total_gl_pct)}. "
        f"Benchmark comparison: Bank FD ~7%/year, Nifty 50 index ~12-14%/year historically. "
        + (f"Your portfolio is {'outperforming the Nifty 50 benchmark — excellent stock selection' if total_gl_pct > 14 else 'performing in line with the market average' if total_gl_pct > 7 else 'underperforming compared to a simple Nifty 50 index fund — consider reviewing your stock picks'}. "
           if total_gl_pct != 0 else "")
        + f"Context matters: a {_pct(total_gl_pct)} return in 6 months is {'excellent' if total_gl_pct > 10 else 'good' if total_gl_pct > 5 else 'modest'}, but over 3 years would be {'below average' if total_gl_pct < 20 else 'reasonable'}."
    )
    e["stock_performance_table"] = (
        f"This table details all {num_stocks} stocks: Buy Price, Current Price, Quantity, Investment Value, Current Value, Absolute Gain/Loss, and Percentage Gain/Loss. "
        f"Currently {profitable} stocks are in profit (green) and {loss_making} are in loss (red). "
        f"Your best pick: {top_name} bought at ₹{top3_stocks[0]['buy']:,.0f}, now ₹{top3_stocks[0]['cur']:,.0f}, returning {_pct(top_return)} on {_fmt(top3_stocks[0]['inv'])} invested. " if top3_stocks else ""
        f"Your worst pick: {worst_name} at {_pct(worst_return)} — evaluate if fundamentals support holding or if cutting losses is prudent. "
        f"Average return per stock: {_pct(total_gl_pct)}. Stocks performing below this average are relative underperformers in your portfolio."
    )
    e["dividend_yield"] = (
        f"Your portfolio's dividend yield is {div_yield:.2f}%, generating approximately {_fmt(div_annual)} per year in passive income. "
        f"Calculation: Dividend Yield = Total Annual Dividends / Current Portfolio Value × 100 = {_fmt(div_annual)} / {_fmt(current_val)} × 100 = {div_yield:.2f}%. "
        f"{div_paying} out of {num_stocks} stocks pay dividends; {non_div} stocks pay no dividends. "
        f"Highest yielding stock: {div_stock} at {div_yield_val:.2f}% yield. "
        + (f"Per-stock dividends: {'; '.join(div_stock_parts)}. " if div_stock_parts else "")
        + f"A good dividend yield for Indian stocks is 1-3%; above 3% is high yield. Your {div_yield:.2f}% yield {'exceeds' if div_yield > 3 else 'is within' if div_yield > 1 else 'is below'} the typical range."
    )

    e["sector_allocation_pie"] = (
        f"Your portfolio spans {num_sectors} sectors. Full sector breakdown: {all_sectors_str}. "
        f"Your largest allocation is {top_sector_name} at {top_sector_pct:.1f}% of your portfolio. Top 3 sectors: {top_3_sectors}. "
        + (f"WARNING: {top_sector_name} at {top_sector_pct:.1f}% exceeds the recommended 25-30% maximum. A 20% drop in {top_sector_name} would drag your portfolio down by ~{top_sector_pct * 0.2:.1f}%. Consider diversifying into other sectors."
           if top_sector_pct > 30 else
           f"Your sector allocation is well-distributed — no single sector dominates beyond 30%, providing good protection against sector-specific risks.")
    )
    e["sector_performance"] = (
        f"Sector-wise returns for your {num_sectors} sectors: {sector_perf_str}. "
        f"Best performing sector: {best_sector.get('name', 'N/A')} at {_pct(best_sector.get('ret', 0))} (P&L: {_fmt(best_sector.get('gl', 0))}). "
        f"Worst performing sector: {worst_sector.get('name', 'N/A')} at {_pct(worst_sector.get('ret', 0))} (P&L: {_fmt(worst_sector.get('gl', 0))}). "
        f"If an entire sector is underperforming, it's typically a market-wide issue. If only your stock in a sector lags while peers do well, review your specific pick. "
        f"Compare your sector returns with sectoral indices (Nifty IT, Nifty Bank, Nifty Pharma) to check if you're beating or trailing the sector average."
    )
    e["sector_insights"] = (
        f"Best sector: {best_sector.get('name', 'N/A')} returning {_pct(best_sector.get('ret', 0))} with {best_sector.get('pct', 0):.1f}% allocation. "
        f"Worst sector: {worst_sector.get('name', 'N/A')} returning {_pct(worst_sector.get('ret', 0))} with {worst_sector.get('pct', 0):.1f}% allocation. "
        f"Highest allocation: {top_sector_name} at {top_sector_pct:.1f}%. "
        + (f"Red flag: Your worst sector ({worst_sector.get('name', 'N/A')}) has a high allocation — consider reducing exposure. " if worst_sector.get('pct', 0) > 20 else "")
        + (f"Opportunity: Your best sector ({best_sector.get('name', 'N/A')}) has only {best_sector.get('pct', 0):.1f}% allocation — consider increasing it for better returns." if best_sector.get('pct', 0) < 15 else "")
    )
    hhi = sum([(float(s.get('Percentage of Portfolio', 0)) ** 2) for s in (c.get('sector_data') or [])]) if c.get('sector_data') else 0
    e["diversification_analysis"] = (
        f"Your portfolio has {num_stocks} stocks across {num_sectors} sectors. Concentration metric (HHI-like): sum of squared sector weights = {hhi:.0f} (lower is better; below 1500 = well-diversified, 1500-2500 = moderate, above 2500 = concentrated). "
        f"Largest sector: {top_sector_name} at {top_sector_pct:.1f}%. If {top_sector_name} drops 20%, your portfolio would lose approximately {top_sector_pct * 0.2:.1f}%. "
        f"Diversification rating: {'Excellent (8+ sectors, no sector above 25%)' if num_sectors >= 8 and top_sector_pct <= 25 else 'Good (5-7 sectors)' if num_sectors >= 5 else 'Needs improvement (fewer than 5 sectors)'}. "
        f"Top 3 sectors account for {sum([float(s.get('Percentage of Portfolio', 0)) for s in (c.get('sector_data') or [])[:3]]):.1f}% of your portfolio."
    )
    e["sector_recommendations"] = (
        f"Based on your sector allocation across {num_sectors} sectors: "
        + (f"TRIM: {top_sector_name} is overweight at {top_sector_pct:.1f}% (recommended max 25-30%) — consider reducing by {top_sector_pct - 25:.1f}% to bring it in line. " if top_sector_pct > 25 else f"Your top sector {top_sector_name} at {top_sector_pct:.1f}% is within acceptable limits. ")
        + (f"REVIEW: {worst_sector.get('name', 'N/A')} is your worst performer at {_pct(worst_sector.get('ret', 0))} — evaluate if the stocks in this sector have recovery potential. " if worst_sector.get('ret', 0) < -5 else "")
        + (f"INCREASE: {best_sector.get('name', 'N/A')} is your best performer at {_pct(best_sector.get('ret', 0))} but only {best_sector.get('pct', 0):.1f}% of portfolio — consider adding exposure." if best_sector.get('pct', 0) < 15 else "")
    )

    e["stock_wise_returns"] = (
        f"Individual stock returns across your {num_stocks} holdings: "
        f"Top 3: {top3_gainers_str}. "
        f"Bottom 3: {bottom3_losers_str}. "
        f"Your best stock {top_name} returned {_pct(top_return)} — for every ₹100 invested, it's now worth ₹{100 + float(top_return) if isinstance(top_return, (int, float)) else 100:.0f}. "
        f"Your worst stock {worst_name} is at {_pct(worst_return)}. "
        f"Win rate: {profitable}/{num_stocks} = {win_rate:.1f}%. Stocks down >20% with deteriorating fundamentals are candidates for exit."
    )
    e["price_chart"] = (
        f"Price charts track each stock's journey from buy price to current price. "
        + (f"For example, {top_name} was bought at ₹{top3_stocks[0]['buy']:,.0f} and is now at ₹{top3_stocks[0]['cur']:,.0f} ({_pct(top3_stocks[0]['gl_pct'])}), showing {'an upward' if top3_stocks[0]['gl_pct'] > 0 else 'a downward'} trend. " if top3_stocks else "")
        + (f"Meanwhile, {worst_name} moved from ₹{bottom3_stocks[-1]['buy']:,.0f} to ₹{bottom3_stocks[-1]['cur']:,.0f} ({_pct(bottom3_stocks[-1]['gl_pct'])}). " if bottom3_stocks else "")
        + f"Look for steady upward trends (consistent growth) vs sharp spikes (speculative) vs gradual declines (review fundamentals). "
        f"Flat lines indicate capital stuck without movement — consider redeploying to better opportunities."
    )
    inv_vs_cur_parts = []
    for s in sorted_by_gl[:3]:
        inv_vs_cur_parts.append(f"{s['name']}: Invested {_fmt(s['inv'])} → Now {_fmt(s['curv'])} ({_pct(s['gl_pct'])})")
    e["investment_vs_current"] = (
        f"Investment vs Current Value comparison for your portfolio: Total Invested {_fmt(total_inv)} → Current {_fmt(current_val)} (P&L: {_fmt(total_gl)}). "
        f"Top performing stocks: {'; '.join(inv_vs_cur_parts) if inv_vs_cur_parts else 'N/A'}. "
        f"Green bars indicate stocks in profit; red bars indicate loss. The wider the gap between green current-value bars and investment bars, the more profitable the stock. "
        f"Stocks with large red gaps are dragging your portfolio — evaluate recovery potential for each."
    )

    nifty_benchmark = 13.0
    alpha_val = float(total_gl_pct) - nifty_benchmark if isinstance(total_gl_pct, (int, float)) else 0
    e["portfolio_vs_nifty"] = (
        f"Your portfolio returned {_pct(total_gl_pct)} vs Nifty 50 historical average of ~13%/year. "
        f"Alpha (excess return) = Portfolio Return − Benchmark = {_pct(total_gl_pct)} − +13.00% = {_pct(alpha_val)}. "
        + (f"Your portfolio is outperforming Nifty 50 by {_pct(abs(alpha_val))} — your stock selection is adding value beyond what a passive index fund would deliver. " if alpha_val > 0 else
           f"Your portfolio trails Nifty 50 by {_pct(abs(alpha_val))} — a simple Nifty 50 index fund (like UTI Nifty ETF or Nippon India Nifty 50 BeES) would have delivered better returns with less effort. ")
        + f"Most professional fund managers struggle to beat Nifty consistently, so {'beating it is impressive' if alpha_val > 0 else 'underperformance is common but worth addressing'}."
    )
    e["portfolio_vs_sensex"] = (
        f"Sensex (BSE 30) comparison: Your portfolio at {_pct(total_gl_pct)} vs Sensex historical ~12-13%/year. "
        f"Sensex tracks top 30 BSE companies and moves similarly to Nifty but is narrower. "
        + (f"With {num_stocks} stocks and {num_sectors} sectors, your portfolio has {'broader diversification than Sensex' if num_stocks > 30 else 'narrower coverage than even the Sensex'}. " if num_stocks > 0 else "")
        + f"If your portfolio consistently underperforms both Nifty and Sensex, shifting a portion to index funds (e.g., 50% index + 50% active picks) could improve risk-adjusted returns."
    )
    e["alpha"] = (
        f"Alpha = Portfolio Return − Benchmark Return = {_pct(total_gl_pct)} − +13.00% (Nifty 50 avg) = {_pct(alpha_val)}. "
        + (f"Positive Alpha of {_pct(alpha_val)} means your stock-picking skill is generating {_pct(abs(alpha_val))} extra return above what the market offers. This is genuinely valuable — most professional fund managers fail to generate consistent positive alpha. " if alpha_val > 0 else
           f"Negative Alpha of {_pct(alpha_val)} means you would have earned {_pct(abs(alpha_val))} more by simply buying a Nifty 50 index fund. Consider reviewing your stock selection strategy or allocating a portion to passive index investing. ")
        + f"Alpha is the truest measure of your investing skill — it strips away the market tailwind and shows only the value your decisions add."
    )
    e["beta"] = (
        f"Your portfolio Beta is {port_beta:.2f}. Beta measures sensitivity to market movements relative to Nifty 50. "
        f"With Beta = {port_beta:.2f}: If Nifty moves +10%, your portfolio is expected to move {port_beta * 10:+.1f}%. If Nifty drops -10%, you'd expect {port_beta * -10:+.1f}%. "
        + (f"Your Beta > 1.0 indicates an aggressive portfolio — higher gains in bull markets but steeper losses in downturns. " if port_beta > 1.0 else
           f"Your Beta < 1.0 indicates a defensive portfolio — more stable but may lag in strong bull markets. " if port_beta < 1.0 else
           f"Beta of ~1.0 means your portfolio tracks the market closely. ")
        + f"Risk classification: {risk_class}. Historical volatility: {hist_vol:.1f}%. For conservative goals (2-3 years), target Beta < 0.8; for long-term growth, Beta 0.8-1.2 is typical."
    )

    e["value_analysis"] = (
        f"Value Analysis evaluates each of your {num_stocks} stocks on P/E ratio (price-to-earnings), P/B ratio (price-to-book), and dividend yield to determine if they're undervalued or overvalued. "
        + (f"For context, {top_name} with {_pct(top_return)} return may be approaching overvaluation if its P/E exceeds sector average. {worst_name} at {_pct(worst_return)} could be a value trap or a genuine bargain depending on fundamentals. " if top_name != 'N/A' else "")
        + f"Stocks with P/E below 15 and P/B below 2 in large-cap space are typically considered value picks. Stocks with P/E above 40 are priced for high growth expectations. "
        f"Your portfolio's dividend yield of {div_yield:.2f}% adds a value dimension — higher-yielding stocks tend to have a margin of safety."
    )
    e["growth_analysis"] = (
        f"Growth Analysis examines revenue growth, profit growth, ROE (return on equity), and market expansion for your {num_stocks} stocks. "
        f"Companies growing revenue at 15-20%+ annually are classified as growth stocks. Your portfolio has {profitable} stocks in profit — these likely include growth winners. "
        f"A company growing at 20% annually doubles in ~3.6 years (Rule of 72: 72/20 = 3.6 years). "
        f"Your best performer {top_name} at {_pct(top_return)} demonstrates strong growth execution. "
        f"Balance growth with valuations — overpaying for growth (P/E > 50-60) increases downside risk if growth slows."
    )
    e["buy_hold_sell"] = (
        f"Each of your {num_stocks} stocks gets a BUY/HOLD/SELL rating based on combined Value + Growth scores. "
        f"BUY = Stock is attractively valued with good growth — consider adding. HOLD = Fairly valued, no action needed. SELL = Overvalued or fundamentally weak — consider exiting. "
        f"Key stocks to watch: {worst_name} at {_pct(worst_return)} — if rated SELL, the data supports cutting losses and redeploying the {_fmt(abs(bottom3_stocks[-1]['gl'])) if bottom3_stocks else 'invested capital'} elsewhere. "
        f"{top_name} at {_pct(top_return)} — if it now exceeds {top1:.1f}% of portfolio, consider partial profit booking to manage concentration risk. "
        f"These are algorithmic recommendations — always cross-check with your investment horizon and risk appetite."
    )
    e["alternative_suggestions"] = (
        f"For SELL-rated stocks, we suggest stronger alternatives within the same sector to maintain your allocation balance. "
        + (f"For instance, if {worst_name} (in {bottom3_stocks[-1]['sector'] if bottom3_stocks else 'N/A'} sector) gets a SELL rating at {_pct(worst_return)}, "
           f"we suggest better-performing or better-valued peers in the same sector. " if bottom3_stocks else "")
        + f"This approach lets you redeploy capital more effectively — selling a weak stock and buying a stronger one in the same industry maintains your sector exposure while improving quality. "
        f"Your current investment of {_fmt(abs(bottom3_stocks[-1]['inv'])) if bottom3_stocks else _fmt(0)} in the weakest stock could work harder in a better-quality alternative. "
        f"Always conduct your own research before acting on replacement suggestions."
    )

    flagged_stocks_str = ", ".join([f"{f['stock']} ({f['percentage']:.1f}%)" for f in single_stock_flags]) if single_stock_flags else "None"
    e["overweight_positions"] = (
        f"Concentration analysis: Top 1 stock = {top1:.1f}% of portfolio, Top 3 = {top3_exp:.1f}%, Top 5 = {top5_exp:.1f}%. "
        f"Stocks exceeding 15% threshold (flagged): {flagged_stocks_str}. "
        + (f"Your largest holding at {top1:.1f}% is too concentrated — if this stock drops 30%, your entire portfolio would lose ~{top1 * 0.3:.1f}%. "
           f"Consider trimming overweight positions and redistributing to underweight stocks or new opportunities. "
           if top1 > 15 else f"No single stock exceeds the 15% concentration threshold — good diversification at the stock level. ")
        + f"Ideal target: no single stock above 10-15% of your {_fmt(current_val)} portfolio."
    )
    drift_sectors = drift_data.get('sector_drifts', []) if isinstance(drift_data, dict) else []
    alignment = drift_data.get('alignment_score', 0) if isinstance(drift_data, dict) else 0
    dev_level = drift_data.get('deviation_level', 'N/A') if isinstance(drift_data, dict) else 'N/A'
    underweight_parts = [f"{d['sector']}: Your {d.get('portfolio_pct', 0):.1f}% vs Benchmark {d.get('benchmark_pct', 0)}% (drift: {d.get('drift', 0):+.1f}%)" for d in drift_sectors if d.get('drift', 0) < 0]
    overweight_drift_parts = [f"{d['sector']}: Your {d.get('portfolio_pct', 0):.1f}% vs Benchmark {d.get('benchmark_pct', 0)}% (drift: {d.get('drift', 0):+.1f}%)" for d in drift_sectors if d.get('drift', 0) > 0]
    e["underweight_positions"] = (
        f"Benchmark alignment score: {alignment:.1f}/100 (Deviation: {dev_level}). "
        f"Underweight sectors vs Nifty 50 benchmark: {'; '.join(underweight_parts) if underweight_parts else 'None — your allocation aligns well with the benchmark'}. "
        f"Overweight sectors: {'; '.join(overweight_drift_parts) if overweight_drift_parts else 'None'}. "
        f"Adding to underweight sectors improves balance and reduces tracking error vs the broader market. "
        f"A well-balanced portfolio typically has exposure to 5-8 sectors, and your {num_sectors} sectors {'meet' if num_sectors >= 5 else 'fall short of'} this target."
    )
    sector_flags_str = ", ".join([f"{f['sector']} ({f['percentage']:.1f}%)" for f in sector_overexposure]) if sector_overexposure else "None"
    e["concentration_alerts"] = (
        f"Concentration Score: {conc_score}/100 (Risk Level: {conc_risk_level}). "
        f"Single stock flags (>15% of portfolio): {flagged_stocks_str}. "
        f"Sector overexposure flags (>30% of portfolio): {sector_flags_str}. "
        f"Top 1/3/5 concentration: {top1:.1f}% / {top3_exp:.1f}% / {top5_exp:.1f}%. Thresholds: Single stock <15%, Top 3 <40%, Top 5 <60%. "
        + (f"ALERT: Your concentration risk is {conc_risk_level} — rebalancing is recommended to reduce single-stock and sector exposure." if conc_risk_level in ['High', 'Medium'] else
           f"Your concentration levels are within safe limits — continue monitoring quarterly.")
    )
    e["rebalancing_strategy"] = (
        f"Based on your portfolio's drift (alignment score: {alignment:.1f}/100) and concentration (score: {conc_score}/100, risk: {conc_risk_level}): "
        + (f"Priority 1: Trim overweight stocks — {flagged_stocks_str} exceed the 15% single-stock limit. " if single_stock_flags else "")
        + (f"Priority 2: Address sector drift — {'; '.join(overweight_drift_parts[:2])} are overweight vs Nifty 50 benchmark. " if overweight_drift_parts else "")
        + (f"Priority 3: Add to underweight sectors — {'; '.join(underweight_parts[:2])}. " if underweight_parts else "")
        + f"Rebalance quarterly or when any position drifts >5% from target. Systematic rebalancing forces 'sell high, buy low' discipline and can improve long-term risk-adjusted returns by 0.5-1% annually."
    )

    e["portfolio_value_over_time"] = (
        f"Your portfolio's journey: Starting investment of {_fmt(total_inv)} → current value of {_fmt(current_val)}, a change of {_fmt(total_gl)} ({_pct(total_gl_pct)}). "
        f"The blue line tracks your portfolio's daily market value; the gray dashed line shows your cost basis of {_fmt(total_inv)}. "
        f"When blue > gray, you're in profit. Your portfolio has {gain_word} {_fmt(abs(total_gl))} from the starting point. "
        f"Maximum drawdown during this period was {max_dd:.1f}% — meaning at the worst point, your portfolio dropped {max_dd:.1f}% from its peak. "
        f"Despite drawdowns, the overall trajectory shows a {_pct(total_gl_pct)} cumulative return."
    )
    e["cumulative_returns"] = (
        f"Cumulative return = (Current Value − Investment) / Investment × 100 = ({_fmt(current_val)} − {_fmt(total_inv)}) / {_fmt(total_inv)} × 100 = {_pct(total_gl_pct)}. "
        f"This chart shows how this return built up over time — green periods indicate positive accumulation, red indicates losses eating into gains. "
        f"Your win rate of {win_rate:.1f}% ({profitable} winners out of {num_stocks}) contributes to the cumulative trajectory. "
        f"Steady, gradual growth is healthier than volatile swings — even if the end result is the same, smoother returns reduce the chance of panic-selling during dips."
    )
    e["drawdown_analysis"] = (
        f"Maximum drawdown: {max_dd:.1f}%. This means at the worst point, your portfolio fell {max_dd:.1f}% from its peak value. "
        f"Calculation: Drawdown = (Trough − Peak) / Peak × 100. For your portfolio with peak near {_fmt(current_val * 100 / (100 - max_dd)) if max_dd < 100 else _fmt(current_val)}, "
        f"the trough represented a loss of approximately {_fmt(current_val * max_dd / (100 - max_dd)) if max_dd < 100 else 'N/A'} from peak. "
        f"Context: A 10% drawdown is normal; 20% is uncomfortable; >30% is severe. Your {max_dd:.1f}% drawdown is {'within normal range' if max_dd < 15 else 'moderate — manageable for long-term investors' if max_dd < 25 else 'significant — ensure you have the emotional resilience to hold through such drops'}. "
        f"Downside deviation: {downside_dev:.2f}%. Lower drawdowns mean your portfolio is easier to hold through market stress."
    )
    e["period_wise_returns"] = (
        f"Period-wise return breakdown shows your portfolio's performance across daily, weekly, and monthly intervals. "
        f"Your overall win rate is {win_rate:.1f}% ({profitable}/{num_stocks} stocks profitable). A win rate above 55% is strong for equity portfolios. "
        f"Portfolio return: {_pct(total_gl_pct)} total. If achieved over 12 months, that's approximately {total_gl_pct / 12:.2f}% per month. "
        f"Context: Average monthly return of 1-2% translates to 12-24% annually — which is excellent for equity investing. "
        f"Track the consistency of returns: steady small gains beat occasional large swings for sustainable wealth building."
    )
    e["performance_summary"] = (
        f"Key performance metrics: Total Return: {_pct(total_gl_pct)} ({_fmt(total_gl)}), Portfolio Value: {_fmt(current_val)}, Investment: {_fmt(total_inv)}. "
        f"Sharpe Ratio: {sharpe} (risk-adjusted return; >1.0 is good, >2.0 is excellent). Sortino Ratio: {sortino} (focuses on downside risk only). "
        f"Max Drawdown: {max_dd:.1f}%, Historical Volatility: {hist_vol:.1f}%, Beta: {port_beta:.2f}. "
        f"Risk Classification: {risk_class}. Win Rate: {win_rate:.1f}% ({profitable} profitable, {loss_making} in loss). "
        f"The ideal combination is high Sharpe (>1.0) with low drawdown (<15%) — meaning steady growth without dramatic swings."
    )
    e["performance_insights"] = (
        f"Data-driven insights: Your {_pct(total_gl_pct)} return with {max_dd:.1f}% max drawdown gives a return/drawdown ratio of {abs(total_gl_pct / max_dd):.2f}x (>1.0 is desirable). " if max_dd > 0 else
        f"Data-driven insights: Your {_pct(total_gl_pct)} return with minimal drawdown indicates strong risk-adjusted performance. "
        f"Portfolio volatility of {hist_vol:.1f}% {'is elevated — expect larger daily swings' if hist_vol > 25 else 'is moderate — typical for a diversified equity portfolio' if hist_vol > 15 else 'is low — your portfolio is relatively stable'}. "
        f"Win rate of {win_rate:.1f}% with {profitable} winners and {loss_making} losers {'shows strong stock selection' if win_rate > 60 else 'is typical for equity portfolios' if win_rate > 45 else 'indicates room for improvement in stock selection'}. "
        f"Sharpe Ratio of {sharpe} {'indicates excellent risk-adjusted returns' if isinstance(sharpe, (int, float)) and sharpe > 1.0 else 'suggests room to improve your risk-return tradeoff' if isinstance(sharpe, (int, float)) else 'could not be computed due to insufficient data'}."
    )

    mcap = structural.get('market_cap_allocation', {}) if isinstance(structural, dict) else {}
    large_pct = mcap.get('Large Cap', 0)
    mid_pct = mcap.get('Mid Cap', 0)
    small_pct = mcap.get('Small Cap', 0)
    style_label = style_data.get('style_label', 'Blend') if isinstance(style_data, dict) else 'Blend'
    thematic = structural.get('thematic_clusters', []) if isinstance(structural, dict) else []
    e["investor_type"] = (
        f"Based on your portfolio composition: Market Cap split — Large Cap: {large_pct:.1f}%, Mid Cap: {mid_pct:.1f}%, Small Cap: {small_pct:.1f}%. "
        f"Investment Style: {style_label}. Thematic clusters detected: {', '.join(thematic) if thematic else 'Diversified'}. "
        + (f"Your profile is Conservative (>60% Large Cap) — prioritizing stability and established companies. " if large_pct > 60 else
           f"Your profile is Aggressive (>40% Mid/Small Cap) — pursuing higher growth with elevated risk. " if (mid_pct + small_pct) > 40 else
           f"Your profile is Moderate — balanced mix across market caps. ")
        + f"With {num_stocks} stocks across {num_sectors} sectors and a {_pct(total_gl_pct)} return, your portfolio aligns with a {style_label.lower()} investing approach."
    )
    e["risk_tolerance"] = (
        f"Risk Classification: {risk_class}. Portfolio Beta: {port_beta:.2f} (market sensitivity). Historical Volatility: {hist_vol:.1f}%. "
        f"With Beta = {port_beta:.2f}, a 10% Nifty move translates to approximately {port_beta * 10:.1f}% move in your portfolio. "
        f"Max Drawdown experienced: {max_dd:.1f}% — this is the worst-case scenario you've already lived through. "
        + (f"Your high-risk profile suits long-term goals (10+ years). For shorter goals (2-3 years), consider shifting 20-30% to debt/FD. " if risk_class == 'High Risk' else
           f"Your moderate risk profile is suitable for medium-term goals (3-5 years). " if risk_class == 'Moderate Risk' else
           f"Your low-risk profile suits conservative goals. You can afford slightly more equity exposure for better long-term returns. ")
        + f"Downside deviation: {downside_dev:.2f}% — measures only negative volatility, a better risk indicator than total volatility."
    )
    avg_hold = behavior.get('average_holding_days', 0) if isinstance(behavior, dict) else 0
    hold_dist = behavior.get('holding_distribution', {}) if isinstance(behavior, dict) else {}
    beh_pattern = behavior.get('behavior_pattern', 'N/A') if isinstance(behavior, dict) else 'N/A'
    e["holding_period"] = (
        f"Average holding period: {avg_hold:.0f} days. Behavior pattern: {beh_pattern}. "
        f"Holding distribution: <3 months: {hold_dist.get('<3 months', 0)} stocks, 3-12 months: {hold_dist.get('3-12 months', 0)} stocks, >12 months: {hold_dist.get('>12 months', 0)} stocks. "
        + (f"With {avg_hold:.0f} days average holding, most of your positions are short-term — attracting 20% STCG tax on profits. " if avg_hold < 365 else
           f"With {avg_hold:.0f} days average holding, most positions qualify for LTCG tax (12.5% above ₹1.25L exemption), saving 7.5% vs STCG rate. ")
        + f"Tax impact: Short-term gains of {_fmt(stcg_gains)} taxed at 20% = {_fmt(est_stcg_tax)}; Long-term gains of {_fmt(ltcg_gains)} taxed at 12.5% (above ₹1.25L) = {_fmt(est_ltcg_tax)}. "
        f"Historically, longer holding periods produce better returns: Indian equity has never given negative returns over any 15-year period."
    )
    short_term_h = behavior.get('short_term_holdings', 0) if isinstance(behavior, dict) else 0
    long_term_h = behavior.get('long_term_holdings', 0) if isinstance(behavior, dict) else 0
    overtrade = behavior.get('overtrading_detected', False) if isinstance(behavior, dict) else False
    beh_score = behavior.get('behavior_score', 0) if isinstance(behavior, dict) else 0
    e["behavioral_analysis"] = (
        f"Behavior Score: {beh_score}/100. Pattern: {beh_pattern}. Overtrading detected: {'Yes — you are churning positions too frequently' if overtrade else 'No — trading frequency is normal'}. "
        f"Short-term holdings (<90 days): {short_term_h} stocks. Long-term holdings (>365 days): {long_term_h} stocks. "
        f"With {profitable} winning and {loss_making} losing stocks, watch for: Loss Aversion (holding losers too long hoping for recovery), "
        f"Disposition Effect (selling winners too early while keeping losers), and Overconfidence (concentrated bets on {top1:.1f}% top holding). "
        + (f"Your high churn rate increases transaction costs and tax liability — consider adopting a buy-and-hold approach. " if overtrade else
           f"Your holding behavior is disciplined — maintain this approach for better long-term outcomes. ")
    )

    e["health_score"] = (
        f"Portfolio Health Score: {health_val}/100 (Grade {health_grade}). "
        f"Formula: Score = Diversification({health_components.get('diversification', 0)}) × 25% + Risk({health_components.get('risk', 0)}) × 25% + Liquidity({health_components.get('liquidity', 0)}) × 20% + Behavior({health_components.get('behavior', 0)}) × 15% + Style({health_components.get('style_balance', 0)}) × 15%. "
        f"Calculation: ({health_components.get('diversification', 0)} × 0.25) + ({health_components.get('risk', 0)} × 0.25) + ({health_components.get('liquidity', 0)} × 0.20) + ({health_components.get('behavior', 0)} × 0.15) + ({health_components.get('style_balance', 0)} × 0.15) = {health_val}. "
        + (f"Grade A (≥80): Your portfolio is well-structured and healthy. " if health_grade == 'A' else
           f"Grade B (65-79): Good portfolio with room for improvement in {'risk management' if health_components.get('risk', 100) < 65 else 'diversification' if health_components.get('diversification', 100) < 65 else 'behavioral discipline'}. " if health_grade == 'B' else
           f"Grade C/D: Significant improvement needed. Focus on the lowest component score first. ")
        + f"{health_summary}"
    )
    e["risk_radar"] = (
        f"Risk radar displays 8 dimensions of portfolio risk with actual values: "
        f"1) Concentration Risk: score {conc_score}/100 (top stock: {top1:.1f}%). "
        f"2) Volatility: {hist_vol:.1f}% annualized. "
        f"3) Max Drawdown: {max_dd:.1f}%. "
        f"4) Sector Risk: top sector {top_sector_name} at {top_sector_pct:.1f}%. "
        f"5) Liquidity Risk: {liquidity_data.get('liquidity_risk', 'N/A')} (score: {liquidity_data.get('portfolio_liquidity_score', 'N/A')}/100). "
        f"6) Tail Risk: {tail_risk_data.get('tail_risk_level', 'N/A')} (score: {tail_risk_data.get('tail_risk_score', 'N/A')}/100). "
        f"7) Beta Risk: {port_beta:.2f} (market sensitivity). "
        f"8) Behavioral Risk: score {beh_score}/100 ({'overtrading detected' if overtrade else 'normal trading pattern'}). "
        f"Focus on spokes extending furthest — those represent your biggest vulnerabilities."
    )
    ind_conc = structural.get('industry_concentration', {}) if isinstance(structural, dict) else {}
    sec_alloc = structural.get('sector_allocation', {}) if isinstance(structural, dict) else {}
    e["structural_diagnostics"] = (
        f"Market Cap breakdown of your {_fmt(current_val)} portfolio: Large Cap: {large_pct:.1f}%, Mid Cap: {mid_pct:.1f}%, Small Cap: {small_pct:.1f}%. "
        f"Sector allocation: {', '.join([f'{k}: {v:.1f}%' for k, v in sec_alloc.items()][:5]) if sec_alloc else 'N/A'}. "
        f"Industry concentration: Top sector {ind_conc.get('top_sector', 'N/A')} at {ind_conc.get('top_sector_pct', 0):.1f}% {'(CONCENTRATED — above 30%)' if ind_conc.get('is_concentrated', False) else '(within limits)'}. "
        f"Thematic clusters: {', '.join(thematic) if thematic else 'Diversified — no single theme dominates'}. "
        f"Recommended balance for moderate investors: 50-60% Large Cap, 20-30% Mid Cap, 10-20% Small Cap. Your {large_pct:.1f}% Large Cap is {'above' if large_pct > 60 else 'within' if large_pct > 40 else 'below'} this range."
    )
    val_tilt = style_data.get('value_tilt', 50) if isinstance(style_data, dict) else 50
    growth_tilt = style_data.get('growth_tilt', 50) if isinstance(style_data, dict) else 50
    momentum = style_data.get('momentum_exposure', 0) if isinstance(style_data, dict) else 0
    quality = style_data.get('quality_factor', 'N/A') if isinstance(style_data, dict) else 'N/A'
    vol_tilt = style_data.get('volatility_tilt', 'Neutral') if isinstance(style_data, dict) else 'Neutral'
    e["style_analysis"] = (
        f"Investment Style: {style_label}. Value Tilt: {val_tilt:.1f}%, Growth Tilt: {growth_tilt:.1f}%. "
        f"Momentum Exposure: {momentum:.1f}% of stocks showing strong upward momentum. Quality Factor: {quality}. Volatility Tilt: {vol_tilt}. "
        + (f"Your portfolio leans towards Value investing — you hold stocks trading below their estimated worth. This style does well in market recoveries and bear markets. " if val_tilt > 60 else
           f"Your portfolio leans towards Growth investing — you hold fast-growing companies that may appear expensive. This style excels in bull markets but can be volatile. " if growth_tilt > 60 else
           f"Your Blend style balances Value and Growth — the most resilient approach across market cycles. ")
        + f"Quality factor '{quality}' indicates the presence of fundamentally strong companies (high ROE, low debt, consistent earnings) in your portfolio."
    )
    e["concentration_risk"] = (
        f"Concentration Score: {conc_score}/100 (Risk Level: {conc_risk_level}). "
        f"Top 1 stock exposure: {top1:.1f}% of portfolio. Top 3: {top3_exp:.1f}%. Top 5: {top5_exp:.1f}%. "
        f"Single stock flags (>15%): {flagged_stocks_str}. Sector overexposure (>30%): {sector_flags_str}. "
        + (f"RISK ALERT: Your largest stock at {top1:.1f}% is dangerously concentrated. A 30% drop in this stock alone would reduce your portfolio by {top1 * 0.3:.1f}% (~{_fmt(current_val * top1 * 0.003)}). " if top1 > 15 else
           f"Your stock-level concentration is within acceptable limits — no single stock dominates excessively. ")
        + f"Thresholds: Single stock <15%, Top 3 <40%, Top 5 <60%, Single sector <30%. Your portfolio {'violates' if conc_risk_level == 'High' else 'meets'} these standards."
    )
    e["volatility_drawdown"] = (
        f"Volatility & Drawdown Analysis: Historical Volatility: {hist_vol:.1f}% (annualized). Max Drawdown: {max_dd:.1f}%. "
        f"Sharpe Ratio: {sharpe} (return per unit of risk; >1.0 good, >2.0 excellent). Sortino Ratio: {sortino} (return per unit of downside risk; higher is better). "
        f"Portfolio Beta: {port_beta:.2f}. Downside Deviation: {downside_dev:.2f}%. Risk Classification: {risk_class}. "
        f"Your Sharpe of {sharpe:.2f} means for every 1% of volatility risk, you earned {sharpe:.2f}% excess return {'— a strong risk/reward tradeoff' if sharpe > 1 else '— room to improve risk-adjusted returns'}. "
        f"Max drawdown of {max_dd:.1f}% is {'minimal — excellent risk control' if max_dd < 10 else 'moderate — typical for equity portfolios' if max_dd < 20 else 'significant — ensure you can tolerate such drops emotionally and financially'}."
    )
    e["behavior_analysis"] = (
        f"Behavioral Score: {beh_score}/100. Pattern: {beh_pattern}. Average Holding: {avg_hold:.0f} days. "
        f"Short-term holdings (<90 days): {short_term_h}. Long-term holdings (>365 days): {long_term_h}. "
        f"Overtrading: {'DETECTED — more than 50% of stocks held under 90 days, increasing costs and tax burden' if overtrade else 'Not detected — trading frequency is healthy'}. "
        f"With {profitable} profitable and {loss_making} loss-making stocks, common biases to watch: Holding {worst_name} ({_pct(worst_return)}) may reflect loss aversion; "
        f"selling winners like {top_name} too early reflects disposition effect. "
        f"Improving behavior score: Hold winners longer, cut losers faster, avoid churning positions."
    )
    drift_details = []
    for d in drift_sectors[:5]:
        ds = d.get('sector', 'N/A') if isinstance(d, dict) else str(d)
        dp = d.get('portfolio_pct', 0) if isinstance(d, dict) else 0
        db = d.get('benchmark_pct', 0) if isinstance(d, dict) else 0
        dd = d.get('drift', 0) if isinstance(d, dict) else 0
        drift_details.append(f"{ds}: Your {dp:.1f}% vs Benchmark {db}% (drift {dd:+.1f}%)")
    drift_text = '; '.join(drift_details) if drift_details else 'Minimal drift — portfolio aligns well with benchmark'
    alignment_desc = 'significant drift — portfolio has deviated substantially from benchmark' if alignment < 50 else ('moderate drift — some sectors are over/underweight' if alignment < 75 else 'low drift — good alignment with benchmark')
    e["drift_analysis"] = (
        f"Drift Analysis vs Nifty 50 Benchmark. Alignment Score: {alignment:.1f}/100. Deviation Level: {dev_level}. "
        f"Sector drifts detected: {drift_text}. "
        f"Your alignment score of {alignment:.1f}% indicates {alignment_desc}. "
        f"Large positive drift means overweight (you have more than benchmark); large negative drift means underweight (you have less). "
        f"Consider rebalancing sectors with drift > ±10% to reduce tracking error."
    )
    overlaps = overlap_data.get('overlaps', []) if isinstance(overlap_data, dict) else []
    overlap_risk = overlap_data.get('overlap_risk', 'N/A') if isinstance(overlap_data, dict) else 'N/A'
    total_overlaps = overlap_data.get('total_overlap_groups', 0) if isinstance(overlap_data, dict) else 0
    overlap_parts = []
    for ov in overlaps[:5]:
        stocks_in_group = ", ".join([s.get('stock', 'Unknown') if isinstance(s, dict) else str(s) for s in ov.get('stocks', [])[:4]])
        overlap_parts.append(f"{ov.get('group', 'Unknown')}: {ov.get('count', 0)} stocks ({stocks_in_group})")
    e["overlap_detection"] = (
        f"Overlap Risk: {overlap_risk}. Total overlap groups found: {total_overlaps}. "
        + (f"Overlapping groups: {'; '.join(overlap_parts)}. " if overlap_parts else "No significant business group or sector overlaps detected. ")
        + f"Overlap means multiple stocks from the same business group or sector — they tend to move together, reducing diversification benefit. "
        f"In your {num_stocks}-stock portfolio, {'these overlaps mean some of your diversification is illusory — the overlapping stocks will rise and fall together' if total_overlaps > 0 else 'the lack of overlaps indicates genuine diversification across different businesses'}. "
        f"True diversification requires stocks that don't correlate strongly — different sectors, different business groups, different market cap segments."
    )
    attr_gain = attribution.get('total_portfolio_gain', 0) if isinstance(attribution, dict) else 0
    top_contribs = attribution.get('top_contributors', []) if isinstance(attribution, dict) else []
    bot_contribs = attribution.get('bottom_contributors', []) if isinstance(attribution, dict) else []
    gainers_ct = attribution.get('gainers_count', 0) if isinstance(attribution, dict) else 0
    losers_ct = attribution.get('losers_count', 0) if isinstance(attribution, dict) else 0
    sec_attr = attribution.get('sector_attribution', {}) if isinstance(attribution, dict) else {}
    top_contrib_str = "; ".join([f"{c.get('stock', 'Unknown')}: {_fmt(c.get('absolute_contribution', 0))} ({c.get('contribution_pct', 0):.1f}% of total P&L)" for c in top_contribs[:3]])
    bot_contrib_str = "; ".join([f"{c.get('stock', 'Unknown')}: {_fmt(c.get('absolute_contribution', 0))} ({c.get('contribution_pct', 0):.1f}% of total P&L)" for c in bot_contribs[:3]])
    sec_attr_str = "; ".join([f"{k}: {_fmt(v.get('absolute', 0))} ({v.get('contribution_pct', 0):.1f}%)" for k, v in list(sec_attr.items())[:4]]) if sec_attr else "N/A"
    e["return_attribution"] = (
        f"Total portfolio P&L: {_fmt(attr_gain)}. Gainers: {gainers_ct} stocks. Losers: {losers_ct} stocks. "
        f"Top contributors: {top_contrib_str if top_contrib_str else 'N/A'}. "
        f"Bottom contributors (drags): {bot_contrib_str if bot_contrib_str else 'N/A'}. "
        f"Sector attribution: {sec_attr_str}. "
        f"This analysis reveals whether your gains come from broad diversification (many stocks contributing) or concentrated bets (1-2 stocks driving all returns). "
        + (f"{'Your returns are concentrated — top 3 contributors drive the majority of gains, making your portfolio vulnerable if these stocks reverse.' if top_contribs and len(top_contribs) > 0 and abs(top_contribs[0].get('contribution_pct', 0)) > 40 else 'Your returns are well-distributed across multiple stocks — a healthier pattern.'}")
    )
    illiquid = liquidity_data.get('illiquid_positions', []) if isinstance(liquidity_data, dict) else []
    liq_score = liquidity_data.get('portfolio_liquidity_score', 0) if isinstance(liquidity_data, dict) else 0
    liq_risk = liquidity_data.get('liquidity_risk', 'N/A') if isinstance(liquidity_data, dict) else 'N/A'
    illiq_str = "; ".join([f"{p.get('stock', 'Unknown')}: {p.get('days_to_liquidate', 0):.1f} days to liquidate" for p in illiquid[:5]]) if illiquid else "None — all positions are liquid"
    e["liquidity_risk"] = (
        f"Portfolio Liquidity Score: {liq_score}/100. Liquidity Risk: {liq_risk}. "
        f"Illiquid positions (>5 days to sell 10% of position): {illiq_str}. "
        f"Out of {num_stocks} stocks, {len(illiquid)} have low liquidity. "
        f"Liquidity matters during emergencies or market crashes when you need to exit quickly. Large-cap stocks like the Nifty 50 constituents can be sold in seconds; small-cap stocks may take days. "
        + (f"ALERT: {len(illiquid)} illiquid positions totaling a portion of your portfolio — if you need urgent cash, these cannot be sold quickly without price impact." if illiquid else
           f"All positions are sufficiently liquid — you can exit the entire portfolio within a few trading sessions.")
    )
    high_vol_stocks = tail_risk_data.get('high_volatility_stocks', []) if isinstance(tail_risk_data, dict) else []
    hvol_pct = tail_risk_data.get('high_vol_exposure_pct', 0) if isinstance(tail_risk_data, dict) else 0
    scap_pct = tail_risk_data.get('small_cap_exposure_pct', 0) if isinstance(tail_risk_data, dict) else 0
    tail_score = tail_risk_data.get('tail_risk_score', 0) if isinstance(tail_risk_data, dict) else 0
    tail_level = tail_risk_data.get('tail_risk_level', 'N/A') if isinstance(tail_risk_data, dict) else 'N/A'
    hvol_str = "; ".join([f"{s.get('stock', 'Unknown')}: {s.get('volatility', 0):.1f}% annualized volatility" for s in high_vol_stocks[:5]]) if high_vol_stocks else "None"
    e["tail_risk"] = (
        f"Tail Risk Score: {tail_score}/100 (Level: {tail_level}). High-volatility stocks (>40% annualized vol): {hvol_str}. "
        f"High-vol exposure: {hvol_pct:.1f}% of portfolio. Small-cap exposure: {scap_pct:.1f}%. "
        f"In a severe crash scenario (like March 2020 COVID crash, -35%), your portfolio could potentially lose {_fmt(current_val * 0.35)} in a worst case. "
        f"With {len(high_vol_stocks)} high-volatility stocks comprising {hvol_pct:.1f}% of your portfolio, "
        + (f"your tail risk is elevated — consider hedging with put options or reducing exposure to the most volatile names. " if tail_level in ['High', 'Moderate'] else
           f"your tail risk is well-managed — the portfolio can withstand moderate market shocks. ")
        + f"Keep 6-12 months of expenses in liquid assets outside equity to avoid forced selling during crashes."
    )
    e["tax_impact"] = (
        f"Tax Analysis (FY 2024 rates): STCG (held <12 months) gains: {_fmt(stcg_gains)}, taxed at 20% = {_fmt(est_stcg_tax)}. "
        f"LTCG (held >12 months) gains: {_fmt(ltcg_gains)}, taxed at 12.5% above ₹1.25L exemption = {_fmt(est_ltcg_tax)}. LTCG exemption remaining: {_fmt(ltcg_exemption_rem)}. "
        f"Short-term losses: {_fmt(stcg_losses)}. Long-term losses: {_fmt(ltcg_losses)}. These losses can offset gains. "
        f"STT on sell: {_fmt(stt_sell)} (0.1% of sell value). Total estimated tax + transaction costs: {_fmt(total_tax_costs)}. "
        f"Tax planning tip: If stocks are near the 1-year mark, wait to convert STCG (20%) to LTCG (12.5%), saving 7.5% in tax rate. "
        f"Net proceeds if you sold everything today: approximately {_fmt(current_val - total_tax_costs)}."
    )
    int_rate = macro_data.get('interest_rate_sensitivity', {}) if isinstance(macro_data, dict) else {}
    commodity = macro_data.get('commodity_exposure', {}) if isinstance(macro_data, dict) else {}
    currency = macro_data.get('currency_exposure', {}) if isinstance(macro_data, dict) else {}
    bank_exp = int_rate.get('banking_exposure_pct', 0)
    nbfc_exp = int_rate.get('nbfc_exposure_pct', 0)
    crude_exp = commodity.get('crude_sensitive_pct', 0)
    metals_exp = commodity.get('metals_exposure_pct', 0)
    export_exp = currency.get('export_oriented_pct', 0)
    e["macro_sensitivity"] = (
        f"Macro Sensitivity Analysis for your {num_stocks}-stock portfolio: "
        f"Interest Rate Sensitivity: Banking {bank_exp:.1f}% + NBFC {nbfc_exp:.1f}% = {bank_exp + nbfc_exp:.1f}% rate-sensitive. {'HIGH sensitivity — an RBI rate hike of 50bps could negatively impact ~' + f'{bank_exp + nbfc_exp:.1f}% of your portfolio.' if bank_exp + nbfc_exp > 30 else 'Moderate rate sensitivity.'} "
        f"Commodity Exposure: Crude-sensitive {crude_exp:.1f}%, Metals {metals_exp:.1f}%. {'Oil price spikes would impact a significant portion of your portfolio.' if crude_exp > 15 else 'Limited commodity sensitivity.'} "
        f"Currency Exposure: Export-oriented stocks {export_exp:.1f}%. {'A weakening rupee benefits your IT/Pharma export stocks; strengthening rupee hurts them.' if export_exp > 15 else 'Low currency sensitivity.'} "
        f"Prepare for RBI policy changes, global commodity swings, and INR movements based on these exposures."
    )
    scenarios = scenario_data.get('scenarios', []) if isinstance(scenario_data, dict) else []
    scen_val = scenario_data.get('current_portfolio_value', current_val) if isinstance(scenario_data, dict) else current_val
    scenario_parts = []
    for sc in scenarios:
        scenario_parts.append(f"{sc.get('scenario', 'N/A')}: Market move {sc.get('market_move', 0)}% → Portfolio impact {sc.get('projected_portfolio_impact_pct', 0):.1f}%, Estimated loss {_fmt(abs(sc.get('projected_loss_amount', 0)))}")
    e["scenario_analysis"] = (
        f"Stress-test results for your {_fmt(scen_val)} portfolio: "
        + (f"{' | '.join(scenario_parts)}. " if scenario_parts else "No scenario data available. ")
        + f"These projections use stock-specific Beta values to estimate how each holding would react to market shocks. "
        f"For example, a stock with Beta 1.5 would drop 15% in a 10% market crash vs Beta 0.7 dropping only 7%. "
        f"Your portfolio Beta of {port_beta:.2f} means a broad market crash of -20% would approximately reduce your portfolio by {_fmt(abs(scen_val * port_beta * 0.2))}. "
        f"Ensure you can financially and emotionally withstand these scenarios before they happen."
    )

    e["methodology_calculations"] = (
        f"Formulas used for your {num_stocks}-stock, {_fmt(current_val)} portfolio: "
        f"Return = (Current − Investment) / Investment × 100 = ({_fmt(current_val)} − {_fmt(total_inv)}) / {_fmt(total_inv)} × 100 = {_pct(total_gl_pct)}. "
        f"Sharpe Ratio = (Portfolio Return − Risk-Free Rate) / Portfolio Std Dev = {sharpe}. "
        f"Beta = Cov(Stock, Market) / Var(Market) = {port_beta:.2f}. "
        f"Max Drawdown = (Trough − Peak) / Peak = {max_dd:.1f}%. "
        f"Health Score = Diversification(25%) + Risk(25%) + Liquidity(20%) + Behavior(15%) + Style(15%) = {health_val}/100. "
        f"HHI Concentration = Σ(sector weight²) = {hhi:.0f}. All numbers are computed from your actual portfolio data for full transparency."
    )

    return e


_translation_cache = {}


def translate_text(text, target_lang_code):
    if target_lang_code == "en":
        return text

    cache_key = f"{target_lang_code}:{text[:100]}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    try:
        client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        )

        lang_names = {v: k.split(" (")[0] if " (" in k else k for k, v in SUPPORTED_LANGUAGES.items()}
        lang_name = lang_names.get(target_lang_code, "Hindi")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text to {lang_name}. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio', 'STCG', 'LTCG', 'ETF' in English. Keep currency symbol ₹ and all numbers as is. Provide only the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            max_completion_tokens=2000
        )
        translated = response.choices[0].message.content.strip()
        _translation_cache[cache_key] = translated
        return translated
    except Exception:
        return text


def get_metric_explanation(metric_key, lang_code="en", analysis_results=None, advanced_metrics=None, recommendations=None):
    ctx = _extract_portfolio_context(analysis_results, advanced_metrics, recommendations)
    all_explanations = _build_all_explanations(ctx)
    text = all_explanations.get(metric_key, "")
    if not text:
        return ""
    if lang_code != "en":
        text = translate_text(text, lang_code)
    return text


def render_inline_explainer(metric_key, lang_code="en", analysis_results=None, advanced_metrics=None, recommendations=None):
    import streamlit as st

    explanation = get_metric_explanation(metric_key, lang_code, analysis_results, advanced_metrics, recommendations)
    if not explanation:
        return

    unique_key = f"explain_{metric_key}_{hash(metric_key) % 100000}"

    with st.popover("ℹ️", use_container_width=False):
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%); 
                    padding: 16px; border-radius: 10px; border-left: 4px solid #4285f4;'>
            <p style='font-size: 14px; color: #333; line-height: 1.7; margin: 0;'>
                {explanation}
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_section_explainer(title, metric_key, lang_code="en", analysis_results=None, advanced_metrics=None, recommendations=None, icon=""):
    import streamlit as st

    explanation = get_metric_explanation(metric_key, lang_code, analysis_results, advanced_metrics, recommendations)
    if not explanation:
        st.subheader(f"{icon} {title}" if icon else title)
        return

    col_title, col_info = st.columns([20, 1])
    with col_title:
        st.subheader(f"{icon} {title}" if icon else title)
    with col_info:
        with st.popover("ℹ️", use_container_width=False):
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%); 
                        padding: 16px; border-radius: 10px; border-left: 4px solid #4285f4;'>
                <p style='font-size: 14px; color: #333; line-height: 1.7; margin: 0;'>
                    {explanation}
                </p>
            </div>
            """, unsafe_allow_html=True)


def generate_dynamic_explanation(page_key, analysis_results=None, advanced_metrics=None, recommendations=None):
    ctx = _extract_portfolio_context(analysis_results, advanced_metrics, recommendations)
    e = _build_all_explanations(ctx)

    page_map = {
        "dashboard": {
            "title": "Dashboard - Executive Summary",
            "icon": "📊",
            "summary": e.get("dashboard_summary", ""),
            "metrics": [
                {"name": "Portfolio Health Score", "explanation": e.get("portfolio_health_score", "")},
                {"name": "Total Investment", "explanation": e.get("total_investment", "")},
                {"name": "Current Value", "explanation": e.get("current_value", "")},
                {"name": "Total Gain/Loss", "explanation": e.get("total_gain_loss", "")},
                {"name": "Return Percentage", "explanation": e.get("return_percentage", "")},
                {"name": "Stock Performance Table", "explanation": e.get("stock_performance_table", "")},
                {"name": "Dividend Yield", "explanation": e.get("dividend_yield", "")},
            ]
        },
        "sectors": {
            "title": "Sectors - Industry Breakdown",
            "icon": "🏭",
            "summary": e.get("sector_allocation_pie", ""),
            "metrics": [
                {"name": "Sector Allocation Pie Chart", "explanation": e.get("sector_allocation_pie", "")},
                {"name": "Sector Performance", "explanation": e.get("sector_performance", "")},
                {"name": "Sector Insights", "explanation": e.get("sector_insights", "")},
                {"name": "Diversification Analysis", "explanation": e.get("diversification_analysis", "")},
                {"name": "Sector Recommendations", "explanation": e.get("sector_recommendations", "")},
            ]
        },
        "stocks": {
            "title": "Stocks - Individual Performance",
            "icon": "📈",
            "summary": e.get("stock_wise_returns", ""),
            "metrics": [
                {"name": "Stock-wise Returns", "explanation": e.get("stock_wise_returns", "")},
                {"name": "Price Chart", "explanation": e.get("price_chart", "")},
                {"name": "Investment vs Current Value", "explanation": e.get("investment_vs_current", "")},
            ]
        },
        "benchmark": {
            "title": "Benchmark - Market Comparison",
            "icon": "📊",
            "summary": e.get("portfolio_vs_nifty", ""),
            "metrics": [
                {"name": "Portfolio vs Nifty 50", "explanation": e.get("portfolio_vs_nifty", "")},
                {"name": "Portfolio vs Sensex", "explanation": e.get("portfolio_vs_sensex", "")},
                {"name": "Alpha", "explanation": e.get("alpha", "")},
                {"name": "Beta", "explanation": e.get("beta", "")},
            ]
        },
        "advice": {
            "title": "Advice - Investment Recommendations",
            "icon": "💡",
            "summary": e.get("buy_hold_sell", ""),
            "metrics": [
                {"name": "Value Analysis", "explanation": e.get("value_analysis", "")},
                {"name": "Growth Analysis", "explanation": e.get("growth_analysis", "")},
                {"name": "BUY / HOLD / SELL Rating", "explanation": e.get("buy_hold_sell", "")},
                {"name": "Alternative Suggestions", "explanation": e.get("alternative_suggestions", "")},
            ]
        },
        "rebalance": {
            "title": "Rebalance - Portfolio Adjustment",
            "icon": "⚖️",
            "summary": e.get("overweight_positions", ""),
            "metrics": [
                {"name": "Overweight Positions", "explanation": e.get("overweight_positions", "")},
                {"name": "Underweight Positions", "explanation": e.get("underweight_positions", "")},
                {"name": "Concentration Alerts", "explanation": e.get("concentration_alerts", "")},
                {"name": "Rebalancing Strategy", "explanation": e.get("rebalancing_strategy", "")},
            ]
        },
        "history": {
            "title": "History - Performance Over Time",
            "icon": "📅",
            "summary": e.get("portfolio_value_over_time", ""),
            "metrics": [
                {"name": "Performance Summary", "explanation": e.get("performance_summary", "")},
                {"name": "Portfolio Value Over Time", "explanation": e.get("portfolio_value_over_time", "")},
                {"name": "Cumulative Returns Over Time", "explanation": e.get("cumulative_returns", "")},
                {"name": "Drawdown Analysis", "explanation": e.get("drawdown_analysis", "")},
                {"name": "Period-wise Returns", "explanation": e.get("period_wise_returns", "")},
                {"name": "Performance Insights", "explanation": e.get("performance_insights", "")},
            ]
        },
        "profile": {
            "title": "Profile - Investor Profile",
            "icon": "👤",
            "summary": e.get("investor_type", ""),
            "metrics": [
                {"name": "Investor Type", "explanation": e.get("investor_type", "")},
                {"name": "Risk Tolerance", "explanation": e.get("risk_tolerance", "")},
                {"name": "Holding Period", "explanation": e.get("holding_period", "")},
                {"name": "Behavioral Analysis", "explanation": e.get("behavioral_analysis", "")},
            ]
        },
        "advanced": {
            "title": "Advanced - Deep Analysis",
            "icon": "🔬",
            "summary": e.get("health_score", ""),
            "metrics": [
                {"name": "Health Score", "explanation": e.get("health_score", "")},
                {"name": "Risk Radar", "explanation": e.get("risk_radar", "")},
                {"name": "Structural Diagnostics", "explanation": e.get("structural_diagnostics", "")},
                {"name": "Style Analysis", "explanation": e.get("style_analysis", "")},
                {"name": "Concentration Risk", "explanation": e.get("concentration_risk", "")},
                {"name": "Volatility & Drawdown", "explanation": e.get("volatility_drawdown", "")},
                {"name": "Behavior Analysis", "explanation": e.get("behavior_analysis", "")},
                {"name": "Drift Analysis", "explanation": e.get("drift_analysis", "")},
                {"name": "Overlap Detection", "explanation": e.get("overlap_detection", "")},
                {"name": "Return Attribution", "explanation": e.get("return_attribution", "")},
                {"name": "Liquidity Risk", "explanation": e.get("liquidity_risk", "")},
                {"name": "Tail Risk", "explanation": e.get("tail_risk", "")},
                {"name": "Tax Impact", "explanation": e.get("tax_impact", "")},
                {"name": "Macro Sensitivity", "explanation": e.get("macro_sensitivity", "")},
                {"name": "Scenario Analysis", "explanation": e.get("scenario_analysis", "")},
            ]
        },
        "methodology": {
            "title": "Methodology - How We Calculate",
            "icon": "📐",
            "summary": e.get("methodology_calculations", ""),
            "metrics": [
                {"name": "Calculation Methods", "explanation": e.get("methodology_calculations", "")},
            ]
        }
    }

    return page_map.get(page_key, {
        "title": page_key.title(),
        "icon": "📊",
        "summary": "",
        "metrics": []
    })


def get_translated_dynamic_explanation(page_key, lang_code="en", analysis_results=None, advanced_metrics=None, recommendations=None):
    explanation = generate_dynamic_explanation(page_key, analysis_results, advanced_metrics, recommendations)

    if lang_code == "en":
        return explanation

    batch_cache_key = f"dyn_batch:{lang_code}:{page_key}:{hash(explanation.get('summary', '')[:50])}"
    if batch_cache_key in _translation_cache:
        return _translation_cache[batch_cache_key]

    try:
        client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        )

        lang_names = {v: k.split(" (")[0] if " (" in k else k for k, v in SUPPORTED_LANGUAGES.items()}
        lang_name = lang_names.get(lang_code, "Hindi")

        texts_to_translate = [explanation.get("summary", "")]
        for metric in explanation.get("metrics", []):
            texts_to_translate.append(metric["explanation"])

        combined = "\n---SEPARATOR---\n".join(texts_to_translate)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following texts to {lang_name}. Each text is separated by '---SEPARATOR---'. Keep the separator in your output. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio', 'STCG', 'LTCG', 'ETF' in English. Keep currency symbol ₹ and all numbers as is. Provide only the translations with separators, nothing else."},
                {"role": "user", "content": combined}
            ],
            max_completion_tokens=4000
        )

        translated_parts = response.choices[0].message.content.strip().split("---SEPARATOR---")
        translated_parts = [p.strip() for p in translated_parts]

        translated = {
            "title": explanation.get("title", ""),
            "icon": explanation.get("icon", ""),
            "summary": translated_parts[0] if translated_parts else explanation.get("summary", ""),
            "metrics": []
        }

        for i, metric in enumerate(explanation.get("metrics", [])):
            idx = i + 1
            translated["metrics"].append({
                "name": metric["name"],
                "explanation": translated_parts[idx] if idx < len(translated_parts) else metric["explanation"]
            })

        _translation_cache[batch_cache_key] = translated
        return translated
    except Exception:
        return explanation


def render_page_explainer(page_key, lang_code="en", analysis_results=None, advanced_metrics=None, recommendations=None):
    import streamlit as st

    explanation = get_translated_dynamic_explanation(
        page_key, lang_code, analysis_results, advanced_metrics, recommendations
    )
    if not explanation:
        return

    expander_label = EXPANDER_LABELS.get(lang_code, "Understanding this page")

    with st.expander(f"ℹ️ {expander_label}", expanded=False):
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%); 
                    padding: 20px; border-radius: 12px; border-left: 4px solid #4285f4;
                    margin-bottom: 16px;'>
            <p style='font-size: 15px; color: #333; line-height: 1.6; margin: 0;'>
                {explanation.get('summary', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        metrics = explanation.get("metrics", [])
        if metrics:
            for metric in metrics:
                st.markdown(f"""
                <div style='background: #ffffff; padding: 14px 18px; border-radius: 10px; 
                            border: 1px solid #e5e7eb; margin-bottom: 10px;'>
                    <p style='font-weight: 700; color: #1a1a2e; margin: 0 0 6px 0; font-size: 14px;'>
                        📌 {metric['name']}
                    </p>
                    <p style='color: #555; font-size: 13px; line-height: 1.5; margin: 0;'>
                        {metric['explanation']}
                    </p>
                </div>
                """, unsafe_allow_html=True)


def render_language_selector():
    import streamlit as st

    if 'explanation_language' not in st.session_state:
        st.session_state.explanation_language = "English"

    lang = st.selectbox(
        "🌐 Explanation Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.explanation_language),
        key="lang_selector"
    )

    if lang != st.session_state.explanation_language:
        st.session_state.explanation_language = lang
        st.rerun()

    return SUPPORTED_LANGUAGES.get(lang, "en")
