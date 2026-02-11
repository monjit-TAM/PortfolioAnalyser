PAGE_EXPLANATIONS = {
    "dashboard": {
        "title": "Dashboard - Executive Summary",
        "icon": "📊",
        "summary": "This is your portfolio's report card. It gives you a quick snapshot of how your investments are doing overall.",
        "metrics": [
            {
                "name": "Portfolio Health Score",
                "explanation": "Think of this like a health check-up score for your investments. A score above 75 means your portfolio is in good shape. Below 50 means it needs attention. It considers how well-spread your investments are, how risky they are, and how well they're performing."
            },
            {
                "name": "Total Investment",
                "explanation": "This is the total amount of money you originally put into buying all your stocks. It's your starting point - the money you spent to buy shares."
            },
            {
                "name": "Current Value",
                "explanation": "This is what all your stocks are worth right now if you were to sell them today. If this is higher than your Total Investment, you're making profit. If lower, you're at a loss."
            },
            {
                "name": "Total Gain/Loss",
                "explanation": "Simply put, this is your profit or loss. It's the difference between what your stocks are worth now versus what you paid for them. Green means profit, red means loss."
            },
            {
                "name": "Return Percentage",
                "explanation": "This tells you the percentage of profit or loss on your investment. For example, if you invested ₹1,00,000 and it's now worth ₹1,20,000, your return is +20%. It helps you compare whether your stocks did better or worse than keeping money in a bank fixed deposit."
            },
            {
                "name": "Stock Performance Table",
                "explanation": "This table shows each stock you own with its buy price, current price, and how much profit or loss it has made. It helps you see which stocks are winners and which ones are dragging your portfolio down."
            }
        ]
    },
    "sectors": {
        "title": "Sectors - Industry Breakdown",
        "icon": "🏭",
        "summary": "This page shows how your money is spread across different industries like IT, Banking, Pharma, etc. A well-balanced portfolio shouldn't have too much money in one industry.",
        "metrics": [
            {
                "name": "Sector Allocation Pie Chart",
                "explanation": "This pie chart shows what percentage of your money is in each industry. For example, if 50% is in IT stocks, you're heavily dependent on the tech sector. Ideally, no single sector should be more than 25-30% of your portfolio."
            },
            {
                "name": "Sector Performance",
                "explanation": "This shows how each industry group in your portfolio has performed. It helps you see which sectors are making money and which are losing. If Banking stocks are all losing, it might be a sector-wide problem, not just your stock picks."
            },
            {
                "name": "Sector Diversification Score",
                "explanation": "This score tells you how well-spread your investments are across industries. A high score means good diversification - your money is spread well. A low score means your money is concentrated in few sectors, which is risky."
            }
        ]
    },
    "stocks": {
        "title": "Stocks - Individual Performance",
        "icon": "📈",
        "summary": "This page gives you a detailed look at how each individual stock in your portfolio is performing. It's like a progress report for each of your investments.",
        "metrics": [
            {
                "name": "Stock-wise Returns",
                "explanation": "Shows the profit or loss for each stock separately. A stock showing +50% means it has grown by half since you bought it. A stock showing -20% means it has lost one-fifth of its value."
            },
            {
                "name": "Price Chart",
                "explanation": "This chart shows how your stock's price has moved over time since you bought it. An upward line is good (price going up), a downward line means the price has been falling."
            },
            {
                "name": "Investment vs Current Value",
                "explanation": "For each stock, this compares what you paid versus what it's worth now. Green bars above the line mean profit, red bars below mean loss. It instantly shows your winners and losers."
            }
        ]
    },
    "benchmark": {
        "title": "Benchmark - Market Comparison",
        "icon": "📊",
        "summary": "This page compares your portfolio's performance against major market indices like Nifty 50 and Sensex. It answers the question: 'Am I doing better or worse than the market?'",
        "metrics": [
            {
                "name": "Portfolio vs Nifty 50",
                "explanation": "Nifty 50 represents the top 50 companies in India. If your portfolio returned +15% but Nifty gave +20%, it means you would have been better off just buying a Nifty index fund. This comparison helps you judge if your stock picking is adding value."
            },
            {
                "name": "Portfolio vs Sensex",
                "explanation": "Sensex tracks the top 30 companies on BSE. Like Nifty comparison, this tells you if your stock selection is beating the market average or not."
            },
            {
                "name": "Alpha",
                "explanation": "Alpha measures your extra returns above the market. Positive alpha means you're earning MORE than the market - your stock picking is working! Negative alpha means you're underperforming the market."
            },
            {
                "name": "Beta",
                "explanation": "Beta measures how much your portfolio swings compared to the market. Beta = 1 means your portfolio moves exactly like the market. Beta > 1 means more ups and downs (riskier). Beta < 1 means steadier than the market (less risky)."
            }
        ]
    },
    "advice": {
        "title": "Advice - Investment Recommendations",
        "icon": "💡",
        "summary": "This page gives you actionable suggestions for each stock - whether to Buy more, Hold, or Sell. It looks at each stock from two perspectives: Value investing (like Warren Buffett) and Growth investing.",
        "metrics": [
            {
                "name": "Value Analysis",
                "explanation": "Value investing looks at whether a stock is cheap or expensive compared to its true worth. Think of it like bargain shopping - is the stock currently at a 'sale price' or is it overpriced? It checks things like P/E ratio (price compared to earnings) and dividend yield."
            },
            {
                "name": "Growth Analysis",
                "explanation": "Growth investing looks at whether a company is growing fast - its revenue is increasing, profits are going up, and the business is expanding. Fast-growing companies can give big returns even if they seem expensive today."
            },
            {
                "name": "BUY / HOLD / SELL Rating",
                "explanation": "BUY means the stock looks good and you might want to add more. HOLD means keep what you have but don't buy more. SELL means the stock isn't performing well and you should consider selling it to invest the money elsewhere."
            },
            {
                "name": "Alternative Suggestions",
                "explanation": "When a stock gets a SELL rating, we suggest better alternatives in the same sector. For example, if a banking stock is underperforming, we might suggest a stronger bank stock to replace it with."
            }
        ]
    },
    "rebalance": {
        "title": "Rebalance - Portfolio Adjustment",
        "icon": "⚖️",
        "summary": "This page tells you how to adjust your portfolio for better balance. Over time, some stocks grow more than others, making your portfolio uneven. Rebalancing means fixing this to reduce risk.",
        "metrics": [
            {
                "name": "Overweight Positions",
                "explanation": "These are stocks that have become too large a portion of your portfolio. Like having too many eggs in one basket - if that stock falls, it will hurt your whole portfolio a lot. The suggestion is to sell some of these and spread the money."
            },
            {
                "name": "Underweight Positions",
                "explanation": "These are stocks or sectors where you have too little investment. Adding more here would improve your portfolio's balance and reduce risk."
            },
            {
                "name": "Concentration Alerts",
                "explanation": "These are warnings when any single stock or sector takes up too much of your portfolio. A general rule is no single stock should be more than 10-15% of your total portfolio, and no sector more than 25-30%."
            }
        ]
    },
    "history": {
        "title": "History - Performance Over Time",
        "icon": "📅",
        "summary": "This page shows how your portfolio value has changed over time. It helps you understand your investment journey - the ups and downs along the way.",
        "metrics": [
            {
                "name": "Portfolio Value Over Time",
                "explanation": "This chart tracks your portfolio's total value from when you first invested to today. The line going up means your investments are growing. Dips are normal and happen to everyone - what matters is the overall upward trend."
            },
            {
                "name": "Monthly/Yearly Returns",
                "explanation": "This breaks down your returns by time period. You can see which months or years were good and which were bad. It helps you understand patterns - for example, markets often dip during certain events but recover later."
            }
        ]
    },
    "profile": {
        "title": "Profile - Investor Profile",
        "icon": "👤",
        "summary": "This page analyzes your investing style and behavior based on your portfolio. It tells you what kind of investor you are and whether your approach matches your goals.",
        "metrics": [
            {
                "name": "Investor Type",
                "explanation": "Based on your stock choices, this tells you if you're an aggressive investor (taking big risks for big returns), conservative investor (preferring safety), or somewhere in between. Knowing your style helps you make better decisions."
            },
            {
                "name": "Risk Tolerance",
                "explanation": "This measures how much risk your portfolio is taking. High risk means bigger potential gains but also bigger potential losses. If you're close to retirement, you might want lower risk. If you're young, you can afford more risk."
            },
            {
                "name": "Holding Period",
                "explanation": "This shows how long you typically hold your stocks. Long-term holding (1+ years) usually means you're a patient investor, which historically gives better returns and lower taxes. Short-term trading means higher taxes and more transaction costs."
            }
        ]
    },
    "advanced": {
        "title": "Advanced - Deep Analysis",
        "icon": "🔬",
        "summary": "This page provides professional-grade analysis with 15 different types of deep checks on your portfolio. Think of it as a complete medical check-up for your investments.",
        "metrics": [
            {
                "name": "Health Score",
                "explanation": "An overall score out of 100 that considers everything - diversification, risk, returns, and more. Like a fitness score for your portfolio. Above 75 is healthy, 50-75 needs some attention, below 50 needs major changes."
            },
            {
                "name": "Risk Radar",
                "explanation": "A spider/radar chart that shows 8 different types of risk in your portfolio. It helps you see at a glance which areas are risky and which are safe. Each spoke of the chart represents a different risk factor."
            },
            {
                "name": "Structural Diagnostics",
                "explanation": "Shows how your money is spread across large companies (safer), medium companies, and small companies (riskier). A good mix of all three types usually works best."
            },
            {
                "name": "Style Analysis",
                "explanation": "Tells you if your portfolio leans towards 'Value' stocks (established companies at reasonable prices) or 'Growth' stocks (fast-growing companies). Neither is wrong - it's about knowing your style."
            },
            {
                "name": "Concentration Risk",
                "explanation": "Measures whether too much of your money is in just a few stocks. If your top 3 stocks make up 60%+ of your portfolio, that's risky because if even one of them falls sharply, your whole portfolio suffers."
            },
            {
                "name": "Volatility & Drawdown",
                "explanation": "Measures how much your portfolio value bounces up and down. High volatility means big swings (stressful but potentially rewarding). Drawdown shows the biggest drop from a peak - how much you could lose in a bad period."
            },
            {
                "name": "Behavior Analysis",
                "explanation": "Analyzes your investing habits - are you buying and selling too frequently? Are you holding losing stocks too long hoping they'll recover? Are you selling winners too early? These are common mistakes this section helps you identify."
            },
            {
                "name": "Drift Analysis",
                "explanation": "Checks if your portfolio has drifted away from a balanced position over time. Stocks that grow a lot can make your portfolio unbalanced. This shows how far you've drifted from an ideal allocation."
            },
            {
                "name": "Overlap Detection",
                "explanation": "Finds stocks in your portfolio that are very similar to each other. For example, having both HDFC Bank and ICICI Bank means you're 'doubling up' on banking. This reduces the benefit of diversification."
            },
            {
                "name": "Return Attribution",
                "explanation": "Breaks down exactly where your profits and losses came from. Which stocks contributed most to your gains? Which stocks pulled your portfolio down? This helps you understand what's really driving your returns."
            },
            {
                "name": "Liquidity Risk",
                "explanation": "Checks if any of your stocks are hard to sell quickly. Stocks with low trading volume can be difficult to sell at a fair price when you need the money. This is especially important for small-cap stocks."
            },
            {
                "name": "Tail Risk",
                "explanation": "Measures the chance of extreme losses - rare but devastating events. Think of it as preparing for a 'worst case scenario'. Portfolios with high tail risk could lose a lot in market crashes."
            },
            {
                "name": "Tax Impact",
                "explanation": "Shows how much tax you'll pay on your gains. In India, stocks held less than 1 year have higher taxes (Short Term Capital Gains at 15%) compared to stocks held over 1 year (Long Term Capital Gains at 10% above ₹1 lakh). This helps you plan when to sell."
            },
            {
                "name": "Macro Sensitivity",
                "explanation": "Shows how your portfolio might be affected by big economic changes like interest rate hikes, oil price changes, or rupee weakness. Helps you prepare for economic shifts."
            },
            {
                "name": "Scenario Analysis",
                "explanation": "Tests your portfolio against worst-case scenarios - what happens if the market crashes 30%? What if interest rates spike? This stress test shows how resilient your portfolio is in tough times."
            }
        ]
    },
    "methodology": {
        "title": "Methodology - How We Calculate",
        "icon": "📐",
        "summary": "This page explains the mathematical methods and formulas we use for all calculations. It's provided for transparency so you can trust and verify our analysis.",
        "metrics": [
            {
                "name": "Calculation Methods",
                "explanation": "We explain every formula used - from simple return calculations to complex risk metrics. This ensures complete transparency. You can verify our calculations or share them with your financial advisor."
            }
        ]
    }
}

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

