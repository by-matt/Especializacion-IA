# Banco de Prompts y Validación de Consistencia (U1.5 - Bloque 10)

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Módulo:** Módulo 1 - Habilitación Técnica  
> **Unidad:** U1.5 Prompt engineering profesional inicial (Bloque 10)  
> **Estado:** Evaluado y Validado Empíricamente (100% de Consistencia)

---

## 1. Artefactos de la Entrega

Este directorio reúne los tres componentes exigidos por la Actividad Core:

| Archivo | Descripción | Enlace Directo |
| :--- | :--- | :--- |
| **`banco.py`** | Definición declarativa de la lista `BANCO_DE_PROMPTS` con esquemas tipados y roles aislados. | [`banco.py`](https://github.com/by-matt/Especializacion-IA/blob/main/prompts/banco.py) |
| **`test_consistencia.py`** | Script de prueba automatizada que ejecuta repeticiones contra la API real y valida contratos JSON. | [`test_consistencia.py`](https://github.com/by-matt/Especializacion-IA/blob/main/prompts/test_consistencia.py) |
| **`registro_resultados.json`** | Evidencia persistida y estructurada del resultado de consistencia en todas las ejecuciones. | [`registro_resultados.json`](https://github.com/by-matt/Especializacion-IA/blob/main/prompts/registro_resultados.json) |

---

## 2. Definición del Banco de Prompts (`BANCO_DE_PROMPTS`)

Se diseñaron 3 tareas especializadas para operaciones de soporte y análisis de infraestructura TI:

### 1. `clasificar_sentimiento`
* **Instrucción de Sistema:** `"Eres un clasificador de sentimiento analítico. Analiza el texto del usuario y responde únicamente con un objeto JSON con las claves 'sentimiento' ('positivo', 'negativo' o 'neutro') y 'confianza' (número decimal entre 0 y 1)."`
* **Entrada de Prueba:** `"El servicio llegó tarde pero el producto está en perfectas condiciones y funciona excelente."`
* **Claves Requeridas:** `["sentimiento", "confianza"]`
* **Schema REST:** `OBJECT` con propiedades `sentimiento` (`STRING`) y `confianza` (`NUMBER`).

### 2. `extraer_entidades_tecnicas`
* **Instrucción de Sistema:** `"Eres un extractor de entidades técnicas para tickets de soporte TI. Analiza el problema del usuario y devuelve únicamente un objeto JSON con las claves 'componente' (string con el subsistema afectado, ej. 'autenticacion', 'facturacion', 'red') y 'criticidad' ('baja', 'media' o 'alta')."`
* **Entrada de Prueba:** `"No puedo iniciar sesión en el portal de producción y los clientes no pueden pagar sus facturas desde las 9 AM."`
* **Claves Requeridas:** `["componente", "criticidad"]`
* **Schema REST:** `OBJECT` con propiedades `componente` (`STRING`) y `criticidad` (`STRING`).

### 3. `resumir_incidencia`
* **Instrucción de Sistema:** `"Eres un asistente de operaciones de infraestructura. Genera un resumen ejecutivo ultraconciso de la incidencia y la acción recomendada inmediata. Responde únicamente con un objeto JSON con las claves 'resumen' (máximo 2 oraciones) y 'accion_inmediata' (el paso técnico a seguir)."`
* **Entrada de Prueba:** `"La base de datos PostgreSQL principal superó el 95% de uso de disco en el cluster de Frankfurt tras una copia de respaldo automática no comprimida."`
* **Claves Requeridas:** `["resumen", "accion_inmediata"]`
* **Schema REST:** `OBJECT` con propiedades `resumen` (`STRING`) y `accion_inmediata` (`STRING`).

---

## 3. Resultados de Consistencia Empírica

El script de prueba ejecutó **3 repeticiones independientes por prompt** (9 peticiones reales a la API de `gemini-2.5-flash`), verificando la decodificación JSON y la presencia obligatoria de todas las claves requeridas:

| Prompt | Intentos | Éxitos | Tasa de Éxito | Estado |
| :--- | :---: | :---: | :---: | :---: |
| `clasificar_sentimiento` | 3 | 3 | **100%** | Conforme ✅ |
| `extraer_entidades_tecnicas` | 3 | 3 | **100%** | Conforme ✅ |
| `resumir_incidencia` | 3 | 3 | **100%** | Conforme ✅ |

### Evidencia Estructurada (`prompts/registro_resultados.json`):
```json
{
  "clasificar_sentimiento": {
    "exitos": 3,
    "intentos": 3
  },
  "extraer_entidades_tecnicas": {
    "exitos": 3,
    "intentos": 3
  },
  "resumir_incidencia": {
    "exitos": 3,
    "intentos": 3
  }
}
```

---

## 4. Arquitectura y Mecanismos de Robustez

1. **Aislamiento de Responsabilidades en la API:**
   - La directiva de comportamiento se canaliza exclusivamente mediante el campo `systemInstruction` de la API REST de Gemini.
   - El dato de entrada del usuario se envía en `contents`, evitando la contaminación semántica o deriva de instrucciones.
2. **Restricción Forzada por Engine (`generationConfig`):**
   - Configuración de `responseMimeType: "application/json"` junto con `responseSchema` estructurado bajo la gramática oficial de la API de Google.
3. **Capa Defensiva en el Cliente (`parsear_respuesta_json`):**
   - Sanitización mediante expresiones regulares (`re.sub`) para remover delimitadores Markdown colados (```` ```json ```` / ```` ``` ````).
   - Manejo de excepciones capturando `json.JSONDecodeError` mapeado a `ValueError`.
   - Verificación de existencia de todas las claves requeridas antes de retornar el diccionario procesado.
4. **Control de Rate Limiting (Prevención HTTP 429):**
   - Pausa programada de 2 segundos entre iteraciones sucesivas (`time.sleep(2)`) garantizando estabilidad frente a las cuotas del proveedor.
