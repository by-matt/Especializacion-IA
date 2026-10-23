import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(
    pregunta: str,
    system_instruction: str = None,
    response_schema: dict = None,
) -> tuple[str, dict]:
    """Valida la entrada, lee credenciales y construye la URL y el body de la peticion.
    
    Soporta opcionalmente instrucciones de sistema en un canal aislado ('systemInstruction')
    y restriccion de esquema JSON estructurado mediante 'generationConfig'.
    """
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "tu_clave_aqui"):
        raise ValueError(
            "No se encontró una clave válida en 'GEMINI_API_KEY'. "
            "Por favor crea tu archivo '.env' en la raíz copiando '.env.example' "
            "y agrega tu API key real obtenida en Google AI Studio (https://aistudio.google.com/)."
        )

    modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta.strip()}
                ]
            }
        ]
    }

    if system_instruction and system_instruction.strip():
        body["systemInstruction"] = {
            "parts": [
                {"text": system_instruction.strip()}
            ]
        }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, body


def enviar_peticion(url: str, body: dict, reintentos_por_modelo: int = 2) -> dict:
    """Envia la peticion HTTP capturando fallos de red y conmutando automaticamente de modelo ante 503 o 404."""
    import time

    # Identificar el modelo solicitado originalmente en la URL
    match_modelo = re.search(r"/models/([^:]+):", url)
    modelo_inicial = match_modelo.group(1) if match_modelo else "gemini-3.8-flash"

    # Cadena de failover ordenado: modelo inicial -> gemini-flash-latest -> gemini-2.5-flash
    cadena_modelos = [modelo_inicial]
    for candidato in ["gemini-flash-latest", "gemini-2.5-flash"]:
        if candidato not in cadena_modelos:
            cadena_modelos.append(candidato)

    ultimo_error = None

    for idx, modelo_actual in enumerate(cadena_modelos):
        # Ajustar la URL para el modelo en turno
        url_actual = re.sub(r"/models/[^:]+:", f"/models/{modelo_actual}:", url)

        for intento in range(reintentos_por_modelo):
            try:
                respuesta = requests.post(url_actual, json=body, timeout=30)
            except requests.exceptions.ConnectionError:
                raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
            except requests.exceptions.Timeout:
                if intento < reintentos_por_modelo - 1:
                    time.sleep(2)
                    continue
                ultimo_error = "El tiempo de espera con el servicio se agoto."
                break

            try:
                datos = respuesta.json()
            except requests.exceptions.JSONDecodeError:
                raise RuntimeError("La respuesta del servicio no llego en el formato esperado.")

            if "error" in datos:
                codigo = datos["error"].get("code", respuesta.status_code)
                mensaje = datos["error"].get("message", "Error devuelto por la API de Gemini.")
                ultimo_error = f"Error devuelto por la API de Gemini (HTTP {codigo}): {mensaje}"

                # Si el modelo esta saturado (503) o no disponible para la cuenta (404)
                if codigo in (503, 404):
                    # Si es 503 y queda intento en el mismo modelo, reintentamos brevemente
                    if codigo == 503 and intento < reintentos_por_modelo - 1:
                        time.sleep(2)
                        continue

                    # Si quedan modelos en la cadena de failover, conmutar automaticamente
                    if idx < len(cadena_modelos) - 1:
                        siguiente_modelo = cadena_modelos[idx + 1]
                        print(
                            f"\n[AUTO-FAILOVER]: Modelo '{modelo_actual}' no disponible ({codigo}). "
                            f"Conmutando automaticamente a '{siguiente_modelo}'..."
                        )
                        break  # Pasa al siguiente modelo en cadena_modelos

                # Errores no recuperables por cambio de modelo (ej. 400 credencial invalida o 429 cuota)
                raise RuntimeError(ultimo_error)

            return datos

    raise RuntimeError(ultimo_error or "No se pudo obtener respuesta valida de los modelos disponibles.")


