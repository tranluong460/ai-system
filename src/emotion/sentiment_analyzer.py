"""
Sentiment Analysis, Mood Tracking và Mental Health Support
"""
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict

class SentimentAnalyzer:
    """Phân tích cảm xúc từ text"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        print("😊 Sentiment Analyzer initialized")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Phân tích sentiment của text"""
        try:
            # VADER analysis (tốt cho informal text)
            vader_scores = self.vader.polarity_scores(text)
            
            # TextBlob analysis
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Combine scores
            combined_score = (vader_scores['compound'] + textblob_polarity) / 2
            
            # Determine overall sentiment
            if combined_score >= 0.1:
                overall_sentiment = "positive"
            elif combined_score <= -0.1:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            # Emotion detection (simple version)
            emotions = self._detect_emotions(text.lower())
            
            return {
                "overall_sentiment": overall_sentiment,
                "combined_score": combined_score,
                "vader": {
                    "compound": vader_scores['compound'],
                    "positive": vader_scores['pos'],
                    "negative": vader_scores['neg'],
                    "neutral": vader_scores['neu']
                },
                "textblob": {
                    "polarity": textblob_polarity,
                    "subjectivity": textblob_subjectivity
                },
                "emotions": emotions,
                "confidence": abs(combined_score)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect basic emotions từ keywords"""
        emotion_keywords = {
            "joy": ["happy", "vui", "vẻ", "hạnh phúc", "excited", "great", "awesome", "love", "yêu"],
            "sadness": ["sad", "buồn", "cry", "khóc", "depressed", "upset", "down"],
            "anger": ["angry", "giận", "mad", "furious", "hate", "ghét", "annoyed"],
            "fear": ["scared", "sợ", "afraid", "worry", "lo lắng", "anxious", "nervous"],
            "surprise": ["surprised", "ngạc nhiên", "wow", "amazing", "unexpected"],
            "disgust": ["disgusting", "kinh tởm", "gross", "awful", "terrible"]
        }
        
        emotions = {}
        words = text.split()
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for word in words if any(kw in word for kw in keywords))
            emotions[emotion] = count / len(words) if words else 0
        
        return emotions

class MoodTracker:
    """Theo dõi mood theo thời gian"""
    
    def __init__(self, data_dir: str = "data/mood"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.mood_file = os.path.join(data_dir, "mood_history.json")
        self.mood_history = self._load_mood_history()
        
        self.sentiment_analyzer = SentimentAnalyzer()
        print("📈 Mood Tracker initialized")
    
    def _load_mood_history(self) -> List[Dict[str, Any]]:
        """Load mood history"""
        try:
            if os.path.exists(self.mood_file):
                with open(self.mood_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading mood history: {e}")
        return []
    
    def _save_mood_history(self):
        """Lưu mood history"""
        try:
            with open(self.mood_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving mood history: {e}")
    
    def record_mood(self, text: str, manual_rating: int = None, context: str = "") -> Dict[str, Any]:
        """Ghi nhận mood từ text hoặc manual rating"""
        sentiment = self.sentiment_analyzer.analyze_sentiment(text)
        
        # Convert sentiment score to 1-10 scale
        auto_rating = int((sentiment.get("combined_score", 0) + 1) * 5)  # -1 to 1 -> 0 to 10
        auto_rating = max(1, min(10, auto_rating))
        
        mood_entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "context": context,
            "auto_rating": auto_rating,
            "manual_rating": manual_rating,
            "final_rating": manual_rating if manual_rating else auto_rating,
            "sentiment": sentiment,
            "emotions": sentiment.get("emotions", {})
        }
        
        self.mood_history.append(mood_entry)
        self._save_mood_history()
        
        return mood_entry
    
    def get_mood_trends(self, days: int = 30) -> Dict[str, Any]:
        """Phân tích xu hướng mood"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_moods = []
        for entry in self.mood_history:
            try:
                entry_date = datetime.fromisoformat(entry["timestamp"])
                if entry_date >= cutoff_date:
                    recent_moods.append(entry)
            except:
                continue
        
        if not recent_moods:
            return {"message": "Không có dữ liệu mood trong khoảng thời gian này"}
        
        # Calculate trends
        ratings = [entry["final_rating"] for entry in recent_moods]
        
        # Daily averages
        daily_moods = defaultdict(list)
        for entry in recent_moods:
            date = entry["timestamp"][:10]  # YYYY-MM-DD
            daily_moods[date].append(entry["final_rating"])
        
        daily_averages = {date: np.mean(ratings) for date, ratings in daily_moods.items()}
        
        # Overall statistics
        avg_mood = np.mean(ratings)
        mood_variance = np.var(ratings)
        
        # Trend direction (last 7 days vs previous 7 days)
        if len(ratings) >= 14:
            recent_week = ratings[-7:]
            previous_week = ratings[-14:-7]
            trend = np.mean(recent_week) - np.mean(previous_week)
        else:
            trend = 0
        
        # Dominant emotions
        all_emotions = defaultdict(list)
        for entry in recent_moods:
            for emotion, score in entry.get("emotions", {}).items():
                all_emotions[emotion].append(score)
        
        avg_emotions = {emotion: np.mean(scores) for emotion, scores in all_emotions.items()}
        dominant_emotion = max(avg_emotions.items(), key=lambda x: x[1])[0] if avg_emotions else "neutral"
        
        return {
            "period_days": days,
            "total_entries": len(recent_moods),
            "average_mood": round(avg_mood, 1),
            "mood_stability": round(10 - mood_variance, 1),  # Higher = more stable
            "trend": "improving" if trend > 0.5 else "declining" if trend < -0.5 else "stable",
            "trend_value": round(trend, 2),
            "dominant_emotion": dominant_emotion,
            "daily_averages": daily_averages,
            "emotions_avg": avg_emotions
        }
    
    def get_mood_insights(self) -> List[str]:
        """Đưa ra insights về mood"""
        trends = self.get_mood_trends(30)
        insights = []
        
        if trends.get("average_mood", 5) >= 7:
            insights.append("🌟 Mood của bạn nhìn chung khá tích cực!")
        elif trends.get("average_mood", 5) <= 4:
            insights.append("😔 Mood của bạn có vẻ thấp, hãy chăm sóc bản thân nhé.")
        
        if trends.get("mood_stability", 5) >= 7:
            insights.append("📊 Mood của bạn khá ổn định.")
        else:
            insights.append("🌊 Mood của bạn có nhiều biến động.")
        
        if trends.get("trend") == "improving":
            insights.append("📈 Mood của bạn đang cải thiện!")
        elif trends.get("trend") == "declining":
            insights.append("📉 Mood của bạn có xu hướng giảm, hãy cẩn thận.")
        
        dominant_emotion = trends.get("dominant_emotion", "")
        if dominant_emotion == "joy":
            insights.append("😊 Bạn thường xuyên cảm thấy vui vẻ.")
        elif dominant_emotion == "sadness":
            insights.append("😢 Bạn có vẻ buồn khá nhiều gần đây.")
        elif dominant_emotion == "anger":
            insights.append("😠 Bạn có dấu hiệu tức giận, hãy tìm cách thư giãn.")
        
        return insights

class MentalHealthSupport:
    """Mental Health Support System"""
    
    def __init__(self, mood_tracker: MoodTracker):
        self.mood_tracker = mood_tracker
        
        # Cơ sở dữ liệu câu trả lời hỗ trợ
        self.support_responses = {
            "low_mood": [
                "Tôi hiểu bạn đang cảm thấy không tốt. Hãy nhớ rằng cảm xúc này sẽ qua đi.",
                "Có thể bạn cần nghỉ ngơi một chút? Thử nghe nhạc hoặc đi dạo nhé.",
                "Bạn có muốn chia sẻ thêm về điều gì đang làm bạn buồn không?"
            ],
            "high_stress": [
                "Tôi cảm nhận được bạn đang stress. Hãy thử hít thở sâu 3 lần.",
                "Khi stress, việc viết ra những gì bạn đang nghĩ có thể giúp ích.",
                "Hãy tạm dừng công việc và làm gì đó bạn thích trong 10 phút."
            ],
            "anxiety": [
                "Cảm giác lo lắng rất bình thường. Hãy tập trung vào hiện tại.",
                "Thử kỹ thuật 5-4-3-2-1: 5 thứ bạn thấy, 4 thứ bạn chạm, 3 thứ bạn nghe, 2 thứ bạn ngửi, 1 thứ bạn nếm.",
                "Lo lắng thường về những điều chưa xảy ra. Hãy tập trung vào những gì bạn có thể kiểm soát."
            ],
            "anger": [
                "Tôi hiểu bạn đang tức giận. Hãy đếm từ 1 đến 10 trước khi phản ứng.",
                "Cơn giận sẽ qua đi. Hãy tìm cách giải tỏa năng lượng này một cách tích cực.",
                "Có điều gì cụ thể làm bạn tức giận? Có thể chúng ta tìm cách giải quyết."
            ],
            "positive": [
                "Tuyệt vời! Tôi vui khi thấy bạn có tâm trạng tốt.",
                "Hãy ghi nhớ cảm giác tích cực này và những gì đã tạo ra nó.",
                "Năng lượng tích cực của bạn có thể lan tỏa đến những người xung quanh đó!"
            ]
        }
        
        print("💚 Mental Health Support initialized")
    
    def provide_support(self, text: str, context: str = "") -> Dict[str, Any]:
        """Đưa ra support dựa trên sentiment và context"""
        sentiment = self.mood_tracker.sentiment_analyzer.analyze_sentiment(text)
        
        # Phân loại tình trạng
        support_type = self._classify_mental_state(sentiment, text.lower())
        
        # Lấy response phù hợp
        responses = self.support_responses.get(support_type, ["Tôi ở đây để lắng nghe bạn."])
        response = np.random.choice(responses)
        
        # Thêm coping strategies nếu cần
        coping_strategies = self._get_coping_strategies(support_type)
        
        # Đánh giá mức độ nghiêm trọng
        severity = self._assess_severity(sentiment, text.lower())
        
        support_response = {
            "support_type": support_type,
            "response": response,
            "coping_strategies": coping_strategies,
            "severity": severity,
            "sentiment_analysis": sentiment
        }
        
        # Nếu nghiêm trọng, đề xuất tìm kiếm hỗ trợ chuyên nghiệp
        if severity == "high":
            support_response["professional_help_suggestion"] = \
                "Nếu cảm xúc này kéo dài, bạn nên tìm kiếm sự hỗ trợ từ chuyên gia tâm lý."
        
        return support_response
    
    def _classify_mental_state(self, sentiment: Dict[str, Any], text: str) -> str:
        """Phân loại tình trạng tâm lý"""
        score = sentiment.get("combined_score", 0)
        emotions = sentiment.get("emotions", {})
        
        # Check for specific keywords
        if any(word in text for word in ["stress", "căng thẳng", "áp lực", "overwhelmed"]):
            return "high_stress"
        
        if any(word in text for word in ["lo lắng", "anxiety", "worry", "nervous", "sợ"]):
            return "anxiety"
        
        if any(word in text for word in ["giận", "angry", "mad", "furious", "tức"]):
            return "anger"
        
        # Based on sentiment score
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "low_mood"
        
        # Based on dominant emotion
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            if dominant_emotion == "sadness":
                return "low_mood"
            elif dominant_emotion == "anger":
                return "anger"
            elif dominant_emotion == "fear":
                return "anxiety"
            elif dominant_emotion == "joy":
                return "positive"
        
        return "neutral"
    
    def _get_coping_strategies(self, support_type: str) -> List[str]:
        """Lấy coping strategies"""
        strategies = {
            "low_mood": [
                "Đi dạo ngoài trời 15 phút",
                "Gọi điện cho bạn bè hoặc gia đình",
                "Viết nhật ký cảm xúc",
                "Nghe nhạc yêu thích",
                "Tập thể dục nhẹ"
            ],
            "high_stress": [
                "Tập hít thở sâu (4-7-8)",
                "Meditation 10 phút",
                "Lập danh sách công việc ưu tiên",
                "Nghỉ ngơi ngắn",
                "Tập yoga hoặc stretching"
            ],
            "anxiety": [
                "Kỹ thuật grounding 5-4-3-2-1",
                "Progressive muscle relaxation",
                "Tập trung vào hiện tại",
                "Viết ra những lo lắng",
                "Tập thể dục aerobic nhẹ"
            ],
            "anger": [
                "Đếm chậm từ 1 đến 10",
                "Rời khỏi tình huống tạm thời",
                "Tập thể dục cường độ cao",
                "Viết thư giận dữ (không gửi)",
                "Nghe nhạc thư giãn"
            ],
            "positive": [
                "Chia sẻ niềm vui với người khác",
                "Ghi lại khoảnh khắc tích cực",
                "Làm điều tốt cho người khác",
                "Lập kế hoạch cho mục tiêu mới"
            ]
        }
        
        return strategies.get(support_type, [])
    
    def _assess_severity(self, sentiment: Dict[str, Any], text: str) -> str:
        """Đánh giá mức độ nghiêm trọng"""
        score = sentiment.get("combined_score", 0)
        
        # Keywords indicating high severity
        high_severity_keywords = [
            "không thể", "muốn chết", "vô vọng", "tuyệt vọng", 
            "không còn ý nghĩa", "cant go on", "hopeless"
        ]
        
        if any(keyword in text for keyword in high_severity_keywords):
            return "high"
        
        if score <= -0.7:
            return "high"
        elif score <= -0.4:
            return "medium"
        else:
            return "low"
    
    def get_wellness_tips(self) -> List[str]:
        """Đưa ra wellness tips hàng ngày"""
        tips = [
            "💧 Nhớ uống đủ nước trong ngày",
            "🌅 Thức dậy sớm và hít thở không khí trong lành",
            "📱 Hạn chế thời gian sử dụng điện thoại trước khi ngủ",
            "🥗 Ăn nhiều rau xanh và trái cây",
            "😴 Đảm bảo ngủ đủ 7-8 tiếng mỗi đêm",
            "🚶 Đi bộ ít nhất 30 phút mỗi ngày",
            "🧘 Dành 10 phút mỗi ngày để meditation",
            "📚 Đọc sách thay vì xem TV",
            "💝 Thể hiện lòng biết ơn với những điều tốt đẹp",
            "🎨 Tìm một sở thích mới để phát triển"
        ]
        
        return np.random.choice(tips, size=3, replace=False).tolist()