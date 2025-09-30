# HAASP: Comprehensive System Instructions
## Hyper-Advanced Associative Application Synthesis Platform

**Version**: 2.0.0  
**Target OS**: Arch Linux, Zen kernel, KDE Plasma 6, Wayland  
**GPU**: NVIDIA RTX 3050 Ti (nvidia-open-dkms)  
**Development Environment**: VS Code (NOT Qt Creator)  
**Audio**: PipeWire  
**Status**: Core QML Interface ✅ WORKING | Advanced Features ⚠️ PENDING IMPLEMENTATION

---

## 1. PROJECT STATUS & ACHIEVEMENTS

### ✅ SUCCESSFULLY IMPLEMENTED
- **C++ Core Engine**: Full compilation success with libgit2, protobuf, gRPC integration
- **QML Interface**: Working Qt6 application with simplified components (avoiding Kirigami dependencies)
- **Resource System**: Traditional .qrc file approach working for QML file loading
- **Build System**: CMake/Ninja configuration optimized for Arch Linux
- **Python Environment**: Virtual environment with ML dependencies (torch, transformers, etc.)
- **Rust WebApp**: Analytics server compiling and running on port 7420
- **Git Service**: Core Git operations via libgit2
- **VS Code Integration**: All development happening in VS Code with Qt extensions

### ⚠️ PENDING CRITICAL IMPLEMENTATIONS
- **Hybrid Data Retrieval System**: FAISS + HNSW + FTS5 + Neural Graph Memory
- **Voice Activation Detection**: PipeWire-based VAD with RMS thresholds
- **AI Pilots System**: Sentinel, Doc Architect, Remediator, Codewright
- **Vector Storage & Indexing**: All conversations/data/code vectorized with embeddings
- **RAG Implementation**: Retrieval-Augmented Generation with Grok API integration
- **Advanced Analytics**: GitHub-like Insights++ with sophisticated metrics
- **Drag & Drop Canvas**: Infinite canvas for pilot orchestration
- **Memory Systems**: Conversation history, context awareness, semantic search

---

## 2. DETAILED TROUBLESHOOTING HISTORY & RESOLUTIONS

### Issue 1: Qt6 Package Dependencies on Arch Linux
**Problem**: `qt6-quickcontrols2` package not found
**Root Cause**: Arch Linux removed qt6-quickcontrols2 package in late 2024, merged into qt6-declarative
**Solution Applied**: 
```bash
sudo pacman -Syu qt6-base qt6-declarative qt6-tools qt6-svg qt6-wayland
```
**Lesson**: Arch rolling release requires monitoring AUR comments for package changes

### Issue 2: libgit2 CMake Detection Failure
**Problem**: `Package 'libgit2' not found`
**Root Cause**: libgit2 not installed on system
**Solution Applied**:
```bash
sudo pacman -S libgit2 pkgconf
# CMakeLists.txt: pkg_check_modules(LIBGIT2 REQUIRED IMPORTED_TARGET libgit2)
```
**Result**: CMake can now find and link libgit2 properly

### Issue 3: QML Module Import Failures
**Problem**: Kirigami modules not installed/linked correctly
**Root Cause**: Complex Kirigami dependencies vs simplified development needs
**Solution Applied**: Created SimpleMain.qml with standard Qt Quick components only
**Code Pattern**:
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
// NO Kirigami imports - use standard Qt components
```

### Issue 4: Meta-Type Redefinition Conflicts
**Problem**: `error: redefinition of 'struct QMetaTypeId<haasp::ui::Controller*>'`
**Root Cause**: Conflicting QML_DECLARE_TYPE and QML_ELEMENT macros
**Solution Applied**: Removed automatic registration, used manual registration in main.cpp
**Prevention**: Avoid mixing automatic and manual QML type registration

### Issue 5: Resource Loading Path Issues
**Problem**: `qrc:/qml/Main.qml: No such file or directory`
**Root Cause**: qt_add_resources vs traditional .qrc file handling
**Solution Applied**: 
- Created traditional resources.qrc file
- Added multiple path fallback logic in main.cpp
- SimpleMain.qml as working baseline

### Issue 6: Build System Generator Confusion
**Problem**: CMake generating Ninja files but scripts using make
**Root Cause**: Mixed generator usage across scripts
**Solution Applied**: Standardized on Ninja throughout, updated all scripts
**Pattern**: Always use `cmake .. -G Ninja` then `ninja` for builds

---

## 3. HYBRID DATA RETRIEVAL SYSTEM ARCHITECTURE
*Based on TelePrompt patterns, enhanced for HAASP needs*

### 3.1 Core Components

#### Vector Storage Layer
```python
# faiss_manager.py - Enhanced from TelePrompt
class HybridVectorManager:
    def __init__(self):
        self.faiss_index = None  # HNSW for fast queries, IVF-PQ for large scale
        self.doc_map = {}        # SQLite instead of .npy for robustness
        self.conversation_indexes = {}  # Per-pilot memory
        self.embedder = SentenceTransformer('e5-base-v2')  # Local model
        
    def build_index(self, documents, index_type="HNSW"):
        """Build FAISS index with M=32, efConstruction=200"""
        
    def query_semantic(self, query, k=10):
        """Vector similarity search"""
        
    def add_conversation(self, pilot_id, utterance):
        """Add to per-pilot conversation memory"""
