"""
Autonomous AI Engine - Self-coding and self-executing AI system
"""
import re
import sys
import os
from typing import Dict, Any, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import ErrorHandler, safe_operation
from assistant.feedback_processor import FeedbackProcessor

class AutonomousEngine:
    """AI engine that can write and execute code autonomously"""
    
    def __init__(self, ai_core, context_info: Dict[str, Any] = None):
        self.ai_core = ai_core
        self.error_handler = ErrorHandler("autonomous_engine")
        self.context_info = context_info or {}
        self.execution_globals = self._setup_execution_environment()
        self.feedback_processor = FeedbackProcessor()
    
    def _setup_execution_environment(self) -> Dict[str, Any]:
        """Setup safe execution environment for AI-generated code"""
        safe_builtins = {
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
        }
        
        # Safe modules
        import os
        import json
        import datetime
        import pathlib
        from pathlib import Path
        
        safe_modules = {
            'os': os,
            'json': json,
            'datetime': datetime,
            'pathlib': pathlib,
            'Path': Path,
        }
        
        return {**safe_builtins, **safe_modules}
    
    @safe_operation("autonomous action")
    def execute_autonomous_action(self, user_input: str) -> str:
        """Main autonomous action executor"""
        
        # Build enhanced prompt for autonomous AI
        prompt = self._build_autonomous_prompt(user_input)
        
        # Get AI response
        ai_response = self.ai_core.chat(prompt)
        
        # Extract and execute any Python code
        execution_results = self._extract_and_execute_code(ai_response)
        
        # Append execution results to response if any
        if execution_results:
            ai_response += f"\\n\\n🔧 Execution Results:\\n{execution_results}"
        
        return ai_response
    
    def _build_autonomous_prompt(self, user_input: str) -> str:
        """Build intelligent prompt based on request type and user preferences"""
        
        working_dir = self.context_info.get('working_directory', os.getcwd())
        last_file = self.context_info.get('last_file_path', 'None')
        
        # Analyze request type
        request_type = self._analyze_request_type(user_input)
        
        # Build context-aware prompt based on request type
        if request_type == 'simple_question':
            return f"""User question: "{user_input}"
            
You are a helpful AI assistant. Provide a DIRECT, CONCISE answer.

IMPORTANT:
- For yes/no questions → answer "Có" or "Không" first, then brief explanation
- For "where is" questions → answer location directly
- For "what time" → show time immediately
- Keep responses under 2 sentences unless more detail is explicitly requested

Context: Working directory: {working_dir}

Provide helpful, direct answer in Vietnamese."""
        
        elif request_type == 'file_search':
            return f"""User wants to search: "{user_input}"

You are an AI assistant that can write and execute Python code.

Task: Write WORKING Python code to search for the requested item.

IMPORTANT:
- Fix all syntax errors (properly escape backslashes in paths)
- Use correct string formatting
- Test code mentally before providing
- Provide direct answer first, then show code if needed

Context: {working_dir}

Format:
```python
# Working Python code here
```

Then brief explanation of results."""
        
        else:  # action_required
            return f"""User request: "{user_input}"

You are an AI that writes and executes Python code to perform tasks.

IMPORTANT RULES:
1. File operations → Write working Python code and execute
2. System info → Write Python code to get actual system data
3. Always test code syntax mentally before providing
4. Fix path escaping issues (use raw strings r"" or forward slashes)
5. Provide brief explanation after code

Context:
- Working directory: {working_dir}
- Previous operation: {last_file}

Format:
```python
# Syntactically correct Python code
```

Brief result explanation."""
    
    def _analyze_request_type(self, user_input: str) -> str:
        """Analyze request type to determine appropriate response style"""
        user_input_lower = user_input.lower()
        
        # Simple questions requiring direct answers
        simple_patterns = [
            'có', 'là gì', 'tên là gì', 'mấy giờ', 'thứ mấy', 'ngày nào',
            'where', 'what time', 'what is', 'how many'
        ]
        
        # File search operations
        search_patterns = [
            'tìm', 'find', 'search', 'có dự án', 'có file', 'trong ổ'
        ]
        
        # Check for simple questions
        if any(pattern in user_input_lower for pattern in simple_patterns):
            return 'simple_question'
        
        # Check for search operations
        if any(pattern in user_input_lower for pattern in search_patterns):
            return 'file_search'
            
        # Default to action required
        return 'action_required'
    
    def _extract_and_execute_code(self, ai_response: str) -> str:
        """Extract Python code blocks and execute them safely with better error handling"""
        
        # Find all Python code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', ai_response, re.DOTALL)
        
        execution_results = []
        
        for i, code in enumerate(code_blocks):
            try:
                # Pre-validate code for common syntax errors
                validated_code = self._validate_and_fix_code(code)
                
                # Log code execution
                self.error_handler.log_user_action(f"code_execution_{i}", validated_code[:100])
                
                print(f"🤖 AI executing code block {i+1}:")
                print(f"```python\n{validated_code}\n```")
                
                # Capture output
                from io import StringIO
                import contextlib
                
                output_buffer = StringIO()
                error_buffer = StringIO()
                
                # Execute code with captured output and errors
                with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                    exec(validated_code, self.execution_globals.copy())
                
                output = output_buffer.getvalue()
                errors = error_buffer.getvalue()
                
                if output.strip():
                    execution_results.append(f"✅ Kết quả: {output.strip()}")
                elif errors.strip():
                    execution_results.append(f"⚠️ Warning: {errors.strip()}")
                else:
                    execution_results.append(f"✅ Code executed successfully")
                
                print("✅ Code executed successfully")
                
            except Exception as e:
                error_msg = f"❌ Lỗi thực thi: {str(e)}"
                execution_results.append(error_msg)
                print(f"❌ Code execution error: {e}")
                self.error_handler.logger.error(f"Code execution failed: {e}")
        
        return "\n".join(execution_results) if execution_results else ""
    
    def _validate_and_fix_code(self, code: str) -> str:
        """Validate and fix common Python syntax errors"""
        # Fix common path escaping issues
        # Replace r"D:\" with r"D:/" or "D:/"
        import re
        
        # Fix raw string issues with backslashes
        code = re.sub(r'r"([^"]*\\)"', r'r"\1/"', code)
        
        # Fix unescaped backslashes in regular strings
        code = re.sub(r'"([^"]*\\[^"]*?)"', lambda m: f'"{m.group(1).replace(chr(92), "/")}"', code)
        
        # Add safety checks
        lines = code.split('\n')
        safe_lines = []
        
        for line in lines:
            # Add path existence checks for os.walk
            if 'os.walk(' in line and 'search_path' in line:
                safe_lines.append('if os.path.exists(search_path):')
                safe_lines.append('    ' + line)
                safe_lines.append('else:')
                safe_lines.append('    print(f"Đường dẫn {search_path} không tồn tại")')
            else:
                safe_lines.append(line)
        
        return '\n'.join(safe_lines)
    
    def update_context(self, **kwargs):
        """Update context information"""
        self.context_info.update(kwargs)
    
    def set_user_preferences(self, preferences: Dict[str, Any]):
        """Set user preferences for response style"""
        self.context_info['user_preferences'] = preferences
    
    def add_safe_module(self, module_name: str, module_obj):
        """Add a safe module to the execution environment"""
        self.execution_globals[module_name] = module_obj
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            "available_modules": list(self.execution_globals.keys()),
            "context_info": self.context_info,
            "safety_enabled": True
        }