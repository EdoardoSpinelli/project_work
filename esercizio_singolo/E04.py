import operator
import random
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END


# 1. Definizione dello Stato
class State(TypedDict):
    numero_segreto: int
    min_val: int
    max_val: int
    tentativi: int
    ipotesi_corrente: int
    esito: str
    storico_ipotesi: Annotated[list[int], operator.add]  # Reducer per salvare i tentativi


# 2. Nodi del Grafo
def setup(state: State) -> dict:
    numero_segreto = state.get("numero_segreto")
    if numero_segreto is None:
        numero_segreto = random.randint(1, 100)

    return {
        "numero_segreto": numero_segreto,
        "min_val": 1,
        "max_val": 100,
        "tentativi": 0,
        "esito": "",
        "storico_ipotesi": [],
    }


def indovina(state: State) -> dict:
    ipotesi = (state["min_val"] + state["max_val"]) // 2
    tentativi = state["tentativi"] + 1
    storico_ipotesi = [ipotesi] + state["storico_ipotesi"]
    return {
        "ipotesi_corrente": ipotesi, 
        "tentativi": tentativi, 
        "storico_ipotesi": [ipotesi],
        }


def suggerisci(state: State) -> dict:
    ipotesi = state["ipotesi_corrente"]
    segreto = state["numero_segreto"]

    if ipotesi == segreto:
        return {"esito": "indovinato"}
    elif ipotesi < segreto:
        return {"esito": "più alto", "min_val": ipotesi + 1}
    else:
        return {"esito": "più basso", "max_val": ipotesi - 1}


def controlla_esito(state: State) -> str:
    if state["esito"] == "indovinato" or state["tentativi"] >= 7:
        return "fine"
    return "continua"

builder = StateGraph(State)

builder.add_node("setup", setup)
builder.add_node("indovina", indovina)
builder.add_node("suggerisci", suggerisci)

builder.add_edge(START, "setup")
builder.add_edge("setup", "indovina")
builder.add_edge("indovina", "suggerisci")

builder.add_conditional_edges(
    "suggerisci",
    controlla_esito,
    {
        "continua": "indovina",
        "fine": END,
    },
)

app = builder.compile()

risultato = app.invoke({
    "numero_segreto": 42,
    "storico_ipotesi": [],
})

print(f"Esito: {risultato['esito']}")
print(f"Tentativi: {risultato['tentativi']}")
print(f"Ipotesi: {risultato['storico_ipotesi']}")