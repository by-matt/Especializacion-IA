"""Pruebas unitarias para el pipeline de procesamiento y evaluacion de texto (Bloques 15-16)."""
import pytest
from pipeline_texto import (
    limpiar_texto,
    tokenizar,
    procesar_texto,
    vectorizar,
    contar_coincidencias,
    calcular_precision_cobertura_f1,
    calcular_metricas,
    resumir_metricas,
)


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []


def test_limpiar_texto_tipo_invalido():
    with pytest.raises(TypeError, match="limpiar_texto espera str, no int"):
        limpiar_texto(123)


def test_tokenizar_espacios_multiples():
    resultado = tokenizar("hola   mundo   python")
    assert resultado == ["hola", "mundo", "python"]


def test_vectorizar_cuenta_repeticiones():
    tokens = ["el", "gato", "el", "perro"]
    conteo = vectorizar(tokens)
    assert conteo["el"] == 2
    assert conteo["gato"] == 1
    assert conteo["perro"] == 1


def test_contar_coincidencias_respeta_minimo_repeticiones():
    # 'el gato el gato' (2 veces 'el') vs 'el gato' (1 vez 'el')
    ref = ["el", "gato"]
    resp = ["el", "gato", "el", "gato"]
    # Coincidencias = 1 'el' + 1 'gato' = 2
    assert contar_coincidencias(ref, resp) == 2


def test_calcular_precision_cobertura_f1_nominal():
    # Ejemplo del manual: ref 6 tokens (el=2), resp 9 tokens (el=3), coincidencias=5
    ref = ["el", "gato", "duerme", "en", "el", "sofa"]
    resp = ["el", "gato", "duerme", "en", "el", "sillon", "todo", "el", "dia"]
    res = calcular_precision_cobertura_f1(ref, resp)
    assert res["precision"] == round(5 / 9, 4)
    assert res["cobertura"] == round(5 / 6, 4)
    assert res["f1"] == round(2 * (5 / 9) * (5 / 6) / ((5 / 9) + (5 / 6)), 4)


def test_calcular_precision_cobertura_f1_vacio():
    res = calcular_precision_cobertura_f1([], ["algo"])
    assert res == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    res2 = calcular_precision_cobertura_f1(["algo"], [])
    assert res2 == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}


def test_calcular_metricas_integrado():
    res = calcular_metricas("El cielo es azul.", "el cielo es azul")
    assert res["precision"] == 1.0
    assert res["cobertura"] == 1.0
    assert res["f1"] == 1.0


def test_resumir_metricas():
    lista = [
        {"precision": 1.0, "cobertura": 0.8, "f1": 0.8889},
        {"precision": 0.5, "cobertura": 0.4, "f1": 0.4444},
    ]
    resumen = resumir_metricas(lista)
    assert resumen["precision_promedio"] == 0.75
    assert resumen["cobertura_promedio"] == 0.6
    assert resumen["f1_promedio"] == 0.6666
