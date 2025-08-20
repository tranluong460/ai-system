"""
Hệ thống học tập và thích ứng cho AI Assistant
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class LearningSystem:
    """Hệ thống học tập thích ứng"""
    
    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Files lưu trữ
        self.patterns_file = os.path.join(data_dir, "patterns.json")
        self.preferences_file = os.path.join(data_dir, "preferences.json")
        self.feedback_file = os.path.join(data_dir, "feedback.json")
        self.commands_file = os.path.join(data_dir, "commands.json")
        
        # Load dữ liệu
        self.patterns = self._load_json(self.patterns_file, {})
        self.preferences = self._load_json(self.preferences_file, {})
        self.feedback_history = self._load_json(self.feedback_file, [])
        self.command_history = self._load_json(self.commands_file, [])
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON file với default value"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi load {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """Lưu data vào JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi save {filepath}: {e}")
    
    def learn_from_interaction(self, user_input: str, ai_response: str, 
                             tools_used: List[str] = None, success: bool = True):
        """Học từ tương tác"""
        timestamp = datetime.now().isoformat()
        
        # Phân tích pattern từ user input
        patterns = self._extract_patterns(user_input)
        
        # Lưu successful patterns
        if success and patterns:
            for pattern in patterns:
                if pattern not in self.patterns:
                    self.patterns[pattern] = {
                        "count": 0,
                        "success_rate": 0,
                        "tools_used": [],
                        "responses": []
                    }
                
                self.patterns[pattern]["count"] += 1
                if tools_used:
                    self.patterns[pattern]["tools_used"].extend(tools_used)
                
                # Lưu response pattern (tóm tắt)
                response_summary = ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
                self.patterns[pattern]["responses"].append({
                    "summary": response_summary,
                    "timestamp": timestamp,
                    "tools": tools_used or []
                })
                
                # Giới hạn lịch sử
                if len(self.patterns[pattern]["responses"]) > 10:
                    self.patterns[pattern]["responses"] = self.patterns[pattern]["responses"][-10:]
        
        # Lưu command history
        self.command_history.append({
            "input": user_input,
            "response": ai_response,
            "tools_used": tools_used or [],
            "success": success,
            "timestamp": timestamp
        })
        
        # Giới hạn lịch sử commands
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
        
        # Lưu dữ liệu
        self._save_json(self.patterns_file, self.patterns)
        self._save_json(self.commands_file, self.command_history)
    
    def _extract_patterns(self, user_input: str) -> List[str]:
        """Trích xuất patterns từ user input"""
        patterns = []
        
        # Patterns cho file operations
        file_patterns = {
            r'(tạo|tạo mới|create).*?(thư mục|folder)': 'create_folder',
            r'(copy|sao chép).*?(file|tệp)': 'copy_file',
            r'(move|di chuyển|chuyển).*?(file|tệp)': 'move_file',
            r'(delete|xóa).*?(file|tệp|thư mục)': 'delete_file',
            r'(đọc|read|xem).*?(file|tệp)': 'read_file',
            r'(ghi|write|lưu).*?(file|tệp)': 'write_file',
            r'(tìm|search|find).*?(file|tệp)': 'search_file',
            r'(liệt kê|list|danh sách).*?(file|tệp)': 'list_files'
        }
        
        # Patterns cho system operations
        system_patterns = {
            r'(thông tin|info).*?(hệ thống|system)': 'system_info',
            r'(process|tiến trình).*?(đang chạy|running)': 'list_processes',
            r'(thời tiết|weather)': 'get_weather',
            r'(mở|open).*?(ứng dụng|app)': 'open_app',
            r'(chạy|run|thực hiện).*?(lệnh|command)': 'run_command'
        }
        
        # Patterns cho conversation
        conversation_patterns = {
            r'(chào|hello|hi)': 'greeting',
            r'(cảm ơn|thank)': 'thanks',
            r'(giúp|help|hướng dẫn)': 'help_request',
            r'(giải thích|explain)': 'explanation_request'
        }
        
        all_patterns = {**file_patterns, **system_patterns, **conversation_patterns}
        
        user_lower = user_input.lower()
        for regex, pattern_name in all_patterns.items():
            if re.search(regex, user_lower):
                patterns.append(pattern_name)
        
        return patterns
    
    def get_suggestions(self, user_input: str) -> List[Dict[str, Any]]:
        """Đưa ra gợi ý dựa trên patterns đã học"""
        patterns = self._extract_patterns(user_input)
        suggestions = []
        
        for pattern in patterns:
            if pattern in self.patterns:
                pattern_data = self.patterns[pattern]
                
                # Lấy tools được sử dụng nhiều nhất
                if pattern_data["tools_used"]:
                    tool_counts = Counter(pattern_data["tools_used"])
                    most_used_tools = tool_counts.most_common(3)
                    
                    suggestions.append({
                        "pattern": pattern,
                        "confidence": min(pattern_data["count"] / 10, 1.0),  # Max 1.0
                        "suggested_tools": [tool for tool, count in most_used_tools],
                        "usage_count": pattern_data["count"]
                    })
        
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
    
    def learn_preferences(self, preference_type: str, value: Any):
        """Học preferences của user"""
        if preference_type not in self.preferences:
            self.preferences[preference_type] = {}
        
        if isinstance(value, str):
            if value not in self.preferences[preference_type]:
                self.preferences[preference_type][value] = 0
            self.preferences[preference_type][value] += 1
        else:
            self.preferences[preference_type] = value
        
        self._save_json(self.preferences_file, self.preferences)
    
    def get_preferences(self, preference_type: str = None) -> Dict[str, Any]:
        """Lấy preferences"""
        if preference_type:
            return self.preferences.get(preference_type, {})
        return self.preferences
    
    def record_feedback(self, rating: int, feedback_text: str = "", 
                       interaction_context: Dict[str, Any] = None):
        """Ghi nhận feedback từ user"""
        feedback_entry = {
            "rating": rating,
            "feedback": feedback_text,
            "timestamp": datetime.now().isoformat(),
            "context": interaction_context or {}
        }
        
        self.feedback_history.append(feedback_entry)
        
        # Giới hạn feedback history
        if len(self.feedback_history) > 500:
            self.feedback_history = self.feedback_history[-500:]
        
        # Cập nhật success rate cho patterns liên quan
        if interaction_context and "patterns" in interaction_context:
            for pattern in interaction_context["patterns"]:
                if pattern in self.patterns:
                    self._update_pattern_success_rate(pattern, rating >= 4)
        
        self._save_json(self.feedback_file, self.feedback_history)
    
    def _update_pattern_success_rate(self, pattern: str, success: bool):
        """Cập nhật success rate cho pattern"""
        if pattern not in self.patterns:
            return
        
        current_rate = self.patterns[pattern].get("success_rate", 0)
        count = self.patterns[pattern].get("count", 1)
        
        # Weighted average
        new_rate = (current_rate * (count - 1) + (1 if success else 0)) / count
        self.patterns[pattern]["success_rate"] = new_rate
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Thống kê quá trình học"""
        total_patterns = len(self.patterns)
        total_interactions = len(self.command_history)
        
        # Tính average rating
        if self.feedback_history:
            ratings = [f["rating"] for f in self.feedback_history if "rating" in f]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
        else:
            avg_rating = 0
        
        # Top patterns
        top_patterns = sorted(
            [(pattern, data["count"]) for pattern, data in self.patterns.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_activity = [
            cmd for cmd in self.command_history 
            if datetime.fromisoformat(cmd["timestamp"]) > week_ago
        ]
        
        return {
            "total_patterns_learned": total_patterns,
            "total_interactions": total_interactions,
            "average_rating": round(avg_rating, 2),
            "top_patterns": top_patterns,
            "recent_activity_count": len(recent_activity),
            "feedback_count": len(self.feedback_history)
        }
    
    def adapt_response_style(self, user_input: str) -> Dict[str, Any]:
        """Thích ứng style response dựa trên user preferences"""
        style_preferences = {
            "verbosity": "normal",  # brief, normal, detailed
            "technical_level": "medium",  # basic, medium, advanced
            "tone": "friendly"  # formal, friendly, casual
        }
        
        # Phân tích user input để điều chỉnh style
        user_lower = user_input.lower()
        
        # Detect verbosity preference
        if any(word in user_lower for word in ["chi tiết", "detailed", "explain more"]):
            style_preferences["verbosity"] = "detailed"
        elif any(word in user_lower for word in ["ngắn gọn", "brief", "quick"]):
            style_preferences["verbosity"] = "brief"
        
        # Detect technical level
        if any(word in user_lower for word in ["code", "technical", "kỹ thuật", "lập trình"]):
            style_preferences["technical_level"] = "advanced"
        elif any(word in user_lower for word in ["đơn giản", "simple", "basic"]):
            style_preferences["technical_level"] = "basic"
        
        # Learn từ preferences
        for pref_type, value in style_preferences.items():
            self.learn_preferences(f"response_style_{pref_type}", value)
        
        return style_preferences
    
    def suggest_next_actions(self, current_context: str) -> List[str]:
        """Gợi ý actions tiếp theo dựa trên context"""
        suggestions = []
        
        # Dựa trên command history để tìm patterns sequence
        recent_commands = self.command_history[-10:] if len(self.command_history) > 10 else self.command_history
        
        if recent_commands:
            last_command = recent_commands[-1]
            last_input = last_command["input"].lower()
            
            # Sequence patterns
            if "tạo" in last_input and "file" in last_input:
                suggestions.append("Mở file vừa tạo để chỉnh sửa")
                suggestions.append("Đặt quyền cho file")
            
            elif "copy" in last_input or "sao chép" in last_input:
                suggestions.append("Kiểm tra file đã copy thành công")
                suggestions.append("Mở thư mục đích")
            
            elif "search" in last_input or "tìm" in last_input:
                suggestions.append("Mở file tìm được")
                suggestions.append("Tìm kiếm với từ khóa khác")
        
        return suggestions[:3]  # Giới hạn 3 suggestions