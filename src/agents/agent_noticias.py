"""
agent_noticias.py – Agent de Notícias e Bem-estar
Coleta e resume notícias personalizadas por tópico.

Documentação NewsAPI: https://newsapi.org/docs/endpoints/everything
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.config import get_llm
from src.tools.news_tools import get_top_news_by_topic, get_daily_news_briefing

SYSTEM_PROMPT = """Você é o Agent Notícias, curador de informações relevantes.
Seu papel é filtrar o ruído e entregar apenas o que realmente importa para o usuário.

Como você trabalha:
- Busca notícias nos temas de interesse do usuário
- Resume em linguagem simples e direta
- Destaca o que tem impacto prático na vida financeira ou pessoal
- Evita sensacionalismo e notícias negativas sem contexto útil
- Para cada notícia importante, explica em 1 linha por que ela é relevante

Responda sempre em português brasileiro.
Seja sintético: o briefing deve ser lido em menos de 5 minutos.
"""

TOOLS = [
    get_top_news_by_topic,
    get_daily_news_briefing,
]


def create_news_agent() -> AgentExecutor:
    """Cria o Agent Notícias."""
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )


if __name__ == "__main__":
    print("Testando Agent Notícias...")
    print("Certifique-se de ter NEWS_API_KEY no .env\n")

    agent = create_news_agent()
    resposta = agent.invoke({"input": "Me dê o briefing de notícias de hoje"})
    print("\nResposta do agent:")
    print(resposta["output"])