```

#### Fuzzy/Lexical Search Layer
```python
# fts_manager.py - NEW: Not in TelePrompt
class FuzzySearchManager:
    def __init__(self):
        self.conn = sqlite3.connect("search.db")
        # CREATE VIRTUAL TABLE docs_fts USING fts5(content, path, tokenize='trigram')
        
    def add_document(self, path, content):
        """Add to FTS5 trigram index"""
        
    def query_fuzzy(self, query, k=10):
        """Substring and wildcard search"""
        
    def levenshtein_search(self, query, max_distance=2):
        """Approximate string matching"""
```

#### Neural Graph Memory
```python
# graph_memory.py - NEW: Advanced reasoning layer
class NeuralGraphMemory:
    def __init__(self):
        self.graph = nx.DiGraph()  # Or Neo4j for persistence
        self.embeddings = {}       # Node embeddings
        
    def add_node(self, node_id, node_type, metadata, embedding):
        """Add code/doc/utterance node"""
        
    def add_similarity_edges(self, threshold=0.7):
        """Connect semantically similar nodes"""
        
    def query_neighborhood(self, node_id, max_depth=3):
        """Graph traversal for reasoning"""
        
    def reasoning_walk(self, start_nodes, goal_type):
        """Multi-hop reasoning queries"""
```

### 3.2 Fusion & RAG Layer
```python
# rag_orchestrator.py - NEW: Multi-source retrieval + generation
class RAGOrchestrator:
    def __init__(self):
        self.vector_mgr = HybridVectorManager()
        self.fuzzy_mgr = FuzzySearchManager()
        self.graph_mgr = NeuralGraphMemory()
        self.grok_client = GrokAPIClient()
        
    def hybrid_retrieve(self, query, mode="all"):
        """RRF fusion of vector + fuzzy + graph results"""
        vector_results = self.vector_mgr.query_semantic(query, k=20)
        fuzzy_results = self.fuzzy_mgr.query_fuzzy(query, k=20)
        graph_results = self.graph_mgr.query_neighborhood(query)
        
        # Reciprocal Rank Fusion
        return self._fuse_results(vector_results, fuzzy_results, graph_results)
        
    def generate_response(self, query, context_chunks):
        """RAG with Grok API, key rotation on rate limits"""
        return self.grok_client.chat_completion(query, context_chunks)
```

---

## 4. VOICE ACTIVATION SYSTEM
*Adapted from TelePrompt VAD for Linux/PipeWire*

### 4.1 Voice Activity Detection
```python
# vad.py - Ported from TelePrompt for PipeWire
class VoiceActivityDetector:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.threshold = None  # Calibrated dynamically
        self.speech_state = False
        self.buffer = collections.deque(maxlen=160000)  # 10 seconds
        
    def calibrate_threshold(self, duration=5.0):
        """Record ambient noise and set RMS threshold"""
        # Use sounddevice with PipeWire backend
        
    def process_audio_chunk(self, audio_chunk):
        """RMS-based speech detection"""
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        
        if rms > self.threshold and not self.speech_state:
            self.speech_state = True
            return "speech_start"
        elif rms < self.threshold and self.speech_state:
            self.speech_state = False
            return "speech_end"
            
    def get_speech_segment(self):
        """Extract recorded segment from circular buffer"""
        return np.array(self.buffer)
