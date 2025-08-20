"""
Machine Learning & Personalization Engine
"""
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle

class ReinforcementLearningSystem:
    """Reinforcement Learning cho response optimization"""
    
    def __init__(self, data_dir: str = "data/ml"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.feedback_file = os.path.join(data_dir, "rl_feedback.json")
        self.model_file = os.path.join(data_dir, "rl_model.pkl")
        
        # Feedback data
        self.feedback_data = self._load_feedback_data()
        
        # Q-learning parameters
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # Exploration rate
        
        # Action-reward mapping
        self.actions = [
            "detailed_response", "concise_response", "empathetic_response",
            "technical_response", "creative_response", "helpful_response"
        ]
        
        print("🧠 Reinforcement Learning System initialized")
    
    def _load_feedback_data(self) -> List[Dict[str, Any]]:
        """Load feedback data"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading RL feedback: {e}")
        return []
    
    def _save_feedback_data(self):
        """Save feedback data"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving RL feedback: {e}")
    
    def _extract_state_features(self, context: Dict[str, Any]) -> str:
        """Extract state từ context"""
        features = []
        
        # User input length
        user_input = context.get("user_input", "")
        if len(user_input) < 20:
            features.append("short_query")
        elif len(user_input) > 100:
            features.append("long_query")
        else:
            features.append("medium_query")
        
        # Question type
        if "?" in user_input:
            features.append("question")
        elif any(word in user_input.lower() for word in ["help", "how", "giúp"]):
            features.append("help_request")
        elif any(word in user_input.lower() for word in ["explain", "giải thích"]):
            features.append("explanation_request")
        
        # Sentiment context
        sentiment = context.get("sentiment", {})
        if sentiment.get("overall_sentiment") == "negative":
            features.append("negative_mood")
        elif sentiment.get("overall_sentiment") == "positive":
            features.append("positive_mood")
        
        # Time context
        hour = datetime.now().hour
        if 6 <= hour < 12:
            features.append("morning")
        elif 12 <= hour < 18:
            features.append("afternoon")
        else:
            features.append("evening")
        
        return "_".join(sorted(features))
    
    def get_best_action(self, state: str) -> str:
        """Lấy best action cho state (epsilon-greedy)"""
        if np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.choice(self.actions)
        else:
            # Exploitation: best known action
            state_q_values = self.q_table[state]
            if not state_q_values:
                return np.random.choice(self.actions)
            return max(state_q_values.items(), key=lambda x: x[1])[0]
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str = None):
        """Update Q-value với reward"""
        current_q = self.q_table[state][action]
        
        if next_state:
            next_q_values = self.q_table[next_state]
            max_next_q = max(next_q_values.values()) if next_q_values else 0
        else:
            max_next_q = 0
        
        # Q-learning update rule
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def learn_from_feedback(self, context: Dict[str, Any], action: str, 
                          rating: float, response_text: str = ""):
        """Học từ user feedback"""
        state = self._extract_state_features(context)
        
        # Convert rating (1-5) to reward (-1 to 1)
        reward = (rating - 3) / 2  # 1->-1, 3->0, 5->1
        
        # Update Q-value
        self.update_q_value(state, action, reward)
        
        # Store feedback data
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "action": action,
            "rating": rating,
            "reward": reward,
            "context": context,
            "response_text": response_text[:200]  # Truncate
        }
        
        self.feedback_data.append(feedback_entry)
        self._save_feedback_data()
        
        print(f"🧠 RL Update: {state} -> {action} = {reward:.2f}")
    
    def get_response_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Lấy response strategy từ RL"""
        state = self._extract_state_features(context)
        best_action = self.get_best_action(state)
        
        # Map action to strategy
        strategies = {
            "detailed_response": {
                "style": "detailed",
                "length": "long",
                "examples": True,
                "explanations": True
            },
            "concise_response": {
                "style": "concise", 
                "length": "short",
                "direct": True,
                "no_fluff": True
            },
            "empathetic_response": {
                "style": "empathetic",
                "emotional_support": True,
                "validation": True,
                "caring_tone": True
            },
            "technical_response": {
                "style": "technical",
                "precise": True,
                "technical_terms": True,
                "code_examples": True
            },
            "creative_response": {
                "style": "creative",
                "analogies": True,
                "storytelling": True,
                "engaging": True
            },
            "helpful_response": {
                "style": "helpful",
                "actionable": True,
                "step_by_step": True,
                "practical": True
            }
        }
        
        return {
            "state": state,
            "recommended_action": best_action,
            "strategy": strategies.get(best_action, strategies["helpful_response"]),
            "confidence": max(self.q_table[state].values()) if self.q_table[state] else 0.0
        }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Thống kê learning"""
        total_feedback = len(self.feedback_data)
        
        if total_feedback == 0:
            return {"message": "No feedback data yet"}
        
        # Recent feedback analysis
        recent_feedback = [f for f in self.feedback_data[-100:]]
        avg_rating = np.mean([f["rating"] for f in recent_feedback])
        
        # Action performance
        action_performance = defaultdict(list)
        for feedback in recent_feedback:
            action_performance[feedback["action"]].append(feedback["rating"])
        
        action_stats = {}
        for action, ratings in action_performance.items():
            action_stats[action] = {
                "avg_rating": np.mean(ratings),
                "count": len(ratings)
            }
        
        # Q-table stats
        q_table_size = len(self.q_table)
        learned_states = sum(1 for state_actions in self.q_table.values() if state_actions)
        
        return {
            "total_feedback": total_feedback,
            "recent_avg_rating": avg_rating,
            "action_performance": action_stats,
            "q_table_size": q_table_size,
            "learned_states": learned_states,
            "exploration_rate": self.epsilon
        }

