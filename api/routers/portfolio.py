"""Portfolio analysis router"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
import pandas as pd
from io import StringIO
from datetime import datetime

from api.models.schemas import (
    PortfolioUpload, PortfolioAnalysisResponse, PortfolioSummary,
    StockAnalysis, ErrorResponse
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio Analysis"])


def get_analyzer_instances():
    """Get instances of the portfolio analyzer and data fetcher"""
    from utils.data_fetcher import DataFetcher
    from utils.portfolio_analyzer import PortfolioAnalyzer
    
    data_fetcher = DataFetcher()
    analyzer = PortfolioAnalyzer()
    return data_fetcher, analyzer


def convert_holdings_to_dataframe(holdings: List[dict]) -> pd.DataFrame:
    """Convert list of holdings to DataFrame"""
    data = []
    for h in holdings:
        data.append({
            "Stock Name": h.get("stock_name", h.get("Stock Name")),
            "Quantity": h.get("quantity", h.get("Quantity")),
            "Buy Price": h.get("buy_price", h.get("Buy Price")),
            "Buy Date": h.get("buy_date", h.get("Buy Date"))
        })
    return pd.DataFrame(data)


@router.post("/upload-csv")
async def upload_portfolio_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload portfolio data via CSV file
    
    Expected CSV columns: Stock Name, Quantity, Buy Price, Buy Date
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    content = await file.read()
    try:
        df = pd.read_csv(StringIO(content.decode('utf-8')))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}"
        )
    
    required_columns = ["Stock Name", "Quantity", "Buy Price", "Buy Date"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {missing}"
        )
    
    holdings = df.to_dict('records')
    
    return {
        "message": "Portfolio uploaded successfully",
        "holdings_count": len(holdings),
        "holdings": holdings
    }


@router.post("/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Analyze portfolio and return comprehensive metrics"""
    try:
        data_fetcher, analyzer = get_analyzer_instances()
        
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
        
        results = analyzer.analyze_portfolio(portfolio_df, current_data, historical_data)
        
        analyzed_df = results.get("portfolio_df", portfolio_df)
        
        holdings_list = []
        for _, row in analyzed_df.iterrows():
            holdings_list.append(StockAnalysis(
                stock_name=row.get("Stock Name", ""),
                symbol=row.get("Symbol", row.get("Stock Name", "")),
                quantity=int(row.get("Quantity", 0)),
                buy_price=float(row.get("Buy Price", 0)),
                current_price=float(row.get("Current Price", row.get("Buy Price", 0))),
                investment_value=float(row.get("Investment Value", 0)),
                current_value=float(row.get("Current Value", 0)),
                absolute_gain_loss=float(row.get("Absolute Gain/Loss", 0)),
                percentage_gain_loss=float(row.get("Percentage Gain/Loss", 0)),
                sector=row.get("Sector"),
                holding_days=row.get("Holding Days")
            ))
        
        sorted_by_gain = sorted(holdings_list, key=lambda x: x.percentage_gain_loss, reverse=True)
        top_performers = sorted_by_gain[:3] if len(sorted_by_gain) >= 3 else sorted_by_gain
        bottom_performers = sorted_by_gain[-3:] if len(sorted_by_gain) >= 3 else sorted_by_gain
        
        summary = PortfolioSummary(
            total_investment=results.get("total_investment", 0),
            current_value=results.get("current_value", 0),
            total_gain_loss=results.get("total_gain_loss", 0),
            percentage_gain_loss=results.get("percentage_gain_loss", 0),
            total_stocks=len(holdings_list),
            analysis_date=datetime.utcnow()
        )
        
        sector_allocation = results.get("sector_allocation", {})
        
        return PortfolioAnalysisResponse(
            summary=summary,
            holdings=holdings_list,
            sector_allocation=sector_allocation,
            top_performers=top_performers,
            bottom_performers=bottom_performers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/quick-analyze")
async def quick_analyze(
    portfolio: PortfolioUpload,
    current_user: dict = Depends(get_current_user)
):
    """Quick portfolio analysis with basic metrics (faster response)"""
    try:
        data_fetcher, _ = get_analyzer_instances()
        
        holdings_data = [h.dict() for h in portfolio.holdings]
        portfolio_df = convert_holdings_to_dataframe(holdings_data)
        
        total_investment = 0
        current_value = 0
        holdings_results = []
        
        for _, row in portfolio_df.iterrows():
            stock_name = row["Stock Name"]
            quantity = row["Quantity"]
            buy_price = row["Buy Price"]
            
            current_price = data_fetcher.get_current_price(stock_name) or buy_price
            
            inv_value = buy_price * quantity
            curr_value = current_price * quantity
            gain_loss = curr_value - inv_value
            pct_gain = ((curr_value - inv_value) / inv_value * 100) if inv_value > 0 else 0
            
            total_investment += inv_value
            current_value += curr_value
            
            holdings_results.append({
                "stock_name": stock_name,
                "quantity": quantity,
                "buy_price": buy_price,
                "current_price": current_price,
                "investment_value": inv_value,
                "current_value": curr_value,
                "gain_loss": gain_loss,
                "percentage_gain_loss": round(pct_gain, 2)
            })
        
        total_gain_loss = current_value - total_investment
        total_pct = ((current_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        return {
            "summary": {
                "total_investment": round(total_investment, 2),
                "current_value": round(current_value, 2),
                "total_gain_loss": round(total_gain_loss, 2),
                "percentage_gain_loss": round(total_pct, 2),
                "total_stocks": len(holdings_results)
            },
            "holdings": holdings_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
