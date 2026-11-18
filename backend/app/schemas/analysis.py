from typing import Literal
from pydantic import BaseModel, Field


class URLRequest(BaseModel):
    url: str = Field(min_length=5, max_length=2048)


class EmailRequest(BaseModel):
    content: str = Field(min_length=5, max_length=20000)


class Indicator(BaseModel):
    name: str
    description: str
    severity: Literal["baixo", "medio", "alto"]
    points: int = Field(ge=0, le=100)


class AnalysisResponse(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    analysis_type: str
    indicators: list[Indicator]
    recommendation: str
    disclaimer: str
