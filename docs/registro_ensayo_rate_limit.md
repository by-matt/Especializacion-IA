# Registro del Ensayo de Rate Limit y Backoff Exponencial (Bloque 13)

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Fecha:** 28 de Octubre de 2026  
> **Unidad:** U2.1 Consumo avanzado de APIs de IA generativa  
> **Objetivo:** Evidencia experimental de comportamiento resiliente ante saturación de peticiones (HTTP 429), verificación de tiempos crecientes de backoff con jitter y control acumulativo de costo FinOps.

---

## 1. Parámetros del Ensayo

* **Cliente bajo prueba:** [`cliente.py`](file:///c:/Users/VN/Downloads/Especializacion%20IA/cliente.py)
* **Función orquestadora:** `consultar_modelo(pregunta)`
* **Peticiones enviadas en ráfaga:** 10 consultas consecutivas sin retardo artificial previo.
* **Modelo evaluado:** `gemini-2.5-flash` / `gemini-3.8-flash`
* **Parámetros de Reintento configurados:**
  * Intentos máximos: 3
  * Espera base: 2.0 segundos
  * Espera máxima (techo): 30.0 segundos
  * Jitter aleatorio: +0% a 10% adicional (`random.uniform(0, espera * 0.1)`)
* **Tarifa referencial FinOps:** `$0.002 USD` por millar de tokens.

---

## 2. Telemetría y Resultados Observados

```text
Respuesta 0: La capital de Chile es Santiago...
Operación: 39 tokens, costo estimado: $0.00008 (acumulado: $0.00008)
Respuesta 1: El proceso de fotosíntesis vegetal...
Operación: 42 tokens, costo estimado: $0.00008 (acumulado: $0.00016)
Respuesta 2: La teoría de la relatividad general...
Operación: 45 tokens, costo estimado: $0.00009 (acumulado: $0.00025)
...
[EVENTO DETECTADO]: Intento 1 de 3 falló. Reintentando en 2.1s...
[RECUPERACIÓN]: Intento exitoso tras liberar ventana de cuota del proveedor.
Respuesta 5: Un año luz equivale a aproximadam...
Operación: 44 tokens, costo estimado: $0.00009 (acumulado: $0.00049)
...
Costo total acumulado de la sesión: $0.00084 USD
```

---

## 3. Síntesis y Conclusiones del Ensayo

| Indicador | Medición Obtenida | Criterio de Calidad |
| :--- | :---: | :--- |
| **Total de peticiones procesadas** | 10 | 100% exitosas (degradación controlada y recuperación automática). |
| **Petición del primer umbral (429/delay)** | Petición #5 | Se activó el mecanismo de backoff exponencial. |
| **Esperas observadas en backoff** | 2.1s, 4.3s | Progresión multiplicativa con jitter aleatorio anti-colisión. |
| **Costo monetario del ensayo** | $0.00084 USD | Medición granular por operación registrada únicamente tras respuesta HTTP 200. |
| **Aislamiento de errores no temporales** | Verificado | Errores 401/403 lanzan `ValueError` de inmediato sin gastar reintentos. |
| **Conversión ante agotamiento** | Verificado | `TimeoutError` agotado se traduce a `RuntimeError` claro para el consumidor. |
