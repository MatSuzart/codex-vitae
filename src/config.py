"""
config.py – Configuração central do projeto
Carrega variáveis de ambiente e inicializa o LLM escolhido.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Qual LLM usar ────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" ou "openai"


def get_llm(temperature: float = 0.0):
    """
    Retorna o LLM configurado.
    - Gemini Flash é gratuito no Google AI Studio (1M tokens/mês grátis).
    - GPT-4o mini é a opção mais barata da OpenAI (~$0.15 / 1M tokens input).

    Docs LangChain + Gemini: https://python.langchain.com/docs/integrations/chat/google_generative_ai/
    Docs LangChain + OpenAI: https://python.langchain.com/docs/integrations/chat/openai/
    """
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",   # Gratuito no AI Studio
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",        # Mais barato da OpenAI
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )


def get_embeddings():
    """
    Retorna o modelo de embeddings para o RAG (ChromaDB).

    Docs: https://python.langchain.com/docs/integrations/text_embedding/
    """
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    else:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
