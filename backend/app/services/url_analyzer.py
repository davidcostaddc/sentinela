
import re
import ipaddress
from urllib.parse import urlparse

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
}

SUSPICIOUS_TERMS = {
    "login",
    "verify",
    "account",
    "password",
    "secure",
    "update",
    "confirm",
}


def analyze_url(url: str) -> list[dict]:
    """Analisa características textuais de uma URL, sem visitá-la."""

    value = url.strip()

    if not value or any(char.isspace() for char in value):
        raise ValueError("Informe uma URL válida, sem espaços.")

    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = "https://" + value

    parsed = urlparse(value)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Somente HTTP e HTTPS são aceitos.")

    try:
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise ValueError("Host ou porta inválidos.")

    if not host:
        raise ValueError("Domínio não identificado.")

    host = host.lower().rstrip(".")

    indicators = []

    def add(name, description, severity, points):
        indicators.append({
            "name": name,
            "description": description,
            "severity": severity,
            "points": points,
        })

    if parsed.scheme.lower() == "http":
        add(
            "Conexão sem HTTPS",
            "O endereço não utiliza criptografia de transporte HTTPS.",
            "medio", 10
        )

    if parsed.username is not None or parsed.password is not None:
        add(
            "Credenciais na URL",
            "A URL contém informações de usuário ou senha antes do host.",
            "alto", 25
        )

    try:
        ipaddress.ip_address(host)
        is_ip = True
    except ValueError:
        is_ip = False

    if is_ip:
        add(
            "Endereço IP direto",
            "O endereço utiliza um IP em vez de um domínio convencional.",
            "medio", 20
        )
    elif "." not in host:
        raise ValueError("Domínio inválido ou incompleto.")

    if "xn--" in host:
        add(
            "Domínio internacional codificado",
            "O domínio utiliza codificação Punycode. Confira sua identidade.",
            "medio", 15
        )

    if not is_ip and len(host.split(".")) >= 5:
        add(
            "Muitos subdomínios",
            "O endereço possui vários níveis de subdomínio.",
            "medio", 10
        )

    if any(
        host == domain or host.endswith("." + domain)
        for domain in SHORTENERS
    ):
        add(
            "Link encurtado",
            "O endereço utiliza um serviço que oculta o destino final.",
            "medio", 10
        )

    if port is not None and port not in {80, 443}:
        add(
            "Porta não convencional",
            "O endereço utiliza uma porta diferente das portas HTTP e HTTPS padrão.",
            "baixo", 5
        )

    parts = re.split(
        r"[^a-zA-Z0-9]+",
        host + parsed.path + parsed.query
    )

    found_terms = SUSPICIOUS_TERMS.intersection(
        part.lower() for part in parts
    )

    if found_terms:
        add(
            "Termos associados a contas",
            "Foram encontrados termos que podem aparecer em páginas de autenticação ou verificação. Isoladamente, não comprovam fraude.",
            "baixo", 5
        )

    if len(value) > 2048:
        add(
            "URL excessivamente longa",
            "O endereço possui comprimento incomum e merece verificação.",
            "baixo", 5
        )

    return indicators

