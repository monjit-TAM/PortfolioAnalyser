"""Recommendations router"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from api.models.schemas import (
    PortfolioUpload, RecommendationsResponse, StockRecommendation,
    ValueAnalysis, GrowthAnalysis, RecommendationType
)
from api.dependencies import get_current_user
from api.routers.portfolio import convert_holdings_to_dataframe, get_analyzer_instances

router = APIRouter(prefix="/recommendations", tags=["Investment Recommendations"])


def get_recommendation_engine():
    """Get recommendation engine instance"""
    from utils.recommendation_engine import RecommendationEngine
    return RecommendationEngine()


@router.post("/full", response_model=RecommendationsResponse)
async def get_full_recommendations(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive BUY/HOLD/SELL recommendations for all holdings
    
    Combines Value Investing and Growth Investing perspectives to generate
    actionable recommendations with confidence levels.
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        engine = get_recommendation_engine()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        stock_names = portfolio_df["Stock Name"].tolist()
        current_data = {}
        historical_data = {}
        
        for stock in stock_names:
            price = data_fetcher.get_current_price(stock)
            if price:
                current_data[stock] = price
            hist = data_fetcher.get_historical_data(stock)
            if hist is not None:
                historical_data[stock] = hist
        
        analysis_results = analyzer.analyze_portfolio(portfolio_df, current_data, historical_data)
        
        recommendations_data = engine.generate_recommendations(
            portfolio_df, current_data, historical_data, analysis_results
        )
        
        recommendations = []
        buy_count = 0
        hold_count = 0
        sell_count = 0
        
        for rec in recommendations_data:
            action = rec.get("action", "HOLD")
            if action == "BUY":
                buy_count += 1
            elif action == "SELL":
                sell_count += 1
            else:
                hold_count += 1
            
            value_data = rec.get("value_analysis", {})
            growth_data = rec.get("growth_analysis", {})
            
            value_analysis = ValueAnalysis(
                score=value_data.get("score", 0),
                factors=value_data.get("factors", []),
                recommendation=RecommendationType(value_data.get("recommendation", "HOLD")),
                rationale=value_data.get("rationale", []),
                pe_ratio=value_data.get("pe_ratio"),
                pb_ratio=value_data.get("pb_ratio"),
                dividend_yield=value_data.get("dividend_yield"),
                debt_to_equity=value_data.get("debt_to_equity")
            )
            
            growth_analysis = GrowthAnalysis(
                score=growth_data.get("score", 0),
                factors=growth_data.get("factors", []),
                recommendation=RecommendationType(growth_data.get("recommendation", "HOLD")),
                rationale=growth_data.get("rationale", []),
                revenue_growth=growth_data.get("revenue_growth"),
                earnings_growth=growth_data.get("earnings_growth"),
                roe=growth_data.get("roe"),
                momentum_52w=growth_data.get("momentum_52w")
            )
            
            stock_rec = StockRecommendation(
                stock_name=rec.get("stock_name", ""),
                symbol=rec.get("symbol", rec.get("stock_name", "")),
                current_price=rec.get("current_price", 0),
                action=RecommendationType(action),
                confidence=rec.get("confidence", "Medium"),
                target_price=rec.get("target_price"),
                value_analysis=value_analysis,
                growth_analysis=growth_analysis,
                combined_score=rec.get("combined_score", 0),
                rationale=rec.get("rationale", []),
                alternative_stocks=rec.get("alternative_stocks")
            )
            recommendations.append(stock_rec)
        
        return RecommendationsResponse(
            recommendations=recommendations,
            summary={"BUY": buy_count, "HOLD": hold_count, "SELL": sell_count}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/value-analysis")
async def get_value_analysis(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get Value Investing perspective analysis for portfolio
    
    Analyzes stocks based on Benjamin Graham / Warren Buffett principles:
    - P/E Ratio vs Industry
    - Price-to-Book Value
    - Dividend Yield
    - Debt-to-Equity Ratio
    - Margin of Safety
    """
    try:
        data_fetcher, _ = get_analyzer_instances()
        engine = get_recommendation_engine()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        results = []
        for _, row in portfolio_df.iterrows():
            stock_name = row["Stock Name"]
            fundamentals = data_fetcher.get_stock_fundamentals(stock_name)
            historical = data_fetcher.get_historical_data(stock_name)
            
            value_analysis = engine.analyze_value_perspective(row, fundamentals, historical)
            
            results.append({
                "stock_name": stock_name,
                "score": value_analysis.get("score", 0),
                "recommendation": value_analysis.get("recommendation", "HOLD"),
                "factors": value_analysis.get("factors", []),
                "rationale": value_analysis.get("rationale", [])
            })
        
        return {"value_analysis": results}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Value analysis failed: {str(e)}"
        )


@router.post("/growth-analysis")
async def get_growth_analysis(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get Growth Investing perspective analysis for portfolio
    
    Analyzes stocks based on growth metrics:
    - Revenue Growth Rate
    - EPS Growth Trajectory
    - 52-week Momentum
    - Relative Strength
    - PEG Ratio
    """
    try:
        data_fetcher, _ = get_analyzer_instances()
        engine = get_recommendation_engine()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        results = []
        for _, row in portfolio_df.iterrows():
            stock_name = row["Stock Name"]
            fundamentals = data_fetcher.get_stock_fundamentals(stock_name)
            historical = data_fetcher.get_historical_data(stock_name)
            
            growth_analysis = engine.analyze_growth_perspective(row, fundamentals, historical)
            
            results.append({
                "stock_name": stock_name,
                "score": growth_analysis.get("score", 0),
                "recommendation": growth_analysis.get("recommendation", "HOLD"),
                "factors": growth_analysis.get("factors", []),
                "rationale": growth_analysis.get("rationale", [])
            })
        
        return {"growth_analysis": results}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Growth analysis failed: {str(e)}"
        )


@router.get("/alternatives/{sector}")
async def get_alternative_stocks(
    sector: str,
    current_stock: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get alternative stock suggestions within a sector
    
    Useful when a SELL recommendation is given - suggests better alternatives
    in the same sector.
    """
    try:
        engine = get_recommendation_engine()
        alternatives = engine.get_alternative_stocks(sector, current_stock)
        
        return {
            "sector": sector,
            "current_stock": current_stock,
            "alternatives": alternatives
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alternatives: {str(e)}"
        )
