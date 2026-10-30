import uuid
from langchain_core.messages import SystemMessage, HumanMessage, trim_messages
from langchain_ollama import ChatOllama
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# 1. Definizione dello Stato (estende MessagesState aggiungendo personalita)
class State(MessagesState):
    personalita: str


# Inizializziamo il modello locale con Ollama (es. llama3, llama3.2, mistral, ecc.)
llm = ChatOllama(model="llama3.2:latest", temperature=0.7)


def chatbot_node(state: State) -> dict:
    messaggi_recenti = trim_messages(
        state["messages"],
        max_tokens=10,
        token_counter=len,
        strategy="last",
        start_on="human",
        include_system=False,
    )

    system_msg = SystemMessage(
        content=f"Personalità: {state['personalita']}"
    )

    risposta = llm.invoke([system_msg] + messaggi_recenti)

    return {"messages": [risposta]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

risultato = app.invoke(
    {
        "messages": [HumanMessage(content="Ciao, presentati.")],
        "personalita": "Sei un programmatore esperto di Python e AI, rispondi in modo conciso e chiaro.",
    },
    config=config,
)

print(risultato["messages"][-1].content)

if __name__ == "__main__":
    thread_id = str(uuid.uuid4())
    personalita = "Sei un programmatore esperto di Python e AI, rispondi in modo conciso e chiaro."

    print("Comandi: /nuova, /storia, /esci")

    while True:
        config = {"configurable": {"thread_id": thread_id}}
        testo = input("Tu > ").strip()

        if testo.lower() == "/esci":
            print("Alla prossima!")
            break

        if testo.lower() == "/nuova":
            thread_id = str(uuid.uuid4())
            print("Nuova conversazione avviata.")
            continue

        if testo.lower() == "/storia":
            stato = app.get_state(config)
            messaggi = stato.values.get("messages", [])
            for messaggio in messaggi:
                ruolo = "Tu" if messaggio.type == "human" else "Bot"
                print(f"{ruolo} > {messaggio.content}")
            continue

        if not testo:
            continue

        risultato = app.invoke(
            {
                "messages": [HumanMessage(content=testo)],
                "personalita": personalita,
            },
            config=config,
        )
        print(f"Bot > {risultato['messages'][-1].content}")