# Sentinela — Interface web + API

Aplicação demonstrativa para análise heurística de links e mensagens suspeitas.

## Executar no Fedora/Linux
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Abra **http://127.0.0.1:8000**. A documentação da API fica em `/docs`.

## O que está incluído
- Interface responsiva em português.
- Alternância entre análise de link e e-mail.
- Integração com os endpoints FastAPI.
- Exibição da pontuação, classificação, indicadores e recomendação.
- O backend analisa o texto da URL e não visita o endereço.

## Observação
A pontuação é heurística e educativa; não representa probabilidade comprovada de fraude. Poucos indicadores não significam que um link seja seguro.
