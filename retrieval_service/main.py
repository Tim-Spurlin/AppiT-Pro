"""
HAASP Hybrid Retrieval Service
FastAPI server exposing all retrieval capabilities
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Add current directory to path for imports
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import our retrieval components
from faiss_manager import HybridVectorManager, GPUVectorManager
from fts_manager import FuzzySearchManager, ReciprocalRankFusion, CodeSearchManager
from graph_memory import NeuralGraphMemory
from rag_orchestrator import RAGOrchestrator, CodeRAG, AIOrganismManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class DocumentRequest(BaseModel):
    doc_id: str
    content: str
    file_path: str = ""
    language: str = ""
    metadata: Dict[str, Any] = {}

class SearchRequest(BaseModel):
    query: str
    k: int = 10
    mode: str = "all"  # all, semantic, fuzzy, graph
    pilot_id: Optional[str] = None
    include_conversation: bool = True

class ConversationRequest(BaseModel):
    pilot_id: str
    utterance: str
    speaker: str = "user"

class RAGRequest(BaseModel):
    query: str
    k: int = 10
    task_type: str = "general"  # general, code, documentation, debugging
    pilot_id: Optional[str] = None
    include_sources: bool = True

class CodeRequest(BaseModel):
    code: str
    language: str
    operation: str  # completion, explanation, debugging
    context_files: List[str] = []

# Initialize FastAPI app
app = FastAPI(
    title="HAASP Hybrid Retrieval Service",
    description="Advanced multi-modal retrieval with vector search, fuzzy matching, and RAG",
    version="1.0.0"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "https://localhost:*", "http://127.0.0.1:*", "https://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global retrieval system instances
vector_manager: Optional[HybridVectorManager] = None
fuzzy_manager: Optional[FuzzySearchManager] = None
graph_memory: Optional[NeuralGraphMemory] = None
rag_orchestrator: Optional[RAGOrchestrator] = None
code_rag: Optional[CodeRAG] = None
organism_manager: Optional[AIOrganismManager] = None

@app.on_event("startup")
async def startup_event():
    """Initialize all retrieval systems"""
    global vector_manager, fuzzy_manager, graph_memory, rag_orchestrator, code_rag, organism_manager
    
    try:
        logger.info("🚀 Starting HAASP Retrieval Service...")
        
        # Check for GPU availability
        try:
            import faiss
            if faiss.get_num_gpus() > 0:
                logger.info("GPU detected, using GPU-accelerated vector manager")
                vector_manager = GPUVectorManager()
            else:
                logger.info("No GPU detected, using CPU vector manager")
                vector_manager = HybridVectorManager()
        except Exception as e:
            logger.warning(f"GPU check failed, using CPU vector manager: {e}")
            vector_manager = HybridVectorManager()
        
        # Initialize other components
        fuzzy_manager = CodeSearchManager()  # Enhanced fuzzy search for code
        graph_memory = NeuralGraphMemory()
        
        # Initialize RAG orchestrator
        rag_orchestrator = RAGOrchestrator()
        rag_orchestrator.vector_manager = vector_manager
        rag_orchestrator.fuzzy_manager = fuzzy_manager
        rag_orchestrator.graph_memory = graph_memory
        
        # Code-specific RAG
        code_rag = CodeRAG()
        code_rag.vector_manager = vector_manager
        code_rag.fuzzy_manager = fuzzy_manager
        code_rag.graph_memory = graph_memory
        
        # AI Organisms for continuous enrichment
        organism_manager = AIOrganismManager(rag_orchestrator)
        
        # Load existing indexes
        logger.info("Loading existing indexes...")
        vector_manager.load_index()
        
        logger.info("✅ All retrieval systems initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("💾 Saving indexes before shutdown...")
        
        if vector_manager:
            vector_manager.save_index()
        
        if graph_memory:
            graph_memory.save_graph()
        
        logger.info("👋 HAASP Retrieval Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Service health check"""
    return {
        "service": "HAASP Hybrid Retrieval Service",
        "status": "running",
        "version": "1.0.0",
        "components": {
            "vector_manager": vector_manager is not None,
            "fuzzy_manager": fuzzy_manager is not None,
            "graph_memory": graph_memory is not None,
            "rag_orchestrator": rag_orchestrator is not None
        }
    }

