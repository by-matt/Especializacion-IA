"""Suite de pruebas unitarias para el cliente modular (Bloque 14 - Actividad Core).

Verifica de forma aislada y determinista las 4 funciones del cliente sin realizar
llamadas reales a la red ni consumir tokens del proveedor.
"""
from unittest.mock import patch, Mock
import pytest
import cliente
from cliente import (
    enviar_peticion,
    con_reintento,
    registrar_costo,
    consultar_modelo,
)


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    """Garantiza el aislamiento del estado global entre ejecuciones de pruebas."""
    cliente.costo_total_sesion = 0.0
    yield


def test_enviar_peticion_credencial_invalida():
    """Verifica que un codigo HTTP 401 lance inmediatamente ValueError sin reintentar."""
    respuesta_falsa = Mock(status_code=401)
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_limite_de_uso():
    """Verifica que un codigo HTTP 429 lance TimeoutError para permitir reintentos."""
    respuesta_falsa = Mock(status_code=429)
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_exito():
    """Verifica el camino nominal donde la API responde HTTP 200 con JSON valido."""
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion({"pregunta": "test"})
        assert resultado == {"texto": "respuesta simulada"}


def test_con_reintento_agota_intentos():
    """Verifica que con_reintento propague el TimeoutError original al agotar los intentos."""
    intentos_ejecutados = {"n": 0}

    def siempre_falla():
        intentos_ejecutados["n"] += 1
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3, espera_base=0.1)

    assert intentos_ejecutados["n"] == 3
    assert mock_sleep.call_count == 2  # Se duerme en intentos 1 y 2, en el 3 levanta excepcion


def test_con_reintento_no_reintenta_value_error():
    """Verifica que errores permanentes (ValueError) fallen de inmediato sin esperas ni reintentos."""
    def falla_credencial():
        raise ValueError("Credencial inválida")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(ValueError):
            con_reintento(falla_credencial, intentos=3)

    mock_sleep.assert_not_called()


def test_registrar_costo_acumula():
    """Verifica el calculo monetario FinOps y la correcta acumulacion en la sesion."""
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = registrar_costo(respuesta_falsa)
    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_consultar_modelo_convierte_error():
    """Verifica que consultar_modelo capture el TimeoutError agotado y lo convierta a RuntimeError."""
    error_simulado = TimeoutError("simulado")
    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError, match="El servicio no respondió tras varios intentos"):
            consultar_modelo("pregunta de prueba")
