"""
agent_agenda.py – Agent de Organização e Agenda
Integra com Trello para gerenciar tarefas e prioridades.

Aprenda LangGraph (ESSENCIAL para este arquivo):
  Tutorial oficial passo a passo: https://langchain-ai.github.io/langgraph/tutorials/introduction/
  Como criar agents com tools: https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.config import get_llm
from src.tools.trello_tools import get_trello_cards_today, get_trello_overdue_summary

# ── Prompt do Agente Agenda ──────────────────────────────────
SYSTEM_PROMPT = """Você é o Agent Agenda, especialista em organização e produtividade.
Seu papel é ajudar o usuário a entender sua situação de tarefas e agenda.

Você tem acesso às tarefas do Trello do usuário.

Ao responder:
- Seja direto e prático
- Priorize tarefas atrasadas e urgentes
- Sugira redistribuição quando a agenda estiver sobrecarregada
- Use emojis para facilitar a leitura
- Responda sempre em português brasileiro
"""

# ── Tools disponíveis para este agente ──────────────────────
TOOLS = [
    get_trello_cards_today,
    get_trello_overdue_summary,
]


def create_agenda_agent() -> AgentExecutor:
    """
    Cria e retorna o Agent Agenda pronto para uso.

    Como funciona:
    1. O LLM recebe a pergunta do usuário
    2. Decide quais tools chamar (Function Calling)
    3. Chama as tools e recebe os dados
    4. Gera a resposta final com base nos dados reais

    Referência: https://python.langchain.com/docs/how_to/agent_executor/
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
        verbose=True,          # Mostra o raciocínio interno (ótimo para aprender)
        max_iterations=5,
        handle_parsing_errors=True,
    )


# ── Teste rápido ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Testando Agent Agenda...")
    print("Certifique-se de ter o .env configurado com TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID\n")

    agent = create_agenda_agent()
    resposta = agent.invoke({"input": "Como está minha agenda hoje?"})
    print("\nResposta do agent:")
    print(resposta["output"])
