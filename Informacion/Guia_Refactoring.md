# Manual de Usuario: Refactoring Avanzado (v4.0)

Herramientas de edición inteligente de código que entienden la estructura de Python mediante AST y Jedi.

## 🚀 Funcionalidades Implementadas
- [x] **Rename Symbol (`F2`):**
    - Renombrado seguro de variables, funciones y clases.
    - **Preview Dialog:** Muestra un resumen de cambios y un diff antes de aplicar.
- [x] **Extract Method (`Ctrl+Shift+E`):**
    - Extrae el código seleccionado a una nueva función.
    - Detecta automáticamente parámetros necesarios y valores de retorno.
    - Filtra funciones *built-in* (como `print`) de los parámetros.
- [x] **Extract Variable (`Ctrl+Shift+L`):**
    - Extrae una expresión a una variable local.
    - Inserta la definición con la indentación correcta.
- [x] **Move to File (`Ctrl+Shift+M`):**
    - Mueve una clase o función completa a otro archivo `.py`.
    - Elimina el código del origen y lo añade al final del destino.

## 🛠️ Próximos Pasos (Pendiente)
- [ ] **Move to File Avanzado:** Actualizar automáticamente los imports en todo el proyecto al mover un componente.
- [ ] **Extract Constant:** Extraer valores directos a constantes globales.
- [ ] **Inline Variable:** El proceso inverso a la extracción.

## 📖 Instrucciones de Uso
- **Renombrar:** Cursor sobre el nombre -> `F2` -> Escribir nombre -> `Apply`.
- **Extraer Función:** Seleccionar líneas -> `Ctrl+Shift+E` -> Escribir nombre.
- **Extraer Variable:** Seleccionar expresión (ej: `x * y`) -> `Ctrl+Shift+L`.
- **Mover:** Seleccionar bloque completo -> `Ctrl+Shift+M` -> Elegir destino.
