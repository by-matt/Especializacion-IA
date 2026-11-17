"""
Batería de Pruebas Automatizadas para Criterios No Compensables del Gate 2
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González

Verifica los cuatro criterios no compensables de la rúbrica oficial:
1. Pipeline RAG de extremo a extremo sin excepciones no capturadas.
2. Citación explícita y verificada de fuentes en la respuesta final.
3. Ausencia absoluta de PII o contenido crudo sensible en los logs (sanitización).
4. Punto de supervisión humana real y funcional con LangGraph (interrupt y resume).
"""

import logging
import pytest
from langgraph.types import Command
from servicio_rag import responder, cargar_indice, app_despliegue

# Dato sensible de prueba que NUNCA debe aparecer en los logs en texto plano
CORREO = "ana.perez@example.com"
PREGUNTA = "Cual es la politica de devoluciones? Mi correo es " + CORREO

logger = logging.getLogger("servicio_rag")


def ejecutar_servicio(pregunta):
    """Corre el flujo completo del servicio RAG (cargar índice, recuperar, filtrar y responder)."""
    vectorstore, estado_indice = cargar_indice()
    resultado = responder(pregunta, vectorstore, estado_indice)
    return resultado["respuesta"], resultado["fuentes"]


def crear_supervision():
    """Devuelve la app de supervisión compilada y el estado inicial para la prueba."""
    return app_despliegue, {"huella_nueva": "c2a733e19c0b", "aprobado": False}


def test_1_pipeline_sin_excepciones():
    """Criterio 1: Que el servicio indexe, recupere y responda sin excepciones."""
    respuesta, _ = ejecutar_servicio(PREGUNTA)
    assert respuesta.strip(), "el servicio devolvio una respuesta vacia"


def test_2_respuesta_cita_fuente():
    """Criterio 2: Que cada respuesta cite la fuente que la respalda."""
    respuesta, fuentes = ejecutar_servicio(PREGUNTA)
    assert fuentes, "el servicio no devolvio ninguna fuente"
    assert any(f in respuesta for f in fuentes), "la respuesta no menciona su fuente"


def test_3_logs_sin_contenido_crudo(caplog):
    """Criterio 3: Que no haya PII ni contenido crudo sensible en los logs."""
    with caplog.at_level(logging.DEBUG, logger="servicio_rag"):
        ejecutar_servicio(PREGUNTA)
    texto_logs = " ".join(r.getMessage() + " " + str(r.__dict__) for r in caplog.records)
    assert CORREO not in texto_logs, "un dato sensible (correo) aparece en los logs"
    assert PREGUNTA not in texto_logs, "la consulta completa en texto crudo aparece en los logs"


def test_4_supervision_pausa_y_reanuda():
    """Criterio 4: Que exista un punto de supervisión humana real y operativo."""
    app, entrada = crear_supervision()
    config = {"configurable": {"thread_id": "test-gate2-ci"}}
    pausado = app.invoke(entrada, config=config)
    assert "__interrupt__" in pausado, "el grafo no se detuvo en el punto de supervision"
    final = app.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in final, "el grafo sigue pausado despues de reanudar"
    assert final["aprobado"] is True, "la decision no quedo registrada"
