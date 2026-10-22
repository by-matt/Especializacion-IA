"""Punto de entrada principal para la ejecucion de la miniaplicacion - Gate 1."""
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
    calcular_costo,
)


def main():
    print("=== INICIANDO MINIAPLICACION - GATE 1 ===")
    pregunta = "Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación."
    system_instruction = (
        "Responde únicamente con un objeto JSON válido, sin texto adicional "
        "y sin usar bloques de markdown. El JSON debe tener exactamente estas "
        "claves: 'categoria' (string) y 'confianza' (número entre 0 y 1)."
    )
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "confianza": {"type": "NUMBER"},
        },
        "required": ["categoria", "confianza"],
    }

    url, body = armar_peticion(pregunta, system_instruction, response_schema)
    respuesta = enviar_peticion(url, body)
    texto = extraer_texto(respuesta)
    datos = parsear_respuesta_json(texto, claves_requeridas=["categoria", "confianza"])

    print("\n[CONSULTA PROCESADA]:", pregunta)
    print("[RESPUESTA ESTRUCTURADA DEL MODELO]:", datos)
    print(f"[ACCESO DIRECTO]: Categoria={datos['categoria']} | Confianza={datos['confianza']}")

    # Metricas FinOps en vivo (referencia gemini-2.5-flash)
    costo = calcular_costo(respuesta, 0.000000075, 0.00000030)
    tokens_in = respuesta["usageMetadata"]["promptTokenCount"]
    tokens_out = respuesta["usageMetadata"]["candidatesTokenCount"]
    print(f"\n[METRICAS DE CONSUMO]: {tokens_in} tokens entrada | {tokens_out} tokens salida | Costo: ${costo:.8f} USD")
    print("\nProceso terminado sin errores.")


if __name__ == "__main__":
    main()
