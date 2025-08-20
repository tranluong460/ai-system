"""
Calendar Integration và Reminder System
"""
import schedule
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from icalendar import Calendar, Event
import time
import threading

class CalendarManager:
    """Quản lý calendar và events"""
    
    def __init__(self, data_dir: str = "data/calendar"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.events_file = os.path.join(data_dir, "events.json")
        self.reminders_file = os.path.join(data_dir, "reminders.json")
        
        self.events = self._load_events()
        self.reminders = self._load_reminders()
        
        # Callback khi có reminder
        self.reminder_callbacks = []
        
        print("📅 Calendar Manager initialized")
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events từ file"""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading events: {e}")
        return []
    
    def _save_events(self):
        """Lưu events"""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving events: {e}")
    
    def _load_reminders(self) -> List[Dict[str, Any]]:
        """Load reminders"""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading reminders: {e}")
        return []
    
    def _save_reminders(self):
        """Lưu reminders"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving reminders: {e}")
    
    def add_event(self, title: str, start_time: str, end_time: str = None,
                  description: str = "", location: str = "", reminder_minutes: int = 15) -> str:
        """Thêm event mới"""
        event_id = f"event_{len(self.events)}_{int(time.time())}"
        
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time or start_time,
            "description": description,
            "location": location,
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.events.append(event)
        self._save_events()
        
        # Tạo reminder
        if reminder_minutes > 0:
            self._create_reminder_for_event(event)
        
        return event_id
    
    def _create_reminder_for_event(self, event: Dict[str, Any]):
        """Tạo reminder cho event"""
        try:
            start_dt = datetime.fromisoformat(event["start_time"])
            reminder_dt = start_dt - timedelta(minutes=event["reminder_minutes"])
            
            reminder = {
                "id": f"reminder_{event['id']}",
                "event_id": event["id"],
                "title": f"Reminder: {event['title']}",
                "trigger_time": reminder_dt.isoformat(),
                "message": f"Sắp tới sự kiện: {event['title']} lúc {start_dt.strftime('%H:%M')}",
                "type": "event_reminder",
                "status": "pending"
            }
            
            self.reminders.append(reminder)
            self._save_reminders()
            
        except Exception as e:
            print(f"❌ Error creating reminder: {e}")
    
    def add_reminder(self, title: str, trigger_time: str, message: str, 
                    reminder_type: str = "general") -> str:
        """Thêm reminder độc lập"""
        reminder_id = f"reminder_{len(self.reminders)}_{int(time.time())}"
        
        reminder = {
            "id": reminder_id,
            "title": title,
            "trigger_time": trigger_time,
            "message": message,
            "type": reminder_type,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        return reminder_id
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Lấy events sắp tới"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        upcoming = []
        for event in self.events:
            if event["status"] != "active":
                continue
                
            try:
                event_start = datetime.fromisoformat(event["start_time"])
                if now <= event_start <= end_date:
                    upcoming.append(event)
            except:
                continue
        
        # Sort by start time
        upcoming.sort(key=lambda x: x["start_time"])
        return upcoming
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """Lấy events hôm nay"""
        today = datetime.now().date()
        
        today_events = []
        for event in self.events:
            if event["status"] != "active":
                continue
                
            try:
                event_date = datetime.fromisoformat(event["start_time"]).date()
                if event_date == today:
                    today_events.append(event)
            except:
                continue
        
        return today_events
    
    def check_reminders(self) -> List[Dict[str, Any]]:
        """Kiểm tra reminders cần trigger"""
        now = datetime.now()
        triggered_reminders = []
        
        for reminder in self.reminders:
            if reminder["status"] != "pending":
                continue
            
            try:
                trigger_time = datetime.fromisoformat(reminder["trigger_time"])
                if now >= trigger_time:
                    triggered_reminders.append(reminder)
                    reminder["status"] = "triggered"
                    reminder["triggered_at"] = now.isoformat()
            except:
                continue
        
        if triggered_reminders:
            self._save_reminders()
            
            # Call callbacks
            for callback in self.reminder_callbacks:
                try:
                    callback(triggered_reminders)
                except Exception as e:
                    print(f"❌ Reminder callback error: {e}")
        
        return triggered_reminders
    
    def add_reminder_callback(self, callback):
        """Thêm callback cho reminders"""
        self.reminder_callbacks.append(callback)
    
    def start_reminder_monitor(self):
        """Bắt đầu monitor reminders"""
        def monitor_loop():
            while True:
                try:
                    self.check_reminders()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"❌ Reminder monitor error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print("⏰ Reminder monitor started")
    
    def export_to_ical(self, filename: str = None) -> str:
        """Export events to iCal format"""
        if not filename:
            filename = os.path.join(self.data_dir, "events.ics")
        
        cal = Calendar()
        cal.add('prodid', '-//AI Assistant//Calendar//EN')
        cal.add('version', '2.0')
        
        for event_data in self.events:
            if event_data["status"] != "active":
                continue
            
            try:
                event = Event()
                event.add('summary', event_data["title"])
                event.add('dtstart', datetime.fromisoformat(event_data["start_time"]))
                event.add('dtend', datetime.fromisoformat(event_data["end_time"]))
                
                if event_data["description"]:
                    event.add('description', event_data["description"])
                if event_data["location"]:
                    event.add('location', event_data["location"])
                
                cal.add_component(event)
            except Exception as e:
                print(f"❌ Error adding event to iCal: {e}")
        
        try:
            with open(filename, 'wb') as f:
                f.write(cal.to_ical())
            return filename
        except Exception as e:
            print(f"❌ Error saving iCal: {e}")
            return ""

class HabitTracker:
    """Theo dõi habits"""
    
    def __init__(self, data_dir: str = "data/habits"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.habits_file = os.path.join(data_dir, "habits.json")
        self.logs_file = os.path.join(data_dir, "habit_logs.json")
        
        self.habits = self._load_habits()
        self.logs = self._load_logs()
        
        print("📈 Habit Tracker initialized")
    
    def _load_habits(self) -> List[Dict[str, Any]]:
        """Load habits"""
        try:
            if os.path.exists(self.habits_file):
                with open(self.habits_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading habits: {e}")
        return []
    
    def _save_habits(self):
        """Lưu habits"""
        try:
            with open(self.habits_file, 'w', encoding='utf-8') as f:
                json.dump(self.habits, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving habits: {e}")
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """Load habit logs"""
        try:
            if os.path.exists(self.logs_file):
                with open(self.logs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading logs: {e}")
        return []
    
    def _save_logs(self):
        """Lưu logs"""
        try:
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving logs: {e}")
    
    def add_habit(self, name: str, description: str = "", 
                  frequency: str = "daily", target_value: int = 1) -> str:
        """Thêm habit mới"""
        habit_id = f"habit_{len(self.habits)}_{int(time.time())}"
        
        habit = {
            "id": habit_id,
            "name": name,
            "description": description,
            "frequency": frequency,  # daily, weekly, monthly
            "target_value": target_value,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.habits.append(habit)
        self._save_habits()
        
        return habit_id
    
    def log_habit(self, habit_id: str, value: int = 1, note: str = "") -> bool:
        """Log habit completion"""
        today = datetime.now().date().isoformat()
        
        log_entry = {
            "habit_id": habit_id,
            "date": today,
            "value": value,
            "note": note,
            "logged_at": datetime.now().isoformat()
        }
        
        # Check if already logged today
        for log in self.logs:
            if log["habit_id"] == habit_id and log["date"] == today:
                log["value"] += value
                log["note"] = note
                log["logged_at"] = datetime.now().isoformat()
                self._save_logs()
                return True
        
        # Add new log
        self.logs.append(log_entry)
        self._save_logs()
        return True
    
    def get_habit_stats(self, habit_id: str, days: int = 30) -> Dict[str, Any]:
        """Lấy thống kê habit"""
        habit = next((h for h in self.habits if h["id"] == habit_id), None)
        if not habit:
            return {}
        
        # Get logs for this habit
        habit_logs = [log for log in self.logs if log["habit_id"] == habit_id]
        
        # Calculate stats for last N days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        completed_days = 0
        total_value = 0
        streak = 0
        current_streak = 0
        
        # Check each day
        current_date = start_date
        consecutive_days = 0
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_logs = [log for log in habit_logs if log["date"] == date_str]
            
            if day_logs:
                day_value = sum(log["value"] for log in day_logs)
                total_value += day_value
                
                if day_value >= habit["target_value"]:
                    completed_days += 1
                    consecutive_days += 1
                    streak = max(streak, consecutive_days)
                else:
                    consecutive_days = 0
            else:
                consecutive_days = 0
            
            current_date += timedelta(days=1)
        
        # Current streak (from today backwards)
        current_date = end_date
        while current_date >= start_date:
            date_str = current_date.isoformat()
            day_logs = [log for log in habit_logs if log["date"] == date_str]
            
            if day_logs:
                day_value = sum(log["value"] for log in day_logs)
                if day_value >= habit["target_value"]:
                    current_streak += 1
                else:
                    break
            else:
                break
            
            current_date -= timedelta(days=1)
        
        completion_rate = (completed_days / days) * 100 if days > 0 else 0
        
        return {
            "habit_name": habit["name"],
            "completion_rate": round(completion_rate, 1),
            "completed_days": completed_days,
            "total_days": days,
            "total_value": total_value,
            "best_streak": streak,
            "current_streak": current_streak,
            "average_daily": round(total_value / days, 1) if days > 0 else 0
        }
    
    def get_today_habits(self) -> List[Dict[str, Any]]:
        """Lấy habits cần làm hôm nay"""
        today = datetime.now().date().isoformat()
        
        today_habits = []
        for habit in self.habits:
            if habit["status"] != "active":
                continue
            
            # Check if already completed today
            today_logs = [log for log in self.logs 
                         if log["habit_id"] == habit["id"] and log["date"] == today]
            
            completed_value = sum(log["value"] for log in today_logs)
            is_completed = completed_value >= habit["target_value"]
            
            today_habits.append({
                "habit": habit,
                "completed_today": completed_value,
                "target": habit["target_value"],
                "is_completed": is_completed,
                "progress": min(100, (completed_value / habit["target_value"]) * 100)
            })
        
        return today_habits

class WorkflowAutomation:
    """Workflow Automation System"""
    
    def __init__(self, data_dir: str = "data/workflows"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.workflows_file = os.path.join(data_dir, "workflows.json")
        self.executions_file = os.path.join(data_dir, "executions.json")
        
        self.workflows = self._load_workflows()
        self.executions = self._load_executions()
        
        print("⚙️ Workflow Automation initialized")
    
    def _load_workflows(self) -> List[Dict[str, Any]]:
        """Load workflows"""
        try:
            if os.path.exists(self.workflows_file):
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading workflows: {e}")
        return []
    
    def _save_workflows(self):
        """Lưu workflows"""
        try:
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflows, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving workflows: {e}")
    
    def _load_executions(self) -> List[Dict[str, Any]]:
        """Load executions"""
        try:
            if os.path.exists(self.executions_file):
                with open(self.executions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading executions: {e}")
        return []
    
    def _save_executions(self):
        """Lưu executions"""
        try:
            with open(self.executions_file, 'w', encoding='utf-8') as f:
                json.dump(self.executions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving executions: {e}")
    
    def create_workflow(self, name: str, description: str, 
                       triggers: List[Dict[str, Any]], 
                       actions: List[Dict[str, Any]]) -> str:
        """Tạo workflow mới"""
        workflow_id = f"workflow_{len(self.workflows)}_{int(time.time())}"
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "triggers": triggers,  # List of trigger conditions
            "actions": actions,    # List of actions to execute
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "execution_count": 0
        }
        
        self.workflows.append(workflow)
        self._save_workflows()
        
        return workflow_id
    
    def check_triggers(self, context: Dict[str, Any]) -> List[str]:
        """Kiểm tra workflows cần trigger"""
        triggered_workflows = []
        
        for workflow in self.workflows:
            if workflow["status"] != "active":
                continue
            
            should_trigger = True
            for trigger in workflow["triggers"]:
                if not self._evaluate_trigger(trigger, context):
                    should_trigger = False
                    break
            
            if should_trigger:
                triggered_workflows.append(workflow["id"])
        
        return triggered_workflows
    
    def _evaluate_trigger(self, trigger: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate trigger condition"""
        trigger_type = trigger.get("type")
        
        if trigger_type == "time":
            # Time-based trigger
            current_time = datetime.now().strftime("%H:%M")
            return current_time == trigger.get("time")
        
        elif trigger_type == "keyword":
            # Keyword trigger
            text = context.get("text", "").lower()
            keyword = trigger.get("keyword", "").lower()
            return keyword in text
        
        elif trigger_type == "context":
            # Context-based trigger
            key = trigger.get("key")
            expected_value = trigger.get("value")
            return context.get(key) == expected_value
        
        return False
    
    def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Thực hiện workflow"""
        workflow = next((w for w in self.workflows if w["id"] == workflow_id), None)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        execution_id = f"exec_{int(time.time())}"
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "started_at": datetime.now().isoformat(),
            "context": context or {},
            "status": "running",
            "results": []
        }
        
        try:
            # Execute actions
            for action in workflow["actions"]:
                result = self._execute_action(action, context or {})
                execution["results"].append(result)
                
                if not result.get("success", False):
                    execution["status"] = "failed"
                    break
            else:
                execution["status"] = "completed"
            
            # Update workflow stats
            workflow["execution_count"] += 1
            workflow["last_executed"] = datetime.now().isoformat()
            
        except Exception as e:
            execution["status"] = "error"
            execution["error"] = str(e)
        
        execution["completed_at"] = datetime.now().isoformat()
        
        # Save execution
        self.executions.append(execution)
        self._save_executions()
        self._save_workflows()
        
        return {
            "success": execution["status"] in ["completed"],
            "execution_id": execution_id,
            "results": execution["results"]
        }
    
    def _execute_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện action"""
        action_type = action.get("type")
        
        if action_type == "log":
            message = action.get("message", "").format(**context)
            print(f"📝 Workflow: {message}")
            return {"success": True, "message": message}
        
        elif action_type == "reminder":
            title = action.get("title", "").format(**context)
            message = action.get("message", "").format(**context)
            # Tích hợp với CalendarManager nếu có
            return {"success": True, "reminder_created": title}
        
        elif action_type == "command":
            command = action.get("command", "").format(**context)
            # Execute system command (cần cẩn thận với security)
            return {"success": True, "command": command}
        
        return {"success": False, "error": f"Unknown action type: {action_type}"}