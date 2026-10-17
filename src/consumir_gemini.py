import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta: str) -> tuple[str, dict]:
    """Lee credenciales y construye la URL del endpoint junto con el payload de la consulta."""
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }
    return url, body


def enviar_peticion(url: str, body: dict) -> dict:
    """Ejecuta la peticion HTTP POST contra la API y retorna la respuesta deserializada en JSON."""
    respuesta = requests.post(url, json=body)
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    """Navega el arbol de la respuesta JSON de Gemini y extrae el texto generado."""
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def obtener_dato_de_prueba(pregunta: str) -> str:
    """Orquesta el flujo completo de consulta delegando en funciones atomicas de responsabilidad unica."""
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    pregunta_prueba = "Confirma en una frase corta que esta conexion funciona"
    print("Enviando consulta refactorizada a Gemini...")
    resultado = obtener_dato_de_prueba(pregunta_prueba)
    print("\n[RESPUESTA]:")
    print(resultado.strip())
