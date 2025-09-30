"""
FAISS-based Vector Search Manager
Enhanced from TelePrompt patterns for HAASP hybrid retrieval system
"""

import numpy as np
import faiss
import sqlite3
import json
import asyncio
from typing import List, Dict, Tuple, Optional, Any
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridVectorManager:
    """
    Advanced vector storage and retrieval system
    Features:
    - FAISS HNSW for fast queries + IVF-PQ for large scale
    - SQLite doc mapping (robust vs .npy files)
    - Conversation-specific indexes per pilot
    - Incremental updates with alignment validation
    - GPU acceleration when available
    """
    
    def __init__(self, models_path: str = "~/.local/share/haasp/models"):
        self.models_path = Path(models_path).expanduser()
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Embedding models (local-first) - force CPU to avoid CUDA issues
        self.primary_embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
        self.secondary_embedder = SentenceTransformer('intfloat/e5-base-v2', device='cpu')
        
        # FAISS indexes
        self.main_index = None          # HNSW for fast queries
        self.large_index = None         # IVF-PQ for large corpora
        self.conversation_indexes = {}  # Per-pilot conversation memory
        
        # Document mapping
        self.doc_db_path = self.models_path / "doc_mapping.db"
        self.init_doc_database()
        
        # Configuration
        self.vector_dim = 384  # MiniLM dimension
        self.chunk_size = 512
        self.chunk_overlap = 128
        
        logger.info(f"HybridVectorManager initialized with models at {self.models_path}")
    
    def init_doc_database(self):
        """Initialize SQLite database for document mapping"""
        conn = sqlite3.connect(self.doc_db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT UNIQUE,
                file_path TEXT,
                content_hash TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT UNIQUE,
                doc_id TEXT,
                vector_id INTEGER,
                chunk_text TEXT,
                start_pos INTEGER,
                end_pos INTEGER,
                content_hash TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pilot_id TEXT,
                utterance_id TEXT UNIQUE,
                vector_id INTEGER,
                utterance_text TEXT,
                speaker TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_hash TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def build_main_index(self, index_type: str = "HNSW") -> bool:
        """Build main FAISS index for semantic search"""
        try:
            if index_type == "HNSW":
                # HNSW for fast approximate search
                self.main_index = faiss.IndexHNSWFlat(self.vector_dim)
                self.main_index.hnsw.M = 32
                self.main_index.hnsw.efConstruction = 200
                self.main_index.hnsw.efSearch = 64
                
            elif index_type == "IVF_PQ":
                # IVF-PQ for large-scale search with compression
                quantizer = faiss.IndexFlatL2(self.vector_dim)
                self.main_index = faiss.IndexIVFPQ(quantizer, self.vector_dim, 4096, 16, 8)
                
            logger.info(f"Built {index_type} index with dimension {self.vector_dim}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            return False
    
    def chunk_document(self, content: str, metadata: Dict = None) -> List[Dict]:
        """
        Intelligent document chunking
        - Language-aware splitting
        - Overlapping windows for context preservation
        """
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunk = {
                "text": chunk_text,
                "start_pos": i,
                "end_pos": min(i + self.chunk_size, len(words)),
                "metadata": metadata or {},
                "hash": hashlib.sha256(chunk_text.encode()).hexdigest()[:16]
            }
            chunks.append(chunk)
            
        return chunks
    
    def add_document(self, doc_id: str, content: str, file_path: str = "", metadata: Dict = None) -> bool:
        """Add document to vector index and mapping database"""
        try:
            # Chunk the document
            chunks = self.chunk_document(content, metadata)
            
            # Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.primary_embedder.encode(chunk_texts, normalize_embeddings=True)
            
            # Add to FAISS index
            if self.main_index is None:
                self.build_main_index()
            
            start_id = self.main_index.ntotal
            self.main_index.add(embeddings.astype(np.float32))
            
            # Store in database
            conn = sqlite3.connect(self.doc_db_path)
            
            # Insert document record
            doc_hash = hashlib.sha256(content.encode()).hexdigest()
            conn.execute("""
                INSERT OR REPLACE INTO documents (doc_id, file_path, content_hash, metadata)
                VALUES (?, ?, ?, ?)
            """, (doc_id, file_path, doc_hash, json.dumps(metadata or {})))
            
            # Insert chunk records
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}::{i}"
                vector_id = start_id + i
                
                conn.execute("""
                    INSERT OR REPLACE INTO chunks 
                    (chunk_id, doc_id, vector_id, chunk_text, start_pos, end_pos, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chunk_id, doc_id, vector_id, chunk["text"], 
                     chunk["start_pos"], chunk["end_pos"], chunk["hash"]))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {e}")
            return False
    
    def query_semantic(self, query: str, k: int = 10, pilot_id: str = None) -> List[Dict]:
        """
        Semantic vector search with conversation context
        """
        try:
            if self.main_index is None or self.main_index.ntotal == 0:
                return []
            
            # Encode query
            query_embedding = self.primary_embedder.encode([query], normalize_embeddings=True)
            
            # Search main index
            scores, indices = self.main_index.search(query_embedding.astype(np.float32), k)
            
            # Get document details from database
            conn = sqlite3.connect(self.doc_db_path)
            results = []
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0:  # Valid result
                    cursor = conn.execute("""
                        SELECT c.chunk_text, c.doc_id, d.file_path, d.metadata
                        FROM chunks c 
                        JOIN documents d ON c.doc_id = d.doc_id
                        WHERE c.vector_id = ?
                    """, (int(idx),))
                    
                    row = cursor.fetchone()
                    if row:
                        results.append({
                            "chunk_text": row[0],
                            "doc_id": row[1],
                            "file_path": row[2],
                            "metadata": json.loads(row[3]),
                            "score": float(score),
                            "rank": i
                        })
            
            conn.close()
            
            # Add conversation context if pilot specified
            if pilot_id and pilot_id in self.conversation_indexes:
                conversation_results = self.query_conversation_memory(query, pilot_id, k=5)
                results.extend(conversation_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def add_conversation(self, pilot_id: str, utterance: str, speaker: str = "user") -> bool:
        """Add utterance to pilot-specific conversation memory"""
        try:
            # Create pilot conversation index if needed
            if pilot_id not in self.conversation_indexes:
                self.conversation_indexes[pilot_id] = faiss.IndexHNSWFlat(self.vector_dim)
                self.conversation_indexes[pilot_id].hnsw.M = 16
                self.conversation_indexes[pilot_id].hnsw.efConstruction = 100
            
            # Embed utterance
            embedding = self.primary_embedder.encode([utterance], normalize_embeddings=True)
            
            # Add to pilot's index
            start_id = self.conversation_indexes[pilot_id].ntotal
            self.conversation_indexes[pilot_id].add(embedding.astype(np.float32))
            
            # Store in database
            conn = sqlite3.connect(self.doc_db_path)
            utterance_id = f"{pilot_id}::{datetime.now().isoformat()}"
            context_hash = hashlib.sha256(utterance.encode()).hexdigest()[:16]
            
            conn.execute("""
                INSERT INTO conversations 
                (pilot_id, utterance_id, vector_id, utterance_text, speaker, context_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pilot_id, utterance_id, start_id, utterance, speaker, context_hash))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Added conversation for pilot {pilot_id}: {utterance[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")
            return False
    
    def query_conversation_memory(self, query: str, pilot_id: str, k: int = 5) -> List[Dict]:
        """Query pilot-specific conversation history"""
        try:
            if pilot_id not in self.conversation_indexes:
                return []
            
            index = self.conversation_indexes[pilot_id]
            if index.ntotal == 0:
                return []
            
            # Embed and search
            query_embedding = self.primary_embedder.encode([query], normalize_embeddings=True)
            scores, indices = index.search(query_embedding.astype(np.float32), k)
            
            # Get conversation details
            conn = sqlite3.connect(self.doc_db_path)
            results = []
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:
                    cursor = conn.execute("""
                        SELECT utterance_text, speaker, timestamp
                        FROM conversations 
                        WHERE pilot_id = ? AND vector_id = ?
                    """, (pilot_id, int(idx)))
                    
                    row = cursor.fetchone()
                    if row:
                        results.append({
                            "utterance": row[0],
                            "speaker": row[1], 
                            "timestamp": row[2],
                            "score": float(score),
                            "type": "conversation"
                        })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Conversation query failed: {e}")
            return []
    
    def get_last_n_messages(self, pilot_id: str, n: int = 10) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            conn = sqlite3.connect(self.doc_db_path)
            cursor = conn.execute("""
                SELECT utterance_text, speaker, timestamp
                FROM conversations 
                WHERE pilot_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (pilot_id, n))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "utterance": row[0],
                    "speaker": row[1],
                    "timestamp": row[2]
                })
            
            conn.close()
            return list(reversed(results))  # Chronological order
            
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []
    
    def save_index(self, index_path: str = None):
        """Persist FAISS index to disk"""
        try:
            if index_path is None:
                index_path = str(self.models_path / "main_index.faiss")
                
            if self.main_index is not None:
                faiss.write_index(self.main_index, index_path)
                logger.info(f"Saved main index to {index_path}")
            
            # Save conversation indexes
            for pilot_id, index in self.conversation_indexes.items():
                pilot_path = str(self.models_path / f"conversation_{pilot_id}.faiss")
                faiss.write_index(index, pilot_path)
                
        except Exception as e:
            logger.error(f"Failed to save indexes: {e}")
    
    def load_index(self, index_path: str = None) -> bool:
        """Load FAISS index from disk"""
        try:
            if index_path is None:
                index_path = str(self.models_path / "main_index.faiss")
            
            if Path(index_path).exists():
                self.main_index = faiss.read_index(index_path)
                logger.info(f"Loaded main index from {index_path}")
                return True
            else:
                logger.warning(f"Index file not found: {index_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def verify_alignment(self) -> Dict[str, Any]:
        """Verify FAISS index alignment with document database"""
        try:
            conn = sqlite3.connect(self.doc_db_path)
            
            # Count chunks in database
            cursor = conn.execute("SELECT COUNT(*) FROM chunks")
            db_count = cursor.fetchone()[0]
            
            # Count vectors in index
            index_count = self.main_index.ntotal if self.main_index else 0
            
            # Check for misalignment
            aligned = (db_count == index_count)
            
            verification = {
                "aligned": aligned,
                "db_chunks": db_count,
                "index_vectors": index_count,
                "drift": abs(db_count - index_count),
                "timestamp": datetime.now().isoformat()
            }
            
            conn.close()
            
            if not aligned:
                logger.warning(f"Index misalignment detected: {verification}")
            else:
                logger.info("Index alignment verified")
                
            return verification
            
        except Exception as e:
            logger.error(f"Alignment verification failed: {e}")
            return {"aligned": False, "error": str(e)}
    
    async def reindex_async(self, force: bool = False):
        """Asynchronous reindexing for performance"""
        try:
            logger.info("Starting asynchronous reindexing...")
            
            # Check alignment first
            alignment = self.verify_alignment()
            if alignment["aligned"] and not force:
                logger.info("Index already aligned, skipping reindex")
                return
            
            # Rebuild index from database
            conn = sqlite3.connect(self.doc_db_path)
            cursor = conn.execute("""
                SELECT c.chunk_text, c.chunk_id, c.doc_id 
                FROM chunks c 
                ORDER BY c.id
            """)
            
            # Collect all chunks
            chunks = []
            chunk_metadata = []
            
            for row in cursor.fetchall():
                chunks.append(row[0])
                chunk_metadata.append({
                    "chunk_id": row[1],
                    "doc_id": row[2]
                })
            
            conn.close()
            
            if not chunks:
                logger.warning("No chunks found for reindexing")
                return
            
            # Re-embed all chunks
            logger.info(f"Re-embedding {len(chunks)} chunks...")
            embeddings = self.primary_embedder.encode(chunks, normalize_embeddings=True)
            
            # Rebuild index
            self.build_main_index()
            self.main_index.add(embeddings.astype(np.float32))
            
            # Save updated index
            self.save_index()
            
            logger.info("Asynchronous reindexing completed successfully")
            
        except Exception as e:
            logger.error(f"Reindexing failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        stats = {
            "main_index": {
                "total_vectors": self.main_index.ntotal if self.main_index else 0,
                "dimension": self.vector_dim,
                "index_type": type(self.main_index).__name__ if self.main_index else None
            },
            "conversation_indexes": {
                pilot_id: index.ntotal 
                for pilot_id, index in self.conversation_indexes.items()
            },
            "database": self._get_db_stats(),
            "alignment": self.verify_alignment()
        }
        
        return stats
    
    def _get_db_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.doc_db_path)
            
            stats = {}
            for table in ["documents", "chunks", "conversations"]:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get DB stats: {e}")
            return {}

# Performance optimization for large-scale deployment
class GPUVectorManager(HybridVectorManager):
    """GPU-accelerated version using FAISS-GPU"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpu_available = self._check_gpu()
        
    def _check_gpu(self) -> bool:
        """Check if FAISS-GPU is available"""
        try:
            import faiss.contrib.torch_utils
            return faiss.get_num_gpus() > 0
        except:
            return False
    
    def build_main_index(self, index_type: str = "HNSW") -> bool:
        """GPU-accelerated index building"""
        if not self.gpu_available:
            return super().build_main_index(index_type)
            
        try:
            # Build on GPU for faster training
            if index_type == "IVF_PQ":
                quantizer = faiss.IndexFlatL2(self.vector_dim)
                index = faiss.IndexIVFPQ(quantizer, self.vector_dim, 4096, 16, 8)
                
                # Move to GPU
                res = faiss.StandardGpuResources()
                self.main_index = faiss.index_cpu_to_gpu(res, 0, index)
                
                logger.info("Built GPU-accelerated IVF-PQ index")
                return True
            else:
                # HNSW doesn't support GPU, fallback to CPU
                return super().build_main_index(index_type)
                
        except Exception as e:
            logger.error(f"GPU index build failed, falling back to CPU: {e}")
            return super().build_main_index(index_type)