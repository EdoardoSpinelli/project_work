from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. Definizione dello Stato
class State(TypedDict):
    nome: str
    ruolo: str
    competenze: list[str]
    scheda: str

# 2. Nodo del Grafo
def componi_scheda(state: State) -> dict:
    nome = state.get("nome", "Nome sconosciuto")
    ruolo = state.get("ruolo", "Ruolo sconosciuto")
    competenze = state.get("competenze", [])

    stringa_competenze = ", ".join(competenze) if competenze else "Nessuna competenza specificata"
    testo_scheda = (
        f"Nome: {nome}\n"
        f"Ruolo: {ruolo}\n"
        f"Competenze ({len(competenze)}): {stringa_competenze}"
    )
    return {"scheda": testo_scheda}


dati_test = {
    "nome": "Edoardo",
    "ruolo": "Studente",
    "competenze": ["Python", "SQL", "LangGraph"],
    "scheda": "",
}

risultato_test = componi_scheda(dati_test)
print(risultato_test["scheda"])


builder = StateGraph(State)

builder.add_node("componi_scheda", componi_scheda)
builder.add_edge(START, "componi_scheda")
builder.add_edge("componi_scheda", END)

grafo = builder.compile()

output_grafo = grafo.invoke(dati_test)
print(output_grafo["scheda"])
