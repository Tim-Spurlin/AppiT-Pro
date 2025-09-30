"""
Fuzzy Search Manager using SQLite FTS5 with trigram tokenization
Enables substring matching, wildcard search, and approximate string matching
"""

import sqlite3
import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import Levenshtein  # pip install python-Levenshtein
from datetime import datetime

logger = logging.getLogger(__name__)

class FuzzySearchManager:
    """
    Advanced fuzzy and substring search capabilities
    Features:
    - SQLite FTS5 with trigram tokenizer for substring matching
    - Wildcard and case-insensitive search
    - Levenshtein distance for approximate matching
    - Integration with vector search via RRF (Reciprocal Rank Fusion)
    """
    
    def __init__(self, db_path: str = "~/.local/share/haasp/fuzzy_search.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
        logger.info(f"FuzzySearchManager initialized with database at {self.db_path}")
    
    def init_database(self):
        """Initialize SQLite database with FTS5 tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Enable FTS5 extension
        conn.enable_load_extension(True)
        
        # Create FTS5 table with trigram tokenizer for substring search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                content,
                path,
                doc_id,
                metadata,
                tokenize = 'trigram case_sensitive 0'
            )
        """)
        
        # Create regular table for metadata and exact matches
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT UNIQUE,
                file_path TEXT,
                language TEXT,
                size_bytes INTEGER,
                line_count INTEGER,
                content_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for fast lookups
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_id ON documents_meta(doc_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON documents_meta(file_path)")
        
        conn.commit()
        conn.close()
    
    def add_document(self, doc_id: str, content: str, file_path: str, 
                    language: str = "", metadata: Dict = None) -> bool:
        """Add document to fuzzy search index"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Insert into FTS5 table for search
            conn.execute("""
                INSERT OR REPLACE INTO documents_fts (content, path, doc_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (content, file_path, doc_id, str(metadata or {})))
            
            # Insert metadata
            content_hash = hash(content)
            line_count = content.count('\n') + 1
            size_bytes = len(content.encode('utf-8'))
            
            conn.execute("""
                INSERT OR REPLACE INTO documents_meta 
                (doc_id, file_path, language, size_bytes, line_count, content_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, file_path, language, size_bytes, line_count, content_hash))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Added document to FTS: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to FTS: {e}")
            return False
    
    def query_fuzzy(self, query: str, k: int = 10, include_snippets: bool = True) -> List[Dict]:
        """
        Fuzzy search with multiple matching strategies
        """
        results = []
        
        # Strategy 1: Exact FTS5 search
        exact_results = self._fts5_search(query, k)
        results.extend(exact_results)
        
        # Strategy 2: Wildcard search for partial matches
        wildcard_results = self._wildcard_search(query, k)
        results.extend(wildcard_results)
        
        # Strategy 3: Levenshtein approximate matching
        if len(results) < k:
            approx_results = self._levenshtein_search(query, k - len(results))
            results.extend(approx_results)
        
        # Deduplicate and sort by score
        seen = set()
        deduped = []
        for result in results:
            if result["doc_id"] not in seen:
                seen.add(result["doc_id"])
                deduped.append(result)
        
        # Sort by score (higher is better)
        deduped.sort(key=lambda x: x["score"], reverse=True)
        
        return deduped[:k]
    
    def _fts5_search(self, query: str, k: int) -> List[Dict]:
        """FTS5 full-text search with trigram tokenization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Escape special characters for FTS5
            escaped_query = self._escape_fts5_query(query)
            
            cursor = conn.execute("""
                SELECT content, path, doc_id, 
                       bm25(documents_fts) as score,
                       snippet(documents_fts, 0, '<mark>', '</mark>', '...', 64) as snippet
                FROM documents_fts 
                WHERE documents_fts MATCH ?
                ORDER BY score DESC
                LIMIT ?
            """, (escaped_query, k))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "content": row[0][:500] + "..." if len(row[0]) > 500 else row[0],
                    "file_path": row[1],
                    "doc_id": row[2],
                    "score": float(row[3]),
                    "snippet": row[4],
                    "type": "fts5_exact"
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"FTS5 search failed: {e}")
            return []
    
    def _wildcard_search(self, query: str, k: int) -> List[Dict]:
        """Wildcard search for partial identifier matching"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Create wildcard patterns
            patterns = [
                f"*{query}*",      # Contains
                f"{query}*",       # Starts with  
                f"*{query}",       # Ends with
            ]
            
            results = []
            for pattern in patterns:
                cursor = conn.execute("""
                    SELECT content, path, doc_id,
                           rank as score
                    FROM documents_fts 
                    WHERE documents_fts MATCH ?
                    ORDER BY score DESC
                    LIMIT ?
                """, (pattern, k // len(patterns) + 1))
                
                for row in cursor.fetchall():
                    results.append({
                        "content": row[0][:500] + "..." if len(row[0]) > 500 else row[0],
                        "file_path": row[1],
                        "doc_id": row[2],
                        "score": float(row[3]) * 0.8,  # Lower weight for wildcard
                        "type": "wildcard"
                    })
            
            conn.close()
            return results[:k]
            
        except Exception as e:
            logger.error(f"Wildcard search failed: {e}")
            return []
    
    def _levenshtein_search(self, query: str, k: int, max_distance: int = 3) -> List[Dict]:
        """Approximate string matching using Levenshtein distance"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get all document content for approximate matching
            # For performance, limit to smaller documents or use sampling
            cursor = conn.execute("""
                SELECT content, path, doc_id, size_bytes
                FROM documents_fts f
                JOIN documents_meta m ON f.doc_id = m.doc_id
                WHERE m.size_bytes < 50000  -- Limit to smaller files
                ORDER BY m.updated_at DESC
                LIMIT 1000
            """)
            
            results = []
            query_lower = query.lower()
            
            for row in cursor.fetchall():
                content, path, doc_id, size = row
                content_lower = content.lower()
                
                # Find approximate matches in content
                words = re.findall(r'\b\w+\b', content_lower)
                best_distance = float('inf')
                best_match = ""
                
                for word in words:
                    if len(word) > 2:  # Skip very short words
                        distance = Levenshtein.distance(query_lower, word)
                        if distance < best_distance and distance <= max_distance:
                            best_distance = distance
                            best_match = word
                
                if best_distance <= max_distance:
                    # Score based on inverse distance (closer = higher score)
                    score = 1.0 / (1.0 + best_distance)
                    
                    results.append({
                        "content": content[:300] + "..." if len(content) > 300 else content,
                        "file_path": path,
                        "doc_id": doc_id,
                        "score": score * 0.6,  # Lower weight for approximate
                        "match": best_match,
                        "distance": best_distance,
                        "type": "levenshtein"
                    })
            
            conn.close()
            
            # Sort by score and return top k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Levenshtein search failed: {e}")
            return []
    
    def _escape_fts5_query(self, query: str) -> str:
        """Escape special characters for FTS5 queries"""
        # Escape FTS5 special characters
        special_chars = '"*'
        for char in special_chars:
            query = query.replace(char, f'"{char}"')
        return query
    
    def update_document(self, doc_id: str, new_content: str, file_path: str = "") -> bool:
        """Update existing document in search index"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Update FTS5 table
            conn.execute("""
                UPDATE documents_fts 
                SET content = ?, path = ?
                WHERE doc_id = ?
            """, (new_content, file_path, doc_id))
            
            # Update metadata
            new_hash = hash(new_content)
            new_line_count = new_content.count('\n') + 1
            new_size = len(new_content.encode('utf-8'))
            
            conn.execute("""
                UPDATE documents_meta 
                SET content_hash = ?, line_count = ?, size_bytes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE doc_id = ?
            """, (new_hash, new_line_count, new_size, doc_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Updated document in FTS: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Remove document from search index"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("DELETE FROM documents_fts WHERE doc_id = ?", (doc_id,))
            conn.execute("DELETE FROM documents_meta WHERE doc_id = ?", (doc_id,))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Deleted document from FTS: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def search_by_file_type(self, query: str, file_extensions: List[str], k: int = 10) -> List[Dict]:
        """Search within specific file types"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Build file extension filter
            ext_patterns = [f"%.{ext}" for ext in file_extensions]
            ext_filter = " OR ".join(["path LIKE ?" for _ in ext_patterns])
            
            cursor = conn.execute(f"""
                SELECT f.content, f.path, f.doc_id, bm25(documents_fts) as score
                FROM documents_fts f
                JOIN documents_meta m ON f.doc_id = m.doc_id
                WHERE documents_fts MATCH ? AND ({ext_filter})
                ORDER BY score DESC
                LIMIT ?
            """, [query] + ext_patterns + [k])
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "content": row[0][:400] + "..." if len(row[0]) > 400 else row[0],
                    "file_path": row[1],
                    "doc_id": row[2],
                    "score": float(row[3]),
                    "type": "filetype_filtered"
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"File type search failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get FTS database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Document count by language
            cursor = conn.execute("""
                SELECT language, COUNT(*) as count
                FROM documents_meta 
                GROUP BY language
                ORDER BY count DESC
            """)
            language_stats = dict(cursor.fetchall())
            
            # Total documents and size
            cursor = conn.execute("""
                SELECT COUNT(*) as total_docs, 
                       SUM(size_bytes) as total_size,
                       AVG(line_count) as avg_lines
                FROM documents_meta
            """)
            totals = cursor.fetchone()
            
            # Recent activity
            cursor = conn.execute("""
                SELECT COUNT(*) as recent_updates
                FROM documents_meta
                WHERE updated_at > datetime('now', '-24 hours')
            """)
            recent = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_documents": totals[0] if totals else 0,
                "total_size_bytes": totals[1] if totals else 0,
                "average_lines": totals[2] if totals else 0,
                "recent_updates_24h": recent[0] if recent else 0,
                "languages": language_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get FTS statistics: {e}")
            return {}

class ReciprocalRankFusion:
    """
    Combine results from multiple search engines using RRF
    Based on: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
    """
    
    def __init__(self, k: int = 60):
        self.k = k  # RRF constant
    
    def fuse_results(self, 
                    vector_results: List[Dict],
                    fuzzy_results: List[Dict], 
                    weights: Dict[str, float] = None) -> List[Dict]:
        """
        Fuse vector and fuzzy search results using RRF
        """
        if weights is None:
            weights = {"vector": 0.6, "fuzzy": 0.4}
        
        # Create unified scoring
        doc_scores = {}
        doc_metadata = {}
        
        # Process vector results
        for rank, result in enumerate(vector_results):
            doc_id = result["doc_id"]
            rrf_score = weights["vector"] / (self.k + rank + 1)
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_metadata[doc_id] = result
            
            doc_scores[doc_id] += rrf_score
            doc_metadata[doc_id]["vector_rank"] = rank
            doc_metadata[doc_id]["vector_score"] = result.get("score", 0)
        
        # Process fuzzy results
        for rank, result in enumerate(fuzzy_results):
            doc_id = result["doc_id"]
            rrf_score = weights["fuzzy"] / (self.k + rank + 1)
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_metadata[doc_id] = result
            
            doc_scores[doc_id] += rrf_score
            
            # Merge metadata
            if doc_id in doc_metadata:
                doc_metadata[doc_id]["fuzzy_rank"] = rank
                doc_metadata[doc_id]["fuzzy_score"] = result.get("score", 0)
                doc_metadata[doc_id]["fuzzy_type"] = result.get("type", "")
            
        # Create final ranked results
        fused_results = []
        for doc_id, final_score in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True):
            result = doc_metadata[doc_id].copy()
            result["fused_score"] = final_score
            result["fusion_method"] = "RRF"
            fused_results.append(result)
        
        return fused_results
    
    def explain_fusion(self, fused_results: List[Dict]) -> Dict[str, Any]:
        """Explain how fusion scores were calculated"""
        explanation = {
            "method": "Reciprocal Rank Fusion",
            "k_constant": self.k,
            "formula": "score = sum(weight / (k + rank + 1)) for each result list",
            "results_breakdown": []
        }
        
        for result in fused_results[:5]:  # Top 5 explanations
            breakdown = {
                "doc_id": result["doc_id"],
                "final_score": result["fused_score"],
                "components": {}
            }
            
            if "vector_rank" in result:
                vector_contrib = 0.6 / (self.k + result["vector_rank"] + 1)
                breakdown["components"]["vector"] = {
                    "rank": result["vector_rank"],
                    "contribution": vector_contrib,
                    "original_score": result.get("vector_score", 0)
                }
            
            if "fuzzy_rank" in result:
                fuzzy_contrib = 0.4 / (self.k + result["fuzzy_rank"] + 1)
                breakdown["components"]["fuzzy"] = {
                    "rank": result["fuzzy_rank"],
                    "contribution": fuzzy_contrib,
                    "original_score": result.get("fuzzy_score", 0),
                    "type": result.get("fuzzy_type", "")
                }
            
            explanation["results_breakdown"].append(breakdown)
        
        return explanation

