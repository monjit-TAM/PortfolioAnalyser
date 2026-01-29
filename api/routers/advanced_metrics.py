"""Advanced Metrics router - 10-layer institutional-grade analysis"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from api.models.schemas import (
    PortfolioUpload, AdvancedMetricsResponse, TaxImpact,
    RebalancingResponse, RebalancingSuggestion, BenchmarkComparison,
    RiskRadarMetrics, HealthScore
)
from api.dependencies import get_current_user
from api.routers.portfolio import convert_holdings_to_dataframe, get_analyzer_instances

router = APIRouter(prefix="/metrics", tags=["Advanced Metrics"])


def get_metrics_calculator():
    """Get advanced metrics calculator instance"""
    from utils.advanced_metrics import AdvancedMetricsCalculator
    return AdvancedMetricsCalculator()


@router.post("/full")
async def get_all_metrics(
    portfolio: PortfolioUpload,
    include_benchmark: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get all 10 layers of advanced metrics analysis
    
    Includes:
    1. Structural Diagnostics (market cap, sector allocation)
    2. Style Analysis (value/growth tilt)
    3. Concentration Risk
    4. Volatility Metrics (beta, Sharpe, Sortino)
    5. Behavior Score
    6. Drift Analysis
    7. Overlap Detection
    8. Return Attribution
    9. Liquidity Risk
    10. Tail Risk & Macro Sensitivity
    
    Plus: Health Score, Scenario Analysis
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        benchmark_data = None
        if include_benchmark:
            benchmark_data = data_fetcher.get_historical_data("^NSEI")
        
        all_metrics = calculator.calculate_all_metrics(
            analyzed_df, historical_data, benchmark_data
        )
        
        return all_metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics calculation failed: {str(e)}"
        )


@router.post("/structural")
async def get_structural_diagnostics(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get structural diagnostics - market cap and sector allocation"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        for _, row in portfolio_df.iterrows():
            stock = row["Stock Name"]
            price = data_fetcher.get_current_price(stock) or row["Buy Price"]
            portfolio_df.loc[portfolio_df["Stock Name"] == stock, "Current Price"] = price
        
        portfolio_df["Current Value"] = portfolio_df["Current Price"] * portfolio_df["Quantity"]
        
        structural = calculator.calculate_structural_diagnostics(portfolio_df)
        return structural
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Structural analysis failed: {str(e)}"
        )


@router.post("/concentration-risk")
async def get_concentration_risk(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get concentration risk analysis - identifies over-allocation"""
    try:
        data_fetcher, _ = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        for _, row in portfolio_df.iterrows():
            stock = row["Stock Name"]
            price = data_fetcher.get_current_price(stock) or row["Buy Price"]
            portfolio_df.loc[portfolio_df["Stock Name"] == stock, "Current Price"] = price
        
        portfolio_df["Current Value"] = portfolio_df["Current Price"] * portfolio_df["Quantity"]
        
        concentration = calculator.calculate_concentration_risk(portfolio_df)
        return concentration
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Concentration analysis failed: {str(e)}"
        )


@router.post("/volatility")
async def get_volatility_metrics(
    portfolio: PortfolioUpload,
    include_benchmark: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get volatility metrics - beta, Sharpe ratio, Sortino ratio, VaR"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        benchmark_data = None
        if include_benchmark:
            benchmark_data = data_fetcher.get_historical_data("^NSEI")
        
        volatility = calculator.calculate_volatility_metrics(
            analyzed_df, historical_data, benchmark_data
        )
        return volatility
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Volatility analysis failed: {str(e)}"
        )


@router.post("/health-score")
async def get_health_score(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get overall portfolio health score (0-100) with grade"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        all_metrics = calculator.calculate_all_metrics(analyzed_df, historical_data, None)
        health = calculator.calculate_health_score(all_metrics)
        
        return health
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health score calculation failed: {str(e)}"
        )


