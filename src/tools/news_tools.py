"""
news_tools.py – Tools do Agent Notícias
Documentação da NewsAPI: https://newsapi.org/docs/endpoints/top-headlines

Plano gratuito da NewsAPI:
  - 100 requisições/dia
  - Notícias dos últimos 30 dias
  - Cadastro em: https://newsapi.org/register
"""
import os
import requests
from langchain.tools import tool
from datetime import date, timedelta

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_TOPICS  = os.getenv("NEWS_TOPICS", "finanças pessoais,saúde,tecnologia").split(",")

BASE_URL = "https://newsapi.org/v2"


@tool
def get_top_news_by_topic(topic: str) -> str:
    """
    Busca as principais notícias sobre um tópico específico.
    Use esta tool para buscar notícias relevantes ao usuário.
    Exemplos de tópico: 'finanças pessoais', 'saúde', 'tecnologia', 'mercado financeiro'.
    """
    params = {
        "q": topic,
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY,
        "from": (date.today() - timedelta(days=1)).isoformat(),
    }
    resp = requests.get(f"{BASE_URL}/everything", params=params)

    # Se não tiver notícias em PT, tenta em EN
    if resp.status_code != 200 or resp.json().get("totalResults", 0) == 0:
        params["language"] = "en"
        resp = requests.get(f"{BASE_URL}/everything", params=params)

    if resp.status_code != 200:
        return f"Erro ao buscar notícias: {resp.status_code}"

    articles = resp.json().get("articles", [])
    if not articles:
        return f"Nenhuma notícia encontrada para '{topic}' nas últimas 24h."

    lines = [f"📰 Notícias sobre '{topic}':"]
    for a in articles[:5]:
        titulo = a.get("title", "Sem título")
        fonte  = a.get("source", {}).get("name", "?")
        url    = a.get("url", "")
        lines.append(f"  • [{fonte}] {titulo}\n    {url}")

    return "\n".join(lines)


@tool
def get_daily_news_briefing() -> str:
    """
    Gera um briefing com as principais notícias do dia nos temas configurados pelo usuário.
    Use esta tool para gerar o resumo matinal completo.
    """
    all_news = []
    for topic in NEWS_TOPICS[:3]:  # Limita a 3 tópicos para não estourar a API
        topic = topic.strip()
        params = {
            "q": topic,
            "language": "pt",
            "sortBy": "publishedAt",
            "pageSize": 3,
            "apiKey": NEWS_API_KEY,
            "from": (date.today() - timedelta(days=1)).isoformat(),
        }
        resp = requests.get(f"{BASE_URL}/everything", params=params)
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            for a in articles[:3]:
                all_news.append({
                    "topic": topic,
                    "title": a.get("title", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "url": a.get("url", ""),
                })

    if not all_news:
        return "Não foi possível carregar notícias agora. Verifique sua NEWS_API_KEY."

    lines = [f"📰 BRIEFING DO DIA – {date.today().strftime('%d/%m/%Y')}\n"]
    current_topic = ""
    for n in all_news:
        if n["topic"] != current_topic:
            current_topic = n["topic"]
            lines.append(f"\n🏷️  {current_topic.upper()}")
        lines.append(f"  • [{n['source']}] {n['title']}")

    return "\n".join(lines)
