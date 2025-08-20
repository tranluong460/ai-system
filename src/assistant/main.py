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
from assistant.command_handler import CommandHandler
from assistant.autonomous_engine import AutonomousEngine
from assistant.response_manager import ResponseManager
from tools.computer_tools import ToolExecutor
from learning.adaptive_system import LearningSystem
from utils.error_handler import ErrorHandler
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
    """AI Assistant thông minh với kiến trúc modular được refactor"""
    
    def __init__(self, model_name: str = "llama3.2"):
        # Check if running in hot-reload mode
        self.is_hot_reload = '--hot-reload' in sys.argv or os.environ.get('HOT_RELOAD_MODE') == '1'
        
        # Initialize error handler
        self.error_handler = ErrorHandler("smart_assistant")
        
        if not self.is_hot_reload:
            safe_print("🤖 Khoi tao AI Assistant...", "Khoi tao AI Assistant...")
        
        # Initialize core components
        self._initialize_components(model_name)
        
        # Check Ollama connection
        self._check_ollama_connection()
        
        if not self.is_hot_reload:
            safe_print("✅ AI Assistant san sang!", "AI Assistant san sang!")
    
    def _initialize_components(self, model_name: str):
        """Initialize all AI Assistant components"""
        # Core AI components
        self.ai_core = AIAssistant(model_name)
        self.tool_executor = ToolExecutor()
        self.learning_system = LearningSystem()
        
        # UI setup
        assistant_name = self.ai_core.get_assistant_name()
        user_name = self.ai_core.user_profile.name if self.ai_core.user_profile.name != "User" else "Người dùng"
        
        if not self.is_hot_reload:
            print(f"Loaded user name: '{self.ai_core.user_profile.name}' -> Display as: '{user_name}'")
            print(f"Loaded assistant name: '{assistant_name}'")
        
        self.ui = ModernChatUI(user_name=user_name, assistant_name=assistant_name)
        
        # Initialize specialized handlers
        self.command_handler = CommandHandler(self.ui, self.ai_core, self.tool_executor, self.learning_system)
        self.autonomous_engine = AutonomousEngine(self.ai_core)
        self.response_manager = ResponseManager(self.ui, self.ai_core, self.learning_system)
    
    def _check_ollama_connection(self):
        """Check Ollama connection and exit if failed"""
        if not self.ai_core.check_ollama_connection():
            error_msg = "Không thể kết nối Ollama. Hãy chạy: ollama serve"
            if self.is_hot_reload:
                print(f"❌ {error_msg}")
            else:
                self.ui.display_error(error_msg)
            sys.exit(1)
    
    def _show_welcome(self):
        """Hiển thị welcome screen với UI mới"""
        self.ui.show_welcome_screen()
    
    
    # Removed old AI detection method - now handled by AutonomousEngine
    
    def _process_autonomous_request(self, user_input: str) -> str:
        """Process request using autonomous engine"""
        try:
            # Update context for autonomous engine
            self.autonomous_engine.update_context(
                working_directory=os.getcwd(),
                last_file_path=getattr(self, 'last_file_path', None)
            )
            
            # Execute autonomous action
            response = self.autonomous_engine.execute_autonomous_action(user_input)
            return response
            
        except Exception as e:
            self.error_handler.logger.error(f"Autonomous processing failed: {e}")
            return f"Lỗi xử lý autonomous: {e}"
    
    # Code execution now handled by AutonomousEngine
    
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
    
    # Command handling now delegated to CommandHandler
    
    # Feedback handling now in CommandHandler
    
    # Help text moved to CommandHandler
    
    # Stats handling moved to CommandHandler
    
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
                
                # Handle special commands
                command_result = self.command_handler.handle_command(user_input)
                if command_result is not None:
                    if command_result == False:  # Exit command
                        break
                    continue
                
                # Show typing indicator
                self.response_manager.show_typing_indicator(1.5)
                
                start_time = time.time()
                
                # Process request autonomously
                response = self._process_autonomous_request(user_input)
                
                processing_time = time.time() - start_time
                
                # Process and display response
                self.response_manager.process_and_respond(
                    user_input=user_input,
                    response=response,
                    tools_used=[],
                    autonomous_execution=True,
                    processing_time=processing_time
                )
                
            except KeyboardInterrupt:
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.response_manager.process_error_response(user_input, e, "xử lý yêu cầu")
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