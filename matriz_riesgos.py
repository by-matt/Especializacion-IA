"""
Matriz de Riesgos y Gobernanza Técnica para IA Generativa (Bloque 32 - Paso 3)
Especialización en Desarrollo con IA Generativa - Accenture & Skillnest
Autor: Byron Calderón González

Prioriza cuantitativamente los riesgos del sistema RAG con personalización:
- Función de severidad matemática: Puntaje = Probabilidad (1-5) * Impacto (1-5).
- Clasificación de severidad: CRÍTICO (>=15), ALTO (>=9), MEDIO (>=4), BAJO (<4).
- Chequeo de sensibilidad en el límite para identificar riesgos frontera.
- Vinculación obligatoria de riesgos CRÍTICOS y ALTOS con puntos de supervisión humana y mitigaciones del programa.
"""


def puntaje_riesgo(probabilidad: int, impacto: int) -> int:
    """Calcula el puntaje de severidad de un riesgo."""
    return probabilidad * impacto


def categoria_riesgo(puntaje: int) -> str:
    """Determina la categoría de severidad según los umbrales estándar del programa."""
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad: int, impacto: int) -> bool:
    """
    Evalúa si una variación de ±1 punto en probabilidad o impacto
    provocaría un cambio en la categoría de riesgo.
    """
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


mis_riesgos = [
    {
        "riesgo": "Inyeccion indirecta de prompt en documentos recuperados del RAG",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": "Filtro de patrones regex + delimitacion XML <CONTEXT> + instruccion imperativa anti-inyeccion (Bloque 31)",
        "punto_supervision": "Interrupcion humana (interrupt) cuando el filtro detecta documentos sospechosos antes de construir el prompt",
    },
    {
        "riesgo": "Filtracion inadvertida de datos personales (PII) en logs de auditoria",
        "probabilidad": 3,
        "impacto": 5,
        "mitigacion": "Logging estructurado sanitizado registrando longitud y huellas SHA-256 en vez de texto plano (Bloque 31)",
        "punto_supervision": "Aprobacion humana requerida para la exportacion o concesion de acceso a registros de logs",
    },
    {
        "riesgo": "Sesgo y degradacion de respuestas por dataset de tuning desbalanceado",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": "Chequeo automatizado de distribucion balanceada y validacion estructural de esquemas JSONL (Bloque 29)",
        "punto_supervision": "Revision y firma humana del reporte de estratificacion antes de lanzar el fine-tuning",
    },
    {
        "riesgo": "Ruptura operativa por deprecacion no anticipada de modelo de embeddings",
        "probabilidad": 2,
        "impacto": 4,
        "mitigacion": "Pinning de modelos productivos (gemini-embedding-001) y monitoreo periodico de catalogo (Bloque 28)",
        "punto_supervision": "Alerta automatizada hacia equipo de arquitectura previa actualizacion de dependencias",
    },
    {
        "riesgo": "Alucinacion por persistencia de chunks obsoletos en base de datos vectorial",
        "probabilidad": 3,
        "impacto": 2,
        "mitigacion": "Control determinista de IDs de chunks y purga de indices previa a la reindexacion (Bloque 25)",
        "punto_supervision": "Validacion de frescura de corpus en despliegues a produccion",
    },
]


if __name__ == "__main__":
    print("=== MATRIZ DE RIESGOS DEL SISTEMA RAG & PERSONALIZACIÓN ===")
    for r in mis_riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])

    # Ordenar por puntaje descendente
    for r in sorted(mis_riesgos, key=lambda x: -x["puntaje"]):
        marca = "[AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']} {marca}")
        print(f"   Mitigacion: {r['mitigacion']}")
        if r["categoria"] in ("CRITICO", "ALTO"):
            print(f"   Punto de Supervision: {r['punto_supervision']}")

    print("\n=== ANÁLISIS DE SENSIBILIDAD (FILAS FRONTERA) ===")
    for r in mis_riesgos:
        if r["al_limite"]:
            print(f"Revisar con otra persona (estimacion sensible): {r['riesgo']} ({r['categoria']})")

    print("\n=== CASO DE CONTRASTE (CONTROL NEGATIVO) ===")
    p_cont, i_cont = 1, 1
    pt_cont = puntaje_riesgo(p_cont, i_cont)
    cat_cont = categoria_riesgo(pt_cont)
    lim_cont = esta_en_el_limite(p_cont, i_cont)
    print(f"Riesgo de contraste (P={p_cont}, I={i_cont}): Puntaje={pt_cont}, Categoría={cat_cont}, En el límite={lim_cont}")
