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


# Mappa degli operatori supportati (usando le lambda come da suggerimento)
OPERATORI = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}


# 2. Funzioni dei Nodi
def calcola_primo(state: State) -> dict:
    op = state["op1"]
    res = OPERATORI[op](state["a"], state["b"])
    return {"risultato1": res}


def calcola_secondo(state: State) -> dict:
    op = state["op2"]
    res = OPERATORI[op](state["c"], state["d"])
    return {"risultato2": res}


def gestisci_errore(state: State) -> dict:
    # Se un router ha impostato il messaggio di errore nel routing o lo rileva qui
    return {}


# 3. Funzioni di Routing (Conditional Edges)
def router1(state: State) -> str:
    op = state.get("op1")
    # Controllo operatore valido
    if op not in OPERATORI:
        state["errore"] = f"Operatore 1 sconosciuto: '{op}'"
        return "errore"
    # Controllo divisione per zero
    if op == "/" and state.get("b") == 0:
        state["errore"] = "Errore nel primo calcolo: divisione per zero!"
        return "errore"
    
    return "calcola_primo"


def router2(state: State) -> str:
    op = state.get("op2")
    # Controllo operatore valido
    if op not in OPERATORI:
        state["errore"] = f"Operatore 2 sconosciuto: '{op}'"
        return "errore"
    # Controllo divisione per zero
    if op == "/" and state.get("d") == 0:
        state["errore"] = "Errore nel secondo calcolo: divisione per zero!"
        return "errore"
    
    return "calcola_secondo"


# 4. Costruzione del Grafo
builder = StateGraph(State)

# Aggiunta dei nodi
builder.add_node("calcola_primo", calcola_primo)
builder.add_node("calcola_secondo", calcola_secondo)
builder.add_node("errore", gestisci_errore)

# Router 1 da START: calcola su a,b oppure errore
builder.add_conditional_edges(
    START,
    router1,
    {
        "calcola_primo": "calcola_primo",
        "errore": "errore"
    }
)

# Router 2 dopo il primo calcolo: calcola su c,d oppure errore
builder.add_conditional_edges(
    "calcola_primo",
    router2,
    {
        "calcola_secondo": "calcola_secondo",
        "errore": "errore"
    }
)

# Chiusura del grafo verso END
builder.add_edge("calcola_secondo", END)
builder.add_edge("errore", END)

# Compilazione
app = builder.compile()


# 5. Test di tutti i rami
if __name__ == "__main__":
    casi_di_test = [
        # Caso 1: Tutto corretto
        {"a": 10, "b": 2, "op1": "+", "c": 20, "d": 4, "op2": "/"},
        # Caso 2: Errore nel primo calcolo (divisione per zero)
        {"a": 10, "b": 0, "op1": "/", "c": 20, "d": 4, "op2": "+"},
        # Caso 3: Errore nel primo calcolo (operatore sconosciuto)
        {"a": 10, "b": 2, "op1": "%", "c": 20, "d": 4, "op2": "+"},
        # Caso 4: Errore nel secondo calcolo (divisione per zero)
        {"a": 10, "b": 2, "op1": "*", "c": 20, "d": 0, "op2": "/"},
        # Caso 5: Errore nel secondo calcolo (operatore sconosciuto)
        {"a": 10, "b": 2, "op1": "-", "c": 20, "d": 4, "op2": "^"},
    ]

    for i, test in enumerate(casi_di_test, 1):
        print(f"\n================ TEST {i} ================")
        
        # Stato iniziale
        input_state = {
            **test,
            "risultato1": None,
            "risultato2": None,
            "errore": None
        }
        
        res = app.invoke(input_state)
        
        if res.get("errore"):
            print(f"❌ ERRORE: {res['errore']}")
        else:
            print(f"✅ Risultato 1: {res['risultato1']}")
            print(f"✅ Risultato 2: {res['risultato2']}")