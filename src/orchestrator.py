"""
orchestrator.py – Orchestrator Central (o cérebro do sistema)
Recebe a pergunta do usuário, decide quais agentes chamar e consolida as respostas.

Este é o arquivo mais importante do projeto.
Estude LangGraph ANTES de modificar este arquivo:
  Tutorial oficial: https://langchain-ai.github.io/langgraph/tutorials/introduction/
  Padrão Supervisor: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/

Como funciona o fluxo:
  Pergunta do usuário
       ↓
  Orchestrator (classifica a intenção)
       ↓
  ┌────────────────────────────────┐
  │  Agenda?  Finanças?  Notícias? │ ← pode chamar mais de um
  └────────────────────────────────┘
       ↓
  Consolida as respostas
       ↓
  Resposta final para o usuário
"""
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import get_llm
from src.agents.agent_agenda import create_agenda_agent
from src.agents.agent_financeiro import create_financial_agent
from src.agents.agent_noticias import create_news_agent

# ── Palavras-chave para classificar a intenção ───────────────
AGENDA_KEYWORDS   = ["agenda", "tarefa", "trello", "prazo", "vence", "atrasado", "semana", "reunião", "compromisso"]
FINANCIAL_KEYWORDS = ["gasto", "financ", "dinheiro", "orçamento", "extrato", "saldo", "pagar", "conta", "salário", "economiz"]
NEWS_KEYWORDS     = ["notícia", "news", "briefing", "hoje", "aconteceu", "mercado", "atualidade", "informação"]


def classify_intent(question: str) -> list[str]:
    """
    Classifica a intenção da pergunta e retorna lista de agentes a chamar.
    Versão simples: baseada em palavras-chave.
    Versão avançada (Fase 4): usar LLM para classificar com mais precisão.
    """
    q = question.lower()
    agents = []

    if any(kw in q for kw in AGENDA_KEYWORDS):
        agents.append("agenda")
    if any(kw in q for kw in FINANCIAL_KEYWORDS):
        agents.append("financeiro")
    if any(kw in q for kw in NEWS_KEYWORDS):
        agents.append("noticias")

    # Se não identificou nenhum, chama todos (pergunta geral como "status do dia")
    if not agents:
        agents = ["agenda", "financeiro", "noticias"]

    return agents


def run(question: str) -> str:
    """
    Ponto de entrada principal do sistema.
    Recebe uma pergunta e retorna a resposta consolidada.

    Exemplo de uso:
        from src.orchestrator import run
        resposta = run("Como está meu dia hoje?")
        print(resposta)
    """
    print(f"\n🎯 Pergunta recebida: {question}")

    # 1. Classifica a intenção
    agents_to_call = classify_intent(question)
    print(f"📋 Agentes selecionados: {', '.join(agents_to_call)}")

    # 2. Chama os agentes necessários
    responses = {}

    if "agenda" in agents_to_call:
        print("\n[Agent Agenda] Consultando Trello...")
        try:
            agent = create_agenda_agent()
            result = agent.invoke({"input": question})
            responses["agenda"] = result["output"]
        except Exception as e:
            responses["agenda"] = f"Erro no Agent Agenda: {e}"

    if "financeiro" in agents_to_call:
        print("\n[Agent Financeiro] Analisando finanças...")
        try:
            agent = create_financial_agent()
            result = agent.invoke({"input": question})
            responses["financeiro"] = result["output"]
        except Exception as e:
            responses["financeiro"] = f"Erro no Agent Financeiro: {e}"

    if "noticias" in agents_to_call:
        print("\n[Agent Notícias] Buscando notícias...")
        try:
            agent = create_news_agent()
            result = agent.invoke({"input": question})
            responses["noticias"] = result["output"]
        except Exception as e:
            responses["noticias"] = f"Erro no Agent Notícias: {e}"

    # 3. Consolida as respostas com um LLM
    if len(responses) == 1:
        # Apenas 1 agente foi chamado, retorna diretamente
        return list(responses.values())[0]

    # Múltiplos agentes: usa LLM para consolidar de forma coerente
    print("\n[Orchestrator] Consolidando respostas...")
    llm = get_llm()

    context_parts = []
    section_map = {"agenda": "📋 AGENDA", "financeiro": "💰 FINANÇAS", "noticias": "📰 NOTÍCIAS"}
    for key, resp in responses.items():
        context_parts.append(f"=== {section_map.get(key, key.upper())} ===\n{resp}")

    context = "\n\n".join(context_parts)

    consolidation_prompt = f"""Você é um assistente pessoal que consolida informações de múltiplas fontes.
Abaixo estão os dados coletados pelos agentes especializados.
Crie uma resposta unificada, clara e útil para a pergunta do usuário.

PERGUNTA ORIGINAL: {question}

DADOS DOS AGENTES:
{context}

INSTRUÇÕES:
- Organize por seção (📋 Agenda, 💰 Finanças, 📰 Notícias) se houver múltiplas
- Destaque os pontos mais importantes de cada área
- Sugira 1-2 ações práticas com base nos dados
- Seja direto, máximo 300 palavras no total
- Responda em português brasileiro
"""

    messages = [HumanMessage(content=consolidation_prompt)]
    response = llm.invoke(messages)

    return response.content


# ── Teste rápido ─────────────────────────────────────────────
if __name__ == "__main__":
    perguntas_teste = [
        "Como está meu dia hoje?",
        "Como estão minhas finanças?",
        "Me dê as notícias de hoje",
    ]

    for pergunta in perguntas_teste:
        print("\n" + "=" * 60)
        resposta = run(pergunta)
        print(f"\n✅ RESPOSTA FINAL:\n{resposta}")
        print("=" * 60)
        input("\nPressione Enter para a próxima pergunta...")
