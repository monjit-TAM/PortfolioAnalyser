"""
Alphalens Portfolio Analyzer - FastAPI Backend
==============================================

REST API for portfolio analysis, recommendations, and advanced metrics.
Designed for integration with Indian stock broker platforms.

API Documentation: /docs (Swagger UI) or /redoc (ReDoc)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from api.routers import (
    auth_router,
    portfolio_router,
    recommendations_router,
    metrics_router,
    rebalancing_router,
    websocket_router
)

app = FastAPI(
    title="Alphalens Portfolio Analyzer API",
    description="""
## Indian Stock Portfolio Analysis API

Comprehensive REST API for analyzing Indian stock market portfolios.
Built for integration with broker platforms.

### Features:
- **Portfolio Analysis**: Upload and analyze stock portfolios
- **Investment Recommendations**: Value and Growth investing perspectives
- **Advanced Metrics**: 10-layer institutional-grade analysis
- **Risk Assessment**: Concentration, volatility, and tail risk metrics
- **Tax Impact**: STCG/LTCG classification and tax estimates
- **Rebalancing**: Suggestions based on risk profile

### Authentication:
- JWT Bearer tokens (for user sessions)
- API Keys (for programmatic access)

### Rate Limits:
- 100 requests/minute for standard users
- 1000 requests/minute for premium users
    """,
    version="1.0.0",
    contact={
        "name": "Alphalens by Edhaz Financial Services",
        "email": "api@alphalens.in"
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(rebalancing_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """API root - health check"""
    return {
        "name": "Alphalens Portfolio Analyzer API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs"
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "data_feeds": "operational"
        }
    }


@app.get("/api/v1/stocks/search", tags=["Stock Data"])
async def search_stocks(q: str, limit: int = 10):
    """Search for Indian stocks by name or symbol
    
    Returns matching stocks with their symbols and sectors.
    """
    from utils.data_fetcher import DataFetcher
    
    data_fetcher = DataFetcher()
    
    results = []
    
    all_symbols = data_fetcher.get_all_symbols()
    
    q_upper = q.upper()
    for symbol_info in all_symbols:
        if q_upper in symbol_info.get("symbol", "").upper() or \
           q_upper in symbol_info.get("name", "").upper():
            results.append(symbol_info)
            if len(results) >= limit:
                break
    
    return {"query": q, "results": results}


@app.get("/api/v1/stocks/{symbol}/price", tags=["Stock Data"])
async def get_stock_price(symbol: str):
    """Get current price for a stock"""
    from utils.data_fetcher import DataFetcher
    
    data_fetcher = DataFetcher()
    price = data_fetcher.get_current_price(symbol)
    
    if price is None:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    return {
        "symbol": symbol,
        "price": price,
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/stocks/{symbol}/fundamentals", tags=["Stock Data"])
async def get_stock_fundamentals(symbol: str):
    """Get fundamental data for a stock (P/E, P/B, dividend yield, etc.)"""
    from utils.data_fetcher import DataFetcher
    
    data_fetcher = DataFetcher()
    fundamentals = data_fetcher.get_stock_fundamentals(symbol)
    
    if not fundamentals:
        raise HTTPException(status_code=404, detail=f"Fundamentals for {symbol} not found")
    
    return {
        "symbol": symbol,
        "fundamentals": fundamentals,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/indices", tags=["Market Data"])
async def get_indices():
    """Get current values of major Indian market indices"""
    from utils.data_fetcher import DataFetcher
    
    data_fetcher = DataFetcher()
    
    indices = {
        "NIFTY50": data_fetcher.get_current_price("^NSEI"),
        "SENSEX": data_fetcher.get_current_price("^BSESN"),
        "NIFTYBANK": data_fetcher.get_current_price("^NSEBANK")
    }
    
    return {
        "indices": {k: v for k, v in indices.items() if v is not None},
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
