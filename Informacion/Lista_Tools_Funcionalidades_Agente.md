# 🛠️ Catálogo de Tools y Funcionalidades para Paridad Agéntica

Para que Nano-Editor funcione como un agente autónomo (estilo Antigravity), se deben implementar las siguientes capas tecnológicas, herramientas y cambios en la interfaz.

---

## 1. Capa de Herramientas (The Toolbelt)
Estas son las funciones que el LLM podrá invocar mediante JSON. Cada una requiere un "Handler" en el backend de Nano-Editor.

### 📂 Gestión de Archivos y Sistema
*   **`view_file(path, start_line, end_line)`**: Permite a la IA leer fragmentos específicos de código.
*   **`list_dir(path)`**: Explorar la estructura de carpetas.
*   **`write_to_file(path, content)`**: Crear archivos nuevos con código generado.
*   **`replace_file_content(path, target_text, replacement_text)`**: Realizar ediciones precisas en archivos existentes sin reescribirlos enteros.
*   **`find_by_name(pattern)`**: Buscar archivos por nombre en todo el workspace.
*   **`grep_search(query)`**: Buscar texto dentro de los archivos (usando el `ripgrep` propuesto en la estrategia de optimización).

### 🖥️ Ejecución y Control
*   **`run_command(command)`**: Ejecutar comandos en la terminal integrada (ej. `pytest`, `npm start`, `python script.py`).
*   **`command_status(command_id)`**: Consultar si un comando de larga duración ya terminó y ver su salida.
*   **`send_command_input(command_id, input)`**: Interactuar con procesos que piden datos (como el `input()` de Python).

### 🌐 Investigación y Visión
*   **`search_web(query)`**: Buscar soluciones en Google/StackOverflow/Docs.
*   **`read_url_content(url)`**: Leer la documentación de una página web para aprender a usar una librería.
*   **`browser_action(action_type, params)`**: (Avanzado) Abrir un navegador (Playwright) para probar la UI que se está desarrollando.

---

## 2. Funcionalidades de Orquestación (The Brain)
No son herramientas aisladas, sino cambios en cómo la IA procesa la información.

*   **Bucle de Pensamiento (CoT - Chain of Thought)**: La IA debe generar una sección de "Pensamiento" antes de cada acción para razonar el *porqué* de lo que va a hacer.
*   **Gestión de Tareas Complejas**: Capacidad de dividir un requerimiento de usuario ("Crea un Dashboard") en sub-tareas (Crear modelo, crear vista, añadir estilos, testear).
*   **Memoria de Sesión de Tarea**: Un archivo de estado (ej. `task.md`) donde el agente anota qué ha hecho y qué falta por hacer.

---

## 3. Cambios en la Interfaz de Usuario (The UI/UX)
Para que el usuario pueda supervisar al agente sin sentirse abrumado.

*   **Panel de Progreso Agéntico**: Una vista lateral que muestre en qué paso está la IA (ej. "🔍 Investigando archivos", "✍️ Escribiendo login.py", "🧪 Ejecutando tests").
*   **Sistema de Aprobación de Comandos**: Cuando la IA quiera ejecutar un comando en la terminal o escribir un archivo, debe aparecer un prompt visual:
    *   `[ Aprobar ]` `[ Editar ]` `[ Rechazar ]`
*   **Visor de Artefactos**: Pestañas especiales para ver documentos de planificación (`implementation_plan.md`) o reportes de progreso generados por la IA.
*   **Notificaciones de Salida**: Un sistema para que la IA "toque el hombro" al usuario mediante la tool `notify_user` cuando necesite una decisión humana.

---

## 4. Contexto Pasivo (The Eyes)
Información que se envía en **cada** prompt sin que el usuario la escriba:
*   Proyecto abierto actual.
*   Archivos actualmente visibles en las pestañas.
*   Posición exacta del cursor.
*   Errores recientes en la terminal o logs de Python.

---

### 📝 Resumen de Implementación
Para lograr esto, Nano-Editor debe evolucionar su `AIProvider` actual para que no solo devuelva texto, sino que sea un **Runtime de Funciones**. Es decir, que sepa parsear las etiquetas de herramientas de la IA y ejecutarlas de forma segura en el sistema operativo del usuario.