@app.post("/documents")
async def add_document(doc_request: DocumentRequest, background_tasks: BackgroundTasks):
    """Add document to all retrieval systems"""
    try:
        if not vector_manager or not fuzzy_manager or not graph_memory:
            raise HTTPException(status_code=503, detail="Retrieval systems not initialized")
        
        # Add to vector index
        vector_success = vector_manager.add_document(
            doc_request.doc_id,
            doc_request.content,
            doc_request.file_path,
            doc_request.metadata
        )
        
        # Add to fuzzy search
        fuzzy_success = fuzzy_manager.add_document(
            doc_request.doc_id,
            doc_request.content,
            doc_request.file_path,
            doc_request.language,
            doc_request.metadata
        )
        
        # Add to graph memory (background task for performance)
        if doc_request.language in ["python", "cpp", "qml", "javascript"]:
            background_tasks.add_task(
                add_to_graph_memory,
                doc_request.doc_id,
                doc_request.content,
                doc_request.file_path,
                doc_request.language
            )
        
        return {
            "doc_id": doc_request.doc_id,
            "vector_indexed": vector_success,
            "fuzzy_indexed": fuzzy_success,
            "graph_processing": True,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Document addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def add_to_graph_memory(doc_id: str, content: str, file_path: str, language: str):
    """Background task to add document to graph memory"""
    try:
        graph_memory.add_code_file(file_path, content, language)
        logger.debug(f"Added {doc_id} to graph memory")
    except Exception as e:
        logger.error(f"Graph memory addition failed: {e}")

@app.post("/search")
async def search(search_request: SearchRequest):
    """Hybrid search across all systems"""
    try:
        if not rag_orchestrator:
            raise HTTPException(status_code=503, detail="RAG orchestrator not initialized")
        
        results = await rag_orchestrator.hybrid_retrieve(
            search_request.query,
            mode=search_request.mode,
            pilot_id=search_request.pilot_id,
            k=search_request.k
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag")
async def rag_query(rag_request: RAGRequest):
    """RAG query with generation"""
    try:
        if not rag_orchestrator:
            raise HTTPException(status_code=503, detail="RAG orchestrator not initialized")
        
        result = await rag_orchestrator.query_rag(
            rag_request.query,
            k=rag_request.k,
            task_type=rag_request.task_type,
            pilot_id=rag_request.pilot_id
        )
        
        if not rag_request.include_sources:
            # Remove source details for cleaner response
            result.pop("retrieval", None)
        
        return result
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversations")
async def add_conversation(conv_request: ConversationRequest):
    """Add conversation utterance"""
    try:
        if not vector_manager:
            raise HTTPException(status_code=503, detail="Vector manager not initialized")
        
        success = vector_manager.add_conversation(
            conv_request.pilot_id,
            conv_request.utterance,
            conv_request.speaker
        )
        
        # Also add to graph memory
        if graph_memory:
            graph_memory.add_conversation_context(
                conv_request.utterance,
                conv_request.pilot_id
            )
        
        return {
            "pilot_id": conv_request.pilot_id,
            "added": success,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
    except Exception as e:
        logger.error(f"Conversation addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{pilot_id}")
async def get_conversation_history(pilot_id: str, limit: int = 20):
    """Get conversation history for a pilot"""
    try:
        if not vector_manager:
            raise HTTPException(status_code=503, detail="Vector manager not initialized")
        
        messages = vector_manager.get_last_n_messages(pilot_id, limit)
        
        return {
            "pilot_id": pilot_id,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Conversation retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/code")
async def code_assistance(code_request: CodeRequest):
    """Code-specific AI assistance"""
    try:
        if not code_rag:
            raise HTTPException(status_code=503, detail="Code RAG not initialized")
        
        if code_request.operation == "completion":
            result = await code_rag.code_completion(
                code_request.code,
                code_request.language,
                code_request.context_files
            )
        elif code_request.operation == "explanation":
            result = await code_rag.explain_code(
                code_request.code,
                code_request.language
            )
        elif code_request.operation == "debugging":
            result = await code_rag.find_bugs(
                code_request.code,  # Treating code as error message for now
                ""  # No stack trace provided
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {code_request.operation}")
        
        return result
        
    except Exception as e:
        logger.error(f"Code assistance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_system_statistics():
    """Get comprehensive system statistics"""
    try:
        stats = {}
        
        if rag_orchestrator:
            stats = rag_orchestrator.get_system_statistics()
        
        # Add organism statistics
        if organism_manager:
            stats["organisms"] = {
                "active_count": len(organism_manager.organisms),
                "max_organisms": organism_manager.max_organisms,
                "replication_rate": organism_manager.replication_rate
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Statistics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reindex")
async def trigger_reindex(background_tasks: BackgroundTasks, force: bool = False):
    """Trigger system reindexing"""
    try:
        if not vector_manager:
            raise HTTPException(status_code=503, detail="Vector manager not initialized")
        
        # Run reindexing in background
        background_tasks.add_task(vector_manager.reindex_async, force)
        
        return {
            "status": "reindex_started",
            "force": force,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
    except Exception as e:
        logger.error(f"Reindex trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/export")
async def export_graph(format: str = "json"):
    """Export graph for visualization"""
    try:
        if not graph_memory:
            raise HTTPException(status_code=503, detail="Graph memory not initialized")
        
        graph_data = graph_memory.export_for_visualization(format)
        return graph_data
        
    except Exception as e:
        logger.error(f"Graph export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/hotspots")
async def get_graph_hotspots(limit: int = 10):
    """Get graph hotspots for analysis"""
    try:
        if not graph_memory:
            raise HTTPException(status_code=503, detail="Graph memory not initialized")
        
        hotspots = graph_memory.get_hotspots(limit)
        return {"hotspots": hotspots, "limit": limit}
        
    except Exception as e:
        logger.error(f"Hotspot analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organisms/create")
async def create_organism(pilot_id: str, focus_area: str):
    """Create new AI organism"""
    try:
        if not organism_manager:
            raise HTTPException(status_code=503, detail="Organism manager not initialized")
        
        organism = await organism_manager.create_organism(focus_area, pilot_id)
        
        # Start organism lifecycle in background
        asyncio.create_task(organism_manager.organism_lifecycle(organism))
        
        return organism
        
    except Exception as e:
        logger.error(f"Organism creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organisms")
async def list_organisms():
    """List active AI organisms"""
    try:
        if not organism_manager:
            return {"organisms": [], "count": 0}
        
        organisms_info = []
        for organism in organism_manager.organisms:
            organisms_info.append({
                "id": organism["id"],
                "focus_area": organism["focus_area"],
                "pilot_id": organism["pilot_id"],
                "generation": organism["generation"],
                "qa_count": len(organism["qa_history"]),
                "enrichment_count": len(organism["enrichment_data"]),
                "created_at": organism["created_at"]
            })
        
        return {
            "organisms": organisms_info,
            "count": len(organisms_info),
            "max_organisms": organism_manager.max_organisms
        }
        
    except Exception as e:
        logger.error(f"Organism listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time retrieval updates"""
    await websocket.accept()
    
    try:
        logger.info("WebSocket client connected")
        
        while True:
            # Send periodic system status
            if rag_orchestrator:
                stats = rag_orchestrator.get_system_statistics()
                await websocket.send_json({
                    "type": "status_update",
                    "data": stats,
                    "timestamp": str(asyncio.get_event_loop().time())
                })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Main entry point
if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )