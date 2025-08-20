"""
Autonomous AI Engine - Self-coding and self-executing AI system
"""
import re
import sys
import os
from typing import Dict, Any, Optional
from ..utils.error_handler import ErrorHandler, safe_operation

class AutonomousEngine:
    """AI engine that can write and execute code autonomously"""
    
    def __init__(self, ai_core, context_info: Dict[str, Any] = None):
        self.ai_core = ai_core
        self.error_handler = ErrorHandler("autonomous_engine")
        self.context_info = context_info or {}
        self.execution_globals = self._setup_execution_environment()
    
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
        """Build comprehensive prompt for autonomous AI"""
        
        working_dir = self.context_info.get('working_directory', os.getcwd())
        last_file = self.context_info.get('last_file_path', 'None')
        
        return f\"\"\"Bạn là AI Assistant với khả năng TỰ ĐỘNG viết code và thực hiện tác vụ.

User request: "{user_input}"

Context:
- Working directory: {working_dir}
- Previous file operation: {last_file}
- Available: Python, file system operations, system info

IMPORTANT RULES:
1. Nếu user muốn tạo file → VIẾT CODE Python để tạo file với nội dung phù hợp
2. Nếu user muốn xem/đọc file → VIẾT CODE Python để đọc và hiển thị file
3. Nếu user muốn system info → VIẾT CODE Python để lấy thông tin hệ thống
4. Bất kỳ request nào → TỰ ĐỘNG viết code Python để thực hiện

RESPONSE FORMAT:
```python
# Code để thực hiện request của user
import os
# ... your implementation here
print("Kết quả thực hiện")
```

Sau đó giải thích ngắn gọn về những gì code đã làm.

QUAN TRỌNG: Hãy THỰC SỰ THỰC HIỆN bằng code, không chỉ mô tả!\"\"\"
    
    def _extract_and_execute_code(self, ai_response: str) -> str:
        """Extract Python code blocks and execute them safely"""
        
        # Find all Python code blocks
        code_blocks = re.findall(r'```python\\n(.*?)\\n```', ai_response, re.DOTALL)
        
        execution_results = []
        
        for i, code in enumerate(code_blocks):
            try:
                # Log code execution
                self.error_handler.log_user_action(f"code_execution_{i}", code[:100])
                
                print(f"🤖 AI executing code block {i+1}:")
                print(f"```python\\n{code}\\n```")
                
                # Capture output
                from io import StringIO
                import contextlib
                
                output_buffer = StringIO()
                
                # Execute code with captured output
                with contextlib.redirect_stdout(output_buffer):
                    exec(code, self.execution_globals.copy())
                
                output = output_buffer.getvalue()
                
                if output.strip():
                    execution_results.append(f"Block {i+1} output: {output.strip()}")
                else:
                    execution_results.append(f"Block {i+1}: Executed successfully (no output)")
                
                print("✅ Code executed successfully")
                
            except Exception as e:
                error_msg = f"Block {i+1} error: {str(e)}"
                execution_results.append(error_msg)
                print(f"❌ Code execution error: {e}")
                self.error_handler.logger.error(f"Code execution failed: {e}")
        
        return "\\n".join(execution_results) if execution_results else ""
    
    def update_context(self, **kwargs):
        """Update context information"""
        self.context_info.update(kwargs)
    
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