"""
Utilidades compartidas para el procesamiento de la salida de la IA.
"""
import re

def process_ai_code_output(text: str) -> str:
    """
    Limpia el código generado por la IA eliminando los delimitadores de Markdown.

    Esta función busca bloques de código envueltos en ´´´, ```, o ''',
    incluyendo un posible identificador de lenguaje (ej. ´´´python),
    y devuelve solo el contenido del bloque.

    Args:
        text: El texto original generado por la IA.

    Returns:
        El código limpio sin los delimitadores de Markdown, o el texto
        original si no se encuentran delimitadores.
    """
    text = text.strip()
    
    # Patrón para detectar ```python\n...```, ```\n...```, etc.
    # Soporta ´´´, ``` y ''' como delimitadores.
    pattern = r"^(?:```|'''|´´´)(?:[a-zA-Z]*)?\n?(.*?)\n?(?:```|'''|´´´)$"
    
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        # Si se encuentra un bloque, devuelve el contenido limpio.
        return match.group(1).strip()
        
    # Si no hay bloque, devuelve el texto original sin espacios extra.
    return text
