"""
Agente con herramientas propias y traza de decisión (Bloque 21).

Implementación de un agente reactivo para operaciones de infraestructura y devops.
Dispone de dos herramientas especializadas con propósitos delimitados:
1. consultar_estado_servicio: Lectura de estado y métricas de microservicios.
2. calcular_costo_instancias: Estimación presupuestaria de cómputo en la nube.
"""

from dotenv import load_dotenv
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
# Herramientas del Agente (Manejo defensivo de errores y retorno en string)
# ---------------------------------------------------------------------------

SERVICIOS_DISPONIBLES = {
    "auth": "Operativo (Uptime: 99.98%, Latencia promedio: 42ms)",
    "pagos": "Operativo (Uptime: 99.95%, Latencia promedio: 110ms)",
    "database": "En mantenimiento preventivo (Finalización estimada: 20 minutos)",
    "notificaciones": "Degradado (Cola de mensajes con demora de 3 minutos)",
}


@tool
def consultar_estado_servicio(nombre_servicio: str) -> str:
    """Consulta el estado operativo, salud y latencia de un microservicio de la plataforma.
    Usar cuando el usuario pregunte por el estado, uptime, disponibilidad o problemas
    de un servicio técnico específico (por ejemplo: 'auth', 'pagos', 'database', 'notificaciones')."""
    clave = nombre_servicio.strip().lower()
    try:
        if clave in SERVICIOS_DISPONIBLES:
            return f"Servicio '{clave}': {SERVICIOS_DISPONIBLES[clave]}"
        # Búsqueda parcial por si el nombre viene dentro de una frase
        for s_nombre, s_info in SERVICIOS_DISPONIBLES.items():
            if s_nombre in clave:
                return f"Servicio '{s_nombre}': {s_info}"
        return (
            f"No se encontró información del servicio '{nombre_servicio}'. "
            f"Servicios registrados: {', '.join(SERVICIOS_DISPONIBLES.keys())}."
        )
    except Exception as error:
        return f"Error consultando el estado del servicio: {error}"


@tool
def calcular_costo_instancias(instancias: int, horas_mes: float = 720.0, precio_hora_usd: float = 0.096) -> str:
    """Calcula el costo estimado de cómputo cloud según la cantidad de instancias activas,
    las horas estimadas de uso en el mes y la tarifa horaria en USD.
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


# ---------------------------------------------------------------------------
# Factoría de Agente
# ---------------------------------------------------------------------------

def construir_agente_operaciones(modelo=None, herramientas=None):
    """Construye y compila el agente con su ejecutor configurado con traza de pasos."""
    if herramientas is None:
        herramientas = [consultar_estado_servicio, calcular_costo_instancias]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de operaciones e infraestructura cloud. "
            "Responde a las consultas del equipo técnico utilizando las herramientas "
            "disponibles según corresponda. Si una pregunta no requiere herramientas, "
            "responde directamente con precisión técnica.",
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
# Ejecución y Verificación de intermediate_steps
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    ejecutor = construir_agente_operaciones(modelo=modelo)

    print("\n" + "=" * 60)
    print("CASO 1: Consulta de estado de servicio (Dispara consultar_estado_servicio)")
    print("=" * 60)
    res_1 = ejecutor.invoke({"entrada": "¿Cuál es el estado del servicio de pagos?"})
    print("\nSalida final:")
    print(res_1["output"])
    if res_1["intermediate_steps"]:
        herramienta_usada = res_1["intermediate_steps"][0][0].tool
        print(f"Herramienta verificada en intermediate_steps: {herramienta_usada}")
        assert herramienta_usada == "consultar_estado_servicio", f"Esperado consultar_estado_servicio, obtenido {herramienta_usada}"

    print("\n" + "=" * 60)
    print("CASO 2: Cálculo presupuestario de nube (Dispara calcular_costo_instancias)")
    print("=" * 60)
    res_2 = ejecutor.invoke({"entrada": "¿Cuánto costará tener 5 instancias encendidas durante 720 horas a 0.096 USD la hora?"})
    print("\nSalida final:")
    print(res_2["output"])
    if res_2["intermediate_steps"]:
        herramienta_usada = res_2["intermediate_steps"][0][0].tool
        print(f"Herramienta verificada en intermediate_steps: {herramienta_usada}")
        assert herramienta_usada == "calcular_costo_instancias", f"Esperado calcular_costo_instancias, obtenido {herramienta_usada}"

    print("\n" + "=" * 60)
    print("CASO 3: Pregunta general conceptual (No debe usar herramientas)")
    print("=" * 60)
    res_3 = ejecutor.invoke({"entrada": "¿Qué diferencia existe entre observabilidad y monitoreo tradicional en software?"})
    print("\nSalida final:")
    print(res_3["output"])
    print(f"Pasos intermedios: {res_3['intermediate_steps']}")
    assert res_3["intermediate_steps"] == [], "No debió ejecutar herramientas para una consulta conceptual."
    print("\nVerificación de los tres casos completada con éxito.")