def extraer_texto(datos: dict) -> str:
    """Navega el arbol de la respuesta JSON capturando posibles campos faltantes."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def parsear_respuesta_json(texto: str, claves_requeridas: list[str] = None) -> dict:
    """Sanitiza delimitadores markdown y parsea la respuesta a diccionario Python.
    
    Remueve bloques de markdown (```json ... ```) de forma tolerante a saltos de linea
    y verifica que la salida contenga las claves obligatorias requeridas.
    """
    if not texto:
        raise ValueError("El texto de respuesta esta vacio.")

    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON valido.")

    if claves_requeridas:
        for clave in claves_requeridas:
            if clave not in datos:
                raise ValueError(f"La respuesta no contiene la clave requerida: '{clave}'.")

    return datos


def calcular_costo(datos: dict, precio_entrada: float, precio_salida: float) -> float:
    """Calcula el costo monetario en USD a partir de usageMetadata y los precios por token."""
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
        return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
    except (KeyError, TypeError):
        raise RuntimeError("La respuesta no contiene 'usageMetadata' o los conteos de tokens esperados.")


def obtener_dato_de_prueba(pregunta: str) -> str:
    """Orquesta el flujo completo de consulta delegando en las funciones atomicas protegidas."""
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    print("=== TEST 1: Validacion preventiva de entrada vacia ===")
    try:
        obtener_dato_de_prueba("")
    except (ValueError, RuntimeError) as error:
        print("[CAPTURA CONTROLADA]:", error)

    print("\n=== TEST 2: Camino nominal exitoso con pregunta valida ===")
    try:
        url, body = armar_peticion("Confirma en una frase corta que esta conexion funciona")
        datos = enviar_peticion(url, body)
        resultado = extraer_texto(datos)
        print("[RESPUESTA EXITOSA]:")
        print(resultado.strip())
        
        # Metadatos de uso y costo en vivo (referencia gemini-2.5-flash)
        costo_real = calcular_costo(datos, 0.000000075, 0.00000030)
        tokens_in = datos["usageMetadata"]["promptTokenCount"]
        tokens_out = datos["usageMetadata"]["candidatesTokenCount"]
        print(f"[METRICAS EN VIVO]: Entrada: {tokens_in} tokens | Salida: {tokens_out} tokens | Costo: ${costo_real:.8f} USD")
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operacion:", error)

    print("\n=== TEST 3: Calculo de costo con metadatos sinteticos de la leccion ===")
    datos_leccion = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
            "totalTokenCount": 1170,
        }
    }
    costo_sintetico = calcular_costo(datos_leccion, 0.00000010, 0.00000040)
    print(f"[COSTO SINTETICO]: ${costo_sintetico:.6f} USD (Esperado exacto: $0.000213 USD)")

    print("\n=== TEST 4: Salida estructurada forzada con schema JSON (Bloque 10) ===")
    system_instruction = (
        "Responde unicamente con un objeto JSON valido, sin texto adicional "
        "y sin usar bloques de markdown. El JSON debe tener exactamente estas "
        "claves: 'categoria' (string) y 'confianza' (numero entre 0 y 1)."
    )
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "confianza": {"type": "NUMBER"},
        },
        "required": ["categoria", "confianza"],
    }
    pregunta_usuario = "Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación."
    try:
        url, body = armar_peticion(pregunta_usuario, system_instruction, response_schema)
        respuesta_json = enviar_peticion(url, body)
        texto = extraer_texto(respuesta_json)
        datos = parsear_respuesta_json(texto, claves_requeridas=["categoria", "confianza"])
        print("[DICCIONARIO PARSEADO]:", datos)
        print("[TIPO CONFIRMADO]:", type(datos))
        print(f"[ACCESO DIRECTO]: Categoria={datos['categoria']} | Confianza={datos['confianza']}")
    except (ValueError, RuntimeError) as error:
        print("Error en prueba de salida estructurada:", error)
