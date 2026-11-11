"""
Lector y analizador de registros de latencia y costo (Bloque 28).
Autor: Byron Calderón González

Permite auditar el histórico de ejecuciones RAG almacenadas en registros_latencia_costo.jsonl.
"""

import json
import os

ARCHIVO_REGISTROS = "registros_latencia_costo.jsonl"


def analizar_registros(archivo: str = ARCHIVO_REGISTROS):
    if not os.path.exists(archivo):
        print(f"Archivo '{archivo}' no encontrado.")
        return

    print(f"Resumen de ejecuciones registradas en '{archivo}':\n")
    with open(archivo, "r", encoding="utf-8") as f:
        for i, linea in enumerate(f, start=1):
            if not linea.strip():
                continue
            r = json.loads(linea)
            tokens = r.get("tokens") or {}
            tokens_entrada = tokens.get("input_tokens", "N/A")
            tokens_salida = tokens.get("output_tokens", "N/A")
            total_ms = r.get("tiempo_total_ms", 0.0)
            k = r.get("k")
            pregunta = r.get("pregunta", "")[:40]
            print(f"[{i}] k={k} | in_tokens={tokens_entrada} | out_tokens={tokens_salida} | total={total_ms}ms | '{pregunta}'")


if __name__ == "__main__":
    analizar_registros()
