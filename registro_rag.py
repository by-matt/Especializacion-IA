"""
Instrumentación de latencia y costo del flujo RAG completo (Bloque 28 - Actividad Core).
Autor: Byron Calderón González

Ejecuta el pipeline RAG de extremo a extremo (cálculo de embeddings, búsqueda vectorial en Chroma
y generación condicionada con Gemini), midiendo con precisión de microsegundos cada etapa
y capturando los metadatos reales de tokens consumidos en registros_latencia_costo.jsonl.
"""

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:"""

ARCHIVO_REGISTROS = "registros_latencia_costo.jsonl"
MODELO_CHAT = "gemini-3.5-flash-lite"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"


def formatear_contexto(chunks_recuperados):
    """Concatena los chunks con numeración entre corchetes para forzar citas."""
    lineas = []
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas)


@contextmanager
def medir(tiempos, etapa):
    """Context manager para instrumentar tiempos de ejecución precisos con perf_counter."""
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta: str, persist_directory: str = "vectorstore/", k: int = 3) -> dict:
    """Corre una consulta RAG real, midiendo tiempo por etapa y tokens reales de la respuesta del modelo."""
    tiempos = {}
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    chat_model = ChatGoogleGenerativeAI(model=MODELO_CHAT)

    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)
        contexto = formatear_contexto(chunks)
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
    }
    return registro


if __name__ == "__main__":
    if not os.path.exists("vectorstore/"):
        raise FileNotFoundError("Directorio 'vectorstore/' no encontrado. Ejecute indexar_corpus.py primero.")

    consultas_prueba = [
        ("¿Qué hace el cliente si hay un TimeoutError?", 3),
        ("¿Qué hace el cliente si hay un TimeoutError?", 5),  # Demuestra crecimiento de tokens de entrada con mayor k
        ("¿Cómo se calcula el costo de una llamada?", 3),
        ("¿Por qué las pruebas unitarias del cliente corren en menos de un segundo?", 3),
    ]

    print(f"Iniciando instrumentación de consultas RAG reales usando modelo '{MODELO_CHAT}'...")
    for pregunta, k_val in consultas_prueba:
        print(f"\n--- Ejecutando consulta (k={k_val}): '{pregunta}' ---")
        reg = registrar_consulta(pregunta, persist_directory="vectorstore/", k=k_val)
        print(json.dumps(reg, indent=2, ensure_ascii=False))

        with open(ARCHIVO_REGISTROS, "a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    print(f"\nRegistros persistidos exitosamente en '{ARCHIVO_REGISTROS}'.")
