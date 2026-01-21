import os
import streamlit as st
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

def get_portfolio_context(analysis_results, portfolio_data, recommendations=None):
    """Build comprehensive context from portfolio analysis for the AI assistant"""
    context = "## Portfolio Analysis Data\n\n"
    
    if not analysis_results:
        return "No portfolio analysis data available."
    
    if 'portfolio_summary' in analysis_results:
        summary = analysis_results['portfolio_summary']
        context += "### Portfolio Summary\n"
        context += f"- **Total Investment:** ₹{summary.get('total_investment', 0):,.2f}\n"
        context += f"- **Current Value:** ₹{summary.get('current_value', 0):,.2f}\n"
        context += f"- **Total Gain/Loss:** ₹{summary.get('total_gain_loss', 0):,.2f}\n"
        context += f"- **Total Return Percentage:** {summary.get('total_gain_loss_percentage', 0):.2f}%\n"
        context += f"- **Number of Stocks:** {summary.get('number_of_stocks', 0)}\n"
        context += f"- **Profitable Stocks:** {summary.get('profitable_stocks', 0)}\n"
        context += f"- **Loss-making Stocks:** {summary.get('loss_making_stocks', 0)}\n\n"
    
    if 'stock_performance' in analysis_results:
        context += "### Individual Stock Performance\n"
        context += "| Stock | Qty | Buy Price | Current Price | Investment | Current Value | Gain/Loss | Return % | Sector | Category |\n"
        context += "|-------|-----|-----------|---------------|------------|---------------|-----------|----------|--------|----------|\n"
        
        for stock in analysis_results['stock_performance']:
            name = stock.get('Stock Name', 'Unknown')
            qty = stock.get('Quantity', 0)
            buy_price = stock.get('Buy Price', 0)
            current_price = stock.get('Current Price', 0)
            investment = stock.get('Investment Value', 0)
            current_val = stock.get('Current Value', 0)
            gain_loss = stock.get('Absolute Gain/Loss', 0)
            gain_pct = stock.get('Percentage Gain/Loss', 0)
            sector = stock.get('Sector', 'Unknown')
            category = stock.get('Category', 'Unknown')
            
            context += f"| {name} | {qty} | ₹{buy_price:,.2f} | ₹{current_price:,.2f} | ₹{investment:,.2f} | ₹{current_val:,.2f} | ₹{gain_loss:,.2f} | {gain_pct:+.2f}% | {sector} | {category} |\n"
        context += "\n"
    
    if 'sector_analysis' in analysis_results:
        context += "### Sector Allocation\n"
        context += "| Sector | Investment | Current Value | Gain/Loss | Stocks | Portfolio % | Sector Return % |\n"
        context += "|--------|------------|---------------|-----------|--------|-------------|------------------|\n"
        
        for sector in analysis_results['sector_analysis']:
            sector_name = sector.get('Sector', 'Unknown')
            investment = sector.get('Investment Value', 0)
            current_val = sector.get('Current Value', 0)
            gain_loss = sector.get('Absolute Gain/Loss', 0)
            num_stocks = sector.get('Number of Stocks', 0)
            pct_portfolio = sector.get('Percentage of Portfolio', 0)
            sector_return = sector.get('Sector Return %', 0)
            
            context += f"| {sector_name} | ₹{investment:,.2f} | ₹{current_val:,.2f} | ₹{gain_loss:,.2f} | {num_stocks} | {pct_portfolio:.1f}% | {sector_return:+.2f}% |\n"
        context += "\n"
    
    if 'category_analysis' in analysis_results:
        context += "### Market Cap Category Analysis\n"
        context += "| Category | Investment | Current Value | Gain/Loss | Stocks | Portfolio % | Category Return % |\n"
        context += "|----------|------------|---------------|-----------|--------|-------------|--------------------|\n"
        
        for cat in analysis_results['category_analysis']:
            cat_name = cat.get('Category', 'Unknown')
            investment = cat.get('Investment Value', 0)
            current_val = cat.get('Current Value', 0)
            gain_loss = cat.get('Absolute Gain/Loss', 0)
            num_stocks = cat.get('Number of Stocks', 0)
            pct_portfolio = cat.get('Percentage of Portfolio', 0)
            cat_return = cat.get('Category Return %', 0)
            
            context += f"| {cat_name} | ₹{investment:,.2f} | ₹{current_val:,.2f} | ₹{gain_loss:,.2f} | {num_stocks} | {pct_portfolio:.1f}% | {cat_return:+.2f}% |\n"
        context += "\n"
    
    if recommendations:
        context += "### Investment Recommendations\n"
        
        if 'value_recommendations' in recommendations:
            context += "\n**Value Investing Perspective:**\n"
            for rec in recommendations['value_recommendations']:
                stock = rec.get('stock', 'Unknown')
                action = rec.get('recommendation', 'HOLD')
                rationale = rec.get('rationale', '')
                context += f"- **{stock}**: {action} - {rationale}\n"
        
        if 'growth_recommendations' in recommendations:
            context += "\n**Growth Investing Perspective:**\n"
            for rec in recommendations['growth_recommendations']:
                stock = rec.get('stock', 'Unknown')
                action = rec.get('recommendation', 'HOLD')
                rationale = rec.get('rationale', '')
                context += f"- **{stock}**: {action} - {rationale}\n"
        
        if 'alternative_stocks' in recommendations:
            context += "\n**Alternative Stock Suggestions:**\n"
            for alt in recommendations['alternative_stocks'][:5]:
                context += f"- {alt.get('stock', 'Unknown')}: {alt.get('reason', '')}\n"
        
        if 'rebalancing_suggestions' in recommendations:
            context += "\n**Rebalancing Suggestions:**\n"
            for suggestion in recommendations['rebalancing_suggestions']:
                context += f"- {suggestion}\n"
    
    if 'benchmark_comparison' in analysis_results:
        bench = analysis_results['benchmark_comparison']
        context += "### Benchmark Comparison\n"
        context += f"- Portfolio Return: {bench.get('portfolio_return', 0):.2f}%\n"
        context += f"- NIFTY 50 Return: {bench.get('nifty_return', 0):.2f}%\n"
        context += f"- Alpha (Outperformance): {bench.get('alpha', 0):.2f}%\n\n"
    
    return context

