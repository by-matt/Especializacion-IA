"""
Suite de pruebas de orquestación, bifurcación y resiliencia de flujos LangChain.

Verifica el cumplimiento integral del checklist de la Unidad 2.3:
- Normalización en la clasificación.
- Bifurcación correcta por condición (queja, pregunta, default).
- Activación de fallbacks ante fallos de llamada a modelo.
- Tolerancia a fallos en el runner general sin propagar excepciones.
"""

from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    construir_paso_clasificacion,
    procesar_mensaje_seguro,
)


def test_clasificacion_normaliza_antes_de_comparar():
    """Verifica que el clasificador elimine espacios en blanco y estandarice a minúsculas."""
    mock_modelo = MagicMock()
    mock_modelo.invoke.return_value = AIMessage(content="  Queja \n")
    mock_modelo.return_value = AIMessage(content="  Queja \n")

    paso_clasif = construir_paso_clasificacion(mock_modelo)
    resultado = paso_clasif.invoke({"mensaje": "El servicio presenta intermitencias."})

    assert resultado == "queja"


def test_enrutamiento_va_a_cadena_queja():
    """Verifica que un mensaje clasificado como 'queja' bifurque a la cadena especializada."""
    clasificacion_falsa = MagicMock(return_value="queja")
    cadena_queja_falsa = MagicMock(return_value="Respuesta empática de queja")

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )
    resultado = cadena.invoke({"mensaje": "Esto no funciona nunca"})

    assert cadena_queja_falsa.called
    assert resultado == "Respuesta empática de queja"


def test_enrutamiento_va_a_cadena_pregunta():
    """Verifica que un mensaje clasificado como 'pregunta' bifurque a la cadena de consulta."""
    clasificacion_falsa = MagicMock(return_value="pregunta")
    cadena_pregunta_falsa = MagicMock(return_value="Respuesta técnica precisa")

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "¿Cómo configuro el webhook?"})

    assert cadena_pregunta_falsa.called
    assert resultado == "Respuesta técnica precisa"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    """Verifica que ante una categoría no identificada, se ejecute la ruta por defecto."""
    clasificacion_falsa = MagicMock(return_value="desconocida")
    cadena_pregunta_falsa = MagicMock(return_value="Respuesta general por defecto")

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "Hola, buenas tardes"})

    assert cadena_pregunta_falsa.called
    assert resultado == "Respuesta general por defecto"


def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    """Verifica que la cadena de queja protegida active el fallback ante fallos de conexión."""
    def fallar_a_proposito(x):
        raise ConnectionError("Simulación de fallo de red")

    cadena_queja_falsa = RunnableLambda(fallar_a_proposito)
    cadena_queja_segura = construir_cadena_queja_segura(cadena_queja_falsa)

    resultado = cadena_queja_segura.invoke({"mensaje": "La pantalla queda en blanco"})
    assert "equipo" in resultado.lower()


def test_procesar_mensaje_seguro_no_propaga_excepciones():
    """Verifica que fallos tempranos en la clasificación sean contenidos sin interrumpir la app."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.side_effect = ConnectionError("Fallo en servicio de clasificación")

    cadena_falsa = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
    )
    resultado = procesar_mensaje_seguro(cadena_falsa, "Mensaje de auditoría")
    assert "no pudimos procesar" in resultado.lower()
