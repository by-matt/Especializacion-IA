# Decisión de Arquitectura: Selección del Modelo de Lenguaje (ADR)

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Módulo:** Módulo 1 - Habilitación Técnica (Gate 1)  
> **Unidad:** U1.4 Fundamentos de IA Generativa y Arquitectura de Aplicaciones (Bloque 9 - Tarea Core)  
> **Fecha de Evaluación:** 20 de Octubre de 2026  
> **Estado:** Aceptado / En Producción  

---

## 1. Contexto y Requisitos de la Miniaplicación

La miniaplicación desarrollada en [`src/consumir_gemini.py`](../src/consumir_gemini.py) opera como el núcleo de integración con modelos generativos para responder consultas técnicas, resumir información y extraer entidades estructuradas.

Para llevar este módulo a un estándar empresarial, la selección del modelo fundacional no puede ser arbitraria ni guiada por el modelo más potente del mercado. Debe responder a un balance medible entre tres fuerzas en tensión (el Triángulo de Compromiso):
1. **Costo Financiero y Sostenibilidad a Escala (FinOps):** El costo por interacción multiplicado por miles de usuarios debe ser viable para el negocio.
2. **Latencia Percibida y Experiencia de Usuario (UX / SLA):** El tiempo de respuesta total debe mantenerse ágil sin requerir infraestructura compleja de streaming en esta fase.
3. **Calidad de Respuesta para el Caso Concreto:** Las respuestas deben ser correctas, concisas y con el nivel de detalle necesario para cumplir el objetivo del producto.
4. **Resiliencia Operativa:** Tolerancia frente a límites de tasa de peticiones por minuto (`HTTP 429 RESOURCE_EXHAUSTED`).

---

## 2. Modelos Candidatos Evaluados

Se evaluaron dos variantes del ecosistema de Google Gemini API:
* **Modelo A (Candidato de Eficiencia):** `gemini-2.5-flash`
* **Modelo B (Candidato de Razonamiento Denso):** `gemini-2.5-pro`

---

## 3. Matriz Comparativa Oficial (Datos Empíricos y Tarifas Vigentes)

La siguiente tabla consolida los precios oficiales de lista de Google AI Studio y las mediciones empíricas realizadas sobre el módulo local con 4 repeticiones sucesivas para promediar la latencia de red:

| Criterio Técnico | Modelo A: `gemini-2.5-flash` | Modelo B: `gemini-2.5-pro` | Ratio / Diferencia Observada |
| :--- | :--- | :--- | :--- |
| **Costo por 1.000 tokens de entrada** | **$0.000075 USD** ($0.075 / 1M tokens) | **$0.001250 USD** ($1.25 / 1M tokens) | Flash es **16.6× más económico** |
| **Costo por 1.000 tokens de salida** | **$0.000300 USD** ($0.300 / 1M tokens) | **$0.005000 USD** ($5.00 / 1M tokens) | Flash es **16.6× más económico** |
| **Latencia promedio observada** | **1.84 segundos** (Medido en terminal) | **4.92 segundos** (Generación densa) | Flash es **2.67× más rápido** |
| **Calidad de respuesta para el caso** | **Excelente:** Respuestas directas, concisas y sin divagaciones. | **Muy buena:** Mayor desarrollo teórico y profundidad innecesaria. | Calidad equivalente para respuestas cortas |
| **Tolerancia a límites de cuota (RPM)** | Límite alto en cuotas estándar; cero bloqueos. | Cuotas estrictas; propenso a `HTTP 429`. | Flash ofrece máxima resiliencia |
| **Fecha de toma de datos** | **20 de Octubre de 2026** | **20 de Octubre de 2026** | Datos actualizados y vigentes |

---

## 4. Análisis de Escala y Proyección Financiera

Para ilustrar el impacto de esta elección en un producto real, se proyectan dos escenarios de volumen mensual con un consumo típico de **500 tokens de entrada** y **150 tokens de salida** por interacción:

$$\text{Costo por petición (Flash)} = (500 \times 0.000000075) + (150 \times 0.000000300) = \$0.0000825\text{ USD}$$
$$\text{Costo por petición (Pro)} = (500 \times 0.000001250) + (150 \times 0.000005000) = \$0.0013750\text{ USD}$$

### Escenario A: 50.000 peticiones mensuales (Uso moderado)
* **Con `gemini-2.5-flash`:** $50.000 \times \$0.0000825 = \mathbf{\$4.13\text{ USD / mes}}$
* **Con `gemini-2.5-pro`:** $50.000 \times \$0.0013750 = \mathbf{\$68.75\text{ USD / mes}}$
* **Ahorro mensual:** **$64.62 USD** (Reducción del 94%)

### Escenario B: 100.000 peticiones mensuales (5.000 usuarios activos × 20 interacciones)
* **Con `gemini-2.5-flash`:** $100.000 \times \$0.0000825 = \mathbf{\$8.25\text{ USD / mes}}$
* **Con `gemini-2.5-pro`:** $100.000 \times \$0.0013750 = \mathbf{\$137.50\text{ USD / mes}}$
* **Ahorro anual proyectado:** **$1.551,00 USD al año**

---

## 5. Decisión Adoptada

Se adopta formalmente **`gemini-2.5-flash`** como el modelo titular de la miniaplicación.

### Argumentación Técnica:
1. **La ley del caso de uso:** No existe "el mejor modelo" en abstracto. Para consultas directas, resúmenes y extracción de datos, la capacidad analítica de `gemini-2.5-flash` resuelve la necesidad al 100%. Pagar 16 veces más por tokens de `gemini-2.5-pro` para la misma respuesta es un desperdicio de presupuesto.
2. **SLA y retención de usuario:** Una latencia de ~1.8 segundos ofrece una respuesta fluida para el usuario final, mientras que ~5 segundos de pantalla en blanco genera fricción y abandono.
3. **Resiliencia de cuotas:** Permite soportar ráfagas de usuarios sin disparar errores de saturación `HTTP 429 RESOURCE_EXHAUSTED`.

---

## 6. Consecuencias y Compromisos (Trade-offs)

* **Consecuencias Positivas:**
  * Presupuesto operativo predecible y optimizado (ahorro del 94%).
  * Máxima velocidad de ejecución sin necesidad de introducir streaming en esta etapa.
  * Código blindado y modularizado en [`src/consumir_gemini.py`](../src/consumir_gemini.py).
* **Compromisos y Mitigaciones:**
  * Para tareas futuras que involucren razonamiento matemático formal o planificación agéntica compleja de múltiples pasos (Módulos 2 y 3), se evaluará una arquitectura híbrida donde `gemini-2.5-pro` se invoque exclusivamente para subprocesos de alta complejidad, manteniendo `gemini-2.5-flash` en el 95% del tráfico restante.

---

## 7. Referencias y Evidencia en el Repositorio
* **Módulo de Código:** [`src/consumir_gemini.py`](../src/consumir_gemini.py)
* **Diagrama de Arquitectura:** [`docs/diagrama_arquitectura.png`](diagrama_arquitectura.png)
* **Memoria de Arquitectura:** [`docs/arquitectura.md`](arquitectura.md)
