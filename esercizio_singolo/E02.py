import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START


# 1. Definizione dello Stato
class State(TypedDict):
    testo: str
    testo_pulito: str
    num_parole: int
    num_caratteri: int
    report: str
    log: Annotated[list[str], operator.add]  # Reducer per concatenare la lista dei nodi


# 2. Definizione dei Nodi
def normalizza(state: State) -> dict:
    testo_normalizzato = " ".join(state["testo"].split()).lower()
    return {
        "testo_pulito": testo_normalizzato,
        "log": ["normalizza"]
    }


def conta(state: State) -> dict:
    testo = state["testo_pulito"]
    parole = testo.split()
    num_parole = len(parole)
    num_caratteri = len(testo.replace(" ", ""))
    return {
        "num_parole": num_parole,
        "num_caratteri": num_caratteri,
        "log": ["conta"]
    }


def crea_report(state: State) -> dict:
    report_str = (
        f"--- REPORT ---\n"
        f"Testo pulito : '{state['testo_pulito']}'\n"
        f"N. Parole   : {state['num_parole']}\n"
        f"N. Caratteri: {state['num_caratteri']}"
    )
    return {
        "report": report_str,
        "log": ["crea_report"]
    }


# 3. Costruzione del Grafo
builder = StateGraph(State)

# Collega in sequenza i nodi: normalizza -> conta -> crea_report
builder.add_sequence([normalizza, conta, crea_report])

# Collega START al primo nodo per definire l'entrypoint del grafo
builder.add_edge(START, "normalizza")

# Compilazione del grafo
app = builder.compile()


# 4. Esecuzione con 3 testi di prova
testi_di_prova = [
    "  Ciao   mondo!  Questo è   un TEST.  ",
    "PYTHON  e    LangGraph   sono    FANTASTICI! ",
    "   Un'altra    stringa   con    MOLTI   spazi   "
]

if __name__ == "__main__":
    for i, t in enumerate(testi_di_prova, 1):
        print(f"\n================ TEST {i} ================")
        
        risultato = app.invoke({"testo": t, "log": []})
        
        print(risultato["report"])
        print(f"Log: {risultato['log']}")
        
        # Verifica del requisito
        assert risultato["log"] == ['normalizza', 'conta', 'crea_report'], "Errore: il log non corrisponde!"