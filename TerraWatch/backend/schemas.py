from typing import List, Optional
from pydantic import BaseModel

class ForecastPoint(BaseModel):
    month: int
    predicted_cm: float
    upper_1s: float
    lower_1s: float
    upper_2s: float
    lower_2s: float

class ExposedStructure(BaseModel):
    display_name: str
    structure_type: str
    vertical_cm: float
    risk_level: str

class PointAnalysisResponse(BaseModel):
    status: str
    lat: float
    lon: float
    exact_80m_cell_cm: Optional[float] = None
    neighborhood_mean_cm: Optional[float] = None
    uncertainty_1sigma_cm: Optional[float] = None
    annualized_rate_cm_yr: Optional[float] = None
    ml_anomaly_score_pct: Optional[float] = None
    risk_level: str
    confidence_level: str
    ai_summary: str
    nearby_structures: List[ExposedStructure] = []
    forecast: List[ForecastPoint] = []

class ChatRequest(BaseModel):
    question: str
    lat: Optional[float] = None
    lon: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
