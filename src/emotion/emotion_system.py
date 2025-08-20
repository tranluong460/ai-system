"""
Emotion System tích hợp Sentiment Analysis, Mood Tracking, Mental Health Support
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from .sentiment_analyzer import SentimentAnalyzer, MoodTracker, MentalHealthSupport

class EmotionSystem:
    """Hệ thống emotion tích hợp sentiment, mood, mental health"""
    
    def __init__(self, data_dir: str = "data/emotion"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        print("💚 Initializing Emotion System...")
        
        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.mood_tracker = MoodTracker(f"{data_dir}/mood")
        self.mental_health = MentalHealthSupport(self.mood_tracker)
        
        # Emotion alerts
        self.alert_callbacks = []
        
        # Empathy settings
        self.empathy_settings = self._load_empathy_settings()
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        print("✅ Emotion System ready!")
    
    def _load_empathy_settings(self) -> Dict[str, Any]:
        """Load empathy settings"""
        settings_file = os.path.join(self.data_dir, "empathy_settings.json")
        
        default_settings = {
            "empathy_level": "medium",  # low, medium, high
            "proactive_support": True,
            "mood_alert_threshold": 3.0,  # Below this for 3 days = alert
            "crisis_keywords": [
                "muốn chết", "tự tử", "không còn ý nghĩa", "tuyệt vọng",
                "want to die", "suicide", "hopeless", "end it all"
            ],
            "response_personalization": True
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except Exception as e:
            print(f"⚠️ Error loading empathy settings: {e}")
        
        return default_settings
    
    def _save_empathy_settings(self):
        """Save empathy settings"""
        settings_file = os.path.join(self.data_dir, "empathy_settings.json")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.empathy_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving empathy settings: {e}")
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load empathetic response templates"""
        return {
            "low_mood": {
                "low": ["Tôi hiểu bạn đang cảm thấy không tốt."],
                "medium": [
                    "Tôi thấy bạn có vẻ buồn. Tôi ở đây để lắng nghe bạn.",
                    "Cảm xúc này sẽ qua đi. Bạn có muốn chia sẻ thêm không?",
                    "Tôi hiểu đây là lúc khó khăn với bạn. Hãy để tôi hỗ trợ bạn."
                ],
                "high": [
                    "Tôi cảm nhận được nỗi buồn trong lời bạn và thật sự quan tâm đến cảm xúc của bạn.",
                    "Những lúc như này thật khó khăn, nhưng bạn không đơn độc. Tôi ở đây cùng bạn.",
                    "Tôi thấy bạn đang trải qua khoảng thời gian khó khăn. Cảm xúc của bạn hoàn toàn có ý nghĩa."
                ]
            },
            "anxiety": {
                "low": ["Hãy thử hít thở sâu."],
                "medium": [
                    "Lo lắng là cảm xúc bình thường. Hãy tập trung vào hiện tại.",
                    "Tôi hiểu bạn đang lo lắng. Hãy thử kỹ thuật thở 4-7-8.",
                    "Cảm giác này sẽ qua đi. Bạn đã vượt qua nhiều khó khăn trước đây rồi."
                ],
                "high": [
                    "Tôi cảm nhận được sự lo lắng trong bạn. Điều này hoàn toàn có thể hiểu được.",
                    "Lo lắng có thể rất áp đảo, nhưng hãy nhớ rằng đây chỉ là cảm xúc tạm thời.",
                    "Tôi ở đây để hỗ trợ bạn vượt qua cảm giác lo lắng này. Hãy từ từ và nhẹ nhàng với bản thân."
                ]
            },
            "anger": {
                "low": ["Hãy bình tĩnh."],
                "medium": [
                    "Tôi hiểu bạn đang tức giận. Hãy thử đếm từ 1 đến 10.",
                    "Cơn giận sẽ qua đi. Hãy tìm cách giải tỏa tích cực.",
                    "Có điều gì làm bạn tức giận? Có thể chúng ta tìm cách giải quyết."
                ],
                "high": [
                    "Tôi thấy bạn đang rất tức giận và điều đó hoàn toàn có thể hiểu được.",
                    "Cơn giận là phản ứng tự nhiên. Hãy để tôi giúp bạn tìm cách xử lý cảm xúc này.",
                    "Tôi cảm nhận được sự bực bội trong bạn. Hãy cùng tìm cách giải quyết vấn đề này."
                ]
            },
            "positive": {
                "low": ["Tốt!"],
                "medium": [
                    "Tuyệt vời! Tôi vui khi thấy bạn có tâm trạng tốt.",
                    "Năng lượng tích cực của bạn thật tuyệt!",
                    "Hãy ghi nhớ cảm giác tốt này!"
                ],
                "high": [
                    "Thật tuyệt vời khi thấy bạn hạnh phúc! Niềm vui của bạn khiến tôi cũng cảm thấy vui vẻ.",
                    "Tôi thật sự hạnh phúc khi thấy bạn có tâm trạng tích cực như vậy!",
                    "Năng lượng tích cực này thật đáng quý. Hãy để nó lan tỏa đến những người xung quanh bạn!"
                ]
            }
        }
    
    def analyze_conversation_emotion(self, user_input: str, context: str = "") -> Dict[str, Any]:
        """Phân tích emotion từ conversation"""
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(user_input)
        
        # Check for crisis keywords
        crisis_detected = any(
            keyword in user_input.lower() 
            for keyword in self.empathy_settings["crisis_keywords"]
        )
        
        # Record mood
        mood_entry = self.mood_tracker.record_mood(user_input, context=context)
        
        # Get mental health support
        support = self.mental_health.provide_support(user_input, context)
        
        # Generate empathetic response
        empathetic_response = self._generate_empathetic_response(sentiment, support["support_type"])
        
        # Check for alerts
        self._check_emotional_alerts(sentiment, crisis_detected)
        
        return {
            "sentiment": sentiment,
            "mood_entry": mood_entry,
            "support": support,
            "empathetic_response": empathetic_response,
            "crisis_detected": crisis_detected,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _generate_empathetic_response(self, sentiment: Dict[str, Any], 
                                    support_type: str) -> Dict[str, Any]:
        """Tạo empathetic response"""
        empathy_level = self.empathy_settings["empathy_level"]
        
        # Determine response category
        response_category = support_type
        if response_category not in self.response_templates:
            response_category = "positive" if sentiment.get("combined_score", 0) > 0 else "low_mood"
        
        # Get templates for this category and empathy level
        templates = self.response_templates.get(response_category, {}).get(empathy_level, [])
        
        if not templates:
            templates = ["Tôi hiểu cảm xúc của bạn."]
        
        # Select response based on context
        selected_response = np.random.choice(templates)
        
        # Add personalization if enabled
        if self.empathy_settings["response_personalization"]:
            selected_response = self._personalize_response(selected_response, sentiment)
        
        return {
            "response": selected_response,
            "empathy_level": empathy_level,
            "category": response_category,
            "confidence": sentiment.get("confidence", 0.5)
        }
    
    def _personalize_response(self, response: str, sentiment: Dict[str, Any]) -> str:
        """Personalize response dựa trên sentiment details"""
        # Add emotional validation
        emotions = sentiment.get("emotions", {})
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            
            if dominant_emotion == "sadness" and "buồn" not in response:
                response += " Tôi cảm nhận được nỗi buồn trong bạn."
            elif dominant_emotion == "fear" and "lo lắng" not in response:
                response += " Tôi hiểu bạn đang cảm thấy bất an."
        
        return response
    
    def _check_emotional_alerts(self, sentiment: Dict[str, Any], crisis_detected: bool):
        """Kiểm tra và gửi emotional alerts"""
        # Crisis alert
        if crisis_detected:
            self._send_alert({
                "type": "crisis",
                "severity": "high",
                "message": "Crisis keywords detected in conversation",
                "timestamp": datetime.now().isoformat(),
                "sentiment": sentiment
            })
        
        # Low mood pattern alert
        if self.empathy_settings["proactive_support"]:
            mood_trends = self.mood_tracker.get_mood_trends(7)  # Last 7 days
            
            if mood_trends.get("average_mood", 5) < self.empathy_settings["mood_alert_threshold"]:
                self._send_alert({
                    "type": "low_mood_pattern",
                    "severity": "medium",
                    "message": f"Low mood pattern detected. Average: {mood_trends.get('average_mood', 0):.1f}",
                    "timestamp": datetime.now().isoformat(),
                    "mood_trends": mood_trends
                })
    
    def _send_alert(self, alert: Dict[str, Any]):
        """Gửi emotional alert"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"❌ Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Thêm alert callback"""
        self.alert_callbacks.append(callback)
    
    def generate_mood_visualization(self, days: int = 30, save_path: str = None) -> str:
        """Tạo visualization cho mood trends"""
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.data_dir, f"mood_chart_{timestamp}.png")
        
        try:
            # Get mood data
            cutoff_date = datetime.now() - timedelta(days=days)
            mood_data = []
            
            for entry in self.mood_tracker.mood_history:
                try:
                    entry_date = datetime.fromisoformat(entry["timestamp"])
                    if entry_date >= cutoff_date:
                        mood_data.append({
                            "date": entry_date.date(),
                            "rating": entry["final_rating"],
                            "sentiment_score": entry.get("sentiment", {}).get("combined_score", 0)
                        })
                except:
                    continue
            
            if not mood_data:
                return ""
            
            # Group by date and calculate daily averages
            daily_moods = {}
            for entry in mood_data:
                date = entry["date"]
                if date not in daily_moods:
                    daily_moods[date] = []
                daily_moods[date].append(entry["rating"])
            
            # Calculate averages
            dates = sorted(daily_moods.keys())
            avg_moods = [np.mean(daily_moods[date]) for date in dates]
            
            # Create visualization
            plt.figure(figsize=(12, 6))
            
            # Plot mood trend
            plt.subplot(1, 2, 1)
            plt.plot(dates, avg_moods, marker='o', linewidth=2, markersize=4)
            plt.title(f'Mood Trends - Last {days} Days')
            plt.xlabel('Date')
            plt.ylabel('Mood Rating (1-10)')
            plt.ylim(1, 10)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Add mood zone colors
            plt.axhspan(1, 4, alpha=0.2, color='red', label='Low')
            plt.axhspan(4, 7, alpha=0.2, color='yellow', label='Medium')
            plt.axhspan(7, 10, alpha=0.2, color='green', label='Good')
            plt.legend()
            
            # Plot emotion distribution
            plt.subplot(1, 2, 2)
            all_emotions = {"joy": [], "sadness": [], "anger": [], "fear": [], "surprise": []}
            
            for entry in mood_data:
                emotions = entry.get("emotions", {})
                for emotion in all_emotions.keys():
                    all_emotions[emotion].append(emotions.get(emotion, 0))
            
            emotion_avgs = {k: np.mean(v) if v else 0 for k, v in all_emotions.items()}
            
            colors = ['gold', 'lightblue', 'lightcoral', 'lightgray', 'lightgreen']
            plt.pie(emotion_avgs.values(), labels=emotion_avgs.keys(), colors=colors, autopct='%1.1f%%')
            plt.title('Emotion Distribution')
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            return ""
    
    def get_wellness_recommendations(self) -> Dict[str, Any]:
        """Đưa ra wellness recommendations dựa trên mood patterns"""
        mood_trends = self.mood_tracker.get_mood_trends(30)
        insights = self.mood_tracker.get_mood_insights()
        wellness_tips = self.mental_health.get_wellness_tips()
        
        recommendations = {
            "immediate_actions": [],
            "weekly_goals": [],
            "long_term_strategies": [],
            "emergency_resources": []
        }
        
        avg_mood = mood_trends.get("average_mood", 5)
        mood_stability = mood_trends.get("mood_stability", 5)
        
        # Immediate actions based on current mood
        if avg_mood < 4:
            recommendations["immediate_actions"].extend([
                "🌅 Dành 10 phút mỗi sáng để meditation",
                "📱 Hạn chế social media trong 1-2 ngày",
                "🚶 Đi dạo ngoài trời ít nhất 20 phút",
                "☎️ Gọi điện cho một người bạn thân"
            ])
        elif avg_mood > 7:
            recommendations["immediate_actions"].extend([
                "📝 Viết nhật ký về những điều tích cực hôm nay",
                "🎯 Đặt một mục tiêu nhỏ cho ngày mai",
                "💝 Làm điều tốt cho ai đó"
            ])
        
        # Weekly goals based on stability
        if mood_stability < 5:
            recommendations["weekly_goals"].extend([
                "🕐 Tạo routine hàng ngày và tuân thủ",
                "😴 Đảm bảo ngủ đúng giờ mỗi đêm",
                "🥗 Ăn uống đều đặn và lành mạnh"
            ])
        
        # Long-term strategies
        recommendations["long_term_strategies"].extend([
            "📚 Học kỹ năng quản lý stress",
            "🏃 Tham gia hoạt động thể thao đều đặn",
            "🧘 Thực hành mindfulness hàng ngày",
            "👥 Xây dựng mạng lưới hỗ trợ xã hội"
        ])
        
        # Emergency resources
        recommendations["emergency_resources"] = [
            "Hotline tâm lý: 1800-1567",
            "Trung tâm tư vấn tâm lý: 028-xxx-xxxx",
            "Website hỗ trợ: mentalhealth.gov",
            "App meditation: Headspace, Calm"
        ]
        
        return {
            "recommendations": recommendations,
            "mood_summary": mood_trends,
            "insights": insights,
            "wellness_tips": wellness_tips
        }
    
    def export_emotion_report(self, days: int = 30) -> str:
        """Export emotion report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.data_dir, f"emotion_report_{timestamp}.json")
        
        try:
            # Generate mood chart
            chart_path = self.generate_mood_visualization(days)
            
            # Compile report data
            report = {
                "report_date": datetime.now().isoformat(),
                "analysis_period_days": days,
                "mood_trends": self.mood_tracker.get_mood_trends(days),
                "mood_insights": self.mood_tracker.get_mood_insights(),
                "wellness_recommendations": self.get_wellness_recommendations(),
                "emotion_settings": self.empathy_settings,
                "mood_chart_path": chart_path,
                "statistics": {
                    "total_mood_entries": len(self.mood_tracker.mood_history),
                    "empathy_level": self.empathy_settings["empathy_level"],
                    "proactive_support_enabled": self.empathy_settings["proactive_support"]
                }
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return report_path
            
        except Exception as e:
            print(f"❌ Export error: {e}")
            return ""
    
    def update_empathy_settings(self, new_settings: Dict[str, Any]):
        """Update empathy settings"""
        self.empathy_settings.update(new_settings)
        self._save_empathy_settings()
        print("💚 Empathy settings updated")
    
    def get_emotion_stats(self) -> Dict[str, Any]:
        """Lấy emotion system statistics"""
        mood_trends = self.mood_tracker.get_mood_trends(30)
        
        return {
            "total_mood_entries": len(self.mood_tracker.mood_history),
            "current_mood_trend": mood_trends.get("trend", "stable"),
            "average_mood_30days": mood_trends.get("average_mood", 5),
            "mood_stability": mood_trends.get("mood_stability", 5),
            "dominant_emotion": mood_trends.get("dominant_emotion", "neutral"),
            "empathy_level": self.empathy_settings["empathy_level"],
            "proactive_support": self.empathy_settings["proactive_support"],
            "last_mood_entry": self.mood_tracker.mood_history[-1]["timestamp"] if self.mood_tracker.mood_history else None
        }