def get_system_prompt(portfolio_context):
    """Create system prompt for the AI assistant"""
    return f"""You are Alphalens AI, an expert financial advisor assistant for Indian stock market portfolio analysis. You help investors understand their portfolio performance and make informed decisions.

You have access to the user's complete portfolio analysis data below. Use this SPECIFIC information to answer their questions accurately with real numbers and stock names from their portfolio.

{portfolio_context}

## Your Capabilities:
1. **Metrics Explanation:** Explain portfolio metrics like total investment, current value, gains/losses, return percentages, and what they mean.
2. **Stock Analysis:** Discuss individual stock performance - which stocks are performing well, which are underperforming, and why.
3. **Sector Analysis:** Discuss sector allocation, which sectors are overweight/underweight, and sector-specific performance.
4. **Category Analysis:** Explain Large Cap, Mid Cap, Small Cap distribution and their performance.
5. **Recommendations:** Explain BUY/HOLD/SELL recommendations with clear rationale based on value and growth perspectives.
6. **Rebalancing:** Suggest how to improve portfolio allocation, reduce risk, and optimize returns.
7. **Benchmark Comparison:** Compare portfolio performance against NIFTY 50 and explain alpha/beta.

## IMPORTANT Guidelines:
- ALWAYS reference SPECIFIC stocks, numbers, and data from the portfolio above
- Use actual stock names like RELIANCE, TCS, INFY etc. from the user's portfolio
- Quote actual values: "Your RELIANCE investment of ₹X is now worth ₹Y, a gain of Z%"
- Always use Indian Rupee (₹) for currency values
- Be specific and data-driven, not generic
- If asked about a stock not in the portfolio, say so clearly
- Provide actionable, specific advice based on the actual portfolio data
- Keep responses informative but conversational
- Always remind users this is educational, not financial advice"""

def chat_with_assistant(user_message, analysis_results, portfolio_data, chat_history=None):
    """Send a message to the AI assistant and get a response"""
    try:
        recommendations = st.session_state.get('recommendations', None)
        portfolio_context = get_portfolio_context(analysis_results, portfolio_data, recommendations)
        system_prompt = get_system_prompt(portfolio_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"AI Assistant error: {e}")
        return f"I apologize, but I'm having trouble processing your request right now. Please try again in a moment. Error: {str(e)}"

def get_quick_insights(analysis_results):
    """Generate quick insights about the portfolio"""
    try:
        portfolio_context = get_portfolio_context(analysis_results, None)
        
        prompt = """Based on the portfolio analysis above, provide 3-4 key insights in bullet points:
1. Overall portfolio health assessment with specific numbers
2. Top performing and underperforming stocks by name
3. Key risk factors or concerns
4. One specific actionable recommendation

Keep each point brief but include actual stock names and numbers."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a concise financial analyst. Analyze this portfolio:\n\n{portfolio_context}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Quick insights error: {e}")
        return None
