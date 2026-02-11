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


def generate_dynamic_explanation(page_key, analysis_results=None, advanced_metrics=None, recommendations=None):
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

    if stock_perf:
        try:
            perf_df = pd.DataFrame(stock_perf) if not isinstance(stock_perf, pd.DataFrame) else stock_perf
            if 'Gain/Loss %' in perf_df.columns:
                top_stock = perf_df.loc[perf_df['Gain/Loss %'].idxmax()]
                worst_stock = perf_df.loc[perf_df['Gain/Loss %'].idxmin()]
                top_name = top_stock.get('Stock Name', 'N/A')
                top_return = top_stock.get('Gain/Loss %', 0)
                worst_name = worst_stock.get('Stock Name', 'N/A')
                worst_return = worst_stock.get('Gain/Loss %', 0)
            else:
                top_name = worst_name = "N/A"
                top_return = worst_return = 0
        except:
            top_name = worst_name = "N/A"
            top_return = worst_return = 0
    else:
        top_name = worst_name = "N/A"
        top_return = worst_return = 0

    if sector_data:
        try:
            sec_df = pd.DataFrame(sector_data) if not isinstance(sector_data, pd.DataFrame) else sector_data
            if not sec_df.empty and 'Percentage of Portfolio' in sec_df.columns:
                top_sector = sec_df.loc[sec_df['Percentage of Portfolio'].idxmax()]
                top_sector_name = top_sector.get('Sector', 'N/A')
                top_sector_pct = top_sector.get('Percentage of Portfolio', 0)
                num_sectors = len(sec_df)
            else:
                top_sector_name = "N/A"
                top_sector_pct = 0
                num_sectors = 0
        except:
            top_sector_name = "N/A"
            top_sector_pct = 0
            num_sectors = 0
    else:
        top_sector_name = "N/A"
        top_sector_pct = 0
        num_sectors = 0

    profit_or_loss = "profit" if total_gl >= 0 else "loss"
    gain_word = "gained" if total_gl >= 0 else "lost"

    if page_key == "dashboard":
        return {
            "title": "Dashboard - Executive Summary",
            "icon": "📊",
            "summary": f"Your portfolio of {num_stocks} stocks has a total investment of {_fmt(total_inv)} and is currently worth {_fmt(current_val)}. "
                       f"You have {gain_word} {_fmt(abs(total_gl))} ({_pct(total_gl_pct)}). "
                       f"{profitable} out of {num_stocks} stocks are in profit.",
            "metrics": [
                {
                    "name": "Portfolio Health Score",
                    "explanation": f"Your portfolio health score considers diversification across {num_sectors} sectors, "
                                   f"your {_pct(total_gl_pct)} return, and your win rate of {profitable}/{num_stocks} stocks in profit. "
                                   f"A score above 75 means your portfolio is in good shape, below 50 means it needs attention."
                },
                {
                    "name": "Total Investment",
                    "explanation": f"You originally invested {_fmt(total_inv)} across {num_stocks} stocks. "
                                   f"This is the total money you spent to buy all your shares."
                },
                {
                    "name": "Current Value",
                    "explanation": f"Your stocks are currently worth {_fmt(current_val)}. "
                                   + (f"This is {_fmt(abs(current_val - total_inv))} MORE than what you invested - you're in profit!"
                                      if current_val >= total_inv else
                                      f"This is {_fmt(abs(total_inv - current_val))} LESS than what you invested - you're at a loss.")
                },
                {
                    "name": "Total Gain/Loss",
                    "explanation": f"You have {gain_word} {_fmt(abs(total_gl))} overall ({_pct(total_gl_pct)}). "
                                   f"Your best performer is {top_name} at {_pct(top_return)}, and your weakest stock is {worst_name} at {_pct(worst_return)}."
                },
                {
                    "name": "Return Percentage",
                    "explanation": f"Your overall portfolio return is {_pct(total_gl_pct)}. "
                                   + (f"For comparison, a bank fixed deposit typically gives 6-7% per year. "
                                      f"Your portfolio is {'outperforming' if total_gl_pct > 7 else 'underperforming compared to'} a simple FD."
                                      if total_gl_pct != 0 else "Upload portfolio to see your returns.")
                },
                {
                    "name": "Stock Performance Table",
                    "explanation": f"This table shows all {num_stocks} stocks with their buy price, current price, and individual gains/losses. "
                                   f"Currently {profitable} stocks are making money and {loss_making} stocks are in loss. "
                                   f"Look for {worst_name} ({_pct(worst_return)}) - it may need your attention."
                }
            ]
        }

    elif page_key == "sectors":
        sector_summary_parts = []
        if sector_data:
            try:
                sec_df = pd.DataFrame(sector_data) if not isinstance(sector_data, pd.DataFrame) else sector_data
                for _, row in sec_df.head(3).iterrows():
                    sector_summary_parts.append(f"{row.get('Sector', 'Unknown')} ({row.get('Percentage of Portfolio', 0):.1f}%)")
            except:
                pass
        top_3_text = ", ".join(sector_summary_parts) if sector_summary_parts else "your various sectors"

        return {
            "title": "Sectors - Industry Breakdown",
            "icon": "🏭",
            "summary": f"Your money is spread across {num_sectors} sectors. Your largest sector is {top_sector_name} "
                       f"at {top_sector_pct:.1f}% of your portfolio. Top sectors: {top_3_text}. "
                       + ("This sector has too much concentration (above 30%). Consider diversifying." if top_sector_pct > 30 else
                          "Your sector allocation looks reasonably balanced."),
            "metrics": [
                {
                    "name": "Sector Allocation Pie Chart",
                    "explanation": f"Your portfolio is spread across {num_sectors} sectors. {top_sector_name} is your largest at {top_sector_pct:.1f}%. "
                                   f"Ideally, no single sector should be more than 25-30%. "
                                   + (f"Your {top_sector_name} allocation is high - if this sector faces problems, a large part of your portfolio could be affected."
                                      if top_sector_pct > 30 else
                                      f"Your allocation looks well-distributed across sectors.")
                },
                {
                    "name": "Sector Performance",
                    "explanation": f"This shows returns for each of your {num_sectors} sectors. "
                                   f"If an entire sector is losing, it's likely a market-wide issue, not just your stock picks."
                },
                {
                    "name": "Sector Diversification Score",
                    "explanation": f"With {num_sectors} sectors and {num_stocks} stocks, this score measures how well-spread your investments are. "
                                   f"More sectors generally means better diversification and lower risk."
                }
            ]
        }

    elif page_key == "stocks":
        return {
            "title": "Stocks - Individual Performance",
            "icon": "📈",
            "summary": f"Here's how each of your {num_stocks} stocks is performing individually. "
                       f"Your star performer is {top_name} ({_pct(top_return)}) "
                       f"and your weakest is {worst_name} ({_pct(worst_return)}).",
            "metrics": [
                {
                    "name": "Stock-wise Returns",
                    "explanation": f"Your best stock {top_name} has returned {_pct(top_return)}, while {worst_name} has returned {_pct(worst_return)}. "
                                   f"Out of {num_stocks} stocks, {profitable} are in profit and {loss_making} are in loss."
                },
                {
                    "name": "Price Chart",
                    "explanation": f"These charts show how each stock's price has moved since you bought it. An upward trend is good. "
                                   f"Compare your stocks' price movements to see which ones have been steadily growing."
                },
                {
                    "name": "Investment vs Current Value",
                    "explanation": f"For each stock, this compares what you paid versus what it's worth now. "
                                   f"Green bars mean profit, red bars mean loss. "
                                   f"Your total investment of {_fmt(total_inv)} is now worth {_fmt(current_val)}."
                }
            ]
        }

    elif page_key == "benchmark":
        return {
            "title": "Benchmark - Market Comparison",
            "icon": "📊",
            "summary": f"Your portfolio returned {_pct(total_gl_pct)} overall. This page compares that against Nifty 50 and Sensex "
                       f"to answer: 'Did your stock picking add value, or would a simple index fund have been better?'",
            "metrics": [
                {
                    "name": "Portfolio vs Nifty 50",
                    "explanation": f"Your portfolio's {_pct(total_gl_pct)} return is compared against Nifty 50 (top 50 Indian companies). "
                                   f"If Nifty beat your return, you might have been better off with a Nifty index fund, which is also less effort."
                },
                {
                    "name": "Portfolio vs Sensex",
                    "explanation": f"Sensex tracks the top 30 companies on BSE. Like the Nifty comparison, this tells you if your stock selection "
                                   f"is adding value compared to the market average."
                },
                {
                    "name": "Alpha",
                    "explanation": f"Alpha measures your EXTRA returns above the market. With your {_pct(total_gl_pct)} return, "
                                   f"positive Alpha means your stock picking is working - you're earning more than the market. "
                                   f"Negative Alpha means you'd be better off with an index fund."
                },
                {
                    "name": "Beta",
                    "explanation": f"Beta measures how much your portfolio swings compared to the market. "
                                   f"Beta = 1 means your {num_stocks} stocks move exactly like the market. "
                                   f"Beta > 1 means more ups and downs (riskier). Beta < 1 means steadier (less risky)."
                }
            ]
        }

    elif page_key == "advice":
        return {
            "title": "Advice - Investment Recommendations",
            "icon": "💡",
            "summary": f"Based on your {num_stocks} stocks, this page gives specific Buy/Hold/Sell advice. "
                       f"With {loss_making} stocks currently in loss, pay special attention to SELL recommendations to cut losses early.",
            "metrics": [
                {
                    "name": "Value Analysis",
                    "explanation": f"Checks if each of your {num_stocks} stocks is cheap or expensive compared to its true worth. "
                                   f"Like bargain shopping - is the stock at a 'sale price' or overpriced? "
                                   f"It looks at P/E ratio, dividend yield, and fundamentals."
                },
                {
                    "name": "Growth Analysis",
                    "explanation": f"Checks if your stocks' companies are growing fast - revenue increasing, profits rising, business expanding. "
                                   f"Fast-growing companies can give big returns even if they seem expensive today."
                },
                {
                    "name": "BUY / HOLD / SELL Rating",
                    "explanation": f"Each of your {num_stocks} stocks gets a specific rating. "
                                   f"BUY = add more shares. HOLD = keep what you have. "
                                   f"SELL = consider selling and reinvesting the money better. "
                                   f"Pay attention to your worst performer {worst_name} ({_pct(worst_return)})."
                },
                {
                    "name": "Alternative Suggestions",
                    "explanation": f"For stocks rated SELL, we suggest stronger alternatives in the same sector. "
                                   f"For example, if {worst_name} gets a SELL rating, we'll suggest better options in its sector."
                }
            ]
        }

    elif page_key == "rebalance":
        return {
            "title": "Rebalance - Portfolio Adjustment",
            "icon": "⚖️",
            "summary": f"Your portfolio of {num_stocks} stocks across {num_sectors} sectors may have drifted from an ideal balance. "
                       f"This page shows which positions are too large or too small and how to fix them.",
            "metrics": [
                {
                    "name": "Overweight Positions",
                    "explanation": f"These are stocks that take up too much of your portfolio. "
                                   + (f"For example, if {top_name} has grown significantly ({_pct(top_return)}), "
                                      f"it may now be a disproportionately large chunk. Consider selling some to spread risk."
                                      if top_name != "N/A" else "Stocks that have grown a lot may need trimming.")
                },
                {
                    "name": "Underweight Positions",
                    "explanation": f"These are sectors or stocks where you have too little. With {_fmt(total_inv)} invested, "
                                   f"adding to underweight areas improves balance and reduces risk."
                },
                {
                    "name": "Concentration Alerts",
                    "explanation": f"Warnings when any single stock exceeds 10-15% of your {_fmt(current_val)} portfolio, "
                                   f"or any sector exceeds 25-30%. "
                                   + (f"Your biggest sector {top_sector_name} is at {top_sector_pct:.1f}%."
                                      if top_sector_name != "N/A" else "")
                }
            ]
        }

    elif page_key == "history":
        return {
            "title": "History - Performance Over Time",
            "icon": "📅",
            "summary": f"Track how your {_fmt(total_inv)} investment has changed over time. "
                       f"Currently at {_fmt(current_val)}, a {_pct(total_gl_pct)} change from your starting point.",
            "metrics": [
                {
                    "name": "Portfolio Value Over Time",
                    "explanation": f"This chart shows your journey from {_fmt(total_inv)} to {_fmt(current_val)}. "
                                   f"Dips along the way are normal - what matters is the overall direction. "
                                   f"Your portfolio has {gain_word} {_fmt(abs(total_gl))} in total."
                },
                {
                    "name": "Monthly/Yearly Returns",
                    "explanation": f"See which months were good and which were tough. With a {_pct(total_gl_pct)} overall return, "
                                   f"understanding timing helps you stay calm during temporary dips."
                }
            ]
        }

    elif page_key == "profile":
        win_rate = (profitable / num_stocks * 100) if num_stocks > 0 else 0
        return {
            "title": "Profile - Investor Profile",
            "icon": "👤",
            "summary": f"Based on your {num_stocks} stock picks, {win_rate:.0f}% win rate, and sector choices, "
                       f"this page tells you what kind of investor you are and whether your approach matches your goals.",
            "metrics": [
                {
                    "name": "Investor Type",
                    "explanation": f"With {num_stocks} stocks across {num_sectors} sectors and a {_pct(total_gl_pct)} return, "
                                   f"your investing style is classified as aggressive, moderate, or conservative. "
                                   f"Knowing this helps you make better decisions."
                },
                {
                    "name": "Risk Tolerance",
                    "explanation": f"Your portfolio's risk level is based on your stock choices and {_pct(total_gl_pct)} return. "
                                   f"High risk means bigger potential gains but also bigger losses. "
                                   f"If you're near retirement, lower risk is safer."
                },
                {
                    "name": "Holding Period",
                    "explanation": f"How long you typically hold stocks matters for taxes. Holding over 1 year means lower taxes (LTCG at 10%) "
                                   f"versus short-term (STCG at 15%). Longer holding also historically gives better returns."
                }
            ]
        }

    elif page_key == "advanced":
        adv = advanced_metrics or {}
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

        return {
            "title": "Advanced - Deep Analysis",
            "icon": "🔬",
            "summary": f"Professional-grade 15-layer analysis of your {num_stocks}-stock, {_fmt(current_val)} portfolio. "
                       f"Health Score: {health_val}/100 (Grade {health_grade}). "
                       f"This is a complete check-up covering risk, concentration, behavior, and more.",
            "metrics": [
                {
                    "name": "Health Score",
                    "explanation": f"Your portfolio scored {health_val}/100 (Grade {health_grade}). "
                                   + (f"Above 75 is healthy. " if isinstance(health_val, (int, float)) and health_val >= 75 else
                                      f"Below 75 means there's room for improvement. " if isinstance(health_val, (int, float)) else "")
                                   + f"It factors in your {_pct(total_gl_pct)} return, {num_sectors} sectors, and risk metrics."
                },
                {
                    "name": "Risk Radar",
                    "explanation": f"A spider chart showing 8 risk dimensions of your portfolio. "
                                   f"Each spoke shows a different risk type - the further out, the higher the risk. "
                                   f"Look for any spokes sticking out far - those need attention."
                },
                {
                    "name": "Structural Diagnostics",
                    "explanation": f"Shows how your {_fmt(current_val)} is split between Large Cap (safer), "
                                   f"Mid Cap, and Small Cap (riskier) stocks. A mix of all three usually works best for growth with manageable risk."
                },
                {
                    "name": "Style Analysis",
                    "explanation": f"Your {num_stocks} stocks are analyzed for Value vs Growth tilt. "
                                   f"Value means buying established companies at fair prices. Growth means betting on fast-growing businesses."
                },
                {
                    "name": "Concentration Risk",
                    "explanation": f"Your single largest stock holds {top1:.1f}% of your portfolio. "
                                   + (f"That's too concentrated (above 15%) - if it drops sharply, your whole portfolio takes a big hit."
                                      if top1 > 15 else f"This is within a reasonable range.")
                                   + f" Ideally, no single stock should exceed 10-15% of your {_fmt(current_val)} portfolio."
                },
                {
                    "name": "Volatility & Drawdown",
                    "explanation": f"Your portfolio's Sharpe ratio is {sharpe} (higher is better, above 1 is good). "
                                   f"Max drawdown was {max_dd:.1f}% - this is the biggest drop from a peak your portfolio experienced."
                },
                {
                    "name": "Behavior Analysis",
                    "explanation": f"Analyzes your investing habits. With {profitable} profitable and {loss_making} loss-making stocks, "
                                   f"are you holding losers too long hoping they'll recover? Are you selling winners too early? "
                                   f"These are common biases this section helps identify."
                },
                {
                    "name": "Drift Analysis",
                    "explanation": f"Checks if your portfolio has drifted from ideal balance. With {top_sector_name} at {top_sector_pct:.1f}%, "
                                   f"this compares your allocation against the Nifty 50 benchmark allocation."
                },
                {
                    "name": "Overlap Detection",
                    "explanation": f"Finds similar stocks in your {num_stocks} holdings. For example, having multiple banking stocks "
                                   f"reduces diversification benefit. This identifies which of your stocks overlap significantly."
                },
                {
                    "name": "Return Attribution",
                    "explanation": f"Your total {'profit' if total_gl >= 0 else 'loss'} of {_fmt(abs(total_gl))} - where did it come from? "
                                   f"Your biggest contributor is {top_name} ({_pct(top_return)}), "
                                   f"while {worst_name} ({_pct(worst_return)}) dragged performance."
                },
                {
                    "name": "Liquidity Risk",
                    "explanation": f"Checks if any of your {num_stocks} stocks would be hard to sell quickly. "
                                   f"Stocks with low trading volume can be hard to exit at a fair price when you need money urgently."
                },
                {
                    "name": "Tail Risk",
                    "explanation": f"Measures the chance of extreme losses in your {_fmt(current_val)} portfolio. "
                                   f"In a severe market crash (like 2020), how much could you lose? This prepares you for worst-case scenarios."
                },
                {
                    "name": "Tax Impact",
                    "explanation": f"Estimated taxes: Short-term (STCG at 15%): {_fmt(stcg)}, Long-term (LTCG at 10% above ₹1L): {_fmt(ltcg)}. "
                                   f"Stocks held less than 1 year attract higher taxes. Planning your sell timing can save you tax money."
                },
                {
                    "name": "Macro Sensitivity",
                    "explanation": f"How your {num_stocks} stocks react to economic changes - interest rates, oil prices, rupee value. "
                                   f"Helps you prepare if, for example, RBI raises interest rates or oil prices spike."
                },
                {
                    "name": "Scenario Analysis",
                    "explanation": f"Stress-tests your {_fmt(current_val)} portfolio: What if the market crashes 30%? "
                                   f"What if interest rates spike? Shows estimated portfolio value under each scenario."
                }
            ]
        }

    elif page_key == "methodology":
        return {
            "title": "Methodology - How We Calculate",
            "icon": "📐",
            "summary": f"This page explains every formula used to analyze your {num_stocks}-stock portfolio. "
                       f"Full transparency so you can verify calculations or share them with your financial advisor.",
            "metrics": [
                {
                    "name": "Calculation Methods",
                    "explanation": f"All calculations for your portfolio - from the {_pct(total_gl_pct)} return to risk metrics - "
                                   f"are explained with formulas here. You can verify any number yourself or share with your CA/advisor."
                }
            ]
        }

    return {
        "title": page_key.title(),
        "icon": "📊",
        "summary": "This section provides analysis of your portfolio.",
        "metrics": []
    }


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
                {"role": "system", "content": f"Translate the following text to {lang_name}. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio' in English. Keep currency symbol ₹ and all numbers as is. Provide only the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            max_completion_tokens=2000
        )
        translated = response.choices[0].message.content.strip()
        _translation_cache[cache_key] = translated
        return translated
    except Exception:
        return text


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
                {"role": "system", "content": f"Translate the following texts to {lang_name}. Each text is separated by '---SEPARATOR---'. Keep the separator in your output. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio', 'STCG', 'LTCG' in English. Keep currency symbol ₹ and all numbers as is. Provide only the translations with separators, nothing else."},
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
