import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
# Definizione dello stato della pipeline

class PipelineState(TypedDict):
    testo_originale: str
    testo_normalizzato: str
    num_parole: int
    num_caratteri_no_spazi: int
    report: str
    log: Annotated[list[str], operator.add]


def normalizza_testo(state: PipelineState) -> dict:
    testo = state.get("testo_originale")
    testo_normalizzato = " ".join(testo.split()).lower()
    return {
        "testo_normalizzato": testo_normalizzato,
        "log": [f"normalizza_testo: '{testo}' -> '{testo_normalizzato}'"]
        }

def conta_parole(state: PipelineState) -> dict:
    testo = state.get("testo_normalizzato")
    num_parole = len(testo.split())
    return {
        "num_parole": num_parole,
        "num_caratteri_no_spazi": len("".join(testo.split())),
        "log": [f"conta_parole: '{testo}' -> {num_parole}"]
    }

def crea_report(state: PipelineState) -> dict:
    num_parole = state.get("num_parole")
    testo = state.get("testo_normalizzato")
    num_caratteri_no_spazi = state.get("num_caratteri_no_spazi")
    report = f"Il testo normalizzato contiene {num_parole} parole e {num_caratteri_no_spazi} caratteri (esclusi gli spazi)."
    return {
        "report": report,
        "num_caratteri_no_spazi": num_caratteri_no_spazi,
        "log": [f"crea_report: {num_parole} parole, {num_caratteri_no_spazi} caratteri"]
    }


builder = StateGraph(PipelineState)

builder.add_node("normalizza_testo", normalizza_testo)
builder.add_node("conta_parole", conta_parole)
builder.add_node("crea_report", crea_report)

builder.add_edge(START, "normalizza_testo")
builder.add_edge("normalizza_testo", "conta_parole")
builder.add_edge("conta_parole", "crea_report")
builder.add_edge("crea_report", END)

app = builder.compile()

risultato = app.invoke({
    "testo_originale": "   Questo è un Esempio di Testo   ",
    "log": []
    })

print("=== RISULTATO FINALE ===")
print(f"Testo normalizzato: {risultato['testo_normalizzato']}")
print(f"Numero di parole: {risultato['num_parole']}")
print(f"Numero di caratteri (senza spazi): {risultato['num_caratteri_no_spazi']}")
print(f"Report: {risultato['report']}")
print(f"Log: {risultato['log']}")