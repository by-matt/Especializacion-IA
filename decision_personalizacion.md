# Decisión de Personalización: AgroExport Compliance AI

## 1. El problema
El módulo clasificador de reportes agronómicos y no conformidades fitosanitarias de exportación presenta inconsistencias críticas de formato en tiempo de inferencia: en una muestra de 20 consultas evaluadas, 6 de ellas (30%) no respetaron el contrato JSON estricto exigido por los microservicios aguas abajo, emitiendo explicaciones conversacionales en texto libre o renombrando las claves obligatorias `categoria` y `accion_sugerida`. El modelo base ya posee comprensión agronómica de los compuestos y plagas; el fallo reside exclusivamente en la falta de consistencia de comportamiento y estructura de salida.

## 2. Resultado del método de decisión
Tras someter el caso al método cuantitativo de cinco criterios ponderados con evidencia del proyecto:

- **PEFT:** 5 puntos
- **RAG:** 2 puntos
- **Fine-tuning completo:** 1 puntos

**Estrategia seleccionada:** PEFT (5 puntos)

## 3. Técnica elegida y por qué
Se selecciona **PEFT (Parameter-Efficient Fine-Tuning) mediante Adapters (LoRA)** como la estrategia óptima.

La justificación técnica y financiera se fundamenta en las tres dimensiones de costo analizadas en el Bloque 30:

1. **Costo de Datos y Muestra Reducida:** El Fine-tuning completo requiere miles de ejemplos para evitar sobreajuste catastrófico (*catastrophic forgetting*). Dado que actualmente contamos con 12 ejemplos curados y proyectamos un dataset inicial de 80 ejemplos, un adapter LoRA con `adapter_size=ADAPTER_SIZE_FOUR` (rank 4) es capaz de fijar el comportamiento sintáctico entrenando menos del 1% de los parámetros del modelo base, a una fracción mínima del costo humano.
2. **Costo de Cómputo e Infraestructura de Servicio:** RAG fue descartado para esta tarea porque al modelo no le falta información factual (los nombres de plagas y agroquímicos son ampliamente reconocidos por Gemini), y mantener un vector store para una tarea de clasificación sintáctica añade latencia de búsqueda (5-15 ms) y costos fijos de mantenimiento. A su vez, el Fine-tuning completo exigiría reentrenar y hospedar un modelo completo e independiente por cada mercado; en contraste, PEFT permite mantener un único modelo base compartido y acoplar adapters modulares y ligeros por cliente o mercado.
3. **Costo de Tiempo y Ciclo de Iteración:** Entrenar un adapter PEFT en la API gestionada toma entre 5 y 15 minutos por trabajo, permitiendo validar rápidamente el comportamiento del validador de esquemas, a diferencia del ciclo de horas o días de un reentrenamiento total.

## 4. Qué necesitarías para ejecutarla
Para llevar a cabo el afinamiento PEFT en fase de homologación productiva se requiere:

- **Estado actual del dataset:** Disponemos de **12 ejemplos etiquetados y auditados** en `dataset_tuning.py`, distribuidos uniformemente en 5 categorías (3 de exceso de residuo, 3 de plaga cuarentenaria, 2 de carencia insuficiente, 2 de fitotoxicidad foliar y 2 de incompatibilidad de mercado).
- **Brecha cuantitativa de datos:** Para alcanzar una muestra robusta de **80 ejemplos** (16 por categoría), se requiere etiquetar **68 ejemplos adicionales**.
- **Estimación de esfuerzo humano:** A un ritmo estándar de 5 minutos por ejemplo técnico y una tarifa de USD 25/hora, el etiquetado base demanda **5.67 horas de trabajo** (aprox. USD 141.67).
- **Protocolo de control de calidad (Segunda Revisión):** Someter el 20% del dataset total (16 ejemplos) a doble revisión ciega (2 minutos por ejemplo) añade **0.53 horas** (aprox. USD 13.33), totalizando **6.20 horas hombre** (USD 155.00 o aprox. 0.9 jornadas laborales de 8 horas).
- **Infraestructura de cómputo:** Configuración formal de `CreateTuningJobConfig` en `google-genai` con `tuning_mode=TUNING_MODE_PEFT_ADAPTER`, `adapter_size=ADAPTER_SIZE_FOUR`, y `epoch_count=5`. No se requiere almacenamiento vectorial ni base de datos adicional para servir el adapter afinado.
- **Corpus documental:** Ninguno. La tarea es de comportamiento sintáctico y extracción normalizada, por lo que no se requiere indexar documentos externos.
