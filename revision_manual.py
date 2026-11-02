"""Script de revision cualitativa manual sobre muestra de evaluaciones (Bloque 17 - Actividad Core).

Aplica la rubrica de tres criterios (correccion factual, completitud y contradiccion)
sobre una muestra estratificada de 10 casos (5 con menor F1 y 5 con mayor F1),
documentando por que la metrica numerica puede ser enganosa (falsos positivos y falsos negativos).
"""
import json
from pathlib import Path

revision_manual = [
    # --- 5 CASOS CON MENOR F1 (Falsos negativos / penalizacion por sinonimos) ---
    {
        "consulta": "¿Qué hace la sentencia break en un bucle?",
        "f1": 0.3158,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Falso negativo por paráfrasis: la respuesta usa 'interrumpe y sale del bucle' "
            "en lugar de 'termina inmediatamente la ejecución'. El significado es idéntico "
            "y técnicamente correcto, pero la métrica léxica la castiga con un F1 muy bajo (0.31)."
        ),
    },
    {
        "consulta": "¿Qué es un entorno virtual en Python?",
        "f1": 0.3200,
        "correccion_factual": "si",
        "completitud": "parcialmente",
        "contradiccion": "no",
        "nota": (
            "La respuesta explica acertadamente que aísla dependencias de librerías globales, "
            "pero omite mencionar que se implementa como un directorio en el sistema de archivos."
        ),
    },
    {
        "consulta": "¿Para qué sirve la función len en Python?",
        "f1": 0.3448,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Falso negativo por sinónimos técnicos: la respuesta emplea 'número total de elementos' "
            "y 'secuencia' en lugar de 'cantidad de elementos' y 'colección'. Semánticamente es exacta."
        ),
    },
    {
        "consulta": "¿Para qué se utiliza el bloque try except?",
        "f1": 0.3448,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Respuesta técnicamente impecable. Penalizada por coincidencia léxica al utilizar "
            "'gestionar errores y excepciones' en vez de 'capturar y manejar de forma controlada'."
        ),
    },
    {
        "consulta": "¿Cuál es el valor booleano de una lista vacía?",
        "f1": 0.3636,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "La respuesta es correcta (False). Coinciden pocas palabras exactas porque la respuesta "
            "emplea 'lista sin elementos tiene valor de verdad' en lugar de la redacción de referencia."
        ),
    },
    # --- 5 CASOS CON MAYOR F1 (Verificacion de falsos positivos y fidelidad) ---
    {
        "consulta": "¿Cómo se define una función anónima en Python?",
        "f1": 0.5600,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Ambas oraciones coinciden en el token clave 'lambda' y en 'función anónima'. "
            "La respuesta agrega valor contextual ('funciones pequeñas de una sola línea')."
        ),
    },
    {
        "consulta": "¿Qué es una lista en Python?",
        "f1": 0.6667,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Alta coincidencia de términos clave ('colección', 'ordenada', 'elementos'). "
            "Usa 'mutable' como sinónimo directo de 'modificable' y agrega que admite duplicados."
        ),
    },
    {
        "consulta": "¿Qué es una tupla en Python?",
        "f1": 0.7273,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Coincidencia alta y precisa. Los conceptos ordenado e inmutable están presentes "
            "tanto en la referencia como en la respuesta."
        ),
    },
    {
        "consulta": "¿Cuándo se creó Python?",
        "f1": 0.8182,
        "correccion_factual": "parcialmente",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Caso crítico de riesgo factual: F1 alto (0.82) pero introduce dos fechas distintas "
            "(creación en 1989 y lanzamiento en 1991). Aunque es históricamente preciso, "
            "evidencia que un F1 alto puede enmascarar discrepancias en datos verificables si el resto coincide."
        ),
    },
    {
        "consulta": "¿Qué es Python?",
        "f1": 0.8696,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": (
            "Respuesta de muy alta fidelidad. Comparte casi todos los tokens cardinales "
            "('lenguaje', 'programación', 'interpretado', 'alto', 'nivel') y complementa con 'propósito general'."
        ),
    },
]


def exportar_revision(ruta_salida: str = "revision_manual.json") -> None:
    """Serializa la revision manual en un archivo JSON estructurado con indentacion UTF-8."""
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)
    print(f"Revision manual exportada exitosamente a '{ruta_salida}' ({len(revision_manual)} casos).")


if __name__ == "__main__":
    exportar_revision()
