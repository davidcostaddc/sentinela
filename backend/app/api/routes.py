from fastapi import APIRouter, HTTPException
from app.schemas.analysis import URLRequest, EmailRequest, AnalysisResponse
from app.services.url_analyzer import analyze_url
from app.services.email_analyzer import analyze_email
from app.services.risk_engine import calculate_risk

router = APIRouter(prefix="/api", tags=["Análises"])


def build_response(indicators: list[dict], analysis_type: str) -> dict:
    result = calculate_risk(indicators)
    if result["risk_score"] >= 70:
        recommendation = "Não interaja com o conteúdo. Confirme a autenticidade por um canal oficial e independente."
    elif result["risk_score"] >= 35:
        recommendation = "Tenha cautela. Confirme a origem antes de clicar ou fornecer informações."
    else:
        recommendation = "Poucos indicadores foram identificados. Isso não garante que o conteúdo seja seguro."
    return {
        **result,
        "analysis_type": analysis_type,
        "indicators": indicators,
        "recommendation": recommendation,
        "disclaimer": "Pontuação heurística e educativa; não representa probabilidade comprovada de fraude.",
    }


@router.post("/analyze/url", response_model=AnalysisResponse)
def analyze_link(request: URLRequest):
    try:
        return build_response(analyze_url(request.url), "link")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/analyze/email", response_model=AnalysisResponse)
def analyze_message(request: EmailRequest):
    return build_response(analyze_email(request.content), "email")
