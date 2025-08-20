"""
Unified response management for AI Assistant
"""
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import ErrorHandler

@dataclass
class ResponseMetadata:
    """Metadata for AI responses"""
    model: str
    processing_time: float
    tools_used: List[str]
    autonomous_execution: bool = False
    context_length: int = 0
    error_occurred: bool = False

class ResponseManager:
    """Manages all AI responses with consistent formatting and metadata"""
    
    def __init__(self, ui, ai_core, learning_system):
        self.ui = ui
        self.ai_core = ai_core
        self.learning_system = learning_system
        self.error_handler = ErrorHandler("response_manager")
    
    def process_and_respond(self, user_input: str, response: str, 
                          tools_used: List[str] = None, 
                          autonomous_execution: bool = False,
                          processing_time: float = 0) -> None:
        """Process AI response and display with metadata"""
        
        # Default values
        tools_used = tools_used or []
        
        # Create metadata
        metadata = ResponseMetadata(
            model=self.ai_core.model_name,
            processing_time=processing_time,
            tools_used=tools_used,
            autonomous_execution=autonomous_execution,
            context_length=len(self.ai_core._get_context(limit=2)),
            error_occurred=False
        )
        
        # Add response to chat
        ai_message = self.ui.add_message("assistant", response, metadata.__dict__)
        self.ui.display_message(ai_message)
        
        # Learn from interaction
        self._record_interaction(user_input, response, tools_used, True)
        
        # Show suggestions if available
        self._show_suggestions(user_input)
    
    def process_error_response(self, user_input: str, error: Exception, 
                             context: str = "") -> None:
        """Process and display error responses consistently"""
        
        error_response = self.error_handler.format_error_response(error, context)
        
        # Create error metadata
        metadata = ResponseMetadata(
            model=self.ai_core.model_name,
            processing_time=0,
            tools_used=[],
            error_occurred=True
        )
        
        # Display error
        self.ui.display_error(error_response["message"])
        
        # Record failed interaction
        self._record_interaction(user_input, error_response["message"], [], False)
    
    def _record_interaction(self, user_input: str, ai_response: str, 
                          tools_used: List[str], success: bool):
        """Record interaction in learning system"""
        try:
            self.learning_system.learn_from_interaction(
                user_input=user_input,
                ai_response=ai_response,
                tools_used=tools_used,
                success=success
            )
        except Exception as e:
            self.error_handler.logger.error(f"Failed to record interaction: {e}")
    
    def _show_suggestions(self, user_input: str):
        """Show AI suggestions and next actions"""
        try:
            # Get suggestions from learning system
            suggestions = self.learning_system.get_suggestions(user_input)
            if suggestions and len(suggestions) > 0:
                suggestion_text = f"💡 Gợi ý: {', '.join([s['pattern'] for s in suggestions[:2]])}"
                self.ui.display_warning(suggestion_text)
            
            # Get next action suggestions
            next_actions = self.learning_system.suggest_next_actions(user_input)
            if next_actions:
                next_text = f"🎯 Có thể bạn muốn: {', '.join(next_actions[:2])}"
                suggestion_msg = self.ui.add_message("system", next_text)
                self.ui.display_message(suggestion_msg)
                
        except Exception as e:
            self.error_handler.logger.warning(f"Failed to show suggestions: {e}")
    
    def show_typing_indicator(self, duration: float = 1.5):
        """Show typing indicator"""
        self.ui.show_typing_indicator(duration)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get response processing statistics"""
        return {
            "total_responses": getattr(self, '_response_count', 0),
            "average_processing_time": getattr(self, '_avg_processing_time', 0),
            "error_rate": getattr(self, '_error_rate', 0)
        }