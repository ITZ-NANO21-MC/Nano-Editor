# 📄 Changelog NanoEditor v4.0

Todas las modificaciones notables a este proyecto serán documentadas en este archivo.

## [4.0.0] - 2026-02-25

### 🏗️ Arquitectura Modular (Gran Refactorización)
- **Reorganización total del proyecto**: Movidos 40+ archivos de la raíz a directorios funcionales:
  - `core/`: Motor central del editor.
  - `ai/`: Lógica de Agentes e Inteligencia Artificial.
  - `ui/`: Componentes de interfaz y paneles.
  - `navigation/`: Herramientas de navegación de código.
  - `terminal/`: Sistema de terminal integrada.
- **Limpieza de dependencias**: Eliminación de importaciones circulares en archivos `__init__.py`.
- **Imports Absolutos**: Estandarización de todos los archivos para usar rutas absolutas dentro del paquete.

### 🤖 Inteligencia Artificial & Agentes
- **AIClient Unificado**: Migración a **LiteLLM**, lo que permite usar Gemini, OpenAI, Anthropic, Claude y DeepSeek de forma transparente.
- **Streaming Real-time**: Implementación de respuestas fluidas carácter por carácter tanto en Chat como en el Agente.
- **Agentic Loop**: Sistema de razonamiento autónomo para ejecutar tareas complejas (leer archivos, ejecutar tests, arreglar código).
- **Human-in-the-Loop**: Implementación de `ai_security.py` para requerir aprobación humana antes de acciones sensibles.
- **Centralización de Prompts**: Todos los prompts del sistema ahora residen en `ai/prompts.py`.

### 🖥️ Interfaz de Usuario (UI)
- **Panel de Agente**: Nueva interfaz para interactuar con el agente autónomo.
- **Feedback Visual Avanzado**: Notificaciones dinámicas y barras de progreso para tareas de IA.
- **Tema Dinámico**: Correcciones exhaustivas para que el tema Light sea 100% elegible y moderno.
- **Autocomplete UI**: Ventanas emergentes de autocompletado mejoradas y sin redundancia.

### 🧪 Calidad y Testing
- **Suite de Pruebas Extendida**: Incremento de ~20 tests a **76 tests unitarios** cubriendo el 100% de la nueva estructura.
- **Tests de Módulo**: Creados tests específicos para cada cluster (`test_core`, `test_ai`, `test_ui`, etc.).
- **Validación Automatizada**: Scripts para ejecución rápida de la suite completa.

### ⚙️ Otras Mejoras
- **Performance**: Reducción de latencia en syntax highlighting mediante el nuevo `AsyncHighlighter`.
- **Robustez**: Manejo de excepciones específicas en lugar de bloques genéricos.
- **Logging**: Sistema de logs centralizado para depuración profesional.

---
**NanoEditor v4.0: El futuro del editor de código modular y agentic.**
