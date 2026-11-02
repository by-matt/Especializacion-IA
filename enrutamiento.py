"""
Enrutamiento condicional y orquestación resiliente con LangChain.

Implementación modular para clasificar mensajes entrantes de soporte
y bifurcar hacia cadenas de destino especializadas (queja, sugerencia o pregunta),
incorporando mecanismos de fallback y tolerancia a fallos.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI

# Plantilla base para clasificar la intención del mensaje
plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola "
    "palabra: pregunta, queja o sugerencia. Responde solo "
    "con esa palabra.\n\n{mensaje}"
)


def construir_paso_clasificacion(modelo):
    """
    Construye el paso de clasificación asegurando normalización
    a minúsculas y eliminación de espacios en blanco.
    """
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )


def construir_cadenas_destino(modelo):
    """Genera las cadenas especializadas para cada ruta de soporte."""
    cadena_pregunta = (
        PromptTemplate.from_template(
            "Responde esta pregunta técnica con precisión:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    cadena_queja = (
        PromptTemplate.from_template(
            "Responde a esta queja con empatía, reconociendo el "
            "problema antes de ofrecer una solución:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    cadena_sugerencia = (
        PromptTemplate.from_template(
            "Agradece esta sugerencia y explica cómo se evaluará "
            "dentro del producto:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    return cadena_pregunta, cadena_queja, cadena_sugerencia


# Fallback estático general para mitigar fallas en rutas críticas
respuesta_generica = RunnableLambda(
    lambda x: (
        "Gracias por tu mensaje. Un miembro de nuestro "
        "equipo te va a responder pronto."
    )
)


def construir_cadena_queja_segura(cadena_queja):
    """Aplica protección con fallback a la ruta de atención de quejas."""
    return cadena_queja.with_fallbacks([respuesta_generica])


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """
    Construye la bifurcación condicional basada en RunnableBranch.
    Permite inyectar mocks o ejecutores alternativos en testing.
    """
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,
    )

    return RunnablePassthrough.assign(categoria=paso_clasificacion) | bifurcacion


def procesar_mensaje_seguro(cadena, mensaje):
    """
    Punto de entrada general con captura global de excepciones.
    Garantiza que ningún fallo impida devolver una respuesta amigable.
    """
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        print(f"Error procesando mensaje: {error}")
        return (
            "No pudimos procesar tu mensaje en este "
            "momento. Intenta de nuevo más tarde."
        )


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    paso_clasif = construir_paso_clasificacion(modelo)
    c_pregunta, c_queja, c_sugerencia = construir_cadenas_destino(modelo)
    c_queja_segura = construir_cadena_queja_segura(c_queja)

    cadena_flujo = construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasif,
        cadena_queja=c_queja_segura,
        cadena_sugerencia=c_sugerencia,
        cadena_pregunta=c_pregunta,
    )

    mensajes_prueba = [
        "¿Cómo cambio mi contraseña de acceso?",
        "La app se cierra sola cada vez que intento exportar el reporte mensual.",
        "Sería excelente que añadieran soporte para exportación en formato parquet.",
    ]

    for msg in mensajes_prueba:
        print(f"\n--- Mensaje: {msg} ---")
        respuesta = procesar_mensaje_seguro(cadena_flujo, msg)
        print(f"Respuesta: {respuesta}")
