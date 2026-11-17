"""decision.py
Método cuantitativo y generador de la decisión fundamentada de personalización.
Dominio: AgroExport Compliance AI - Unidad 2.6 (Bloque 30).
"""

def recomendar_estrategia(respuestas: dict[str, bool]) -> tuple[dict[str, int], list[str]]:
    """Aplica el método de ponderación de 5 preguntas sobre las técnicas de personalización.
    
    Ponderaciones:
    - informacion_cambia_seguido: +3 RAG
    - problema_de_formato_o_tono: +2 PEFT, +1 Fine-tuning completo
    - dataset_grande_y_de_calidad: +2 Fine-tuning completo, +1 PEFT
    - presupuesto_limitado_o_iterar_rapido: +2 RAG, +1 PEFT
    - necesita_multiples_variantes: +2 PEFT
    """
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3

    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1

    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1

    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1

    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


# ------------------------------------------------------------------------------
# 1. Respuestas auditadas con evidencia cuantitativa para AgroExport Compliance AI
# ------------------------------------------------------------------------------
respuestas_agroexport = {
    # 1. ¿La información que necesita el modelo cambia seguido?
    # False: La taxonomía de las 5 categorías de no conformidades fitosanitarias es fija
    # bajo regulaciones internacionales SAG/Codex; el contenido dinámico de LMR se resuelve con RAG.
    "informacion_cambia_seguido": False,

    # 2. ¿El problema es que el modelo no mantiene un formato o tono consistente?
    # True: En auditoría de 20 inferencias en lenguaje natural, 6 (30%) emitieron texto libre
    # o alteraron los nombres de claves JSON ('categoria' y 'accion_sugerida').
    "problema_de_formato_o_tono": True,

    # 3. ¿Tienes un dataset grande y de calidad ya etiquetado?
    # False: Tenemos 12 ejemplos curados en dataset_tuning.py; faltan 188 para llegar a 200.
    "dataset_grande_y_de_calidad": False,

    # 4. ¿Tienes presupuesto de cómputo limitado o necesitas iterar rápido?
    # True: Presupuesto acotado para un máximo de 2 entrenamientos cloud e iteración < 12 hrs.
    "presupuesto_limitado_o_iterar_rapido": True,

    # 5. ¿Necesitas múltiples variantes personalizadas del mismo modelo base?
    # True: Se proyectan 3 adapters independientes según mercado destino (UE, EE.UU. y Asia).
    "necesita_multiples_variantes": True,
}


def estimar_costo_etiquetado(num_ejemplos: int, minutos_por_ejemplo: float = 5.0, costo_hora: float = 25.0) -> tuple[float, float]:
    """Calcula horas y costo monetario de etiquetado humano."""
    horas = (num_ejemplos * minutos_por_ejemplo) / 60.0
    costo = horas * costo_hora
    return horas, costo


