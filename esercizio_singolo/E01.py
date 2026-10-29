import sys
from langgraph.graph import StateGraph, START, END

# Usiamo un dict normale o una classe semplice al posto di TypedDict
# (un junior spesso preferisce un dict standard per semplicita)

# 1. Definizione della funzione del nodo
def componi_scheda(state):
    # Prendo i dati uno alla volta dallo stato
    nome_utente = state.get("nome")
    ruolo_utente = state.get("ruolo")
    lista_competenze = state.get("competenze")
    
    # Calcolo quante competenze ci sono
    quante_competenze = len(lista_competenze)
    
    # Ciclo o join per fare la stringa delle competenze
    stringa_competenze = ""
    for i in range(len(lista_competenze)):
        if i == 0:
            stringa_competenze = lista_competenze[i]
        else:
            stringa_competenze = stringa_competenze + ", " + lista_competenze[i]
    
    # Creo il testo della scheda finale concatenando le stringhe
    testo = "Nome: " + str(nome_utente) + "\n"
    testo = testo + "Ruolo: " + str(ruolo_utente) + "\n"
    testo = testo + "Competenze (" + str(quante_competenze) + "): " + stringa_competenze
    
    # Creo un nuovo dizionario da restituire per aggiornare lo stato
    risultato = {}
    risultato["scheda"] = testo
    
    return risultato


# ==================================================
# TEST DEL NODO (PROVA MANUALE)
# ==================================================
print("--- INIZIO TEST NODO ---")
dati_test = {
    "nome": "Edoardo",
    "ruolo": "Spinelli",
    "competenze": ["Python", "SQL", "LangGraph"],
    "scheda": ""
}

res = componi_scheda(dati_test)

# Controllo se funziona con degli if invece di assert
if "scheda" in res:
    print("La chiave 'scheda' esiste nel risultato!")

if "Competenze (3): Python, SQL, LangGraph" in res["scheda"]:
    print("✅ TEST SUPERATO!")
else:
    print("❌ TEST FALLITO!")

print("------------------------\n")


# ==================================================
# CREAZIONE DEL GRAFO
# ==================================================
# Creo il builder del grafo usando dict come stato
builder = StateGraph(dict)

# Aggiungo il nodo
builder.add_node("componi_scheda", componi_scheda)

# Collego lo START al nodo e il nodo al END
builder.add_edge(START, "componi_scheda")
builder.add_edge("componi_scheda", END)

# Compilo il grafo
grafo = builder.compile()


# ==================================================
# ESECUZIONE MAIN
# ==================================================
if __name__ == "__main__":
    
    # Dati di input
    dati_in = {
        "nome": "Marco Rossi",
        "ruolo": "AI Engineer",
        "competenze": ["Python", "SQL", "LangGraph"],
        "scheda": ""
    }
    
    print("Eseguo il grafo...")
    output_grafo = grafo.invoke(dati_in)
    
    print("\n--- RISULTATO FINALE ---")
    print(output_grafo)
    
    print("\n--- SCHEDA STAMPATA ---")
    print(output_grafo["scheda"])
    
    print("\n--- CODICE MERMAID ---")
    try:
        codice_mermaid = grafo.get_graph().draw_mermaid()
        print(codice_mermaid)
    except:
        print("Errore: Impossibile generare il diagramma Mermaid.")