def get_page_explanation(page_key):
    return PAGE_EXPLANATIONS.get(page_key, {})

_translation_cache = {}

def translate_text(text, target_lang_code):
    if target_lang_code == "en":
        return text
    
    cache_key = f"{target_lang_code}:{text[:100]}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        import os
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        )
        
        lang_names = {v: k.split(" (")[0] if " (" in k else k for k, v in SUPPORTED_LANGUAGES.items()}
        lang_name = lang_names.get(target_lang_code, "Hindi")
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text to {lang_name}. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio' in English. Keep currency symbol ₹ as is. Provide only the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            max_completion_tokens=2000
        )
        translated = response.choices[0].message.content.strip()
        _translation_cache[cache_key] = translated
        return translated
    except Exception as e:
        return text

def get_translated_explanation(page_key, lang_code="en"):
    explanation = get_page_explanation(page_key)
    if not explanation or lang_code == "en":
        return explanation
    
    batch_cache_key = f"batch:{lang_code}:{page_key}"
    if batch_cache_key in _translation_cache:
        return _translation_cache[batch_cache_key]
    
    try:
        import os, json
        from openai import OpenAI
        
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
                {"role": "system", "content": f"Translate the following texts to {lang_name}. Each text is separated by '---SEPARATOR---'. Keep the separator in your output. Keep financial terms like 'Nifty 50', 'Sensex', 'P/E ratio', 'Alpha', 'Beta', 'Sharpe ratio' in English. Keep currency symbol ₹ as is. Provide only the translations with separators, nothing else."},
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

def render_page_explainer(page_key, lang_code="en"):
    import streamlit as st
    
    explanation = get_translated_explanation(page_key, lang_code)
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
    
    return SUPPORTED_LANGUAGES[lang]
