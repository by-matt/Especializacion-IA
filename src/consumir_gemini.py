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
    modelo = "gemini-2.5-flash"
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


def enviar_peticion(url: str, body: dict) -> dict:
    """Envia la peticion HTTP capturando fallos de conexion y decodificacion JSON."""
    try:
        respuesta = requests.post(url, json=body, timeout=15)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    except requests.exceptions.Timeout:
        raise RuntimeError("El tiempo de espera con el servicio se agoto. Intenta de nuevo.")

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llego en el formato esperado.")


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
