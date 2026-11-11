"""
Agente con herramientas propias, supervisión humana y traza de decisión (Bloque 21 - 23).
Autor: Byron Calderón González

Implementación de un agente para operaciones de infraestructura y devops.
Dispone de:
1. consultar_estado_servicio: Bajo riesgo. Lectura de estado y métricas.
2. calcular_costo_instancias: Bajo riesgo. Estimación presupuestaria.
3. reiniciar_servicio_critico: Alto riesgo. Requiere supervisión humana obligatoria (esperar_aprobacion).
Trazabilidad completa persistida en trazas_agente.jsonl con detección de bucles anómalos.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# ---------------------------------------------------------------------------
# Esquemas Pydantic para Validación Estricta de Entradas
# ---------------------------------------------------------------------------

class ArgumentosConsultaServicio(BaseModel):
    nombre_servicio: str = Field(
        ...,
        description="Nombre o identificador del microservicio a inspeccionar (ej: 'auth', 'pagos', 'database', 'notificaciones').",
    )


class ArgumentosCostoInstancias(BaseModel):
    instancias: int = Field(
        ...,
        description="Cantidad total de instancias de cómputo encendidas. Debe ser un entero mayor a cero.",
    )
    horas_mes: float = Field(
        720.0,
        description="Número de horas activas proyectadas en el mes (default 720.0 horas = 30 días continuos).",
    )
    precio_hora_usd: float = Field(
        0.096,
        description="Tarifa horaria por instancia en dólares estadounidenses (USD).",
    )


class ArgumentosReinicioServicio(BaseModel):
    nombre_servicio: str = Field(
        ...,
        description="Nombre del microservicio que se pretende reiniciar.",
    )
    motivo: str = Field(
        ...,
        description="Justificación técnica detallada del reinicio del servicio.",
    )


# ---------------------------------------------------------------------------
# Protocolo de Supervisión Humana (Human-in-the-Loop)
# ---------------------------------------------------------------------------

def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 30) -> bool:
    """Solicita confirmación explícita a un operador humano antes de ejecutar una acción de alto riesgo.
    En entornos automatizados de prueba o CI/CD respeta la variable AGENT_AUTO_APPROVE."""
    print(f"\n[ALERTA DE SUPERVISIÓN HUMANA - ACCIÓN CRÍTICA]")
    print(f"Detalle: {mensaje}")

    # Si se define en el entorno para pruebas automatizadas
    if os.environ.get("AGENT_AUTO_APPROVE", "").lower() in ("1", "true", "yes"):
        print("[SUPERVISIÓN] Aprobación concedida automáticamente por política de pruebas (AGENT_AUTO_APPROVE=1).")
        return True

    # Comprobación interactiva protegida para Windows y consolas no interactivas
    if not sys.stdin.isatty():
        print("[SUPERVISIÓN] Entorno no interactivo detectado. Rechazando por principio de menor privilegio.")
        return False

    try:
        respuesta = input(f"¿Autoriza esta operación dentro de los próximos {tiempo_limite_segundos}s? (s/N): ").strip().lower()
        aprobado = respuesta in ("s", "si", "y", "yes")
        print(f"[SUPERVISIÓN] Decisión del operador: {'APROBADO' if aprobado else 'RECHAZADO'}")
        return aprobado
    except Exception as err:
        print(f"[SUPERVISIÓN] Error al capturar entrada del operador: {err}. Operación denegada.")
        return False


# ---------------------------------------------------------------------------
# Herramientas del Agente con Tipado y Control de Riesgos
# ---------------------------------------------------------------------------

SERVICIOS_DISPONIBLES = {
    "auth": "Operativo (Uptime: 99.98%, Latencia promedio: 42ms)",
    "pagos": "Operativo (Uptime: 99.95%, Latencia promedio: 110ms)",
    "database": "En mantenimiento preventivo (Finalización estimada: 20 minutos)",
    "notificaciones": "Degradado (Cola de mensajes con demora de 3 minutos)",
}


@tool(args_schema=ArgumentosConsultaServicio)
def consultar_estado_servicio(nombre_servicio: str) -> str:
    """Consulta el estado operativo, salud y latencia de un microservicio de la plataforma.
    Nivel de riesgo: BAJO (Acción de solo lectura).
    Usar cuando el usuario pregunte por el estado, uptime, disponibilidad o problemas
    de un servicio técnico específico (por ejemplo: 'auth', 'pagos', 'database', 'notificaciones')."""
    clave = nombre_servicio.strip().lower()
    try:
        if clave in SERVICIOS_DISPONIBLES:
            return f"Servicio '{clave}': {SERVICIOS_DISPONIBLES[clave]}"
        for s_nombre, s_info in SERVICIOS_DISPONIBLES.items():
            if s_nombre in clave:
                return f"Servicio '{s_nombre}': {s_info}"
        return (
            f"No se encontró información del servicio '{nombre_servicio}'. "
            f"Servicios registrados: {', '.join(SERVICIOS_DISPONIBLES.keys())}."
        )
    except Exception as error:
        return f"Error consultando el estado del servicio: {error}"


@tool(args_schema=ArgumentosCostoInstancias)
def calcular_costo_instancias(instancias: int, horas_mes: float = 720.0, precio_hora_usd: float = 0.096) -> str:
    """Calcula el costo estimado de cómputo cloud según la cantidad de instancias activas,
    las horas estimadas de uso en el mes y la tarifa horaria en USD.
    Nivel de riesgo: BAJO (Cálculo determinista en memoria).
    Usar cuando el usuario requiera calcular presupuestos, gastos de infraestructura o costos de servidores."""
    try:
        if instancias <= 0:
            return "La cantidad de instancias debe ser un número entero positivo mayor a cero."
        if horas_mes < 0 or precio_hora_usd < 0:
            return "Las horas de uso y el precio por hora no pueden ser negativos."

        costo_total = instancias * horas_mes * precio_hora_usd
        return (
            f"Costo proyectado para {instancias} instancias durante {horas_mes:.1f} horas "
            f"a ${precio_hora_usd:.3f} USD/hora: ${costo_total:.2f} USD."
        )
    except Exception as error:
        return f"Error al calcular costos de infraestructura: {error}"


@tool(args_schema=ArgumentosReinicioServicio)
def reiniciar_servicio_critico(nombre_servicio: str, motivo: str) -> str:
    """Ejecuta el reinicio controlado de un microservicio crítico de producción.
    Nivel de riesgo: ALTO (Impacto potencial en la disponibilidad del sistema).
    Requiere obligatoriamente autorización de un operador humano previo a su ejecución."""
    clave = nombre_servicio.strip().lower()
    try:
        mensaje_autorizacion = (
            f"Solicitud de reinicio sobre '{clave}'. "
            f"Motivo técnico: {motivo}. Esta acción puede interrumpir transacciones activas."
        )
        autorizado = esperar_aprobacion(mensaje_autorizacion, tiempo_limite_segundos=30)
        if not autorizado:
            return f"Operación CANCELADA: El reinicio de '{clave}' fue rechazado por falta de aprobación humana."

        SERVICIOS_DISPONIBLES[clave] = "Reiniciado y Operativo (Uptime: 100%, Latencia promedio: 35ms)"
        return f"Éxito: El servicio '{clave}' ha sido reiniciado correctamente tras recibir aprobación humana."
    except Exception as error:
        return f"Error durante la solicitud de reinicio: {error}"


# ---------------------------------------------------------------------------
# Trazabilidad Estructurada y Detección de Bucles Anómalos
# ---------------------------------------------------------------------------

ARCHIVO_TRAZAS = "trazas_agente.jsonl"


def registrar_traza(
    entrada: str,
    salida: str,
    pasos_intermedios: list,
    archivo: str = ARCHIVO_TRAZAS,
) -> dict:
    """Registra una interacción completa del agente en formato JSON Lines para auditoría."""
    herramientas_usadas = []
    nivel_riesgo_maximo = "BAJO"
    requirio_aprobacion = False

    for paso in pasos_intermedios:
        accion, resultado = paso
        herramientas_usadas.append({
            "herramienta": accion.tool,
            "argumentos": accion.tool_input,
            "resultado": str(resultado),
        })
        if accion.tool == "reiniciar_servicio_critico":
            nivel_riesgo_maximo = "ALTO"
            requirio_aprobacion = True

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entrada": entrada,
        "salida": salida if isinstance(salida, str) else str(salida),
        "herramientas_invocadas": herramientas_usadas,
        "conteo_herramientas": len(herramientas_usadas),
        "nivel_riesgo": nivel_riesgo_maximo,
        "requirio_supervision": requirio_aprobacion,
    }

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    return registro


def marcar_repeticiones_sospechosas(archivo: str = ARCHIVO_TRAZAS, umbral_repeticiones: int = 3) -> list[dict]:
    """Inspecciona el archivo de trazas y detecta posibles bucles de decisión o llamadas anómalas."""
    alertas = []
    if not os.path.exists(archivo):
        return alertas

    with open(archivo, "r", encoding="utf-8") as f:
        lineas = [json.loads(linea) for linea in f if linea.strip()]

    for i, registro in enumerate(lineas, start=1):
        herramientas = [h["herramienta"] for h in registro.get("herramientas_invocadas", [])]
        for h in set(herramientas):
            conteo = herramientas.count(h)
            if conteo >= umbral_repeticiones:
                alertas.append({
                    "linea": i,
                    "timestamp": registro.get("timestamp"),
                    "herramienta": h,
                    "conteo": conteo,
                    "advertencia": f"Posible bucle: herramienta '{h}' llamada {conteo} veces en una misma consulta.",
                })

    return alertas


# ---------------------------------------------------------------------------
# Factoría de Agente
# ---------------------------------------------------------------------------

def construir_agente_operaciones(modelo=None, herramientas=None):
    """Construye y compila el agente con su ejecutor configurado con traza de pasos."""
    if herramientas is None:
        herramientas = [
            consultar_estado_servicio,
            calcular_costo_instancias,
            reiniciar_servicio_critico,
        ]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente senior de operaciones e infraestructura cloud. "
            "Responde a las consultas del equipo técnico utilizando las herramientas "
            "disponibles según corresponda. Si el usuario solicita reiniciar un servicio, "
            "debes invocar inmediatamente la herramienta reiniciar_servicio_critico (dicha herramienta se encarga de solicitar la aprobación humana requerida). "
            "Si una pregunta es puramente conceptual o informativa, responde directamente con precisión técnica.",
        ),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    if modelo is None:
        load_dotenv()
        modelo = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )
    return ejecutor


# ---------------------------------------------------------------------------
# Ejecución y Verificación de Casos y Trazabilidad
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    ejecutor = construir_agente_operaciones(modelo=modelo)

    print("\n" + "=" * 60)
    print("CASO 1: Consulta de estado de servicio (Riesgo Bajo - Lectura)")
    print("=" * 60)
    query_1 = "¿Cuál es el estado del servicio de notificaciones?"
    res_1 = ejecutor.invoke({"entrada": query_1})
    reg_1 = registrar_traza(query_1, res_1["output"], res_1["intermediate_steps"])
    print(f"Salida: {res_1['output']}")
    print(f"Traza registrada: Nivel {reg_1['nivel_riesgo']}, Herramientas: {len(reg_1['herramientas_invocadas'])}")

    print("\n" + "=" * 60)
    print("CASO 2: Cálculo presupuestario de nube (Riesgo Bajo - Cómputo)")
    print("=" * 60)
    query_2 = "¿Cuánto costará tener 8 instancias encendidas durante 720 horas a 0.096 USD la hora?"
    res_2 = ejecutor.invoke({"entrada": query_2})
    reg_2 = registrar_traza(query_2, res_2["output"], res_2["intermediate_steps"])
    print(f"Salida: {res_2['output']}")
    print(f"Traza registrada: Nivel {reg_2['nivel_riesgo']}, Herramientas: {len(reg_2['herramientas_invocadas'])}")

    print("\n" + "=" * 60)
    print("CASO 3: Pregunta general conceptual (Sin herramientas)")
    print("=" * 60)
    query_3 = "¿Qué es la resiliencia en arquitecturas distribuidas?"
    res_3 = ejecutor.invoke({"entrada": query_3})
    reg_3 = registrar_traza(query_3, res_3["output"], res_3["intermediate_steps"])
    print(f"Salida: {res_3['output']}")
    print(f"Traza registrada: Nivel {reg_3['nivel_riesgo']}, Herramientas: {len(reg_3['herramientas_invocadas'])}")

    print("\n" + "=" * 60)
    print("CASO 4: Acción de Alto Riesgo con Supervisión Humana")
    print("=" * 60)
    os.environ["AGENT_AUTO_APPROVE"] = "1"  # Habilitado para trazado determinista de aprobación
    query_4 = "Ejecuta reiniciar_servicio_critico para el servicio 'notificaciones' con motivo 'acumulación de memoria detectada en logs'."
    res_4 = ejecutor.invoke({"entrada": query_4})
    reg_4 = registrar_traza(query_4, res_4["output"], res_4["intermediate_steps"])
    print(f"Salida: {res_4['output']}")
    print(f"Traza registrada: Nivel {reg_4['nivel_riesgo']}, Supervisión requerida: {reg_4['requirio_supervision']}")

    alertas = marcar_repeticiones_sospechosas()
    print(f"\nVerificación de anomalías en trazas: {len(alertas)} alertas detectadas.")
    print(f"Archivo de trazas '{ARCHIVO_TRAZAS}' actualizado con éxito.")
