"""
trello_tools.py – Tools do Agent Agenda para consultar o Trello
Documentação oficial da API do Trello: https://developer.atlassian.com/cloud/trello/rest/

Como obter as credenciais:
  1. Acesse https://trello.com/app-key → copie sua API Key
  2. Na mesma página, clique em "Token" → autorize → copie o Token
  3. Abra seu board no Trello, veja a URL: trello.com/b/BOARD_ID/nome
  4. Coloque as 3 infos no .env
"""
import os
import requests
from langchain.tools import tool
from datetime import date

TRELLO_KEY   = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID     = os.getenv("TRELLO_BOARD_ID")

BASE_URL = "https://api.trello.com/1"


def _auth_params() -> dict:
    return {"key": TRELLO_KEY, "token": TRELLO_TOKEN}


@tool
def get_trello_cards_today() -> str:
    """
    Busca todas as tarefas do Trello que vencem hoje ou estão atrasadas.
    Retorna uma lista formatada com nome, lista e data de vencimento.
    Use esta tool quando o usuário perguntar sobre tarefas do dia.
    """
    today = date.today().isoformat()

    # 1. Busca todas as listas do board
    lists_url = f"{BASE_URL}/boards/{BOARD_ID}/lists"
    lists_resp = requests.get(lists_url, params=_auth_params())
    lists_resp.raise_for_status()
    lists_data = {l["id"]: l["name"] for l in lists_resp.json()}

    # 2. Busca todos os cards do board
    cards_url = f"{BASE_URL}/boards/{BOARD_ID}/cards"
    cards_resp = requests.get(cards_url, params={**_auth_params(), "fields": "name,due,idList,closed"})
    cards_resp.raise_for_status()
    cards = cards_resp.json()

    # 3. Filtra: cards com due hoje ou atrasados, não arquivados
    results = []
    for card in cards:
        if card.get("closed"):
            continue
        due = card.get("due")
        if due and due[:10] <= today:
            list_name = lists_data.get(card["idList"], "?")
            status = "⚠️ ATRASADO" if due[:10] < today else "📅 HOJE"
            results.append(f"{status} | {card['name']} | Lista: {list_name} | Vence: {due[:10]}")

    if not results:
        return "Nenhuma tarefa vence hoje ou está atrasada no Trello."

    return f"Tarefas do dia ({len(results)} encontradas):\n" + "\n".join(results)


@tool
def get_trello_overdue_summary() -> str:
    """
    Retorna um resumo de quantas tarefas estão atrasadas por lista.
    Use para dar uma visão geral da saúde da agenda.
    """
    today = date.today().isoformat()

    lists_url = f"{BASE_URL}/boards/{BOARD_ID}/lists"
    lists_resp = requests.get(lists_url, params=_auth_params())
    lists_resp.raise_for_status()
    lists_data = {l["id"]: l["name"] for l in lists_resp.json()}

    cards_url = f"{BASE_URL}/boards/{BOARD_ID}/cards"
    cards_resp = requests.get(cards_url, params={**_auth_params(), "fields": "name,due,idList,closed"})
    cards_resp.raise_for_status()
    cards = cards_resp.json()

    overdue_by_list: dict[str, int] = {}
    for card in cards:
        if card.get("closed"):
            continue
        due = card.get("due")
        if due and due[:10] < today:
            list_name = lists_data.get(card["idList"], "?")
            overdue_by_list[list_name] = overdue_by_list.get(list_name, 0) + 1

    if not overdue_by_list:
        return "Nenhuma tarefa atrasada. Agenda em dia! ✅"

    total = sum(overdue_by_list.values())
    lines = [f"  • {lst}: {count} tarefa(s)" for lst, count in overdue_by_list.items()]
    return f"Total de tarefas atrasadas: {total}\n" + "\n".join(lines)
