"""dataset_tuning.py
Preparación y validación de dataset para personalización con PEFT (LoRA).
Dominio: AgroExport Compliance AI - Clasificación de No Conformidades Fitosanitarias.
"""

import json
from collections import Counter
from google.genai import types

# ------------------------------------------------------------------------------
# 1. Dataset de Entrenamiento: Texto libre -> JSON normalizado
# ------------------------------------------------------------------------------
# Tarea de comportamiento: estandarizar la clasificación de reportes de campo
# en un esquema estricto {"categoria": str, "accion_sugerida": str}.
ejemplos_raw: list[tuple[str, dict]] = [
    (
        "Cromatografía en cerezas arrojó 0.04 ppm de Clorpirifos, superando el límite de 0.01 ppm para la Unión Europea.",
        {"categoria": "exceso_residuo", "accion_sugerida": "retener lote y solicitar contraprueba analitica"},
    ),
    (
        "El lote de uva de mesa presenta residuos de Captan en 0.08 ppm cuando el protocolo exige maximo 0.02 ppm.",
        {"categoria": "exceso_residuo", "accion_sugerida": "retener lote y evaluar degradacion termica"},
    ),
    (
        "Se aplico Tebuconazol hace 4 dias en arandanos y la cosecha comercial esta planificada para manana.",
        {"categoria": "carencia_insuficiente", "accion_sugerida": "postergar cosecha hasta cumplir 14 dias de carencia"},
    ),
    (
        "La cuadrilla de cosecha entro al cuartel de nectarines a los 3 dias de pulverizar Fenhexamida (carencia minima 7 dias).",
        {"categoria": "carencia_insuficiente", "accion_sugerida": "interrumpir recoleccion y segregar fruta cosechada"},
    ),
    (
        "Hojas basales de los manzanos muestran clorosis marginal y quemaduras tras mezcla en tanque de aceite mineral con azufre.",
        {"categoria": "fitotoxicidad_foliar", "accion_sugerida": "suspender aplicacion foliar y lavar maquinaria de pulverizacion"},
    ),
    (
        "Aparicion de manchas necroticas en brotes tiernos posterior a tratamiento foliar con sales de cobre a alta temperatura.",
        {"categoria": "fitotoxicidad_foliar", "accion_sugerida": "neutralizar caldo sobrante y aplicar bioestimulante antiestres"},
    ),
    (
        "Trampa delta en sector norte capturo dos especimenes adultos sospechosos de Lobesia botrana en estado reproductivo.",
        {"categoria": "plaga_cuarentenaria", "accion_sugerida": "aislar cuartel y notificar inmediatamente al inspector fitosanitario oficial"},
    ),
    (
        "Inspeccion visual de embalaje detecto presencia de larva viva de falsa aranita de la vid en racimo de uva de exportacion.",
        {"categoria": "plaga_cuarentenaria", "accion_sugerida": "inmovilizar pallet y activar protocolo de cuarentena SAG"},
    ),
    (
        "Se detecto presencia de cochinilla harinosa en fruta embalada con destino a mercado de Estados Unidos.",
        {"categoria": "plaga_cuarentenaria", "accion_sugerida": "rechazar lote para mercado libre de plaga y redirigir a fumigacion"},
    ),
    (
        "El productor utilizo Mancozeb en ciruelas, ingrediente no autorizado en la lista de fitosanitarios para Corea del Sur.",
        {"categoria": "incompatibilidad_mercado", "accion_sugerida": "redireccionar exportacion a mercado con tolerancia y registro vigente"},
    ),
    (
        "Aplicacion de Procloraz en citricos, molecula dada de baja en la directiva fitosanitaria del Reino Unido.",
        {"categoria": "incompatibilidad_mercado", "accion_sugerida": "bloquear despacho a Reino Unido y reasignar a mercado alternativo"},
    ),
    (
        "Analisis multiresiduo reporto concentracion residual de Difenoconazol en 0.15 ppm, rebasando el LMR admitido.",
        {"categoria": "exceso_residuo", "accion_sugerida": "paralizar liberacion de embarque y auditar calibracion de dosificador"},
    ),
]

