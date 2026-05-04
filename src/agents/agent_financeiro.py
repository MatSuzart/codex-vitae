"""
agent_financeiro.py – Agent de Análise Financeira
Analisa gastos, alertas de orçamento e saúde financeira.

Aprenda sobre RAG com LangChain (para a memória financeira):
  https://python.langchain.com/docs/tutorials/rag/
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.config import get_llm
from src.tools.financial_tools import get_monthly_summary, get_spending_alert

SYSTEM_PROMPT = """Você é o Agent Financeiro, especialista em finanças pessoais.
Seu papel é analisar os dados financeiros do usuário e dar insights práticos.

Princípios que você segue:
- Regra 50/30/20: 50% necessidades, 30% desejos, 20% investimentos
- Alertar quando gastos estão fora de controle, sem julgamentos
- Sugerir ações concretas e possíveis de implementar
- Celebrar quando as finanças estão bem

Responda sempre em português brasileiro com dados reais do extrato.
Nunca invente números — use apenas os dados retornados pelas tools.
"""

TOOLS = [
    get_monthly_summary,
    get_spending_alert,
]


def create_financial_agent() -> AgentExecutor:
    """
    Cria o Agent Financeiro.

    Próxima evolução (Fase 4):
    - Adicionar RAG sobre histórico de meses anteriores
    - Integrar com Pluggy para dados bancários reais: https://docs.pluggy.ai/
    """
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
    print("Testando Agent Financeiro...")
    print("Certifique-se de ter o arquivo data/extrato.csv criado\n")

    agent = create_financial_agent()
    resposta = agent.invoke({"input": "Como estão minhas finanças este mês?"})
    print("\nResposta do agent:")
    print(resposta["output"])
