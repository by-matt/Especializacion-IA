"""Modulo cliente - Cliente modular resiliente con reintentos, backoff exponencial y telemetria de costo (Bloques 12-13)."""
import os
import time
import random
import requests
from dotenv import load_dotenv
from typing import Callable, Any
from cliente_api import armar_peticion, extraer_texto

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODELO}:generateContent?key={GEMINI_API_KEY}"
)
headers = {"Content-Type": "application/json"}


def enviar_peticion(cuerpo: dict) -> dict:
    """Realiza la llamada HTTP POST al proveedor clasificando fallos permanentes vs recuperables."""
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Verificar la variable GEMINI_API_KEY.")

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
            raise ValueError("Credencial inválida o sin permiso. Verificar la variable GEMINI_API_KEY.")

    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")

    respuesta.raise_for_status()
    return respuesta.json()


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Ejecuta una funcion con politica de reintentos mediante backoff exponencial y jitter aleatorio.
    
    Solo intercepta TimeoutError (errores transitorios). Si se agotan los intentos permitidos,
    deja propagar la excepcion original. Excepciones no transitorias como ValueError se propagan de inmediato.
    """
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


COSTO_POR_1000_TOKENS = 0.002  # Tarifa referencial FinOps por millar de tokens
costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float:
    """Calcula el costo monetario de la operacion segun tokens consumidos y lo acumula en la sesion."""
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {}) if isinstance(respuesta, dict) else {}
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    print(f"Operación: {total_tokens} tokens, costo estimado: ${costo_estimado:.5f} (acumulado: ${costo_total_sesion:.5f})")
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """Punto de entrada publico unificado: encapsula construccion, reintentos, costo y extraccion."""
    cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    print("=== INICIANDO PRUEBA NOMINAL DEL CLIENTE MODULAR ===")
    try:
        respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
        print("\n[RESPUESTA MODELO]:", respuesta.strip())
        print(f"[SESION FINOPS]: Costo acumulado de la sesión: ${costo_total_sesion:.5f}")
    except ValueError as error:
        print(f"[ERROR CONFIGURACION]: {error}")
    except RuntimeError as error:
        print(f"[FALLA SERVICIO TRAS REINTENTOS]: {error}")
