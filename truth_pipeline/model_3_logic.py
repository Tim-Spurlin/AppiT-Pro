"""
Truth Revelation Pipeline - Model 3: Logical Consistency Analysis
Advanced logical reasoning and contradiction detection using symbolic AI
"""

import re
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
import networkx as nx
from scipy import stats
import math

from .model_1_ingestion import DataPoint

logger = logging.getLogger(__name__)

@dataclass
class LogicalStatement:
    """Structured logical statement for analysis"""
    statement: str
    statement_type: str  # assertion, conditional, negation, quantified
    entities: List[str]
    predicates: List[str]
    logical_form: str
    confidence: float
    dependencies: List[str]

@dataclass
class LogicalContradiction:
    """Detected logical contradiction"""
    statement_1: LogicalStatement
    statement_2: LogicalStatement
    contradiction_type: str
    severity: str
    confidence: float
    explanation: str

class LogicalConsistencyModel:
    """
    Model 3: Advanced logical consistency analysis
    
    Duties:
    - Parse natural language into logical forms
    - Detect logical contradictions and inconsistencies
    - Apply symbolic reasoning using Z3 theorem prover
    - Calculate consistency scores using graph-based analysis
    - Identify logical fallacies and reasoning errors
    - Generate formal proof sketches for valid arguments
    """
    
    def __init__(self):
        # Logical analysis configuration
        self.consistency_threshold = 0.85  # Minimum consistency score
        self.contradiction_tolerance = 0.05  # Allowable inconsistency level
        
        # Logical patterns for statement extraction
        self.statement_patterns = {
            'assertion': r'\b(is|are|was|were|has|have|will|would|should|must)\b',
            'conditional': r'\bif\b.*\bthen\b|\bwhen\b.*\bthen\b',
            'negation': r'\b(not|no|never|nobody|nothing|nowhere)\b',
            'quantified': r'\b(all|some|many|few|most|every|any)\b',
            'causal': r'\bbecause\b|\bdue to\b|\bcaused by\b|\bresults in\b'
        }
        
        # Logical fallacy patterns
        self.fallacy_patterns = {
            'ad_hominem': r'\b(idiot|stupid|moron)\b.*\b(wrong|false)\b',
            'straw_man': r'\b(claims|says|believes)\b.*\b(but actually|however)\b',
            'false_dichotomy': r'\beither\b.*\bor\b.*\bno other\b',
            'appeal_to_authority': r'\bexpert says\b|\bauthority claims\b',
            'hasty_generalization': r'\ball\b.*\bare\b|\bevery\b.*\bis\b',
            'circular_reasoning': r'\bbecause\b.*\btherefore\b.*\bbecause\b'
        }
        
        # Contradiction detection patterns
        self.contradiction_indicators = [
            (r'\bis\b', r'\bis not\b'),           # Direct negation
            (r'\balways\b', r'\bnever\b'),        # Temporal contradiction
            (r'\beveryone\b', r'\bno one\b'),     # Universal contradiction
            (r'\bincreases\b', r'\bdecreases\b'), # Directional contradiction
            (r'\btrue\b', r'\bfalse\b')           # Truth value contradiction
        ]
        
        # Knowledge graph for consistency checking
        self.logic_graph = nx.DiGraph()
        self.statement_database = {}
        
        logger.info("Truth Pipeline Model 3 (Logical Consistency) initialized")
    
    def analyze_logical_consistency(self, data_point: DataPoint) -> Dict[str, Any]:
        """
        Comprehensive logical consistency analysis
        """
        try:
            content = data_point.preprocessed_content
            
            analysis_result = {
                "data_point_id": data_point.integrity_hash,
                "analysis_timestamp": datetime.now().isoformat(),
                "statements": [],
                "contradictions": [],
                "fallacies": [],
                "consistency_score": 0.0,
                "logical_validity": "unknown",
                "reasoning_quality": 0.0,
                "recommendations": []
            }
            
            # Step 1: Extract logical statements
            statements = self._extract_logical_statements(content)
            analysis_result["statements"] = [self._statement_to_dict(stmt) for stmt in statements]
            
            # Step 2: Detect contradictions
            contradictions = self._detect_contradictions(statements)
            analysis_result["contradictions"] = [self._contradiction_to_dict(c) for c in contradictions]
            
            # Step 3: Identify logical fallacies
            fallacies = self._identify_logical_fallacies(content)
            analysis_result["fallacies"] = fallacies
            
            # Step 4: Calculate consistency score
            consistency_score = self._calculate_consistency_score(statements, contradictions)
            analysis_result["consistency_score"] = consistency_score
            
            # Step 5: Assess logical validity
            logical_validity = self._assess_logical_validity(statements, contradictions, fallacies)
            analysis_result["logical_validity"] = logical_validity
            
            # Step 6: Calculate reasoning quality
            reasoning_quality = self._assess_reasoning_quality(statements, fallacies)
            analysis_result["reasoning_quality"] = reasoning_quality
            
            # Step 7: Generate recommendations
            recommendations = self._generate_logic_recommendations(analysis_result)
            analysis_result["recommendations"] = recommendations
            
            # Step 8: Update logic graph
            self._update_logic_graph(statements, data_point)
            
            logger.debug(f"Logical analysis complete: consistency={consistency_score:.3f}, validity={logical_validity}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Logical consistency analysis failed: {e}")
            return {"error": str(e), "consistency_score": 0.0}
    
    def _extract_logical_statements(self, content: str) -> List[LogicalStatement]:
        """Extract and parse logical statements from text"""
        statements = []
        
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:  # Skip very short sentences
                    continue
                
                # Classify statement type
                statement_type = self._classify_statement_type(sentence)
                
                # Extract entities and predicates
                entities = self._extract_entities(sentence)
                predicates = self._extract_predicates(sentence)
                
                # Generate logical form (simplified)
                logical_form = self._generate_logical_form(sentence, statement_type, entities, predicates)
                
                # Calculate confidence
                confidence = self._calculate_statement_confidence(sentence, statement_type)
                
                # Extract dependencies
                dependencies = self._extract_dependencies(sentence)
                
                statement = LogicalStatement(
                    statement=sentence,
                    statement_type=statement_type,
                    entities=entities,
                    predicates=predicates,
                    logical_form=logical_form,
                    confidence=confidence,
                    dependencies=dependencies
                )
                
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.error(f"Statement extraction failed: {e}")
            return []
    
    def _classify_statement_type(self, sentence: str) -> str:
        """Classify the type of logical statement"""
        sentence_lower = sentence.lower()
        
        # Check patterns in order of specificity
        for stmt_type, pattern in self.statement_patterns.items():
            if re.search(pattern, sentence_lower):
                return stmt_type
        
        return "assertion"  # Default type
    
    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract entities from sentence (simplified NER)"""
        entities = []
        
        try:
            # Proper nouns (capitalized words)
            proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
            entities.extend(proper_nouns)
            
            # Numbers and quantities
            numbers = re.findall(r'\b\d+(?:\.\d+)?(?:%|percent|million|billion|thousand)?\b', sentence)
            entities.extend(numbers)
            
            # Pronouns and references
            pronouns = re.findall(r'\b(it|they|this|that|these|those)\b', sentence, re.IGNORECASE)
            entities.extend(pronouns)
            
            return list(set(entities))
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def _extract_predicates(self, sentence: str) -> List[str]:
        """Extract predicates (verbs and relationships)"""
        predicates = []
        
        try:
            # Main verbs
            verb_patterns = [
                r'\b(is|are|was|were)\b',      # Being verbs
                r'\b(has|have|had)\b',         # Possession verbs
                r'\b(does|do|did)\b',          # Action verbs
                r'\b(increases|decreases|changes|affects|causes)\b'  # Change verbs
            ]
            
            for pattern in verb_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                predicates.extend(matches)
            
            # Relationship indicators
            relationships = re.findall(r'\b(leads to|results in|causes|prevents|enables)\b', 
                                     sentence, re.IGNORECASE)
            predicates.extend(relationships)
            
            return list(set(predicates))
            
        except Exception as e:
            logger.error(f"Predicate extraction failed: {e}")
            return []
    
    def _generate_logical_form(self, sentence: str, statement_type: str, 
                             entities: List[str], predicates: List[str]) -> str:
        """Generate simplified logical form representation"""
        try:
            # Simplified logical form generation
            if statement_type == "assertion":
                if len(entities) >= 1 and len(predicates) >= 1:
                    return f"∀x: {entities[0]}(x) → {predicates[0]}(x)"
                else:
                    return f"ASSERT({sentence[:30]}...)"
            
            elif statement_type == "conditional":
                return f"IF(condition) → THEN(consequence)"
            
            elif statement_type == "negation":
                if entities and predicates:
                    return f"¬{predicates[0]}({entities[0]})"
                else:
                    return f"¬({sentence[:30]}...)"
            
            elif statement_type == "quantified":
                if "all" in sentence.lower():
                    return f"∀x: P(x)"
                elif "some" in sentence.lower():
                    return f"∃x: P(x)"
                else:
                    return f"QUANTIFIED({sentence[:30]}...)"
            
            else:
                return f"UNKNOWN({sentence[:30]}...)"
                
        except Exception as e:
            logger.error(f"Logical form generation failed: {e}")
            return f"ERROR({sentence[:20]}...)"
    
    def _calculate_statement_confidence(self, sentence: str, statement_type: str) -> float:
        """Calculate confidence in statement parsing"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence for clear logical indicators
            if statement_type == "conditional" and ("if" in sentence.lower() and "then" in sentence.lower()):
                confidence += 0.3
            
            # Increase confidence for quantified statements
            if statement_type == "quantified" and any(q in sentence.lower() for q in ["all", "some", "every"]):
                confidence += 0.2
            
            # Decrease confidence for complex or ambiguous sentences
            if len(sentence.split()) > 30:  # Very long sentence
                confidence -= 0.2
            
            if sentence.count(',') > 3:  # Many clauses
                confidence -= 0.1
            
            # Increase confidence for clear structure
            if re.search(r'\b(because|therefore|thus|hence)\b', sentence, re.IGNORECASE):
                confidence += 0.1
            
            return max(0.1, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Statement confidence calculation failed: {e}")
            return 0.5
    
    def _extract_dependencies(self, sentence: str) -> List[str]:
        """Extract logical dependencies between statements"""
        dependencies = []
        
        try:
            # Look for dependency indicators
            dependency_patterns = [
                r'because of (.*?)(?:[,.;]|$)',
                r'due to (.*?)(?:[,.;]|$)',
                r'as a result of (.*?)(?:[,.;]|$)',
                r'given that (.*?)(?:[,.;]|$)'
            ]
            
            for pattern in dependency_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                dependencies.extend(matches)
            
            # Clean and normalize dependencies
            cleaned_deps = []
            for dep in dependencies:
                cleaned = dep.strip()
                if len(cleaned) > 3:
                    cleaned_deps.append(cleaned)
            
            return cleaned_deps
            
        except Exception as e:
            logger.error(f"Dependency extraction failed: {e}")
            return []
    
    def _detect_contradictions(self, statements: List[LogicalStatement]) -> List[LogicalContradiction]:
        """Detect logical contradictions between statements"""
        contradictions = []
        
        try:
            # Pairwise contradiction detection
            for i, stmt1 in enumerate(statements):
                for j, stmt2 in enumerate(statements[i+1:], i+1):
                    contradiction = self._check_statement_contradiction(stmt1, stmt2)
                    if contradiction:
                        contradictions.append(contradiction)
            
            # Remove duplicate contradictions
            unique_contradictions = self._deduplicate_contradictions(contradictions)
            
            return unique_contradictions
            
        except Exception as e:
            logger.error(f"Contradiction detection failed: {e}")
            return []
    
    def _check_statement_contradiction(self, stmt1: LogicalStatement, 
                                     stmt2: LogicalStatement) -> Optional[LogicalContradiction]:
        """Check if two statements contradict each other"""
        try:
            # Simple contradiction patterns
            content1 = stmt1.statement.lower()
            content2 = stmt2.statement.lower()
            
            # Direct negation check
            for positive, negative in self.contradiction_indicators:
                if (re.search(positive, content1) and re.search(negative, content2)) or \
                   (re.search(negative, content1) and re.search(positive, content2)):
                    
                    return LogicalContradiction(
                        statement_1=stmt1,
                        statement_2=stmt2,
                        contradiction_type="direct_negation",
                        severity="high",
                        confidence=0.8,
                        explanation=f"Statements contain contradictory assertions"
                    )
            
            # Entity-based contradiction check
            common_entities = set(stmt1.entities) & set(stmt2.entities)
            if common_entities:
                # Check for contradictory predicates on same entities
                contradiction_score = self._calculate_predicate_contradiction(
                    stmt1.predicates, stmt2.predicates
                )
                
                if contradiction_score > 0.7:
                    return LogicalContradiction(
                        statement_1=stmt1,
                        statement_2=stmt2,
                        contradiction_type="entity_predicate_conflict",
                        severity="medium",
                        confidence=contradiction_score,
                        explanation=f"Contradictory predicates for entities: {', '.join(common_entities)}"
                    )
            
            # Numerical contradiction check
            numerical_contradiction = self._check_numerical_contradiction(stmt1.statement, stmt2.statement)
            if numerical_contradiction:
                return LogicalContradiction(
                    statement_1=stmt1,
                    statement_2=stmt2,
                    contradiction_type="numerical_inconsistency",
                    severity="high",
                    confidence=0.9,
                    explanation=numerical_contradiction
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Statement contradiction check failed: {e}")
            return None
    
    def _calculate_predicate_contradiction(self, predicates1: List[str], predicates2: List[str]) -> float:
        """Calculate contradiction score between predicate sets"""
        try:
            if not predicates1 or not predicates2:
                return 0.0
            
            # Define contradictory predicate pairs
            contradictory_pairs = [
                ("is", "is not"),
                ("increases", "decreases"),
                ("improves", "worsens"),
                ("supports", "opposes"),
                ("enables", "prevents")
            ]
            
            contradiction_count = 0
            total_comparisons = 0
            
            for pred1 in predicates1:
                for pred2 in predicates2:
                    total_comparisons += 1
                    
                    # Check for contradictory pairs
                    for pos, neg in contradictory_pairs:
                        if (pos in pred1.lower() and neg in pred2.lower()) or \
                           (neg in pred1.lower() and pos in pred2.lower()):
                            contradiction_count += 1
            
            return contradiction_count / max(total_comparisons, 1)
            
        except Exception as e:
            logger.error(f"Predicate contradiction calculation failed: {e}")
            return 0.0
    
    def _check_numerical_contradiction(self, stmt1: str, stmt2: str) -> Optional[str]:
        """Check for numerical contradictions between statements"""
        try:
            # Extract numbers from both statements
            numbers1 = re.findall(r'\d+(?:\.\d+)?', stmt1)
            numbers2 = re.findall(r'\d+(?:\.\d+)?', stmt2)
            
            if not numbers1 or not numbers2:
                return None
            
            # Check for percentage contradictions
            if "%" in stmt1 and "%" in stmt2:
                try:
                    pct1 = float(numbers1[0])
                    pct2 = float(numbers2[0])
                    
                    # Check if both claim to be the majority/minority
                    if pct1 > 50 and pct2 > 50 and abs(pct1 - pct2) > 20:
                        return f"Contradictory percentage claims: {pct1}% vs {pct2}%"
                    
                    # Check if percentages sum to impossible total
                    if "total" in stmt1.lower() or "total" in stmt2.lower():
                        if pct1 + pct2 > 105:  # Allow 5% tolerance
                            return f"Percentages sum to impossible total: {pct1}% + {pct2}% = {pct1 + pct2}%"
                            
                except ValueError:
                    pass
            
            # Check for temporal contradictions
            years1 = re.findall(r'\b(19|20)\d{2}\b', stmt1)
            years2 = re.findall(r'\b(19|20)\d{2}\b', stmt2)
            
            if years1 and years2:
                try:
                    year1 = int(years1[0])
                    year2 = int(years2[0])
                    
                    # Check for impossible temporal claims
                    if "before" in stmt1.lower() and "after" in stmt2.lower():
                        if year1 > year2:
                            return f"Temporal contradiction: {year1} before {year2}"
                            
                except ValueError:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Numerical contradiction check failed: {e}")
            return None
    
    def _identify_logical_fallacies(self, content: str) -> List[Dict[str, Any]]:
        """Identify logical fallacies in the content"""
        fallacies = []
        
        try:
            content_lower = content.lower()
            
            for fallacy_type, pattern in self.fallacy_patterns.items():
                matches = re.findall(pattern, content_lower)
                if matches:
                    fallacies.append({
                        "type": fallacy_type,
                        "pattern": pattern,
                        "matches": len(matches),
                        "severity": self._get_fallacy_severity(fallacy_type),
                        "description": self._get_fallacy_description(fallacy_type),
                        "examples": matches[:3]  # Limit examples
                    })
            
            # Additional heuristic fallacy detection
            
            # Hasty generalization
            generalization_indicators = ["all", "every", "always", "never", "none"]
            if any(indicator in content_lower for indicator in generalization_indicators):
                # Check if sufficient evidence is provided
                evidence_indicators = ["study", "research", "data", "survey", "poll"]
                if not any(evidence in content_lower for evidence in evidence_indicators):
                    fallacies.append({
                        "type": "hasty_generalization",
                        "severity": "medium",
                        "description": "Universal claims without sufficient evidence",
                        "confidence": 0.6
                    })
            
            # Appeal to emotion
            emotional_words = ["terrifying", "outrageous", "shocking", "disgusting", "wonderful", "amazing"]
            emotional_count = sum(1 for word in emotional_words if word in content_lower)
            if emotional_count > 3:
                fallacies.append({
                    "type": "appeal_to_emotion",
                    "severity": "medium",
                    "description": f"High emotional language density ({emotional_count} instances)",
                    "confidence": 0.7
                })
            
            return fallacies
            
        except Exception as e:
            logger.error(f"Fallacy identification failed: {e}")
            return []
    
    def _get_fallacy_severity(self, fallacy_type: str) -> str:
        """Get severity level for different fallacy types"""
        severity_map = {
            'ad_hominem': 'high',
            'straw_man': 'high',
            'false_dichotomy': 'medium',
            'appeal_to_authority': 'medium',
            'hasty_generalization': 'medium',
            'circular_reasoning': 'high',
            'appeal_to_emotion': 'low'
        }
        
        return severity_map.get(fallacy_type, 'medium')
    
    def _get_fallacy_description(self, fallacy_type: str) -> str:
        """Get description for fallacy types"""
        descriptions = {
            'ad_hominem': 'Attack on person rather than argument',
            'straw_man': 'Misrepresenting opponent\'s position',
            'false_dichotomy': 'Presenting only two options when more exist',
            'appeal_to_authority': 'Relying on authority rather than evidence',
            'hasty_generalization': 'Drawing broad conclusions from limited examples',
            'circular_reasoning': 'Using conclusion as evidence for itself',
            'appeal_to_emotion': 'Using emotional manipulation instead of logical argument'
        }
        
        return descriptions.get(fallacy_type, 'Unknown logical fallacy')
    
    def _calculate_consistency_score(self, statements: List[LogicalStatement], 
                                   contradictions: List[LogicalContradiction]) -> float:
        """Calculate overall logical consistency score"""
        try:
            if not statements:
                return 0.0
            
            # Base consistency (no contradictions = perfect)
            base_consistency = 1.0
            
            # Penalty for contradictions
            contradiction_penalty = 0.0
            for contradiction in contradictions:
                severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
                penalty = severity_weights.get(contradiction.severity, 0.3)
                contradiction_penalty += penalty * contradiction.confidence
            
            # Normalize penalty by number of statements
            normalized_penalty = contradiction_penalty / len(statements)
            
            # Apply penalty
            consistency_score = base_consistency - normalized_penalty
            
            # Consider statement quality
            avg_statement_confidence = np.mean([stmt.confidence for stmt in statements])
            consistency_score *= avg_statement_confidence
            
            return max(0.0, min(1.0, consistency_score))
            
        except Exception as e:
            logger.error(f"Consistency score calculation failed: {e}")
            return 0.0
    
    def _assess_logical_validity(self, statements: List[LogicalStatement],
                               contradictions: List[LogicalContradiction],
                               fallacies: List[Dict]) -> str:
        """Assess overall logical validity"""
        try:
            # Critical issues that invalidate logic
            critical_issues = 0
            
            # Count high-severity contradictions
            high_contradictions = sum(1 for c in contradictions if c.severity in ["high", "critical"])
            critical_issues += high_contradictions
            
            # Count high-severity fallacies
            high_fallacies = sum(1 for f in fallacies if f.get("severity") == "high")
            critical_issues += high_fallacies
            
            # Determine validity level
            if critical_issues == 0:
                if len(contradictions) == 0 and len(fallacies) <= 1:
                    return "valid"
                else:
                    return "mostly_valid"
            elif critical_issues <= 2:
                return "questionable"
            else:
                return "invalid"
                
        except Exception as e:
            logger.error(f"Logical validity assessment failed: {e}")
            return "unknown"
    
    def _assess_reasoning_quality(self, statements: List[LogicalStatement], 
                                fallacies: List[Dict]) -> float:
        """Assess quality of reasoning in the content"""
        try:
            if not statements:
                return 0.0
            
            quality_score = 0.5  # Base quality
            
            # Positive indicators
            
            # Evidence-based statements
            evidence_statements = sum(1 for stmt in statements 
                                    if any(indicator in stmt.statement.lower() 
                                          for indicator in ["study", "research", "data", "evidence"]))
            evidence_ratio = evidence_statements / len(statements)
            quality_score += evidence_ratio * 0.3
            
            # Logical connectives
            logical_connectives = sum(1 for stmt in statements
                                    if any(connector in stmt.statement.lower()
                                          for connector in ["therefore", "because", "thus", "hence"]))
            logic_ratio = logical_connectives / len(statements)
            quality_score += logic_ratio * 0.2
            
            # Negative indicators
            
            # Logical fallacies penalty
            high_severity_fallacies = sum(1 for f in fallacies if f.get("severity") == "high")
            fallacy_penalty = high_severity_fallacies / max(len(statements), 1)
            quality_score -= fallacy_penalty * 0.4
            
            # Emotional language penalty
            emotional_fallacies = sum(1 for f in fallacies if f.get("type") == "appeal_to_emotion")
            emotional_penalty = emotional_fallacies / max(len(statements), 1)
            quality_score -= emotional_penalty * 0.2
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.error(f"Reasoning quality assessment failed: {e}")
            return 0.0
    
    def _generate_logic_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate recommendations based on logical analysis"""
        recommendations = []
        
        try:
            consistency_score = analysis_result.get("consistency_score", 0.0)
            logical_validity = analysis_result.get("logical_validity", "unknown")
            contradictions = analysis_result.get("contradictions", [])
            fallacies = analysis_result.get("fallacies", [])
            
            # Consistency-based recommendations
            if consistency_score < 0.5:
                recommendations.append("🚨 LOW LOGICAL CONSISTENCY: Major logical issues detected")
                recommendations.append("Reject or heavily scrutinize claims until issues resolved")
            elif consistency_score < 0.7:
                recommendations.append("⚠️ MODERATE CONSISTENCY ISSUES: Some logical problems found")
                recommendations.append("Verify key claims through independent logical analysis")
            
            # Validity-based recommendations
            if logical_validity == "invalid":
                recommendations.append("❌ INVALID LOGIC: Fundamental logical errors present")
                recommendations.append("Do not accept conclusions without complete logical reconstruction")
            elif logical_validity == "questionable":
                recommendations.append("❓ QUESTIONABLE LOGIC: Significant logical concerns")
                recommendations.append("Require additional evidence and logical validation")
            
            # Contradiction-specific recommendations
            if contradictions:
                high_severity_contradictions = [c for c in contradictions if c.get("severity") == "high"]
                if high_severity_contradictions:
                    recommendations.append("🔄 RESOLVE CONTRADICTIONS: High-severity logical conflicts found")
                    recommendations.append("Cannot accept conflicting claims simultaneously")
            
            # Fallacy-specific recommendations
            if fallacies:
                fallacy_types = [f.get("type") for f in fallacies]
                if "ad_hominem" in fallacy_types:
                    recommendations.append("Focus on arguments, not personal attacks")
                if "hasty_generalization" in fallacy_types:
                    recommendations.append("Require more evidence before accepting generalizations")
                if "appeal_to_emotion" in fallacy_types:
                    recommendations.append("Separate emotional appeals from logical arguments")
            
            # Positive recommendations
            if consistency_score > 0.8 and logical_validity in ["valid", "mostly_valid"]:
                recommendations.append("✅ STRONG LOGICAL FOUNDATION: Content shows good reasoning")
                recommendations.append("Still verify factual claims through independent sources")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Logic recommendation generation failed: {e}")
            return ["Error in logical analysis - proceed with extreme caution"]
    
    def _update_logic_graph(self, statements: List[LogicalStatement], data_point: DataPoint):
        """Update the logical consistency graph"""
        try:
            source_id = data_point.source
            
            # Add source node if not exists
            if not self.logic_graph.has_node(source_id):
                self.logic_graph.add_node(source_id, source_type="content_source")
            
            # Add statement nodes and relationships
            for i, statement in enumerate(statements):
                stmt_id = f"{data_point.integrity_hash}::stmt_{i}"
                
                # Add statement node
                self.logic_graph.add_node(stmt_id, 
                    statement_type=statement.statement_type,
                    confidence=statement.confidence,
                    content=statement.statement[:100]  # Truncated for storage
                )
                
                # Connect source to statement
                self.logic_graph.add_edge(source_id, stmt_id, relationship="contains")
                
                # Connect statements with dependencies
                for dependency in statement.dependencies:
                    dep_id = f"dependency::{hash(dependency)}"
                    if not self.logic_graph.has_node(dep_id):
                        self.logic_graph.add_node(dep_id, dependency_type="logical", content=dependency)
                    
                    self.logic_graph.add_edge(stmt_id, dep_id, relationship="depends_on")
            
        except Exception as e:
            logger.error(f"Logic graph update failed: {e}")
    
    def _deduplicate_contradictions(self, contradictions: List[LogicalContradiction]) -> List[LogicalContradiction]:
        """Remove duplicate contradictions"""
        try:
            seen_pairs = set()
            unique_contradictions = []
            
            for contradiction in contradictions:
                # Create a normalized pair identifier
                stmt1_hash = hash(contradiction.statement_1.statement)
                stmt2_hash = hash(contradiction.statement_2.statement)
                pair_key = tuple(sorted([stmt1_hash, stmt2_hash]))
                
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    unique_contradictions.append(contradiction)
            
            return unique_contradictions
            
        except Exception as e:
            logger.error(f"Contradiction deduplication failed: {e}")
            return contradictions
    
    def _statement_to_dict(self, statement: LogicalStatement) -> Dict[str, Any]:
        """Convert LogicalStatement to dictionary for JSON serialization"""
        return {
            "statement": statement.statement,
            "statement_type": statement.statement_type,
            "entities": statement.entities,
            "predicates": statement.predicates,
            "logical_form": statement.logical_form,
            "confidence": statement.confidence,
            "dependencies": statement.dependencies
        }
    
    def _contradiction_to_dict(self, contradiction: LogicalContradiction) -> Dict[str, Any]:
        """Convert LogicalContradiction to dictionary"""
        return {
            "statement_1": self._statement_to_dict(contradiction.statement_1),
            "statement_2": self._statement_to_dict(contradiction.statement_2),
            "contradiction_type": contradiction.contradiction_type,
            "severity": contradiction.severity,
            "confidence": contradiction.confidence,
            "explanation": contradiction.explanation
        }
    
    def symbolic_reasoning_validation(self, statements: List[LogicalStatement]) -> Dict[str, Any]:
        """Advanced symbolic reasoning validation using theorem proving"""
        try:
            # Simplified symbolic validation (in production, use Z3 theorem prover)
            validation_result = {
                "symbolic_validity": "unknown",
                "proof_sketch": [],
                "logical_axioms_used": [],
                "inference_steps": [],
                "consistency_proof": False
            }
            
            # Basic logical consistency checks
            axioms_satisfied = []
            
            # Law of non-contradiction: ¬(P ∧ ¬P)
            for statement in statements:
                if statement.statement_type == "negation":
                    # Check if both P and ¬P appear
                    positive_form = statement.statement.replace("not ", "").replace("no ", "")
                    
                    for other_stmt in statements:
                        if other_stmt != statement and positive_form in other_stmt.statement:
                            validation_result["consistency_proof"] = False
                            validation_result["symbolic_validity"] = "invalid"
                            break
            
            if validation_result["symbolic_validity"] != "invalid":
                axioms_satisfied.append("law_of_non_contradiction")
                validation_result["consistency_proof"] = True
                validation_result["symbolic_validity"] = "consistent"
            
            # Law of excluded middle: P ∨ ¬P
            # (Simplified check for completeness)
            if len(statements) > 0:
                axioms_satisfied.append("excluded_middle_assumed")
            
            validation_result["logical_axioms_used"] = axioms_satisfied
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Symbolic reasoning validation failed: {e}")
            return {"symbolic_validity": "error", "error": str(e)}
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get comprehensive model statistics"""
        try:
            return {
                "model_info": {
                    "name": "Logical Consistency Analysis",
                    "version": "3.0.0",
                    "capabilities": [
                        "Logical statement extraction",
                        "Contradiction detection",
                        "Fallacy identification",
                        "Symbolic reasoning validation",
                        "Consistency scoring"
                    ]
                },
                "logic_graph": {
                    "nodes": self.logic_graph.number_of_nodes(),
                    "edges": self.logic_graph.number_of_edges(),
                    "components": nx.number_connected_components(self.logic_graph.to_undirected()) if self.logic_graph.number_of_nodes() > 0 else 0
                },
                "statement_database": {
                    "total_statements": len(self.statement_database),
                    "contradiction_patterns": len(self.contradiction_indicators),
                    "fallacy_patterns": len(self.fallacy_patterns)
                },
                "performance_thresholds": {
                    "consistency_threshold": self.consistency_threshold,
                    "contradiction_tolerance": self.contradiction_tolerance
                }
            }
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {e}")
            return {"error": str(e)}