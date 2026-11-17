# Servicio IA Modular con RAG — Gate 2

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Repositorio:** [https://github.com/by-matt/Especializacion-IA](https://github.com/by-matt/Especializacion-IA)  
> **Estado:** Gate 2 entregado  

---

## 1. Descripción del Proyecto

Este repositorio contiene la integración del **Módulo 2 (Construcción de Componentes IA)** en un servicio RAG (*Retrieval-Augmented Generation*) modular. El sistema permite responder consultas sobre documentación de soporte técnico citando las fuentes correspondientes, e incorpora mecanismos de observabilidad, mitigación de inyección indirecta y un flujo de supervisión humana (HITL).

### Componentes principales integrados:

1. **Pipeline RAG (U2.5):**
   - Indexación con chunks de tamaño semántico (`chunk_size=200`, `chunk_overlap=30`) persistidos en Chroma DB local (`indice_gate2/`).
   - Actualización incremental para evitar chunks duplicados en disco.
   - Búsqueda semántica (`k=2`) y generación de respuesta citando obligatoriamente el documento origen (`[manual.pdf]`).

2. **Evaluación de la recuperación (Bloque 27):**
   - Evaluación sobre 10 casos de prueba midiendo $\text{Precisión}@k$ ($0.300$) y $\text{Recall}@k$ ($1.000$) con $k=3$ (`resultados_evaluacion.txt`).

3. **Métricas de latencia y costo (Bloque 28):**
   - Medición de tiempos por etapa con `time.perf_counter()` y captura de tokens con `usage_metadata` de `AIMessage` (`registros_latencia_costo.jsonl`).

4. **Estrategia de personalización (Bloques 29 y 30):**
   - Dataset estructurado para PEFT LoRA enfocado en el caso de cumplimiento fitosanitario de exportación agrícola (12 ejemplos balanceados en `dataset_tuning.py`).
   - Matriz cuantitativa de decisión que justifica la elección de PEFT frente a RAG y Fine-Tuning completo por volumen de datos, infraestructura y tiempos de iteración (`decision_personalizacion.md`).

5. **Logging estructurado y trazabilidad (Bloque 31):**
   - Formateador JSON y propagación de `trace_id` por consulta usando `contextvars.ContextVar`.
   - Registro seguro de eventos: solo se guardan longitudes de texto y conteos (`pregunta_len`, `n_limpios`, `n_descartados`), evitando almacenar PII (datos personales) o texto plano sensible en los logs.

6. **Filtro contra inyección indirecta (Bloques 31 y S1):**
   - Detección de patrones maliciosos en los fragmentos recuperados mediante expresiones regulares sobre `d.page_content`.
   - Manejo de contingencia: si el contexto recuperado está comprometido o vacío, el servicio interrumpe la respuesta con el mensaje: *"No tengo informacion suficiente y verificada para responder esto."*

7. **Gobernanza y supervisión humana (Bloque 32):**
   - Versionado de prompts con hash SHA-256 de 12 caracteres y diff de palabras (`registro_prompts.py`).
   - Flujo con LangGraph que implementa pausa determinista (`interrupt()`) con checkpointer en memoria (`InMemorySaver()`), requiriendo confirmación manual explícita (`Command(resume=True)` o `resume=False`).
   - Matriz de riesgos ($P \times I$) con 5 riesgos identificados, clasificación por severidad y análisis de sensibilidad en frontera (`matriz_riesgos.py`).

---

## 2. Pruebas de Criterios No Compensables

En `test_gate2.py` implementé la suite de pruebas automatizadas con pytest para validar los cuatro criterios no compensables exigidos en el Gate 2:

| Criterio | Prueba en `test_gate2.py` | Qué valida |
| :--- | :--- | :--- |
| **1. Pipeline sin excepciones** | `test_1_pipeline_sin_excepciones` | Que el flujo completo (cargar índice, recuperar, filtrar y responder) ejecute de inicio a fin con código 0 y devuelva respuesta. |
| **2. Cita de fuentes** | `test_2_respuesta_cita_fuente` | Que la respuesta cite explícitamente el documento origen respaldado (`manual.pdf`). |
| **3. Sanitización de logs / Sin PII** | `test_3_logs_sin_contenido_crudo` | Que al enviar una consulta con datos sensibles (correo de prueba), los logs no contengan el texto crudo ni PII, registrando solo métricas (`pregunta_len`). |
| **4. Supervisión humana funcional** | `test_4_supervision_pausa_y_reanuda` | Que el grafo de LangGraph se detenga en la interrupción (`__interrupt__`), retenga el estado y solo continúe cuando el supervisor reanuda con `Command(resume=True)`. |

Para correr las pruebas:
```bash
python -m pytest test_gate2.py -v
```

---

## 3. Estructura del Repositorio

```text
Especializacion-IA/
├── servicio_rag.py              # Servicio RAG modular integrado del Gate 2
├── test_gate2.py                # Pruebas automatizadas de los 4 criterios no compensables
├── verificar_entorno.py         # Script de comprobación de dependencias, variables e índice
├── ensayo_gate2.py              # Ensayo funcional del flujo completo de extremo a extremo
├── rubrica_gate2.py             # Script de verificación de dimensiones de la rúbrica
│
├── logging_rag.py               # U2.7: Logging estructurado JSON, trace_id y filtro de inyección
├── registro_prompts.py          # U2.7: Versionado de prompts con hash SHA-256 y diff
├── grafo_supervision.py         # U2.7: Flujo de supervisión humana con LangGraph (interrupt/resume)
├── matriz_riesgos.py            # U2.7: Matriz cuantitativa de riesgos (P x I) y sensibilidad
│
├── dataset_tuning.py            # U2.6: Dataset validado para PEFT LoRA y balance de clases
├── decision.py                  # U2.6: Ponderación de decisión técnica (RAG vs Fine-Tuning vs PEFT)
├── decision_personalizacion.md  # U2.6: Memoria justificativa de la técnica seleccionada
│
├── indexar_corpus.py            # U2.5: Ingesta, chunking y almacenamiento vectorial Chroma
├── recuperacion.py              # U2.5: Búsqueda semántica y armado de prompt con fuentes
├── evaluacion_recuperacion.py   # U2.5: Medición de Precision@k y Recall@k
├── resultados_evaluacion.txt    # U2.5: Resultados de la evaluación de recuperación
├── registro_rag.py              # U2.5: Medición de tiempos por etapa y conteo de tokens
├── registros_latencia_costo.jsonl # U2.5: Registro histórico de latencias y consumo
├── leer_registros.py            # U2.5: Lector y resumen de métricas registradas
├── preflight.py                 # U2.5: Verificación local del índice vectorial
│
├── agente_con_herramientas.py   # U2.4: Agente con herramientas Pydantic y supervisión HITL
├── test_agente_con_herramientas.py # U2.4: Pruebas unitarias del agente
├── limites_autonomia_agente.md  # U2.4: Matriz de gobernanza y límites de autonomía
├── trazas_agente.jsonl          # U2.4: Registro de trazas de ejecución del agente
│
├── cadena_tres_pasos.py         # U2.3: Cadena secuencial LCEL de tres pasos
├── enrutamiento.py              # U2.3: Enrutamiento condicional con RunnableBranch
├── pipeline_texto.py            # U2.2: Normalización, tokenización y métricas de texto
│
├── cliente.py                   # U2.1 / Gate 1: Cliente con reintentos y backoff exponencial
├── cliente_api.py               # U2.1 / Gate 1: Manejo de peticiones HTTP y errores
├── main.py                      # U1.6 / Gate 1: CLI de clasificación y FinOps
├── test_cliente.py              # U2.1 / Gate 1: Pruebas del cliente HTTP
│
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Exclusiones estándar (.env, venv, índices)
└── README.md                    # Documentación del proyecto
```

---

## 4. Cómo Ejecutar el Proyecto

### 1. Clonar y preparar el entorno
```bash
git clone https://github.com/by-matt/Especializacion-IA.git
cd Especializacion-IA
```

Crear y activar el entorno virtual:
```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Instalar dependencias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurar la clave de API
Crear el archivo `.env` a partir de `.env.example` y colocar la clave de Gemini:
```ini
GEMINI_API_KEY=AIzaSy...tu_clave_aqui
```

### 3. Verificar que el entorno esté listo
Ejecutar el script de comprobación previa:
```bash
python verificar_entorno.py
```
Salida esperada:
```text
Python: 3.13.7
langchain-core: 1.7.4
langchain-chroma: 1.1.0
langgraph: 1.2.19
python-dotenv: 1.2.4
GEMINI_API_KEY: definida
indice en indice_gate2/: ok

Entorno listo para la corrida final
```

### 4. Ejecutar el servicio RAG
Para correr el servicio modular integrado:
```bash
python servicio_rag.py
```

### 5. Ejecutar la suite de pruebas del Gate 2
Para correr los tests automatizados:
```bash
python -m pytest test_gate2.py -v
```

---

## 5. Notas Técnicas de la Integración

Durante el desarrollo e integración de los componentes del Módulo 2 resolví los siguientes puntos clave:

- **Compatibilidad con objetos Document de LangChain:**  
  Al conectar el filtro de inyección indirecta (desarrollado inicialmente en el Bloque 31) con el retriever de Chroma, ajusté la función para extraer el texto desde `d.page_content` y el origen desde `d.metadata["fuente"]`, adaptándolo a la estructura real que entrega Chroma.
- **Manejo de inyección indirecta en el corpus:**  
  Probé inyectar intencionalmente un fragmento con instrucciones maliciosas (*"ignora las instrucciones anteriores..."*). El filtro lo detecta, lo descarta del contexto y el servicio activa la salida de contingencia (*"No tengo informacion suficiente y verificada para responder esto."*), evitando que el LLM ejecute instrucciones ajenas.
- **Aislamiento de trazas en concurrencia:**  
  Utilicé `contextvars.ContextVar("trace_id")` en lugar de variables globales para asegurar que cada consulta mantenga su propio identificador de trazabilidad aislado, incluso en llamadas sucesivas o asíncronas.

---

## 6. Entregas Anteriores (Gate 1)

Los componentes desarrollados para el Gate 1 (Habilitación Técnica) se encuentran disponibles en el repositorio:
- `cliente.py`: Cliente modular con reintentos y backoff exponencial.
- `prompts/`: Definición de esquemas JSON estructurados y consistencia de prompts.
- `docs/arquitectura.md` y `docs/decision_modelo.md`: Diseño de arquitectura y selección de modelos.
- `main.py`: Punto de entrada CLI del Gate 1.
