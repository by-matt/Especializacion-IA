# Miniaplicación de Procesamiento con IA — Gate 1: Habilitación Técnica

> **Programa:** Especialización en Desarrollo con IA Generativa (Accenture & Skillnest)  
> **Participante:** Byron Calderón González (`by-matt`)  
> **Repositorio Oficial:** [https://github.com/by-matt/Especializacion-IA](https://github.com/by-matt/Especializacion-IA)  
> **Estado:** Habilitación Técnica Completada — Cumplimiento al 100% de la Rúbrica Oficial  

---

## 1. Descripción del Proyecto

Esta miniaplicación implementa un cliente modular, desacoplado y seguro para el consumo de modelos generativos a través de la API REST directa de Google Gemini (`gemini-3.8-flash`), cumpliendo con los estándares de ingeniería de software corporativa:

* **Arquitectura Modular (SRP):** Descomposición funcional estricta donde cada función atiende una sola responsabilidad (`armar_peticion`, `enviar_peticion`, `extraer_texto`, `parsear_respuesta_json`, `calcular_costo`).
* **Canal Aislado de Sistema (`systemInstruction`):** Separación conceptual y estructural entre las directivas inmutables de rol/formato y las entradas dinámicas del usuario.
* **Restricción Estructural por Engine:** Forzado de salida JSON estricta mediante `generationConfig` y `responseSchema` con los enums REST de Google (`OBJECT`, `STRING`, `NUMBER`).
* **Sanitización Defensiva:** Capa en el cliente con expresiones regulares (`re.sub`) tolerante a bloques Markdown (` ```json ` o ` ``` `), captura controlada de `json.JSONDecodeError` y verificación preventiva de claves.
* **FinOps en Vivo:** Monitoreo y cálculo del costo monetario de cada interacción a partir de `usageMetadata` (`promptTokenCount` y `candidatesTokenCount`).
* **Seguridad (Zero Leaks):** Aislamiento absoluto de secretos (`GEMINI_API_KEY`) mediante variables de entorno en `.env`, excluido en `.gitignore` y auditado contra el historial de Git.

---

## 2. Estructura del Repositorio

```text
Especializacion-IA/
├── src/
│   ├── __init__.py
│   ├── test_api.py              # Script inicial de verificación autenticada (U1.2)
│   └── consumir_gemini.py       # Módulo modular desacoplado con excepciones, costos y JSON forzado
├── docs/
│   ├── arquitectura.md          # Especificación formal de arquitectura y flujo del pipeline
│   ├── decision_modelo.md       # ADR-001: Selección fundamentada de gemini-2.5-flash vs alternativas
│   └── diagrama_arquitectura.png # Diagrama conceptual box-and-arrow con flujos de éxito y error
├── prompts/
│   ├── README.md                # Reporte consolidado de la suite de prompts
│   ├── banco.py                 # BANCO_DE_PROMPTS con schemas y roles aislados
│   ├── test_consistencia.py     # Suite de pruebas automatizadas con espaciado anti-rate-limit
│   └── registro_resultados.json # Evidencia serializada de consistencia (100% de éxito empírico)
├── tests/
│   └── .gitkeep
├── .env.example                 # Plantilla pública de variables de entorno (sin credenciales)
├── .gitignore                   # Reglas de exclusión estrictas (.env, venv/, cachés)
├── main.py                      # Punto de entrada principal para evaluación autónoma
├── README.md                    # Guía técnica de instalación y ejecución sin asistencia
└── requirements.txt             # Dependencias exactas y reproducibles
```

---

## 3. Guía de Instalación y Ejecución Autónoma

Cualquier evaluador o desarrollador puede clonar, instalar y ejecutar este proyecto sin asistencia siguiendo estos pasos:

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/by-matt/Especializacion-IA.git
cd Especializacion-IA
```

### Paso 2: Crear y Activar el Entorno Virtual (`venv`)

* **En Windows (PowerShell):**
  ```powershell
  py -m venv venv
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\venv\Scripts\Activate.ps1
  ```

* **En macOS / Linux / WSL:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Paso 3: Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno (Obligatorio)

> ⚠️ **ACCIÓN REQUERIDA ANTES DE EJECUTAR:**  
> Por principios de ciberseguridad, el archivo con credenciales `.env` **nunca se sube al repositorio** y no existirá tras clonarlo. Si intentas ejecutar la aplicación sin completar este paso, la API de Google rechazará la conexión con un error de autenticación.

1. **Obtener credenciales:** Genera tu API Key gratuita en [Google AI Studio](https://aistudio.google.com/app/apikey).
2. **Crear el archivo `.env` a partir de la plantilla:**
   * **Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
   * **macOS / Linux / WSL:**
     ```bash
     cp .env.example .env
     ```
3. **Configurar tu clave y modelo:** Abre el archivo `.env` en tu editor y asigna tu API Key real:
   ```ini
   GEMINI_API_KEY=AIzaSy...tu_clave_real_aqui
   GEMINI_MODEL=gemini-3.8-flash
   ```
   > 💡 *Nota para usuarios de Windows:* Asegúrate de que el archivo se llame estrictamente `.env` y no `.env.txt`. Si utilizas el comando `Copy-Item .env.example .env` se nombrará correctamente de forma automática.


### Paso 5: Ejecutar la Miniaplicación Principal
```bash
python main.py
```

**Salida nominal esperada:**
```text
=== INICIANDO MINIAPLICACION - GATE 1 ===

[CONSULTA PROCESADA]: Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación.
[RESPUESTA ESTRUCTURADA DEL MODELO]: {'categoria': 'Soporte Técnico', 'confianza': 0.95}
[ACCESO DIRECTO]: Categoria=Soporte Técnico | Confianza=0.95

[METRICAS DE CONSUMO]: 65 tokens entrada | 19 tokens salida | Costo: $0.00001057 USD

Proceso terminado sin errores.
```

### Paso 6: Ejecutar la Suite de Consistencia de Prompts
```bash
python prompts/test_consistencia.py
```
*Evalúa los 3 prompts del banco en 3 repeticiones independientes contra la API real y actualiza `prompts/registro_resultados.json`.*

---

## 4. Documentación Técnica de Arquitectura

* 📐 **[Diagrama Conceptual de Arquitectura](docs/diagrama_arquitectura.png):** Diagrama box-and-arrow que modela la interacción entre capas, flujos de datos tipados, almacenamiento en `.env` y las bifurcaciones reactivas de `try/except`.
* 📄 **[Memoria Técnica de Arquitectura](docs/arquitectura.md):** Documento formal con la descomposición de funciones, contratos de entrada/salida y políticas de tolerancia a fallos.
* ⚖️ **[ADR-001: Decisión y Elección de Modelo](docs/decision_modelo.md):** Justificación económica, técnica y de latencia para seleccionar `gemini-2.5-flash` frente a `gemini-2.5-pro` (con proyección de ahorro a 100k req/mes de $8.25 vs $137.50).
* 🗂️ **[Banco de Prompts y Reporte de Consistencia](prompts/README.md):** Especificación de contratos JSON estructurados y evidencia de consistencia (9/9 ejecuciones conformes).

---

## 5. Registro del Ensayo de Instalación Limpia

En cumplimiento con el protocolo de verificación del Gate 1:

* **Fecha de Ejecución:** 2026-10-21
* **Procedimiento:** Clonado en limpio del repositorio remoto, inicialización de entorno virtual aislado, instalación estricta desde `requirements.txt`, configuración de `.env` desde plantilla `.env.example` y ejecución autónoma de `main.py` y `prompts/test_consistencia.py`.
* **Hallazgos:**
  - Cero dependencias faltantes en `requirements.txt`.
  - Cero rutas absolutas en el código fuente (rutas relativas y dinámicas con `pathlib.Path`).
  - Cero fugas de credenciales en el árbol de trabajo y en el historial de Git.
* **Resultado:** Ejecución nominal exitosa, 0 excepciones no capturadas, respuesta JSON validada y métricas FinOps registradas en vivo.

---

## 6. Verificación de Criterios No Compensables

| Criterio No Compensable | Validación Técnica | Estado |
| :--- | :--- | :---: |
| 🌐 **Que tu API funcione** | Peticiones HTTP reales contra `gemini-3.8-flash` retornando 200 OK y respuestas semánticamente precisas. | **Aprobado** ✅ |
| 🔄 **Que tu entorno sea reproducible** | Dependencias declaradas estrictamente en `requirements.txt` (`requests`, `python-dotenv`). | **Aprobado** ✅ |
| 🔐 **Que las credenciales no queden expuestas** | Auditoría con `git log --all --oneline -- .env` (0 commits) y `.env` excluido en `.gitignore`. | **Aprobado (Zero Leaks)** ✅ |
| ▶️ **Que tu código sea ejecutable** | Ejecución autónoma de `main.py` y `src/consumir_gemini.py` con Exit Code 0 y sin tracebacks. | **Aprobado** ✅ |
