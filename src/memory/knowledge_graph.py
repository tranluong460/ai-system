"""
Knowledge Graph System cho AI Assistant
"""
import networkx as nx
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pickle
from collections import defaultdict

class KnowledgeGraph:
    """Knowledge Graph để lưu trữ relationships"""
    
    def __init__(self, data_dir: str = "data/knowledge_graph"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.graph_file = os.path.join(data_dir, "knowledge_graph.pkl")
        self.metadata_file = os.path.join(data_dir, "metadata.json")
        
        # Khởi tạo graph
        self.graph = nx.MultiDiGraph()
        self.metadata = {}
        
        # Load existing data
        self._load_graph()
        self._load_metadata()
        
        print("🕸️  Knowledge Graph initialized")
    
    def _load_graph(self):
        """Load graph từ file"""
        try:
            if os.path.exists(self.graph_file):
                with open(self.graph_file, 'rb') as f:
                    self.graph = pickle.load(f)
                print(f"📊 Loaded graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        except Exception as e:
            print(f"❌ Error loading graph: {e}")
            self.graph = nx.MultiDiGraph()
    
    def _save_graph(self):
        """Lưu graph vào file"""
        try:
            with open(self.graph_file, 'wb') as f:
                pickle.dump(self.graph, f)
        except Exception as e:
            print(f"❌ Error saving graph: {e}")
    
    def _load_metadata(self):
        """Load metadata"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            self.metadata = {}
    
    def _save_metadata(self):
        """Lưu metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
    
    def add_entity(self, entity_id: str, entity_type: str, 
                   properties: Dict[str, Any] = None) -> bool:
        """Thêm entity vào graph"""
        try:
            # Thêm node với properties
            node_attrs = {
                "type": entity_type,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if properties:
                node_attrs.update(properties)
            
            self.graph.add_node(entity_id, **node_attrs)
            
            # Update metadata
            if entity_type not in self.metadata:
                self.metadata[entity_type] = {"count": 0, "examples": []}
            
            self.metadata[entity_type]["count"] += 1
            if entity_id not in self.metadata[entity_type]["examples"]:
                self.metadata[entity_type]["examples"].append(entity_id)
                # Giới hạn examples
                if len(self.metadata[entity_type]["examples"]) > 10:
                    self.metadata[entity_type]["examples"] = \
                        self.metadata[entity_type]["examples"][-10:]
            
            self._save_graph()
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"❌ Error adding entity: {e}")
            return False
    
    def add_relationship(self, source: str, target: str, 
                        relation_type: str, properties: Dict[str, Any] = None) -> bool:
        """Thêm relationship giữa entities"""
        try:
            # Thêm nodes nếu chưa có
            if not self.graph.has_node(source):
                self.add_entity(source, "unknown")
            if not self.graph.has_node(target):
                self.add_entity(target, "unknown")
            
            # Thêm edge
            edge_attrs = {
                "type": relation_type,
                "created_at": datetime.now().isoformat(),
                "weight": 1.0
            }
            
            if properties:
                edge_attrs.update(properties)
            
            self.graph.add_edge(source, target, **edge_attrs)
            
            self._save_graph()
            return True
            
        except Exception as e:
            print(f"❌ Error adding relationship: {e}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin entity"""
        if self.graph.has_node(entity_id):
            return dict(self.graph.nodes[entity_id])
        return None
    
    def get_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Lấy tất cả relationships của entity"""
        relationships = []
        
        # Outgoing relationships
        for target in self.graph.successors(entity_id):
            for edge_key, edge_data in self.graph[entity_id][target].items():
                relationships.append({
                    "direction": "outgoing",
                    "source": entity_id,
                    "target": target,
                    "type": edge_data.get("type", "unknown"),
                    "properties": edge_data
                })
        
        # Incoming relationships
        for source in self.graph.predecessors(entity_id):
            for edge_key, edge_data in self.graph[source][entity_id].items():
                relationships.append({
                    "direction": "incoming",
                    "source": source,
                    "target": entity_id,
                    "type": edge_data.get("type", "unknown"),
                    "properties": edge_data
                })
        
        return relationships
    
    def find_path(self, source: str, target: str, max_length: int = 3) -> List[List[str]]:
        """Tìm đường đi giữa 2 entities"""
        try:
            paths = []
            for path in nx.all_simple_paths(self.graph, source, target, cutoff=max_length):
                paths.append(path)
            return paths[:10]  # Giới hạn 10 paths
        except:
            return []
    
    def get_neighbors(self, entity_id: str, hops: int = 1) -> Dict[str, List[str]]:
        """Lấy neighbors trong N hops"""
        neighbors = {"direct": [], "indirect": []}
        
        if not self.graph.has_node(entity_id):
            return neighbors
        
        # Direct neighbors (1 hop)
        direct = set()
        direct.update(self.graph.successors(entity_id))
        direct.update(self.graph.predecessors(entity_id))
        neighbors["direct"] = list(direct)
        
        # Indirect neighbors (2+ hops)
        if hops > 1:
            all_neighbors = set([entity_id])
            current_level = {entity_id}
            
            for hop in range(hops):
                next_level = set()
                for node in current_level:
                    next_level.update(self.graph.successors(node))
                    next_level.update(self.graph.predecessors(node))
                
                next_level -= all_neighbors  # Remove already visited
                all_neighbors.update(next_level)
                current_level = next_level
                
                if hop > 0:  # Skip first hop (direct neighbors)
                    neighbors["indirect"].extend(list(next_level))
        
        return neighbors
    
    def search_entities(self, query: str, entity_type: str = None) -> List[Dict[str, Any]]:
        """Tìm kiếm entities"""
        results = []
        query_lower = query.lower()
        
        for node_id, node_data in self.graph.nodes(data=True):
            # Filter by type if specified
            if entity_type and node_data.get("type") != entity_type:
                continue
            
            # Search in node_id and properties
            match_score = 0
            if query_lower in node_id.lower():
                match_score += 2
            
            # Search in properties
            for key, value in node_data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    match_score += 1
            
            if match_score > 0:
                results.append({
                    "entity_id": node_id,
                    "type": node_data.get("type", "unknown"),
                    "score": match_score,
                    "properties": node_data
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:20]  # Top 20 results
    
    def get_entity_importance(self, entity_id: str) -> Dict[str, float]:
        """Tính importance của entity"""
        if not self.graph.has_node(entity_id):
            return {"degree": 0, "betweenness": 0, "pagerank": 0}
        
        try:
            # Degree centrality
            degree = self.graph.degree(entity_id)
            
            # Betweenness centrality (expensive for large graphs)
            betweenness = 0
            if self.graph.number_of_nodes() < 1000:
                betweenness_dict = nx.betweenness_centrality(self.graph)
                betweenness = betweenness_dict.get(entity_id, 0)
            
            # PageRank
            pagerank = 0
            if self.graph.number_of_nodes() > 1:
                pagerank_dict = nx.pagerank(self.graph)
                pagerank = pagerank_dict.get(entity_id, 0)
            
            return {
                "degree": degree,
                "betweenness": betweenness,
                "pagerank": pagerank
            }
        except Exception as e:
            print(f"❌ Error calculating importance: {e}")
            return {"degree": 0, "betweenness": 0, "pagerank": 0}
    
    def get_clusters(self) -> Dict[str, List[str]]:
        """Tìm clusters trong graph"""
        try:
            # Convert to undirected for clustering
            undirected = self.graph.to_undirected()
            
            # Find connected components
            components = list(nx.connected_components(undirected))
            
            clusters = {}
            for i, component in enumerate(components):
                if len(component) > 1:  # Ignore single nodes
                    clusters[f"cluster_{i}"] = list(component)
            
            return clusters
        except Exception as e:
            print(f"❌ Error finding clusters: {e}")
            return {}
    
    def analyze_conversation_context(self, conversation: str) -> Dict[str, Any]:
        """Phân tích conversation để extract entities và relationships"""
        # Simple entity extraction (có thể improve bằng NLP)
        entities = []
        relationships = []
        
        # Extract potential entities (words, phrases)
        words = conversation.lower().split()
        potential_entities = []
        
        # Look for existing entities in graph
        for node_id in self.graph.nodes():
            if node_id.lower() in conversation.lower():
                potential_entities.append(node_id)
        
        return {
            "entities": potential_entities,
            "relationships": relationships,
            "conversation_length": len(words)
        }
    
    def update_entity_from_conversation(self, entity_id: str, conversation: str):
        """Cập nhật entity dựa trên conversation"""
        if self.graph.has_node(entity_id):
            # Update last_mentioned
            self.graph.nodes[entity_id]["last_mentioned"] = datetime.now().isoformat()
            self.graph.nodes[entity_id]["mention_count"] = \
                self.graph.nodes[entity_id].get("mention_count", 0) + 1
            
            # Update context
            current_context = self.graph.nodes[entity_id].get("recent_context", [])
            current_context.append({
                "conversation": conversation[:200],  # Truncate
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only recent context
            if len(current_context) > 5:
                current_context = current_context[-5:]
            
            self.graph.nodes[entity_id]["recent_context"] = current_context
            self._save_graph()
    
    def get_stats(self) -> Dict[str, Any]:
        """Thống kê knowledge graph"""
        try:
            stats = {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
                "entity_types": dict(self.metadata),
                "avg_degree": 0,
                "top_entities": []
            }
            
            if stats["nodes"] > 0:
                # Average degree
                degrees = [d for n, d in self.graph.degree()]
                stats["avg_degree"] = sum(degrees) / len(degrees)
                
                # Top entities by degree
                top_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)[:5]
                stats["top_entities"] = [{"entity": node, "degree": degree} for node, degree in top_nodes]
            
            return stats
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

class PersonalityGraph(KnowledgeGraph):
    """Specialized Knowledge Graph cho personality traits"""
    
    def __init__(self, data_dir: str = "data/personality_graph"):
        super().__init__(data_dir)
        self.personality_traits = [
            "communication_style", "interests", "preferences", 
            "expertise", "goals", "values", "habits"
        ]
    
    def add_personality_trait(self, trait_name: str, value: str, 
                            confidence: float = 1.0, context: str = ""):
        """Thêm personality trait"""
        trait_id = f"trait_{trait_name}"
        
        # Add trait entity
        self.add_entity(trait_id, "personality_trait", {
            "trait_name": trait_name,
            "value": value,
            "confidence": confidence,
            "context": context
        })
        
        # Connect to user entity
        user_id = "user_profile"
        self.add_entity(user_id, "user")
        self.add_relationship(user_id, trait_id, "has_trait", {
            "confidence": confidence,
            "discovered_at": datetime.now().isoformat()
        })
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt personality"""
        summary = {}
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("type") == "personality_trait":
                trait_name = node_data.get("trait_name")
                if trait_name:
                    summary[trait_name] = {
                        "value": node_data.get("value"),
                        "confidence": node_data.get("confidence", 1.0),
                        "context": node_data.get("context", "")
                    }
        
        return summary