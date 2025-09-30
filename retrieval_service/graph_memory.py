"""
Neural Graph Memory System
Advanced relationship mapping and reasoning over code/docs/conversations
"""

import networkx as nx
import numpy as np
import sqlite3
import json
import logging
from typing import List, Dict, Tuple, Optional, Set, Any
from pathlib import Path
from datetime import datetime
import pickle
import ast
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class NeuralGraphMemory:
    """
    Advanced graph-based memory system for reasoning over relationships
    Features:
    - Multi-modal nodes (code, docs, conversations, edits)
    - Semantic similarity edges from FAISS HNSW
    - Dependency edges from code analysis
    - Temporal edges from edit history
    - Reasoning via graph traversal algorithms
    """
    
    def __init__(self, graph_path: str = "~/.local/share/haasp/knowledge_graph.gpickle"):
        self.graph_path = Path(graph_path).expanduser()
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.embeddings_cache = {}  # Node ID -> embedding vector
        
        # Node type registry
        self.node_types = {
            "document": {"color": "#4CAF50", "shape": "rectangle"},
            "function": {"color": "#2196F3", "shape": "ellipse"},
            "class": {"color": "#FF9800", "shape": "diamond"},
            "conversation": {"color": "#9C27B0", "shape": "circle"},
            "edit": {"color": "#F44336", "shape": "triangle"},
            "error": {"color": "#795548", "shape": "hexagon"}
        }
        
        # Edge type registry
        self.edge_types = {
            "similarity": {"weight_range": (0.0, 1.0), "color": "#2196F3"},
            "dependency": {"weight_range": (0.0, 1.0), "color": "#4CAF50"},
            "temporal": {"weight_range": (0.0, 1.0), "color": "#FF9800"},
            "conversation": {"weight_range": (0.0, 1.0), "color": "#9C27B0"},
            "edit_relation": {"weight_range": (0.0, 1.0), "color": "#F44336"}
        }
        
        self.load_graph()
        logger.info(f"NeuralGraphMemory initialized with {self.graph.number_of_nodes()} nodes")
    
    def add_node(self, node_id: str, node_type: str, content: str, 
                metadata: Dict = None, embedding: np.ndarray = None) -> bool:
        """Add a new node to the knowledge graph"""
        try:
            if metadata is None:
                metadata = {}
            
            # Node attributes
            attrs = {
                "type": node_type,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "content_hash": hash(content)
            }
            
            # Add visual attributes for graph rendering
            if node_type in self.node_types:
                attrs.update(self.node_types[node_type])
            
            self.graph.add_node(node_id, **attrs)
            
            # Cache embedding if provided
            if embedding is not None:
                self.embeddings_cache[node_id] = embedding
            
            logger.debug(f"Added {node_type} node: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            return False
    
    def add_edge(self, source: str, target: str, edge_type: str, 
                weight: float, metadata: Dict = None) -> bool:
        """Add relationship edge between nodes"""
        try:
            if source not in self.graph or target not in self.graph:
                logger.warning(f"Edge source or target not found: {source} -> {target}")
                return False
            
            edge_attrs = {
                "type": edge_type,
                "weight": weight,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }
            
            # Add visual attributes
            if edge_type in self.edge_types:
                edge_attrs.update(self.edge_types[edge_type])
            
            self.graph.add_edge(source, target, **edge_attrs)
            
            logger.debug(f"Added {edge_type} edge: {source} -> {target} (weight: {weight:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add edge {source} -> {target}: {e}")
            return False
    
    def add_similarity_edges_from_faiss(self, faiss_index, doc_mapping: Dict, 
                                      similarity_threshold: float = 0.7):
        """
        Extract similarity edges from FAISS HNSW graph
        Connect semantically similar documents/chunks
        """
        try:
            if faiss_index is None or faiss_index.ntotal == 0:
                return
            
            logger.info("Extracting similarity edges from FAISS index...")
            
            # For each vector in the index, get its neighbors
            for i in range(faiss_index.ntotal):
                # Get k nearest neighbors
                query_vector = faiss_index.reconstruct(i).reshape(1, -1)
                scores, neighbors = faiss_index.search(query_vector, k=10)
                
                source_doc = doc_mapping.get(i)
                if not source_doc:
                    continue
                
                for j, neighbor_id in enumerate(neighbors[0]):
                    if neighbor_id == i or neighbor_id < 0:  # Skip self and invalid
                        continue
                    
                    target_doc = doc_mapping.get(neighbor_id)
                    if not target_doc:
                        continue
                    
                    similarity = float(scores[0][j])
                    if similarity >= similarity_threshold:
                        self.add_edge(
                            source_doc, target_doc, "similarity", 
                            similarity, {"faiss_rank": j}
                        )
            
            logger.info(f"Added similarity edges from FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to extract FAISS edges: {e}")
    
    def analyze_code_dependencies(self, file_path: str, content: str, language: str) -> List[Tuple[str, str]]:
        """Extract code dependencies using AST analysis"""
        dependencies = []
        
        try:
            if language == "python":
                dependencies.extend(self._analyze_python_dependencies(content))
            elif language in ["cpp", "c", "hpp", "h"]:
                dependencies.extend(self._analyze_cpp_dependencies(content))
            elif language == "qml":
                dependencies.extend(self._analyze_qml_dependencies(content))
            
        except Exception as e:
            logger.error(f"Dependency analysis failed for {file_path}: {e}")
        
        return dependencies
    
    def _analyze_python_dependencies(self, content: str) -> List[Tuple[str, str]]:
        """Analyze Python imports and function calls"""
        dependencies = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(("import", alias.name))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            dependencies.append(("import_from", f"{node.module}.{alias.name}"))
                
                elif isinstance(node, ast.FunctionDef):
                    dependencies.append(("defines_function", node.name))
                
                elif isinstance(node, ast.ClassDef):
                    dependencies.append(("defines_class", node.name))
        
        except SyntaxError:
            # Fallback to regex for malformed Python
            dependencies.extend(self._regex_python_dependencies(content))
        
        return dependencies
    
    def _analyze_cpp_dependencies(self, content: str) -> List[Tuple[str, str]]:
        """Analyze C++ includes and declarations"""
        dependencies = []
        
        # Include statements
        includes = re.findall(r'#include\s*[<"](.*?)[>"]', content)
        for include in includes:
            dependencies.append(("includes", include))
        
        # Class declarations
        classes = re.findall(r'class\s+(\w+)', content)
        for cls in classes:
            dependencies.append(("defines_class", cls))
        
        # Function declarations
        functions = re.findall(r'(?:void|int|bool|float|double|auto)\s+(\w+)\s*\(', content)
        for func in functions:
            dependencies.append(("defines_function", func))
        
        # Namespace usage
        namespaces = re.findall(r'(\w+)::', content)
        for ns in set(namespaces):
            dependencies.append(("uses_namespace", ns))
        
        return dependencies
    
    def _analyze_qml_dependencies(self, content: str) -> List[Tuple[str, str]]:
        """Analyze QML imports and component usage"""
        dependencies = []
        
        # Import statements
        imports = re.findall(r'import\s+([\w.]+)', content)
        for imp in imports:
            dependencies.append(("imports", imp))
        
        # Property definitions
        properties = re.findall(r'property\s+\w+\s+(\w+)', content)
        for prop in properties:
            dependencies.append(("defines_property", prop))
        
        # Signal definitions
        signals = re.findall(r'signal\s+(\w+)', content)
        for signal in signals:
            dependencies.append(("defines_signal", signal))
        
        # Component usage
        components = re.findall(r'^[ ]*(\w+)\s*{', content, re.MULTILINE)
        for component in set(components):
            if component[0].isupper():  # QML components start with uppercase
                dependencies.append(("uses_component", component))
        
        return dependencies
    
    def _regex_python_dependencies(self, content: str) -> List[Tuple[str, str]]:
        """Fallback regex-based Python analysis"""
        dependencies = []
        
        # Import statements
        imports = re.findall(r'import\s+([\w.]+)', content)
        for imp in imports:
            dependencies.append(("import", imp))
        
        from_imports = re.findall(r'from\s+([\w.]+)\s+import\s+([\w,\s]+)', content)
        for module, names in from_imports:
            for name in names.split(','):
                dependencies.append(("import_from", f"{module}.{name.strip()}"))
        
        return dependencies
    
    def add_code_file(self, file_path: str, content: str, language: str) -> str:
        """Add code file with automatic dependency analysis"""
        try:
            # Create node for the file
            file_id = f"file::{file_path}"
            
            self.add_node(
                file_id, "document", content,
                metadata={
                    "file_path": file_path,
                    "language": language,
                    "line_count": content.count('\n') + 1,
                    "size": len(content)
                }
            )
            
            # Analyze dependencies
            dependencies = self.analyze_code_dependencies(file_path, content, language)
            
            # Add dependency edges
            for dep_type, dep_name in dependencies:
                dep_id = f"{dep_type}::{dep_name}"
                
                # Create dependency node if it doesn't exist
                if not self.graph.has_node(dep_id):
                    self.add_node(dep_id, dep_type, dep_name)
                
                # Add edge
                self.add_edge(file_id, dep_id, "dependency", 1.0, {"type": dep_type})
            
            logger.info(f"Added code file {file_path} with {len(dependencies)} dependencies")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to add code file {file_path}: {e}")
            return ""
    
    def query_neighbors(self, node_id: str, max_depth: int = 2, 
                       edge_types: List[str] = None) -> Dict[str, List[Dict]]:
        """Query node neighborhood for reasoning"""
        try:
            if node_id not in self.graph:
                return {"neighbors": []}
            
            neighbors_by_depth = defaultdict(list)
            visited = set()
            queue = [(node_id, 0)]
            
            while queue:
                current_node, depth = queue.pop(0)
                
                if depth > max_depth or current_node in visited:
                    continue
                
                visited.add(current_node)
                
                # Get direct neighbors
                for neighbor in self.graph.neighbors(current_node):
                    edge_data = self.graph.edges[current_node, neighbor]
                    
                    # Filter by edge type if specified
                    if edge_types and edge_data.get("type") not in edge_types:
                        continue
                    
                    neighbor_info = {
                        "node_id": neighbor,
                        "node_type": self.graph.nodes[neighbor].get("type", "unknown"),
                        "edge_type": edge_data.get("type", "unknown"),
                        "weight": edge_data.get("weight", 0.0),
                        "depth": depth + 1,
                        "content_preview": self.graph.nodes[neighbor].get("content", "")[:100]
                    }
                    
                    neighbors_by_depth[depth + 1].append(neighbor_info)
                    
                    # Add to queue for next depth
                    if depth + 1 < max_depth:
                        queue.append((neighbor, depth + 1))
            
            return dict(neighbors_by_depth)
            
        except Exception as e:
            logger.error(f"Neighbor query failed for {node_id}: {e}")
            return {"neighbors": []}
    
    def reasoning_walk(self, start_nodes: List[str], goal_type: str, 
                      max_steps: int = 5) -> List[Dict]:
        """
        Perform reasoning walk to find nodes of specific type
        Uses multiple graph algorithms for comprehensive search
        """
        try:
            results = []
            
            for start_node in start_nodes:
                if start_node not in self.graph:
                    continue
                
                # Strategy 1: Breadth-first search
                bfs_results = self._bfs_search(start_node, goal_type, max_steps)
                results.extend(bfs_results)
                
                # Strategy 2: PageRank-guided search
                pagerank_results = self._pagerank_search(start_node, goal_type, max_steps)
                results.extend(pagerank_results)
                
                # Strategy 3: Shortest path search
                shortest_results = self._shortest_path_search(start_node, goal_type, max_steps)
                results.extend(shortest_results)
            
            # Deduplicate and rank results
            seen = set()
            final_results = []
            
            for result in results:
                if result["node_id"] not in seen:
                    seen.add(result["node_id"])
                    final_results.append(result)
            
            # Sort by composite score
            final_results.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Reasoning walk failed: {e}")
            return []
    
    def _bfs_search(self, start_node: str, goal_type: str, max_steps: int) -> List[Dict]:
        """Breadth-first search for goal type"""
        results = []
        visited = set()
        queue = [(start_node, 0, [])]  # (node, depth, path)
        
        while queue and len(results) < 10:
            current, depth, path = queue.pop(0)
            
            if depth > max_steps or current in visited:
                continue
            
            visited.add(current)
            
            # Check if this is a goal node
            node_type = self.graph.nodes[current].get("type", "")
            if node_type == goal_type and current != start_node:
                results.append({
                    "node_id": current,
                    "path": path + [current],
                    "depth": depth,
                    "method": "bfs",
                    "composite_score": 1.0 / (depth + 1)  # Closer is better
                })
            
            # Add neighbors to queue
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1, path + [current]))
        
        return results
    
    def _pagerank_search(self, start_node: str, goal_type: str, max_steps: int) -> List[Dict]:
        """PageRank-guided search for important nodes"""
        try:
            # Compute PageRank scores
            pagerank = nx.pagerank(self.graph, weight='weight')
            
            # Find goal type nodes within max_steps
            goal_nodes = []
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get("type") == goal_type:
                    try:
                        path_length = nx.shortest_path_length(self.graph, start_node, node_id)
                        if path_length <= max_steps:
                            goal_nodes.append({
                                "node_id": node_id,
                                "pagerank_score": pagerank.get(node_id, 0),
                                "path_length": path_length,
                                "method": "pagerank",
                                "composite_score": pagerank.get(node_id, 0) / (path_length + 1)
                            })
                    except nx.NetworkXNoPath:
                        continue
            
            return goal_nodes
            
        except Exception as e:
            logger.error(f"PageRank search failed: {e}")
            return []
    
    def _shortest_path_search(self, start_node: str, goal_type: str, max_steps: int) -> List[Dict]:
        """Find shortest paths to goal type nodes"""
        results = []
        
        try:
            # Find all nodes of goal type
            goal_nodes = [
                node_id for node_id, data in self.graph.nodes(data=True)
                if data.get("type") == goal_type
            ]
            
            for goal_node in goal_nodes:
                try:
                    path = nx.shortest_path(self.graph, start_node, goal_node, weight='weight')
                    if len(path) <= max_steps + 1:  # +1 because path includes start and end
                        # Calculate path weight
                        path_weight = 0
                        for i in range(len(path) - 1):
                            edge_data = self.graph.edges[path[i], path[i+1]]
                            path_weight += edge_data.get("weight", 0)
                        
                        results.append({
                            "node_id": goal_node,
                            "path": path,
                            "path_length": len(path) - 1,
                            "path_weight": path_weight,
                            "method": "shortest_path",
                            "composite_score": path_weight / len(path)
                        })
                        
                except nx.NetworkXNoPath:
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Shortest path search failed: {e}")
            return []
    
    def add_conversation_context(self, utterance: str, pilot_id: str, 
                               related_docs: List[str] = None) -> str:
        """Add conversation with automatic context linking"""
        try:
            # Create conversation node
            conv_id = f"conversation::{pilot_id}::{datetime.now().isoformat()}"
            
            self.add_node(conv_id, "conversation", utterance, metadata={
                "pilot_id": pilot_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Link to related documents if provided
            if related_docs:
                for doc_id in related_docs:
                    if self.graph.has_node(doc_id):
                        self.add_edge(conv_id, doc_id, "conversation", 0.8)
            
            # Auto-link to semantically similar content
            self._auto_link_conversation(conv_id, utterance)
            
            return conv_id
            
        except Exception as e:
            logger.error(f"Failed to add conversation context: {e}")
            return ""
    
    def _auto_link_conversation(self, conv_id: str, utterance: str):
        """Automatically link conversation to related graph nodes"""
        try:
            # Simple keyword matching for auto-linking
            keywords = re.findall(r'\b\w{3,}\b', utterance.lower())
            
            for node_id, node_data in self.graph.nodes(data=True):
                content = node_data.get("content", "").lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in content)
                
                if matches >= 2:  # Threshold for relevance
                    similarity = matches / len(keywords)
                    self.add_edge(conv_id, node_id, "conversation", similarity)
                    
        except Exception as e:
            logger.error(f"Auto-linking failed: {e}")
    
    def get_hotspots(self, limit: int = 10) -> List[Dict]:
        """Identify highly connected nodes (hotspots)"""
        try:
            # Calculate centrality metrics
            betweenness = nx.betweenness_centrality(self.graph, weight='weight')
            degree = dict(self.graph.degree(weight='weight'))
            closeness = nx.closeness_centrality(self.graph)
            
            # Combine metrics for hotspot score
            hotspots = []
            for node_id in self.graph.nodes():
                hotspot_score = (
                    betweenness.get(node_id, 0) * 0.4 +
                    (degree.get(node_id, 0) / max(degree.values(), default=1)) * 0.4 +
                    closeness.get(node_id, 0) * 0.2
                )
                
                node_data = self.graph.nodes[node_id]
                hotspots.append({
                    "node_id": node_id,
                    "node_type": node_data.get("type", "unknown"),
                    "hotspot_score": hotspot_score,
                    "betweenness": betweenness.get(node_id, 0),
                    "degree": degree.get(node_id, 0),
                    "closeness": closeness.get(node_id, 0),
                    "content_preview": node_data.get("content", "")[:100]
                })
            
            # Sort by hotspot score
            hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)
            
            return hotspots[:limit]
            
        except Exception as e:
            logger.error(f"Hotspot analysis failed: {e}")
            return []
    
    def save_graph(self, path: str = None):
        """Persist graph to disk"""
        try:
            if path is None:
                path = str(self.graph_path)
            
            with open(path, 'wb') as f:
                pickle.dump({
                    "graph": self.graph,
                    "embeddings_cache": self.embeddings_cache
                }, f)
            
            logger.info(f"Saved graph with {self.graph.number_of_nodes()} nodes to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
    
    def load_graph(self, path: str = None) -> bool:
        """Load graph from disk"""
        try:
            if path is None:
                path = str(self.graph_path)
            
            if not Path(path).exists():
                logger.info("No existing graph found, starting with empty graph")
                return True
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.graph = data["graph"]
                self.embeddings_cache = data.get("embeddings_cache", {})
            
            logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False
    
    def export_for_visualization(self, format: str = "json") -> Dict[str, Any]:
        """Export graph data for visualization in WebApp"""
        try:
            if format == "json":
                # Convert NetworkX graph to JSON format for D3.js/vis.js
                nodes = []
                edges = []
                
                for node_id, node_data in self.graph.nodes(data=True):
                    nodes.append({
                        "id": node_id,
                        "type": node_data.get("type", "unknown"),
                        "content_preview": node_data.get("content", "")[:50],
                        "metadata": node_data.get("metadata", {}),
                        "visual": {
                            "color": node_data.get("color", "#666666"),
                            "shape": node_data.get("shape", "circle")
                        }
                    })
                
                for source, target, edge_data in self.graph.edges(data=True):
                    edges.append({
                        "source": source,
                        "target": target,
                        "type": edge_data.get("type", "unknown"),
                        "weight": edge_data.get("weight", 0.0),
                        "visual": {
                            "color": edge_data.get("color", "#999999")
                        }
                    })
                
                return {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "total_nodes": len(nodes),
                        "total_edges": len(edges),
                        "node_types": list(set(n["type"] for n in nodes)),
                        "edge_types": list(set(e["type"] for e in edges)),
                        "exported_at": datetime.now().isoformat()
                    }
                }
            
        except Exception as e:
            logger.error(f"Graph export failed: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        try:
            stats = {
                "nodes": {
                    "total": self.graph.number_of_nodes(),
                    "by_type": defaultdict(int)
                },
                "edges": {
                    "total": self.graph.number_of_edges(),
                    "by_type": defaultdict(int)
                },
                "connectivity": {
                    "density": nx.density(self.graph),
                    "connected_components": nx.number_weakly_connected_components(self.graph),
                    "average_clustering": nx.average_clustering(self.graph.to_undirected()) if self.graph.number_of_nodes() > 0 else 0
                },
                "centrality": {
                    "most_central": self._get_most_central_nodes(5)
                }
            }
            
            # Count nodes by type
            for node_id, node_data in self.graph.nodes(data=True):
                node_type = node_data.get("type", "unknown")
                stats["nodes"]["by_type"][node_type] += 1
            
            # Count edges by type
            for _, _, edge_data in self.graph.edges(data=True):
                edge_type = edge_data.get("type", "unknown")
                stats["edges"]["by_type"][edge_type] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {}
    
    def _get_most_central_nodes(self, limit: int) -> List[Dict]:
        """Get most central nodes for hotspot identification"""
        try:
            if self.graph.number_of_nodes() == 0:
                return []
            
            centrality = nx.degree_centrality(self.graph)
            
            central_nodes = []
            for node_id, centrality_score in sorted(centrality.items(), 
                                                   key=lambda x: x[1], reverse=True)[:limit]:
                node_data = self.graph.nodes[node_id]
                central_nodes.append({
                    "node_id": node_id,
                    "centrality_score": centrality_score,
                    "node_type": node_data.get("type", "unknown"),
                    "content_preview": node_data.get("content", "")[:50]
                })
            
            return central_nodes
            
        except Exception as e:
            logger.error(f"Central nodes calculation failed: {e}")
            return []