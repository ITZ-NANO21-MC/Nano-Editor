# 🚀 Estrategia de Optimización Futura: Híbrida y Pragmática

Este documento describe la estrategia técnica para optimizar NanoEditor una vez completada la **Fase de Consolidación v3.7**. El objetivo es alcanzar rendimiento nativo en operaciones pesadas sin sacrificar la flexibilidad de Python.

---

## 📅 Momento de Ejecución
Esta estrategia se evaluará e implementará **después** de finalizar la estabilización de la arquitectura actual (Fase de Consolidación). No se deben reescribir componentes críticos mientras se está refactorizando la base.

---

## 🧠 Filosofía: "Delegar, no Reescribir"
Evitaremos reescribir la lógica de negocio (UI, Eventos, Coordinación) en lenguajes de bajo nivel. En su lugar, utilizaremos binarios de alto rendimiento y bindings para tareas específicas de uso intensivo de CPU/IO.

---

## 🎯 Componentes Candidatos a Optimización

### 1. Búsqueda Global y en Archivos (IO Bound)
*   **Problema Actual**: Python usa `os.walk` y `open()` secuencial, lo cual es lento para proyectos con miles de archivos (`node_modules`, etc.).
*   **Solución Propuesta**: Integrar **`ripgrep` (rg)**.
    *   Ejecutar el binario `rg` mediante `subprocess`.
    *   Parsear la salida estándar.
    *   **Beneficio estimado**: 10x-100x más rápido en búsquedas de texto.

### 2. Resaltado de Sintaxis (CPU Bound)
*   **Problema Actual**: `Pygments` (Python puro) tokeniza el texto usando expresiones regulares en el hilo principal (o secundario). Archivos >1MB causan lag perceptible.
*   **Solución Propuesta**: Evaluar **Tree-sitter** (Binding de Python a C).
    *   Genera un AST incremental.
    *   Mucho más rápido y preciso que RegExp.
    *   **Beneficio estimado**: Resaltado instantáneo y características de IDE (folding, selección inteligente).

### 3. Autocompletado y Análisis (CPU Bound)
*   **Problema Actual**: `Jedi` es excelente pero puede ser lento en arrancar o analizar librerías gigantes.
*   **Solución Propuesta**: Servidor LSP (Language Server Protocol) nativo.
    *   Conectarse a servidores LSP escritos en Rust/Go (ej. `ruff`, `pyright`).
    *   **Beneficio estimado**: Diagnósticos en tiempo real con rendimiento industrial.

---

## ⚠️ Riesgos y Consideraciones
1.  **Complejidad de Distribución**: Al depender de binarios externos (`rg`), la instalación se vuelve más compleja (hay que empaquetar los ejecutables para Windows/Linux/Mac).
2.  **Curva de Aprendizaje**: Integrar Tree-sitter o LSP requiere cambiar drásticamente la lógica de manejo de texto actual.

---

## ✅ Próximos Pasos (Post-Consolidación)
1.  Realizar **Profiling** real para confirmar que estos son los verdaderos cuellos de botella.
2.  Crear prototipos aislados (POCs) de la integración con `ripgrep`.
