# Límites de la Métrica de Evaluación

> **Autor:** Byron Calderón González (`by-matt`)  
> **Módulo:** Módulo 2 - Construcción de componentes IA  
> **Unidad:** U2.2 Pipeline de texto, NLP básico y evaluación inicial (Bloque 17 - Actividad Core)  
> **Fecha de Elaboración:** 02 de noviembre de 2026  

---

## 1. Qué Mide

Esta métrica evalúa la coincidencia léxica exacta (bolsa de palabras) entre una respuesta generada por el modelo y un texto de referencia predefinido, calculando la intersección de tokens con repeticiones (`Counter`) para obtener **precisión**, **cobertura (recall)** y la media armónica **F1-score**.

---

## 2. Modos de Falla Conocidos

A partir de la revisión manual de mis evaluaciones, documenté los siguientes modos de falla estructurales donde el número por sí solo resulta engañoso:

* **Penalización por sinónimos y paráfrasis válidas (Falsos Negativos):**  
  La métrica compara tokens literales, por lo que una respuesta conceptualmente perfecta puede recibir una puntuación baja si el modelo elige vocabulario alternativo.  
  * **Ejemplo observado:** En la consulta *`"¿Qué hace la sentencia break en un bucle?"`*, la respuesta generada utilizó *"interrumpe y sale del bucle"* en lugar de *"termina inmediatamente la ejecución"*. Aunque el significado técnico es idéntico y correcto, el F1 cayó a **0.3158**, clasificándola erróneamente como una respuesta deficiente.
  * **Ejemplo técnico:** En *`"¿Para qué sirve la función len en Python?"`*, la respuesta empleó *"número total de elementos"* en lugar de *"cantidad de elementos"*, reduciendo el F1 a **0.3448** pese a tener corrección factual y completitud totales.

* **Tolerancia a datos factuales erróneos (Riesgo de Falsos Positivos):**  
  Como cada palabra tiene el mismo peso numérico, equivocarse en una cifra, fecha o nombre propio apenas afecta la métrica si el resto de la frase coincide con la referencia.  
  * **Ejemplo observado:** En la consulta *`"¿Cuándo se creó Python?"`*, la respuesta obtuvo un F1 alto de **0.8182** porque casi todas las palabras coincidieron, a pesar de que introdujo una discrepancia cronológica al mencionar el inicio de desarrollo en 1989 junto al lanzamiento de 1991. En sistemas donde la exactitud del dato es crítica, un F1 superior a 0.80 puede generar una falsa sensación de seguridad.

* **Inversión semántica por negación ausente o agregada:**  
  Omitir una palabra de negación (*"no"*, *"nunca"*) cambia radicalmente el significado de una respuesta técnica (por ejemplo, afirmar *"Python es un lenguaje compilado"* frente a *"Python no es un lenguaje compilado"*), pero la métrica solo castiga una única palabra faltante, arrojando un F1 cercano a **0.91** para una afirmación fácticamente opuesta.

* **Falta de consideración del orden de las palabras:**  
  La representación bolsa de palabras ignora la sintaxis y la jerarquía gramatical. Dos frases con los mismos términos en orden invertido obtendrán un F1 de **1.0**, sin reflejar si el significado fue alterado.

---

## 3. Muestra Revisada

Para auditar el comportamiento real del pipeline, evalué un conjunto de **20 consultas técnicas** almacenadas en [`resultados_metricas.json`](../resultados_metricas.json) y seleccioné una muestra estratificada de **10 casos** para inspección cualitativa detallada (registrados en [`revision_manual.json`](../revision_manual.json)):

* **Criterio de selección:** Los 5 casos con menor F1 (rango **0.3158 a 0.3636**) para identificar falsos negativos, y los 5 casos con mayor F1 (rango **0.5600 a 0.8696**) para validar consistencia y descartar falsos positivos.
* **Rúbrica aplicada a cada caso:**
  1. *Corrección factual:* ¿Todo dato verificable es correcto? (Sí / No / Parcialmente).
  2. *Completitud:* ¿Cubre los conceptos clave de la referencia? (Sí / No / Parcialmente).
  3. *Contradicción:* ¿Afirma algo opuesto a la referencia? (Sí / No).
  4. *Nota técnica:* Justificación cualitativa del desfase entre el número y la calidad real.

---

## 4. Recomendación de Uso

* **Cuándo confiar en la métrica automática (F1):**  
  Recomiendo utilizar el F1-score como indicador de primer orden para comparar lotes masivos de respuestas (decenas o cientos de consultas), detectar regresiones evidentes entre versiones de prompts o cambios de modelo, y ordenar las salidas para priorizar la revisión humana empezando por los casos con menor puntaje.

* **Cuándo realizar revisión manual obligatoria:**  
  No se debe delegar la decisión final únicamente en la métrica cuando las respuestas involucren:
  1. **Fechas, cifras numéricas, identificadores o comandos de configuración.**
  2. **Respuestas con F1 bajo (inferior a 0.40)** que ameritan validar si se trata de un falso negativo por paráfrasis antes de descartarlas.
  3. **Respuestas con F1 casi perfecto (superior a 0.90)** en preguntas donde una negación o inversión de palabras pueda haber alterado el sentido de negocio.
