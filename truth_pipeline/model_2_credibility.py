"""
Truth Revelation Pipeline - Model 2: Source Credibility Assessment
Advanced source analysis using graph networks and probabilistic modeling
"""

import numpy as np
import networkx as nx
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
import math

from .model_1_ingestion import DataPoint

logger = logging.getLogger(__name__)

@dataclass
class SourceProfile:
    """Comprehensive source credibility profile"""
    source_id: str
    domain: str
    source_type: str  # academic, news, social, government, commercial
    credibility_score: float
    bias_indicators: Dict[str, float]
    historical_accuracy: float
    network_centrality: float
    verification_count: int
    last_updated: datetime

class SourceCredibilityModel:
    """
    Model 2: Advanced source credibility assessment
    
    Duties:
    - Evaluate source reputation using probabilistic graph networks
    - Calculate Bayesian credibility scores with historical priors
    - Detect bias patterns and propaganda indicators
    - Assess network centrality and citation relationships
    - Generate confidence intervals for source reliability
    - Cross-reference against known disinformation sources
    """
    
    def __init__(self):
        # Credibility graph network
        self.source_network = nx.DiGraph()
        self.source_profiles = {}
        
        # Bayesian parameters
        self.prior_credibility = 0.5  # Neutral prior
        self.credibility_decay = 0.95  # Temporal decay factor
        self.evidence_weight = 0.7    # Weight of evidence vs prior
        
        # Source classification patterns
        self.domain_patterns = {
            'academic': r'\.(edu|ac\.uk|ac\.au)$',
            'government': r'\.(gov|mil)$',
            'news_major': r'\.(bbc\.com|reuters\.com|apnews\.com|npr\.org)$',
            'news_tabloid': r'\.(dailymail\.|thesun\.|tmz\.)',
            'social_media': r'\.(twitter\.com|facebook\.com|reddit\.com|tiktok\.com)',
            'wiki': r'\.wikipedia\.org$',
            'commercial': r'\.(com|biz)$'
        }
        
        # Bias detection patterns
        self.bias_patterns = {
            'political_left': [r'\b(progressive|liberal|democrat)\b', r'\bconservative.*bad\b'],
            'political_right': [r'\b(conservative|republican|traditional)\b', r'\bliberal.*bad\b'],
            'commercial': [r'\bbuy\b', r'\bpurchase\b', r'\bbest price\b'],
            'sensational': [r'\bSHOCKING\b', r'\bUNBELIEVABLE\b', r'\bYOU WON\'T BELIEVE\b'],
            'conspiracy': [r'\bcover.?up\b', r'\bthey don\'t want you to know\b', r'\bwake up\b']
        }
        
        # Known disinformation source patterns
        self.disinfo_patterns = [
            r'\.rt\.com$',        # Russia Today
            r'\.sputnik',         # Sputnik News
            r'\.infowars\.',      # InfoWars
            r'breitbart',         # Breitbart
            r'fake.*news',        # Generic fake news patterns
        ]
        
        logger.info("Truth Pipeline Model 2 (Source Credibility) initialized")
    
    def assess_source_credibility(self, data_point: DataPoint) -> Dict[str, Any]:
        """
        Comprehensive source credibility assessment
        """
        try:
            source = data_point.source
            content = data_point.preprocessed_content
            
            assessment = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "credibility_score": 0.0,
                "confidence_interval": (0.0, 0.0),
                "bias_analysis": {},
                "risk_factors": [],
                "verification_status": "unverified",
                "network_metrics": {},
                "recommendations": []
            }
            
            # Step 1: Domain-based classification
            domain_analysis = self._classify_source_domain(source)
            assessment["domain_classification"] = domain_analysis
            
            # Step 2: Historical credibility lookup
            historical_credibility = self._get_historical_credibility(source)
            assessment["historical_credibility"] = historical_credibility
            
            # Step 3: Bias pattern detection
            bias_analysis = self._detect_bias_patterns(content)
            assessment["bias_analysis"] = bias_analysis
            
            # Step 4: Disinformation source check
            disinfo_check = self._check_disinformation_sources(source)
            assessment["disinformation_check"] = disinfo_check
            
            # Step 5: Network centrality analysis
            network_metrics = self._analyze_network_position(source)
            assessment["network_metrics"] = network_metrics
            
            # Step 6: Bayesian credibility calculation
            credibility_score, confidence_interval = self._calculate_bayesian_credibility(
                domain_analysis, historical_credibility, bias_analysis, disinfo_check, network_metrics
            )
            
            assessment["credibility_score"] = credibility_score
            assessment["confidence_interval"] = confidence_interval
            
            # Step 7: Generate risk factors and recommendations
            risk_factors = self._identify_risk_factors(assessment)
            assessment["risk_factors"] = risk_factors
            
            recommendations = self._generate_credibility_recommendations(assessment)
            assessment["recommendations"] = recommendations
            
            # Step 8: Update source profile
            self._update_source_profile(source, assessment)
            
            logger.debug(f"Source credibility assessed: {source} -> {credibility_score:.3f}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Source credibility assessment failed: {e}")
            return {"error": str(e), "credibility_score": 0.0}
    
    def _classify_source_domain(self, source: str) -> Dict[str, Any]:
        """Classify source based on domain patterns"""
        try:
            classification = {
                "primary_type": "unknown",
                "secondary_types": [],
                "authority_level": 0.5,
                "institutional_backing": False
            }
            
            source_lower = source.lower()
            
            # Check against domain patterns
            for domain_type, pattern in self.domain_patterns.items():
                if re.search(pattern, source_lower):
                    classification["primary_type"] = domain_type
                    break
            
            # Set authority level based on type
            authority_levels = {
                'academic': 0.9,
                'government': 0.85,
                'news_major': 0.8,
                'wiki': 0.7,
                'commercial': 0.5,
                'news_tabloid': 0.3,
                'social_media': 0.2
            }
            
            classification["authority_level"] = authority_levels.get(
                classification["primary_type"], 0.5
            )
            
            # Check institutional backing
            institutional_indicators = ['.edu', '.gov', '.org', 'university', 'institute']
            classification["institutional_backing"] = any(
                indicator in source_lower for indicator in institutional_indicators
            )
            
            return classification
            
        except Exception as e:
            logger.error(f"Domain classification failed: {e}")
            return {"primary_type": "unknown", "authority_level": 0.5}
    
    def _get_historical_credibility(self, source: str) -> Dict[str, Any]:
        """Retrieve or calculate historical credibility metrics"""
        try:
            source_id = self._normalize_source_id(source)
            
            if source_id in self.source_profiles:
                profile = self.source_profiles[source_id]
                
                # Apply temporal decay to historical accuracy
                days_since_update = (datetime.now() - profile.last_updated).days
                decay_factor = self.credibility_decay ** days_since_update
                
                historical_data = {
                    "exists": True,
                    "accuracy_score": profile.historical_accuracy * decay_factor,
                    "verification_count": profile.verification_count,
                    "last_updated": profile.last_updated.isoformat(),
                    "decay_applied": decay_factor
                }
            else:
                # No historical data - use neutral prior
                historical_data = {
                    "exists": False,
                    "accuracy_score": self.prior_credibility,
                    "verification_count": 0,
                    "last_updated": None,
                    "decay_applied": 1.0
                }
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical credibility lookup failed: {e}")
            return {"exists": False, "accuracy_score": self.prior_credibility}
    
    def _detect_bias_patterns(self, content: str) -> Dict[str, Any]:
        """Detect bias patterns using linguistic analysis"""
        try:
            bias_scores = {}
            total_words = len(content.split())
            
            if total_words == 0:
                return {"error": "Empty content"}
            
            # Check each bias category
            for bias_type, patterns in self.bias_patterns.items():
                matches = 0
                for pattern in patterns:
                    matches += len(re.findall(pattern, content, re.IGNORECASE))
                
                # Normalize by content length
                bias_scores[bias_type] = matches / total_words
            
            # Calculate overall bias intensity
            max_bias = max(bias_scores.values()) if bias_scores else 0.0
            bias_variance = np.var(list(bias_scores.values())) if bias_scores else 0.0
            
            bias_analysis = {
                "bias_scores": bias_scores,
                "max_bias_intensity": max_bias,
                "bias_variance": bias_variance,
                "primary_bias": max(bias_scores.keys(), key=bias_scores.get) if bias_scores else None,
                "overall_bias_level": self._categorize_bias_level(max_bias)
            }
            
            return bias_analysis
            
        except Exception as e:
            logger.error(f"Bias pattern detection failed: {e}")
            return {"error": str(e)}
    
    def _categorize_bias_level(self, bias_intensity: float) -> str:
        """Categorize bias level based on intensity"""
        if bias_intensity >= 0.05:
            return "high"
        elif bias_intensity >= 0.02:
            return "medium"
        elif bias_intensity >= 0.005:
            return "low"
        else:
            return "minimal"
    
    def _check_disinformation_sources(self, source: str) -> Dict[str, Any]:
        """Check against known disinformation source patterns"""
        try:
            source_lower = source.lower()
            
            disinfo_flags = []
            risk_level = 0.0
            
            for pattern in self.disinfo_patterns:
                if re.search(pattern, source_lower):
                    disinfo_flags.append(pattern)
                    risk_level += 0.3  # Cumulative risk
            
            # Additional heuristics
            suspicious_indicators = [
                'fake', 'hoax', 'conspiracy', 'truth', 'patriot', 'resist',
                'awakening', 'expose', 'reveal', 'hidden'
            ]
            
            for indicator in suspicious_indicators:
                if indicator in source_lower:
                    disinfo_flags.append(f"suspicious_keyword_{indicator}")
                    risk_level += 0.1
            
            # Check domain age heuristics (newer domains more suspicious)
            if re.search(r'\.(tk|ml|ga|cf)$', source_lower):  # Free domains
                disinfo_flags.append("free_domain")
                risk_level += 0.2
            
            disinfo_result = {
                "is_flagged": len(disinfo_flags) > 0,
                "risk_level": min(1.0, risk_level),
                "flags": disinfo_flags,
                "confidence": 0.8 if disinfo_flags else 0.9
            }
            
            return disinfo_result
            
        except Exception as e:
            logger.error(f"Disinformation check failed: {e}")
            return {"is_flagged": False, "risk_level": 0.0, "error": str(e)}
    
    def _analyze_network_position(self, source: str) -> Dict[str, Any]:
        """Analyze source position in credibility network"""
        try:
            source_id = self._normalize_source_id(source)
            
            network_metrics = {
                "in_network": False,
                "centrality_scores": {},
                "citation_count": 0,
                "cited_by_count": 0,
                "network_reliability": 0.5
            }
            
            if source_id in self.source_network:
                network_metrics["in_network"] = True
                
                # Calculate centrality measures
                try:
                    # Degree centrality (connections)
                    degree_centrality = nx.degree_centrality(self.source_network)[source_id]
                    
                    # Betweenness centrality (bridge position)
                    betweenness = nx.betweenness_centrality(self.source_network).get(source_id, 0)
                    
                    # PageRank (authority measure)
                    pagerank = nx.pagerank(self.source_network).get(source_id, 0)
                    
                    network_metrics["centrality_scores"] = {
                        "degree": degree_centrality,
                        "betweenness": betweenness,
                        "pagerank": pagerank
                    }
                    
                    # Citation metrics
                    network_metrics["citation_count"] = self.source_network.out_degree(source_id)
                    network_metrics["cited_by_count"] = self.source_network.in_degree(source_id)
                    
                    # Overall network reliability
                    network_metrics["network_reliability"] = (
                        degree_centrality * 0.3 +
                        betweenness * 0.3 +
                        pagerank * 0.4
                    )
                    
                except Exception as e:
                    logger.warning(f"Network centrality calculation failed: {e}")
            
            return network_metrics
            
        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
            return {"in_network": False, "network_reliability": 0.5}
    
    def _calculate_bayesian_credibility(self, domain_analysis: Dict, historical_data: Dict,
                                      bias_analysis: Dict, disinfo_check: Dict,
                                      network_metrics: Dict) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate Bayesian credibility score with confidence intervals
        Uses Bayes' theorem: P(credible|evidence) = P(evidence|credible) * P(credible) / P(evidence)
        """
        try:
            # Prior probability from domain classification
            prior = domain_analysis.get("authority_level", 0.5)
            
            # Likelihood calculations
            likelihoods = []
            
            # Historical accuracy likelihood
            historical_accuracy = historical_data.get("accuracy_score", 0.5)
            likelihoods.append(historical_accuracy)
            
            # Bias likelihood (lower bias = higher credibility)
            max_bias = bias_analysis.get("max_bias_intensity", 0.0)
            bias_likelihood = 1.0 - min(1.0, max_bias * 10)  # Scale bias impact
            likelihoods.append(bias_likelihood)
            
            # Disinformation likelihood (inverse of risk)
            disinfo_risk = disinfo_check.get("risk_level", 0.0)
            disinfo_likelihood = 1.0 - disinfo_risk
            likelihoods.append(disinfo_likelihood)
            
            # Network reliability likelihood
            network_reliability = network_metrics.get("network_reliability", 0.5)
            likelihoods.append(network_reliability)
            
            # Combined likelihood using geometric mean (more conservative)
            combined_likelihood = math.pow(math.prod(likelihoods), 1.0 / len(likelihoods))
            
            # Bayesian update
            # Simplified: posterior ∝ likelihood * prior
            unnormalized_posterior = combined_likelihood * prior
            
            # Normalization (simplified for this context)
            evidence = combined_likelihood * prior + (1 - combined_likelihood) * (1 - prior)
            posterior = unnormalized_posterior / evidence if evidence > 0 else prior
            
            # Calculate confidence interval using beta distribution
            # Model credibility as beta distribution with alpha, beta parameters
            alpha = max(1.0, posterior * 10)  # Pseudo-count for successes
            beta = max(1.0, (1 - posterior) * 10)  # Pseudo-count for failures
            
            # 95% confidence interval
            confidence_low = stats.beta.ppf(0.025, alpha, beta)
            confidence_high = stats.beta.ppf(0.975, alpha, beta)
            
            return posterior, (confidence_low, confidence_high)
            
        except Exception as e:
            logger.error(f"Bayesian credibility calculation failed: {e}")
            return 0.5, (0.0, 1.0)  # Neutral with maximum uncertainty
    
    def _identify_risk_factors(self, assessment: Dict) -> List[Dict[str, Any]]:
        """Identify specific risk factors for the source"""
        risk_factors = []
        
        try:
            # Low credibility risk
            credibility_score = assessment.get("credibility_score", 0.5)
            if credibility_score < 0.3:
                risk_factors.append({
                    "type": "low_credibility",
                    "severity": "high",
                    "value": credibility_score,
                    "description": f"Credibility score ({credibility_score:.2f}) below reliability threshold"
                })
            
            # High bias risk
            bias_analysis = assessment.get("bias_analysis", {})
            max_bias = bias_analysis.get("max_bias_intensity", 0.0)
            if max_bias > 0.03:
                risk_factors.append({
                    "type": "high_bias",
                    "severity": "medium" if max_bias < 0.1 else "high",
                    "value": max_bias,
                    "description": f"High bias intensity detected ({max_bias:.3f})",
                    "bias_type": bias_analysis.get("primary_bias", "unknown")
                })
            
            # Disinformation source risk
            disinfo_check = assessment.get("disinformation_check", {})
            if disinfo_check.get("is_flagged", False):
                risk_factors.append({
                    "type": "disinformation_source",
                    "severity": "critical",
                    "value": disinfo_check.get("risk_level", 1.0),
                    "description": "Source matches known disinformation patterns",
                    "flags": disinfo_check.get("flags", [])
                })
            
            # Wide confidence interval (high uncertainty)
            confidence_interval = assessment.get("confidence_interval", (0.0, 1.0))
            interval_width = confidence_interval[1] - confidence_interval[0]
            if interval_width > 0.5:
                risk_factors.append({
                    "type": "high_uncertainty",
                    "severity": "medium",
                    "value": interval_width,
                    "description": f"Wide confidence interval ({interval_width:.2f}) indicates high uncertainty"
                })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Risk factor identification failed: {e}")
            return [{"type": "analysis_error", "severity": "high", "description": str(e)}]
    
    def _generate_credibility_recommendations(self, assessment: Dict) -> List[str]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        
        try:
            credibility_score = assessment.get("credibility_score", 0.5)
            risk_factors = assessment.get("risk_factors", [])
            
            # Score-based recommendations
            if credibility_score < 0.3:
                recommendations.append("🚨 HIGH RISK: Verify information through multiple independent sources")
                recommendations.append("Consider rejecting claims from this source without additional verification")
            elif credibility_score < 0.6:
                recommendations.append("⚠️ MEDIUM RISK: Cross-reference key claims with reliable sources")
                recommendations.append("Apply additional fact-checking before accepting information")
            else:
                recommendations.append("✅ ACCEPTABLE: Source shows good credibility indicators")
                recommendations.append("Still recommend fact-checking for critical decisions")
            
            # Risk-factor specific recommendations
            for risk_factor in risk_factors:
                risk_type = risk_factor.get("type", "")
                
                if risk_type == "high_bias":
                    recommendations.append("Account for potential bias in interpretation")
                    recommendations.append("Seek sources with opposing viewpoints for balance")
                
                elif risk_type == "disinformation_source":
                    recommendations.append("🛑 CRITICAL: Source flagged as potential disinformation")
                    recommendations.append("Require extraordinary evidence for any claims")
                
                elif risk_type == "high_uncertainty":
                    recommendations.append("Insufficient data for reliable assessment")
                    recommendations.append("Gather more information about source reliability")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Error generating recommendations - proceed with extreme caution"]
    
    def _normalize_source_id(self, source: str) -> str:
        """Normalize source identifier for consistent lookup"""
        try:
            # Extract domain from URL if applicable
            if 'http' in source.lower():
                match = re.search(r'https?://(?:www\.)?([^/]+)', source)
                if match:
                    return match.group(1).lower()
            
            return source.lower().strip()
            
        except Exception as e:
            logger.error(f"Source normalization failed: {e}")
            return source
    
    def _update_source_profile(self, source: str, assessment: Dict):
        """Update source profile with new assessment data"""
        try:
            source_id = self._normalize_source_id(source)
            
            if source_id in self.source_profiles:
                profile = self.source_profiles[source_id]
                
                # Update with weighted average
                new_score = assessment.get("credibility_score", 0.5)
                current_score = profile.historical_accuracy
                verification_count = profile.verification_count
                
                # Weighted update: more verifications = more stable score
                weight = min(0.9, verification_count / (verification_count + 1))
                updated_score = current_score * weight + new_score * (1 - weight)
                
                profile.historical_accuracy = updated_score
                profile.verification_count += 1
                profile.last_updated = datetime.now()
                
            else:
                # Create new profile
                domain_analysis = assessment.get("domain_classification", {})
                
                profile = SourceProfile(
                    source_id=source_id,
                    domain=source,
                    source_type=domain_analysis.get("primary_type", "unknown"),
                    credibility_score=assessment.get("credibility_score", 0.5),
                    bias_indicators=assessment.get("bias_analysis", {}),
                    historical_accuracy=assessment.get("credibility_score", 0.5),
                    network_centrality=0.0,
                    verification_count=1,
                    last_updated=datetime.now()
                )
                
                self.source_profiles[source_id] = profile
                
                # Add to network graph
                self.source_network.add_node(source_id, **{
                    "credibility": profile.credibility_score,
                    "type": profile.source_type,
                    "last_verified": profile.last_updated.isoformat()
                })
            
            logger.debug(f"Updated source profile: {source_id}")
            
        except Exception as e:
            logger.error(f"Source profile update failed: {e}")
    
    def build_credibility_network(self, citation_data: List[Dict]) -> Dict[str, Any]:
        """Build network graph of source citations and references"""
        try:
            network_stats = {
                "nodes_added": 0,
                "edges_added": 0,
                "components": 0,
                "density": 0.0
            }
            
            # Add citation relationships to graph
            for citation in citation_data:
                citing_source = self._normalize_source_id(citation.get("source", ""))
                cited_source = self._normalize_source_id(citation.get("cited_source", ""))
                
                if citing_source and cited_source and citing_source != cited_source:
                    # Add nodes if they don't exist
                    if not self.source_network.has_node(citing_source):
                        self.source_network.add_node(citing_source)
                        network_stats["nodes_added"] += 1
                    
                    if not self.source_network.has_node(cited_source):
                        self.source_network.add_node(cited_source)
                        network_stats["nodes_added"] += 1
                    
                    # Add citation edge
                    citation_weight = citation.get("weight", 1.0)
                    self.source_network.add_edge(citing_source, cited_source, 
                                               weight=citation_weight,
                                               citation_type=citation.get("type", "reference"))
                    network_stats["edges_added"] += 1
            
            # Calculate network statistics
            if self.source_network.number_of_nodes() > 0:
                network_stats["components"] = nx.number_connected_components(
                    self.source_network.to_undirected()
                )
                network_stats["density"] = nx.density(self.source_network)
            
            logger.info(f"Built credibility network: {network_stats}")
            return network_stats
            
        except Exception as e:
            logger.error(f"Network building failed: {e}")
            return {"error": str(e)}
    
    def get_network_recommendations(self, source: str) -> List[str]:
        """Get recommendations based on network analysis"""
        try:
            source_id = self._normalize_source_id(source)
            recommendations = []
            
            if source_id not in self.source_network:
                recommendations.append("Source not in credibility network - limited verification data")
                return recommendations
            
            # Analyze network neighbors
            neighbors = list(self.source_network.neighbors(source_id))
            
            if neighbors:
                # Find highly credible neighbors
                credible_neighbors = []
                for neighbor in neighbors:
                    neighbor_data = self.source_network.nodes.get(neighbor, {})
                    credibility = neighbor_data.get("credibility", 0.5)
                    if credibility > 0.7:
                        credible_neighbors.append(neighbor)
                
                if credible_neighbors:
                    recommendations.append(f"✅ Connected to {len(credible_neighbors)} highly credible sources")
                    recommendations.append("Cross-reference through network connections for verification")
                else:
                    recommendations.append("⚠️ No highly credible sources in immediate network")
                    recommendations.append("Seek independent verification outside source network")
            
            # Centrality-based recommendations
            network_metrics = self._analyze_network_position(source)
            centrality = network_metrics.get("centrality_scores", {})
            
            pagerank = centrality.get("pagerank", 0.0)
            if pagerank > 0.01:  # High authority in network
                recommendations.append("📈 Source has high authority in credibility network")
            elif pagerank < 0.001:  # Low authority
                recommendations.append("📉 Source has low authority in credibility network")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Network recommendation generation failed: {e}")
            return ["Error analyzing network position"]
    
    def export_credibility_database(self) -> Dict[str, Any]:
        """Export credibility database for external analysis"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_sources": len(self.source_profiles),
                "network_size": {
                    "nodes": self.source_network.number_of_nodes(),
                    "edges": self.source_network.number_of_edges()
                },
                "source_profiles": {},
                "network_data": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            # Export source profiles
            for source_id, profile in self.source_profiles.items():
                export_data["source_profiles"][source_id] = {
                    "credibility_score": profile.credibility_score,
                    "source_type": profile.source_type,
                    "verification_count": profile.verification_count,
                    "last_updated": profile.last_updated.isoformat()
                }
            
            # Export network structure
            for node in self.source_network.nodes(data=True):
                export_data["network_data"]["nodes"].append({
                    "id": node[0],
                    "attributes": node[1]
                })
            
            for edge in self.source_network.edges(data=True):
                export_data["network_data"]["edges"].append({
                    "source": edge[0],
                    "target": edge[1],
                    "attributes": edge[2]
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Database export failed: {e}")
            return {"error": str(e)}
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get comprehensive model statistics"""
        try:
            stats = {
                "model_info": {
                    "name": "Source Credibility Assessment",
                    "version": "2.0.0",
                    "initialization_time": datetime.now().isoformat()
                },
                "source_database": {
                    "total_sources": len(self.source_profiles),
                    "verified_sources": sum(1 for p in self.source_profiles.values() 
                                          if p.verification_count > 1),
                    "average_credibility": np.mean([p.credibility_score 
                                                   for p in self.source_profiles.values()]) if self.source_profiles else 0.5
                },
                "network_analysis": {
                    "nodes": self.source_network.number_of_nodes(),
                    "edges": self.source_network.number_of_edges(),
                    "density": nx.density(self.source_network) if self.source_network.number_of_nodes() > 0 else 0.0
                },
                "configuration": {
                    "prior_credibility": self.prior_credibility,
                    "credibility_decay": self.credibility_decay,
                    "evidence_weight": self.evidence_weight
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {e}")
            return {"error": str(e)}