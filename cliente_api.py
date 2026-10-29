"""Modulo cliente_api - Consumo base y clasificacion de excepciones HTTP (Bloque 12)."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODELO}:generateContent?key={GEMINI_API_KEY}"
)
headers = {"Content-Type": "application/json"}


def armar_peticion(pregunta: str, system_instruction: str = "") -> dict:
    """Valida la entrada del usuario y construye el cuerpo JSON de la peticion."""
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia")

    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta.strip()}
                ]
            }
        ]
    }

    if system_instruction and system_instruction.strip():
        cuerpo["systemInstruction"] = {
            "parts": [
                {"text": system_instruction.strip()}
            ]
        }

    return cuerpo


def enviar_peticion(cuerpo: dict) -> dict:
    """Envia la peticion clasificando errores no recuperables (401/403) vs recuperables (429/5xx/red)."""
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if respuesta.status_code == 400:
        es_clave_invalida = False
        try:
            datos_err = respuesta.json()
            msg = datos_err.get("error", {}).get("message", "")
            if "API key" in msg or "API_KEY" in msg:
                es_clave_invalida = True
        except Exception:
            pass
        if es_clave_invalida:
            raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After") if hasattr(respuesta, "headers") else None
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite de peticiones excedido. Hay que esperar y reintentar."
        raise TimeoutError(mensaje)

    if respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")

    respuesta.raise_for_status()
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    """Extrae el contenido textual procesado desde la estructura de respuesta."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        # Soporte para respuestas mock o estructuras alternativas en tests
        if isinstance(datos, dict):
            if "texto" in datos:
                return datos["texto"]
            if "contenido" in datos:
                return datos["contenido"]
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


if __name__ == "__main__":
    print("=== Probando cliente_api directamente ===")
    try:
        cuerpo = armar_peticion("¿Cual es la capital de Chile?")
        resultado = enviar_peticion(cuerpo)
        print("[EXITO]:", extraer_texto(resultado))
    except (ValueError, TimeoutError) as e:
        print("[ERROR CAPTURADO]:", type(e).__name__, "-", e)
