"""
Feedback processing system for improving AI responses
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.error_handler import ErrorHandler

class FeedbackProcessor:
    """Process user feedback to improve AI response quality"""
    
    def __init__(self, data_dir: str = "data/feedback"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.feedback_file = os.path.join(data_dir, "response_feedback.json")
        self.patterns_file = os.path.join(data_dir, "learned_patterns.json")
        
        self.feedback_history = self._load_feedback_history()
        self.learned_patterns = self._load_learned_patterns()
        
        self.error_handler = ErrorHandler("feedback_processor")
    
    def _load_feedback_history(self) -> List[Dict[str, Any]]:
        """Load feedback history"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.error_handler.logger.error(f"Failed to load feedback: {e}")
        return []
    
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load learned response patterns"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.error_handler.logger.error(f"Failed to load patterns: {e}")
        return {
            "good_patterns": [],
            "bad_patterns": [],
            "style_preferences": {
                "response_length": "medium",  # short, medium, long
                "technical_detail": "medium", # low, medium, high
                "code_explanation": "brief"   # none, brief, detailed
            }
        }
    
    def _save_feedback_history(self):
        """Save feedback history"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.error_handler.logger.error(f"Failed to save feedback: {e}")
    
    def _save_learned_patterns(self):
        """Save learned patterns"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.error_handler.logger.error(f"Failed to save patterns: {e}")
    
    def record_feedback(self, user_input: str, ai_response: str, 
                       rating: int, comment: str = "") -> None:
        """Record user feedback and learn from it"""
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "rating": rating,
            "comment": comment,
            "response_analysis": self._analyze_response(ai_response),
            "user_input_analysis": self._analyze_user_input(user_input)
        }
        
        self.feedback_history.append(feedback_entry)
        
        # Learn from feedback
        self._learn_from_feedback(feedback_entry)
        
        # Save data
        self._save_feedback_history()
        self._save_learned_patterns()
        
        self.error_handler.log_user_action("feedback_recorded", f"rating: {rating}")
    
    def _analyze_response(self, ai_response: str) -> Dict[str, Any]:
        """Analyze AI response characteristics"""
        # Ensure ai_response is string
        if not isinstance(ai_response, str):
            ai_response = str(ai_response)
        
        analysis = {
            "length": len(ai_response),
            "word_count": len(ai_response.split()),
            "has_code": "```" in ai_response,
            "has_execution_results": "🔧 Execution Results:" in ai_response,
            "response_type": "unknown"
        }
        
        # Classify response type
        if analysis["has_code"]:
            analysis["response_type"] = "code_execution"
        elif len(ai_response.split()) < 10:
            analysis["response_type"] = "brief_answer"
        elif len(ai_response.split()) > 50:
            analysis["response_type"] = "detailed_explanation"
        else:
            analysis["response_type"] = "standard_response"
        
        return analysis
    
    def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to understand intent"""
        # Ensure user_input is string
        if not isinstance(user_input, str):
            user_input = str(user_input)
            
        analysis = {
            "length": len(user_input),
            "word_count": len(user_input.split()),
            "question_type": "unknown"
        }
        
        user_lower = user_input.lower()
        
        # Classify question type
        if any(word in user_lower for word in ['có', 'không', 'yes', 'no']):
            analysis["question_type"] = "yes_no"
        elif any(word in user_lower for word in ['tìm', 'find', 'search']):
            analysis["question_type"] = "search"
        elif any(word in user_lower for word in ['tạo', 'create', 'make']):
            analysis["question_type"] = "creation"
        elif any(word in user_lower for word in ['là gì', 'what is', 'explain']):
            analysis["question_type"] = "explanation"
        
        return analysis
    
    def _learn_from_feedback(self, feedback_entry: Dict[str, Any]):
        """Learn patterns from feedback"""
        rating = feedback_entry["rating"]
        comment = feedback_entry["comment"].lower()
        response_analysis = feedback_entry["response_analysis"]
        input_analysis = feedback_entry["user_input_analysis"]
        
        # Learn from good responses (rating 4-5)
        if rating >= 4:
            pattern = {
                "response_type": response_analysis["response_type"],
                "question_type": input_analysis["question_type"],
                "characteristics": {
                    "length": response_analysis["length"],
                    "has_code": response_analysis["has_code"]
                },
                "feedback": comment,
                "timestamp": feedback_entry["timestamp"]
            }
            self.learned_patterns["good_patterns"].append(pattern)
        
        # Learn from bad responses (rating 1-2)
        elif rating <= 2:
            pattern = {
                "response_type": response_analysis["response_type"],
                "question_type": input_analysis["question_type"],
                "issues": self._extract_issues_from_comment(comment),
                "feedback": comment,
                "timestamp": feedback_entry["timestamp"]
            }
            self.learned_patterns["bad_patterns"].append(pattern)
        
        # Update style preferences based on feedback
        self._update_style_preferences(comment, rating)
    
    def _extract_issues_from_comment(self, comment: str) -> List[str]:
        """Extract specific issues from feedback comment"""
        issues = []
        
        issue_keywords = {
            "too_long": ["dài", "long", "verbose", "quá nhiều"],
            "too_short": ["ngắn", "short", "brief", "thiếu"],
            "code_error": ["lỗi", "error", "syntax", "không chạy"],
            "wrong_answer": ["sai", "wrong", "incorrect", "không đúng"],
            "irrelevant": ["không liên quan", "irrelevant", "off-topic"]
        }
        
        for issue, keywords in issue_keywords.items():
            if any(keyword in comment for keyword in keywords):
                issues.append(issue)
        
        return issues
    
    def _update_style_preferences(self, comment: str, rating: int):
        """Update style preferences based on feedback"""
        preferences = self.learned_patterns["style_preferences"]
        
        # Length preferences
        if rating <= 2:
            if any(word in comment for word in ["dài", "long", "verbose"]):
                if preferences["response_length"] == "long":
                    preferences["response_length"] = "medium"
                elif preferences["response_length"] == "medium":
                    preferences["response_length"] = "short"
            elif any(word in comment for word in ["ngắn", "short", "thiếu"]):
                if preferences["response_length"] == "short":
                    preferences["response_length"] = "medium"
                elif preferences["response_length"] == "medium":
                    preferences["response_length"] = "long"
        
        # Technical detail preferences
        if rating >= 4:
            if any(word in comment for word in ["chi tiết", "detailed", "explain more"]):
                preferences["technical_detail"] = "high"
            elif any(word in comment for word in ["ngắn gọn", "concise", "brief"]):
                preferences["technical_detail"] = "low"
    
    def get_response_guidance(self, user_input: str) -> Dict[str, Any]:
        """Get guidance for generating appropriate response"""
        input_analysis = self._analyze_user_input(user_input)
        question_type = input_analysis["question_type"]
        
        # Find relevant patterns
        good_patterns = [p for p in self.learned_patterns["good_patterns"] 
                        if p["question_type"] == question_type]
        bad_patterns = [p for p in self.learned_patterns["bad_patterns"] 
                       if p["question_type"] == question_type]
        
        guidance = {
            "preferred_style": self.learned_patterns["style_preferences"].copy(),
            "question_type": question_type,
            "recommendations": [],
            "avoid": []
        }
        
        # Add specific recommendations based on patterns
        if good_patterns:
            latest_good = good_patterns[-1]  # Most recent good pattern
            guidance["recommendations"].append(f"Use {latest_good['response_type']} style")
            
            if latest_good["characteristics"]["has_code"]:
                guidance["recommendations"].append("Include executable code")
            else:
                guidance["recommendations"].append("Provide direct answer without code")
        
        if bad_patterns:
            for bad_pattern in bad_patterns[-3:]:  # Recent bad patterns
                for issue in bad_pattern["issues"]:
                    guidance["avoid"].append(issue)
        
        # Special handling for yes/no questions
        if question_type == "yes_no":
            guidance["recommendations"].append("Start with clear yes/no answer")
            guidance["preferred_style"]["response_length"] = "short"
        
        return guidance
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        if not self.feedback_history:
            return {"message": "No feedback data available"}
        
        ratings = [f["rating"] for f in self.feedback_history]
        
        return {
            "total_feedback": len(self.feedback_history),
            "average_rating": sum(ratings) / len(ratings),
            "rating_distribution": {
                i: ratings.count(i) for i in range(1, 6)
            },
            "good_patterns_learned": len(self.learned_patterns["good_patterns"]),
            "bad_patterns_learned": len(self.learned_patterns["bad_patterns"]),
            "current_preferences": self.learned_patterns["style_preferences"]
        }