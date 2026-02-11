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
    
    # Patrón para detectar bloques de código markdown ```...```, '''...''', ´´´...´´´
    # Busca el primer bloque de código válido, ignorando el texto anterior o posterior.
    pattern = r"(?:```|'''|´´´)(?:[a-zA-Z0-9+\-]*)?\n?(.*?)\n?(?:```|'''|´´´)"
    
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        # Si se encuentra un bloque, devuelve el contenido limpio.
        return match.group(1).strip()
        
    # Fallback: Si no hay bloques de código explícitos, intenta limpiar comillas simples si envuelven todo el texto
    # Esto maneja casos donde la IA devuelve 'code' en lugar de ```code```
    if len(text) > 2 and ((text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')) or (text.startswith("´") and text.endswith("´"))):
         return text[1:-1].strip()

    # Si no hay bloque, devuelve el texto original
    return text


def strip_markdown_formatting(text: str) -> str:
    """
    Strips inline Markdown formatting from AI output text.
    
    Removes: **bold**, *italic*, `inline code`, ### headers, --- separators.
    Preserves the actual text content inside the formatting.
    
    Args:
        text: The AI-generated text potentially containing Markdown formatting.
    
    Returns:
        Clean plain text without Markdown formatting characters.
    """
    # Remove markdown code blocks (```...```) and keep content
    text = re.sub(r'```[a-zA-Z]*\n?', '', text)
    
    # Remove bold: **text** -> text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Remove italic: *text* -> text (but not bullet points)
    text = re.sub(r'(?<!\n)(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
    
    # Remove inline code backticks: `text` -> text
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove markdown headers: ### Header -> Header
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules: --- or ***
    text = re.sub(r'^[-*]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def clean_ai_json_response(text: str) -> str:
    """
    Cleans AI response to extract valid JSON content, stripping markdown code blocks.
    
    Args:
        text (str): Raw response text from AI.
        
    Returns:
        str: Cleaned JSON string ready for parsing.
    """
    text = text.strip()
    
    # Simple regex to find the first JSON-like structure if wrapped in code blocks
    # This handles ```json ... ``` or just ``` ... ```
    pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
        
    return text

