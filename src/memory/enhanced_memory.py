"""
Enhanced Memory System với Vector DB và Knowledge Graph integration
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .vector_db.chroma_manager import ChromaMemoryManager, SemanticSearch
from .knowledge_graph import KnowledgeGraph, PersonalityGraph

class EnhancedMemorySystem:
    """Hệ thống memory tích hợp vector DB và knowledge graph"""
    
    def __init__(self, data_dir: str = "data/enhanced_memory"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Khởi tạo các components
        print("🧠 Initializing Enhanced Memory System...")
        
        try:
            self.vector_memory = ChromaMemoryManager(
                db_path=os.path.join(data_dir, "vector_db")
            )
            
            self.semantic_search = SemanticSearch(self.vector_memory)
            print("✅ Vector memory initialized")
        except Exception as e:
            print(f"⚠️ Vector memory initialization failed: {e}")
            self.vector_memory = None
            self.semantic_search = None
        
        try:
            self.knowledge_graph = KnowledgeGraph(
                data_dir=os.path.join(data_dir, "knowledge_graph")
            )
            print("✅ Knowledge graph initialized")
        except Exception as e:
            print(f"⚠️ Knowledge graph initialization failed: {e}")
            self.knowledge_graph = None
        
        try:
            self.personality_graph = PersonalityGraph(
                data_dir=os.path.join(data_dir, "personality_graph")
            )
            print("✅ Personality graph initialized")
        except Exception as e:
            print(f"⚠️ Personality graph initialization failed: {e}")
            self.personality_graph = None
        
        # Memory integration settings
        self.settings_file = os.path.join(data_dir, "memory_settings.json")
        self.settings = self._load_settings()
        
        print("✅ Enhanced Memory System ready!")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load memory settings"""
        default_settings = {
            "vector_similarity_threshold": 0.7,
            "max_context_conversations": 5,
            "auto_extract_entities": True,
            "personality_learning_enabled": True,
            "knowledge_extraction_enabled": True,
            "semantic_clustering_enabled": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"⚠️ Error loading memory settings: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """Save memory settings"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memory settings: {e}")
    
    def store_conversation(self, user_input: str, ai_response: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Lưu conversation với full processing"""
        print("💾 Storing conversation with enhanced processing...")
        
        # 1. Store in vector database
        conversation_id = None
        if self.vector_memory:
            try:
                conversation_id = self.vector_memory.add_conversation(
                    user_input, ai_response, context
                )
            except Exception as e:
                print(f"⚠️ Error storing in vector DB: {e}")
                conversation_id = f"local_{datetime.now().timestamp()}"
        else:
            conversation_id = f"local_{datetime.now().timestamp()}"
        
        # 2. Extract and store entities in knowledge graph
        if self.settings["auto_extract_entities"] and self.knowledge_graph:
            try:
                self._extract_and_store_entities(user_input, ai_response, conversation_id)
            except Exception as e:
                print(f"⚠️ Error extracting entities: {e}")
        
        # 3. Update personality insights
        if self.settings["personality_learning_enabled"] and self.personality_graph:
            try:
                self._update_personality_insights(user_input, ai_response)
            except Exception as e:
                print(f"⚠️ Error updating personality: {e}")
        
        # 4. Extract knowledge if applicable
        if self.settings["knowledge_extraction_enabled"] and self.knowledge_graph:
            try:
                self._extract_knowledge(user_input, ai_response)
            except Exception as e:
                print(f"⚠️ Error extracting knowledge: {e}")
        
        return {
            "conversation_id": conversation_id,
            "processed": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_and_store_entities(self, user_input: str, ai_response: str, 
                                   conversation_id: str):
        """Extract entities và relationships từ conversation"""
        full_text = f"{user_input} {ai_response}"
        
        # Simple entity extraction (có thể enhance với NER models)
        entities = self._simple_entity_extraction(full_text)
        
        for entity in entities:
            # Add entity to knowledge graph
            self.knowledge_graph.add_entity(
                entity_id=entity["id"],
                entity_type=entity["type"],
                properties={
                    "name": entity["name"],
                    "mentioned_in": conversation_id,
                    "context": entity.get("context", ""),
                    "confidence": entity.get("confidence", 0.8)
                }
            )
            
            # Update entity with conversation context
            self.knowledge_graph.update_entity_from_conversation(
                entity["id"], full_text[:200]
            )
    
    def _simple_entity_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Simple entity extraction (có thể thay bằng spaCy/transformers)"""
        entities = []
        words = text.split()
        
        # Extract potential names (capitalized words)
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                entities.append({
                    "id": f"entity_{word.lower()}",
                    "name": word,
                    "type": "person_or_place",
                    "context": " ".join(words[max(0, i-2):i+3]),
                    "confidence": 0.6
                })
        
        # Extract numbers and dates
        import re
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        for date in dates:
            entities.append({
                "id": f"date_{date.replace('/', '_').replace('-', '_')}",
                "name": date,
                "type": "date",
                "context": text,
                "confidence": 0.9
            })
        
        return entities
    
    def _update_personality_insights(self, user_input: str, ai_response: str):
        """Cập nhật personality insights từ conversation"""
        # Phân tích communication style
        if len(user_input.split()) > 20:
            self.personality_graph.add_personality_trait(
                "communication_style", "detailed", 0.7, 
                f"Uses long messages: {len(user_input.split())} words"
            )
        elif len(user_input.split()) < 5:
            self.personality_graph.add_personality_trait(
                "communication_style", "concise", 0.7,
                f"Uses short messages: {len(user_input.split())} words"
            )
        
        # Phân tích interests từ keywords
        tech_keywords = ["code", "programming", "AI", "computer", "software", "lập trình"]
        if any(kw.lower() in user_input.lower() for kw in tech_keywords):
            self.personality_graph.add_personality_trait(
                "interests", "technology", 0.8,
                f"Mentioned tech topics: {user_input[:100]}"
            )
        
        # Phân tích work patterns
        work_keywords = ["meeting", "work", "công việc", "deadline", "project"]
        if any(kw.lower() in user_input.lower() for kw in work_keywords):
            self.personality_graph.add_personality_trait(
                "work_focus", "professional", 0.7,
                f"Work-related discussion: {user_input[:100]}"
            )
    
    def _extract_knowledge(self, user_input: str, ai_response: str):
        """Extract knowledge từ conversation"""
        # Tìm factual statements trong AI response
        if any(indicator in ai_response.lower() for indicator in 
               ["là", "được", "có thể", "thường", "luôn", "bao gồm"]):
            
            # Extract potential knowledge
            sentences = ai_response.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 20 and len(sentence.strip()) < 200:
                    # Add as knowledge
                    self.vector_memory.add_knowledge(
                        topic=user_input[:50],
                        content=sentence.strip(),
                        source="ai_response",
                        tags=self._extract_tags(sentence)
                    )
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags từ text"""
        # Simple tag extraction
        tags = []
        
        categories = {
            "tech": ["technology", "computer", "software", "AI", "programming"],
            "work": ["work", "job", "career", "business", "meeting"],
            "personal": ["family", "friend", "hobby", "personal"],
            "health": ["health", "exercise", "diet", "medical"],
            "education": ["learn", "study", "school", "course", "education"]
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(category)
        
        return tags
    
    def get_enhanced_context(self, query: str, max_items: int = 5) -> Dict[str, Any]:
        """Lấy context tăng cường từ cả vector DB và knowledge graph"""
        # 1. Semantic search trong conversations
        similar_conversations = []
        if self.vector_memory:
            try:
                similar_conversations = self.vector_memory.search_conversations(
                    query, n_results=max_items
                )
            except Exception as e:
                print(f"⚠️ Error searching conversations: {e}")
        
        # 2. Search knowledge base
        relevant_knowledge = []
        if self.vector_memory:
            try:
                relevant_knowledge = self.vector_memory.search_knowledge(
                    query, n_results=max_items
                )
            except Exception as e:
                print(f"⚠️ Error searching knowledge: {e}")
        
        # 3. Find related entities trong knowledge graph
        related_entities = []
        if self.knowledge_graph:
            try:
                related_entities = self.knowledge_graph.search_entities(query)
            except Exception as e:
                print(f"⚠️ Error searching entities: {e}")
        
        # 4. Get personality context
        personality_summary = {}
        if self.personality_graph:
            try:
                personality_summary = self.personality_graph.get_personality_summary()
            except Exception as e:
                print(f"⚠️ Error getting personality: {e}")
        
        # 5. Combine và rank results
        context = {
            "similar_conversations": similar_conversations,
            "relevant_knowledge": relevant_knowledge,
            "related_entities": related_entities[:max_items],
            "personality_insights": personality_summary,
            "query": query,
            "generated_at": datetime.now().isoformat()
        }
        
        return context
    
    def generate_smart_response_context(self, user_input: str) -> str:
        """Tạo context thông minh cho AI response"""
        enhanced_context = self.get_enhanced_context(user_input)
        
        context_parts = []
        
        # Add conversation history context
        if enhanced_context["similar_conversations"]:
            context_parts.append("Previous relevant conversations:")
            for conv in enhanced_context["similar_conversations"][:2]:
                if conv["similarity"] > self.settings["vector_similarity_threshold"]:
                    context_parts.append(f"- User asked: {conv['user_input'][:100]}")
                    context_parts.append(f"  AI responded: {conv['ai_response'][:100]}")
        
        # Add knowledge context
        if enhanced_context["relevant_knowledge"]:
            context_parts.append("\nRelevant knowledge:")
            for knowledge in enhanced_context["relevant_knowledge"][:2]:
                if knowledge["similarity"] > 0.6:
                    context_parts.append(f"- {knowledge['content'][:150]}")
        
        # Add personality context
        personality = enhanced_context["personality_insights"]
        if personality:
            context_parts.append(f"\nUser personality insights:")
            for trait, data in list(personality.items())[:3]:
                context_parts.append(f"- {trait}: {data['value']}")
        
        # Add entity context
        if enhanced_context["related_entities"]:
            context_parts.append(f"\nRelated entities:")
            for entity in enhanced_context["related_entities"][:3]:
                context_parts.append(f"- {entity['entity_id']}: {entity['type']}")
        
        return "\n".join(context_parts)
    
    def analyze_conversation_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Phân tích patterns trong conversations"""
        # Get recent conversations
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Use semantic search để find patterns
        common_topics = [
            "work", "technology", "personal", "help", "question", 
            "problem", "learn", "understand"
        ]
        
        topic_analysis = {}
        for topic in common_topics:
            results = self.vector_memory.search_conversations(topic, n_results=20)
            topic_analysis[topic] = {
                "count": len([r for r in results if r["similarity"] > 0.5]),
                "avg_similarity": sum(r["similarity"] for r in results) / len(results) if results else 0
            }
        
        # Knowledge graph analysis
        kg_stats = self.knowledge_graph.get_stats()
        
        # Personality evolution
        personality_summary = self.personality_graph.get_personality_summary()
        
        return {
            "analysis_period_days": days,
            "topic_frequency": topic_analysis,
            "knowledge_graph_stats": kg_stats,
            "personality_traits_count": len(personality_summary),
            "dominant_traits": list(personality_summary.keys())[:5],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def export_memory_snapshot(self, export_path: str = None) -> str:
        """Export snapshot của toàn bộ memory system"""
        if not export_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(self.data_dir, f"memory_snapshot_{timestamp}.json")
        
        # Collect data from all components
        snapshot = {
            "export_timestamp": datetime.now().isoformat(),
            "vector_db_stats": self.vector_memory.get_stats(),
            "knowledge_graph_stats": self.knowledge_graph.get_stats(),
            "personality_summary": self.personality_graph.get_personality_summary(),
            "memory_settings": self.settings,
            "conversation_patterns": self.analyze_conversation_patterns(30)
        }
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            
            print(f"📤 Memory snapshot exported to: {export_path}")
            return export_path
        except Exception as e:
            print(f"Export error: {e}")
            return ""
    
    def get_memory_insights(self) -> List[str]:
        """Đưa ra insights về memory system"""
        insights = []
        
        # Vector DB insights
        vector_stats = self.vector_memory.get_stats()
        if vector_stats.get("conversations", 0) > 50:
            insights.append(f"🗃️ Đã lưu trữ {vector_stats['conversations']} cuộc hội thoại")
        
        if vector_stats.get("knowledge_items", 0) > 10:
            insights.append(f"📚 Đã tích lũy {vector_stats['knowledge_items']} mục kiến thức")
        
        # Knowledge graph insights
        kg_stats = self.knowledge_graph.get_stats()
        if kg_stats.get("nodes", 0) > 20:
            insights.append(f"🕸️ Knowledge graph có {kg_stats['nodes']} entities với {kg_stats['edges']} connections")
        
        # Personality insights
        personality = self.personality_graph.get_personality_summary()
        if len(personality) > 3:
            traits = list(personality.keys())[:3]
            insights.append(f"👤 Đã nhận diện các traits: {', '.join(traits)}")
        
        # Usage patterns
        patterns = self.analyze_conversation_patterns(7)
        top_topics = sorted(
            patterns["topic_frequency"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:2]
        
        if top_topics:
            topic_names = [topic for topic, _ in top_topics]
            insights.append(f"💬 Chủ đề thường xuyên: {', '.join(topic_names)}")
        
        return insights
    
    def cleanup_and_optimize(self):
        """Dọn dẹp và tối ưu memory system"""
        print("🧹 Cleaning up and optimizing memory system...")
        
        # Cleanup old vector data
        self.vector_memory.cleanup_old_data(days=90)
        
        # Optimize knowledge graph (remove low-confidence entities)
        # This would need to be implemented in knowledge_graph.py
        
        print("✅ Memory system optimized")
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update memory settings"""
        self.settings.update(new_settings)
        self._save_settings()
        print("⚙️ Memory settings updated")