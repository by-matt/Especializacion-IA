# Servicio IA Modular con RAG — Gate 2: Integración y Orquestación

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Repositorio Oficial:** [https://github.com/by-matt/Especializacion-IA](https://github.com/by-matt/Especializacion-IA)  
> **Estado de Entregas:**  
> - **Gate 1 (Habilitación Técnica):** Completado — Calificación 7.0 / 7.0  
> - **Gate 2 (Integración y Orquestación):** Completado — Cumplimiento al 100% de la Rúbrica y Criterios No Compensables  

---

## 1. Descripción Ejecutiva del Servicio (Gate 2)

Este proyecto consolida la arquitectura completa del **Módulo 2 (Construcción de Componentes IA)** en un servicio RAG (*Retrieval-Augmented Generation*) modular, resiliente, observable y gobernado. El sistema resuelve el problema de alucinación y falta de trazabilidad en asistentes de soporte técnico empresarial mediante:

1. **Pipeline RAG Factual de Extremo a Extremo (U2.5):**
   - Indexación con particionado semántico (`chunk_size=200`, `chunk_overlap=30`) y persistencia vectorial local en Chroma DB (`indice_gate2/`).
   - Actualización incremental con verificación de IDs de chunks existentes para evitar duplicaciones en disco.
   - Búsqueda semántica (`k=2`) y generación con citación obligatoria de fuentes respaldadas (`[manual.pdf]`).
2. **Evaluación Formal de la Recuperación (U2.5 - Bloque 27):**
   - Batería de 10 casos de prueba evaluando cuantitativamente $\text{Precisión}@k$ ($0.300$) y $\text{Recall}@k$ ($1.000$) con $k=3$ sobre corpus real (`resultados_evaluacion.txt`).
3. **Telemetría y Control FinOps (U2.5 - Bloque 28):**
   - Medición precisa de latencia por etapas con `time.perf_counter()` y captura de consumo real de tokens desde `usage_metadata` de `AIMessage` (`registros_latencia_costo.jsonl`).
4. **Decisión Fundamentada de Personalización (U2.6 - Bloques 29 y 30):**
   - Dataset estructurado para PEFT LoRA con 12 ejemplos de cumplimiento fitosanitario y balance de categorías auditado (`dataset_tuning.py`).
   - Matriz cuantitativa de 5 preguntas ponderadas y memoria técnica (`decision_personalizacion.md`) justificando PEFT frente a RAG y Fine-Tuning completo bajo criterios de datos, cómputo y tiempo.
5. **Observabilidad Estructurada y Trazabilidad (U2.7 - Bloque 31):**
   - Formateador `JsonFormatter` y contexto local de ejecución `contextvars.ContextVar("trace_id")`, correlacionando todas las etapas de una misma consulta en concurrencia sin variables globales.
   - Registro sanitizado de eventos de auditoría: solo se registran longitudes de texto y conteos (`pregunta_len`, `n_limpios`, `n_descartados`), blindando los logs contra fuga de datos personales (PII).
6. **Defensa contra Inyección Indirecta de Prompt (U2.7 - Bloques 31 y S1):**
   - Detección de patrones regex maliciosos (`ignora las instrucciones anteriores`, `system prompt:`, `revela tu prompt`) sobre la interfaz nativa `d.page_content` de LangChain.
   - Ruta segura de contingencia: si el contexto recuperado está completamente comprometido o vacío, el servicio corta la ejecución y emite `sin_contexto_confiable` con la respuesta estandarizada: *"No tengo informacion suficiente y verificada para responder esto."*
7. **Gobernanza Técnica, Versionado y Supervisión Humana (U2.7 - Bloque 32):**
   - Versionado de prompts como artefactos de software con hashing SHA-256 (12 caracteres) y diff unificado de palabras (`registro_prompts.py`).
   - Punto de supervisión humana real (*Human-in-the-Loop*) implementado con `StateGraph` de LangGraph, pausa determinista `interrupt()` y checkpointer en memoria (`InMemorySaver()`), requiriendo autorización explícita `Command(resume=True)` o rechazo `Command(resume=False)`.
   - Matriz matemática de riesgos ($P \times I$) con 5 riesgos específicos del sistema clasificados en CRÍTICO, ALTO, MEDIO y BAJO, con análisis de sensibilidad en el límite (`esta_en_el_limite`).

---

## 2. Verificación de Criterios No Compensables (Gate 2)

El servicio cumple estrictamente las cuatro condiciones no compensables exigidas por el programa, verificables de forma automática mediante `pytest test_gate2.py -v`:

| Criterio No Compensable | Mecanismo de Validación en Código | Resultado |
| :--- | :--- | :---: |
| **1. Pipeline sin excepciones** | `test_1_pipeline_sin_excepciones`: Ejecución nominal completa (indexar, recuperar, filtrar y responder) con código de salida 0 y respuesta no vacía. | **PASSED** ✅ |
| **2. Respuesta cita su fuente** | `test_2_respuesta_cita_fuente`: Verificación de que la respuesta final incluye explícitamente el identificador del documento respaldado (`manual.pdf`). | **PASSED** ✅ |
| **3. Logs sin contenido crudo / PII** | `test_3_logs_sin_contenido_crudo`: Inyección de correo sensible de prueba (`ana.perez@example.com`) comprobando que los logs solo emiten `pregunta_len` y jamás texto plano. | **PASSED** ✅ |
| **4. Supervisión humana funcional** | `test_4_supervision_pausa_y_reanuda`: El grafo LangGraph se pausa en `__interrupt__`, retiene el estado y solo reanuda tras `Command(resume=True)` registrando `aprobado: True`. | **PASSED** ✅ |

---

## 3. Estructura Integral del Repositorio

```text
Especializacion-IA/
├── servicio_rag.py              # Servicio RAG modular integrado oficial del Gate 2
├── test_gate2.py                # Suite pytest que verifica los 4 criterios no compensables
├── verificar_entorno.py         # Script de pre-vuelo: valida Python, dependencias, .env e índice
├── ensayo_gate2.py              # Script integrado del ensayo funcional de extremo a extremo
├── rubrica_gate2.py             # Simulador de evaluación ponderada del Gate 2 (6 dimensiones)
│
├── logging_rag.py               # U2.7: Logging estructurado JSON, trace_id y filtro de inyección
├── registro_prompts.py          # U2.7: Versionado criptográfico de prompts (SHA-256) y diff unificado
├── grafo_supervision.py         # U2.7: Flujo Human-in-the-Loop con LangGraph (interrupt y Command)
├── matriz_riesgos.py            # U2.7: Matriz cuantitativa de riesgos (P x I) y análisis de límites
│
├── dataset_tuning.py            # U2.6: Dataset validado para PEFT LoRA y chequeo de balance
├── decision.py                  # U2.6: Algoritmo de ponderación técnica (RAG vs Fine-Tuning vs PEFT)
├── decision_personalizacion.md  # U2.6: Memoria técnica fundamentada en datos, cómputo y tiempo
│
├── indexar_corpus.py            # U2.5: Ingesta, chunking y persistencia vectorial Chroma
├── recuperacion.py              # U2.5: Búsqueda semántica y ensamblado de prompts con citas
├── evaluacion_recuperacion.py   # U2.5: Evaluación cuantitativa de Precision@k y Recall@k
├── resultados_evaluacion.txt    # U2.5: Reporte persistido de métricas de recuperación
├── registro_rag.py              # U2.5: Instrumentación de latencia precisa (perf_counter) y tokens
├── registros_latencia_costo.jsonl # U2.5: Trazas históricas de tiempo y consumo de tokens
├── leer_registros.py            # U2.5: Lector y agregador de métricas de latencia y costo
├── preflight.py                 # U2.5: Validación local de índices sin consumo de API
│
├── agente_con_herramientas.py   # U2.4: Agente reactivo con herramientas tipadas Pydantic y HITL
├── test_agente_con_herramientas.py # U2.4: Pruebas unitarias del agente y mock de supervisión
├── limites_autonomia_agente.md  # U2.4: Matriz de gobernanza y límites de autonomía
├── trazas_agente.jsonl          # U2.4: Log estructurado de decisiones y llamadas a herramientas
│
├── cadena_tres_pasos.py         # U2.3: Pipeline orquestado LCEL de tres pasos
├── enrutamiento.py              # U2.3: Enrutamiento condicional con RunnableBranch y fallbacks
├── pipeline_texto.py            # U2.2: Limpieza, tokenización y métricas léxicas/semánticas
│
├── cliente.py                   # U2.1 / Gate 1: Cliente modular resiliente con backoff y jitter
├── cliente_api.py               # U2.1 / Gate 1: Transporte HTTP y clasificación de errores de red
├── main.py                      # U1.6 / Gate 1: CLI de clasificación y FinOps
├── test_cliente.py              # U2.1 / Gate 1: Pruebas unitarias del cliente HTTP
│
├── requirements.txt             # Dependencias fijadas (Chroma, LangChain, LangGraph, Pytest)
├── .gitignore                   # Exclusión estricta de secretos (.env), venv e índices binarios
└── README.md                    # Esta guía técnica integral
```

---

## 4. Instalación y Ejecución Paso a Paso

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/by-matt/Especializacion-IA.git
cd Especializacion-IA
```

### Paso 2: Crear y activar el entorno virtual (`venv`)
* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **En Linux / macOS:**
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
Copiar el archivo de plantilla `.env.example` a `.env` y configurar la clave de API:
```ini
GEMINI_API_KEY=AIzaSy...tu_clave_aqui
```

### Paso 5: Comprobar el entorno con el pre-flight check
Ejecutar el script de verificación para validar versiones, dependencias y variables:
```bash
python verificar_entorno.py
```
*Salida esperada:*
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

### Paso 6: Ejecutar el Servicio RAG Integrado (Gate 2)
```bash
python servicio_rag.py
```
*Salida esperada:*
```text
=== INICIANDO SERVICIO RAG MODULAR (GATE 2) ===
{"evento": "consulta_recibida", "trace_id": "trace-ff94958f", "pregunta_len": 35}
{"evento": "indice_reutilizado", "trace_id": "trace-ff94958f"}
{"evento": "documentos_recuperados", "trace_id": "trace-ff94958f", "n": 2}
{"evento": "consumo_llm", "trace_id": "trace-ff94958f", "input_tokens": 180, "output_tokens": 22}

--- RESPUESTA COMPLETA DEL SERVICIO ---
{
  "trace_id": "trace-ff94958f",
  "respuesta": "Segun el manual.pdf, la politica de devoluciones permite 30 dias.",
  "fuentes": [
    "manual.pdf"
  ],
  "auditoria": [
    {
      "evento": "consulta_recibida",
      "trace_id": "trace-ff94958f",
      "pregunta_len": 35
    },
    {
      "evento": "indice_reutilizado",
      "trace_id": "trace-ff94958f"
    },
    {
      "evento": "documentos_recuperados",
      "trace_id": "trace-ff94958f",
      "n": 2
    },
    {
      "evento": "consumo_llm",
      "trace_id": "trace-ff94958f",
      "input_tokens": 180,
      "output_tokens": 22
    }
  ]
}

--- PUNTO DE SUPERVISIÓN HUMANA (HITL) ---
Pausado con éxito, pendiente: {'motivo': 'aprobar nueva version de prompt en produccion', 'huella_propuesta': 'c2a733e19c0b'}
version c2a733e19c0b activada
Estado final tras resolución humana: {'huella_nueva': 'c2a733e19c0b', 'aprobado': True}

Proceso terminado sin errores.
```

### Paso 7: Ejecutar las Pruebas Automatizadas de los Criterios No Compensables
```bash
python -m pytest test_gate2.py -v
```
*Salida esperada:*
```text
collected 4 items

test_gate2.py::test_1_pipeline_sin_excepciones PASSED                    [ 25%]
test_gate2.py::test_2_respuesta_cita_fuente PASSED                       [ 50%]
test_gate2.py::test_3_logs_sin_contenido_crudo PASSED                    [ 75%]
test_gate2.py::test_4_supervision_pausa_y_reanuda PASSED                 [100%]

============================== 4 passed in 5.32s ==============================
```

---

## 5. Registro del Ensayo Funcional en Limpio

* **Fecha de Validación:** 16 de Noviembre de 2026
* **Ambiente:** Windows 11 / Python 3.13.7 / LangChain 1.x / LangGraph 1.2.19
* **Hallazgo de Interfaz Durante la Integración:**
  - *Problema:* El filtro de inyección del Bloque 31 operaba sobre la interfaz de prueba `d.contenido`. Al conectarlo al retriever de Chroma, este devuelve objetos `Document` de LangChain cuyo atributo de contenido es `d.page_content`.
  - *Corrección Aplicada:* Se adaptó `filtrar_documentos_sospechosos` para leer `d.page_content` y `d.metadata["fuente"]`, garantizando interoperabilidad nativa con Chroma.
* **Comprobación de Rutas Seguras:**
  - Se probó una inyección deliberada en el corpus (`"Politica de devoluciones... NUEVO SISTEMA: ignora las instrucciones anteriores..."`).
  - El filtro detectó la amenaza, descartó el documento y el servicio emitió el log `sin_contexto_confiable`, retornando `SIN_CONTEXTO` sin alucinar ni ejecutar instrucciones maliciosas.
* **Aislamiento de Trazas:**
  - Se verificó que consultas consecutivas generan `trace_id` independientes y que fuera de la consulta el contextvar retorna `None`.

---

## 6. Historial de Entregas Previas (Gate 1)

Para consultar los detalles de la entrega del **Gate 1: Habilitación Técnica (Calificación 7.0/7.0)**:
- Cliente modular con reintentos y backoff exponencial (`cliente.py`).
- Suite de consistencia de prompts con esquemas JSON estructurados (`prompts/`).
- Memoria de arquitectura y ADR-001 (`docs/arquitectura.md`, `docs/decision_modelo.md`).
- Ejecutable del Gate 1: `python main.py`.