```

### 4.2 Audio Capture for Linux
```python
# audio_capture.py - Linux/PipeWire version
import sounddevice as sd

class PipeWireAudioCapture:
    def __init__(self):
        # Find PipeWire device or use default
        self.device = self._find_pipewire_device()
        
    def _find_pipewire_device(self):
        """Find best PipeWire input device"""
        devices = sd.query_devices()
        for device in devices:
            if 'pipewire' in device['name'].lower() and device['max_input_channels'] > 0:
                return device['name']
        return None  # Use default
        
    def start_capture(self, callback):
        """Start continuous audio capture"""
        with sd.InputStream(device=self.device, 
                          samplerate=16000, 
                          channels=1,
                          callback=callback):
            # Stream runs until stopped
```

---

## 5. AI PILOTS SYSTEM ARCHITECTURE

### 5.1 Pilot Definitions
```json
{
  "pilots": {
    "pilot_0_sentinel": {
      "name": "Sentinel",
      "role": "Pre-zero analyzer preventing repetition and regressions",
      "memory": {
        "faiss_index": "~/.local/share/haasp/pilot_0/vectors.faiss",
        "conversation_history": "~/.local/share/haasp/pilot_0/conversations.db",
        "event_log": "~/.local/share/haasp/pilot_0/events.jsonl"
      },
      "capabilities": [
        "mistake_detection",
        "repetition_prevention", 
        "event_recording",
        "consistency_validation"
      ]
    },
    "pilot_1_doc_architect": {
      "name": "Doc Architect", 
      "role": "Full documentation generation with dependency graphs",
      "memory": {
        "knowledge_graph": "~/.local/share/haasp/pilot_1/knowledge.neo4j",
        "templates": "~/.local/share/haasp/pilot_1/templates/",
        "generated_docs": "~/.local/share/haasp/pilot_1/outputs/"
      }
    },
    "pilot_2_remediator": {
      "name": "Remediator",
      "role": "Multi-API issue fixer with automated patches",
      "capabilities": [
        "diagnostic_analysis",
        "patch_generation", 
        "safe_automated_edits",
        "pr_creation"
      ]
    },
    "pilot_3_codewright": {
      "name": "Codewright", 
      "role": "AST-aware code synthesis and refactoring",
      "capabilities": [
        "ast_analysis",
        "code_generation",
        "test_synthesis",
        "refactoring_suggestions"
      ]
    }
  }
}
```

### 5.2 Pilot Chain Orchestration
```cpp
// pilots.hpp - C++ orchestration layer
namespace haasp {
    class PilotOrchestrator {
    public:
        struct PilotResult {
            std::string pilot_id;
            std::vector<std::string> outputs;
            std::map<std::string, double> confidence_scores;
            std::chrono::milliseconds processing_time;
        };
        
        // Chain execution with topological sorting
        std::vector<PilotResult> executeChain(const std::string& chain_id);
        
        // Individual pilot execution
        PilotResult executePilot(const std::string& pilot_id, const std::map<std::string, std::string>& inputs);
        
