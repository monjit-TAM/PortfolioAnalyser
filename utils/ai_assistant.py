import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

def get_portfolio_context(analysis_results, portfolio_data):
    """Build context from portfolio analysis for the AI assistant"""
    context = "## Portfolio Analysis Summary\n\n"
    
    if analysis_results:
        if 'summary' in analysis_results:
            summary = analysis_results['summary']
            context += f"**Total Investment:** ₹{summary.get('total_investment', 0):,.2f}\n"
            context += f"**Current Value:** ₹{summary.get('current_value', 0):,.2f}\n"
            context += f"**Total Return:** {summary.get('total_return_pct', 0):.2f}%\n"
            context += f"**Number of Stocks:** {summary.get('num_stocks', 0)}\n\n"
        
        if 'stocks' in analysis_results:
            context += "### Stock Performance\n"
            for stock in analysis_results['stocks'][:10]:
                name = stock.get('name', 'Unknown')
                gain_pct = stock.get('gain_pct', 0)
                recommendation = stock.get('recommendation', 'N/A')
                context += f"- **{name}**: {gain_pct:+.2f}% | Recommendation: {recommendation}\n"
            context += "\n"
        
        if 'sector_allocation' in analysis_results:
            context += "### Sector Allocation\n"
            for sector, pct in analysis_results['sector_allocation'].items():
                context += f"- {sector}: {pct:.1f}%\n"
            context += "\n"
        
        if 'benchmark_comparison' in analysis_results:
            bench = analysis_results['benchmark_comparison']
            context += "### Benchmark Comparison\n"
            context += f"- Portfolio Return: {bench.get('portfolio_return', 0):.2f}%\n"
            context += f"- NIFTY 50 Return: {bench.get('nifty_return', 0):.2f}%\n"
            context += f"- Alpha (Outperformance): {bench.get('alpha', 0):.2f}%\n\n"
        
        if 'recommendations' in analysis_results:
            context += "### Investment Recommendations\n"
            recs = analysis_results['recommendations']
            if 'value' in recs:
                context += f"**Value Perspective:** {recs['value']}\n"
            if 'growth' in recs:
                context += f"**Growth Perspective:** {recs['growth']}\n"
            context += "\n"
        
        if 'rebalancing' in analysis_results:
            context += "### Rebalancing Suggestions\n"
            for suggestion in analysis_results['rebalancing'][:5]:
                context += f"- {suggestion}\n"
            context += "\n"
    
    return context

def get_system_prompt(portfolio_context):
    """Create system prompt for the AI assistant"""
    return f"""You are Alphalens AI, an expert financial advisor assistant for Indian stock market portfolio analysis. You help investors understand their portfolio performance and make informed decisions.

You have access to the user's portfolio analysis data below. Use this information to answer their questions accurately and helpfully.

{portfolio_context}

## Your Capabilities:
1. **Metrics Explanation:** Explain portfolio metrics like returns, gains/losses, CAGR, volatility, etc.
2. **Sector Analysis:** Discuss sector allocation, diversification, and sector-specific risks/opportunities.
3. **Benchmark Comparison:** Explain how the portfolio compares to NIFTY 50, Sensex, and what alpha/beta mean.
4. **Recommendations:** Explain BUY/HOLD/SELL recommendations with clear rationale based on value and growth perspectives.
5. **Rebalancing:** Suggest how to improve portfolio allocation and reduce risk.
6. **General Guidance:** Provide investment education and best practices.

## Guidelines:
- Always use Indian Rupee (₹) for currency values
- Be educational and explain concepts in simple terms
- Provide specific, actionable advice based on the portfolio data
- Mention relevant stocks from the portfolio when applicable
- If you don't have specific data, say so clearly
- Never provide guaranteed returns or promises
- Always remind users that this is educational and not financial advice
- Keep responses concise but informative
- Use bullet points for clarity when listing multiple items"""

def chat_with_assistant(user_message, analysis_results, portfolio_data, chat_history=None):
    """Send a message to the AI assistant and get a response"""
    try:
        portfolio_context = get_portfolio_context(analysis_results, portfolio_data)
        system_prompt = get_system_prompt(portfolio_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
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
1. Overall portfolio health assessment
2. Top performing and underperforming areas
3. Key risk factors or concerns
4. One actionable recommendation

Keep each point brief (1-2 sentences max)."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a concise financial analyst. Analyze this portfolio:\n\n{portfolio_context}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Quick insights error: {e}")
        return None
