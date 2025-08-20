"""
Main AI Assistant - Giao diện chính để tương tác
"""
import sys
import os

# Fix encoding on Windows
if sys.platform == 'win32':
    import locale
    import ctypes
    
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Set console code pages
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except:
        pass
    
    # Set locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant.core import AIAssistant
from assistant.chat_ui import ModernChatUI
from tools.computer_tools import ToolExecutor
from learning.adaptive_system import LearningSystem
import json
import re
import time
from typing import Dict, Any, List

def safe_print(text: str, fallback: str = None):
    """Safe print function that handles Unicode errors"""
    try:
        print(text)
    except UnicodeEncodeError:
        if fallback:
            print(fallback)
        else:
            # Remove emojis and special characters as fallback
            import re
            clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
            print(clean_text)

class SmartAssistant:
    """AI Assistant thông minh với khả năng học tập"""
    
    def __init__(self, model_name: str = "llama3.2"):
        # Check if running in hot-reload mode
        self.is_hot_reload = '--hot-reload' in sys.argv or os.environ.get('HOT_RELOAD_MODE') == '1'
        
        # Remember last file operation for context
        self.last_file_path = None
        
        if not self.is_hot_reload:
            safe_print("🤖 Khoi tao AI Assistant...", "Khoi tao AI Assistant...")
        
        # Khởi tạo các component AI trước
        self.ai_core = AIAssistant(model_name)
        self.tool_executor = ToolExecutor()
        self.learning_system = LearningSystem()
        
        # Khởi tạo UI với tên đã load từ AI core
        assistant_name = self.ai_core.get_assistant_name()
        user_name = self.ai_core.user_profile.name if self.ai_core.user_profile.name != "User" else "Người dùng"
        
        # Debug: hiển thị tên đã load
        if not self.is_hot_reload:
            print(f"Loaded user name: '{self.ai_core.user_profile.name}' -> Display as: '{user_name}'")
            print(f"Loaded assistant name: '{assistant_name}'")
        
        self.ui = ModernChatUI(user_name=user_name, assistant_name=assistant_name)
        
        # Kiểm tra kết nối
        if not self.ai_core.check_ollama_connection():
            if self.is_hot_reload:
                print("❌ Không thể kết nối Ollama. Hãy chạy: ollama serve")
            else:
                self.ui.display_error("Không thể kết nối Ollama. Hãy chạy: ollama serve")
            sys.exit(1)
        
        if not self.is_hot_reload:
            safe_print("✅ AI Assistant san sang!", "AI Assistant san sang!")
    
    def _show_welcome(self):
        """Hiển thị welcome screen với UI mới"""
        self.ui.show_welcome_screen()
    
    
    def _ai_detect_tool_request(self, user_input: str) -> Dict[str, Any]:
        """AI-driven tool detection - hiểu ngôn ngữ tự nhiên hoàn toàn"""
        
        detection_prompt = f"""
Bạn là AI assistant có khả năng thực hiện các thao tác hệ thống. Phân tích yêu cầu của user và quyết định có cần tool không.

User request: "{user_input}"

Context: 
- Last file operation: {self.last_file_path or 'None'}
- Current working directory: D:\\MKT\\mkt-uid-2025\\libs\\data

Available tools và cách dùng:
1. create_file(path, content): tạo file mới với nội dung
2. create_folder(path): tạo thư mục
3. list(path): liệt kê files trong thư mục
4. read(path): đọc nội dung file
5. delete(path): xóa file/folder
6. copy(src, dst): copy file
7. move(src, dst): di chuyển file
8. system_info(): thông tin hệ thống
9. processes(): danh sách tiến trình
10. weather(city): thời tiết

QUAN TRỌNG: Khi tạo file, luôn thêm nội dung mẫu phù hợp:
- File .txt → thêm text mô tả
- File .py → thêm Python code template
- File .js → thêm JavaScript template
- File khác → thêm comment giải thích

Nếu user muốn thực hiện thao tác → trả về JSON:
{{"tool": "tool_name", "params": {{"key": "value"}}}}

Nếu chỉ chat thông thường → trả về: null

Hãy hiểu ý định thực sự của user và đưa ra quyết định thông minh.

Examples:
- "tạo file test.txt trong D:\\data" → {{"tool": "create_file", "params": {{"path": "D:\\\\data\\\\test.txt", "content": "Đây là file test được tạo bởi AI Assistant.\\nFile này dùng để test chức năng tạo file.\\n\\nNgày tạo: $(date)"}}}}
- "tạo file main.py" → {{"tool": "create_file", "params": {{"path": "main.py", "content": "#!/usr/bin/env python3\\n# -*- coding: utf-8 -*-\\n\\\"\\\"\\\"\\nMain Python script\\nCreated by AI Assistant\\n\\\"\\\"\\\"\\n\\nif __name__ == '__main__':\\n    print('Hello World!')"}}}}
- "liệt kê file" → {{"tool": "list", "params": {{"path": "."}}}}
- "xin chào" → null
"""
        
        try:
            response = self.ai_core.chat(detection_prompt)
            response = response.strip()
            
            if response.lower() in ['null', 'none', '']:
                return None
            
            # Extract JSON from response (AI might include extra text)
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate result structure
                if 'tool' in result and 'params' in result:
                    # Check if tool exists
                    available_tools = self.tool_executor.get_available_tools()
                    if result['tool'] in available_tools:
                        print(f"🤖 AI detected: {result}")
                        return result
                    else:
                        print(f"❌ Unknown tool: {result['tool']}")
                        return None
            
            return None
        except Exception as e:
            print(f"❌ AI detection error: {e}")
            return None
    
    def _ai_autonomous_action(self, user_input: str) -> str:
        """AI hoàn toàn tự chủ - tự code và thực hiện mọi thứ"""
        
        autonomous_prompt = f"""
Bạn là AI Assistant có khả năng TỰ ĐỘNG viết code và thực hiện bất kỳ tác vụ nào.

User request: "{user_input}"

Context:
- Working directory: D:\\MKT\\mkt-uid-2025\\libs\\data
- Previous file: {self.last_file_path or 'None'}
- Available: Python, file system, system commands

IMPORTANT: Thay vì chỉ mô tả, hãy THỰC SỰ THỰC HIỆN:

1. Nếu user muốn tạo file → VIẾT CODE Python và CHẠY để tạo file
2. Nếu user muốn xem file → VIẾT CODE Python và CHẠY để đọc file  
3. Nếu user muốn system info → VIẾT CODE Python và CHẠY để lấy thông tin
4. Bất kỳ request nào → TỰ ĐỘNG viết code phù hợp và thực hiện

Format response:
```python
# Code để thực hiện request
import os
# ... your code here
```

Kết quả: [mô tả kết quả sau khi chạy code]

Hãy THỰC SỰ LÀM, không chỉ nói!
"""
        
        try:
            response = self.ai_core.chat(autonomous_prompt)
            
            # Extract và execute Python code từ response
            self._extract_and_execute_code(response)
            
            return response
            
        except Exception as e:
            return f"Lỗi autonomous action: {e}"
    
    def _extract_and_execute_code(self, ai_response: str):
        """Extract Python code từ AI response và execute"""
        import re
        
        # Find Python code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', ai_response, re.DOTALL)
        
        for code in code_blocks:
            try:
                print(f"🤖 AI executing code:")
                print(f"```python\n{code}\n```")
                
                # Execute the code
                exec(code)
                
                print("✅ Code executed successfully")
                
            except Exception as e:
                print(f"❌ Code execution error: {e}")
    
    def _execute_tool_and_respond(self, tool_request: Dict[str, Any], user_input: str) -> str:
        """Thực hiện tool và tạo response"""
        tool_name = tool_request['tool']
        params = tool_request['params']
        
        # Thực hiện tool
        print(f"Thuc hien: {tool_name}")
        result = self.tool_executor.execute(tool_name, **params)
        
        # Tạo context cho AI
        context = f"""
Người dùng yêu cầu: {user_input}
Tool được sử dụng: {tool_name}
Tham số: {params}
Kết quả: {json.dumps(result, ensure_ascii=False, indent=2)}

Hãy phản hồi một cách tự nhiên về kết quả này.
"""
        
        # Gọi AI để tạo response tự nhiên
        ai_response = self.ai_core._call_ollama(context)
        
        # Lưu vào learning system
        self.learning_system.learn_from_interaction(
            user_input=user_input,
            ai_response=ai_response,
            tools_used=[tool_name],
            success=result.get('success', True)
        )
        
        return ai_response
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Xử lý các lệnh đặc biệt với UI mới"""
        cmd = user_input.lower().strip()
        
        if cmd == '/help':
            self.ui.show_help_screen()
            return True
        
        elif cmd == '/stats':
            stats = self.ai_core.get_stats()
            self.ui.show_stats_screen(stats)
            return True
        
        elif cmd.startswith('/name '):
            name = user_input[6:].strip()
            if name:
                self.ai_core.set_user_name(name)
                self.ui.set_user_name(name)
                self.ui.display_success(f"Xin chào {name}! Tôi sẽ ghi nhớ tên của bạn.")
            else:
                self.ui.display_error("Vui lòng nhập tên. VD: /name John")
            return True
        
        elif cmd.startswith('/ainame '):
            ai_name = user_input[8:].strip()
            if ai_name:
                # Set name in both AI core and UI
                self.ai_core.set_assistant_name(ai_name)
                self.ui.set_assistant_name(ai_name)
                self.ui.display_success(f"Tôi giờ tên là {ai_name}!")
            else:
                self.ui.display_error("Vui lòng nhập tên cho AI. VD: /ainame Leo")
            return True
        
        elif cmd.startswith('/feedback '):
            self._handle_feedback(user_input[10:])
            return True
        
        elif cmd == '/tools':
            tools = self.tool_executor.get_available_tools()
            tools_text = "Các tools có sẵn:\n" + "\n".join([f"  • {tool}" for tool in tools])
            message = self.ui.add_message("system", tools_text)
            self.ui.display_message(message)
            return True
        
        elif cmd == '/safe':
            result = self.tool_executor.tools.toggle_safe_mode()
            message = self.ui.add_message("system", result['message'])
            self.ui.display_message(message)
            return True
        
        elif cmd == '/clear':
            self.ui.clear_chat_history()
            self._show_welcome()
            return True
        
        elif cmd == '/exit':
            return False  # Signal to exit
        
        return None  # Not a special command
    
    def _handle_feedback(self, feedback_text: str):
        """Xử lý feedback từ user với UI mới"""
        parts = feedback_text.split(' ', 1)
        try:
            rating = int(parts[0])
            comment = parts[1] if len(parts) > 1 else ""
            
            if 1 <= rating <= 5:
                self.ai_core.learn_from_feedback(comment, rating)
                self.learning_system.record_feedback(rating, comment)
                self.ui.display_success(f"Cảm ơn feedback! Rating: {rating}/5")
            else:
                self.ui.display_error("Rating phải từ 1-5")
        except ValueError:
            self.ui.display_error("Format: /feedback <rating 1-5> <comment>")
    
    def _get_help_text(self) -> str:
        """Text hướng dẫn"""
        return """
