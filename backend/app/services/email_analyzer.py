
import re
import unicodedata
from app.services.url_analyzer import analyze_url

URGENCY = [
    "urgente",
    "imediatamente",
    "ultima chance",
    "acao necessaria",
    "sua conta sera bloqueada",
]

CREDENTIALS = [
    "informe sua senha",
    "confirme sua senha",
    "digite sua senha",
    "confirme suas credenciais",
]

PAYMENTS = [
    "pagamento pendente",
    "pix pendente",
    "fatura vencida",
    "pagamento imediato",
    "dados bancarios",
]

BLOCKING = [
    "bloqueio definitivo",
    "conta sera bloqueada",
    "conta suspensa",
    "suspensao do servico",
    "acesso sera bloqueado",
]

PERSONAL_DATA = [
    "dados pessoais",
    "documento de identidade",
    "numero do cpf",
    "atualize seu cadastro",
]

PRIZES = [
    "premio exclusivo",
    "voce foi selecionado",
    "premiacao",
    "premio liberado",
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )


def analyze_email(content: str) -> list[dict]:
    text = normalize(content)
    indicators = []

    def add(name, description, severity, points):
        indicators.append({
            "name": name,
            "description": description,
            "severity": severity,
            "points": points,
        })

    if any(term in text for term in URGENCY):
        add(
            "Linguagem de urgencia",
            "A mensagem utiliza pressao para provocar uma acao rapida.",
            "medio", 15
        )

    if any(term in text for term in CREDENTIALS):
        add(
            "Solicitacao de credenciais",
            "A mensagem solicita senhas ou dados de autenticacao.",
            "alto", 25
        )

    if any(term in text for term in PAYMENTS):
        add(
            "Solicitacao relacionada a pagamentos",
            "A mensagem apresenta cobrancas ou solicitacoes financeiras.",
            "medio", 15
        )

    if any(term in text for term in BLOCKING):
        add(
            "Ameaca de bloqueio ou suspensao",
            "A mensagem utiliza ameacas de bloqueio para pressionar o destinatario.",
            "alto", 15
        )

    if any(term in text for term in PERSONAL_DATA):
        add(
            "Solicitacao de dados pessoais",
            "A mensagem solicita ou sugere a atualizacao de dados pessoais.",
            "medio", 10
        )

    if any(term in text for term in PRIZES):
        add(
            "Promessa de premio",
            "A mensagem apresenta uma promessa de premio que merece verificacao.",
            "medio", 10
        )

    urls = re.findall(
        r"https?://[^\s<>\"']+",
        content,
        flags=re.IGNORECASE
    )

    for url in urls[:10]:
        url = url.rstrip(".,;:!?)\"]}")

        try:
            for item in analyze_url(url):
                indicators.append({
                    **item,
                    "name": "Link: " + item["name"]
                })
        except ValueError:
            pass

    return indicators
