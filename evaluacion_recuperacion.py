"""
Evaluación de la recuperación RAG: precisión@k, recall@k y promedios sobre conjunto de evaluación (Bloque 27).
Autor: Byron Calderón González

Evalúa sistemáticamente la efectividad del retriever semántico contra un conjunto
de preguntas etiquetadas manualmente, persistiendo los resultados en resultados_evaluacion.txt.
"""

import os
from datetime import date
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Constantes de configuración de la evaluación
K = 3
PERSIST_DIRECTORY = "vectorstore/"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"
ARCHIVO_RESULTADOS = "resultados_evaluacion.txt"

# ---------------------------------------------------------------------------
# Conjunto de Evaluación Etiquetado Manualmente (8 a 15 casos diversos)
# ---------------------------------------------------------------------------

casos_evaluacion = [
    {
        "pregunta": "¿Qué hace el cliente si una llamada tarda demasiado tiempo?",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "¿Cuántas veces se reintenta ante un TimeoutError?",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "¿Qué ocurre si la clave de API es inválida o falla la autenticación?",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "¿Se reintentan los errores de autenticación en la plataforma?",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "¿Cómo se calcula el costo de una llamada al modelo?",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "¿Qué métricas se usan para tarifar cada mil tokens consumidos?",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "¿Cómo decide el agente autónomo qué herramienta debe utilizar?",
        "ids_relevantes": {"doc3"},
    },
    {
        "pregunta": "¿El agente de la Unidad 2.4 requiere intervención para elegir su herramienta?",
        "ids_relevantes": {"doc3"},
    },
    {
        "pregunta": "¿Por qué la suite completa de pruebas unitarias corre en menos de un segundo?",
        "ids_relevantes": {"doc4"},
    },
    {
        "pregunta": "¿Qué base de datos relacional PostgreSQL se utiliza en producción?",
        "ids_relevantes": set(),  # Pregunta sin respuesta en el corpus: evalúa abstención y caso borde
    },
]


# ---------------------------------------------------------------------------
# Métricas Robustas ante Casos Borde
# ---------------------------------------------------------------------------

def precision_at_k(ids_recuperados: list[str], ids_relevantes: set[str]) -> float:
    """Fracción de los ids recuperados que son relevantes.
    Devuelve 0.0 si el retriever no devolvió ningún id."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados: list[str], ids_relevantes: set[str]) -> float | None:
    """Fracción de los ids relevantes que efectivamente se recuperaron.
    Devuelve None si el caso no tiene ids relevantes (pregunta sin respuesta en el corpus)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores) -> float:
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos: list[dict], k: int = 3):
    """Corre cada caso contra el retriever real y calcula precisión y recall."""
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({
            "pregunta": caso["pregunta"],
            "ids_recuperados": ids_recuperados,
            "ids_relevantes": caso["ids_relevantes"],
            "precision": p,
            "recall": r,
        })

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


# ---------------------------------------------------------------------------
# Ejecución Principal y Persistencia de Resultados
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(PERSIST_DIRECTORY):
        raise FileNotFoundError(f"Directorio {PERSIST_DIRECTORY} no existe. Ejecute indexar_corpus.py primero.")

    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": K})

    print(f"Iniciando evaluación de recuperación sobre {len(casos_evaluacion)} casos con k={K}...")
    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
        retriever, casos_evaluacion, k=K
    )

    print("\nResultados individuales:")
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}")

    print(f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}")

    # Guardado en resultados_evaluacion.txt
    with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n\n")
        for r in resultados:
            recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
            archivo.write(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}\n")
        archivo.write(
            f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}\n"
        )

    print(f"\nResultados guardados en {ARCHIVO_RESULTADOS}")
