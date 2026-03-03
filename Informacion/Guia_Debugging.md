# Manual de Usuario: Debugging Integrado (v4.0)

Este módulo permite depurar código Python directamente desde NanoEditor utilizando `pdb` en segundo plano.

## 🚀 Funcionalidades Implementadas
- [x] **Gestión de Breakpoints:** Haz clic en el margen de los números de línea para poner/quitar puntos de parada.
- [x] **Panel de Control:** Sección dedicada en la barra lateral para ver la lista de breakpoints y controles de flujo.
- [x] **Inyectar Breakpoints Dinámicos:** Los puntos se cargan automáticamente al iniciar la depuración.
- [x] **Controles de Paso (Stepping):**
    - `Continue`: Seguir hasta el siguiente punto.
    - `Step Over`: Saltar a la siguiente línea.
    - `Step Into`: Entrar en funciones.
    - `Stop`: Detener la ejecución.
- [x] **Salida de Debug:** Consola dedicada en la parte inferior del panel para ver mensajes de `pdb` y variables.
- [x] **Auto-Guardado:** El editor guarda los cambios antes de lanzar el debugger.

## 🛠️ Próximos Pasos (Pendiente)
- [ ] **Inspección de Variables (TreeView):** Ver variables locales/globales en una lista estructurada.
- [ ] **Call Stack Viewer:** Ver la pila de llamadas de funciones.
- [ ] **Soporte para otros lenguajes:** Integrar Node.js o GDB.

## 📖 Instrucciones de Uso
1. Abre un archivo `.py`.
2. Haz clic a la izquierda de los números de línea para poner un punto rojo `⬤`.
3. Ve al panel de **Run and Debug** (ícono del bicho 🐛).
4. Presiona **🐛 Debug Current File**.
5. Usa los botones de control para avanzar por el código.
6. Revisa el **DEBUG OUTPUT** para los resultados.
