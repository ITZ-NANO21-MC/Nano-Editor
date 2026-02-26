# 🧪 Guía de Testing - NanoEditor v4.0

## ✅ Estado Actual de la Suite
A partir de la Versión 4.0, NanoEditor cuenta con una suite de pruebas profesional dividida por módulos, garantizando que el desacoplamiento y la funcionalidad se mantengan íntegros durante el desarrollo.

**Métricas Finales:**
- **Total de tests:** 76
- **Estado:** 100% PASSED ✅
- **Cobertura estimada:** 85% del núcleo del sistema.

---

## 🏗️ Distribución de Tests por Módulo

### 1. Core Editor (`tests/test_core.py`) ✅ 11/11 tests
- Validación de importaciones de `editor_view`, `text_area`, `tab_manager`.
- Pruebas de instanciación de clases críticas.
- Verificación de la limpieza de dependencias circulares.

### 2. AI & Agente (`tests/test_ai.py`) ✅ 22/22 tests
- Registro de herramientas del Agente.
- Sistema de seguridad (Safe Mode, Paranoid, Autonomous).
- Instanciación de `AIClient`, `AIAssistant` y `AIAgent`.
- Verificación de prompts no vacíos.

### 3. UI & Paneles (`tests/test_ui.py`) ✅ 15/15 tests
- Importación de los 14 paneles y ventanas.
- Verificación de widgets dinámicos (GeminiPanel, AgentPanel, FileTree).
- Persistencia de estados Visuales.

### 4. Navegación (`tests/test_navigation.py`) ✅ 7/7 tests
- Resolución de `GotoDefinition` via Jedi (Mocks).
- Generación de `ProjectContext` dinámico.
- Búsqueda global en proyecto.

### 5. Terminal (`tests/test_terminal.py`) ✅ 6/6 tests
- Ciclo de vida de `TerminalProcess` (Inicio/Kill).
- Importación del panel GUI.

### 6. IA Client & Utils (`tests/test_gemini_client.py`, `tests/test_utils.py`) ✅ 15/15 tests
- Mocks para LiteLLM/Streaming.
- Detección de lenguajes y manipulación de rutas.

---

## 🚀 Cómo Ejecutar los Tests

### Suite Completa (Recomendado)
```bash
source env/bin/activate
cd Nano-Editor
python -m pytest tests/ -v --tb=short
```

### Por Módulo Individual (Depuración)
```bash
# Solo IA
python -m pytest tests/test_ai.py -v

# Solo Core
python -m pytest tests/test_core.py -v
```

---

## 🛠️ Herramientas Utilizadas
- **Pytest:** Motor de ejecución principal.
- **Unittest.mock:** Para simular llamadas a APIs externas (Gemini/LiteLLM) y evitar costos/latencia.
- **Customtkinter Mocks:** Para testear la lógica de la UI sin necesidad de abrir ventanas físicas durante los tests automáticos.

---

## 🎯 Plan de Testing Futuro
1. **Tests de Integración E2E:** Simulación de flujo completo de usuario con el Agente IA.
2. **Performance Benchmarks:** Scripts para medir el tiempo de respuesta del `AsyncHighlighter`.
3. **CI/CD:** Integración con GitHub Actions para ejecución automática en cada Push.

---
**Actualizado:** Febrero 2026
**Responsable:** Nano-Agent AI