# Specialized search for code repositories
class CodeSearchManager(FuzzySearchManager):
    """Enhanced fuzzy search for code repositories"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_extensions = {
            'python': ['.py', '.pyx', '.pyi'],
            'cpp': ['.cpp', '.hpp', '.cc', '.h', '.cxx'],
            'javascript': ['.js', '.ts', '.jsx', '.tsx'],
            'rust': ['.rs'],
            'qml': ['.qml', '.js'],
            'markdown': ['.md', '.rst'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini']
        }
    
    def search_symbols(self, symbol_name: str, language: str = "", k: int = 10) -> List[Dict]:
        """Search for function/class/variable symbols"""
        # Language-specific symbol patterns
        patterns = {
            'python': [
                f"def {symbol_name}",
                f"class {symbol_name}",
                f"{symbol_name} ="
            ],
            'cpp': [
                f"class {symbol_name}",
                f"struct {symbol_name}",
                f"void {symbol_name}",
                f"int {symbol_name}",
                f"{symbol_name}::"
            ],
            'qml': [
                f"property.*{symbol_name}",
                f"function {symbol_name}",
                f"signal {symbol_name}"
            ]
        }
        
        search_patterns = patterns.get(language, [f"{symbol_name}"])
        
        results = []
        for pattern in search_patterns:
            pattern_results = self._fts5_search(pattern, k // len(search_patterns) + 1)
            for result in pattern_results:
                result["symbol_pattern"] = pattern
                result["symbol_language"] = language
            results.extend(pattern_results)
        
        return results[:k]
    
    def search_documentation(self, query: str, k: int = 10) -> List[Dict]:
        """Search specifically in documentation files"""
        doc_extensions = ['.md', '.rst', '.txt', '.doc']
        return self.search_by_file_type(query, [ext[1:] for ext in doc_extensions], k)
    
    def search_similar_functions(self, function_signature: str, k: int = 5) -> List[Dict]:
        """Find functions with similar signatures"""
        # Extract function name and parameters
        func_pattern = re.search(r'(\w+)\s*\((.*?)\)', function_signature)
        if not func_pattern:
            return []
        
        func_name, params = func_pattern.groups()
        
        # Search for similar function patterns
        search_queries = [
            f"def {func_name}",
            f"function {func_name}",
            params.strip() if params.strip() else func_name
        ]
        
        results = []
        for query in search_queries:
            query_results = self.query_fuzzy(query, k // len(search_queries) + 1)
            results.extend(query_results)
        
        return results[:k]