    private:
        std::unique_ptr<RetrievalService> retrieval_service_;
        std::unique_ptr<VoiceService> voice_service_;
        std::map<std::string, std::unique_ptr<BasePilot>> pilots_;
    };
}
```

---

## 6. MISSING FEATURES ANALYSIS & IMPLEMENTATION PLAN

### 6.1 Critical Missing Components from HAASP Project

Based on the file browser images showing the original HAASP project structure, these components need to be migrated to AppiT-Pro:

#### Advanced QML Components (Missing)
```qml
// CanvasView.qml - Infinite drag-to-pan canvas
Item {
    id: infiniteCanvas
    
    property real zoomLevel: 1.0
    property point panOffset: Qt.point(0, 0)
    
    PinchHandler {
        target: canvasContent
        minimumScale: 0.1
        maximumScale: 10.0
    }
    
    DragHandler {
        target: canvasContent
        onActiveChanged: if (active) canvasContent.grabToImage(updateSnapshot)
    }
    
    // Pilot node rendering with connection ports
    Repeater {
        model: pilotsModel
        delegate: PilotCard {
            x: model.x; y: model.y
            pilotData: model
            onConnectionRequested: canvas.createConnection(sourcePort, targetPort)
        }
    }
}
```

#### Analytics Visualization (Missing)
```qml
// InsightsView.qml - GitHub-like analytics with more features
ScrollView {
    ColumnLayout {
        // Repository overview with advanced metrics
        GitAnalyticsPanel {
            metrics: [
                "commit_velocity", "code_churn", "ownership_distribution",
                "temporal_coupling", "risk_hotspots", "bus_factor",
                "change_failure_rate", "lead_time_p95", "pilot_impact"
            ]
        }
        
        // Live updating charts
        ChartGrid {
            charts: [
                CommitVelocityChart { /* Real-time updates */ },
                OwnershipSunburst { /* Interactive drill-down */ },
                RiskHeatmap { /* File-level risk visualization */ },
                CouplingNetwork { /* Temporal coupling graph */ }
            ]
        }
    }
}
```

### 6.2 Hybrid Storage Implementation Requirements

#### Multi-Modal Storage Architecture
```python
# hybrid_storage.py - The "HAN" (Hybrid Archival Nexus)
class HybridArchivalNexus:
    def __init__(self):
        # Vector stores
        self.faiss_semantic = None      # Semantic embeddings
        self.faiss_conversation = None  # Conversation history
        self.hnsw_hot = None           # Hot/recent vectors
        
        # Structured storage
        self.sqlite_meta = None        # Metadata, doc maps, events
        self.sqlite_fts = None         # Full-text search with trigrams
        
        # Graph storage
        self.neo4j_graph = None        # Relationship graph
        self.networkx_memory = None    # In-memory graph cache
        
        # KV Cache
        self.rocksdb_cache = None      # High-speed cache layer
        
        # Time-series
        self.influxdb_metrics = None   # Optional metrics storage
        
    def vectorize_all(self, data_type, content):
        """Vectorize every piece of data that enters the system"""
        # ALL conversations, code, docs, errors, commands vectorized
        
    def index_everything(self, source_type, data):
        """Multi-modal indexing: vector + text + graph + cache"""
        
    def hybrid_search(self, query, modes=["semantic", "fuzzy", "graph"]):
        """Multi-modal search with RRF fusion"""
        
    def conversation_aware_retrieval(self, pilot_id, query, context_window=10):
        """Context-aware search using conversation history"""
```

### 6.3 Voice Integration for Linux

#### PipeWire Integration (Replacing Windows Virtual Audio)
```python
# voice_integration.py - Linux voice system
class LinuxVoiceSystem:
    def __init__(self):
        self.vad = VoiceActivityDetector()
        self.capture = PipeWireAudioCapture()
        self.transcription_queue = asyncio.Queue()
        
    async def start_voice_loop(self):
        """Main voice processing loop"""
        await self.vad.calibrate_threshold()
        
        async def audio_callback(audio_chunk):
            event = self.vad.process_audio_chunk(audio_chunk)
            if event == "speech_end":
                segment = self.vad.get_speech_segment()
                await self.transcription_queue.put(segment)
                
        await self.capture.start_capture(audio_callback)
        
    async def transcribe_and_process(self):
        """Transcribe speech segments and add to retrieval system"""
        while True:
            segment = await self.transcription_queue.get()
            # Transcribe with Grok or local Whisper
            transcript = await self.transcribe_audio(segment)
            # Add to conversation memory
            await self.add_to_memory(transcript)
```

---

## 7. ADVANCED FEATURES IMPLEMENTATION

### 7.1 Semantic Search & Context Memory
```python
# context_memory.py - Conversation awareness
class ConversationMemory:
    def __init__(self):
        self.current_context = []
        self.context_embeddings = []
        self.context_graph = nx.DiGraph()
        
    def add_interaction(self, user_input, ai_response, pilot_id):
        """Add interaction to searchable memory"""
        # Vectorize both input and response
        # Link to related code/docs via graph
        # Store with timestamp and pilot context
        
    def get_relevant_context(self, query, pilot_id, k=5):
        """Retrieve relevant conversation history"""
        # Semantic search across conversation history
        # Filter by pilot and recency
        # Return context for RAG
```

### 7.2 Advanced Analytics Engine
```cpp
// git_analytics.cpp - Advanced repository analytics
namespace haasp {
    class GitAnalyticsEngine {
    public:
        struct RepositoryMetrics {
            double commit_velocity;
            std::map<std::string, double> ownership_distribution;
            std::vector<std::pair<std::string, std::string>> temporal_coupling;
            std::map<std::string, double> risk_scores;
            int bus_factor;
            double change_failure_rate;
            std::chrono::milliseconds lead_time_p95;
        };
        
