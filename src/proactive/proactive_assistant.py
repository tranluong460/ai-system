"""
Proactive Assistant System tích hợp Calendar, Habits, Workflows
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from .calendar_manager import CalendarManager, HabitTracker, WorkflowAutomation

class ProactiveAssistant:
    """Assistant chủ động với calendar, habits, workflows"""
    
    def __init__(self, data_dir: str = "data/proactive"):
        self.data_dir = data_dir
        
        # Initialize components
        print("🚀 Initializing Proactive Assistant...")
        
        self.calendar = CalendarManager(f"{data_dir}/calendar")
        self.habits = HabitTracker(f"{data_dir}/habits") 
        self.workflows = WorkflowAutomation(f"{data_dir}/workflows")
        
        # Notification callbacks
        self.notification_callbacks = []
        
        # Proactive monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Daily summary cache
        self.last_daily_summary = None
        self.last_summary_date = None
        
        print("✅ Proactive Assistant ready!")
    
    def add_notification_callback(self, callback: Callable):
        """Thêm callback cho notifications"""
        self.notification_callbacks.append(callback)
    
    def start_proactive_monitoring(self):
        """Bắt đầu proactive monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        
        # Start calendar reminder monitoring
        self.calendar.start_reminder_monitor()
        
        # Start main proactive loop
        self.monitoring_thread = threading.Thread(
            target=self._proactive_loop, 
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("👀 Proactive monitoring started")
    
    def stop_proactive_monitoring(self):
        """Dừng proactive monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Proactive monitoring stopped")
    
    def _proactive_loop(self):
        """Main proactive monitoring loop"""
        while self.monitoring_active:
            try:
                # Check every 5 minutes
                self._check_proactive_opportunities()
                time.sleep(300)  # 5 minutes
            except Exception as e:
                print(f"❌ Proactive loop error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _check_proactive_opportunities(self):
        """Kiểm tra cơ hội để proactive"""
        current_time = datetime.now()
        
        # Morning briefing (8 AM)
        if current_time.hour == 8 and current_time.minute < 5:
            self._send_morning_briefing()
        
        # Evening summary (6 PM)
        elif current_time.hour == 18 and current_time.minute < 5:
            self._send_evening_summary()
        
        # Habit reminders
        self._check_habit_reminders()
        
        # Workflow triggers
        self._check_workflow_triggers()
        
        # Smart suggestions
        self._generate_smart_suggestions()
    
    def _send_morning_briefing(self):
        """Gửi briefing buổi sáng"""
        if self.last_summary_date == datetime.now().date():
            return  # Already sent today
        
        briefing = self.get_daily_briefing()
        self._send_notification(
            title="🌅 Good Morning Briefing",
            message=briefing,
            type="daily_briefing"
        )
        
        self.last_summary_date = datetime.now().date()
    
    def _send_evening_summary(self):
        """Gửi summary buổi tối"""
        summary = self.get_daily_summary()
        self._send_notification(
            title="🌇 Evening Summary",
            message=summary,
            type="daily_summary"
        )
    
    def _check_habit_reminders(self):
        """Kiểm tra habit reminders"""
        today_habits = self.habits.get_today_habits()
        
        incomplete_habits = [
            habit for habit in today_habits 
            if not habit["is_completed"]
        ]
        
        # Remind at specific times
        current_hour = datetime.now().hour
        if current_hour in [9, 14, 20] and incomplete_habits:  # 9 AM, 2 PM, 8 PM
            habit_names = [h["habit"]["name"] for h in incomplete_habits[:3]]
            message = f"⏰ Nhắc nhở habits: {', '.join(habit_names)}"
            
            self._send_notification(
                title="📈 Habit Reminder",
                message=message,
                type="habit_reminder"
            )
    
    def _check_workflow_triggers(self):
        """Kiểm tra workflow triggers"""
        context = {
            "time": datetime.now().strftime("%H:%M"),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "date": datetime.now().date().isoformat()
        }
        
        triggered_workflows = self.workflows.check_triggers(context)
        
        for workflow_id in triggered_workflows:
            result = self.workflows.execute_workflow(workflow_id, context)
            
            if result["success"]:
                self._send_notification(
                    title="⚙️ Workflow Executed",
                    message=f"Workflow {workflow_id} completed successfully",
                    type="workflow_notification"
                )
    
    def _generate_smart_suggestions(self):
        """Tạo smart suggestions"""
        current_time = datetime.now()
        
        # Suggestion based on time and context
        suggestions = []
        
        # Work time suggestions (9 AM - 5 PM on weekdays)
        if (current_time.weekday() < 5 and 
            9 <= current_time.hour <= 17):
            
            # Check if no events scheduled
            today_events = self.calendar.get_today_events()
            if not today_events:
                suggestions.append("📅 Bạn chưa có lịch hẹn nào hôm nay. Có cần lập kế hoạch?")
        
        # Break time suggestions
        if current_time.hour in [10, 15]:  # 10 AM, 3 PM
            suggestions.append("☕ Đã đến giờ nghỉ giải lao. Hãy đứng dậy và vận động nhẹ!")
        
        # Weekend planning (Friday evening)
        if current_time.weekday() == 4 and current_time.hour >= 17:
            suggestions.append("🎉 Cuối tuần sắp đến! Bạn có kế hoạch gì không?")
        
        # Send suggestions
        for suggestion in suggestions:
            self._send_notification(
                title="💡 Smart Suggestion",
                message=suggestion,
                type="smart_suggestion"
            )
    
    def _send_notification(self, title: str, message: str, 
                         notification_type: str = "general"):
        """Gửi notification thông qua callbacks"""
        notification = {
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now().isoformat()
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                print(f"❌ Notification callback error: {e}")
    
    def get_daily_briefing(self) -> str:
        """Tạo daily briefing"""
        today = datetime.now().date()
        
        # Today's events
        today_events = self.calendar.get_today_events()
        
        # Today's habits
        today_habits = self.habits.get_today_habits()
        incomplete_habits = [h for h in today_habits if not h["is_completed"]]
        
        # Upcoming events (next 3 days)
        upcoming_events = self.calendar.get_upcoming_events(3)
        
        briefing_parts = [
            f"📅 **Daily Briefing - {today.strftime('%A, %B %d')}**\n"
        ]
        
        # Today's schedule
        if today_events:
            briefing_parts.append("**📋 Lịch hôm nay:**")
            for event in today_events[:5]:
                time_str = datetime.fromisoformat(event["start_time"]).strftime("%H:%M")
                briefing_parts.append(f"• {time_str} - {event['title']}")
        else:
            briefing_parts.append("📋 Không có lịch hẹn nào hôm nay")
        
        # Habits to complete
        if incomplete_habits:
            briefing_parts.append("\n**📈 Habits cần hoàn thành:**")
            for habit in incomplete_habits[:5]:
                progress = habit["progress"]
                briefing_parts.append(f"• {habit['habit']['name']} ({progress:.0f}%)")
        
        # Upcoming events
        if upcoming_events:
            briefing_parts.append("\n**⏰ Sắp tới:**")
            for event in upcoming_events[:3]:
                date_str = datetime.fromisoformat(event["start_time"]).strftime("%m/%d %H:%M")
                briefing_parts.append(f"• {date_str} - {event['title']}")
        
        briefing_parts.append("\n✨ Chúc bạn một ngày tốt lành!")
        
        return "\n".join(briefing_parts)
    
    def get_daily_summary(self) -> str:
        """Tạo daily summary"""
        today = datetime.now().date()
        
        # Today's completed habits
        today_habits = self.habits.get_today_habits()
        completed_habits = [h for h in today_habits if h["is_completed"]]
        
        # Today's events that happened
        today_events = self.calendar.get_today_events()
        
        summary_parts = [
            f"🌇 **Daily Summary - {today.strftime('%A, %B %d')}**\n"
        ]
        
        # Habit completion
        if today_habits:
            completion_rate = (len(completed_habits) / len(today_habits)) * 100
            summary_parts.append(f"📈 **Habits:** {len(completed_habits)}/{len(today_habits)} hoàn thành ({completion_rate:.0f}%)")
            
            if completed_habits:
                summary_parts.append("✅ Đã hoàn thành:")
                for habit in completed_habits:
                    summary_parts.append(f"• {habit['habit']['name']}")
        
        # Events summary
        if today_events:
            summary_parts.append(f"\n📅 **Lịch hẹn:** {len(today_events)} sự kiện hôm nay")
        
        # Motivational message
        if completed_habits:
            summary_parts.append("\n🎉 Tuyệt vời! Bạn đã hoàn thành một số habits hôm nay!")
        
        summary_parts.append("\n💤 Chúc bạn ngủ ngon và nghỉ ngơi tốt!")
        
        return "\n".join(summary_parts)
    
    # Calendar methods
    def add_event(self, title: str, start_time: str, **kwargs) -> str:
        """Thêm event và tự động tạo reminder"""
        return self.calendar.add_event(title, start_time, **kwargs)
    
    def add_reminder(self, title: str, trigger_time: str, message: str) -> str:
        """Thêm reminder"""
        return self.calendar.add_reminder(title, trigger_time, message)
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Lấy upcoming events"""
        return self.calendar.get_upcoming_events(days)
    
    # Habit methods
    def add_habit(self, name: str, **kwargs) -> str:
        """Thêm habit mới"""
        return self.habits.add_habit(name, **kwargs)
    
    def log_habit(self, habit_id: str, value: int = 1, note: str = "") -> bool:
        """Log habit completion"""
        return self.habits.log_habit(habit_id, value, note)
    
    def get_habit_stats(self, habit_id: str, days: int = 30) -> Dict[str, Any]:
        """Lấy habit statistics"""
        return self.habits.get_habit_stats(habit_id, days)
    
    # Workflow methods
    def create_workflow(self, name: str, description: str, 
                       triggers: List[Dict], actions: List[Dict]) -> str:
        """Tạo workflow automation"""
        return self.workflows.create_workflow(name, description, triggers, actions)
    
    def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """Thực hiện workflow manually"""
        return self.workflows.execute_workflow(workflow_id, context or {})
    
    # Integration methods
    def process_natural_language_request(self, request: str) -> Dict[str, Any]:
        """Xử lý yêu cầu bằng ngôn ngữ tự nhiên"""
        request_lower = request.lower()
        
        # Event creation
        if any(phrase in request_lower for phrase in 
               ["tạo lịch", "add event", "đặt lịch", "meeting"]):
            return self._parse_event_request(request)
        
        # Habit logging
        elif any(phrase in request_lower for phrase in 
                ["đã làm", "hoàn thành", "completed", "done"]):
            return self._parse_habit_completion(request)
        
        # Reminder creation
        elif any(phrase in request_lower for phrase in 
                ["nhắc nhở", "remind", "nhắc tôi"]):
            return self._parse_reminder_request(request)
        
        # Query requests
        elif any(phrase in request_lower for phrase in 
                ["lịch", "schedule", "calendar", "habit", "thói quen"]):
            return self._parse_query_request(request)
        
        return {"type": "unknown", "message": "Không hiểu yêu cầu"}
    
    def _parse_event_request(self, request: str) -> Dict[str, Any]:
        """Parse event creation request"""
        # Simple parsing (có thể enhance với NLP)
        import re
        
        # Extract time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 14:30
            r'(\d{1,2})h(\d{2})',  # 14h30
            r'(\d{1,2}) giờ',      # 2 giờ
        ]
        
        time_match = None
        for pattern in time_patterns:
            time_match = re.search(pattern, request)
            if time_match:
                break
        
        # Extract date patterns
        date_patterns = [
            r'hôm nay',
            r'ngày mai',
            r'(\d{1,2})/(\d{1,2})',  # 25/12
        ]
        
        date_info = "hôm nay"  # default
        for pattern in date_patterns:
            if re.search(pattern, request):
                date_info = re.search(pattern, request).group()
                break
        
        # Parse event title (words after "tạo lịch" or "meeting")
        title_patterns = [
            r'(?:tạo lịch|add event|đặt lịh|meeting)\s+(.+?)(?:\s+lúc|\s+vào|\s+at|$)',
            r'(.+?)\s+(?:lúc|vào|at)\s+',
        ]
        
        title = "Sự kiện mới"  # default
        for pattern in title_patterns:
            title_match = re.search(pattern, request, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                break
        
        return {
            "type": "event_creation",
            "title": title,
            "time": time_match.group() if time_match else "09:00",
            "date": date_info,
            "raw_request": request
        }
    
    def _parse_habit_completion(self, request: str) -> Dict[str, Any]:
        """Parse habit completion request"""
        # Extract habit name
        completion_phrases = ["đã làm", "hoàn thành", "completed", "done"]
        
        for phrase in completion_phrases:
            if phrase in request.lower():
                # Get text after the phrase
                parts = request.lower().split(phrase)
                if len(parts) > 1:
                    habit_name = parts[1].strip()
                    return {
                        "type": "habit_completion",
                        "habit_name": habit_name,
                        "raw_request": request
                    }
        
        return {"type": "habit_completion", "message": "Không xác định được habit"}
    
    def _parse_reminder_request(self, request: str) -> Dict[str, Any]:
        """Parse reminder creation request"""
        # Similar parsing logic for reminders
        return {
            "type": "reminder_creation",
            "message": "Parsing reminder request...",
            "raw_request": request
        }
    
    def _parse_query_request(self, request: str) -> Dict[str, Any]:
        """Parse query request"""
        if "lịch" in request.lower() or "schedule" in request.lower():
            events = self.get_upcoming_events(7)
            return {
                "type": "schedule_query",
                "events": events,
                "count": len(events)
            }
        
        elif "habit" in request.lower() or "thói quen" in request.lower():
            today_habits = self.habits.get_today_habits()
            return {
                "type": "habit_query", 
                "habits": today_habits,
                "count": len(today_habits)
            }
        
        return {"type": "general_query", "message": "Đang xử lý truy vấn..."}
    
    def get_proactive_stats(self) -> Dict[str, Any]:
        """Lấy thống kê proactive system"""
        return {
            "calendar": {
                "total_events": len(self.calendar.events),
                "upcoming_events": len(self.get_upcoming_events(7)),
                "active_reminders": len([r for r in self.calendar.reminders if r["status"] == "pending"])
            },
            "habits": {
                "total_habits": len(self.habits.habits),
                "active_habits": len([h for h in self.habits.habits if h["status"] == "active"]),
                "today_completion": len([h for h in self.habits.get_today_habits() if h["is_completed"]])
            },
            "workflows": {
                "total_workflows": len(self.workflows.workflows),
                "active_workflows": len([w for w in self.workflows.workflows if w["status"] == "active"])
            },
            "monitoring_active": self.monitoring_active
        }