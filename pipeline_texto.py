"""Modulo pipeline_texto - Pipeline de texto, NLP basico y evaluacion de salidas (Bloques 15-16).

Implementa la normalizacion (limpieza y tokenizacion) y las metricas formales de evaluacion
lexica basada en bolsa de palabras con conteo de repeticiones (Precision, Cobertura y F1).
"""
import re
from collections import Counter
from cliente import consultar_modelo


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: valida tipo str, pasa a minusculas, elimina puntuacion y colapsa espacios."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens separando por espacios."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Compone la limpieza y la tokenizacion en una sola llamada centralizada."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuantas veces aparece cada token (representacion bolsa de palabras)."""
    return Counter(tokens)


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta respetando repeticiones mediante interseccion de Counter."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precision, cobertura (recall) y F1 de dos listas de tokens de forma defensiva."""
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)
    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)
    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = (2 * precision * cobertura) / (precision + cobertura)

    return {
        "precision": round(precision, 4),
        "cobertura": round(cobertura, 4),
        "f1": round(f1, 4),
    }


def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    """Punto de entrada unificado: tokeniza ambos textos y calcula precision, cobertura y F1."""
    tokens_ref = procesar_texto(texto_referencia)
    tokens_resp = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_ref, tokens_resp)


def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Calcula promedios agregados de precision, cobertura y F1 sobre una lista de evaluaciones."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }
    n = len(resultados)
    return {
        "precision_promedio": round(sum(r["precision"] for r in resultados) / n, 4),
        "cobertura_promedio": round(sum(r["cobertura"] for r in resultados) / n, 4),
        "f1_promedio": round(sum(r["f1"] for r in resultados) / n, 4),
    }


if __name__ == "__main__":
    print("=== PIPELINE DE TEXTO Y EVALUACION (BLOQUE 15 Y 16) ===")

    casos = [
        (
            "¿Qué es Python?",
            "Python es un lenguaje de programación interpretado.",
        ),
        (
            "¿Cuándo se creó Python?",
            "Python fue creado en 1991.",
        ),
        (
            "¿Qué es una lista en Python?",
            "Una lista es una colección ordenada y modificable.",
        ),
    ]

    for idx, (consulta, referencia) in enumerate(casos, 1):
        print(f"\n--- [Caso {idx}] ---")
        print(f"Consulta: {consulta}")
        print(f"Referencia: {referencia}")

        try:
            respuesta = consultar_modelo(consulta)
        except Exception:
            respuesta = "Python es un lenguaje interpretado y dinámico."

        print(f"Respuesta: {respuesta}")

        # Comparacion antes/despues
        crudo_ref = referencia.split()
        crudo_resp = respuesta.split()
        comunes_crudo = set(crudo_ref) & set(crudo_resp)
        pct_crudo = len(comunes_crudo) / len(set(crudo_ref)) if crudo_ref else 0.0

        metricas = calcular_metricas(referencia, respuesta)
        print(f"Coincidencia cruda (set)   : {pct_crudo:.1%}")
        print(f"Metricas formales procesadas: {metricas}")
