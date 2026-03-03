# Manual de Usuario: Git Integration (v4.0)

NanoEditor incluye un cliente de Git integrado para gestionar versiones de tu código sin salir del editor.

## 🚀 Funcionalidades Implementadas
- [x] **Estado del Repositorio:** Detección automática de repositorios Git al abrir carpetas.
- [x] **Visualización de Rama:** Muestra la rama actual (ej. `⎇ main`) en la cabecera del panel.
- [x] **Indicadores de Cambio:** 
    - `M` (Modified): El archivo ha cambiado.
    - `A` (Added): Archivo nuevo en el índice.
    - `??` (Untracked): Archivo no rastreado.
- [x] **Diff Viewer:** Ver exactamente qué líneas han cambiado con colores (Rojo/Verde) y estadísticas (+ / -).
- [x] **Commit Directo:** Escribir mensaje y realizar commit con `Ctrl+Enter`. Por defecto realiza `git add .` automáticamente.

## 🛠️ Próximos Pasos (Pendiente)
- [ ] **Cuentas y Remotos:** Botones directos para configurar remotos.
- [ ] **Push / Pull Automático:** Botones en la UI para sincronizar con GitHub (Requiere gestión de credenciales).
- [ ] **Gestión de Ramas:** Crear y cambiar ramas desde un menú gráfico.
- [ ] **Conflict Resolver:** Interfaz para resolver conflictos de mezcla.

## 📖 Instrucciones de Uso
1. Abre el panel de **Source Control** (ícono de ramas).
2. Haz clic en un archivo modificado para abrir el **Diff Viewer** y revisar cambios.
3. Escribe un mensaje en la caja de texto.
4. Presiona **Commit** o use `Ctrl+Enter`.
5. Ejecuta `git push` en la terminal para subir los cambios al servidor.
