# Límites de Autonomía, Supervisión Humana y Auditoría del Agente
**Autor:** Byron Calderón González  
**Rol:** Ingeniero de Software & Arquitecto de Sistemas  
**Repositorio:** `https://github.com/by-matt/Especializacion-IA`  
**Entorno Operativo:** Agente de Operaciones de Infraestructura Cloud (LangChain + Gemini 2.5)

---

## 1. Filosofía de Autonomía y Principio de Menor Privilegio

En el diseño de agentes autónomos basados en modelos de lenguaje (LLMs), delegar la toma de decisiones sin salvaguardas operacionales introduce riesgos críticos de degradación de servicio, sobrecostos imprevistos e indisponibilidad. Como responsable técnico de este sistema, establezco que **la autonomía del agente nunca es absoluta**, sino graduada y acotada mediante el principio de menor privilegio (*least privilege*) y supervisión humana en el bucle (*Human-in-the-Loop, HITL*).

El agente opera en el dominio de operaciones de infraestructura y DevOps, donde coexisten consultas inocuas de telemetría y comandos destructivos con impacto en clientes finales.

---

## 2. Matriz de Clasificación de Herramientas por Nivel de Riesgo

He clasificado formalmente las herramientas del agente en tres niveles de criticidad operacional:

| Herramienta | Nivel de Riesgo | Naturaleza de la Acción | Política de Autonomía | Justificación Técnica |
|---|---|---|---|---|
| `consultar_estado_servicio` | **Bajo** | Solo lectura (*read-only*) | **Autonomía Total** | Consulta métricas de salud, uptime y latencia sin mutar el estado del clúster ni comprometer la continuidad del servicio. |
| `calcular_costo_instancias` | **Bajo** | Cálculo determinista local | **Autonomía Total** | Estima proyecciones presupuestarias en memoria. No realiza llamadas de aprovisionamiento de recursos ni genera cargos financieros en los proveedores cloud. |
| `reiniciar_servicio_critico` | **Alto** | Mutación destructiva de estado | **Bloqueo Obligatorio (HITL)** | Reinicia instancias de microservicios de producción. Puede interrumpir transacciones en vuelo, vaciar cachés calientes y provocar latencia o caída temporal. Requiere confirmación humana explícita previa vía `esperar_aprobacion()`. |

---

## 3. Mecanismo de Supervisión Humana (`esperar_aprobacion`)

Para mitigar riesgos catastróficos derivados de interpretaciones erróneas o alucinaciones del modelo:

1. **Protocolo de Intercepción:** Antes de que la herramienta `reiniciar_servicio_critico` ejecute cualquier comando de reinicio en el clúster, invoca obligatoriamente `esperar_aprobacion(mensaje, tiempo_limite_segundos=30)`.
2. **Presentación de Contexto al Operador:** El agente debe detallar al operador el servicio afectado, el motivo técnico esgrimido y el impacto previsto en las transacciones activas.
3. **Política de Falla Segura (*Fail-Safe*):**
   - Si el operador responde negativamente o transcurre el tiempo límite (30 segundos) sin respuesta, la acción es **rechazada por defecto** (*deny-by-default*).
   - En entornos no interactivos (background daemon sin TTY interactivo) o sin autorización explícita por entorno (`AGENT_AUTO_APPROVE=1` exclusivo para testing controlado), la herramienta deniega la ejecución automáticamente.
4. **Respuesta Transparente:** La herramienta retorna un mensaje explícito indicando que la operación fue abortada por falta de autorización humana, informando al agente para que adapte su plan sin entrar en bucles de reintento destructivos.

---

## 4. Auditoría Estructurada de Decisiones (`trazas_agente.jsonl`)

Toda interacción procesada por el agente —tanto consultas que disparan herramientas como aquellas resueltas puramente con conocimiento base— es instrumentada y persistida en un archivo de trazas estructuradas `trazas_agente.jsonl`.

### 4.1. Esquema de Registro JSON Lines
Cada línea del archivo representa un registro atómico con la siguiente estructura:
- `timestamp`: Marca temporal en formato ISO 8601 (UTC).
- `entrada`: Prompt original del usuario o evento disparador.
- `salida`: Respuesta final generada por el agente.
- `herramientas_invocadas`: Lista detallada de cada herramienta ejecutada, con sus argumentos validados por Pydantic y el resultado devuelto.
- `conteo_herramientas`: Número total de llamadas intermedias realizadas.
- `nivel_riesgo`: Calificación de riesgo del paso más sensible (`BAJO` o `ALTO`).
- `requirio_supervision`: Booleano que acredita si la interacción requirió aprobación humana en el flujo.

### 4.2. Cadencia de Revisión y Detección de Bucles Anómalos
- **Revisión en Línea:** La función `marcar_repeticiones_sospechosas(archivo, umbral_repeticiones=3)` analiza de forma automatizada las trazas para identificar patrones donde el agente invoque la misma herramienta 3 o más veces consecutivas para una misma consulta, señal inequívoca de bucle de razonamiento (*reasoning loop*) o parámetro rechazado iterativamente.
- **Auditoría Periódica:** Revisión diaria de trazas con filtro `nivel_riesgo == "ALTO"` para contrastar las aprobaciones concedidas contra los incidentes reportados en los tableros de observabilidad.

---

## 5. Plan de Respuesta ante Comportamiento Inesperado

Si el agente exhibe comportamientos erráticos, degradación en sus decisiones o intentos persistentes de evadir las salvaguardas:

1. **Aislamiento Inmediato (*Kill-Switch*):**
   - Revocación de las credenciales de API del agente mediante rotación instantánea de variables de entorno (`GEMINI_API_KEY`).
   - Detención de los procesos de ejecución en el servidor o contenedor.
2. **Degradación a Modo Solo-Lectura (*Read-Only Fallback*):**
   - En caso de requerir mantener el agente activo para asistencia informativa, se desacopla la herramienta `reiniciar_servicio_critico` de la lista de herramientas disponibles en `construir_agente_operaciones()`, restringiendo la factoría exclusivamente a herramientas de consulta.
3. **Análisis de Causa Raíz (RCA):**
   - Descarga e inspección de `trazas_agente.jsonl` correlacionada con las alertas de Prometheus y logs de la plataforma.
   - Ajuste de los esquemas Pydantic y refuerzo del System Prompt con *few-shot examples* de contención antes de cualquier reactivación en producción.

---
*Documento de gobernanza técnica elaborado y suscrito por Byron Calderón González.*