        RepositoryMetrics computeAdvancedMetrics(const std::string& repo_path);
        std::vector<FileRisk> identifyHotspots(const std::string& repo_path);
        CouplingMatrix computeTemporalCoupling(const std::string& repo_path);
        
    private:
        // SZZ algorithm for bug-introducing changes
        std::vector<std::string> identifyBugIntroducingCommits(const std::string& file_path);
        
        // Ownership analysis with time decay
        std::map<std::string, double> computeOwnership(const std::string& file_path);
    };
}
```

### 7.3 Grok API Integration with Rate Limiting
```python
# grok_client.py - Rate-limited API client
class GrokAPIClient:
    def __init__(self):
        self.api_keys = [
            os.getenv("GROK_4_CODE_FAST_API_KEY"),
            os.getenv("GROK_4_GENERAL_API_KEY"),
            # Additional backup keys
        ]
        self.current_key_index = 0
        self.rate_limiter = TokenBucket(requests_per_minute=60)
        
    async def chat_completion(self, messages, model="grok-4", task_type="general"):
        """Chat completion with automatic key rotation"""
        if task_type == "code":
            model = "grok-4-code-fast-1"
            
        for attempt in range(len(self.api_keys)):
            try:
                await self.rate_limiter.acquire()
                response = await self._make_request(messages, model)
                return response
            except RateLimitError:
                self._rotate_key()
                await asyncio.sleep(1)  # Brief pause before retry
                
    def _rotate_key(self):
        """Rotate to next available API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
```

---

## 8. QML/C++ INTEGRATION PATTERNS (VS CODE COMPATIBLE)

### 8.1 QML Component Registration
```cpp
// main.cpp - Manual registration (not Qt Creator auto-generation)
int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    
    // Manual QML type registration for VS Code compatibility
    qmlRegisterSingletonType<haasp::GitService>(
        "org.haasp.core", 1, 0, "GitService",
        [](QQmlEngine *, QJSEngine *) -> QObject * {
            return new haasp::GitService();
        });
        
    qmlRegisterType<haasp::PilotOrchestrator>("org.haasp.core", 1, 0, "PilotOrchestrator");
    qmlRegisterType<haasp::RetrievalService>("org.haasp.core", 1, 0, "RetrievalService");
    
    // Load QML with fallback paths for VS Code development
    QQmlApplicationEngine engine;
    QString qmlPath = findProjectRoot() + "/src/ui/qml/Main.qml";
    engine.load(QUrl::fromLocalFile(qmlPath));
    
    return app.exec();
}
```

### 8.2 Async C++/QML Communication
```cpp
// retrieval_service.hpp - Async communication patterns
class RetrievalService : public QObject {
    Q_OBJECT
    
public slots:
    void performSemanticSearch(const QString& query);
    void addToMemory(const QString& content, const QString& source);
    
signals:
    void searchResults(const QVariantList& results);
    void memoryUpdated(const QString& status);
    
private:
    // QtConcurrent for background processing
    void executeSearchAsync(const QString& query);
};
```

---

## 9. DIRECTORY STRUCTURE (COMPLETE)

```
AppiT-Pro/  (Current working directory)
├── src/
│   ├── nucleus/                 # ✅ IMPLEMENTED
│   │   ├── associative_nexus.cpp/hpp
│   │   ├── quantum_conduit.cpp/hpp  
│   │   └── git_service.cpp/hpp
│   ├── ui/
│   │   ├── qml/                 # ✅ WORKING (SimpleMain.qml)
│   │   │   ├── SimpleMain.qml   # ✅ Current working interface
│   │   │   ├── Main.qml         # ⚠️ Complex version (Kirigami issues)
│   │   │   └── [other QML files]
│   │   └── controller.cpp/hpp   # ✅ IMPLEMENTED
├── python/
│   ├── enrichment_pipeline/     # ⚠️ BASIC IMPLEMENTATION
│   │   └── git_intelligence.py  # Basic but needs hybrid retrieval
│   └── [MISSING: Advanced retrieval services]
├── webapp/                      # ✅ RUST ANALYTICS WORKING
├── build/                       # ✅ SUCCESSFUL BUILDS
├── resources.qrc               # ✅ WORKING RESOURCE FILE
└── [MISSING: Advanced voice, RAG, pilots]

REQUIRED ADDITIONS:
├── retrieval_service/           # ⚠️ NEEDS IMPLEMENTATION
│   ├── faiss_manager.py         # Vector storage & search
│   ├── fts_manager.py           # Fuzzy/substring search  
│   ├── graph_memory.py          # Neural graph relationships
│   ├── rag_orchestrator.py      # RAG with Grok integration
│   └── voice_integration.py     # Voice activation for Linux
├── pilots/                      # ⚠️ NEEDS IMPLEMENTATION
│   ├── sentinel.py              # Pilot 0: Mistake prevention
│   ├── doc_architect.py         # Pilot 1: Documentation
│   ├── remediator.py            # Pilot 2: Issue fixing
│   └── codewright.py            # Pilot 3: Code synthesis
├── advanced_ui/                 # ⚠️ NEEDS IMPLEMENTATION
│   ├── InfiniteCanvas.qml       # Drag & drop pilot canvas
│   ├── PilotCard.qml            # Pilot visualization
│   ├── InsightsView.qml         # Advanced analytics
│   └── VoiceInterface.qml       # Voice activation UI
└── memory_systems/              # ⚠️ NEEDS IMPLEMENTATION
    ├── conversation_memory.py   # Context-aware memory
    ├── vectorization_engine.py  # Everything vectorized
    └── context_retrieval.py     # Intelligent context lookup
```

---

## 10. IMPLEMENTATION PRIORITIES

### Phase 1: Foundation Enhancement (Immediate)
1. **Migrate Advanced Features**: Copy missing components from `/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/HAASP` 
2. **Implement Hybrid Retrieval**: Build faiss_manager, fts_manager, graph_memory
3. **Voice System**: Port TelePrompt VAD to PipeWire
4. **Pilot Framework**: Create base pilot classes and orchestration

### Phase 2: Advanced Interface (Week 2)
1. **Infinite Canvas**: Implement drag-and-drop pilot design interface
2. **Advanced Analytics**: GitHub-like Insights++ with superior metrics
3. **Voice Interface**: Speech-to-text integration with Grok
4. **Context Memory**: Conversation-aware retrieval system

### Phase 3: AI Integration (Week 3)
1. **RAG System**: Full retrieval-augmented generation pipeline
2. **Pilot Intelligence**: All 4 pilots with memory and reasoning
3. **Auto-Vectorization**: Everything stored as searchable vectors
4. **Advanced Reasoning**: Graph-based multi-hop queries

---

## 11. TECHNICAL SPECIFICATIONS

### 11.1 Performance Targets
- **Vector Search**: <120ms p95 latency on RTX 3050 Ti
- **Voice Detection**: <50ms response time for speech events  
- **Canvas Rendering**: 60fps with 1000+ nodes
- **Context Retrieval**: <200ms for conversation-aware search
- **RAG Generation**: <3s for code assistance, <5s for documentation

### 11.2 Memory Architecture
```python
# Memory hierarchy for optimal performance
MEMORY_HIERARCHY = {
    "L1_HOT": {
        "storage": "in_memory_cache",
        "size": "256MB", 
        "latency": "<1ms",
        "content": "current_conversation, active_pilots"
    },
    "L2_WARM": {
        "storage": "rocksdb_cache",
        "size": "2GB",
        "latency": "<10ms", 
        "content": "recent_searches, vector_cache"
    },
    "L3_COLD": {
        "storage": "faiss_index + sqlite",
        "size": "unlimited",
        "latency": "<100ms",
        "content": "all_historical_data, full_codebase"
    }
}
```

---

## 12. BUILD INSTRUCTIONS (VS CODE WORKFLOW)

### 12.1 Environment Setup
```bash
# From AppiT-Pro directory
cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

# Install missing Python packages for advanced features
source .venv/bin/activate
pip install sentence-transformers faiss-cpu networkx neo4j sounddevice asyncio-mqtt

# Install additional Arch packages for voice/graph
sudo pacman -S portaudio pipewire-pulse neo4j
```

### 12.2 VS Code Configuration
```json
// .vscode/settings.json
{
    "cmake.generator": "Ninja",
    "cmake.buildDirectory": "${workspaceFolder}/build",
    "qt.qmlls.enabled": true,
    "qt.cmake.enabled": true,
    "python.defaultInterpreterPath": "./.venv/bin/python"
}
```

### 12.3 Build Process
```bash
# Clean rebuild with all features
rm -rf build
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
ninja

# Start enhanced application
./haasp
```

---

## 13. GROK API INTEGRATION PATTERN

### 13.1 Rate-Limited Client Implementation
```python
# grok_integration.py - Production-grade API client
class GrokAPIManager:
    def __init__(self):
        self.keys = {
            "code_fast": os.getenv("GROK_4_CODE_FAST_API_KEY"),
            "general": os.getenv("GROK_4_GENERAL_API_KEY"),
            # Additional keys for rotation
        }
        self.rate_limiters = {
            key: TokenBucket(rate=60, capacity=100) for key in self.keys
        }
        
    async def smart_completion(self, prompt, task_type="general", context=None):
        """Intelligent model selection and rate limiting"""
        model = "grok-4-code-fast-1" if task_type == "code" else "grok-4"
        key_type = "code_fast" if task_type == "code" else "general"
        
        # Format request with context if available
        messages = []
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": prompt})
        
        # Execute with rate limiting and fallbacks
        return await self._execute_with_fallback(messages, model, key_type)
```

---

## 14. SYSTEM ACTIVATION CHECKLIST

### 14.1 Pre-Requirements Verification
- [ ] ✅ Arch Linux with Zen kernel
- [ ] ✅ KDE Plasma 6 on Wayland  
- [ ] ✅ VS Code with Qt extensions installed
- [ ] ✅ Qt6 packages (qt6-base, qt6-declarative, qt6-tools)
- [ ] ✅ libgit2 installed and CMake-detectable
- [ ] ✅ Python 3.12+ with ML libraries
- [ ] ⚠️ PipeWire audio system configured
- [ ] ⚠️ NVIDIA drivers (nvidia-open-dkms) for GPU acceleration
- [ ] ⚠️ API keys stored in KWallet/libsecret

### 14.2 Feature Activation Sequence
1. **Core QML Interface** ✅ WORKING
2. **Basic Git Integration** ✅ WORKING  
3. **Hybrid Retrieval System** ⚠️ IMPLEMENT NEXT
4. **Voice Activation** ⚠️ IMPLEMENT NEXT
5. **AI Pilots** ⚠️ IMPLEMENT NEXT
6. **Advanced Analytics** ⚠️ IMPLEMENT NEXT
7. **Infinite Canvas** ⚠️ IMPLEMENT NEXT

---

## 15. NEXT ACTIONS REQUIRED

### Immediate Implementation Tasks
1. **Copy Advanced Components**: Migrate all missing features from original HAASP project
2. **Implement Retrieval Service**: Build Python service with FAISS + FTS5 + Graph
3. **Voice Integration**: Implement PipeWire-based voice activation
4. **Pilot System**: Create all 4 pilots with memory and reasoning
5. **Advanced UI**: Build infinite canvas and analytics visualization
6. **API Integration**: Complete Grok integration with rate limiting

### Testing & Validation
1. **Vector Search Performance**: Benchmark search latency targets
2. **Voice Detection Accuracy**: Test VAD calibration and recognition
3. **Memory Retention**: Validate conversation context awareness
4. **Multi-Modal Retrieval**: Test semantic + fuzzy + graph fusion
5. **End-to-End Workflow**: Complete pilot chain execution

---

## 16. CONCLUSION

**Current Status**: Foundation successfully established with working QML interface and core C++ engine.

**Achievement**: Resolved all major build system issues, package dependencies, and QML module conflicts for VS Code development.

**Next Phase**: Implement the sophisticated hybrid retrieval system, voice activation, AI pilots, and advanced analytics to achieve the full HAASP vision.

**Architecture**: Ready for hybrid C++/QML/Python implementation with local-first design, no external dependencies except Grok API for generation.

**Development Environment**: Fully configured for VS Code (not Qt Creator) on Arch Linux with Wayland support.

This system instruction provides the complete roadmap for engineers to build HAASP from scratch, incorporating all requested advanced features while maintaining the successful foundation we've established.

---

*Generated with Memex AI Assistant*  
*Co-Authored-By: Memex <noreply@memex.tech>*