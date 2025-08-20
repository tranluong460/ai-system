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
        
        if not self.is_hot_reload:
            safe_print("🤖 Khoi tao AI Assistant...", "Khoi tao AI Assistant...")
        
        # Khởi tạo UI
        self.ui = ModernChatUI()
        
        # Khởi tạo các component
        self.ai_core = AIAssistant(model_name)
        self.tool_executor = ToolExecutor()
        self.learning_system = LearningSystem()
        
        # Kiểm tra kết nối
        if not self.ai_core.check_ollama_connection():
            if self.is_hot_reload:
                print("❌ Không thể kết nối Ollama. Hãy chạy: ollama serve")
            else:
                self.ui.display_error("Không thể kết nối Ollama. Hãy chạy: ollama serve")
            sys.exit(1)
        
        if not self.is_hot_reload:
            safe_print("✅ AI Assistant san sang!", "AI Assistant san sang!")
        
        # Set user name if available
        if self.ai_core.user_profile.name != "User":
            self.ui.set_user_name(self.ai_core.user_profile.name)
    
    def _show_welcome(self):
        """Hiển thị welcome screen với UI mới"""
        self.ui.show_welcome_screen()
    
    def _detect_tool_request(self, user_input: str) -> Dict[str, Any]:
        """Phát hiện yêu cầu sử dụng tool"""
        user_lower = user_input.lower()
        
        # Patterns cho các tools
        tool_patterns = {
            # File operations
            r'(liệt kê|list|xem).*(file|tệp|thư mục)': ('list', {'path': '.'}),
            r'(tạo|tạo mới|create).*(thư mục|folder)\s+(.+)': ('create_folder', 'path_from_match'),
            r'(copy|sao chép).*(file|tệp)\s+(.+)\s+(to|đến|sang)\s+(.+)': ('copy', 'src_dst_from_match'),
            r'(move|di chuyển|chuyển).*(file|tệp)\s+(.+)\s+(to|đến|sang)\s+(.+)': ('move', 'src_dst_from_match'),
            r'(delete|xóa|remove).*(file|tệp|thư mục)\s+(.+)': ('delete', 'path_from_match'),
            r'(đọc|read|xem).*(file|tệp)\s+(.+)': ('read', 'path_from_match'),
            r'(tìm|search|find).*(file|tệp)\s+(.+)': ('search', 'query_from_match'),
            
            # System operations
            r'(thông tin|info).*(hệ thống|system)': ('system_info', {}),
            r'(process|tiến trình).*(đang chạy|running)': ('processes', {}),
            r'(thời tiết|weather)(?:\s+(.+))?': ('weather', 'city_from_match'),
            r'(mở|open).*(ứng dụng|app)\s+(.+)': ('open', 'app_from_match'),
            r'(chạy|run|thực hiện).*(lệnh|command)\s+(.+)': ('command', 'cmd_from_match'),
        }
        
        for pattern, (tool_name, params) in tool_patterns.items():
            match = re.search(pattern, user_lower)
            if match:
                # Xử lý parameters
                if params == {}:
                    return {'tool': tool_name, 'params': {}}
                elif params == 'path_from_match':
                    return {'tool': tool_name, 'params': {'path': match.group(3).strip()}}
                elif params == 'query_from_match':
                    return {'tool': tool_name, 'params': {'query': match.group(3).strip()}}
                elif params == 'city_from_match':
                    city = match.group(2).strip() if match.group(2) else "Ho Chi Minh City"
                    return {'tool': tool_name, 'params': {'city': city}}
                elif params == 'app_from_match':
                    return {'tool': tool_name, 'params': {'app_name': match.group(3).strip()}}
                elif params == 'cmd_from_match':
                    return {'tool': tool_name, 'params': {'command': match.group(3).strip()}}
                elif params == 'src_dst_from_match':
                    src = match.group(3).strip()
                    dst = match.group(5).strip()
                    return {'tool': tool_name, 'params': {'src': src, 'dst': dst}}
                elif isinstance(params, dict):
                    return {'tool': tool_name, 'params': params}
        
        return None
    
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
  • /name <ten> - Dat ten
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
                
                # Phát hiện tool request
                tool_request = self._detect_tool_request(user_input)
                
                tools_used = []
                if tool_request:
                    # Thực hiện tool
                    response = self._execute_tool_and_respond(tool_request, user_input)
                    tools_used = [tool_request['tool']]
                else:
                    # Chat thông thường
                    response = self.ai_core.chat(user_input)
                    
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