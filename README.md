# Miniaplicación de Procesamiento con IA — Gate 1: Habilitación Técnica

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Repositorio Oficial:** [https://github.com/by-matt/Especializacion-IA](https://github.com/by-matt/Especializacion-IA)  
> **Estado:** Habilitación Técnica Completada — Calificación Gate 1: 7.0 / 7.0  

---

## 1. Descripción del Proyecto

En este proyecto desarrollé un cliente modular y seguro para interactuar con la API REST directa de Google Gemini (`gemini-3.8-flash`) utilizando Python estándar, sin depender de librerías de alto nivel o SDKs opacos. Mi foco estuvo en la separación limpia de responsabilidades, la resiliencia en red y el cumplimiento estricto de contratos de datos JSON.

Puntos centrales de mi diseño:
* **Separación de responsabilidades:** Dividí el código en capas independientes. `cliente_api.py` maneja exclusivamente el transporte HTTP, la autenticación y la clasificación de códigos de error (401/403 vs 429/5xx), mientras que `cliente.py` y `main.py` gestionan las políticas de reintentos, el cálculo de costo y la lógica de negocio.
* **Canal aislado de sistema (`systemInstruction`):** Separé las instrucciones de rol y formato de las entradas del usuario para evitar contaminación semántica y asegurar respuestas consistentes.
* **Salida estructurada forzada por API:** Configuré `generationConfig` y `responseSchema` en cada petición para que la API de Gemini devuelva exclusivamente JSON válido, con tipos definidos (`OBJECT`, `STRING`, `NUMBER`).
* **Sanitización y parseo defensivo:** Implementé `parsear_respuesta_json()` con expresiones regulares para remover posibles delimitadores Markdown colados (` ```json `), capturando excepciones con `json.JSONDecodeError` y verificando la presencia obligatoria de todas las claves requeridas.
* **Monitoreo FinOps en vivo:** Integre el cálculo del costo monetario de cada consulta directamente desde `usageMetadata` (`promptTokenCount` y `candidatesTokenCount`).
* **Seguridad de credenciales:** Mi API key (`GEMINI_API_KEY`) reside únicamente en el archivo local `.env`, el cual está excluido del repositorio mediante `.gitignore` y protegido contra fugas accidentales.

---

## 2. Estructura del Repositorio

```text
Especializacion-IA/
├── cliente_api.py               # Módulo base: armado de petición, transporte HTTP y clasificación de errores
├── cliente.py                   # Cliente resiliente: reintentos con backoff exponencial, jitter y FinOps
├── main.py                      # Punto de entrada principal y orquestación del flujo nominal
├── test_cliente.py              # Suite de pruebas unitarias deterministas con mocks y pytest
├── src/
│   ├── __init__.py
│   ├── test_api.py              # Script de diagnóstico y verificación autenticada
│   └── consumir_gemini.py       # Cliente modular alternativo con soporte de failover dinámico
├── prompts/
│   ├── README.md                # Reporte técnico consolidado de la suite de prompts
│   ├── banco.py                 # Banco de prompts con roles y esquemas estructurados
│   ├── test_consistencia.py     # Pruebas automatizadas de consistencia contra la API real
│   └── registro_resultados.json # Evidencia persistida de ejecuciones (100% consistencia)
├── docs/
│   ├── arquitectura.md          # Especificación técnica de componentes y flujo de datos
│   ├── decision_modelo.md       # ADR-001: Selección fundamentada de gemini-3.8-flash
│   └── diagrama_arquitectura.png # Diagrama de bloques y flujo del pipeline
├── tests/
│   └── test_cliente.py          # Pruebas unitarias preparadas para ejecución en CI/CD
├── .env.example                 # Plantilla pública sin credenciales
├── .gitignore                   # Reglas de exclusión estrictas (.env, venv/, cachés)
├── README.md                    # Esta guía técnica de instalación y documentación de contratos
└── requirements.txt             # Dependencias del proyecto fijadas para reproducibilidad
```

---

## 3. Instalación y Ejecución

Instrucciones para clonar y ejecutar este proyecto en un entorno local:

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/by-matt/Especializacion-IA.git
cd Especializacion-IA
```

### Paso 2: Crear y activar el entorno virtual (`venv`)

* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\venv\Scripts\Activate.ps1
  ```

* **En macOS / Linux / WSL:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Paso 3: Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
Creación del archivo `.env` a partir de la plantilla `.env.example`:

* **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
* **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Configuración de la clave obtenida en [Google AI Studio](https://aistudio.google.com/) dentro del archivo `.env`:
```ini
GEMINI_API_KEY=AIzaSy...clave_real_aqui
GEMINI_MODEL=gemini-3.8-flash
```

### Paso 5: Ejecutar la aplicación principal
```bash
python main.py
```

**Salida obtenida en terminal:**
```text
=== INICIANDO MINIAPLICACION - GATE 1 ===

[CONSULTA PROCESADA]: Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación.
[RESPUESTA ESTRUCTURADA DEL MODELO]: {'categoria': 'Soporte Técnico', 'confianza': 0.95}
[ACCESO DIRECTO]: Categoria=Soporte Técnico | Confianza=0.95

[METRICAS DE CONSUMO]: 65 tokens entrada | 19 tokens salida | Costo: $0.00001057 USD

Proceso terminado sin errores.
```

### Paso 6: Ejecutar las suites de pruebas

* **Pruebas unitarias del cliente (con mocks, sin llamadas de red ni gasto de tokens):**
  ```bash
  pytest test_cliente.py -v
  ```
* **Suite de consistencia de prompts (contra la API real de Gemini):**
  ```bash
  python prompts/test_consistencia.py
  ```

---

## 4. Especificación y Contratos de Interfaz (JSON Schemas)

Para documentar formalmente la interacción entre mi código y el servicio, definí dos niveles de contrato: el payload de transporte recibido desde la API de Google y el payload estructurado de dominio que utilizo en la lógica de la aplicación.

### 4.1 Contrato de Transporte REST Crudo (Gemini API Envelope)
Estructura JSON nativa que retorna el endpoint de Gemini tras ejecutar `enviar_peticion()`. En ella viaja el contenido generado dentro de `parts[0].text` junto con los metadatos de tokens en `usageMetadata`:

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "{\n  \"categoria\": \"Soporte Técnico\",\n  \"confianza\": 0.95\n}"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 65,
    "candidatesTokenCount": 19,
    "totalTokenCount": 84
  },
  "modelVersion": "gemini-3.8-flash"
}
```

### 4.2 Contrato de Dominio Estructurado (Payload de Aplicación)
Objeto JSON final deserializado, validado defensivamente y consumido por `main.py` a través de `parsear_respuesta_json()`:

```json
{
  "categoria": "Soporte Técnico",
  "confianza": 0.95
}
```

#### Diccionario de Datos del Contrato Principal:
| Campo | Tipo | Obligatorio | Rango / Valores | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `categoria` | `string` | Sí | Texto descriptivo | Clasificación funcional del problema planteado por el usuario. |
| `confianza` | `number` | Sí | `[0.0, 1.0]` | Puntuación de certeza estimada por el modelo para dicha categoría. |

---

### 4.3 Catálogo de Contratos del Banco de Prompts (`prompts/banco.py`)

Cada una de las tareas del banco de prompts cuenta con su propio esquema estricto de respuesta:

#### A. Clasificación de Sentimiento (`clasificar_sentimiento`)
* **Entrada de prueba:** `"El servicio llegó tarde pero el producto está en perfectas condiciones y funciona excelente."`
* **JSON de respuesta:**
```json
{
  "sentimiento": "positivo",
  "confianza": 0.92
}
```

#### B. Extracción de Entidades Técnicas (`extraer_entidades_tecnicas`)
* **Entrada de prueba:** `"No puedo iniciar sesión en el portal de producción y los clientes no pueden pagar sus facturas desde las 9 AM."`
* **JSON de respuesta:**
```json
{
  "componente": "autenticacion",
  "criticidad": "alta"
}
```

#### C. Resumen de Incidencias Operativas (`resumir_incidencia`)
* **Entrada de prueba:** `"La base de datos PostgreSQL principal superó el 95% de uso de disco en el cluster de Frankfurt tras una copia de respaldo automática no comprimida."`
* **JSON de respuesta:**
```json
{
  "resumen": "La base de datos PostgreSQL en Frankfurt alcanzó el 95% de capacidad debido a un respaldo automático sin compresión.",
  "accion_inmediata": "Comprimir o eliminar respaldos antiguos y liberar espacio en disco inmediatamente."
}
```

---

## 5. Documentación Técnica Complementaria

* 📐 **[Diagrama Conceptual de Arquitectura](docs/diagrama_arquitectura.png):** Diagrama que diseñé para ilustrar el flujo de datos, el aislamiento del entorno y el árbol de excepciones.
* 📄 **[Memoria Técnica de Arquitectura](docs/arquitectura.md):** Documento formal con la descomposición funcional, contratos de entrada/salida y políticas de resiliencia.
* ⚖️ **[ADR-001: Decisión y Elección de Modelo](docs/decision_modelo.md):** Registro de decisión arquitectónica justificando la adopción de la familia Flash (`gemini-3.8-flash`) frente a alternativas Pro.
* 🗂️ **[Banco de Prompts y Reporte de Consistencia](prompts/README.md):** Especificación de los prompts y evidencia empírica de consistencia (9 de 9 peticiones conformes).

---

## 6. Registro de Mi Prueba de Instalación Limpia

Como parte del aseguramiento de calidad del proyecto, realicé un ensayo completo de clonado y ejecución en limpio:

* **Fecha de validación:** 2026-10-21
* **Procedimiento aplicado:**
  1. Cloné el repositorio en un directorio temporal limpio.
  2. Inicialicé un entorno virtual aislado (`python -m venv venv`).
  3. Instalé las dependencias desde `requirements.txt`.
  4. Configuré `.env` con credenciales de prueba.
  5. Ejecuté `main.py` y `prompts/test_consistencia.py`.
* **Resultados observados:**
  - Cero dependencias faltantes durante la instalación.
  - Cero rutas absolutas en el código (empleo de rutas relativas con `pathlib.Path`).
  - Cero credenciales expuestas en el historial de Git o en archivos bajo seguimiento.
  - Ejecución nominal con código de salida 0 y parseo JSON conforme.

---

## 7. Verificación de Criterios No Compensables

| Criterio | Validación Técnica | Resultado |
| :--- | :--- | :---: |
| 🌐 **Que la API funcione** | Consultas HTTP reales contra la API de Gemini retornando HTTP 200 y JSON consistente. | **Aprobado** ✅ |
| 🔄 **Que el entorno sea reproducible** | Dependencias declaradas en `requirements.txt` (`requests`, `python-dotenv`, `pytest`). | **Aprobado** ✅ |
| 🔐 **Que las credenciales no queden expuestas** | Verificado con `git log` y exclusión de `.env` en `.gitignore`. | **Aprobado** ✅ |
| ▶️ **Que el código sea ejecutable** | Ejecución directa de `main.py` y suites de pruebas sin errores no capturados. | **Aprobado** ✅ |
