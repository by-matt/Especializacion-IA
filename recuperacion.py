"""
Recuperación semántica y prompt dinámico con citas de fuentes (Bloque 26).
Autor: Byron Calderón González

Recupera los chunks más relevantes para una consulta desde el almacén vectorial Chroma,
estructura el bloque de contexto numerado para el prompt y genera el mapeo {numero: fuente}
que permite verificar la procedencia de cada afirmación.
"""

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:"""


def formatear_contexto(chunks_recuperados: list[Document]) -> tuple[str, dict[int, str]]:
    """Arma un bloque de contexto numerado para el prompt, y un mapa numero -> fuente
    para reconstruir la cita después."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(pregunta: str, persist_directory: str = "vectorstore/", k: int = 3) -> tuple[str, dict[int, str]]:
    """Recupera los k chunks más relevantes para la pregunta y arma el prompt dinámico
    con contexto numerado, listo para pasarle al modelo."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas


if __name__ == "__main__":
    print("=" * 60)
    print("DEMOSTRACIÓN DE CITAS SOBRE CHUNKS DE EJEMPLO")
    print("=" * 60)
    chunks_ejemplo = [
        Document(
            page_content="El cliente reintenta hasta 3 veces ante un TimeoutError.",
            metadata={"fuente": "doc0.md"},
        ),
        Document(
            page_content="El costo de cada llamada se calcula a partir de totalTokenCount.",
            metadata={"fuente": "doc2.md"},
        ),
    ]
    contexto_ejemplo, citas_ejemplo = formatear_contexto(chunks_ejemplo)
    print("Diccionario de citas generado:")
    print(citas_ejemplo)
    assert citas_ejemplo == {1: "doc0.md", 2: "doc2.md"}

    print("\n" + "=" * 60)
    print("CONSULTA REAL 1: Manejo de fallos en llamadas de red")
    print("=" * 60)
    pregunta_1 = "¿Qué hace el cliente si una llamada tarda demasiado tiempo?"
    prompt_1, citas_1 = construir_prompt(pregunta_1, persist_directory="vectorstore/", k=3)
    print("Prompt generado:")
    print(prompt_1)
    print("\nMapa de citas:")
    print(citas_1)
    assert len(citas_1) == 3
    assert all(v != "desconocida" for v in citas_1.values())

    print("\n" + "=" * 60)
    print("CONSULTA REAL 2: Cálculo financiero de llamadas")
    print("=" * 60)
    pregunta_2 = "¿Cómo se calcula el costo de una llamada?"
    prompt_2, citas_2 = construir_prompt(pregunta_2, persist_directory="vectorstore/", k=3)
    print("Prompt generado:")
    print(prompt_2)
    print("\nMapa de citas:")
    print(citas_2)
    assert len(citas_2) == 3
    assert all(v != "desconocida" for v in citas_2.values())

    print("\nVerificación de recuperación y armado de prompt con citas completada con éxito.")
