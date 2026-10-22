import json
import sys
import time
from pathlib import Path

# Resolver la raiz del proyecto para importar src y prompts de forma limpia
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)
from prompts.banco import BANCO_DE_PROMPTS


def evaluar_consistencia_prompts(intentos: int = 3) -> dict:
    """Ejecuta cada prompt del banco multiples veces y registra la tasa de exito."""
    registro = {}
    print("=== INICIANDO SUITE DE PRUEBAS DE CONSISTENCIA ===")
    print(f"Total de prompts: {len(BANCO_DE_PROMPTS)} | Repeticiones por prompt: {intentos}\n")

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]
        print(f"Probando prompt '{nombre}'...")
        exitos = 0

        for intento in range(intentos):
            try:
                url, body = armar_peticion(
                    pregunta=prompt["ejemplo_usuario"],
                    system_instruction=prompt["system_instruction"],
                    response_schema=prompt.get("response_schema"),
                )
                respuesta = enviar_peticion(url, body)
                texto = extraer_texto(respuesta)
                datos = parsear_respuesta_json(texto, claves_requeridas=prompt["claves_esperadas"])

                if all(clave in datos for clave in prompt["claves_esperadas"]):
                    exitos += 1
                    print(f"  Intento {intento + 1}/{intentos}: Exito -> {datos}")
            except (ValueError, RuntimeError) as error:
                print(f"  Intento {intento + 1}/{intentos} fallo: {error}")

            # Pausa prudencial entre llamadas para evitar errores de tasa HTTP 429
            time.sleep(2)

        print(f"-> {nombre}: {exitos}/{intentos} respuestas validas\n")
        registro[nombre] = {
            "exitos": exitos,
            "intentos": intentos,
        }

    archivo_salida = ROOT_DIR / "prompts" / "registro_resultados.json"
    with open(archivo_salida, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)

    print(f"Registro persistido exitosamente en: {archivo_salida}")
    return registro


if __name__ == "__main__":
    evaluar_consistencia_prompts()
