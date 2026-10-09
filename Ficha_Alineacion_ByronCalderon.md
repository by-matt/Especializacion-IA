# Plantilla: Ficha de Alineación Técnica

> **Instrucciones:** Completa esta plantilla con lo trabajado en el documento de la clase ("Completa tu Ficha de Alineación Técnica y elige tu ruta"), conviértela a PDF y súbela en la plataforma como archivo adjunto. Tu nombre y la fecha de entrega ya quedan registrados por sistema al subir el archivo, así que la ficha parte directo en el contenido.

---

### Datos generales

Escribe el nombre del perfil que elegiste: *Backend / Integración de APIs*, *Frontend / Producto*, *QA / Soporte técnico*, o *Data / DevOps junior*. Si tu experiencia previa no calza bien con ninguno de los 4, escribe "Personalizado" y descríbelo en la fila de abajo: no te limita, solo ayuda al equipo docente a acompañarte mejor.

| Campo | Detalle |
| :--- | :--- |
| **Perfil de egreso seleccionado** | Personalizado |
| **Si es "Personalizado", descríbelo aquí** | Ingeniero en Biotecnología. No provengo del desarrollo de software tradicional, pero utilizo intensivamente herramientas de IA para resolver problemas técnicos y automatizar tareas. Mi objetivo es integrar perfiles: aprovechar mi base en biotecnología y análisis de datos, y aprender a construir servicios backend e integraciones de APIs con IA que sean robustos, útiles y testeados en producción. |

---

### Diagnóstico técnico

En "Nivel" marca del 1 (recién partiendo) al 5 (lo dominas) qué tan cómodo te sientes hoy en cada área. En "Comentario" anota algo puntual solo si te ayuda a explicar tu nivel (ej. una herramienta específica que ya usaste, o un tipo de error que aún te cuesta).

| Área | Nivel (1 a 5) | Comentario breve |
| :--- | :---: | :--- |
| **Python (variables, funciones, manejo de errores)** | 3 | Me apoyo bastante en herramientas de IA para generar y depurar código; entiendo variables, funciones y control de flujo, pero busco ganar autonomía en la estructuración de scripts más complejos y manejo sistemático de excepciones. |
| **Git y control de versiones (commits, ramas, remotos)** | 2 | Conozco los comandos elementales (commit, push, clone), pero me cuesta el trabajo con ramas, la resolución de conflictos y entender el estado del repositorio sin asistencia paso a paso. |
| **Consumo de APIs (peticiones HTTP, JSON, autenticación)** | 3 | He realizado peticiones a servicios guiado por asistentes de IA y comprendo el formato JSON y las API keys; mi brecha está en dominar el ciclo HTTP, el control de rate limits y reintentos por código propio. |
| **Entorno de desarrollo (terminal, entorno virtual, dependencias)** | 3 | Me desenvuelvo en la terminal para lo esencial (instalar paquetes, activar entornos virtuales); cuando surgen conflictos de dependencias o variables de entorno, dependo de la IA para diagnosticarlos. |

---

### Problema de negocio tentativo para tu proyecto

En 2 o 3 líneas: a quién ayuda tu proyecto, qué pregunta o tarea resuelve, y con qué información cuenta para responder. No necesita ser definitivo, lo vas a poder ajustar durante el Módulo 1.

| Descripción del problema de negocio |
| :--- |
| Ayuda a profesionales, analistas e investigadores en biotecnología a consultar y validar condiciones de bioprocesos o protocolos de laboratorio. Resuelve la tarea de buscar y extraer de forma confiable parámetros clave (rangos de pH, temperatura, sustratos y tasas de rendimiento) y normas de bioseguridad, respondiendo a partir de un conjunto de documentos técnicos, fichas y literatura especializada indexada mediante RAG. |

---

### Progresión de los 3 Gates, en tus palabras

Explica por qué lo que entregas en el Gate 1 no se descarta en el Gate 2, y por qué lo del Gate 2 no se descarta en el Gate 3. Evita copiar la definición del documento de la clase, cuéntalo con tus propias palabras.

| Progresión conceptual de los Gates |
| :--- |
| En el **Gate 1** construyo la base técnica para comunicarme con un modelo vía API de forma confiable, logrando que procese entradas y responda en JSON sin caerse ante errores de red. En el **Gate 2** no descarto ese código: lo convierto en el motor interno para que ahora consulte mis propios documentos de biotecnología (RAG) y tome decisiones mediante herramientas y agentes. Finalmente, en el **Gate 3**, tomo esa solución y la empaqueto como un producto real: la expongo como una API web con FastAPI, la meto dentro de un contenedor Docker para que corra en cualquier máquina sin configurar nada extra, y le agrego matrices de pruebas y control de riesgos. |

---

### Criterios críticos no compensables, en tus palabras

Para cada Gate, anota una condición puntual que, si no se cumple, debería hacer fallar la entrega aunque el resto esté bien resuelto (ej. "que el servicio no corra en el contenedor"). Es tu hipótesis inicial, no necesita ser exacta.

| Gate | Criterio crítico no compensable (hipótesis) |
| :--- | :--- |
| **Gate 1 (Habilitación técnica)** | **Manejo de errores de API y no exponer secretos:** Que el programa capture caídas de conexión o límites de consulta (rate limits) sin cerrarse abruptamente, y que las credenciales/API keys jamás se suban al repositorio de Git (.env en .gitignore). |
| **Gate 2 (Integración y orquestación)** | **Cero alucinación y respaldo en fuentes RAG:** Que el sistema no invente datos y responda exclusivamente respaldado en los documentos indexados, citando la fuente o declarando con honestidad que la información no está disponible si no la encuentra. |
| **Gate 3 / Capstone** | **Ejecución 100% reproducible en Docker:** Que la aplicación completa se pueda clonar y levantar en cualquier máquina únicamente con Docker, funcionando en sus endpoints sin requerir instalaciones manuales previas ni fallar por configuraciones locales. |

---

### Tu punto de partida declarado (fortalezas y brechas)

Resume en 2 o 3 líneas qué es lo que ya sabes hacer bien (tus fortalezas) y en qué áreas sabes que vas a necesitar más práctica (tus brechas), conectándolo con lo que marcaste en el diagnóstico técnico.

| Fortalezas y brechas declaradas |
| :--- |
| **Fortalezas:** Pensamiento analítico y metodológico propio de la biotecnología, y gran soltura aprovechando herramientas de IA para estructurar ideas, resolver problemas y crear código funcional.<br>**Brechas:** Poca experiencia en desarrollo de software formal, especialmente en el dominio autónomo de Git, arquitectura de microservicios con FastAPI y despliegue contenerizado en Docker. |
