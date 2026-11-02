"""
Cadena de tres pasos encadenados con LangChain y LCEL.

Implementación diseñada para transformar un texto técnico en inglés,
resumir sus conceptos centrales y presentarlos en formato de viñetas Markdown.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def construir_cadena(modelo):
    """
    Construye y conecta una chain de tres pasos con responsabilidades delimitadas:
    1. Traducción técnica al español.
    2. Extracción y síntesis de ideas principales.
    3. Formateo estructurado a viñetas Markdown.
    """
    # Paso 1: Traducir manteniendo precisión técnica
    plantilla_traducir = PromptTemplate.from_template(
        "Traduce el siguiente texto técnico en inglés al español, "
        "manteniendo la fidelidad conceptual y un tono profesional:\n\n{texto}"
    )
    paso_traducir = plantilla_traducir | modelo | StrOutputParser()

    # Paso 2: Resumir ideas fundamentales
    plantilla_resumir = PromptTemplate.from_template(
        "Lee la siguiente traducción técnica y extrae las 3 ideas "
        "fundamentales, una por línea y sin introducción:\n\n{traduccion}"
    )
    paso_resumir = plantilla_resumir | modelo | StrOutputParser()

    # Paso 3: Formatear en lista de viñetas Markdown
    plantilla_formato = PromptTemplate.from_template(
        "Convierte estas ideas clave en una lista de viñetas Markdown "
        "concisa y lista para documentación ejecutiva, sin comentarios extra:\n\n{ideas}"
    )
    paso_formato = plantilla_formato | modelo | StrOutputParser()

    # Enlace secuencial de los tres pasos conectando salidas intermedias
    cadena = (
        paso_traducir
        | (lambda traduccion: {"traduccion": traduccion})
        | paso_resumir
        | (lambda ideas: {"ideas": ideas})
        | paso_formato
    )

    return cadena


if __name__ == "__main__":
    load_dotenv()
    # Instancio el modelo configurado con credenciales de entorno
    modelo = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    cadena = construir_cadena(modelo)

    texto_entrada = (
        "Retrieval-Augmented Generation (RAG) optimizes the output of a large language model "
        "by referencing an authoritative knowledge base outside of its training data sources "
        "before generating a response. This allows the model to deliver precise domain-specific "
        "answers while mitigating factual hallucinations and maintaining data privacy."
    )

    print("=== Entrada original (Inglés) ===")
    print(texto_entrada)
    print("\n=== Resultado tras los 3 pasos de la cadena ===")
    resultado = cadena.invoke({"texto": texto_entrada})
    print(resultado)
