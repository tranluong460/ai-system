"""
ChromaDB Vector Database Manager cho long-term memory
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

class ChromaMemoryManager:
    """Quản lý long-term memory với ChromaDB"""
    
    def __init__(self, db_path: str = "data/vector_db"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # Khởi tạo ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Load sentence transformer
        print("🧠 Loading sentence transformer...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collections
        self.conversations_collection = self._get_or_create_collection("conversations")
        self.knowledge_collection = self._get_or_create_collection("knowledge")
        self.personality_collection = self._get_or_create_collection("personality")
        
        print("✅ ChromaDB initialized successfully")
    
    def _get_or_create_collection(self, name: str):
        """Tạo hoặc lấy collection"""
        try:
            # Try to get existing collection
            return self.client.get_collection(name)
        except Exception as e:
            # Collection doesn't exist, create it
            try:
                print(f"Creating new collection: {name}")
                return self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as create_error:
                print(f"❌ Error creating collection {name}: {create_error}")
                # Try without metadata as fallback
                return self.client.create_collection(name=name)
    
    def add_conversation(self, user_input: str, ai_response: str, 
                        context: Dict[str, Any] = None) -> str:
        """Thêm conversation vào vector DB"""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Tạo document text
        full_text = f"User: {user_input}\nAI: {ai_response}"
        
        # Metadata
        metadata = {
            "timestamp": timestamp,
            "user_input": user_input,
            "ai_response": ai_response,
            "type": "conversation",
            "context": json.dumps(context or {})
        }
        
        # Thêm vào collection
        self.conversations_collection.add(
            documents=[full_text],
            metadatas=[metadata],
            ids=[conversation_id]
        )
        
        return conversation_id
    
    def search_conversations(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm conversations liên quan"""
        try:
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            conversations = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                conversations.append({
                    "document": doc,
                    "user_input": metadata.get("user_input", ""),
                    "ai_response": metadata.get("ai_response", ""),
                    "timestamp": metadata.get("timestamp", ""),
                    "similarity": 1 - distance,  # Convert distance to similarity
                    "context": json.loads(metadata.get("context", "{}"))
                })
            
            return conversations
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def add_knowledge(self, topic: str, content: str, 
                     source: str = "user", tags: List[str] = None) -> str:
        """Thêm knowledge vào DB"""
        knowledge_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        metadata = {
            "topic": topic,
            "source": source,
            "timestamp": timestamp,
            "tags": json.dumps(tags or []),
            "type": "knowledge"
        }
        
        self.knowledge_collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[knowledge_id]
        )
        
        return knowledge_id
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Tìm kiếm knowledge"""
        try:
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            knowledge_items = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                knowledge_items.append({
                    "content": doc,
                    "topic": metadata.get("topic", ""),
                    "source": metadata.get("source", ""),
                    "timestamp": metadata.get("timestamp", ""),
                    "tags": json.loads(metadata.get("tags", "[]")),
                    "similarity": 1 - distance
                })
            
            return knowledge_items
        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return []
    
    def update_personality_trait(self, trait: str, value: str, 
                               confidence: float = 1.0) -> str:
        """Cập nhật personality trait"""
        trait_id = f"trait_{trait}"
        timestamp = datetime.now().isoformat()
        
        # Xóa trait cũ nếu có
        try:
            self.personality_collection.delete(ids=[trait_id])
        except:
            pass
        
        metadata = {
            "trait": trait,
            "confidence": confidence,
            "timestamp": timestamp,
            "type": "personality"
        }
        
        self.personality_collection.add(
            documents=[value],
            metadatas=[metadata],
            ids=[trait_id]
        )
        
        return trait_id
    
    def get_personality_profile(self) -> Dict[str, Any]:
        """Lấy personality profile"""
        try:
            results = self.personality_collection.get(
                include=["documents", "metadatas"]
            )
            
            profile = {}
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                trait = metadata.get("trait")
                confidence = metadata.get("confidence", 1.0)
                
                profile[trait] = {
                    "value": doc,
                    "confidence": confidence,
                    "timestamp": metadata.get("timestamp")
                }
            
            return profile
        except Exception as e:
            print(f"❌ Personality profile error: {e}")
            return {}
    
    def get_conversation_context(self, query: str, n_results: int = 3) -> str:
        """Lấy context từ conversations trước"""
        conversations = self.search_conversations(query, n_results)
        
        if not conversations:
            return ""
        
        context_parts = []
        for conv in conversations:
            if conv["similarity"] > 0.7:  # Chỉ lấy conversations tương tự cao
                context_parts.append(
                    f"Previous context: {conv['user_input']} -> {conv['ai_response']}"
                )
        
        return "\n".join(context_parts)
    
    def get_relevant_knowledge(self, query: str) -> str:
        """Lấy knowledge liên quan"""
        knowledge_items = self.search_knowledge(query)
        
        if not knowledge_items:
            return ""
        
        knowledge_parts = []
        for item in knowledge_items:
            if item["similarity"] > 0.6:
                knowledge_parts.append(f"Knowledge: {item['content']}")
        
        return "\n".join(knowledge_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Thống kê vector DB"""
        try:
            conv_count = self.conversations_collection.count()
            knowledge_count = self.knowledge_collection.count()
            personality_count = self.personality_collection.count()
            
            return {
                "conversations": conv_count,
                "knowledge_items": knowledge_count,
                "personality_traits": personality_count,
                "total_entries": conv_count + knowledge_count + personality_count
            }
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Dọn dẹp dữ liệu cũ"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        try:
            # Lấy tất cả conversations
            results = self.conversations_collection.get(include=["metadatas"])
            
            ids_to_delete = []
            for i, metadata in enumerate(results["metadatas"]):
                timestamp_str = metadata.get("timestamp", "")
                try:
                    timestamp = datetime.fromisoformat(timestamp_str).timestamp()
                    if timestamp < cutoff_date:
                        ids_to_delete.append(results["ids"][i])
                except:
                    continue
            
            if ids_to_delete:
                self.conversations_collection.delete(ids=ids_to_delete)
                print(f"🗑️  Cleaned up {len(ids_to_delete)} old conversations")
        
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

