from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from cadena_tres_pasos import construir_cadena


def test_cadena_tres_pasos_ejecuta_secuencia_completa():
    """Valida que la cadena ejecute secuencialmente los tres pasos y devuelva el formato esperado."""
    mock_modelo = MagicMock()
    mock_modelo.invoke.side_effect = [
        AIMessage(content="La generación aumentada por recuperación optimiza modelos de lenguaje."),
        AIMessage(content="Optimización con datos externos\nMitigación de alucinaciones\nPrivacidad de datos"),
        AIMessage(content="- Optimización con datos externos\n- Mitigación de alucinaciones\n- Privacidad de datos"),
    ]
    mock_modelo.side_effect = mock_modelo.invoke.side_effect

    cadena = construir_cadena(mock_modelo)
    resultado = cadena.invoke({"texto": "Large language models optimize performance using external data."})

    assert "- Optimización con datos externos" in resultado
    assert "- Mitigación de alucinaciones" in resultado
    assert "- Privacidad de datos" in resultado
    assert mock_modelo.call_count == 3 or mock_modelo.invoke.call_count == 3


def test_cadena_tres_pasos_pasa_variables_intermedias():
    """Verifica que el output de cada paso se transforme adecuadamente en la clave esperada por el siguiente."""
    llamadas_recibidas = []

    def mock_invocacion(prompt_value, *args, **kwargs):
        texto_prompt = str(prompt_value)
        llamadas_recibidas.append(texto_prompt)
        if len(llamadas_recibidas) == 1:
            return AIMessage(content="Traduccion simulada paso 1")
        elif len(llamadas_recibidas) == 2:
            return AIMessage(content="Idea simulada paso 2")
        else:
            return AIMessage(content="- Resultado final paso 3")

    mock_modelo = MagicMock()
    mock_modelo.invoke.side_effect = mock_invocacion
    mock_modelo.side_effect = mock_invocacion

    cadena = construir_cadena(mock_modelo)
    resultado = cadena.invoke({"texto": "Texto inicial de prueba"})

    assert resultado == "- Resultado final paso 3"
    assert len(llamadas_recibidas) == 3
    assert "Texto inicial de prueba" in llamadas_recibidas[0]
    assert "Traduccion simulada paso 1" in llamadas_recibidas[1]
    assert "Idea simulada paso 2" in llamadas_recibidas[2]