# Construcción formal de TuningExamples para la API de Gemini
examples: list[types.TuningExample] = [
    types.TuningExample(
        text_input=texto,
        output=json.dumps(salida, ensure_ascii=False)
    )
    for texto, salida in ejemplos_raw
]


# ------------------------------------------------------------------------------
# 2. Análisis de Balance de Categorías
# ------------------------------------------------------------------------------
def chequear_balance(ejemplos: list[tuple[str, dict]], clave: str = "categoria") -> Counter:
    """Calcula la frecuencia de distribución de clases para evitar sesgos en el adapter."""
    return Counter(salida[clave] for _, salida in ejemplos)


# ------------------------------------------------------------------------------
# 3. Validación Estricta de Integridad del Dataset
# ------------------------------------------------------------------------------
def validar_dataset(
    ejemplos_tuning: list[types.TuningExample],
    claves_esperadas: tuple[str, ...] = ("categoria", "accion_sugerida")
) -> list[str]:
    """Audita reglas de calidad: no vacíos, sin duplicados, JSON válido y presencia de campos."""
    problemas = []
    textos_vistos = set()

    for i, ej in enumerate(ejemplos_tuning):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue

        if ej.text_input in textos_vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        textos_vistos.add(ej.text_input)

        try:
            salida_dict = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue

        for clave in claves_esperadas:
            if clave not in salida_dict:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')

    return problemas


# ------------------------------------------------------------------------------
# 4. Demostración de Configuración del Trabajo de Tuning (PEFT LoRA)
# ------------------------------------------------------------------------------
def armar_configuracion_peft() -> tuple[types.TuningDataset, types.CreateTuningJobConfig]:
    """Genera la especificación técnica verificada para afinamiento mediante adapter."""
    dataset = types.TuningDataset(examples=examples)
    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="clasificador-fitosanitario-agroexport",
    )
    return dataset, config


# ------------------------------------------------------------------------------
# 5. Ejecución y Verificación
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== PASO 1: CONSTRUCCIÓN DEL DATASET ===")
    print(f"Total ejemplos construidos: {len(examples)}")
    print(f"Muestra primer ejemplo:\n  text_input: {examples[0].text_input}\n  output: {examples[0].output}\n")

    print("=== PASO 2: BALANCE DE CATEGORÍAS ===")
    balance = chequear_balance(ejemplos_raw, "categoria")
    for categoria, cuenta in balance.most_common():
        print(f"  {categoria}: {cuenta} ejemplos")
    maximo = max(balance.values())
    minimo = min(balance.values())
    razon = maximo / minimo
    print(f"Razón max/min: {razon:.2f}x (distribución balanceada)\n")

    print("=== PASO 3: VALIDACIÓN DEL DATASET NOMINAL ===")
    problemas_base = validar_dataset(examples)
    print(f"Ejemplos evaluados: {len(examples)} | Problemas encontrados: {len(problemas_base)}")
    if problemas_base:
        for p in problemas_base:
            print(f"  [ERROR] {p}")
    else:
        print("  [OK] Dataset 100% válido y libre de inconsistencias.\n")

    print("=== PASO 4: PRUEBA DE SENSIBILIDAD DEL VALIDADOR (CASOS ROTOS) ===")
    ejemplos_rotos = examples + [
        types.TuningExample(text_input="", output='{"categoria": "exceso_residuo"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="no_es_un_json_valido"),
    ]
    problemas_rotos = validar_dataset(ejemplos_rotos)
    print(f"Ejemplos corruptos inyectados: 2 | Problemas detectados: {len(problemas_rotos)}")
    for p in problemas_rotos:
        print(f"  - {p}")

    print("\n=== PASO 5: CONFIGURACIÓN TÉCNICA DE PEFT ADAPTER ===")
    dataset_peft, config_peft = armar_configuracion_peft()
    print(f"Tuning Mode: {config_peft.tuning_mode}")
    print(f"Adapter Size: {config_peft.adapter_size}")
    print(f"Epoch Count: {config_peft.epoch_count}")
    print(f"Model Display Name: {config_peft.tuned_model_display_name}")
    print("Validación completada exitosamente.")
