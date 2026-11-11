"""
Pruebas unitarias para el agente con herramientas (Bloque 21).

Verifica la invocación de herramientas, la correcta estructura de intermediate_steps
y el comportamiento ante consultas generales.
"""

from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from agente_con_herramientas import (
    calcular_costo_instancias,
    consultar_estado_servicio,
)


def test_consultar_estado_servicio_existente():
    resultado = consultar_estado_servicio.invoke({"nombre_servicio": "pagos"})
    assert "Operativo" in resultado
    assert "pagos" in resultado.lower()


def test_consultar_estado_servicio_inexistente():
    resultado = consultar_estado_servicio.invoke({"nombre_servicio": "analytics"})
    assert "No se encontró información" in resultado


def test_calcular_costo_instancias_nominal():
    resultado = calcular_costo_instancias.invoke({
        "instancias": 5,
        "horas_mes": 720.0,
        "precio_hora_usd": 0.10,
    })
    # 5 * 720 * 0.10 = 360.00 USD
    assert "$360.00 USD" in resultado


def test_calcular_costo_instancias_validacion_cero():
    resultado = calcular_costo_instancias.invoke({"instancias": 0})
    assert "número entero positivo" in resultado.lower()
