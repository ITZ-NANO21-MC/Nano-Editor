"AI-powered real-time code completion system."
import threading
import queue
import time
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass
from ai_assistant import AIAssistant
from config import config
from logger import logger


@dataclass
class CompletionSuggestion:
    """Represents a code completion suggestion."""
    text: str
    confidence: float
    type: str  # "function", "variable", "class", "snippet", "line"


class AICompletionEngine:
    """Engine for real-time AI code completion with debouncing and caching."""
    
    def __init__(self):
        self.ai = AIAssistant()
        self.completion_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.debounce_time = 0.3  # 300ms debounce
        self.last_request_time = 0
        self.last_request_id = 0
        self.current_request_id = 0
        self.cache = {}
        self.max_cache_size = 100
        self.is_processing = False
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.process_thread.start()
    
    def request_completion(self, 
                          code: str, 
                          cursor_line: int, 
                          cursor_col: int,
                          file_path: Optional[str] = None,
                          callback: Optional[Callable[[List[CompletionSuggestion]], None]] = None) -> int:
        """Request AI code completion with debouncing."""
        request_id = self.current_request_id + 1
        self.current_request_id = request_id
        
        current_time = time.time()
        
        # Check debounce
        if current_time - self.last_request_time < self.debounce_time:
            logger.debug(f"Completion request {request_id} debounced")
            return request_id
        
        self.last_request_time = current_time
        self.last_request_id = request_id
        
        # Check cache
        cache_key = self._generate_cache_key(code, cursor_line, cursor_col)
        if cache_key in self.cache:
            logger.debug(f"Cache hit for completion request {request_id}")
            if callback:
                self._execute_callback(callback, self.cache[cache_key])
            return request_id
        
        # Add to queue
        self.completion_queue.put({
            'id': request_id,
            'code': code,
            'line': cursor_line,
            'col': cursor_col,
            'file_path': file_path,
            'callback': callback,
            'cache_key': cache_key
        })
        
        logger.debug(f"Completion request {request_id} queued")
        return request_id
    
    def _process_queue(self):
        """Process completion requests from queue."""
        while True:
            try:
                request = self.completion_queue.get(timeout=1)
                
                # Skip if a newer request exists
                if request['id'] < self.last_request_id:
                    logger.debug(f"Skipping outdated request {request['id']}")
                    continue
                
                # Generate completion
                suggestions = self._generate_completion(
                    request['code'],
                    request['line'],
                    request['col'],
                    request['file_path']
                )
                
                # Cache result
                self._add_to_cache(request['cache_key'], suggestions)
                
                # Execute callback if provided
                if request['callback']:
                    self._execute_callback(request['callback'], suggestions)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing completion request: {e}")
    
    def _generate_completion(self, 
                            code: str, 
                            line: int, 
                            col: int,
                            file_path: Optional[str] = None) -> List[CompletionSuggestion]:
        """Generate AI-powered code completions."""
        try:
            # Prepare context for AI
            context = self._prepare_context(code, line, col, file_path)
            
            # Call AI (this would be async in real implementation)
            # For now, we'll use a synchronous call but in a thread
            prompt = self._build_completion_prompt(context)
            
            suggestions = []
            
            # This would be replaced with actual AI call
            # For now, we'll use a placeholder
            ai_response = self._call_ai_completion(prompt)
            
            if ai_response:
                suggestions = self._parse_ai_response(ai_response, context)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return []
    
    def _call_ai_completion(self, prompt: str) -> Optional[str]:
        """Call AI model for completion (placeholder implementation)."""
        # In a real implementation, this would call the AI API
        # For now, we'll simulate with the existing AI assistant
        result = []
        
        # We'll use a simple synchronous call for now
        # In production, this should be async
        def callback(response):
            result.append(response)
        
        self.ai._run_gemini_command(prompt, callback)
        
        # Wait for result (timeout after 2 seconds)
        start_time = time.time()
        while not result and time.time() - start_time < 2:
            time.sleep(0.1)
        
        return result[0] if result else None
    
    def _prepare_context(self, 
                        code: str, 
                        line: int, 
                        col: int,
                        file_path: Optional[str] = None) -> dict:
        """Prepare context for AI completion."""
        lines = code.split('\n')
        
        # Get current line and surrounding context
        start_line = max(0, line - 5)
        end_line = min(len(lines), line + 5)
        
        context_lines = lines[start_line:end_line]
        context_code = '\n'.join(context_lines)
        
        # Get current line up to cursor
        current_line = lines[line - 1] if line - 1 < len(lines) else ""
        prefix = current_line[:col]
        
        return {
            'full_code': code,
            'context_code': context_code,
            'current_line': current_line,
            'prefix': prefix,
            'line': line,
            'col': col,
            'file_path': file_path,
            'language': self._detect_language(file_path) if file_path else 'python'
        }
    
    def _build_completion_prompt(self, context: dict) -> str:
        """Build prompt for AI completion."""
        return f"""Complete the code at line {context['line']}, column {context['col']}.

Current code context:
```{context['language']}
{context['context_code']}
```

The cursor is at line {context['line']}, after: "{context['prefix']}"

Suggest 3-5 possible completions for what comes next. Format as JSON:
{{
  "suggestions": [
    {{
      "text": "completion text",
      "type": "function|variable|class|snippet|line",
      "confidence": 0.95
    }}
  ]
}}

Return ONLY valid JSON, no explanations."""
    
    def _parse_ai_response(self, response: str, context: dict) -> List[CompletionSuggestion]:
        """Parse AI response into completion suggestions."""
        try:
            import json
            data = json.loads(response)
            suggestions = []
            
            for item in data.get('suggestions', []):
                suggestion = CompletionSuggestion(
                    text=item.get('text', ''),
                    confidence=float(item.get('confidence', 0.5)),
                    type=item.get('type', 'snippet')
                )
                suggestions.append(suggestion)
            
            return suggestions
            
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, try to extract completions from plain text
            return self._extract_completions_from_text(response, context)
    
    def _extract_completions_from_text(self, text: str, context: dict) -> List[CompletionSuggestion]:
        """Extract completion suggestions from plain text response."""
        suggestions = []
        lines = text.strip().split('\n')
        
        for line in lines[:5]:  # Take first 5 lines as suggestions
            line = line.strip()
            if line and len(line) > 1:
                suggestion = CompletionSuggestion(
                    text=line,
                    confidence=0.7,
                    type=self._guess_suggestion_type(line, context)
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _guess_suggestion_type(self, text: str, context: dict) -> str:
        """Guess the type of suggestion based on text."""
        text_lower = text.lower()
        
        if text_lower.startswith('def ') or text_lower.startswith('async def '):
            return 'function'
        elif text_lower.startswith('class '):
            return 'class'
        elif '(' in text and ')' in text:
            return 'function'
        elif any(keyword in text for keyword in ['import', 'from', 'return', 'if', 'for', 'while']):
            return 'line'
        elif len(text.split()) <= 3:
            return 'variable'
        else:
            return 'snippet'
    
    def _generate_cache_key(self, code: str, line: int, col: int) -> str:
        """Generate cache key for completion request."""
        # Create a hash based on code context around cursor
        lines = code.split('\n')
        start = max(0, line - 3)
        end = min(len(lines), line + 1)
        context = '\n'.join(lines[start:end])
        
        import hashlib
        key_data = f"{context}:{line}:{col}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _add_to_cache(self, key: str, suggestions: List[CompletionSuggestion]):
        """Add result to cache."""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = suggestions
    
    def _execute_callback(self, callback: Callable, suggestions: List[CompletionSuggestion]):
        """Execute callback in main thread."""
        # This should be called from main thread using after() in tkinter
        # For now, we'll execute directly (should be adapted for tkinter)
        try:
            callback(suggestions)
        except Exception as e:
            logger.error(f"Error executing completion callback: {e}")
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
        }
        
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'python')


# Global completion engine instance
completion_engine = AICompletionEngine()
