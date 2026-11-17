"""
Punto de Supervisión Humana (Human-in-the-Loop) con LangGraph (Bloque 32 - Paso 2)
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González

Implementa un flujo de control gobernado para el despliegue de prompts en producción:
- Nodo 'proponer': Registra la intención de despliegue con la huella candidata.
- Nodo 'supervisar': Emite un interrupt() que suspende el grafo hasta recibir autorización humana explícita.
- Nodo 'aplicar': Ejecuta la activación si la decisión es afirmativa, o preserva la versión anterior ante rechazo.
- Usa checkpointer para garantizar persistencia y aislamiento de hilos (thread_id).
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    print(f"nodo [proponer]: Evaluando despliegue de huella {estado['huella_nueva']}")
    return {}


def supervisar(estado: EstadoDespliegue):
    # Pausa la ejecución del grafo exponiendo el payload hacia el operador humano
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}


# Construcción y compilación del grafo con checkpointer en memoria
grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)

grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    # Huella obtenida de la versión fortificada (Paso 1)
    huella = "c2a733e19c0b"

    print("=== TEST 1: Invocación Inicial y Suspensión en interrupt() ===")
    config_1 = {"configurable": {"thread_id": "despliegue-prod-001"}}
    resultado_inicial = app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_1)
    print("1) tras invocar (estado pausado):", resultado_inicial)

    snapshot_1 = app_despliegue.get_state(config_1)
    print("2) pendiente en checkpointer:", snapshot_1.interrupts[0].value)

    print("\n=== TEST 2: Reanudación con Aprobación Humana (Command(resume=True)) ===")
    resultado_aprobado = app_despliegue.invoke(Command(resume=True), config=config_1)
    print("3) tras aprobar:", resultado_aprobado)

    print("\n=== TEST 3: Reanudación con Rechazo Humano (Command(resume=False)) ===")
    # Se debe usar un thread_id independiente para evitar colisión con el estado ya finalizado
    config_2 = {"configurable": {"thread_id": "despliegue-prod-002"}}
    app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_2)
    resultado_rechazado = app_despliegue.invoke(Command(resume=False), config=config_2)
    print("4) tras rechazar:", resultado_rechazado)