class SemanticSearch:
    """Semantic search với nhiều strategies"""
    
    def __init__(self, chroma_manager: ChromaMemoryManager):
        self.chroma = chroma_manager
    
    def search_all(self, query: str, n_results: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Tìm kiếm trên tất cả collections"""
        return {
            "conversations": self.chroma.search_conversations(query, n_results),
            "knowledge": self.chroma.search_knowledge(query, n_results),
        }
    
    def find_similar_situations(self, current_input: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Tìm situations tương tự"""
        conversations = self.chroma.search_conversations(current_input, n_results=10)
        
        similar_situations = []
        for conv in conversations:
            if conv["similarity"] >= threshold:
                similar_situations.append({
                    "situation": conv["user_input"],
                    "response": conv["ai_response"],
                    "similarity": conv["similarity"],
                    "timestamp": conv["timestamp"]
                })
        
        return similar_situations
    
    def extract_insights(self, query: str) -> Dict[str, Any]:
        """Trích xuất insights từ search results"""
        all_results = self.search_all(query)
        
        insights = {
            "total_matches": 0,
            "high_confidence_matches": 0,
            "topics_mentioned": [],
            "response_patterns": [],
            "knowledge_gaps": []
        }
        
        # Phân tích conversations
        for conv in all_results["conversations"]:
            insights["total_matches"] += 1
            if conv["similarity"] > 0.8:
                insights["high_confidence_matches"] += 1
                insights["response_patterns"].append(conv["ai_response"][:100])
        
        # Phân tích knowledge
        for knowledge in all_results["knowledge"]:
            insights["topics_mentioned"].append(knowledge["topic"])
        
        return insights