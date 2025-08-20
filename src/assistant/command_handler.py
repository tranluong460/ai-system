"""
Command handler for special commands in AI Assistant
"""
from typing import Optional, Dict, Any
from .chat_ui import ModernChatUI
from .core import AIAssistant
from tools.computer_tools import ToolExecutor
from learning.adaptive_system import LearningSystem

class CommandHandler:
    """Handles special commands and system operations"""
    
    def __init__(self, ui: ModernChatUI, ai_core: AIAssistant, 
                 tool_executor: ToolExecutor, learning_system: LearningSystem, autonomous_engine=None):
        self.ui = ui
        self.ai_core = ai_core
        self.tool_executor = tool_executor
        self.learning_system = learning_system
        self.autonomous_engine = autonomous_engine
    
    def handle_command(self, user_input: str) -> Optional[bool]:
        """
        Handle special commands
        Returns:
            True: Command handled successfully, continue
            False: Exit command
            None: Not a special command
        """
        cmd = user_input.lower().strip()
        
        if cmd == '/help':
            self.ui.show_help_screen()
            return True
        
        elif cmd == '/stats':
            stats = self.ai_core.get_stats()
            self.ui.show_stats_screen(stats)
            return True
        
        elif cmd.startswith('/name '):
            return self._handle_set_user_name(user_input[6:].strip())
        
        elif cmd.startswith('/ainame '):
            return self._handle_set_ai_name(user_input[8:].strip())
        
        elif cmd.startswith('/feedback '):
            self._handle_feedback(user_input[10:])
            return True
        
        elif cmd == '/tools':
            self._show_available_tools()
            return True
        
        elif cmd == '/safe':
            self._toggle_safe_mode()
            return True
        
        elif cmd == '/clear':
            self.ui.clear_chat_history()
            return True
        
        elif cmd == '/exit':
            return False
        
        return None  # Not a special command
    
    def _handle_set_user_name(self, name: str) -> bool:
        """Set user name"""
        if name:
            self.ai_core.set_user_name(name)
            self.ui.set_user_name(name)
            self.ui.display_success(f"Xin chào {name}! Tôi sẽ ghi nhớ tên của bạn.")
        else:
            self.ui.display_error("Vui lòng nhập tên. VD: /name John")
        return True
    
    def _handle_set_ai_name(self, ai_name: str) -> bool:
        """Set AI assistant name"""
        if ai_name:
            self.ai_core.set_assistant_name(ai_name)
            self.ui.set_assistant_name(ai_name)
            self.ui.display_success(f"Tôi giờ tên là {ai_name}!")
        else:
            self.ui.display_error("Vui lòng nhập tên cho AI. VD: /ainame Leo")
        return True
    
    def _handle_feedback(self, feedback_text: str):
        """Handle user feedback and send to autonomous engine"""
        parts = feedback_text.split(' ', 1)
        try:
            rating = int(parts[0])
            comment = parts[1] if len(parts) > 1 else ""
            
            if 1 <= rating <= 5:
                # Get last conversation for feedback context
                if hasattr(self.ai_core, 'conversations') and self.ai_core.conversations:
                    last_conv = self.ai_core.conversations[-1]
                    user_input = last_conv.user_input
                    ai_response = last_conv.ai_response
                    
                    # Send feedback to autonomous engine if available
                    if self.autonomous_engine:
                        self.autonomous_engine.record_feedback(user_input, ai_response, rating, comment)
                    
                    # Original feedback handling
                    self.ai_core.learn_from_feedback(comment, rating)
                    self.learning_system.record_feedback(rating, comment)
                    self.ui.display_success(f"Cảm ơn feedback! Rating: {rating}/5")
                else:
                    self.ui.display_error("Không có conversation để feedback")
            else:
                self.ui.display_error("Rating phải từ 1-5")
        except ValueError:
            self.ui.display_error("Format: /feedback <rating 1-5> <comment>")
    
    def _show_available_tools(self):
        """Show available tools"""
        tools = self.tool_executor.get_available_tools()
        tools_text = "Các tools có sẵn:\\n" + "\\n".join([f"  • {tool}" for tool in tools])
        message = self.ui.add_message("system", tools_text)
        self.ui.display_message(message)
    
    def _toggle_safe_mode(self):
        """Toggle safe mode"""
        result = self.tool_executor.tools.toggle_safe_mode()
        message = self.ui.add_message("system", result['message'])
        self.ui.display_message(message)