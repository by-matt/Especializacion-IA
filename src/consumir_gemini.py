import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta: str) -> tuple[str, dict]:
    """Valida la entrada, lee credenciales y construye la URL y el body de la peticion."""
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
        resultado = obtener_dato_de_prueba("Confirma en una frase corta que esta conexion funciona")
        print("[RESPUESTA EXITOSA]:")
        print(resultado.strip())
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operacion:", error)
