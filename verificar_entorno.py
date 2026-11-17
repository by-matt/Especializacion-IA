"""
Verificación de Entorno y Pre-requisitos del Gate 2 (Bloque S1)
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González
"""

import os
import sys
from importlib.metadata import version, PackageNotFoundError

PAQUETES = ["langchain-core", "langchain-chroma", "langgraph", "python-dotenv"]
VARIABLES = ["GEMINI_API_KEY"]
INDICE_DIR = "indice_gate2"  # carpeta del vector store persistido

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

problemas = []
print("Python:", sys.version.split()[0])
if sys.version_info < (3, 10):
    problemas.append("usar Python 3.10 o superior")

for paquete in PAQUETES:
    try:
        print(f"{paquete}: {version(paquete)}")
    except PackageNotFoundError:
        print(f"{paquete}: NO instalado")
        problemas.append(f"instalar {paquete}")

for nombre in VARIABLES:
    estado = "definida" if os.getenv(nombre) else "FALTA"
    print(f"{nombre}: {estado}")
    if estado == "FALTA":
        problemas.append(f"definir {nombre} en el archivo .env")

if os.path.isdir(INDICE_DIR) and os.listdir(INDICE_DIR):
    print(f"indice en {INDICE_DIR}/: ok")
else:
    print(f"indice en {INDICE_DIR}/: NO existe o esta vacio")
    problemas.append("indexar el corpus")

print()
if problemas:
    print("Pendiente: " + "; ".join(problemas))
    sys.exit(1)

print("Entorno listo para la corrida final")
