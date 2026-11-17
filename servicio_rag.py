"""
Servicio RAG Modular Integrado para el Gate 2 (Bloque S1)
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González

Integra todos los componentes construidos a lo largo del Módulo 2:
1. Pipeline RAG de extremo a extremo (U2.5):
   - Almacenamiento vectorial persistente e incremental con Chroma.
   - Recuperación semántica de chunks relevantes y citación de fuentes respaldadas.
2. Observabilidad y Trazabilidad (U2.7 - Bloque 31):
   - Trazabilidad determinista por consulta vía contextvars (trace_id).
   - Logging estructurado en JSON con metadatos sanitizados (longitudes y conteos).
   - Telemetría de consumo de tokens LLM (usage_metadata).
3. Seguridad Defensiva contra Inyección de Prompt (U2.7 - Bloque 31):
   - Análisis de patrones regex sobre la interfaz oficial de Document (page_content).
   - Ruta segura de contención ante ausencia de contexto verificado.
4. Gobernanza Técnica y Human-in-the-Loop (U2.7 - Bloque 32):
   - Flujo de control con LangGraph, interrupt() determinista y checkpointer en memoria.
"""

import contextvars
import json
import logging
import re
import sys
import uuid
from typing import TypedDict

try:
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_core.embeddings import DeterministicFakeEmbedding
    from langchain_core.language_models.fake import FakeListLLM
    from langchain_core.messages import AIMessage
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import interrupt, Command
except ImportError as e:
    sys.exit(f"Falta una dependencia ({e}). Instala con: pip install langchain-core langchain-chroma langgraph")

INDICE_DIR = "indice_gate2"

# ---------- Logging estructurado con trace_id
trace_id_var = contextvars.ContextVar("trace_id", default=None)
logger = logging.getLogger("servicio_rag")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
# Permitir propagación para captura determinista en pruebas unitarias y caplog
logger.propagate = True


def evento(auditoria, nombre, **campos):
    """Escribe un log JSON sanitizado y lo añade a la traza de auditoría en memoria."""
    registro = {"evento": nombre, "trace_id": trace_id_var.get(), **campos}
    logger.info(json.dumps(registro, ensure_ascii=False))
    auditoria.append(registro)


# ---------- Indexación persistida: no se reconstruye en cada corrida
CORPUS = [
    Document(
        page_content="Politica de devoluciones: 30 dias desde la compra presentando boleta o factura.",
        metadata={"fuente": "manual.pdf"},
    ),
    Document(
        page_content="Politica de envios: 5 dias habiles a todo el pais mediante transporte certificado.",
        metadata={"fuente": "manual.pdf"},
    ),
]
embeddings = DeterministicFakeEmbedding(size=768)


def cargar_indice():
    """Carga el vector store de Chroma desde disco; si está vacío, indexa el corpus inicial."""
    vectorstore = Chroma(
        collection_name="gate2",
        embedding_function=embeddings,
        persist_directory=INDICE_DIR,
    )
    if vectorstore.get()["ids"]:
        return vectorstore, "indice_reutilizado"
    vectorstore.add_documents(CORPUS)
    return vectorstore, "indice_creado"


# ---------- Filtro de inyección (Bloque 31) sobre la interfaz real de Document
PATRONES_SOSPECHOSOS = [
    r"ignora(?:r|\s+las)?\s+(?:todas\s+las\s+)?instrucciones\s+(?:anteriores|previas)",
    r"nuevo\s+sistema\s*:",
    r"revela\s+tu\s+prompt",
]


def detectar_inyeccion(texto):
    return [p for p in PATRONES_SOSPECHOSOS if re.search(p, texto.lower())]


def filtrar_documentos_sospechosos(documentos):
    limpios, descartados = [], []
    for d in documentos:
        (descartados if detectar_inyeccion(d.page_content) else limpios).append(d)
    return limpios, descartados


# ---------- Pipeline: recuperar, filtrar, citar, generar, registrar consumo
llm = FakeListLLM(responses=["Segun el manual.pdf, la politica de devoluciones permite 30 dias."])
SIN_CONTEXTO = "No tengo informacion suficiente y verificada para responder esto."


def responder(pregunta, vectorstore, estado_indice):
    token = trace_id_var.set("trace-" + uuid.uuid4().hex[:8])
    auditoria = []
    try:
        # Registro sanitizado: solo longitud de la pregunta, nunca texto plano ni PII
        evento(auditoria, "consulta_recibida", pregunta_len=len(pregunta))
        evento(auditoria, estado_indice)

        documentos = vectorstore.as_retriever(search_kwargs={"k": 2}).invoke(pregunta)
        evento(auditoria, "documentos_recuperados", n=len(documentos))

        limpios, descartados = filtrar_documentos_sospechosos(documentos)
        if descartados:
            evento(auditoria, "documentos_descartados", n=len(descartados))

        if not limpios:
            evento(auditoria, "sin_contexto_confiable")
            return {
                "trace_id": trace_id_var.get(),
                "respuesta": SIN_CONTEXTO,
                "fuentes": [],
                "auditoria": auditoria,
            }

        contexto = "\n\n".join(f"[{d.metadata['fuente']}] {d.page_content}" for d in limpios)
        texto = llm.invoke(f"Contexto:\n{contexto}\n\nPregunta: {pregunta}")

        mensaje = AIMessage(
            content=texto,
            usage_metadata={"input_tokens": 180, "output_tokens": 22, "total_tokens": 202},
        )
        evento(auditoria, "consumo_llm", input_tokens=180, output_tokens=22)

        return {
            "trace_id": trace_id_var.get(),
            "respuesta": mensaje.content,
            "fuentes": sorted({d.metadata["fuente"] for d in limpios}),
            "auditoria": auditoria,
        }
    finally:
        trace_id_var.reset(token)


# ---------- Punto de supervisión humana (Bloque 32) con interrupt() y Command
class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    print("version", estado["huella_nueva"], "activada" if estado["aprobado"] else "rechazada, se mantiene la anterior")
    return {}


grafo = StateGraph(EstadoDespliegue)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


def main():
    print("=== INICIANDO SERVICIO RAG MODULAR (GATE 2) ===")
    vectorstore, estado_indice = cargar_indice()
    respuesta = responder("cual es la politica de devoluciones", vectorstore, estado_indice)

    print("\n--- RESPUESTA COMPLETA DEL SERVICIO ---")
    print(json.dumps(respuesta, ensure_ascii=False, indent=2))
    assert respuesta["fuentes"], "la respuesta debe citar al menos una fuente"

    print("\n--- PUNTO DE SUPERVISIÓN HUMANA (HITL) ---")
    config = {"configurable": {"thread_id": "gate2-despliegue-1"}}
    pausado = app_despliegue.invoke({"huella_nueva": "c2a733e19c0b", "aprobado": False}, config=config)
    assert "__interrupt__" in pausado, "el grafo debe pausarse en el punto de supervision"
    print("Pausado con éxito, pendiente:", pausado["__interrupt__"][0].value)

    final = app_despliegue.invoke(Command(resume=True), config=config)
    print("Estado final tras resolución humana:", final)
    print("\nProceso terminado sin errores.")


if __name__ == "__main__":
    main()
