# Tests - NanoEditor v3.2

## 📋 Test Suite

Tests unitarios y de integración básica para NanoEditor v3.2.

## 🧪 Tests Incluidos

### test_config.py
- Carga de configuración desde `.env`.
- Validación de valores por defecto.
- Conversión robusta de tipos (int, bool).

### test_tab_manager.py
- Lógica de la clase `EditorTab`.
- Gestión de rutas de archivos y estados de modificación.
- Generación dinámica de títulos de pestañas.

### test_utils.py
- Detección de lenguaje por extensión.
- Operaciones seguras de rutas (`os.path`).

### test_gemini_client.py
- **Streaming de IA**: Verificación de la recepción de fragmentos en tiempo real.
- **Mocks de API**: Simulación completa de la librería `google-generativeai` para tests rápidos y sin coste.
- **Manejo de Errores**: Pruebas de fallos de API, errores de conexión y ausencia de API Key.

## 🚀 Ejecutar Tests

### Opción 1: Script (Recomendado)
```bash
./run_tests.sh
```

### Opción 2: Cobertura (Detailed Report)
```bash
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report
```

## 📊 Cobertura Actual

- **TOTAL**: 📈 **39%** (Aumento desde 34%)
- **config.py**: ✅ 82%
- **event_bus.py**: ✅ 61%
- **gemini_client.py**: 🔵 56% (Aumento significativo con mocks)
- **tab_manager.py**: 🟡 21% (Lógica de datos cubierta)

## 🎯 Próximos Tests

- [ ] Tests de integración para la interfaz de usuario (GUI)
- [ ] Tests para operaciones de archivos con IA (`ai_file_operations.py`)
- [ ] Tests para el terminal integrado
- [ ] Tests para el resaltado de sintaxis asíncrono
- [x] Mocks para API de Gemini

## 📝 Notas de Robustez

- **Aislamiento de UI**: Los módulos principales (`tab_manager.py`, `text_area.py`) han sido modificados para permitir su importación en entornos de test sin necesidad de tener instalada la librería `customtkinter`.
- **Ejecución Headless**: No se requiere ventana gráfica ni API Key real para pasar los tests.
- **Velocidad**: La suite completa se ejecuta en <1.5s.

## 🔧 Agregar Nuevos Tests

1. Crear archivo `test_nombre.py` en `tests/`
2. Importar unittest
3. Crear clase que herede de `unittest.TestCase`
4. Agregar métodos que empiecen con `test_`
5. Ejecutar con `./run_tests.sh`

Ejemplo:
```python
import unittest

class TestMiModulo(unittest.TestCase):
    def test_algo(self):
        self.assertEqual(1 + 1, 2)

if __name__ == "__main__":
    unittest.main()
```
