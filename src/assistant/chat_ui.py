"""
Modern Chat UI for AI Assistant
"""
import os
import sys
import time
import datetime
from typing import Dict, Any, List, Optional
import textwrap
from dataclasses import dataclass

# Color codes for terminal
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

@dataclass
class ChatMessage:
    role: str  # 'user' or 'assistant' or 'system'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class ModernChatUI:
    """Modern, beautiful chat interface for AI Assistant"""
    
    def __init__(self, user_name: str = "Người dùng", assistant_name: str = "AI Assistant"):
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.chat_history: List[ChatMessage] = []
        self.terminal_width = self._get_terminal_width()
        self.setup_colors()
        
    def setup_colors(self):
        """Setup color support for terminal"""
        if sys.platform == 'win32':
            try:
                # Enable ANSI color support on Windows
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    def _get_terminal_width(self) -> int:
        """Get terminal width, default to 80 if unable to detect"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80
    
    def _update_terminal_width(self):
        """Update terminal width dynamically"""
        self.terminal_width = self._get_terminal_width()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def safe_print(self, text: str, color: str = "", end: str = "\n"):
        """Safe print with color support and Unicode fallback"""
        try:
            # Bypass hot-reload by writing directly to stdout
            import sys
            sys.stdout.write(f"{color}{text}{Colors.RESET}{end}")
            sys.stdout.flush()
        except UnicodeEncodeError:
            # Fallback to ASCII if Unicode fails
            import re
            clean_text = re.sub(r'[^\x00-\x7F]+', '?', text)
            import sys
            sys.stdout.write(f"{color}{clean_text}{Colors.RESET}{end}")
            sys.stdout.flush()
    
    def draw_header(self):
        """Draw beautiful header"""
        self._update_terminal_width()  # Update width dynamically
        width = self.terminal_width
        self.safe_print("")
        self.safe_print("╔" + "═" * (width - 2) + "╗", Colors.CYAN)
        
        # Unicode-aware title with emoji
        title = "🤖 AI ASSISTANT - Trợ lý thông minh"
        # Calculate visual width (emoji takes 2 chars visually but 1 in string)
        title_visual_len = len(title) + 1  # +1 for emoji visual width
        if title_visual_len > width - 4:
            title = "🤖 AI ASSISTANT"
            title_visual_len = len(title) + 1
        
        padding = max(0, (width - title_visual_len - 2) // 2)
        remaining = max(0, width - title_visual_len - padding - 2)
        title_line = "║" + " " * padding + title + " " * remaining + "║"
        self.safe_print(title_line, Colors.CYAN + Colors.BOLD)
        
        subtitle = f"Xin chào {self.user_name}! Tôi sẵn sàng hỗ trợ bạn"
        subtitle_len = len(subtitle)
        if subtitle_len > width - 4:
            subtitle = f"Xin chào {self.user_name}!"
            subtitle_len = len(subtitle)
            
        padding = max(0, (width - subtitle_len - 2) // 2)
        remaining = max(0, width - subtitle_len - padding - 2)
        subtitle_line = "║" + " " * padding + subtitle + " " * remaining + "║"
        self.safe_print(subtitle_line, Colors.CYAN)
        
        self.safe_print("╚" + "═" * (width - 2) + "╝", Colors.CYAN)
        self.safe_print("")
    
    def draw_separator(self, char: str = "─", color: str = Colors.BRIGHT_BLACK):
        """Draw a separator line"""
        self._update_terminal_width()  # Update width dynamically
        self.safe_print(char * self.terminal_width, color)
    
    def format_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def display_message(self, message: ChatMessage, show_timestamp: bool = True):
        """Display a chat message with beautiful formatting"""
        timestamp = f"[{message.timestamp}]" if show_timestamp else ""
        
        if message.role == "user":
            self._display_user_message(message, timestamp)
        elif message.role == "assistant":
            self._display_assistant_message(message, timestamp)
        elif message.role == "system":
            self._display_system_message(message, timestamp)
    
    def _display_user_message(self, message: ChatMessage, timestamp: str):
        """Display user message"""
        self._update_terminal_width()  # Update width dynamically
        self.safe_print("")
        
        # User header
        header = f"👤 {self.user_name} {timestamp}"
        self.safe_print(f"┌─ {header}", Colors.BRIGHT_BLUE)
        
        # Message content
        wrapped_lines = self._wrap_text(message.content, self.terminal_width - 4)
        for line in wrapped_lines:
            self.safe_print(f"│ {line}", Colors.BLUE)
        
        # Calculate separator length based on actual terminal width
        separator_length = min(len(header) + 2, self.terminal_width - 1)
        self.safe_print("└" + "─" * separator_length, Colors.BRIGHT_BLUE)
    
    def _display_assistant_message(self, message: ChatMessage, timestamp: str):
        """Display assistant message"""
        self._update_terminal_width()  # Update width dynamically
        self.safe_print("")
        
        # Assistant header
        header = f"🤖 {self.assistant_name} {timestamp}"
        self.safe_print(f"┌─ {header}", Colors.BRIGHT_GREEN)
        
        # Message content
        wrapped_lines = self._wrap_text(message.content, self.terminal_width - 4)
        for line in wrapped_lines:
            self.safe_print(f"│ {line}", Colors.GREEN)
        
        # Show metadata if available
        if message.metadata:
            self._display_metadata(message.metadata)
        
        # Calculate separator length based on actual terminal width
        separator_length = min(len(header) + 2, self.terminal_width - 1)
        self.safe_print("└" + "─" * separator_length, Colors.BRIGHT_GREEN)
    
    def _display_system_message(self, message: ChatMessage, timestamp: str):
        """Display system message"""
        self._update_terminal_width()  # Update width dynamically
        self.safe_print("")
        header = f"ℹ️  System {timestamp}"
        self.safe_print(f"┌─ {header}", Colors.BRIGHT_YELLOW)
        
        wrapped_lines = self._wrap_text(message.content, self.terminal_width - 4)
        for line in wrapped_lines:
            self.safe_print(f"│ {line}", Colors.YELLOW)
        
        # Calculate separator length based on actual terminal width
        separator_length = min(len(header) + 2, self.terminal_width - 1)
        self.safe_print("└" + "─" * separator_length, Colors.BRIGHT_YELLOW)
    
    def _display_metadata(self, metadata: Dict[str, Any]):
        """Display message metadata"""
        if metadata.get("tools_used"):
            tools = ", ".join(metadata["tools_used"])
            self.safe_print(f"│ 🔧 Tools: {tools}", Colors.DIM + Colors.GREEN)
        
        if metadata.get("model"):
            self.safe_print(f"│ 🧠 Model: {metadata['model']}", Colors.DIM + Colors.GREEN)
        
        if metadata.get("processing_time"):
            self.safe_print(f"│ ⏱️  Time: {metadata['processing_time']:.2f}s", Colors.DIM + Colors.GREEN)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width"""
        lines = []
        for paragraph in text.split('\n'):
            if paragraph.strip():
                wrapped = textwrap.fill(paragraph, width=width-2)
                lines.extend(wrapped.split('\n'))
            else:
                lines.append("")
        return lines
    
    def show_typing_indicator(self, duration: float = 1.0):
        """Show typing indicator animation"""
        self.safe_print("")
        self.safe_print(f"🤖 {self.assistant_name} đang suy nghĩ", Colors.BRIGHT_GREEN, end="")
        
        for i in range(int(duration * 4)):
            dots = "." * ((i % 3) + 1) + " " * (3 - (i % 3))
            self.safe_print(f"\r🤖 {self.assistant_name} đang suy nghĩ{dots}", Colors.BRIGHT_GREEN, end="")
            time.sleep(0.25)
        
        self.safe_print("\r" + " " * 50 + "\r", end="")  # Clear line
    
    def get_user_input(self) -> str:
        """Get user input with beautiful prompt"""
        self._update_terminal_width()  # Update before showing prompt
        self.safe_print("")
        prompt = f"💬 {self.user_name}: "
        try:
            self.safe_print(prompt, Colors.BRIGHT_BLUE, end="")
            # Use direct input to avoid hot-reload capture
            import sys
            sys.stdout.flush()
            user_input = input()
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return "/exit"
    
    def show_welcome_screen(self):
        """Show welcome screen with available commands"""
        self.clear_screen()
        self.draw_header()
        
        self.safe_print("🎯 Tôi có thể giúp bạn:", Colors.BRIGHT_WHITE + Colors.BOLD)
        capabilities = [
            "💼 Quản lý file và thư mục",
            "⚙️  Thực hiện lệnh hệ thống",
            "🔍 Tìm kiếm thông tin",
            "💭 Trò chuyện và tư vấn",
            "🧠 Học hỏi từ phản hồi của bạn",
            "🎨 Xử lý hình ảnh và văn bản",
            "📊 Phân tích dữ liệu"
        ]
        
        for cap in capabilities:
            self.safe_print(f"  {cap}", Colors.WHITE)
        
        self.safe_print("")
        self.safe_print("⚡ Lệnh đặc biệt:", Colors.BRIGHT_WHITE + Colors.BOLD)
        commands = [
            ("/help", "Hiển thị hướng dẫn chi tiết"),
            ("/stats", "Xem thống kê sử dụng"),
            ("/name <tên>", "Đặt tên của bạn"),
            ("/ainame <tên>", "Đặt tên cho AI"),
            ("/feedback <1-5> <nhận xét>", "Đánh giá phản hồi"),
            ("/tools", "Xem danh sách công cụ"),
            ("/clear", "Xóa màn hình chat"),
            ("/exit", "Thoát chương trình")
        ]
        
        for cmd, desc in commands:
            self.safe_print(f"  {Colors.CYAN}{cmd:<25}{Colors.WHITE} {desc}")
        
        self.draw_separator()
        self.safe_print("💡 Gõ tin nhắn và nhấn Enter để bắt đầu trò chuyện!", Colors.BRIGHT_YELLOW)
        self.safe_print("")
    
    def show_help_screen(self):
        """Show detailed help screen"""
        self.safe_print("")
        self.safe_print("📖 HƯỚNG DẪN SỬ DỤNG CHI TIẾT", Colors.BRIGHT_WHITE + Colors.BOLD)
        self.draw_separator("═", Colors.BRIGHT_WHITE)
        
        sections = [
            ("🗣️  TRRO CHUYỆN TỰ NHIÊN", [
                "Gõ câu hỏi hoặc yêu cầu bằng tiếng Việt",
                "VD: 'Giải thích về AI', 'Hôm nay thời tiết thế nào?'"
            ]),
            ("📁 QUẢN LÝ FILE", [
                "'Liệt kê file trong thư mục Documents'",
                "'Tạo thư mục mới tên project'",
                "'Copy file abc.txt đến thư mục backup'",
                "'Xóa file cũ không cần thiết'"
            ]),
            ("💻 HỆ THỐNG", [
                "'Thông tin hệ thống'",
                "'Xem các tiến trình đang chạy'",
                "'Chạy lệnh ping google.com'",
                "'Mở ứng dụng notepad'"
            ]),
            ("🎯 LỆNH ĐẶC BIỆT", [
                "/help - Hướng dẫn này",
                "/stats - Thống kê sử dụng",
                "/name <tên> - Đặt tên bạn",
                "/ainame <tên> - Đặt tên cho AI",
                "/feedback 5 Rất tốt! - Đánh giá",
                "/tools - Xem công cụ có sẵn",
                "/clear - Xóa màn hình",
                "/exit - Thoát"
            ])
        ]
        
        for title, items in sections:
            self.safe_print(f"\n{title}", Colors.BRIGHT_GREEN + Colors.BOLD)
            for item in items:
                self.safe_print(f"  • {item}", Colors.GREEN)
        
        self.safe_print("")
        self.draw_separator()
        
    def show_stats_screen(self, stats: Dict[str, Any]):
        """Show statistics in beautiful format"""
        self.safe_print("")
        self.safe_print("📊 THỐNG KÊ SỬ DỤNG", Colors.BRIGHT_WHITE + Colors.BOLD)
        self.draw_separator("═", Colors.BRIGHT_WHITE)
        
        # Basic stats
        self.safe_print(f"💬 Tổng cuộc hội thoại: {stats.get('total_conversations', 0)}", Colors.CYAN)
        
        avg_rating = stats.get('average_rating', 0)
        stars = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
        self.safe_print(f"⭐ Đánh giá trung bình: {avg_rating:.1f}/5 {stars}", Colors.YELLOW)
        
        if stats.get('usage_patterns'):
            self.safe_print(f"\n🎯 Hoạt động phổ biến:", Colors.BRIGHT_GREEN + Colors.BOLD)
            for activity, count in stats['usage_patterns'].items():
                bar = "█" * min(count, 20) + "░" * (20 - min(count, 20))
                self.safe_print(f"  {activity:<12} {bar} ({count})", Colors.GREEN)
        
        # Enhanced memory stats
        if stats.get('enhanced_memory'):
            em_stats = stats['enhanced_memory']
            self.safe_print(f"\n🧠 Bộ nhớ tăng cường:", Colors.BRIGHT_MAGENTA + Colors.BOLD)
            
            if em_stats.get('insights'):
                insights = em_stats['insights']
                self.safe_print(f"  📚 Kiến thức đã học: {insights.get('total_memories', 0)}", Colors.MAGENTA)
                self.safe_print(f"  🔗 Mối quan hệ: {insights.get('total_relationships', 0)}", Colors.MAGENTA)
            
            if em_stats.get('personality_traits'):
                self.safe_print(f"  👤 Đặc điểm cá nhân: {em_stats['personality_traits']}", Colors.MAGENTA)
        
        self.safe_print("")
        self.draw_separator()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to chat history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=self.format_timestamp(),
            metadata=metadata
        )
        self.chat_history.append(message)
        return message
    
    def display_error(self, error_message: str):
        """Display error message"""
        self.safe_print("")
        self.safe_print("❌ LỖI", Colors.BRIGHT_RED + Colors.BOLD)
        self.safe_print(f"│ {error_message}", Colors.RED)
        self.safe_print("")
    
    def display_success(self, success_message: str):
        """Display success message"""
        self.safe_print("")
        self.safe_print(f"✅ {success_message}", Colors.BRIGHT_GREEN)
        self.safe_print("")
    
    def display_warning(self, warning_message: str):
        """Display warning message"""
        self.safe_print("")
        self.safe_print(f"⚠️  {warning_message}", Colors.BRIGHT_YELLOW)
        self.safe_print("")
    
    def clear_chat_history(self):
        """Clear chat history and screen"""
        self.chat_history.clear()
        self.clear_screen()
        self.safe_print("🧹 Đã xóa lịch sử chat", Colors.BRIGHT_GREEN)
        self.safe_print("")
    
    def set_user_name(self, name: str):
        """Set user name"""
        old_name = self.user_name
        self.user_name = name
        self.safe_print(f"✅ Đã đổi tên từ '{old_name}' thành '{name}'", Colors.BRIGHT_GREEN)
    
    def set_assistant_name(self, name: str):
        """Set assistant name"""
        old_name = self.assistant_name
        self.assistant_name = name
        self.safe_print(f"✅ AI đã đổi tên từ '{old_name}' thành '{name}'", Colors.BRIGHT_GREEN)
    
    def show_goodbye(self):
        """Show goodbye message"""
        self.safe_print("")
        self.draw_separator("═", Colors.BRIGHT_CYAN)
        self.safe_print("👋 CẢM ƠN BẠN ĐÃ SỬ DỤNG AI ASSISTANT!", Colors.BRIGHT_CYAN + Colors.BOLD)
        self.safe_print(f"Hẹn gặp lại {self.user_name}! 🤖💙", Colors.CYAN)
        self.draw_separator("═", Colors.BRIGHT_CYAN)
        self.safe_print("")