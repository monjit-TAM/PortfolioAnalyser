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
        total_inv = summary.get('total_investment', 0)
        current_val = summary.get('current_value', 0)
        gain_loss = summary.get('total_gain_loss', 0)
        gain_pct = summary.get('total_gain_loss_percentage', 0)
        
        context += "### Portfolio Summary\n"
        context += f"- **Total Investment:** ₹{total_inv:,.2f}\n"
        context += f"- **Current Value:** ₹{current_val:,.2f}\n"
        context += f"- **Total Gain/Loss:** ₹{gain_loss:,.2f} ({'+' if gain_loss >= 0 else ''}{gain_pct:.2f}%)\n"
        context += f"- **Number of Stocks:** {summary.get('number_of_stocks', 0)}\n"
        context += f"- **Profitable Stocks:** {summary.get('profitable_stocks', 0)}\n"
        context += f"- **Loss-making Stocks:** {summary.get('loss_making_stocks', 0)}\n\n"
    
    if 'stock_performance' in analysis_results:
        stocks = analysis_results['stock_performance']
        
        sorted_by_return = sorted(stocks, key=lambda x: x.get('Percentage Gain/Loss', 0), reverse=True)
        
        context += "### Individual Stock Performance (Sorted by Return)\n"
        context += "| Stock | Qty | Buy Price | Current Price | Investment | Current Value | Gain/Loss | Return % | Sector | Category |\n"
        context += "|-------|-----|-----------|---------------|------------|---------------|-----------|----------|--------|----------|\n"
        
        for stock in sorted_by_return:
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
        
        context += "\n**Top 3 Performers:** " + ", ".join([f"{s.get('Stock Name')} ({s.get('Percentage Gain/Loss', 0):+.1f}%)" for s in sorted_by_return[:3]]) + "\n"
        context += "**Bottom 3 Performers:** " + ", ".join([f"{s.get('Stock Name')} ({s.get('Percentage Gain/Loss', 0):+.1f}%)" for s in sorted_by_return[-3:]]) + "\n\n"
    
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
        context += "\n### Benchmark Comparison\n"
        port_ret = bench.get('portfolio_return', 0)
        nifty_ret = bench.get('nifty_return', 0)
        alpha = bench.get('alpha', port_ret - nifty_ret)
        context += f"- Portfolio Return: {port_ret:.2f}%\n"
        context += f"- NIFTY 50 Return: {nifty_ret:.2f}%\n"
        context += f"- Alpha (Outperformance): {alpha:+.2f}%\n"
        if alpha > 0:
            context += f"- Your portfolio is OUTPERFORMING the market by {alpha:.2f}%!\n"
        else:
            context += f"- Your portfolio is UNDERPERFORMING the market by {abs(alpha):.2f}%\n"
    
    return context

def get_system_prompt(portfolio_context):
    """Create system prompt for the AI assistant"""
    return f"""You are Alphalens AI, an expert Indian stock market financial advisor. You provide personalized, data-driven portfolio analysis and investment guidance.

## YOUR PORTFOLIO DATA
{portfolio_context}

## CORE CAPABILITIES

**1. Portfolio Performance Analysis**
- Explain overall returns, gains/losses with exact figures
- Identify best and worst performing stocks
- Calculate weighted returns and portfolio metrics

**2. Individual Stock Analysis**
- Discuss specific stock performance using actual data
- Explain why certain stocks are outperforming/underperforming
- Provide price movements and percentage changes

**3. Sector & Category Analysis**
- Analyze sector allocation and concentration
- Explain Large/Mid/Small cap distribution
- Identify overweight/underweight sectors

**4. Investment Recommendations**
- Explain BUY/HOLD/SELL signals with rationale
- Distinguish between Value and Growth perspectives
- Suggest portfolio improvements

**5. Benchmark Comparisons**
- Compare against NIFTY 50, Sensex
- Explain alpha generation
- Contextualize performance

**6. Risk Assessment**
- Identify concentration risks
- Suggest diversification strategies
- Highlight volatile holdings

## RESPONSE GUIDELINES

1. **BE SPECIFIC**: Always use exact stock names and numbers from the data
   - GOOD: "Your RELIANCE investment of ₹1,81,100 is now worth ₹1,65,890, a loss of ₹15,210 (-8.4%)"
   - BAD: "Your technology stocks are performing well"

2. **BE ACTIONABLE**: Give clear, practical advice
   - GOOD: "Consider reducing your Banking sector exposure from 35% to 25%"
   - BAD: "You might want to rebalance"

3. **BE CONCISE**: Answer questions directly, then elaborate

4. **USE RUPEE (₹)**: All currency values in Indian Rupees

5. **ACKNOWLEDGE LIMITATIONS**: If asked about stocks not in the portfolio, say so

6. **DISCLAIMER**: End significant advice with "This is for educational purposes. Consult a financial advisor for personalized advice."

## EXAMPLE RESPONSES

Q: "How is my portfolio doing?"
A: "Your portfolio of 11 stocks has a total investment of ₹19,16,155 with a current value of ₹23,88,247 - a gain of ₹4,72,092 (+24.6%). Your top performer is OLECTRA at +105.3%, while RELIANCE is your only significant loss at -8.4%. Overall, you're outperforming NIFTY 50 by approximately X%."

Q: "Which stock should I sell?"
A: "Based on the analysis, RELIANCE shows a loss of -8.4% and is recommended as HOLD from value perspective but may be considered for review. However, the recommendations suggest holding most positions. The rebalancing suggestions indicate reducing exposure to overweight sectors like Banking if above 30%."

Now respond to user questions using the actual portfolio data above. Be helpful, specific, and data-driven."""

def chat_with_assistant(user_message, analysis_results, portfolio_data, chat_history=None):
    """Send a message to the AI assistant and get a response"""
    try:
        recommendations = st.session_state.get('recommendations', None)
        portfolio_context = get_portfolio_context(analysis_results, portfolio_data, recommendations)
        system_prompt = get_system_prompt(portfolio_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-6:]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2000,
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"AI Assistant error: {e}")
        return f"I apologize, but I'm having trouble processing your request. Please try again. Error: {str(e)}"

def get_quick_insights(analysis_results, recommendations=None):
    """Generate quick insights about the portfolio"""
    try:
        portfolio_context = get_portfolio_context(analysis_results, None, recommendations)
        
        prompt = """Provide 4 key insights about this portfolio in bullet points:
1. Overall performance summary (use exact ₹ values and %)
2. Top 2 performers and bottom 2 performers by name
3. Main risk or concern
4. One specific actionable recommendation

Keep each point to 1-2 sentences with real numbers."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a concise financial analyst. Analyze:\n\n{portfolio_context}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Quick insights error: {e}")
        return None
