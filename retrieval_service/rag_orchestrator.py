"""
RAG (Retrieval-Augmented Generation) Orchestrator
Combines hybrid retrieval with Grok API for intelligent responses
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import re
import hashlib
import sqlite3
from pathlib import Path

from faiss_manager import HybridVectorManager
from fts_manager import FuzzySearchManager, ReciprocalRankFusion
from graph_memory import NeuralGraphMemory

logger = logging.getLogger(__name__)

class GrokAPIClient:
    """
    Production-grade Grok API client with rate limiting and key rotation
    """
    
    def __init__(self):
        # Load API keys from environment (should be set from KWallet/libsecret)
        self.api_keys = {
            "code_fast": os.getenv("GROK_4_CODE_FAST_API_KEY"),
            "general": os.getenv("GROK_4_GENERAL_API_KEY"),
            # Add additional backup keys
            "backup_1": os.getenv("GROK_BACKUP_KEY_1"),
            "backup_2": os.getenv("GROK_BACKUP_KEY_2")
        }
        
        # Remove None keys
        self.api_keys = {k: v for k, v in self.api_keys.items() if v}
        
        if not self.api_keys:
            logger.warning("No Grok API keys found in environment - running in demo mode")
            self.demo_mode = True
            self.current_key = None
            self.rate_limits = {}
        else:
            self.demo_mode = False
            # Rate limiting state
            self.current_key = "code_fast" if "code_fast" in self.api_keys else list(self.api_keys.keys())[0]
            self.rate_limits = {key: {"requests": 0, "reset_time": time.time()} for key in self.api_keys}
            self.max_requests_per_minute = 50  # Conservative limit
        
        # Response cache
        self.cache_path = Path("~/.local/share/haasp/response_cache.db").expanduser()
        self.init_cache()
        
        logger.info(f"GrokAPIClient initialized with {len(self.api_keys)} keys")
    
    def init_cache(self):
        """Initialize response cache database"""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.cache_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT,
                response_text TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_cached_response(self, query: str, model: str) -> Optional[str]:
        """Check cache for existing response"""
        try:
            query_hash = hashlib.sha256(f"{query}::{model}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_path)
            cursor = conn.execute("""
                SELECT response_text FROM response_cache 
                WHERE query_hash = ? AND created_at > datetime('now', '-24 hours')
            """, (query_hash,))
            
            result = cursor.fetchone()
            
            if result:
                # Update access count
                conn.execute("""
                    UPDATE response_cache 
                    SET access_count = access_count + 1 
                    WHERE query_hash = ?
                """, (query_hash,))
                conn.commit()
            
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Cache lookup failed: {e}")
            return None
    
    def _cache_response(self, query: str, response: str, model: str):
        """Cache response for future use"""
        try:
            query_hash = hashlib.sha256(f"{query}::{model}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_path)
            conn.execute("""
                INSERT OR REPLACE INTO response_cache 
                (query_hash, query_text, response_text, model_used)
                VALUES (?, ?, ?, ?)
            """, (query_hash, query[:1000], response, model))  # Limit query text length
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def _should_rotate_key(self, key: str) -> bool:
        """Check if we should rotate to a different API key"""
        if self.demo_mode:
            return False
        rate_info = self.rate_limits[key]
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - rate_info["reset_time"] > 60:
            rate_info["requests"] = 0
            rate_info["reset_time"] = current_time
        
        return rate_info["requests"] >= self.max_requests_per_minute
    
    def _rotate_key(self):
        """Rotate to next available API key"""
        if self.demo_mode:
            return
        keys = list(self.api_keys.keys())
        current_index = keys.index(self.current_key)
        
        # Try each key in sequence
        for i in range(1, len(keys)):
            next_index = (current_index + i) % len(keys)
            next_key = keys[next_index]
            
            if not self._should_rotate_key(next_key):
                self.current_key = next_key
                logger.info(f"Rotated to API key: {next_key}")
                return
        
        # All keys rate limited - use least recently used
        logger.warning("All API keys rate limited, using least recent")
        oldest_key = min(self.rate_limits.keys(), 
                        key=lambda k: self.rate_limits[k]["reset_time"])
        self.current_key = oldest_key
    
    async def chat_completion(self, messages: List[Dict], model: str = "grok-4", 
                            task_type: str = "general", max_retries: int = 3) -> Dict[str, Any]:
        """
        Call Grok API with automatic model selection and rate limiting
        """
        try:
            # Demo mode response
            if self.demo_mode:
                demo_response = f"[DEMO MODE] This is a simulated response for: {messages[-1]['content'] if messages else 'No message'}. Configure GROK API keys for real functionality."
                return {
                    "response": demo_response,
                    "cached": False,
                    "model": "demo",
                    "demo_mode": True
                }
            
            # Check cache first
            query_text = json.dumps(messages, sort_keys=True)
            cached = self._get_cached_response(query_text, model)
            if cached:
                logger.debug("Returning cached response")
                return {"response": cached, "cached": True, "model": model}
            
            # Select optimal model based on task type
            if task_type == "code":
                model = "grok-4-code-fast-1"
                if self.current_key != "code_fast" and "code_fast" in self.api_keys:
                    self.current_key = "code_fast"
            
            # Ensure we have a valid key
            if not self.api_keys:
                raise Exception("No API keys available")
            
            # Check rate limiting and rotate if needed
            if self._should_rotate_key(self.current_key):
                self._rotate_key()
            
            # Prepare request
            api_key = self.api_keys[self.current_key]
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": False
            }
            
            # Make request with retries
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://api.x.ai/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            # Track rate limiting
                            self.rate_limits[self.current_key]["requests"] += 1
                            
                            if response.status == 200:
                                result = await response.json()
                                response_text = result["choices"][0]["message"]["content"]
                                
                                # Cache successful response
                                self._cache_response(query_text, response_text, model)
                                
                                return {
                                    "response": response_text,
                                    "cached": False,
                                    "model": model,
                                    "api_key_used": self.current_key,
                                    "attempt": attempt + 1
                                }
                            
                            elif response.status == 429:  # Rate limited
                                logger.warning(f"Rate limited on key {self.current_key}")
                                self._rotate_key()
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            
                            elif response.status == 401:  # Unauthorized
                                logger.error(f"API key {self.current_key} is invalid")
                                # Remove invalid key and rotate
                                del self.api_keys[self.current_key]
                                if self.api_keys:
                                    self._rotate_key()
                                else:
                                    raise Exception("All API keys are invalid")
                                continue
                            
                            else:
                                error_text = await response.text()
                                logger.error(f"API error {response.status}: {error_text}")
                                await asyncio.sleep(1)
                                continue
                
                except asyncio.TimeoutError:
                    logger.warning(f"Request timeout on attempt {attempt + 1}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                except Exception as e:
                    logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
            
            raise Exception(f"All {max_retries} attempts failed")
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return {"error": str(e), "cached": False}

class RAGOrchestrator:
    """
    Master orchestrator for Retrieval-Augmented Generation
    Combines vector search, fuzzy search, graph memory, and LLM generation
    """
    
    def __init__(self):
        # Initialize retrieval components
        self.vector_manager = HybridVectorManager()
        self.fuzzy_manager = FuzzySearchManager()
        self.graph_memory = NeuralGraphMemory()
        self.rrf_fusion = ReciprocalRankFusion(k=60)
        self.grok_client = GrokAPIClient()
        
        # Configuration
        self.default_k = 10  # Number of results to retrieve
        self.context_window = 8192  # Max context tokens for LLM
        
        logger.info("RAGOrchestrator initialized with all retrieval systems")
    
    async def hybrid_retrieve(self, query: str, mode: str = "all", 
                            pilot_id: str = None, k: int = None) -> Dict[str, Any]:
        """
        Perform hybrid retrieval across all systems
        """
        if k is None:
            k = self.default_k
        
        try:
            results = {
                "query": query,
                "mode": mode,
                "pilot_id": pilot_id,
                "timestamp": datetime.now().isoformat(),
                "vector_results": [],
                "fuzzy_results": [],
                "graph_results": [],
                "fused_results": []
            }
            
            # Vector search
            if mode in ["all", "semantic", "vector"]:
                vector_results = self.vector_manager.query_semantic(query, k=k*2, pilot_id=pilot_id)
                results["vector_results"] = vector_results
                logger.debug(f"Vector search returned {len(vector_results)} results")
            
            # Fuzzy search
            if mode in ["all", "fuzzy", "lexical"]:
                fuzzy_results = self.fuzzy_manager.query_fuzzy(query, k=k*2)
                results["fuzzy_results"] = fuzzy_results
                logger.debug(f"Fuzzy search returned {len(fuzzy_results)} results")
            
            # Graph search
            if mode in ["all", "graph"]:
                # Find nodes related to query
                query_nodes = self._find_query_nodes(query)
                if query_nodes:
                    graph_results = []
                    for node_id in query_nodes[:3]:  # Limit starting nodes
                        neighbors = self.graph_memory.query_neighbors(node_id, max_depth=2)
                        for depth, neighbor_list in neighbors.items():
                            graph_results.extend(neighbor_list)
                    
                    results["graph_results"] = graph_results[:k]
                    logger.debug(f"Graph search returned {len(graph_results)} results")
            
            # Fuse results if multiple modes
            if mode == "all" and (results["vector_results"] or results["fuzzy_results"]):
                fused = self.rrf_fusion.fuse_results(
                    results["vector_results"],
                    results["fuzzy_results"],
                    weights={"vector": 0.6, "fuzzy": 0.4}
                )
                results["fused_results"] = fused[:k]
                logger.debug(f"RRF fusion produced {len(fused)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return {"error": str(e), "query": query}
    
    async def generate_response(self, query: str, context_chunks: List[Dict], 
                              task_type: str = "general", pilot_id: str = None) -> Dict[str, Any]:
        """
        Generate response using RAG pattern
        """
        try:
            # Prepare context from retrieved chunks
            context_text = self._prepare_context(context_chunks)
            
            # Build conversation history if pilot specified
            conversation_context = ""
            if pilot_id:
                recent_messages = self.vector_manager.get_last_n_messages(pilot_id, n=5)
                if recent_messages:
                    conversation_context = "\n".join([
                        f"{msg['speaker']}: {msg['utterance']}" 
                        for msg in recent_messages
                    ])
            
            # Construct prompt with context
            system_prompt = self._build_system_prompt(task_type, pilot_id)
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if available
            if conversation_context:
                messages.append({
                    "role": "assistant", 
                    "content": f"Previous conversation context:\n{conversation_context}"
                })
            
            # Add retrieved context
            if context_text:
                messages.append({
                    "role": "assistant",
                    "content": f"Retrieved context:\n{context_text}"
                })
            
            # Add user query
            messages.append({"role": "user", "content": query})
            
            # Generate response
            response = await self.grok_client.chat_completion(
                messages=messages,
                task_type=task_type
            )
            
            # Store conversation in vector memory
            if pilot_id and "response" in response:
                self.vector_manager.add_conversation(pilot_id, query, "user")
                self.vector_manager.add_conversation(pilot_id, response["response"], "assistant")
            
            # Enhance response with metadata
            enhanced_response = {
                "query": query,
                "response": response.get("response", ""),
                "context_chunks": len(context_chunks),
                "model_used": response.get("model", "unknown"),
                "api_key_used": response.get("api_key_used", "unknown"),
                "cached": response.get("cached", False),
                "task_type": task_type,
                "pilot_id": pilot_id,
                "generated_at": datetime.now().isoformat(),
                "sources": [chunk.get("file_path", "unknown") for chunk in context_chunks]
            }
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {"error": str(e), "query": query}
    
    def _prepare_context(self, chunks: List[Dict], max_length: int = 6000) -> str:
        """Prepare context text from retrieved chunks"""
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            chunk_text = chunk.get("chunk_text", chunk.get("content", ""))
            source = chunk.get("file_path", chunk.get("doc_id", "unknown"))
            
            # Format chunk with source
            formatted = f"[Source: {source}]\n{chunk_text}\n"
            
            if current_length + len(formatted) > max_length:
                break
            
            context_parts.append(formatted)
            current_length += len(formatted)
        
        return "\n---\n".join(context_parts)
    
    def _build_system_prompt(self, task_type: str, pilot_id: str = None) -> str:
        """Build system prompt based on task type and pilot"""
        base_prompt = "You are HAASP, an advanced AI development assistant."
        
        if pilot_id:
            pilot_prompts = {
                "pilot_0_sentinel": """
                You are Sentinel, the pre-zero analyzer. Your role is to:
                - Prevent repetition and regressions
                - Analyze mistakes and inconsistencies
                - Record events with precise timestamps
                - Maintain vigilance against errors
                """,
                "pilot_1_doc_architect": """
                You are Doc Architect, the documentation specialist. Your role is to:
                - Generate comprehensive technical documentation
                - Create dependency graphs and schemas
                - Build clear architectural diagrams
                - Ensure documentation completeness
                """,
                "pilot_2_remediator": """
                You are Remediator, the issue fixer. Your role is to:
                - Analyze diagnostics and error reports
                - Propose safe automated fixes
                - Generate minimal, targeted patches
                - Ensure code quality improvements
                """,
                "pilot_3_codewright": """
                You are Codewright, the code synthesizer. Your role is to:
                - Generate high-quality code with AST awareness
                - Create comprehensive test suites
                - Perform intelligent refactoring
                - Optimize performance and maintainability
                """
            }
            
            base_prompt = pilot_prompts.get(pilot_id, base_prompt)
        
        task_modifiers = {
            "code": "\nFocus on code analysis, generation, and technical accuracy.",
            "documentation": "\nProvide comprehensive, well-structured documentation.",
            "debugging": "\nAnalyze errors systematically and provide clear solutions.",
            "architecture": "\nThink about system design and component interactions."
        }
        
        return base_prompt + task_modifiers.get(task_type, "")
    
    def _find_query_nodes(self, query: str) -> List[str]:
        """Find graph nodes relevant to the query"""
        try:
            # Simple keyword matching to find relevant nodes
            query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
            relevant_nodes = []
            
            for node_id, node_data in self.graph_memory.graph.nodes(data=True):
                content = node_data.get("content", "").lower()
                content_words = set(re.findall(r'\b\w{3,}\b', content))
                
                # Calculate word overlap
                overlap = len(query_words.intersection(content_words))
                if overlap >= 2:  # Minimum relevance threshold
                    relevant_nodes.append((node_id, overlap))
            
            # Sort by relevance and return top nodes
            relevant_nodes.sort(key=lambda x: x[1], reverse=True)
            return [node_id for node_id, _ in relevant_nodes[:5]]
            
        except Exception as e:
            logger.error(f"Query node search failed: {e}")
            return []
    
    async def query_rag(self, query: str, k: int = 10, task_type: str = "general",
                       pilot_id: str = None, include_graph: bool = True) -> Dict[str, Any]:
        """
        Complete RAG query: retrieve + generate response
        """
        try:
            logger.info(f"RAG query: {query[:100]}...")
            
            # Step 1: Hybrid retrieval
            retrieval_results = await self.hybrid_retrieve(
                query, mode="all", pilot_id=pilot_id, k=k
            )
            
            # Step 2: Select best chunks for context
            if retrieval_results.get("fused_results"):
                context_chunks = retrieval_results["fused_results"]
            else:
                # Fallback to individual results
                context_chunks = (
                    retrieval_results.get("vector_results", []) +
                    retrieval_results.get("fuzzy_results", [])
                )[:k]
            
            # Step 3: Generate response
            if context_chunks:
                generation_result = await self.generate_response(
                    query, context_chunks, task_type, pilot_id
                )
            else:
                # No context found, direct generation
                generation_result = await self.grok_client.chat_completion(
                    messages=[{"role": "user", "content": query}],
                    task_type=task_type
                )
                generation_result["context_chunks"] = 0
                generation_result["sources"] = []
            
            # Step 4: Combine results
            rag_result = {
                "query": query,
                "response": generation_result.get("response", ""),
                "retrieval": retrieval_results,
                "generation": generation_result,
                "metadata": {
                    "total_chunks_retrieved": len(context_chunks),
                    "sources_used": len(set(chunk.get("file_path", "") for chunk in context_chunks)),
                    "task_type": task_type,
                    "pilot_id": pilot_id,
                    "include_graph": include_graph,
                    "processing_time": None  # TODO: Add timing
                }
            }
            
            return rag_result
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request."
            }
    
    async def summarize_conversation(self, pilot_id: str, window_size: int = 20) -> Dict[str, Any]:
        """Summarize recent conversation history for a pilot"""
        try:
            # Get recent messages
            recent_messages = self.vector_manager.get_last_n_messages(pilot_id, window_size)
            
            if not recent_messages:
                return {"summary": "No conversation history found.", "message_count": 0}
            
            # Prepare conversation for summarization
            conversation_text = "\n".join([
                f"{msg['timestamp']} - {msg['speaker']}: {msg['utterance']}"
                for msg in recent_messages
            ])
            
            # Generate summary
            summary_prompt = f"""
            Please provide a concise summary of this conversation history:
            
            {conversation_text}
            
            Focus on:
            - Key topics discussed
            - Decisions made
            - Tasks or actions planned
            - Important context for future interactions
            """
            
            summary_response = await self.grok_client.chat_completion(
                messages=[{"role": "user", "content": summary_prompt}],
                task_type="general"
            )
            
            return {
                "summary": summary_response.get("response", ""),
                "message_count": len(recent_messages),
                "time_span": {
                    "start": recent_messages[0]["timestamp"] if recent_messages else None,
                    "end": recent_messages[-1]["timestamp"] if recent_messages else None
                },
                "pilot_id": pilot_id
            }
            
        except Exception as e:
            logger.error(f"Conversation summarization failed: {e}")
            return {"error": str(e), "pilot_id": pilot_id}
    
    async def explain_reasoning(self, query: str, results: List[Dict]) -> Dict[str, Any]:
        """Generate explanation of how results were found and ranked"""
        try:
            # Build explanation context
            explanation_context = []
            
            for i, result in enumerate(results[:5]):
                source_info = f"Result {i+1}: {result.get('file_path', 'unknown source')}"
                score_info = f"Score: {result.get('score', 0):.3f}"
                type_info = f"Type: {result.get('type', 'unknown')}"
                
                explanation_context.append(f"{source_info} | {score_info} | {type_info}")
            
            explanation_prompt = f"""
            Explain how these search results were found and ranked for the query: "{query}"
            
            Search Results:
            {chr(10).join(explanation_context)}
            
            Please explain:
            1. What made these results relevant to the query
            2. How the ranking/scoring likely worked
            3. What types of information were found
            4. How this helps answer the original question
            """
            
            explanation_response = await self.grok_client.chat_completion(
                messages=[{"role": "user", "content": explanation_prompt}],
                task_type="general"
            )
            
            return {
                "explanation": explanation_response.get("response", ""),
                "query": query,
                "results_analyzed": len(results),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reasoning explanation failed: {e}")
            return {"error": str(e)}
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all retrieval systems"""
        try:
            return {
                "vector_storage": self.vector_manager.get_statistics(),
                "fuzzy_search": self.fuzzy_manager.get_statistics(), 
                "graph_memory": self.graph_memory.get_statistics(),
                "api_usage": {
                    "current_key": self.grok_client.current_key,
                    "available_keys": len(self.grok_client.api_keys),
                    "rate_limits": self.grok_client.rate_limits
                },
                "system_health": {
                    "components_active": 4,  # vector, fuzzy, graph, api
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {e}")
            return {"error": str(e)}

# Specialized RAG for different use cases
class CodeRAG(RAGOrchestrator):
    """RAG specialized for code-related queries"""
    
    def __init__(self):
        super().__init__()
        self.code_languages = ["python", "cpp", "javascript", "rust", "qml"]
    
    async def code_completion(self, partial_code: str, language: str, 
                            context_files: List[str] = None) -> Dict[str, Any]:
        """Generate code completion with relevant context"""
        
        # Search for similar code patterns
        search_query = f"{language} {partial_code}"
        retrieval = await self.hybrid_retrieve(search_query, mode="all", k=15)
        
        # Filter for code-specific results
        code_chunks = [
            chunk for chunk in retrieval.get("fused_results", [])
            if any(ext in chunk.get("file_path", "") for ext in [".py", ".cpp", ".js", ".rs", ".qml"])
        ]
        
        # Generate completion
        completion_prompt = f"""
        Complete this {language} code:
        
        ```{language}
        {partial_code}
        ```
        
        Provide a natural completion that follows good coding practices.
        """
        
        response = await self.generate_response(
            completion_prompt, code_chunks, "code", "pilot_3_codewright"
        )
        
        return response
    
    async def explain_code(self, code_snippet: str, language: str) -> Dict[str, Any]:
        """Explain code functionality with context"""
        
        # Search for related code and documentation
        search_query = f"explain {language} documentation"
        retrieval = await self.hybrid_retrieve(search_query, mode="all", k=10)
        
        explanation_prompt = f"""
        Explain this {language} code in detail:
        
        ```{language}
        {code_snippet}
        ```
        
        Include:
        - What the code does
        - Key concepts and patterns used
        - Potential improvements or issues
        - How it relates to the broader codebase
        """
        
        response = await self.generate_response(
            explanation_prompt, retrieval.get("fused_results", []), 
            "code", "pilot_1_doc_architect"
        )
        
        return response
    
    async def find_bugs(self, error_message: str, stack_trace: str = "") -> Dict[str, Any]:
        """Find and suggest fixes for bugs"""
        
        # Search for similar errors and solutions
        search_query = f"error fix {error_message}"
        retrieval = await self.hybrid_retrieve(search_query, mode="all", k=12)
        
        bug_fix_prompt = f"""
        Analyze this error and suggest fixes:
        
        Error: {error_message}
        
        Stack Trace:
        {stack_trace}
        
        Provide:
        1. Root cause analysis
        2. Specific fix recommendations
        3. Prevention strategies
        4. Related documentation
        """
        
        response = await self.generate_response(
            bug_fix_prompt, retrieval.get("fused_results", []),
            "debugging", "pilot_2_remediator"
        )
        
        return response

# AI Organisms - Self-replicating enrichment agents
class AIOrganismManager:
    """
    Manage self-replicating AI organisms for continuous data enrichment
    """
    
    def __init__(self, rag_orchestrator: RAGOrchestrator):
        self.rag = rag_orchestrator
        self.organisms = []
        self.max_organisms = 50
        self.replication_rate = 0.1  # 10% chance per cycle
        
    async def create_organism(self, focus_area: str, pilot_id: str) -> Dict[str, Any]:
        """Create a new AI organism focused on specific area"""
        organism_id = f"org_{pilot_id}_{time.time()}"
        
        organism = {
            "id": organism_id,
            "focus_area": focus_area,
            "pilot_id": pilot_id,
            "created_at": datetime.now().isoformat(),
            "enrichment_data": [],
            "qa_history": [],
            "pass_count": 0,
            "receive_count": 0,
            "generation": 0
        }
        
        self.organisms.append(organism)
        logger.info(f"Created organism {organism_id} for {focus_area}")
        
        return organism
    
    async def organism_lifecycle(self, organism: Dict[str, Any]):
        """Execute organism lifecycle: 5x Q/A, 2x pass, deletion criteria"""
        try:
            # Phase 1: 5x internal Q/A enrichment
            for i in range(5):
                question = await self._generate_question(organism)
                answer = await self._generate_answer(question, organism)
                
                organism["qa_history"].append({
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Extract enrichment data
                enrichment = self._extract_enrichment(answer)
                organism["enrichment_data"].extend(enrichment)
            
            # Phase 2: 2x data passing to other organisms
            for i in range(2):
                await self._pass_enrichment_data(organism)
                organism["pass_count"] += 1
            
            # Phase 3: Check deletion criteria
            if self._meets_deletion_criteria(organism):
                await self._delete_organism(organism)
                logger.info(f"Organism {organism['id']} completed lifecycle - deleting")
            
        except Exception as e:
            logger.error(f"Organism lifecycle failed: {e}")
    
    async def _generate_question(self, organism: Dict[str, Any]) -> str:
        """Generate internal question for organism"""
        focus = organism["focus_area"]
        question_prompts = [
            f"What optimization opportunities exist in {focus}?",
            f"How can we improve the accuracy of {focus} analysis?",
            f"What patterns should we look for in {focus}?",
            f"What errors commonly occur with {focus}?",
            f"How does {focus} relate to other system components?"
        ]
        
        return question_prompts[len(organism["qa_history"]) % len(question_prompts)]
    
    async def _generate_answer(self, question: str, organism: Dict[str, Any]) -> str:
        """Generate answer using RAG system"""
        try:
            rag_result = await self.rag.query_rag(
                question, k=5, task_type="general", pilot_id=organism["pilot_id"]
            )
            return rag_result.get("response", "No answer generated")
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "Error generating answer"
    
    def _extract_enrichment(self, answer: str) -> List[str]:
        """Extract enrichment data from answer"""
        # Simple extraction - look for key insights
        insights = []
        sentences = answer.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in 
                  ["improve", "optimize", "pattern", "solution", "approach"]):
                insights.append(sentence.strip())
        
        return insights
    
    async def _pass_enrichment_data(self, organism: Dict[str, Any]):
        """Pass enrichment data to another organism"""
        if len(self.organisms) <= 1:
            return
        
        # Find target organism (different from self)
        target = None
        for other in self.organisms:
            if other["id"] != organism["id"]:
                target = other
                break
        
        if target:
            target["enrichment_data"].extend(organism["enrichment_data"])
            target["receive_count"] += 1
            logger.debug(f"Organism {organism['id']} passed data to {target['id']}")
    
    def _meets_deletion_criteria(self, organism: Dict[str, Any]) -> bool:
        """Check if organism should be deleted"""
        return (organism["receive_count"] >= 2 and 
                organism["pass_count"] >= 2 and
                len(organism["enrichment_data"]) > 0)
    
    async def _delete_organism(self, organism: Dict[str, Any]):
        """Delete organism and preserve enrichment data"""
        # Store enrichment data in permanent memory
        if organism["enrichment_data"]:
            enrichment_summary = "\n".join(organism["enrichment_data"])
            
            # Add to graph memory
            enrichment_id = f"enrichment::{organism['id']}"
            self.rag.graph_memory.add_node(
                enrichment_id, "enrichment", enrichment_summary,
                metadata=organism
            )
        
        # Remove from active organisms
        self.organisms = [o for o in self.organisms if o["id"] != organism["id"]]