@router.post("/tax-impact")
async def get_tax_impact(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Calculate tax impact - STCG/LTCG classification and estimated taxes"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        stock_names = portfolio_df["Stock Name"].tolist()
        current_data = {}
        
        for stock in stock_names:
            price = data_fetcher.get_current_price(stock)
            if price:
                current_data[stock] = price
        
        analysis_results = analyzer.analyze_portfolio(portfolio_df, current_data, {})
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        tax_impact = calculator.calculate_tax_impact(analyzed_df)
        return tax_impact
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tax impact calculation failed: {str(e)}"
        )


@router.post("/risk-radar")
async def get_risk_radar(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Get risk radar metrics for spider chart visualization
    
    Returns 6 risk dimensions (0-100 scale):
    - Concentration Risk
    - Volatility Risk
    - Liquidity Risk
    - Sector Risk
    - Tail Risk
    - Behavioral Risk
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        all_metrics = calculator.calculate_all_metrics(analyzed_df, historical_data, None)
        
        concentration = all_metrics.get("concentration", {})
        volatility = all_metrics.get("volatility", {})
        liquidity = all_metrics.get("liquidity", {})
        tail = all_metrics.get("tail_risk", {})
        behavior = all_metrics.get("behavior", {})
        structural = all_metrics.get("structural", {})
        
        def normalize_risk(value, max_val=100):
            return min(100, max(0, (value / max_val) * 100)) if value else 0
        
        radar_metrics = {
            "concentration_risk": normalize_risk(concentration.get("top3_concentration", 0)),
            "volatility_risk": normalize_risk(volatility.get("portfolio_volatility", 0) * 3, 100),
            "liquidity_risk": 100 - normalize_risk(liquidity.get("liquidity_score", 100)),
            "sector_risk": normalize_risk(
                structural.get("industry_concentration", {}).get("top_sector_pct", 0)
            ),
            "tail_risk": normalize_risk(tail.get("tail_risk_score", 0)),
            "behavioral_risk": 100 - normalize_risk(behavior.get("diversification_score", 0))
        }
        
        return radar_metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk radar calculation failed: {str(e)}"
        )


@router.post("/benchmark-comparison")
async def get_benchmark_comparison(
    portfolio: PortfolioUpload,
    benchmark: str = "NIFTY50",
    current_user: dict = Depends(get_current_user)
):
    """Compare portfolio performance against benchmark index
    
    Available benchmarks: NIFTY50, SENSEX, NIFTYMIDCAP, NIFTYBANK
    """
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
        benchmark_symbols = {
            "NIFTY50": "^NSEI",
            "SENSEX": "^BSESN",
            "NIFTYMIDCAP": "^NSEMDCP50",
            "NIFTYBANK": "^NSEBANK"
        }
        
        benchmark_symbol = benchmark_symbols.get(benchmark.upper(), "^NSEI")
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        benchmark_data = data_fetcher.get_historical_data(benchmark_symbol)
        
        portfolio_return = analysis_results.get("percentage_gain_loss", 0)
        
        benchmark_return = 0
        if benchmark_data is not None and len(benchmark_data) > 0:
            if 'Close' in benchmark_data.columns:
                first_price = benchmark_data['Close'].iloc[0]
                last_price = benchmark_data['Close'].iloc[-1]
                benchmark_return = ((last_price - first_price) / first_price) * 100
        
        drift = calculator.calculate_drift_analysis(analyzed_df, benchmark_data)
        volatility = calculator.calculate_volatility_metrics(analyzed_df, historical_data, benchmark_data)
        
        return {
            "benchmark_name": benchmark.upper(),
            "benchmark_return": round(benchmark_return, 2),
            "portfolio_return": round(portfolio_return, 2),
            "alpha": round(portfolio_return - benchmark_return, 2),
            "beta": volatility.get("beta", 1.0),
            "tracking_error": drift.get("tracking_error", 0),
            "active_share": drift.get("active_share", 0),
            "outperformance": round(portfolio_return - benchmark_return, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark comparison failed: {str(e)}"
        )


@router.post("/scenario-analysis")
async def get_scenario_analysis(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Run scenario analysis - bull, bear, and recession cases"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        calculator = get_metrics_calculator()
        
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
        analyzed_df = analysis_results.get("portfolio_df", portfolio_df)
        
        scenarios = calculator.calculate_scenario_analysis(analyzed_df, historical_data, None)
        return scenarios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario analysis failed: {str(e)}"
        )
