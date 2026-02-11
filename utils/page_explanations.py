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
    adv = c['advanced_metrics']
    win_rate = (profitable / num_stocks * 100) if num_stocks > 0 else 0

    health = _safe_get(adv, 'health_score', default={})
    health_val = health.get('score', 'N/A') if isinstance(health, dict) else 'N/A'
    health_grade = health.get('grade', 'N/A') if isinstance(health, dict) else 'N/A'
    concentration = _safe_get(adv, 'concentration', default={})
    top1 = concentration.get('top1_pct', 0) if isinstance(concentration, dict) else 0
    volatility = _safe_get(adv, 'volatility', default={})
    sharpe = volatility.get('sharpe_ratio', 'N/A') if isinstance(volatility, dict) else 'N/A'
    max_dd = volatility.get('max_drawdown', 0) if isinstance(volatility, dict) else 0
    tax_data = _safe_get(adv, 'tax_impact', default={})
    stcg = tax_data.get('stcg_tax', 0) if isinstance(tax_data, dict) else 0
    ltcg = tax_data.get('ltcg_tax', 0) if isinstance(tax_data, dict) else 0

    sector_summary_parts = []
    if c['sector_data']:
        try:
            sec_df = pd.DataFrame(c['sector_data']) if not isinstance(c['sector_data'], pd.DataFrame) else c['sector_data']
            for _, row in sec_df.head(3).iterrows():
                sector_summary_parts.append(f"{row.get('Sector', 'Unknown')} ({row.get('Percentage of Portfolio', 0):.1f}%)")
        except:
            pass
    top_3_sectors = ", ".join(sector_summary_parts) if sector_summary_parts else "your various sectors"

    d = c.get('dividend_metrics', {})
    div_yield = d.get('portfolio_dividend_yield', 0)
    div_annual = d.get('total_annual_dividend', 0)
    div_stock = d.get('highest_yield_stock', 'N/A')
    div_paying = d.get('dividend_paying_stocks', 0)

    e = {}

    e["dashboard_summary"] = (
        f"Your portfolio of {num_stocks} stocks has a total investment of {_fmt(total_inv)} and is currently worth {_fmt(current_val)}. "
        f"You have {gain_word} {_fmt(abs(total_gl))} ({_pct(total_gl_pct)}). "
        f"{profitable} out of {num_stocks} stocks are in profit and {loss_making} are in loss. "
        f"Your best performer is {top_name} ({_pct(top_return)}) and your weakest is {worst_name} ({_pct(worst_return)})."
    )
    e["portfolio_health_score"] = (
        f"Your portfolio health score is a single number (0-100) that grades your overall portfolio quality. It considers multiple factors: "
        f"your diversification across {num_sectors} sectors, your overall return of {_pct(total_gl_pct)}, "
        f"your win rate ({profitable} out of {num_stocks} stocks are profitable = {win_rate:.0f}% win rate), "
        f"and how well-balanced your sector allocation is. "
        f"A score above 75 means your portfolio is healthy and well-structured. A score between 50-75 means there's room to improve. "
        f"Below 50 means your portfolio needs significant attention - perhaps too concentrated in one sector, too many loss-making stocks, "
        f"or insufficient diversification. Think of it like a health check-up report for your investments."
    )
    e["total_investment"] = (
        f"This is the total money you originally spent to buy all {num_stocks} stocks in your portfolio - currently {_fmt(total_inv)}. "
        f"This is your 'cost basis' or the starting point to measure whether you're making or losing money. "
        f"For example, if you bought 100 shares of a stock at ₹200 each, that contributes ₹20,000 to your total investment. "
        f"This number doesn't change with market movements - it only changes if you buy or sell stocks."
    )
    e["current_value"] = (
        f"This is what all your {num_stocks} stocks are worth right now at current market prices - {_fmt(current_val)}. "
        + (f"Since this is {_fmt(abs(current_val - total_inv))} MORE than what you invested ({_fmt(total_inv)}), "
           f"you're sitting on a profit of {_pct(total_gl_pct)}. "
           f"If you sold everything today, you would receive approximately {_fmt(current_val)} (before taxes and charges)."
           if current_val >= total_inv else
           f"Since this is {_fmt(abs(total_inv - current_val))} LESS than what you invested ({_fmt(total_inv)}), "
           f"you're currently at a loss of {_pct(abs(total_gl_pct))}. "
           f"However, this is an 'unrealized' loss - meaning you haven't actually lost money until you sell.")
    )
    e["total_gain_loss"] = (
        f"You have {gain_word} {_fmt(abs(total_gl))} overall ({_pct(total_gl_pct)}). "
        f"This is the difference between what your stocks are worth now ({_fmt(current_val)}) and what you paid ({_fmt(total_inv)}). "
        f"Your biggest winner is {top_name} which has returned {_pct(top_return)}, and your biggest drag is {worst_name} at {_pct(worst_return)}. "
        f"Out of {num_stocks} stocks, {profitable} are making money and {loss_making} are in loss. "
        f"Remember: gains/losses are 'unrealized' until you actually sell the stocks. "
        + (f"If you hold profitable stocks for more than 1 year, you pay only 10% LTCG tax (above ₹1 lakh gain). "
           f"Selling within 1 year means 15% STCG tax." if total_gl > 0 else
           f"Tax benefit: Losses can be set off against gains to reduce your tax liability.")
    )
    e["return_percentage"] = (
        f"Your overall portfolio return is {_pct(total_gl_pct)}. This tells you how much your money has grown (or shrunk) as a percentage. "
        f"For comparison: a bank Fixed Deposit gives about 6-7% per year, a Nifty 50 index fund historically gives 12-14% per year. "
        + (f"Your portfolio is {'outperforming' if total_gl_pct > 14 else 'performing in line with' if total_gl_pct > 7 else 'underperforming compared to'} the market average. "
           if total_gl_pct != 0 else "")
        + f"Important: Compare your return with the time period - a 20% return in 3 months is excellent, but 20% in 5 years is below average."
    )
    e["stock_performance_table"] = (
        f"This table lists all {num_stocks} stocks with detailed performance data for each one. "
        f"It shows: Buy Price (what you paid per share), Current Price (what it's worth now), Quantity (shares you hold), "
        f"Investment Value (total cost), Current Value (total worth), and Gain/Loss (both in ₹ and %). "
        f"Currently {profitable} stocks are in profit (green) and {loss_making} stocks are in loss (red). "
        f"Pay special attention to {worst_name} ({_pct(worst_return)}) - if the loss is significant, evaluate whether to hold or cut losses. "
        f"Also watch {top_name} ({_pct(top_return)}) - consider booking partial profits if it has become too large a portion of your portfolio."
    )
    e["dividend_yield"] = (
        f"Your portfolio's overall dividend yield is {div_yield:.2f}%, generating approximately {_fmt(div_annual)} per year in dividends. "
        f"{div_paying} out of {num_stocks} stocks pay dividends. Your highest dividend-paying stock is {div_stock}. "
        f"Dividends are like 'rent' from your stocks - companies share their profits with you regularly. "
        f"A good dividend yield for Indian stocks is 1-3%. Above 3% is considered high yield. "
        f"Dividends provide income even when stock prices don't rise, making your portfolio more resilient."
    )

    e["sector_allocation_pie"] = (
        f"Your portfolio is spread across {num_sectors} sectors. Your top sectors are: {top_3_sectors}. "
        f"The largest sector is {top_sector_name} at {top_sector_pct:.1f}% of your portfolio. "
        f"Think of sectors like baskets - you don't want all eggs in one basket. "
        f"Ideally, no single sector should be more than 25-30% of your portfolio. "
        + (f"Your {top_sector_name} allocation at {top_sector_pct:.1f}% is quite concentrated. "
           f"If this sector faces regulatory changes, economic slowdown, or industry-specific issues, "
           f"a large portion of your portfolio could be negatively affected. Consider spreading into other sectors."
           if top_sector_pct > 30 else
           f"Your sector allocation looks reasonably well-distributed, which provides good protection against sector-specific risks.")
    )
    e["sector_performance"] = (
        f"This chart shows returns for each of your {num_sectors} sectors. Green bars mean the sector is in profit, red means loss. "
        f"If an entire sector is losing money, it's usually a market-wide or industry issue, not just your stock-picking. "
        f"For example, if all IT stocks are down, it might be due to global tech spending cuts, not because you picked wrong IT stocks. "
        f"Conversely, if only YOUR stock in a sector is down while the sector is up, your specific stock pick may need review. "
        f"Compare your sector returns with sectoral indices (like Nifty IT, Nifty Bank) to see if you're beating the sector average."
    )
    e["sector_insights"] = (
        f"These insights identify your best-performing sector, worst-performing sector, and highest allocation sector. "
        f"Key things to watch: Is your worst-performing sector also your largest allocation? That's a red flag. "
        f"Is your best-performing sector a tiny allocation? You might want to increase exposure there. "
        f"The ideal scenario is having your largest allocations in well-performing sectors with reasonable growth prospects."
    )
    e["diversification_analysis"] = (
        f"With {num_sectors} sectors and {num_stocks} stocks, this measures how well-spread your investments are. "
        f"Excellent diversification: 8+ sectors with no single sector above 25%. "
        f"Good diversification: 5-7 sectors. Needs improvement: fewer than 5 sectors. "
        f"Your concentration risk shows what percentage of your portfolio is in the largest sector ({top_sector_name}: {top_sector_pct:.1f}%). "
        f"Higher concentration = higher risk. If {top_sector_name} drops 20%, it would drag your entire portfolio down by approximately {top_sector_pct * 0.2:.1f}%."
    )
    e["sector_recommendations"] = (
        f"Actionable suggestions based on your sector allocation: over-concentrated sectors to trim, "
        f"underperforming sectors to review, strong performers to potentially increase. "
        f"These help you make informed decisions about whether to add, hold, or reduce exposure to specific industries."
    )

    e["stock_wise_returns"] = (
        f"Individual stock returns show exactly how much each of your {num_stocks} stocks has earned or lost. "
        f"Your best stock {top_name} has returned {_pct(top_return)} - this means for every ₹100 you invested in it, "
        f"it's now worth ₹{100 + float(top_return) if isinstance(top_return, (int,float)) else 100:.0f}. "
        f"Your worst stock {worst_name} is at {_pct(worst_return)}. "
        f"Out of {num_stocks} stocks, {profitable} are making money and {loss_making} are in loss. "
        f"A general rule: if a stock is down more than 20-30% and fundamentals haven't changed, consider averaging down. "
        f"If fundamentals have worsened, consider cutting your losses."
    )
    e["price_chart"] = (
        f"Price charts show how each stock's price has moved over time since you bought it. "
        f"An upward-sloping line means the stock has been growing in value. A downward slope means declining. "
        f"Look for these patterns: steady upward trend (good - consistent growth), sharp spikes (might be speculative), "
        f"gradual decline (review fundamentals), or flat line (stock isn't moving, your money is stuck). "
        f"Compare your stocks' movements to see which ones have been steadily growing versus which are volatile."
    )
    e["investment_vs_current"] = (
        f"For each stock, this bar chart compares your original investment (what you paid) versus current value (what it's worth). "
        f"Green bars mean the stock is in profit, red bars mean loss. "
        f"Your total investment of {_fmt(total_inv)} is now worth {_fmt(current_val)}. "
        f"The taller the green bar above your investment bar, the more profitable that stock is. "
        f"Stocks with large red bars are dragging your portfolio down - evaluate whether they have recovery potential."
    )

    e["portfolio_vs_nifty"] = (
        f"Your portfolio returned {_pct(total_gl_pct)} overall. This is compared against the Nifty 50 index (top 50 Indian companies by market cap). "
        f"If Nifty 50 has beaten your return, it means you would have earned more money with less effort by simply buying a Nifty 50 index fund (like UTI Nifty ETF or SBI Nifty Index Fund). "
        f"If your portfolio beats Nifty, your stock selection skill is adding value - keep doing what you're doing! "
        f"Most professional fund managers struggle to beat the Nifty consistently, so beating it is genuinely impressive."
    )
    e["portfolio_vs_sensex"] = (
        f"Sensex tracks the top 30 companies on BSE (Bombay Stock Exchange). Like the Nifty comparison, "
        f"this tells you if your active stock picking is worthwhile compared to simply investing in the market. "
        f"Sensex and Nifty move very similarly, but Sensex is narrower (30 stocks vs 50). "
        f"If your portfolio consistently underperforms both benchmarks, consider shifting some money to index funds."
    )
    e["alpha"] = (
        f"Alpha measures your EXTRA returns above what the market delivered. With your {_pct(total_gl_pct)} return: "
        f"Positive Alpha = Your stock picking is adding value - you're earning MORE than the market average. "
        f"Negative Alpha = You'd actually be better off with a simple index fund. "
        f"Zero Alpha = Your returns match the market exactly. "
        f"Think of Alpha as your 'skill premium' - the reward (or penalty) for the time and effort you spend picking individual stocks "
        f"instead of just buying the whole market through an index fund."
    )
    e["beta"] = (
        f"Beta measures how much your portfolio swings compared to the market. "
        f"Beta = 1.0 means your {num_stocks} stocks move exactly like the market (Nifty goes up 2%, your portfolio goes up ~2%). "
        f"Beta > 1.0 (say 1.5) means your portfolio is MORE volatile - if Nifty drops 10%, your portfolio might drop ~15%. But on good days, you gain more too. "
        f"Beta < 1.0 (say 0.7) means your portfolio is LESS volatile - steadier, fewer dramatic ups and downs. "
        f"For retirement or conservative goals, lower Beta is safer. For long-term wealth building, moderate Beta (0.8-1.2) is typical."
    )

    e["value_analysis"] = (
        f"Value Analysis checks if each of your {num_stocks} stocks is 'cheap' or 'expensive' compared to its actual worth. "
        f"It uses metrics like P/E ratio (price vs earnings), P/B ratio (price vs book value), and dividend yield. "
        f"Think of it like buying a house - is the asking price fair compared to the property's value? "
        f"A stock trading below its intrinsic value is a 'bargain' - you might want to buy more. "
        f"A stock trading well above its value might be overpriced - time to consider booking profits."
    )
    e["growth_analysis"] = (
        f"Growth Analysis checks if your stocks' companies are growing fast - revenue increasing, profits rising, market share expanding. "
        f"Fast-growing companies like TCS, Infosys, or Bajaj Finance can give big returns even if they seem expensive today. "
        f"It examines: revenue growth rate, profit growth, return on equity (ROE), and business expansion. "
        f"A company growing at 20%+ annually could double in value in 3-4 years, even if its P/E ratio looks high right now."
    )
    e["buy_hold_sell"] = (
        f"Each of your {num_stocks} stocks gets a specific recommendation combining both Value and Growth perspectives. "
        f"BUY = The stock looks attractive at current prices - consider adding more shares. "
        f"HOLD = Keep what you have - the stock is fairly valued, no urgent action needed. "
        f"SELL = Consider exiting - the stock may be overvalued or fundamentally weak. "
        f"Pay attention to {worst_name} ({_pct(worst_return)}) - if it gets a SELL rating, the data supports cutting your losses. "
        f"Remember: These are algorithmic recommendations based on data, not personal advice. Always cross-check with your investment goals."
    )
    e["alternative_suggestions"] = (
        f"For stocks rated SELL, we suggest stronger alternatives in the same sector. "
        f"For example, if {worst_name} gets a SELL rating, we'll suggest better-performing or better-valued options in the same industry. "
        f"This helps you redeploy your money more effectively without changing your overall sector exposure. "
        f"Always research the suggested alternatives before investing."
    )

    e["overweight_positions"] = (
        f"These are stocks that take up too much of your portfolio. "
        + (f"If {top_name} has grown significantly ({_pct(top_return)}), it may now represent a disproportionately large chunk of your portfolio. "
           f"While it's great that it grew, having too much in one stock is risky - if it suddenly drops, your entire portfolio takes a big hit. "
           f"Consider selling some shares and spreading that money across other stocks to manage risk."
           if top_name != "N/A" else "Stocks that have grown a lot may need trimming.")
    )
    e["underweight_positions"] = (
        f"These are sectors or stock categories where you have too little invested. With {_fmt(total_inv)} total investment, "
        f"adding to underweight areas improves balance and reduces risk. "
        f"For example, if you have zero exposure to Pharma or IT, you're missing potential growth opportunities. "
        f"A well-balanced portfolio typically has exposure to 5-8 different sectors at minimum."
    )
    e["concentration_alerts"] = (
        f"Warnings when any single stock exceeds 10-15% of your {_fmt(current_val)} portfolio, "
        f"or any sector exceeds 25-30%. "
        + (f"Your biggest sector {top_sector_name} is at {top_sector_pct:.1f}%. "
           if top_sector_name != "N/A" else "")
        + f"Concentration risk is one of the biggest portfolio killers - even great companies can face unexpected problems "
        f"(regulatory changes, management issues, sector downturns). Diversification is your best protection."
    )
    e["rebalancing_strategy"] = (
        f"Rebalancing means adjusting your portfolio back to a target allocation. Over time, winning stocks grow bigger "
        f"and losing ones shrink, causing your portfolio to drift from your intended balance. "
        f"Regular rebalancing (quarterly or semi-annually) forces you to 'sell high and buy low' systematically. "
        f"It's one of the simplest ways to manage risk and potentially improve long-term returns."
    )

    e["portfolio_value_over_time"] = (
        f"This chart shows your portfolio's journey from {_fmt(total_inv)} to {_fmt(current_val)} over time. "
        f"The blue line represents your portfolio's actual value on each day. The gray dashed line shows your cost basis (what you invested). "
        f"When the blue line is above the gray line, you're in profit. Below it means you're at a loss for that period. "
        f"The star marker shows your portfolio's all-time peak value. "
        f"Dips along the way are completely normal - what matters is the overall direction. "
        f"Your portfolio has {gain_word} {_fmt(abs(total_gl))} in total from your starting point."
    )
    e["cumulative_returns"] = (
        f"This shows your cumulative return percentage over time. Green bars mean positive returns, red bars mean negative. "
        f"With your current {_pct(total_gl_pct)} total return, you can see exactly when your portfolio was performing best and worst. "
        f"This helps you understand if your portfolio's growth has been steady or if it came in sudden bursts. "
        f"Steady growth is generally better than volatile swings, even if the end result is the same."
    )
    e["drawdown_analysis"] = (
        f"Drawdown measures how much your portfolio has fallen from its highest point. "
        f"Think of it like a hiker climbing a mountain - drawdown shows how far they've slipped back from the peak. "
        f"A max drawdown of -20% means at some point, your portfolio lost 20% from its highest value. "
        f"This is crucial for understanding risk: even if your overall return is positive, large drawdowns can be emotionally devastating "
        f"and might cause you to panic-sell at the worst time. "
        f"Lower drawdowns (less negative) mean your portfolio is more stable and easier to hold through tough times."
    )
    e["period_wise_returns"] = (
        f"This breaks down your returns by time periods - daily, weekly, or monthly. "
        f"You can see which months were good and which were tough. "
        f"Win Rate shows the percentage of periods with positive returns. A win rate above 55% is quite good for equity investments. "
        f"The Best Period and Average Return help you set realistic expectations. "
        f"If your average monthly return is 1-2%, that's about 12-24% annually - which is excellent."
    )
    e["performance_summary"] = (
        f"Key performance numbers at a glance: Total Return ({_pct(total_gl_pct)} overall change), "
        f"Peak Portfolio Value (highest value your portfolio ever reached), "
        f"Current Drawdown (how far you are from that peak), and Annualized Volatility (how much your portfolio swings). "
        f"Low volatility with high returns is the ideal combination - it means steady growth without dramatic ups and downs."
    )
    e["performance_insights"] = (
        f"Automated observations about your portfolio's health based on return levels, drawdown severity, volatility, and recent momentum. "
        f"These insights flag potential concerns (high drawdowns, negative trends) and highlight positives (strong returns, low volatility). "
        f"Think of it as a quick health check summary - green insights are good, yellow means watch out, red means action needed."
    )

    e["investor_type"] = (
        f"With {num_stocks} stocks across {num_sectors} sectors and a {_pct(total_gl_pct)} return, "
        f"your investing style is classified as aggressive, moderate, or conservative. "
        f"Aggressive: Heavy small/mid-cap, concentrated bets, high volatility stocks. "
        f"Moderate: Mix of large and mid-cap, balanced sectors, moderate volatility. "
        f"Conservative: Mostly large-cap blue chips, diversified sectors, low volatility. "
        f"Knowing your style helps you make consistent decisions aligned with your risk tolerance."
    )
    e["risk_tolerance"] = (
        f"Your portfolio's risk level is assessed based on your stock choices, sector concentration, and returns pattern. "
        f"High risk means bigger potential gains but also bigger losses. "
        f"If you're investing for goals within 2-3 years (like buying a house), lower risk is safer. "
        f"For long-term goals (10+ years like retirement), you can afford higher risk as temporary dips tend to recover."
    )
    e["holding_period"] = (
        f"How long you typically hold stocks significantly impacts taxes and returns. "
        f"Short-term (less than 1 year): 15% STCG tax on profits. "
        f"Long-term (more than 1 year): 10% LTCG tax on profits above ₹1 lakh per year. "
        f"Historical data shows longer holding periods generally produce better returns and lower taxes. "
        f"The stock market has never given negative returns over any 15-year period in India's history."
    )
    e["behavioral_analysis"] = (
        f"This examines your investing habits and potential biases. With {profitable} winning and {loss_making} losing stocks: "
        f"Loss Aversion: Are you holding losing stocks too long, hoping they'll recover? "
        f"Disposition Effect: Are you selling winners too early while keeping losers? "
        f"Overconfidence: Did you bet too heavily on certain stocks? "
        f"Recency Bias: Are your recent decisions influenced by recent news rather than fundamentals? "
        f"These biases are natural human tendencies, but awareness helps you make better decisions."
    )

    e["health_score"] = (
        f"Your portfolio scored {health_val}/100 (Grade {health_grade}). "
        + (f"Above 75 is healthy - your portfolio is well-structured. " if isinstance(health_val, (int, float)) and health_val >= 75 else
           f"Below 75 means there's room for improvement. " if isinstance(health_val, (int, float)) else "")
        + f"The score considers: diversification ({num_sectors} sectors), returns ({_pct(total_gl_pct)}), risk metrics, "
        f"concentration levels, and overall portfolio balance. "
        f"To improve your score: add more sectors, reduce largest positions, and review consistently underperforming stocks."
    )
    e["risk_radar"] = (
        f"A spider chart showing 8 risk dimensions of your portfolio. "
        f"Each spoke represents a different risk type - the further out the point on each spoke, the higher that particular risk. "
        f"Risk dimensions include: concentration risk, volatility, drawdown, sector risk, liquidity risk, and more. "
        f"Look for any spokes sticking out dramatically far - those are your biggest vulnerabilities. "
        f"An ideal portfolio would have a relatively even, moderate shape across all spokes."
    )
    e["structural_diagnostics"] = (
        f"Shows how your {_fmt(current_val)} portfolio is split between Large Cap (top 100 companies - safer, steadier), "
        f"Mid Cap (101-250 - moderate risk, good growth potential), and Small Cap (250+ - higher risk, highest growth potential). "
        f"A balanced mix for moderate investors: 50-60% Large Cap, 20-30% Mid Cap, 10-20% Small Cap. "
        f"Conservative: 70%+ Large Cap. Aggressive: 40%+ Mid/Small Cap."
    )
    e["style_analysis"] = (
        f"Your {num_stocks} stocks are analyzed for Value vs Growth investment tilt. "
        f"Value investing: Buying established companies whose stock price is below their actual worth (like buying a ₹100 item for ₹70). "
        f"Growth investing: Buying fast-growing companies that might seem expensive but could grow into their valuation. "
        f"Most successful portfolios have a blend of both. Pure value can miss opportunities; pure growth can be volatile."
    )
    e["concentration_risk"] = (
        f"Your single largest stock holds {top1:.1f}% of your portfolio. "
        + (f"That's too concentrated (above 15%) - if this one stock drops 30%, your entire portfolio would lose about {top1 * 0.3:.1f}%. "
           f"Consider selling some shares and redistributing across other stocks."
           if top1 > 15 else f"This is within a reasonable range - good diversification.")
        + f" Ideally, no single stock should exceed 10-15% of your {_fmt(current_val)} portfolio."
    )
    e["volatility_drawdown"] = (
        f"Your portfolio's Sharpe ratio is {sharpe} (higher is better; above 1.0 is good, above 2.0 is excellent). "
        f"The Sharpe ratio measures 'risk-adjusted returns' - how much return you get per unit of risk taken. "
        f"A Sharpe of 0.5 means mediocre risk-adjusted performance, while 1.5+ means excellent. "
        f"Max drawdown was {max_dd:.1f}% - this is the biggest drop from a peak your portfolio experienced."
    )
    e["behavior_analysis"] = (
        f"Analyzes your investing habits. With {profitable} profitable and {loss_making} loss-making stocks, "
        f"this section identifies common behavioral biases: "
        f"Are you holding losers too long hoping they'll bounce back? Are you selling winners too early? "
        f"These are the most common and costly investing mistakes."
    )
    e["drift_analysis"] = (
        f"Checks if your portfolio has drifted from ideal balance. With {top_sector_name} at {top_sector_pct:.1f}%, "
        f"this compares your allocation against the Nifty 50 benchmark allocation. "
        f"Large drift means your portfolio has changed significantly from your original plan - time to rebalance."
    )
    e["overlap_detection"] = (
        f"Finds correlated or similar stocks in your {num_stocks} holdings. For example, having HDFC Bank, ICICI Bank, "
        f"SBI, and Kotak all at once means heavy banking overlap - they tend to move together. "
        f"Multiple similar stocks reduce the diversification benefit. "
        f"True diversification means stocks that don't move in the same direction at the same time."
    )
    e["return_attribution"] = (
        f"Breaks down your total {'profit' if total_gl >= 0 else 'loss'} of {_fmt(abs(total_gl))} - which stocks contributed how much? "
        f"Your biggest positive contributor is {top_name} ({_pct(top_return)}), "
        f"while {worst_name} ({_pct(worst_return)}) dragged performance. "
        f"This helps you understand whether your profit is coming from many stocks or just one lucky pick."
    )
    e["liquidity_risk"] = (
        f"Checks if any of your {num_stocks} stocks would be hard to sell quickly without affecting the price. "
        f"Large-cap stocks (like Reliance, TCS) are highly liquid - you can sell thousands of shares instantly. "
        f"Small-cap stocks might take days to sell if you have large positions. "
        f"Liquidity matters most when you urgently need cash or want to exit during a market crash."
    )
    e["tail_risk"] = (
        f"Measures the probability of extreme losses in your {_fmt(current_val)} portfolio. "
        f"In a severe market crash (like March 2020 COVID crash when markets fell 35%), how much could you lose? "
        f"This uses statistical methods (Value at Risk, Conditional VaR) to estimate worst-case scenarios. "
        f"Understanding tail risk helps you keep emergency reserves and avoid over-leveraging."
    )
    e["tax_impact"] = (
        f"Estimated taxes if you sold today: Short-term Capital Gains (STCG) at 15%: {_fmt(stcg)}, "
        f"Long-term Capital Gains (LTCG) at 10% above ₹1 lakh per year: {_fmt(ltcg)}. "
        f"Stocks held less than 1 year attract higher taxes (15% vs 10%). "
        f"Tax planning tip: If a stock is near 1-year holding, wait a few more days/weeks to save 5% in taxes. "
        f"You can also offset gains against losses to reduce your overall tax bill."
    )
    e["macro_sensitivity"] = (
        f"How your {num_stocks} stocks react to macroeconomic changes - interest rate changes by RBI, oil price movements, "
        f"rupee value fluctuation, inflation, GDP growth. "
        f"For example: Banking stocks benefit from rate cuts but suffer when rates rise. "
        f"IT stocks benefit from a weaker rupee (they earn in dollars). "
        f"FMCG stocks are relatively unaffected by most macro changes. "
        f"Understanding these sensitivities helps you prepare for different economic scenarios."
    )
    e["scenario_analysis"] = (
        f"Stress-tests your {_fmt(current_val)} portfolio under extreme conditions: "
        f"What if the market crashes 30%? What if interest rates spike by 2%? What if oil doubles? "
        f"Shows estimated portfolio value under each scenario. "
        f"This isn't about predicting the future - it's about understanding your worst-case exposure and ensuring "
        f"you can financially and emotionally handle those scenarios."
    )

    e["methodology_calculations"] = (
        f"This page explains every formula used to analyze your {num_stocks}-stock portfolio. "
        f"All calculations for your portfolio - from the {_pct(total_gl_pct)} return to risk metrics - "
        f"are explained with formulas here. Full transparency so you can verify any number yourself or share with your financial advisor."
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
