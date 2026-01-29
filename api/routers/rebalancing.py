"""Rebalancing suggestions router"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from api.models.schemas import PortfolioUpload, RebalancingResponse, RebalancingSuggestion
from api.dependencies import get_current_user
from api.routers.portfolio import convert_holdings_to_dataframe, get_analyzer_instances

router = APIRouter(prefix="/rebalancing", tags=["Portfolio Rebalancing"])


@router.post("/suggestions")
async def get_rebalancing_suggestions(
    portfolio: PortfolioUpload,
    risk_profile: str = "moderate",
    current_user: dict = Depends(get_current_user)
):
    """Get portfolio rebalancing suggestions based on risk profile
    
    Risk profiles: conservative, moderate, aggressive
    
    Returns:
    - Suggested trades to optimize sector allocation
    - Target weights based on risk profile
    - Concentration alerts
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        
        risk_profiles = {
            "conservative": {
                "Banking": 0.25, "IT": 0.15, "FMCG": 0.20,
                "Pharma": 0.15, "Auto": 0.10, "Others": 0.15
            },
            "moderate": {
                "Banking": 0.20, "IT": 0.20, "FMCG": 0.15,
                "Pharma": 0.15, "Auto": 0.15, "Others": 0.15
            },
            "aggressive": {
                "Banking": 0.15, "IT": 0.25, "Auto": 0.20,
                "Pharma": 0.10, "FMCG": 0.10, "Others": 0.20
            }
        }
        
        target_allocation = risk_profiles.get(risk_profile.lower(), risk_profiles["moderate"])
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        current_data = {}
        for _, row in portfolio_df.iterrows():
            stock = row["Stock Name"]
            price = data_fetcher.get_current_price(stock) or row["Buy Price"]
            current_data[stock] = price
        
        analysis_results = analyzer.analyze_portfolio(portfolio_df, current_data, {})
        
        current_allocation = analysis_results.get("sector_allocation", {})
        total_value = analysis_results.get("current_value", 0)
        
        suggestions = []
        
        for sector, target_pct in target_allocation.items():
            current_pct = current_allocation.get(sector, 0) / 100
            diff = target_pct - current_pct
            
            if abs(diff) > 0.03:
                amount = abs(diff * total_value)
                
                if diff > 0:
                    action = "BUY"
                    reason = f"Underweight in {sector} - increase allocation by {abs(diff)*100:.1f}%"
                else:
                    action = "SELL"
                    reason = f"Overweight in {sector} - reduce allocation by {abs(diff)*100:.1f}%"
                
                suggestions.append({
                    "sector": sector,
                    "current_weight": round(current_pct * 100, 2),
                    "target_weight": round(target_pct * 100, 2),
                    "action": action,
                    "amount": round(amount, 2),
                    "reason": reason
                })
        
        current_alloc_pct = {k: round(v, 2) for k, v in current_allocation.items()}
        target_alloc_pct = {k: round(v * 100, 2) for k, v in target_allocation.items()}
        
        rebalancing_cost = sum(s["amount"] * 0.001 for s in suggestions)
        
        return {
            "risk_profile": risk_profile,
            "suggestions": suggestions,
            "current_allocation": current_alloc_pct,
            "target_allocation": target_alloc_pct,
            "total_portfolio_value": round(total_value, 2),
            "estimated_rebalancing_cost": round(rebalancing_cost, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rebalancing calculation failed: {str(e)}"
        )


@router.post("/concentration-alerts")
async def get_concentration_alerts(
    portfolio: PortfolioUpload,
    max_single_stock: float = 15.0,
    max_sector: float = 30.0,
    current_user: dict = Depends(get_current_user)
):
    """Get concentration alerts when holdings exceed thresholds
    
    Parameters:
    - max_single_stock: Maximum % for single stock (default 15%)
    - max_sector: Maximum % for single sector (default 30%)
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        current_data = {}
        for _, row in portfolio_df.iterrows():
            stock = row["Stock Name"]
            price = data_fetcher.get_current_price(stock) or row["Buy Price"]
            current_data[stock] = price
        
        analysis_results = analyzer.analyze_portfolio(portfolio_df, current_data, {})
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        total_value = analyzed_df["Current Value"].sum()
        
        stock_alerts = []
        sector_alerts = []
        
        for _, row in analyzed_df.iterrows():
            weight = (row["Current Value"] / total_value) * 100
            if weight > max_single_stock:
                stock_alerts.append({
                    "stock": row["Stock Name"],
                    "weight": round(weight, 2),
                    "threshold": max_single_stock,
                    "severity": "high" if weight > max_single_stock * 1.5 else "medium",
                    "action": f"Consider reducing position by {round(weight - max_single_stock, 1)}%"
                })
        
        sector_allocation = analysis_results.get("sector_allocation", {})
        for sector, weight in sector_allocation.items():
            if weight > max_sector:
                sector_alerts.append({
                    "sector": sector,
                    "weight": round(weight, 2),
                    "threshold": max_sector,
                    "severity": "high" if weight > max_sector * 1.5 else "medium",
                    "action": f"Consider reducing {sector} exposure by {round(weight - max_sector, 1)}%"
                })
        
        return {
            "stock_alerts": stock_alerts,
            "sector_alerts": sector_alerts,
            "total_alerts": len(stock_alerts) + len(sector_alerts),
            "thresholds": {
                "max_single_stock": max_single_stock,
                "max_sector": max_sector
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Concentration alerts failed: {str(e)}"
        )
