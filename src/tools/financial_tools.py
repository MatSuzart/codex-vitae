"""
financial_tools.py – Tools do Agent Financeiro
Versão 1: usa um arquivo CSV como fonte de dados (fácil de começar).
Versão 2 (futura): integrar com Pluggy (Open Finance BR) https://pluggy.ai/

Formato esperado do CSV (coloque em data/extrato.csv):
  data,descricao,valor,categoria
  2024-01-05,Mercado,-250.00,Alimentação
  2024-01-06,Salário,5000.00,Renda
  2024-01-07,Uber,-35.00,Transporte

Aprenda sobre pandas (necessário aqui):
  https://pandas.pydata.org/docs/getting_started/10min.html
"""
import os
import pandas as pd
from pathlib import Path
from langchain.tools import tool
from datetime import date

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "extrato.csv"
CURRENCY  = os.getenv("CURRENCY", "BRL")
SYMBOL    = "R$" if CURRENCY == "BRL" else "$"


def _load_extrato() -> pd.DataFrame | None:
    """Carrega o CSV de extrato. Retorna None se não existir."""
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH, parse_dates=["data"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df


@tool
def get_monthly_summary() -> str:
    """
    Retorna um resumo financeiro do mês atual:
    - Total de entradas e saídas
    - Saldo do mês
    - Maiores categorias de gastos
    Use quando o usuário perguntar sobre finanças, gastos ou saúde financeira.
    """
    df = _load_extrato()
    if df is None:
        return (
            "Arquivo data/extrato.csv não encontrado.\n"
            "Crie o arquivo com colunas: data, descricao, valor, categoria\n"
            "Valores negativos = despesas | Positivos = receitas"
        )

    hoje = date.today()
    mes_atual = df[(df["data"].dt.month == hoje.month) & (df["data"].dt.year == hoje.year)]

    if mes_atual.empty:
        return f"Nenhuma transação registrada para {hoje.strftime('%B/%Y')}."

    entradas  = mes_atual[mes_atual["valor"] > 0]["valor"].sum()
    saidas    = mes_atual[mes_atual["valor"] < 0]["valor"].sum()
    saldo     = entradas + saidas

    # Top 3 categorias de gastos
    gastos = mes_atual[mes_atual["valor"] < 0].copy()
    gastos["valor_abs"] = gastos["valor"].abs()
    top_cat = gastos.groupby("categoria")["valor_abs"].sum().sort_values(ascending=False).head(3)

    emoji_saldo = "✅" if saldo >= 0 else "⚠️"
    lines = [
        f"💰 RESUMO FINANCEIRO – {hoje.strftime('%B/%Y')}",
        f"  Entradas : {SYMBOL} {entradas:,.2f}",
        f"  Saídas   : {SYMBOL} {abs(saidas):,.2f}",
        f"  Saldo    : {emoji_saldo} {SYMBOL} {saldo:,.2f}",
        "",
        "📊 Top 3 categorias de gastos:",
    ]
    for cat, val in top_cat.items():
        pct = (val / abs(saidas) * 100) if saidas != 0 else 0
        lines.append(f"  • {cat}: {SYMBOL} {val:,.2f} ({pct:.0f}% das saídas)")

    return "\n".join(lines)


@tool
def get_spending_alert(budget_limit: float = 3000.0) -> str:
    """
    Verifica se os gastos do mês estão dentro de um limite orçamentário.
    Retorna um alerta se os gastos ultrapassaram 80% do limite.
    Parâmetro: budget_limit = limite mensal em reais (padrão: 3000.0).
    """
    df = _load_extrato()
    if df is None:
        return "Extrato não encontrado. Veja as instruções em financial_tools.py."

    hoje = date.today()
    mes_atual = df[(df["data"].dt.month == hoje.month) & (df["data"].dt.year == hoje.year)]
    saidas = abs(mes_atual[mes_atual["valor"] < 0]["valor"].sum())
    pct = (saidas / budget_limit * 100) if budget_limit > 0 else 0

    if pct >= 100:
        return f"🚨 ALERTA: Você ultrapassou o orçamento! Gastou {SYMBOL} {saidas:,.2f} de {SYMBOL} {budget_limit:,.2f} ({pct:.0f}%)"
    elif pct >= 80:
        restante = budget_limit - saidas
        return f"⚠️ ATENÇÃO: {pct:.0f}% do orçamento usado. Restam {SYMBOL} {restante:,.2f} até o fim do mês."
    else:
        restante = budget_limit - saidas
        return f"✅ Finanças OK: {pct:.0f}% do orçamento usado. {SYMBOL} {restante:,.2f} disponíveis."