class PersonalizationEngine:
    """Personalization algorithms"""
    
    def __init__(self, data_dir: str = "data/ml"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.user_profile_file = os.path.join(data_dir, "user_profile_ml.json")
        self.interaction_patterns_file = os.path.join(data_dir, "interaction_patterns.json")
        
        # User profile
        self.user_profile = self._load_user_profile()
        self.interaction_patterns = self._load_interaction_patterns()
        
        # ML models
        self.preference_classifier = None
        self.topic_clusterer = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        print("🎯 Personalization Engine initialized")
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile"""
        default_profile = {
            "communication_style": "balanced",
            "technical_level": "intermediate",
            "preferred_topics": [],
            "interaction_times": [],
            "response_preferences": {},
            "learning_style": "visual",
            "attention_span": "medium",
            "expertise_areas": []
        }
        
        try:
            if os.path.exists(self.user_profile_file):
                with open(self.user_profile_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_profile.update(loaded)
        except Exception as e:
            print(f"❌ Error loading user profile: {e}")
        
        return default_profile
    
    def _save_user_profile(self):
        """Save user profile"""
        try:
            with open(self.user_profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving user profile: {e}")
    
    def _load_interaction_patterns(self) -> List[Dict[str, Any]]:
        """Load interaction patterns"""
        try:
            if os.path.exists(self.interaction_patterns_file):
                with open(self.interaction_patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading interaction patterns: {e}")
        return []
    
    def _save_interaction_patterns(self):
        """Save interaction patterns"""
        try:
            with open(self.interaction_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving interaction patterns: {e}")
    
    def analyze_user_behavior(self, conversations: List[Dict[str, Any]]):
        """Phân tích user behavior từ conversations"""
        if not conversations:
            return
        
        # Extract patterns
        patterns = {
            "message_lengths": [],
            "question_types": [],
            "topics": [],
            "interaction_times": [],
            "response_satisfaction": []
        }
        
        for conv in conversations:
            user_input = conv.get("user_input", "")
            timestamp = conv.get("timestamp", "")
            feedback = conv.get("feedback", "")
            
            # Message length pattern
            patterns["message_lengths"].append(len(user_input.split()))
            
            # Question type pattern
            if "?" in user_input:
                if any(word in user_input.lower() for word in ["how", "why", "what"]):
                    patterns["question_types"].append("factual")
                elif any(word in user_input.lower() for word in ["help", "can you"]):
                    patterns["question_types"].append("assistance")
                else:
                    patterns["question_types"].append("general")
            
            # Topic extraction (simple keyword-based)
            topics = self._extract_topics(user_input)
            patterns["topics"].extend(topics)
            
            # Interaction time
            try:
                dt = datetime.fromisoformat(timestamp)
                patterns["interaction_times"].append(dt.hour)
            except:
                pass
            
            # Satisfaction from feedback
            if feedback:
                satisfaction = self._estimate_satisfaction(feedback)
                patterns["response_satisfaction"].append(satisfaction)
        
        # Update user profile based on patterns
        self._update_profile_from_patterns(patterns)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics từ text"""
        topic_keywords = {
            "technology": ["ai", "computer", "software", "code", "programming", "tech"],
            "work": ["work", "job", "career", "meeting", "project", "deadline"],
            "personal": ["family", "friend", "personal", "life", "relationship"],
            "learning": ["learn", "study", "education", "course", "tutorial"],
            "health": ["health", "exercise", "diet", "medical", "wellness"],
            "entertainment": ["movie", "game", "music", "book", "fun"]
        }
        
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _estimate_satisfaction(self, feedback: str) -> float:
        """Estimate satisfaction từ feedback text"""
        positive_words = ["good", "great", "excellent", "helpful", "thanks", "tốt", "hay"]
        negative_words = ["bad", "wrong", "useless", "terrible", "dở", "tệ"]
        
        feedback_lower = feedback.lower()
        
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        if positive_count > negative_count:
            return 0.8
        elif negative_count > positive_count:
            return 0.2
        else:
            return 0.5
    
    def _update_profile_from_patterns(self, patterns: Dict[str, List]):
        """Update user profile từ patterns"""
        # Communication style from message length
        avg_length = np.mean(patterns["message_lengths"]) if patterns["message_lengths"] else 10
        if avg_length < 5:
            self.user_profile["communication_style"] = "concise"
        elif avg_length > 20:
            self.user_profile["communication_style"] = "detailed"
        else:
            self.user_profile["communication_style"] = "balanced"
        
        # Preferred topics
        if patterns["topics"]:
            topic_counts = Counter(patterns["topics"])
            self.user_profile["preferred_topics"] = [
                topic for topic, count in topic_counts.most_common(5)
            ]
        
        # Interaction times
        if patterns["interaction_times"]:
            common_hours = Counter(patterns["interaction_times"])
            self.user_profile["interaction_times"] = [
                hour for hour, count in common_hours.most_common(3)
            ]
        
        # Technical level from topic analysis
        tech_ratio = patterns["topics"].count("technology") / len(patterns["topics"]) if patterns["topics"] else 0
        if tech_ratio > 0.3:
            self.user_profile["technical_level"] = "advanced"
        elif tech_ratio > 0.1:
            self.user_profile["technical_level"] = "intermediate"
        else:
            self.user_profile["technical_level"] = "basic"
        
        self._save_user_profile()
    
    def get_personalized_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Đưa ra recommendations dựa trên personalization"""
        recommendations = {
            "response_style": {},
            "content_suggestions": [],
            "interaction_optimizations": [],
            "learning_suggestions": []
        }
        
        # Response style recommendations
        comm_style = self.user_profile["communication_style"]
        tech_level = self.user_profile["technical_level"]
        
        recommendations["response_style"] = {
            "length": "short" if comm_style == "concise" else "detailed" if comm_style == "detailed" else "medium",
            "technical_depth": tech_level,
            "examples": tech_level in ["intermediate", "advanced"],
            "step_by_step": tech_level == "basic"
        }
        
        # Content suggestions based on preferred topics
        preferred_topics = self.user_profile["preferred_topics"]
        if preferred_topics:
            recommendations["content_suggestions"] = [
                f"Có thể bạn quan tâm đến: {topic}" for topic in preferred_topics[:3]
            ]
        
        # Interaction optimizations
        current_hour = datetime.now().hour
        preferred_hours = self.user_profile["interaction_times"]
        
        if preferred_hours and current_hour not in preferred_hours:
            recommendations["interaction_optimizations"].append(
                f"Bạn thường tương tác vào {preferred_hours[0]}:00h. Có cần reminder không?"
            )
        
        # Learning suggestions
        if tech_level == "basic":
            recommendations["learning_suggestions"].append(
                "Có thể bắt đầu với tutorial cơ bản"
            )
        elif tech_level == "advanced":
            recommendations["learning_suggestions"].append(
                "Có thể khám phá advanced topics hoặc best practices"
            )
        
        return recommendations
    
    def train_preference_model(self, training_data: List[Dict[str, Any]]):
        """Train model để predict user preferences"""
        if len(training_data) < 10:
            print("⚠️ Insufficient training data")
            return
        
        try:
            # Prepare features và labels
            features = []
            labels = []
            
            for data in training_data:
                # Feature extraction
                feature_vector = self._extract_feature_vector(data)
                features.append(feature_vector)
                
                # Label (satisfaction level)
                satisfaction = data.get("satisfaction", 0.5)
                labels.append(1 if satisfaction > 0.6 else 0)
            
            # Train classifier
            X = np.array(features)
            y = np.array(labels)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.preference_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.preference_classifier.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.preference_classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Preference model trained. Accuracy: {accuracy:.2f}")
            
            # Save model
            model_path = os.path.join(self.data_dir, "preference_model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self.preference_classifier, f)
                
        except Exception as e:
            print(f"❌ Model training error: {e}")
    
    def _extract_feature_vector(self, data: Dict[str, Any]) -> List[float]:
        """Extract feature vector cho ML model"""
        features = []
        
        # Text length feature
        text_length = len(data.get("user_input", ""))
        features.append(text_length / 100)  # Normalize
        
        # Time feature
        try:
            timestamp = data.get("timestamp", "")
            dt = datetime.fromisoformat(timestamp)
            features.append(dt.hour / 24)  # Normalize to 0-1
        except:
            features.append(0.5)  # Default
        
        # Topic features (one-hot encoding)
        topics = ["technology", "work", "personal", "learning", "health", "entertainment"]
        user_text = data.get("user_input", "").lower()
        for topic in topics:
            topic_keywords = {
                "technology": ["ai", "computer", "code"],
                "work": ["work", "job", "meeting"],
                "personal": ["family", "friend", "life"],
                "learning": ["learn", "study", "education"],
                "health": ["health", "exercise", "medical"],
                "entertainment": ["movie", "game", "music"]
            }
            
            has_topic = any(keyword in user_text for keyword in topic_keywords.get(topic, []))
            features.append(1.0 if has_topic else 0.0)
        
        return features

class BehaviorPredictor:
    """Predict user behavior patterns"""
    
    def __init__(self, data_dir: str = "data/ml"):
        self.data_dir = data_dir
        self.model_file = os.path.join(data_dir, "behavior_model.pkl")
        
        self.behavior_model = None
        self.behavior_patterns = defaultdict(list)
        
        print("🔮 Behavior Predictor initialized")
    
    def record_behavior(self, behavior_type: str, context: Dict[str, Any]):
        """Record user behavior"""
        behavior_entry = {
            "timestamp": datetime.now().isoformat(),
            "behavior_type": behavior_type,
            "context": context,
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }
        
        self.behavior_patterns[behavior_type].append(behavior_entry)
    
    def predict_next_action(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user's next likely action"""
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        predictions = {}
        
        # Analyze patterns for each behavior type
        for behavior_type, entries in self.behavior_patterns.items():
            if not entries:
                continue
            
            # Count occurrences by time
            hour_counts = Counter([entry["hour"] for entry in entries])
            day_counts = Counter([entry["day_of_week"] for entry in entries])
            
            # Calculate probability for current time
            hour_prob = hour_counts.get(current_hour, 0) / len(entries)
            day_prob = day_counts.get(current_day, 0) / len(entries)
            
            # Combined probability
            combined_prob = (hour_prob + day_prob) / 2
            
            predictions[behavior_type] = {
                "probability": combined_prob,
                "hour_frequency": hour_counts.get(current_hour, 0),
                "day_frequency": day_counts.get(current_day, 0)
            }
        
        # Sort by probability
        sorted_predictions = sorted(
            predictions.items(), 
            key=lambda x: x[1]["probability"], 
            reverse=True
        )
        
        return {
            "predictions": dict(sorted_predictions[:5]),  # Top 5
            "most_likely": sorted_predictions[0] if sorted_predictions else None,
            "confidence": sorted_predictions[0][1]["probability"] if sorted_predictions else 0
        }
    
    def get_usage_insights(self) -> Dict[str, Any]:
        """Insights về usage patterns"""
        if not self.behavior_patterns:
            return {"message": "No behavior data collected yet"}
        
        insights = {
            "most_active_hours": [],
            "behavior_frequency": {},
            "patterns": []
        }
        
        # All behaviors by hour
        all_hours = []
        for entries in self.behavior_patterns.values():
            all_hours.extend([entry["hour"] for entry in entries])
        
        if all_hours:
            hour_counts = Counter(all_hours)
            insights["most_active_hours"] = [
                {"hour": hour, "count": count} 
                for hour, count in hour_counts.most_common(5)
            ]
        
        # Behavior frequency
        for behavior_type, entries in self.behavior_patterns.items():
            insights["behavior_frequency"][behavior_type] = len(entries)
        
        # Detect patterns
        patterns = []
        
        # Morning vs evening preference
        morning_count = sum(1 for hour in all_hours if 6 <= hour < 12)
        evening_count = sum(1 for hour in all_hours if 18 <= hour < 24)
        
        if morning_count > evening_count * 1.5:
            patterns.append("Morning person - more active in AM")
        elif evening_count > morning_count * 1.5:
            patterns.append("Evening person - more active in PM")
        
        # Weekday vs weekend
        all_days = []
        for entries in self.behavior_patterns.values():
            all_days.extend([entry["day_of_week"] for entry in entries])
        
        weekday_count = sum(1 for day in all_days if day < 5)  # Mon-Fri
        weekend_count = sum(1 for day in all_days if day >= 5)  # Sat-Sun
        
        if weekday_count > weekend_count * 2:
            patterns.append("Primarily weekday usage")
        elif weekend_count > weekday_count:
            patterns.append("Higher weekend usage")
        
        insights["patterns"] = patterns
        
        return insights

class PersonalizationSystem:
    """Main Personalization System"""
    
    def __init__(self, data_dir: str = "data/ml"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize components
        print("🎯 Initializing Personalization System...")
        
        self.rl_system = ReinforcementLearningSystem(data_dir)
        self.personalization_engine = PersonalizationEngine(data_dir)
        self.behavior_predictor = BehaviorPredictor(data_dir)
        
        print("✅ Personalization System ready!")
    
    def process_interaction(self, user_input: str, ai_response: str, 
                          context: Dict[str, Any], feedback: Dict[str, Any] = None):
        """Process interaction cho learning"""
        
        # Record behavior
        behavior_type = self._classify_interaction_type(user_input)
        self.behavior_predictor.record_behavior(behavior_type, {
            "user_input_length": len(user_input),
            "response_length": len(ai_response),
            "context": context
        })
        
        # RL learning từ feedback
        if feedback and "rating" in feedback:
            response_strategy = self._determine_response_strategy(ai_response)
            self.rl_system.learn_from_feedback(
                context, response_strategy, feedback["rating"], ai_response
            )
        
        # Update personalization
        interaction_data = {
            "user_input": user_input,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback.get("text", "") if feedback else "",
            "satisfaction": self._estimate_satisfaction_from_feedback(feedback) if feedback else 0.5
        }
        
        self.personalization_engine.analyze_user_behavior([interaction_data])
    
    def _classify_interaction_type(self, user_input: str) -> str:
        """Classify type of interaction"""
        user_lower = user_input.lower()
        
        if "?" in user_input:
            return "question"
        elif any(word in user_lower for word in ["help", "giúp", "hỗ trợ"]):
            return "help_request"
        elif any(word in user_lower for word in ["create", "tạo", "make"]):
            return "creation_request"
        elif any(word in user_lower for word in ["explain", "giải thích"]):
            return "explanation_request"
        else:
            return "general_conversation"
    
    def _determine_response_strategy(self, ai_response: str) -> str:
        """Determine response strategy từ AI response"""
        response_length = len(ai_response.split())
        
        if response_length < 20:
            return "concise_response"
        elif response_length > 100:
            return "detailed_response"
        elif any(word in ai_response.lower() for word in ["understand", "feel", "support"]):
            return "empathetic_response"
        elif any(word in ai_response.lower() for word in ["step", "first", "next", "finally"]):
            return "helpful_response"
        elif any(word in ai_response.lower() for word in ["code", "function", "algorithm"]):
            return "technical_response"
        else:
            return "helpful_response"
    
    def _estimate_satisfaction_from_feedback(self, feedback: Dict[str, Any]) -> float:
        """Estimate satisfaction từ feedback"""
        if "rating" in feedback:
            return feedback["rating"] / 5.0
        
        feedback_text = feedback.get("text", "").lower()
        positive_indicators = ["good", "great", "helpful", "thanks", "perfect"]
        negative_indicators = ["bad", "wrong", "useless", "terrible"]
        
        positive_count = sum(1 for word in positive_indicators if word in feedback_text)
        negative_count = sum(1 for word in negative_indicators if word in feedback_text)
        
        if positive_count > negative_count:
            return 0.8
        elif negative_count > positive_count:
            return 0.2
        else:
            return 0.5
    
    def get_personalized_response_guidance(self, user_input: str, 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Lấy guidance cho personalized response"""
        
        # RL strategy recommendation
        rl_guidance = self.rl_system.get_response_strategy(context)
        
        # Personalization recommendations
        personalization_recs = self.personalization_engine.get_personalized_recommendations(context)
        
        # Behavior predictions
        behavior_predictions = self.behavior_predictor.predict_next_action(context)
        
        return {
            "rl_guidance": rl_guidance,
            "personalization": personalization_recs,
            "behavior_predictions": behavior_predictions,
            "combined_strategy": self._combine_strategies(rl_guidance, personalization_recs)
        }
    
    def _combine_strategies(self, rl_guidance: Dict, personalization_recs: Dict) -> Dict[str, Any]:
        """Combine RL và personalization strategies"""
        combined = {
            "response_style": "balanced",
            "length": "medium",
            "tone": "helpful",
            "technical_level": "intermediate",
            "include_examples": True,
            "empathy_level": "medium"
        }
        
        # Apply RL guidance
        rl_strategy = rl_guidance.get("strategy", {})
        if rl_strategy.get("style"):
            combined["response_style"] = rl_strategy["style"]
        
        if rl_strategy.get("length"):
            combined["length"] = rl_strategy["length"]
        
        # Apply personalization
        person_style = personalization_recs.get("response_style", {})
        if person_style.get("technical_depth"):
            combined["technical_level"] = person_style["technical_depth"]
        
        if person_style.get("length"):
            combined["length"] = person_style["length"]
        
        # Confidence score
        rl_confidence = rl_guidance.get("confidence", 0)
        combined["confidence"] = rl_confidence
        
        return combined
    
    def get_ml_statistics(self) -> Dict[str, Any]:
        """Lấy ML system statistics"""
        return {
            "reinforcement_learning": self.rl_system.get_learning_stats(),
            "user_profile": self.personalization_engine.user_profile,
            "behavior_insights": self.behavior_predictor.get_usage_insights(),
            "total_interactions": len(self.rl_system.feedback_data),
            "personalization_active": True
        }