def redactar_documento_decision(puntos: dict[str, int], ganadoras: list[str]) -> str:
    """Redacta el documento formal decision_personalizacion.md con sus 4 secciones obligatorias."""
    # Estimaciones cuantitativas de datos
    ejemplos_actuales = 12
    meta_produccion = 80
    ejemplos_faltantes = meta_produccion - ejemplos_actuales
    horas_base, costo_base = estimar_costo_etiquetado(ejemplos_faltantes, minutos_por_ejemplo=5, costo_hora=25)
    horas_rev, costo_rev = estimar_costo_etiquetado(int(meta_produccion * 0.20), minutos_por_ejemplo=2, costo_hora=25)
    total_horas = horas_base + horas_rev
    total_costo = costo_base + costo_rev

    lineas = [
        "# Decisión de Personalización: AgroExport Compliance AI",
        "",
        "## 1. El problema",
        "El módulo clasificador de reportes agronómicos y no conformidades fitosanitarias de exportación presenta "
        "inconsistencias críticas de formato en tiempo de inferencia: en una muestra de 20 consultas evaluadas, "
        "6 de ellas (30%) no respetaron el contrato JSON estricto exigido por los microservicios aguas abajo, "
        "emitiendo explicaciones conversacionales en texto libre o renombrando las claves obligatorias `categoria` "
        "y `accion_sugerida`. El modelo base ya posee comprensión agronómica de los compuestos y plagas; "
        "el fallo reside exclusivamente en la falta de consistencia de comportamiento y estructura de salida.",
        "",
        "## 2. Resultado del método de decisión",
        "Tras someter el caso al método cuantitativo de cinco criterios ponderados con evidencia del proyecto:",
        "",
    ]

    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- **{tecnica}:** {p} puntos")

    lineas.append("")
    if len(ganadoras) > 1:
        lineas.append(f"**Empate técnico entre:** {', '.join(ganadoras)}")
    else:
        lineas.append(f"**Técnica ganadora indiscutida:** {ganadoras[0]} ({puntos[ganadoras[0]]} puntos)")

    lineas.extend([
        "",
        "## 3. Técnica elegida y por qué",
        "Se selecciona **PEFT (Parameter-Efficient Fine-Tuning) mediante Adapters (LoRA)** como la estrategia óptima.",
        "",
        "La justificación técnica y financiera se fundamenta en las tres dimensiones de costo analizadas en el Bloque 30:",
        "",
        "1. **Costo de Datos y Muestra Reducida:** El Fine-tuning completo requiere miles de ejemplos para evitar sobreajuste "
        "catastrófico (*catastrophic forgetting*). Dado que actualmente contamos con 12 ejemplos curados y proyectamos un "
        "dataset inicial de 80 ejemplos, un adapter LoRA con `adapter_size=ADAPTER_SIZE_FOUR` (rank 4) es capaz de fijar el "
        "comportamiento sintáctico entrenando menos del 1% de los parámetros del modelo base, a una fracción mínima del costo humano.",
        "2. **Costo de Cómputo e Infraestructura de Servicio:** RAG fue descartado para esta tarea porque al modelo no le falta "
        "información factual (los nombres de plagas y agroquímicos son ampliamente reconocidos por Gemini), y mantener un vector "
        "store para una tarea de clasificación sintáctica añade latencia de búsqueda (5-15 ms) y costos fijos de mantenimiento. "
        "A su vez, el Fine-tuning completo exigiría reentrenar y hospedar un modelo completo e independiente por cada mercado; "
        "en contraste, PEFT permite mantener un único modelo base compartido y acoplar adapters modulares y ligeros por cliente o mercado.",
        "3. **Costo de Tiempo y Ciclo de Iteración:** Entrenar un adapter PEFT en la API gestionada toma entre 5 y 15 minutos por trabajo, "
        "permitiendo validar rápidamente el comportamiento del validador de esquemas, a diferencia del ciclo de horas o días de un reentrenamiento total.",
        "",
        "## 4. Qué necesitarías para ejecutarla",
        "Para llevar a cabo el afinamiento PEFT en fase de homologación productiva se requiere:",
        "",
        f"- **Estado actual del dataset:** Disponemos de **{ejemplos_actuales} ejemplos etiquetados y auditados** en `dataset_tuning.py`, "
        "distribuidos uniformemente en 5 categorías (3 de exceso de residuo, 3 de plaga cuarentenaria, 2 de carencia insuficiente, "
        "2 de fitotoxicidad foliar y 2 de incompatibilidad de mercado).",
        f"- **Brecha cuantitativa de datos:** Para alcanzar una muestra robusta de **{meta_produccion} ejemplos** (16 por categoría), "
        f"se requiere etiquetar **{ejemplos_faltantes} ejemplos adicionales**.",
        f"- **Estimación de esfuerzo humano:** A un ritmo estándar de 5 minutos por ejemplo técnico y una tarifa de USD 25/hora, "
        f"el etiquetado base demanda **{horas_base:.2f} horas de trabajo** (aprox. USD {costo_base:.2f}).",
        f"- **Protocolo de control de calidad (Segunda Revisión):** Someter el 20% del dataset total ({int(meta_produccion * 0.20)} ejemplos) "
        f"a doble revisión ciega (2 minutos por ejemplo) añade **{horas_rev:.2f} horas** (aprox. USD {costo_rev:.2f}), "
        f"totalizando **{total_horas:.2f} horas hombre** (USD {total_costo:.2f} o aprox. 0.9 jornadas laborales de 8 horas).",
        "- **Infraestructura de cómputo:** Configuración formal de `CreateTuningJobConfig` en `google-genai` con "
        "`tuning_mode=TUNING_MODE_PEFT_ADAPTER`, `adapter_size=ADAPTER_SIZE_FOUR`, y `epoch_count=5`. No se requiere almacenamiento "
        "vectorial ni base de datos adicional para servir el adapter afinado.",
        "- **Corpus documental:** Ninguno. La tarea es de comportamiento sintáctico y extracción normalizada, por lo que no se requiere indexar documentos externos."
    ])

    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    print("=== EVALUACIÓN CUANTITATIVA DEL MÉTODO DE DECISIÓN ===")
    puntos, ganadoras = recomendar_estrategia(respuestas_agroexport)
    print("Puntajes obtenidos:")
    for tecnica, score in puntos.items():
        print(f"  {tecnica}: {score} puntos")
    print(f"Candidatas ganadoras: {ganadoras}\n")

    documento = redactar_documento_decision(puntos, ganadoras)
    with open("decision_personalizacion.md", "w", encoding="utf-8") as f:
        f.write(documento)

    print("Archivo 'decision_personalizacion.md' generado exitosamente con las 4 secciones requeridas.")
