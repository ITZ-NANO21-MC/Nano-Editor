# Tests - NanoEditor

## 📋 Test Suite

Tests básicos para NanoEditor v3.0.

## 🧪 Tests Incluidos

### test_config.py
- Carga de configuración
- Valores por defecto
- Conversión de tipos (int, bool)

### test_tab_manager.py
- Creación de tabs
- Títulos de tabs
- Estado modificado
- Manejo de archivos

### test_utils.py
- Detección de lenguaje por extensión
- Operaciones de path
- Basename, dirname, splitext

### test_gemini_client.py
- Inicialización del cliente
- Métodos disponibles

## 🚀 Ejecutar Tests

### Opción 1: Script
```bash
./run_tests.sh
```

### Opción 2: Python unittest
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### Opción 3: Pytest (si está instalado)
```bash
pytest tests/ -v
```

### Opción 4: Test individual
```bash
python3 tests/test_config.py
python3 tests/test_tab_manager.py
python3 tests/test_utils.py
python3 tests/test_gemini_client.py
```

## 📊 Cobertura Actual

- **config.py**: ✅ Básico
- **tab_manager.py**: ✅ EditorTab
- **Utilidades**: ✅ Path operations
- **gemini_client.py**: ✅ Inicialización

## 🎯 Próximos Tests

- [ ] Tests de integración para GUI
- [ ] Tests para AI operations
- [ ] Tests para file operations
- [ ] Tests para terminal
- [ ] Tests para syntax highlighter
- [ ] Mocks para API de Gemini

## 📝 Notas

- Tests actuales son unitarios básicos
- No requieren GUI (headless)
- No requieren API key de Gemini
- Ejecutan rápido (<1s)

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
