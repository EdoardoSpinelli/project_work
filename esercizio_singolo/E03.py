from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END


# 1. Definizione dello Stato
class State(TypedDict):
    a: float
    b: float
    op1: str
    c: float
    d: float
    op2: str
    risultato1: Optional[float]
    risultato2: Optional[float]
    errore: Optional[str]


# Dizionario con gli operatori (usiamo le lambda come suggerito)
OPERATORI = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}

def calcola_primo(state: State) -> dict:
    risultato = OPERATORI[state["op1"]](state["a"], state["b"])
    return {"risultato1": risultato}

def calcola_secondo(state: State) -> dict:
    risultato = OPERATORI[state["op2"]](state["c"], state["d"])
    return {"risultato2": risultato}


def esegui_operazione(a: float, b: float, op: str) -> tuple[Optional[float], Optional[str]]:
    if op not in OPERATORI:
        return None, f"Operatore '{op}' non valido"

    if op == "/" and b == 0:
        return None, "Divisione per zero non permessa"

    return OPERATORI[op](a, b), None


def controlla_operazione(op: str, divisore: float) -> Optional[str]:
    if op not in OPERATORI:
        return f"Operatore '{op}' non valido"
    if op == "/" and divisore == 0:
        return "Divisione per zero non permessa"
    return None


def router1(state: State) -> str:
    if controlla_operazione(state["op1"], state["b"]):
        return "errore"
    return "calcola_primo"


def router2(state: State) -> str:
    if controlla_operazione(state["op2"], state["d"]):
        return "errore"
    return "calcola_secondo"


def gestisci_errore(state: State) -> dict:
    messaggio = (
        controlla_operazione(state["op1"], state["b"])
        or controlla_operazione(state["op2"], state["d"])
    )
    return {"errore": messaggio}

builder = StateGraph(State)

builder.add_node("calcola_primo", calcola_primo)
builder.add_node("calcola_secondo", calcola_secondo)

builder.add_node("gestisci_errore", gestisci_errore)

builder.add_conditional_edges(
    START,
    router1,
    {
        "calcola_primo": "calcola_primo",
        "errore": "gestisci_errore",
    },
)

builder.add_conditional_edges(
    "calcola_primo",
    router2,
    {
        "calcola_secondo": "calcola_secondo",
        "errore": "gestisci_errore",
    },
)

builder.add_edge("calcola_secondo", END)
builder.add_edge("gestisci_errore", END)

grafo = builder.compile()


casi = [
    {"a": 10, "b": 2, "op1": "+", "c": 20, "d": 4, "op2": "/"},
    {"a": 10, "b": 0, "op1": "/", "c": 20, "d": 4, "op2": "+"},
    {"a": 10, "b": 2, "op1": "+", "c": 20, "d": 4, "op2": "%"},
    {"a": 10, "b": 2, "op1": "%", "c": 20, "d": 4, "op2": "+"},
    {"a": 10, "b": 2, "op1": "+", "c": 20, "d": 0, "op2": "/"},
]

for caso in casi:
    stato = {
        **caso,
        "risultato1": None,
        "risultato2": None,
        "errore": None,
    }
    risultato = grafo.invoke(stato)
    print(risultato)

print("\n--- GRAFO ---")
print(grafo.get_graph().draw_mermaid())
