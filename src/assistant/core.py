"""
Core AI Assistant với khả năng học tập và tương tác
"""
import json
import os
import datetime
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory.enhanced_memory import EnhancedMemorySystem

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

@dataclass
class Conversation:
    """Class lưu trữ cuộc hội thoại"""
    timestamp: str
    user_input: str
    ai_response: str
    context: Dict[str, Any]
    feedback: Optional[str] = None

@dataclass
class UserProfile:
    """Profile người dùng để cá nhân hóa"""
    name: str = "User"
    preferences: Dict[str, Any] = None
    usage_patterns: Dict[str, int] = None
    common_tasks: List[str] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.usage_patterns is None:
            self.usage_patterns = {}
        if self.common_tasks is None:
            self.common_tasks = []

class AIAssistant:
    """AI Assistant chính với khả năng học tập"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        self.memory_file = "data/memory/conversations.json"
        self.profile_file = "data/memory/user_profile.json"
        self.learning_file = "data/memory/learning_data.json"
        self.assistant_name = "AI Assistant"  # Default name
        
        # Khởi tạo thư mục
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Load dữ liệu
        self.conversations = self._load_conversations()
        self.user_profile = self._load_user_profile()
        self.learning_data = self._load_learning_data()
        
        # Load assistant name from profile
        self._load_assistant_name()
        
        # Initialize Enhanced Memory System
        safe_print("Initializing Enhanced Memory...", "Initializing Enhanced Memory...")
        self.enhanced_memory = EnhancedMemorySystem()
        
        # System prompt cơ bản
        self.system_prompt = self._build_system_prompt()
    
    def _load_conversations(self) -> List[Conversation]:
        """Load lịch sử hội thoại"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [Conversation(**conv) for conv in data]
            except Exception as e:
                print(f"Loi load conversations: {e}")
        return []
    
    def _save_conversations(self):
        """Lưu lịch sử hội thoại"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(conv) for conv in self.conversations], f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Loi save conversations: {e}")
    
    def _load_user_profile(self) -> UserProfile:
        """Load profile người dùng"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserProfile(**data)
            except Exception as e:
                print(f"Loi load profile: {e}")
        return UserProfile()
    
    def _save_user_profile(self):
        """Lưu profile người dùng"""
        try:
            # Include assistant name in profile
            profile_data = asdict(self.user_profile)
            profile_data['assistant_name'] = self.assistant_name
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Loi save profile: {e}")
    
    def _load_assistant_name(self):
        """Load assistant name from profile"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.assistant_name = data.get('assistant_name', 'AI Assistant')
            except Exception as e:
                print(f"Loi load assistant name: {e}")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load dữ liệu học tập"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Loi load learning data: {e}")
        return {
            "successful_patterns": [],
            "failed_patterns": [],
            "user_corrections": [],
            "task_preferences": {},
            "response_ratings": []
        }
    
    def _save_learning_data(self):
        """Lưu dữ liệu học tập"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Loi save learning data: {e}")
    
    def _build_system_prompt(self) -> str:
        """Xây dựng system prompt dựa trên profile và learning data"""
        base_prompt = f"""Bạn là {self.assistant_name}, một AI Assistant thông minh hỗ trợ người dùng các tác vụ trên máy tính.

Khả năng của bạn:
- Tương tác và trò chuyện tự nhiên
- Hỗ trợ quản lý file và thư mục
- Thực hiện các lệnh hệ thống
- Tìm kiếm thông tin
- Học từ phản hồi của người dùng

Quy tắc:
- Luôn hỏi rõ trước khi thực hiện hành động quan trọng
- Giải thích các bước thực hiện
- Học hỏi từ phản hồi để cải thiện
- Cá nhân hóa dựa trên sở thích người dùng"""

        # Thêm thông tin cá nhân hóa
        base_prompt += f"\n\nTên của bạn: {self.assistant_name}"
        if self.user_profile.name != "User":
            base_prompt += f"\nTên người dùng: {self.user_profile.name}"
        
        if self.user_profile.common_tasks:
            tasks = ", ".join(self.user_profile.common_tasks[:5])
            base_prompt += f"\nCác tác vụ thường làm: {tasks}"
        
        # Thêm patterns học được
        if self.learning_data.get("successful_patterns"):
            recent_patterns = self.learning_data["successful_patterns"][-3:]
            patterns_text = "; ".join(recent_patterns)
            base_prompt += f"\nCác cách làm hiệu quả: {patterns_text}"
        
        return base_prompt
    
    def _call_ollama(self, prompt: str, context: List[Dict] = None) -> str:
        """Gọi Ollama API"""
        try:
            messages = []
            
            # Thêm system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Thêm context từ cuộc hội thoại trước
            if context:
                messages.extend(context)
            
            # Thêm câu hỏi hiện tại
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False
            }
            
            # Set proper headers for UTF-8
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                # Ensure proper UTF-8 handling
                response.encoding = 'utf-8'
                result = response.json()
                return result["message"]["content"]
            else:
                return f"Lỗi khi gọi Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Lỗi kết nối: {str(e)}"
    
    def _get_context(self, limit: int = 5) -> List[Dict]:
        """Lấy context từ cuộc hội thoại gần đây"""
        context = []
        recent_convs = self.conversations[-limit:] if len(self.conversations) > limit else self.conversations
        
        for conv in recent_convs:
            context.append({"role": "user", "content": conv.user_input})
            context.append({"role": "assistant", "content": conv.ai_response})
        
        return context
    
    def chat(self, user_input: str) -> str:
        """Chat với AI với Enhanced Memory"""
        safe_print("🤖 Dang xu ly voi Enhanced Memory...", "Dang xu ly voi Enhanced Memory...")
        
        # Get enhanced context từ memory system
        smart_context = self.enhanced_memory.generate_smart_response_context(user_input)
        
        # Lấy context truyền thống
        traditional_context = self._get_context(limit=2)
        
        # Combine contexts
        if smart_context:
            enhanced_prompt = f"""Context từ memory system:
{smart_context}

Current conversation context: {len(traditional_context)} previous messages

User question: {user_input}"""
        else:
            enhanced_prompt = user_input
        
        # Gọi AI với enhanced context
        ai_response = self._call_ollama(enhanced_prompt, traditional_context)
        
        # Lưu vào cả traditional và enhanced memory
        conversation = Conversation(
            timestamp=datetime.datetime.now().isoformat(),
            user_input=user_input,
            ai_response=ai_response,
            context={"model": self.model_name, "context_length": len(traditional_context), "enhanced_memory": True}
        )
        
        self.conversations.append(conversation)
        self._save_conversations()
        
        # Store trong Enhanced Memory System
        self.enhanced_memory.store_conversation(
            user_input=user_input,
            ai_response=ai_response,
            context=conversation.context
        )
        
        # Update usage patterns
        self._update_usage_patterns(user_input)
        
        return ai_response
    
    def _update_usage_patterns(self, user_input: str):
        """Cập nhật patterns sử dụng"""
        # Phân tích loại câu hỏi
        keywords = {
            "file": ["file", "tệp", "folder", "thư mục", "copy", "move", "delete"],
            "search": ["tìm", "search", "find", "look"],
            "system": ["system", "hệ thống", "process", "tiến trình"],
            "coding": ["code", "lập trình", "python", "script"],
            "chat": ["chào", "hello", "how", "gì", "sao"]
        }
        
        for category, words in keywords.items():
            if any(word in user_input.lower() for word in words):
                self.user_profile.usage_patterns[category] = \
                    self.user_profile.usage_patterns.get(category, 0) + 1
        
        self._save_user_profile()
    
    def learn_from_feedback(self, feedback: str, rating: int = None):
        """Học từ phản hồi của người dùng"""
        if self.conversations:
            # Cập nhật feedback cho cuộc hội thoại cuối
            self.conversations[-1].feedback = feedback
            
            # Lưu vào learning data
            if rating and rating >= 4:  # Rating tốt
                pattern = {
                    "user_input": self.conversations[-1].user_input,
                    "ai_response": self.conversations[-1].ai_response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.learning_data["successful_patterns"].append(pattern)
            
            if feedback.strip():
                self.learning_data["user_corrections"].append({
                    "original_response": self.conversations[-1].ai_response,
                    "user_feedback": feedback,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            
            if rating:
                self.learning_data["response_ratings"].append({
                    "rating": rating,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            
            # Lưu dữ liệu
            self._save_conversations()
            self._save_learning_data()
            
            print("Da ghi nhan phan hoi, cam on ban!")
    
    def get_stats(self) -> Dict[str, Any]:
        """Thống kê sử dụng với Enhanced Memory"""
        total_conversations = len(self.conversations)
        
        if total_conversations == 0:
            return {"message": "Chưa có cuộc hội thoại nào"}
        
        # Tính rating trung bình
        ratings = [r["rating"] for r in self.learning_data.get("response_ratings", [])]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Get enhanced memory insights
        memory_insights = self.enhanced_memory.get_memory_insights()
        
        # Get conversation patterns analysis
        patterns_analysis = self.enhanced_memory.analyze_conversation_patterns(30)
        
        return {
            "total_conversations": total_conversations,
            "usage_patterns": self.user_profile.usage_patterns,
            "average_rating": avg_rating,
            "successful_patterns": len(self.learning_data.get("successful_patterns", [])),
            "user_corrections": len(self.learning_data.get("user_corrections", [])),
            "enhanced_memory": {
                "insights": memory_insights,
                "conversation_patterns": patterns_analysis,
                "personality_traits": len(self.enhanced_memory.personality_graph.get_personality_summary())
            }
        }
    
    def set_user_name(self, name: str):
        """Đặt tên người dùng"""
        self.user_profile.name = name
        self._save_user_profile()
        self.system_prompt = self._build_system_prompt()  # Rebuild prompt
        print(f"Da dat ten: {name}")
    
    def set_assistant_name(self, name: str):
        """Đặt tên cho AI assistant"""
        self.assistant_name = name
        self._save_user_profile()
        self.system_prompt = self._build_system_prompt()  # Rebuild prompt
        print(f"AI da doi ten thanh: {name}")
    
    def get_assistant_name(self) -> str:
        """Lấy tên AI assistant"""
        return self.assistant_name
    
    def check_ollama_connection(self) -> bool:
        """Kiểm tra kết nối Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False