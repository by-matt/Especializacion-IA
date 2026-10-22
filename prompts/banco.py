"""Banco de prompts estructurados para la miniaplicacion de procesamiento con IA.

Cada prompt define:
- nombre: Identificador unico de la tarea.
- system_instruction: Instruccion de rol y restriccion de formato JSON en canal separado.
- ejemplo_usuario: Entrada representativa para pruebas de consistencia.
- claves_esperadas: Claves requeridas que deben existir en el diccionario de respuesta.
- response_schema: Esquema JSON estricto compatible con generationConfig de la API de Gemini.
"""

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Eres un clasificador de sentimiento analítico. Analiza el texto del usuario "
            "y responde únicamente con un objeto JSON con las claves 'sentimiento' "
            "('positivo', 'negativo' o 'neutro') y 'confianza' (número decimal entre 0 y 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está en perfectas condiciones y funciona excelente.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["sentimiento", "confianza"],
        },
    },
    {
        "nombre": "extraer_entidades_tecnicas",
        "system_instruction": (
            "Eres un extractor de entidades técnicas para tickets de soporte TI. "
            "Analiza el problema del usuario y devuelve únicamente un objeto JSON con las claves "
            "'componente' (string con el subsistema afectado, ej. 'autenticacion', 'facturacion', 'red') "
            "y 'criticidad' ('baja', 'media' o 'alta')."
        ),
        "ejemplo_usuario": "No puedo iniciar sesión en el portal de producción y los clientes no pueden pagar sus facturas desde las 9 AM.",
        "claves_esperadas": ["componente", "criticidad"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "componente": {"type": "STRING"},
                "criticidad": {"type": "STRING"},
            },
            "required": ["componente", "criticidad"],
        },
    },
    {
        "nombre": "resumir_incidencia",
        "system_instruction": (
            "Eres un asistente de operaciones de infraestructura. Genera un resumen ejecutivo "
            "ultraconciso de la incidencia y la acción recomendada inmediata. Responde únicamente "
            "con un objeto JSON con las claves 'resumen' (máximo 2 oraciones) y 'accion_inmediata' "
            "(el paso técnico a seguir)."
        ),
        "ejemplo_usuario": "La base de datos PostgreSQL principal superó el 95% de uso de disco en el cluster de Frankfurt tras una copia de respaldo automática no comprimida.",
        "claves_esperadas": ["resumen", "accion_inmediata"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "accion_inmediata": {"type": "STRING"},
            },
            "required": ["resumen", "accion_inmediata"],
        },
    },
]
