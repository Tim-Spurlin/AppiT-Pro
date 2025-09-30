#!/usr/bin/env python3
"""
Git Intelligence Pipeline for HAASP

Provides ML-driven code analysis, quality prediction, and change impact assessment.
Integrates with GitService through Kafka messaging for real-time insights.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import git
from kafka import KafkaConsumer, KafkaProducer
import networkx as nx
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeMetrics:
    """Represents code quality metrics for a file or commit"""
    file_path: str
    lines_of_code: int
    complexity: float
    test_coverage: float
    technical_debt: float
    maintainability_score: float
    bug_probability: float

@dataclass
class ChangeImpact:
    """Represents the impact of a code change"""
    affected_files: List[str]
    risk_score: float
    suggested_tests: List[str]
    coupling_strength: float
    blast_radius: int

class CodeEmbeddingModel:
    """BERT-based model for generating code embeddings"""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def encode(self, code_text: str) -> np.ndarray:
        """Generate embedding for code snippet"""
        inputs = self.tokenizer(
            code_text, 
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use CLS token embedding
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        
        return embedding.flatten()

class QualityPredictor:
    """ML model for predicting code quality metrics"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = []
    
    def extract_features(self, code_text: str, git_history: List[Dict]) -> np.ndarray:
        """Extract features from code and Git history"""
        features = []
        
        # Basic code metrics
        lines = code_text.count('\n')
        functions = code_text.count('function') + code_text.count('def ')
        complexity = self._calculate_complexity(code_text)
        
        features.extend([lines, functions, complexity])
        
        # Git history features
        if git_history:
            commits = len(git_history)
            authors = len(set(commit.get('author', '') for commit in git_history))
            avg_commit_size = np.mean([commit.get('changes', 0) for commit in git_history])
            
            features.extend([commits, authors, avg_commit_size])
        else:
            features.extend([0, 0, 0])
        
        return np.array(features)
    
    def _calculate_complexity(self, code_text: str) -> float:
        """Calculate cyclomatic complexity"""
        # Simplified complexity calculation
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'catch', 'switch']
        complexity = 1  # Base complexity
        
        for keyword in complexity_keywords:
            complexity += code_text.count(keyword)
        
        return complexity
    
    def train(self, training_data: List[Tuple[str, List[Dict], float]]):
        """Train the quality prediction model"""
        X = []
        y = []
        
        for code_text, git_history, quality_score in training_data:
            features = self.extract_features(code_text, git_history)
            X.append(features)
            y.append(quality_score)
        
        X = np.array(X)
        y = np.array(y)
        
        self.model.fit(X, y)
        self.is_trained = True
        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        
        logger.info(f"Quality predictor trained with {len(training_data)} samples")
    
    def predict(self, code_text: str, git_history: List[Dict]) -> float:
        """Predict quality score for code"""
        if not self.is_trained:
            return 0.5  # Default neutral score
        
        features = self.extract_features(code_text, git_history).reshape(1, -1)
        prediction = self.model.predict(features)[0]
        
        # Clip to valid range
        return max(0.0, min(1.0, prediction))

