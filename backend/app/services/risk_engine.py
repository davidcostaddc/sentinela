def calculate_risk(indicators: list[dict]) -> dict:
    score = max(0, min(int(sum(item.get("points", 0) for item in indicators)), 100))
    if score >= 70:
        level = "Alto risco"
    elif score >= 35:
        level = "Risco moderado"
    else:
        level = "Baixo risco"
    return {"risk_score": score, "risk_level": level}
