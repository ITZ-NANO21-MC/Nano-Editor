# 🛠️ Fase de Consolidación: Camino a NanoEditor v4.0

Esta fase tiene como objetivo optimizar la deuda técnica acumulada y preparar la arquitectura del editor para la escalabilidad profesional de la versión 4.0. Aplicamos el principio de Pareto (20/80) para enfocarnos en los componentes que generan más impacto con el menor riesgo.

---

## 📅 Resumen de la Estrategia

El plan se divide en **3 Fases de Refactorización**, cada una diseñada para ser aplicada de forma independiente para evitar regresiones.

---

## 🔵 Fase 1: Optimización de Rendimiento y Lógica (CRÍTICO)
*Enfoque: Eliminar latencias y mejorar la eficiencia del motor de IA.*

### Parte 1.1: Refactorización de `ai_completion.py`
- [x] **Eliminar Espera Activa**: Sustituir el bucle `while/sleep` en el hilo de autocompletado por una llamada bloqueante directa al cliente de IA.
- [x] **Simplificación de Hilos**: Evitar la creación de hilos duplicados por cada solicitud de autocompletado.
- [x] **Optimización de Caché**: Mejorar la estructura de la caché de autocompletado para búsquedas más rápidas.

### Parte 1.2: Consolidación de `AIAssistant`
- [x] **Uniformidad de Métodos**: Asegurar que todos los métodos de `AIAssistant` usen el nuevo `AIClient` de forma estandarizada.
- [x] **Manejo de Errores**: Robustecer el manejo de excepciones en las llamadas asíncronas de IA.
PI para evitar bloqueos en la UI.

---

## 🟢 Fase 2: Desacoplamiento y Arquitectura (CRÍTICO)
*Enfoque: Romper el "God Object" y estandarizar la comunicación.*

### Parte 2.1: Modularización de `App` (`editor_view_v3.py`)
- [x] **Extracción de Handlers**: Mover la lógica de ventanas emergentes y atajos de teclado a archivos específicos.
- [x] **Limpia de Inicialización**: Reducir el tamaño de `__init__` delegando la configuración de componentes a fábricas o métodos especializados.

### Parte 2.2: Implementación de Eventos Estándar
- [ ] **Migración a `EventBus`**: Cambiar llamadas directas entre componentes (ej. FileHandler -> FileTree) por eventos de publicación/suscripción.
- [ ] **Events Catalog**: Ampliar la clase `Events` en `event_bus.py` para cubrir todas las interacciones comunes.

---

## 🟡 Fase 3: Limpieza de Componentes UI (ADVERTENCIA)
*Enfoque: Estabilidad visual y organización de la base de código.*

### Parte 3.1: Reorganización de `terminal_panel.py`
- [ ] **Separación Backend/Frontend**: Aislar la gestión del proceso PTY/Shell de la lógica de renderizado en el widget de texto.
- [ ] **Gestión de Streams**: Optimizar la forma en que el terminal lee la salida para evitar "saltos" en archivos de log grandes.

### Parte 3.2: Modularización de `text_area.py`
- [ ] **Extraer GhostText**: Mover la lógica de visualización del texto fantasma a su propio módulo para simplificar el widget de código principal.
- [ ] **Optimización de Highlighting**: Refinar el debouncing del resaltado asíncrono.

---

## 🚦 Indicadores de Éxito
- **Rendimiento**: Reducción del uso de CPU en reposo (menys hilos activos).
- **Mantenibilidad**: Archivos principales reducidos en un 30% en líneas de código.
- **Preparación v4**: El sistema de plugins debe poder suscribirse a eventos sin modificar el core del editor.

---
**Ultima actualización:** 2026-01-27
**Estado:** Pendiente de Inicio de Ejecución
