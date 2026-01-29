"""Pydantic models for API request/response schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class APIKeyCreate(BaseModel):
    name: str = Field(..., description="Name for this API key")
    permissions: List[str] = Field(default=["read"], description="Permissions: read, write, admin")


class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: datetime
    permissions: List[str]


class StockHolding(BaseModel):
    stock_name: str = Field(..., description="Stock symbol or name (e.g., RELIANCE, TCS)")
    quantity: int = Field(..., gt=0)
    buy_price: float = Field(..., gt=0)
    buy_date: str = Field(..., description="Date in YYYY-MM-DD format")


class PortfolioUpload(BaseModel):
    holdings: List[StockHolding]


class PortfolioSummary(BaseModel):
    total_investment: float
    current_value: float
    total_gain_loss: float
    percentage_gain_loss: float
    total_stocks: int
    analysis_date: datetime


class StockAnalysis(BaseModel):
    stock_name: str
    symbol: str
    quantity: int
    buy_price: float
    current_price: float
    investment_value: float
    current_value: float
    absolute_gain_loss: float
    percentage_gain_loss: float
    sector: Optional[str] = None
    holding_days: Optional[int] = None


class PortfolioAnalysisResponse(BaseModel):
    summary: PortfolioSummary
    holdings: List[StockAnalysis]
    sector_allocation: Dict[str, float]
    top_performers: List[StockAnalysis]
    bottom_performers: List[StockAnalysis]


class ValueAnalysis(BaseModel):
    score: int
    factors: List[str]
    recommendation: RecommendationType
    rationale: List[str]
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    debt_to_equity: Optional[float] = None


class GrowthAnalysis(BaseModel):
    score: int
    factors: List[str]
    recommendation: RecommendationType
    rationale: List[str]
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    roe: Optional[float] = None
    momentum_52w: Optional[float] = None


class StockRecommendation(BaseModel):
    stock_name: str
    symbol: str
    current_price: float
    action: RecommendationType
    confidence: str
    target_price: Optional[float] = None
    value_analysis: ValueAnalysis
    growth_analysis: GrowthAnalysis
    combined_score: float
    rationale: List[str]
    alternative_stocks: Optional[List[str]] = None


class RecommendationsResponse(BaseModel):
    recommendations: List[StockRecommendation]
    summary: Dict[str, int]


class StructuralDiagnostics(BaseModel):
    market_cap_allocation: Dict[str, float]
    sector_allocation: Dict[str, float]
    industry_concentration: Dict[str, Any]
    thematic_clusters: List[str]
    total_stocks: int
    total_value: float


class StyleAnalysis(BaseModel):
    value_tilt: float
    growth_tilt: float
    momentum_exposure: float
    quality_factor: str
    volatility_tilt: str
    style_label: str


class ConcentrationRisk(BaseModel):
    top1_concentration: float
    top3_concentration: float
    top5_concentration: float
    hhi_index: float
    risk_level: str
    single_stock_flags: List[Dict[str, Any]]
    sector_flags: List[Dict[str, Any]]


class VolatilityMetrics(BaseModel):
    portfolio_volatility: float
    max_drawdown: float
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    var_95: float
    cvar_95: float


class BehaviorScore(BaseModel):
    avg_holding_period: float
    trading_frequency: str
    disposition_effect: str
    diversification_score: float
    behavior_grade: str


class DriftAnalysis(BaseModel):
    sector_drift: Dict[str, float]
    active_share: float
    tracking_error: float
    style_drift: str


class OverlapDetection(BaseModel):
    business_group_overlap: Dict[str, List[str]]
    sector_overlap: Dict[str, float]
    overlap_risk_score: float


class ReturnAttribution(BaseModel):
    top_contributors: List[Dict[str, Any]]
    bottom_contributors: List[Dict[str, Any]]
    sector_contribution: Dict[str, float]


class LiquidityRisk(BaseModel):
    illiquid_holdings: List[Dict[str, Any]]
    liquidity_score: float
    days_to_liquidate: float


class TailRisk(BaseModel):
    high_volatility_exposure: float
    small_cap_exposure: float
    tail_risk_score: float


class MacroSensitivity(BaseModel):
    interest_rate_sensitivity: str
    currency_sensitivity: str
    commodity_sensitivity: str
    inflation_sensitivity: str


class HealthScore(BaseModel):
    overall_score: float
    grade: str
    components: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]


class ScenarioAnalysis(BaseModel):
    bull_case: Dict[str, float]
    bear_case: Dict[str, float]
    recession_case: Dict[str, float]
    stress_test_results: Dict[str, Any]


class AdvancedMetricsResponse(BaseModel):
    structural: StructuralDiagnostics
    style: StyleAnalysis
    concentration: ConcentrationRisk
    volatility: VolatilityMetrics
    behavior: BehaviorScore
    drift: DriftAnalysis
    overlap: OverlapDetection
    attribution: ReturnAttribution
    liquidity: LiquidityRisk
    tail_risk: TailRisk
    macro_sensitivity: MacroSensitivity
    health_score: HealthScore
    scenario_analysis: ScenarioAnalysis


class TaxImpact(BaseModel):
    short_term_gains: float
    short_term_losses: float
    long_term_gains: float
    long_term_losses: float
    estimated_stcg_tax: float
    estimated_ltcg_tax: float
    total_tax_liability: float
    tax_loss_harvesting_opportunities: List[Dict[str, Any]]


class RebalancingSuggestion(BaseModel):
    stock_name: str
    current_weight: float
    target_weight: float
    action: str
    amount: float
    reason: str


class RebalancingResponse(BaseModel):
    suggestions: List[RebalancingSuggestion]
    current_allocation: Dict[str, float]
    target_allocation: Dict[str, float]
    rebalancing_cost: float


class BenchmarkComparison(BaseModel):
    benchmark_name: str
    benchmark_return: float
    portfolio_return: float
    alpha: float
    beta: float
    tracking_error: float
    information_ratio: float
    outperformance: float


class RiskRadarMetrics(BaseModel):
    concentration_risk: float
    volatility_risk: float
    liquidity_risk: float
    sector_risk: float
    tail_risk: float
    behavioral_risk: float


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
