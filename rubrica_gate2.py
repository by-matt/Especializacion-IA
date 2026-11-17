"""
Simulador de Evaluación y Rúbrica Ponderada del Gate 2 (Bloque S1)
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González

Modela las 6 dimensiones de la rúbrica y la regla estricta de los 4 criterios no compensables:
- Pipeline RAG funcional (25%)
- Calidad de la recuperación y citación de fuentes (15%)
- Costo, latencia y checklist operativo (10%)
- Personalización justificada (15%)
- Observabilidad y trazabilidad (15%)
- Seguridad, versionado y gobernanza (20%)
"""


def promedio_ponderado(puntajes, pesos):
    return sum(puntajes[d] * pesos[d] for d in pesos)


pesos = {
    "pipeline_funcional": 0.25,
    "recuperacion_citacion": 0.15,
    "costo_latencia": 0.10,
    "personalizacion": 0.15,
    "observabilidad": 0.15,
    "seguridad_gobernanza": 0.20,
}


def evaluar_gate(puntajes, no_compensables_ok, umbral=80):
    promedio = promedio_ponderado(puntajes, pesos)
    aprueba = promedio >= umbral and no_compensables_ok
    return promedio, aprueba


if __name__ == "__main__":
    print("=== SIMULADOR DE EVALUACIÓN GATE 2 ===")
    print("Suma de pesos de la rúbrica:", sum(pesos.values()))

    # Puntajes modelo de alta efectividad técnica
    puntajes = {
        "pipeline_funcional": 95,
        "recuperacion_citacion": 90,
        "costo_latencia": 85,
        "personalizacion": 88,
        "observabilidad": 92,
        "seguridad_gobernanza": 80,
    }

    # Caso 1: promedio alto, pero los logs exponen contenido crudo sensible
    promedio_1, aprueba_1 = evaluar_gate(puntajes, no_compensables_ok=False)
    print(f"Caso 1: Promedio {promedio_1:.1f}%, No compensables OK? False -> ¿Aprueba?: {aprueba_1}")

    # Caso 2: mismo promedio exacto, no compensables OK
    promedio_2, aprueba_2 = evaluar_gate(puntajes, no_compensables_ok=True)
    print(f"Caso 2: Promedio {promedio_2:.1f}%, No compensables OK? True  -> ¿Aprueba?: {aprueba_2}")

    # Caso 3: promedio por debajo del umbral, no compensables OK
    puntajes_bajos = {k: v - 15 for k, v in puntajes.items()}
    promedio_3, aprueba_3 = evaluar_gate(puntajes_bajos, no_compensables_ok=True)
    print(f"Caso 3: Promedio {promedio_3:.1f}%, No compensables OK? True  -> ¿Aprueba?: {aprueba_3}")
