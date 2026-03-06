# Manual de Usuario: Editor Core & Performance (v4.0)

El motor principal de NanoEditor, optimizado para ser extremadamente rápido y ligero.

## 🚀 Funcionalidades Implementadas
- [x] **Syntax Highlighting Asíncrono:** El resaltado de colores no bloquea la escritura, incluso en archivos grandes.
- [x] **Token Merging:** Optimización de renderizado que reduce el uso de memoria fusionando tokens consecutivos del mismo tipo.
- [x] **Debouncing:** El resaltado se activa de forma inteligente para ahorrar CPU.
- [x] **Gestión de Pestañas:** Interfaz multizona para trabajar con varios archivos a la vez.

## 🛠️ Próximos Pasos (Pendiente)
- [ ] **Soporte de Archivos Grandes:** Carga incremental o virtualización del buffer para archivos >10MB.
- [ ] **Minimapa:** Vista en miniatura del código en el lateral.
- [ ] **Multi-cursor:** Edición en múltiples líneas simultáneamente.
- [ ] **Búsqueda Global:** Buscar texto en todo el proyecto de forma instantánea.

## 📖 Instrucciones de Uso
- **Abrir Archivo:** Usa el explorador de archivos a la izquierda.
- **Guardar:** `Ctrl+S`.
- **Cerrar Pestaña:** Clic en la `x` de la pestaña o botón central del ratón.
- **Scroll:** Usa la rueda del ratón o la barra lateral.
