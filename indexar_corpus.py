"""
Indexación del corpus con chunking, embeddings y persistencia en Chroma (Bloque 24 - 25).
Autor: Byron Calderón González

Segmenta el corpus con RecursiveCharacterTextSplitter, genera embeddings
semánticos mediante GoogleGenerativeAIEmbeddings y persiste en Chroma DB
con metadatos explícitos e identificadores unívocos para recuperación y evaluación RAG.
"""

import os
import shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Corpus Canónico del Proyecto
# ---------------------------------------------------------------------------

CORPUS_CANONICO = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
    "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
]

DIRECTORIO_VECTORSTORE = "vectorstore/"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"


def indexar_corpus(
    corpus: list[str] = None,
    persist_directory: str = DIRECTORIO_VECTORSTORE,
    chunk_size: int = 200,
    chunk_overlap: int = 30,
    limpiar_existente: bool = True,
) -> Chroma:
    """Indexa una lista de documentos asignando metadatos e IDs explícitos."""
    if corpus is None:
        corpus = CORPUS_CANONICO

    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno o archivo .env.")

    # Si se solicita limpiar o si ya existe, borramos para evitar duplicados en Chroma
    if limpiar_existente and os.path.exists(persist_directory):
        print(f"Limpiando directorio vectorial previo: {persist_directory}")
        shutil.rmtree(persist_directory)

    # 1. Metadatos e IDs predecibles (esenciales para citas y evaluación de precisión/recall)
    metadatas = [{"fuente": f"doc{i}.md"} for i in range(len(corpus))]
    ids = [f"doc{i}" for i in range(len(corpus))]

    # 2. Chunking estructurado
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.create_documents(corpus, metadatas=metadatas)

    # 3. Cálculo de embeddings y persistencia en Chroma
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        persist_directory=persist_directory,
    )

    print(f"Reindexados {len(chunks)} chunks en {persist_directory}, ahora con metadata e ids")
    return vectorstore


def cargar_vectorstore(persist_directory: str = DIRECTORIO_VECTORSTORE) -> Chroma:
    """Reconecta de forma persistente con el almacén vectorial sin recalcular embeddings."""
    load_dotenv()
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )


if __name__ == "__main__":
    vs = indexar_corpus()
    total = vs._collection.count()
    print(f"Verificación exitosa: Total de {total} chunks persistidos en '{DIRECTORIO_VECTORSTORE}'.")
    assert total >= 5, f"Se esperaban al menos 5 documentos, se encontraron {total}."