class CouplingAnalyzer:
    """Analyzes code coupling and dependencies"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.embedding_model = CodeEmbeddingModel()
    
    def analyze_repository(self, repo_path: Path) -> Dict[str, float]:
        """Analyze coupling across entire repository"""
        source_files = list(repo_path.rglob("*.py")) + list(repo_path.rglob("*.qml"))
        
        # Build dependency graph
        self._build_dependency_graph(source_files)
        
        # Calculate coupling metrics
        coupling_scores = {}
        for file_path in source_files:
            coupling_scores[str(file_path)] = self._calculate_coupling(file_path)
        
        return coupling_scores
    
    def _build_dependency_graph(self, source_files: List[Path]):
        """Build dependency graph from source files"""
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add node
                self.dependency_graph.add_node(str(file_path))
                
                # Extract imports/dependencies (simplified)
                if file_path.suffix == '.py':
                    self._extract_python_dependencies(file_path, content)
                elif file_path.suffix == '.qml':
                    self._extract_qml_dependencies(file_path, content)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
    
    def _extract_python_dependencies(self, file_path: Path, content: str):
        """Extract Python import dependencies"""
        import re
        
        import_pattern = r'^\s*(?:from\s+(\S+)\s+)?import\s+(\S+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1) or match.group(2)
            # Simplified - just track internal dependencies
            if not module.startswith(('.', '/')):
                continue
            
            self.dependency_graph.add_edge(str(file_path), module)
    
    def _extract_qml_dependencies(self, file_path: Path, content: str):
        """Extract QML import dependencies"""
        import re
        
        import_pattern = r'^\s*import\s+(\S+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1)
            self.dependency_graph.add_edge(str(file_path), module)
    
    def _calculate_coupling(self, file_path: Path) -> float:
        """Calculate coupling score for a file"""
        file_str = str(file_path)
        
        if file_str not in self.dependency_graph:
            return 0.0
        
        # Afferent coupling (incoming dependencies)
        afferent = len(list(self.dependency_graph.predecessors(file_str)))
        
        # Efferent coupling (outgoing dependencies) 
        efferent = len(list(self.dependency_graph.successors(file_str)))
        
        # Combined coupling score
        total_coupling = afferent + efferent
        max_possible = len(self.dependency_graph.nodes) - 1
        
        return total_coupling / max_possible if max_possible > 0 else 0.0

class GitIntelligencePipeline:
    """Main pipeline for Git-based code intelligence"""
    
    def __init__(self, kafka_bootstrap_servers: List[str] = None):
        self.kafka_servers = kafka_bootstrap_servers or ['localhost:9092']
        self.embedding_model = CodeEmbeddingModel()
        self.quality_predictor = QualityPredictor()
        self.coupling_analyzer = CouplingAnalyzer()
        
        # Kafka setup
        self.consumer = None
        self.producer = None
    
    async def start(self):
        """Start the intelligence pipeline"""
        logger.info("Starting Git Intelligence Pipeline...")
        
        # Setup Kafka (with fallback if not available)
        try:
            self.consumer = KafkaConsumer(
                'haasp.git.events',
                bootstrap_servers=self.kafka_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000  # Timeout quickly if no Kafka
            )
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            logger.info("✅ Kafka connection established")
            # Start processing loop
            await self._process_git_events()
            
        except Exception as e:
            logger.warning(f"⚠️  Kafka not available: {e}")
            logger.info("🔄 Running in standalone mode without Kafka...")
            self.consumer = None
            self.producer = None
            # Run in standalone mode
            await self._run_standalone_mode()
    
    async def _process_git_events(self):
        """Process incoming Git events"""
        for message in self.consumer:
            try:
                event = message.value
                logger.info(f"Processing Git event: {event.get('type', 'unknown')}")
                
                if event['type'] == 'repository_opened':
                    await self._analyze_repository(event['repo_path'])
                elif event['type'] == 'file_changed':
                    await self._analyze_file_change(event)
                elif event['type'] == 'commit_created':
                    await self._analyze_commit(event)
                
            except Exception as e:
                logger.error(f"Error processing Git event: {e}")
    
    async def _analyze_repository(self, repo_path: str):
        """Analyze entire repository"""
        logger.info(f"Analyzing repository: {repo_path}")
        
        repo = git.Repo(repo_path)
        repo_path_obj = Path(repo_path)
        
        # Calculate coupling
        coupling_scores = self.coupling_analyzer.analyze_repository(repo_path_obj)
        
        # Generate overall metrics
        metrics = {
            'repository_path': repo_path,
            'total_files': len(coupling_scores),
            'average_coupling': np.mean(list(coupling_scores.values())),
            'max_coupling': max(coupling_scores.values()) if coupling_scores else 0,
            'coupling_distribution': coupling_scores,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send results
        self.producer.send('haasp.intelligence.repository_analysis', metrics)
        logger.info("Repository analysis complete")
    
    async def _analyze_file_change(self, event: Dict):
        """Analyze individual file change"""
        file_path = event['file_path']
        repo_path = event['repo_path']
        
        logger.info(f"Analyzing file change: {file_path}")
        
        try:
            # Read file content
            with open(Path(repo_path) / file_path, 'r') as f:
                content = f.read()
            
            # Get Git history for file
            repo = git.Repo(repo_path)
            commits = list(repo.iter_commits(paths=file_path, max_count=20))
            git_history = [
                {
                    'author': commit.author.name,
                    'message': commit.message.strip(),
                    'timestamp': commit.committed_datetime.isoformat(),
                    'changes': len(list(commit.diff(commit.parents[0] if commit.parents else None)))
                }
                for commit in commits
            ]
            
            # Predict quality
            quality_score = self.quality_predictor.predict(content, git_history)
            
            # Generate embedding
            embedding = self.embedding_model.encode(content)
            
            # Calculate change impact
            impact = self._calculate_change_impact(file_path, repo_path, content)
            
            analysis = {
                'file_path': file_path,
                'repository_path': repo_path,
                'quality_score': quality_score,
                'change_impact': impact.__dict__,
                'embedding': embedding.tolist(),
                'metrics': {
                    'lines_of_code': content.count('\n'),
                    'complexity': self.quality_predictor._calculate_complexity(content),
                    'git_commits': len(git_history),
                    'unique_authors': len(set(h['author'] for h in git_history))
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.producer.send('haasp.intelligence.file_analysis', analysis)
            logger.info(f"File analysis complete: {file_path} (quality: {quality_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
    
    def _calculate_change_impact(self, file_path: str, repo_path: str, content: str) -> ChangeImpact:
        """Calculate impact of changes to a file"""
        
        # Get related files based on coupling
        coupling_scores = self.coupling_analyzer.analyze_repository(Path(repo_path))
        current_coupling = coupling_scores.get(str(Path(repo_path) / file_path), 0.0)
        
        # Find highly coupled files
        affected_files = [
            path for path, score in coupling_scores.items()
            if score > 0.3 and path != str(Path(repo_path) / file_path)
        ]
        
        # Calculate risk score based on complexity and coupling
        complexity = self.quality_predictor._calculate_complexity(content)
        risk_score = min(1.0, (complexity * 0.1) + (current_coupling * 0.5))
        
        # Suggest tests (simplified)
        suggested_tests = [f"test_{Path(file_path).stem}.py"] if file_path.endswith('.py') else []
        
        return ChangeImpact(
            affected_files=affected_files[:10],  # Limit to top 10
            risk_score=risk_score,
            suggested_tests=suggested_tests,
            coupling_strength=current_coupling,
            blast_radius=len(affected_files)
        )
    
    async def _analyze_commit(self, event: Dict):
        """Analyze a new commit"""
        commit_id = event['commit_id']
        repo_path = event['repo_path']
        
        logger.info(f"Analyzing commit: {commit_id}")
        
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_id)
            
            # Analyze changed files
            changed_files = []
            for diff in commit.diff(commit.parents[0] if commit.parents else None):
                if diff.a_path:
                    changed_files.append(diff.a_path)
            
            # Calculate commit metrics
            commit_analysis = {
                'commit_id': commit_id,
                'repository_path': repo_path,
                'author': commit.author.name,
                'message': commit.message.strip(),
                'timestamp': commit.committed_datetime.isoformat(),
                'changed_files': changed_files,
                'files_count': len(changed_files),
                'insertions': commit.stats.total['insertions'],
                'deletions': commit.stats.total['deletions'],
                'overall_impact': self._calculate_commit_impact(changed_files, repo_path),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.producer.send('haasp.intelligence.commit_analysis', commit_analysis)
            logger.info(f"Commit analysis complete: {commit_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_id}: {e}")
    
    def _calculate_commit_impact(self, changed_files: List[str], repo_path: str) -> float:
        """Calculate overall impact score for a commit"""
        if not changed_files:
            return 0.0
        
        # Get coupling data
        coupling_scores = self.coupling_analyzer.analyze_repository(Path(repo_path))
        
        # Calculate weighted impact based on file coupling
        total_impact = 0.0
        for file_path in changed_files:
            full_path = str(Path(repo_path) / file_path)
            coupling = coupling_scores.get(full_path, 0.0)
            total_impact += coupling
        
        return min(1.0, total_impact / len(changed_files))

    async def _run_standalone_mode(self):
        """Run in standalone mode without Kafka"""
        logger.info("🔄 Running Git Intelligence Pipeline in standalone mode...")

        # Simple loop that monitors for repositories and processes them
        while True:
            try:
                # Look for repositories in common paths
                import os
                home_dir = os.path.expanduser("~")
                common_paths = [
                    os.path.join(home_dir, "Desktop"),
                    os.path.join(home_dir, "Documents"),
                    os.path.join(home_dir, "Projects"),
                    "/tmp",
                    "."
                ]

                repositories_found = []
                for path in common_paths:
                    if os.path.exists(os.path.join(path, ".git")):
                        repositories_found.append(path)

                if repositories_found:
                    logger.info(f"📁 Found {len(repositories_found)} repositories")
                    for repo_path in repositories_found:
                        logger.info(f"📊 Analyzing repository: {repo_path}")
                        try:
                            await self._analyze_repository(repo_path)
                        except Exception as e:
                            logger.error(f"Error analyzing {repo_path}: {e}")
                else:
                    logger.debug("No repositories found in common paths")

                # Sleep for a while before checking again
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in standalone mode: {e}")
                await asyncio.sleep(60)


class AIOrganismReplicator:
    """Self-replicating AI organisms for continuous enrichment"""
    
    def __init__(self, max_organisms: int = 100):
        self.organisms = []
        self.max_organisms = max_organisms
        self.question_count = 0
        
    async def spawn_organism(self, initial_query: str, context: Dict):
        """Spawn a new AI organism"""
        if len(self.organisms) >= self.max_organisms:
            # Delete oldest organism
            self.organisms.pop(0)
        
        organism = {
            'id': f"org_{len(self.organisms)}_{datetime.now().timestamp()}",
            'query': initial_query,
            'context': context,
            'questions_asked': 0,
            'answers_received': 0,
            'passes_made': 0,
            'enrichment_data': [],
            'created_at': datetime.now()
        }
        
        self.organisms.append(organism)
        await self._organism_lifecycle(organism)
    
    async def _organism_lifecycle(self, organism: Dict):
        """Manage organism lifecycle: 5x Q/A, 2x passes, then deletion"""
        
        # Phase 1: Ask 5 questions internally
        for i in range(5):
            question = await self._generate_question(organism)
            answer = await self._generate_answer(question, organism['context'])
            
            organism['questions_asked'] += 1
            organism['enrichment_data'].append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
            
            # Brief pause for realism
            await asyncio.sleep(0.1)
        
        # Phase 2: Make 2 passes to other organisms
        for i in range(2):
            await self._make_pass(organism)
            organism['passes_made'] += 1
        
        # Phase 3: Check deletion criteria
        if organism['passes_made'] >= 2 and organism['questions_asked'] >= 5:
            logger.info(f"Organism {organism['id']} completed lifecycle - deleting")
            self.organisms.remove(organism)
    
    async def _generate_question(self, organism: Dict) -> str:
        """Generate internal question for organism"""
        questions = [
            "What optimization could improve QML performance here?",
            "How can we reduce coupling in this code?",
            "What potential bugs might exist in this pattern?",
            "How would this change impact other components?",
            "What tests would be most valuable for this code?"
        ]
        
        return questions[organism['questions_asked'] % len(questions)]
    
    async def _generate_answer(self, question: str, context: Dict) -> str:
        """Generate answer based on context and ML models"""
        # Simplified answer generation
        if "performance" in question.lower():
            return "Consider async loading and property caching optimizations"
        elif "coupling" in question.lower():
            return "Use dependency injection and event-driven architecture"
        elif "bugs" in question.lower():
            return "Null pointer exceptions and race conditions are likely risks"
        elif "impact" in question.lower():
            return "Changes may affect dependent components - run impact analysis"
        elif "tests" in question.lower():
            return "Unit tests for core logic and integration tests for UI components"
        else:
            return "Requires further analysis based on specific context"
    
    async def _make_pass(self, organism: Dict):
        """Pass enrichment data to other organisms"""
        if len(self.organisms) > 1:
            target = np.random.choice([o for o in self.organisms if o['id'] != organism['id']])
            target['enrichment_data'].extend(organism['enrichment_data'])
            logger.debug(f"Organism {organism['id']} passed data to {target['id']}")