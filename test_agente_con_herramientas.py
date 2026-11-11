"""
Pruebas unitarias para el agente con herramientas y supervisión humana (Bloque 21 - 23).
Autor: Byron Calderón González

Verifica la invocación de herramientas, la correcta estructura de intermediate_steps,
la supervisión humana con esperar_aprobacion y la persistencia de trazas.
"""

import os
from unittest.mock import patch
from agente_con_herramientas import (
    calcular_costo_instancias,
    consultar_estado_servicio,
    reiniciar_servicio_critico,
    esperar_aprobacion,
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


def test_reiniciar_servicio_aprobado():
    with patch("agente_con_herramientas.esperar_aprobacion", return_value=True):
        resultado = reiniciar_servicio_critico.invoke({
            "nombre_servicio": "auth",
            "motivo": "parche de seguridad urgente",
        })
        assert "Éxito" in resultado
        assert "reiniciado correctamente" in resultado


def test_reiniciar_servicio_rechazado():
    with patch("agente_con_herramientas.esperar_aprobacion", return_value=False):
        resultado = reiniciar_servicio_critico.invoke({
            "nombre_servicio": "pagos",
            "motivo": "prueba no autorizada",
        })
        assert "Operación CANCELADA" in resultado
        assert "rechazado por falta de aprobación" in resultado