HUONG DAN SU DUNG AI ASSISTANT

QUAN LY FILE:
  • "Liet ke file trong thu muc Documents"
  • "Tao thu muc moi ten test"
  • "Copy file abc.txt den folder backup"
  • "Xoa file old_file.txt"
  • "Doc file config.txt"
  • "Tim file co ten python"

HE THONG:
  • "Thong tin he thong"
  • "Xem cac tien trinh dang chay"
  • "Chay lenh ping google.com"
  • "Mo ung dung notepad"

THONG TIN:
  • "Thoi tiet Ha Noi"
  • "Thoi tiet hom nay"

TRO CHUYEN:
  • Hoi bat cu dieu gi
  • Toi se hoc tu phan hoi cua ban

LENH DAC BIET:
  • /name <ten> - Dat ten ban
  • /ainame <ten> - Dat ten cho AI
  • /feedback <1-5> <comment> - Danh gia
  • /stats - Xem thong ke
  • /safe - Che do an toan
  • /exit - Thoat
"""
    
    def _get_stats(self) -> str:
        """Lấy thống kê"""
        ai_stats = self.ai_core.get_stats()
        learning_stats = self.learning_system.get_learning_stats()
        
        return f"""
THONG KE AI ASSISTANT

Cuoc hoi thoai: {ai_stats.get('total_conversations', 0)}
Rating trung binh: {ai_stats.get('average_rating', 0):.1f}/5
Patterns da hoc: {learning_stats['total_patterns_learned']}
Tuong tac gan day: {learning_stats['recent_activity_count']} (7 ngay qua)

Top patterns:
{chr(10).join([f"  • {pattern}: {count} lan" for pattern, count in learning_stats['top_patterns']])}

So thich:
{chr(10).join([f"  • {k}: {v}" for k, v in ai_stats.get('usage_patterns', {}).items()])}
"""
    
    def run(self):
        """Chạy AI Assistant với UI mới"""
        # Hiển thị welcome screen
        self._show_welcome()
        
        while True:
            try:
                # Lấy input từ user với UI đẹp
                user_input = self.ui.get_user_input()
                
                if not user_input:
                    continue
                
                # Thêm message của user vào chat
                user_message = self.ui.add_message("user", user_input)
                self.ui.display_message(user_message)
                
                # Xử lý lệnh đặc biệt
                special_result = self._handle_special_commands(user_input)
                if special_result is not None:
                    if special_result == False:  # Exit command
                        break
                    continue
                
                # Hiển thị typing indicator
                self.ui.show_typing_indicator(1.5)
                
                start_time = time.time()
                
                # Lấy suggestions từ learning system
                suggestions = self.learning_system.get_suggestions(user_input)
                
                # AI tự động xử lý request - hoàn toàn autonomous
                response = self._ai_autonomous_action(user_input)
                tools_used = []
                
                # Lưu vào learning system
                self.learning_system.learn_from_interaction(
                    user_input=user_input,
                    ai_response=response,
                    tools_used=[],
                    success=True
                )
                
                processing_time = time.time() - start_time
                
                # Thêm response của AI vào chat với metadata
                metadata = {
                    "model": self.ai_core.model_name,
                    "processing_time": processing_time,
                    "tools_used": tools_used
                }
                
                ai_message = self.ui.add_message("assistant", response, metadata)
                self.ui.display_message(ai_message)
                
                # Hiển thị suggestions nếu có
                if suggestions and len(suggestions) > 0:
                    suggestion_text = f"💡 Gợi ý: {', '.join([s['pattern'] for s in suggestions[:2]])}"
                    self.ui.display_warning(suggestion_text)
                
                # Gợi ý next actions
                next_actions = self.learning_system.suggest_next_actions(user_input)
                if next_actions:
                    next_text = f"🎯 Có thể bạn muốn: {', '.join(next_actions[:2])}"
                    suggestion_msg = self.ui.add_message("system", next_text)
                    self.ui.display_message(suggestion_msg)
                
            except KeyboardInterrupt:
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.ui.display_error(f"Đã xảy ra lỗi: {str(e)}")
                continue

def main():
    """Hàm main"""
    try:
        # Cho phép user chọn model
        print("AI Assistant - Chon model AI:")
        print("1. llama3.2 (mac dinh)")
        print("2. qwen2.5:7b")
        print("3. codellama:7b")
        print("4. Model khac")
        
        choice = input("Chon (1-4): ").strip()
        
        model_map = {
            "1": "llama3.2",
            "2": "qwen2.5:7b", 
            "3": "codellama:7b",
            "4": None
        }
        
        model_name = model_map.get(choice, "llama3.2")
        
        if model_name is None:
            model_name = input("Nhap ten model: ").strip()
        
        # Khởi tạo và chạy assistant
        assistant = SmartAssistant(model_name)
        assistant.run()
        
    except Exception as e:
        print(f"Loi khoi tao: {e}")
        print("Hay chac chan Ollama da duoc cai dat va chay: ollama serve")

if __name__ == "__main__":
    main()