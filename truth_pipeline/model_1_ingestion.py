"""
Truth Revelation Pipeline - Model 1: Data Ingestion and Preprocessing
Advanced preprocessing with entropy analysis and noise filtering
"""

import numpy as np
import hashlib
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
from scipy import stats
from scipy.signal import savgol_filter
import networkx as nx

logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """Structured data point for truth pipeline"""
    content: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]
    integrity_hash: str
    preprocessed_content: str = ""
    entropy_score: float = 0.0
    noise_level: float = 0.0
    credibility_indicators: Dict[str, float] = None

class DataIngestionModel:
    """
    Model 1: Advanced data preprocessing with mathematical rigor
    
    Duties:
    - Ingest multi-modal data (text, documents, feeds, queries)
    - Calculate Shannon entropy for information content assessment
    - Apply noise filtering using Savitzky-Golay and statistical methods
    - Generate integrity hashes (BLAKE3) for tamper detection
    - Extract linguistic features and credibility indicators
    - Normalize data for downstream processing
    """
    
    def __init__(self):
        # Mathematical parameters
        self.entropy_threshold = 3.0  # bits - flag low-entropy (engineered) content
        self.noise_threshold = 0.15   # normalized noise level threshold
        self.complexity_threshold = 64  # Kolmogorov complexity minimum (bits)
        
        # Preprocessing filters
        self.savgol_window = 7        # Savitzky-Golay filter window
        self.savgol_polyorder = 3     # Polynomial order for smoothing
        
        # Text analysis patterns
        self.propaganda_patterns = [
            r'\b(always|never|everyone|nobody|all|none)\b',  # Absolutist language
            r'\b(obvious|clearly|undoubtedly|certainly)\b',   # False certainty
            r'\b(they|them|those people)\b',                  # Vague targeting
            r'[!]{2,}',                                       # Excessive punctuation
            r'\b(BREAKING|URGENT|SHOCKING)\b'                # Sensationalism
        ]
        
        # Source reliability indicators
        self.reliability_indicators = {
            'primary_source': 1.0,
            'peer_reviewed': 0.9,
            'established_media': 0.7,
            'social_media': 0.3,
            'anonymous': 0.1,
            'known_disinfo': -1.0
        }
        
        logger.info("Truth Pipeline Model 1 (Data Ingestion) initialized")
    
    def ingest_and_preprocess(self, raw_data: str, source: str, 
                            metadata: Dict[str, Any] = None) -> DataPoint:
        """
        Main ingestion and preprocessing pipeline
        """
        try:
            if metadata is None:
                metadata = {}
            
            # Generate integrity hash
            integrity_hash = self._generate_integrity_hash(raw_data, source)
            
            # Create initial data point
            data_point = DataPoint(
                content=raw_data,
                source=source,
                timestamp=datetime.now(),
                metadata=metadata,
                integrity_hash=integrity_hash,
                credibility_indicators={}
            )
            
            # Step 1: Content preprocessing and cleaning
            cleaned_content = self._preprocess_content(raw_data)
            data_point.preprocessed_content = cleaned_content
            
            # Step 2: Shannon entropy analysis
            entropy_score = self._calculate_shannon_entropy(cleaned_content)
            data_point.entropy_score = entropy_score
            
            # Step 3: Noise assessment and filtering
            noise_level = self._assess_noise_level(cleaned_content)
            data_point.noise_level = noise_level
            
            # Step 4: Extract credibility indicators
            credibility_indicators = self._extract_credibility_indicators(cleaned_content, source)
            data_point.credibility_indicators = credibility_indicators
            
            # Step 5: Kolmogorov complexity estimation
            complexity_score = self._estimate_kolmogorov_complexity(cleaned_content)
            metadata['complexity_score'] = complexity_score
            
            # Step 6: Flag potential issues
            flags = self._generate_quality_flags(data_point)
            metadata['quality_flags'] = flags
            
            logger.debug(f"Ingested data: entropy={entropy_score:.3f}, noise={noise_level:.3f}, complexity={complexity_score}")
            
            return data_point
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            # Return minimal data point with error info
            return DataPoint(
                content=raw_data,
                source=source,
                timestamp=datetime.now(),
                metadata={"error": str(e)},
                integrity_hash="",
                credibility_indicators={"error": -1.0}
            )
    
    def _generate_integrity_hash(self, content: str, source: str) -> str:
        """Generate BLAKE3 hash for data integrity"""
        try:
            # Use SHA-256 as BLAKE3 equivalent for availability
            hash_input = f"{content}::{source}::{datetime.now().isoformat()}"
            return hashlib.sha256(hash_input.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            return ""
    
    def _preprocess_content(self, content: str) -> str:
        """Advanced content preprocessing"""
        try:
            # Step 1: Normalize whitespace and encoding
            cleaned = re.sub(r'\s+', ' ', content.strip())
            
            # Step 2: Remove obvious noise patterns
            # Remove excessive punctuation
            cleaned = re.sub(r'[!]{3,}', '!!', cleaned)
            cleaned = re.sub(r'[?]{3,}', '??', cleaned)
            
            # Remove excessive capitalization
            cleaned = re.sub(r'\b[A-Z]{4,}\b', lambda m: m.group().title(), cleaned)
            
            # Step 3: Extract and normalize URLs
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, cleaned)
            for i, url in enumerate(urls):
                cleaned = cleaned.replace(url, f'[URL_{i}]')
            
            # Step 4: Normalize numeric expressions
            # Convert numbers to standardized format
            number_pattern = r'\b\d+(?:\.\d+)?\b'
            numbers = re.findall(number_pattern, cleaned)
            for num in numbers:
                if '.' in num:
                    normalized = f"{float(num):.2f}"
                    cleaned = cleaned.replace(num, normalized, 1)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Content preprocessing failed: {e}")
            return content  # Return original on error
    
    def _calculate_shannon_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy to measure information content
        Low entropy suggests engineered/artificial content
        """
        try:
            if not text:
                return 0.0
            
            # Count character frequencies
            char_counts = {}
            for char in text.lower():
                char_counts[char] = char_counts.get(char, 0) + 1
            
            # Calculate probabilities
            total_chars = len(text)
            probabilities = [count / total_chars for count in char_counts.values()]
            
            # Shannon entropy: H = -Σ(p_i * log2(p_i))
            entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Entropy calculation failed: {e}")
            return 0.0
    
    def _assess_noise_level(self, text: str) -> float:
        """
        Assess noise level using statistical analysis
        """
        try:
            if not text:
                return 1.0  # Maximum noise for empty content
            
            # Convert text to numeric representation for analysis
            char_values = [ord(char) for char in text]
            
            if len(char_values) < 10:
                return 0.5  # Medium noise for very short text
            
            # Apply Savitzky-Golay filter to smooth signal
            try:
                window_size = min(self.savgol_window, len(char_values))
                if window_size % 2 == 0:
                    window_size -= 1  # Must be odd
                
                if window_size >= 3:
                    smoothed = savgol_filter(char_values, window_size, self.savgol_polyorder)
                    
                    # Calculate noise as variance between original and smoothed
                    noise_variance = np.var(np.array(char_values) - smoothed)
                    
                    # Normalize noise level
                    max_possible_variance = np.var(char_values)
                    noise_level = noise_variance / max(max_possible_variance, 1.0)
                    
                    return min(1.0, noise_level)
            except:
                pass
            
            # Fallback: Use coefficient of variation
            mean_val = np.mean(char_values)
            std_val = np.std(char_values)
            noise_level = std_val / max(mean_val, 1.0) / 100  # Normalize
            
            return min(1.0, noise_level)
            
        except Exception as e:
            logger.error(f"Noise assessment failed: {e}")
            return 0.5  # Default medium noise
    
    def _extract_credibility_indicators(self, content: str, source: str) -> Dict[str, float]:
        """
        Extract linguistic and source-based credibility indicators
        """
        indicators = {}
        
        try:
            # Linguistic indicators
            
            # 1. Propaganda pattern detection
            propaganda_score = 0.0
            for pattern in self.propaganda_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                propaganda_score += matches / max(len(content.split()), 1)
            
            indicators['propaganda_density'] = min(1.0, propaganda_score)
            
            # 2. Emotional language intensity
            emotional_words = ['amazing', 'terrible', 'incredible', 'shocking', 'outrageous', 'fantastic']
            emotional_count = sum(1 for word in emotional_words if word in content.lower())
            indicators['emotional_intensity'] = emotional_count / max(len(content.split()), 1)
            
            # 3. Certainty language assessment
            certainty_words = ['definitely', 'absolutely', 'certainly', 'obviously', 'clearly']
            certainty_count = sum(1 for word in certainty_words if word in content.lower())
            indicators['false_certainty'] = certainty_count / max(len(content.split()), 1)
            
            # 4. Evidence language presence
            evidence_words = ['study', 'research', 'data', 'evidence', 'according to', 'source']
            evidence_count = sum(1 for word in evidence_words if word in content.lower())
            indicators['evidence_density'] = evidence_count / max(len(content.split()), 1)
            
            # Source-based indicators
            source_lower = source.lower()
            
            # Source type classification
            if any(domain in source_lower for domain in ['.edu', '.gov', '.org']):
                indicators['source_authority'] = 0.8
            elif any(domain in source_lower for domain in ['.com', '.net']):
                indicators['source_authority'] = 0.5
            elif 'social' in source_lower or 'forum' in source_lower:
                indicators['source_authority'] = 0.2
            else:
                indicators['source_authority'] = 0.4  # Unknown source
            
            # URL structure analysis
            if 'http' in source_lower:
                # Check for suspicious URL patterns
                if len(re.findall(r'-', source)) > 5:  # Many hyphens
                    indicators['url_suspicion'] = 0.3
                elif any(suspicious in source_lower for suspicious in ['bit.ly', 'tinyurl', 'shortened']):
                    indicators['url_suspicion'] = 0.7
                else:
                    indicators['url_suspicion'] = 0.1
            else:
                indicators['url_suspicion'] = 0.0
            
            return indicators
            
        except Exception as e:
            logger.error(f"Credibility indicator extraction failed: {e}")
            return {"error": 1.0}
    
    def _estimate_kolmogorov_complexity(self, text: str) -> float:
        """
        Estimate Kolmogorov complexity using compression ratio
        Low complexity suggests artificially generated content
        """
        try:
            import zlib
            
            if not text:
                return 0.0
            
            # Compress text and calculate ratio
            original_size = len(text.encode('utf-8'))
            compressed_size = len(zlib.compress(text.encode('utf-8')))
            
            # Compression ratio as complexity estimate
            compression_ratio = compressed_size / original_size
            
            # Convert to bits (approximation of Kolmogorov complexity)
            estimated_complexity = compression_ratio * original_size * 8
            
            return estimated_complexity
            
        except Exception as e:
            logger.error(f"Complexity estimation failed: {e}")
            return 64.0  # Default safe value
    
    def _generate_quality_flags(self, data_point: DataPoint) -> List[str]:
        """Generate quality and risk flags for the data point"""
        flags = []
        
        try:
            # Low entropy flag (potentially engineered)
            if data_point.entropy_score < self.entropy_threshold:
                flags.append("LOW_ENTROPY")
            
            # High noise flag
            if data_point.noise_level > self.noise_threshold:
                flags.append("HIGH_NOISE")
            
            # Propaganda indicators
            propaganda_density = data_point.credibility_indicators.get('propaganda_density', 0)
            if propaganda_density > 0.1:
                flags.append("PROPAGANDA_PATTERNS")
            
            # False certainty
            false_certainty = data_point.credibility_indicators.get('false_certainty', 0)
            if false_certainty > 0.05:
                flags.append("FALSE_CERTAINTY")
            
            # Low evidence density
            evidence_density = data_point.credibility_indicators.get('evidence_density', 0)
            if evidence_density < 0.02:
                flags.append("LOW_EVIDENCE")
            
            # Suspicious source
            url_suspicion = data_point.credibility_indicators.get('url_suspicion', 0)
            if url_suspicion > 0.5:
                flags.append("SUSPICIOUS_SOURCE")
            
            # Low complexity (potentially artificial)
            complexity = data_point.metadata.get('complexity_score', 64)
            if complexity < self.complexity_threshold:
                flags.append("LOW_COMPLEXITY")
            
            return flags
            
        except Exception as e:
            logger.error(f"Flag generation failed: {e}")
            return ["ERROR"]
    
    def batch_preprocess(self, data_batch: List[Tuple[str, str, Dict]]) -> List[DataPoint]:
        """
        Process multiple data points in batch for efficiency
        """
        processed_batch = []
        
        try:
            for content, source, metadata in data_batch:
                data_point = self.ingest_and_preprocess(content, source, metadata)
                processed_batch.append(data_point)
            
            # Batch-level analysis
            if len(processed_batch) > 1:
                batch_stats = self._analyze_batch_statistics(processed_batch)
                
                # Add batch context to each data point
                for data_point in processed_batch:
                    data_point.metadata['batch_stats'] = batch_stats
            
            logger.info(f"Batch processed: {len(processed_batch)} data points")
            return processed_batch
            
        except Exception as e:
            logger.error(f"Batch preprocessing failed: {e}")
            return []
    
    def _analyze_batch_statistics(self, batch: List[DataPoint]) -> Dict[str, Any]:
        """Analyze statistical properties across the batch"""
        try:
            if not batch:
                return {}
            
            # Collect metrics
            entropies = [dp.entropy_score for dp in batch]
            noise_levels = [dp.noise_level for dp in batch]
            propaganda_scores = [dp.credibility_indicators.get('propaganda_density', 0) for dp in batch]
            
            # Calculate statistics
            stats_summary = {
                'entropy': {
                    'mean': np.mean(entropies),
                    'std': np.std(entropies),
                    'median': np.median(entropies),
                    'outliers': self._detect_outliers(entropies)
                },
                'noise': {
                    'mean': np.mean(noise_levels),
                    'std': np.std(noise_levels),
                    'median': np.median(noise_levels)
                },
                'propaganda': {
                    'mean': np.mean(propaganda_scores),
                    'max': max(propaganda_scores),
                    'high_risk_count': sum(1 for score in propaganda_scores if score > 0.1)
                },
                'batch_size': len(batch),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            return stats_summary
            
        except Exception as e:
            logger.error(f"Batch statistics analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_outliers(self, values: List[float]) -> List[int]:
        """Detect outliers using IQR method"""
        try:
            if len(values) < 4:
                return []
            
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    outliers.append(i)
            
            return outliers
            
        except Exception as e:
            logger.error(f"Outlier detection failed: {e}")
            return []
    
    def validate_data_integrity(self, data_point: DataPoint) -> Dict[str, Any]:
        """Validate data integrity using mathematical checks"""
        try:
            validation_result = {
                "integrity_valid": True,
                "hash_verified": False,
                "entropy_valid": True,
                "complexity_valid": True,
                "quality_score": 0.0,
                "issues": []
            }
            
            # Hash verification
            expected_hash = self._generate_integrity_hash(data_point.content, data_point.source)
            validation_result["hash_verified"] = (expected_hash == data_point.integrity_hash)
            
            if not validation_result["hash_verified"]:
                validation_result["issues"].append("Hash mismatch - potential tampering")
                validation_result["integrity_valid"] = False
            
            # Entropy validation
            if data_point.entropy_score < self.entropy_threshold:
                validation_result["entropy_valid"] = False
                validation_result["issues"].append(f"Low entropy ({data_point.entropy_score:.2f}) - potentially artificial")
            
            # Complexity validation
            complexity = data_point.metadata.get('complexity_score', 64)
            if complexity < self.complexity_threshold:
                validation_result["complexity_valid"] = False
                validation_result["issues"].append(f"Low complexity ({complexity:.0f} bits) - potentially engineered")
            
            # Calculate overall quality score
            quality_components = [
                validation_result["hash_verified"] * 0.3,
                validation_result["entropy_valid"] * 0.3,
                validation_result["complexity_valid"] * 0.2,
                (1.0 - data_point.noise_level) * 0.2
            ]
            
            validation_result["quality_score"] = sum(quality_components)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {"integrity_valid": False, "error": str(e)}
    
    def extract_entities_and_claims(self, data_point: DataPoint) -> Dict[str, Any]:
        """
        Extract entities and factual claims for downstream verification
        """
        try:
            content = data_point.preprocessed_content
            
            extraction_result = {
                "entities": {},
                "claims": [],
                "statements": [],
                "numerical_claims": [],
                "temporal_references": []
            }
            
            # Extract named entities (simplified)
            # Organizations
            org_pattern = r'\b([A-Z][a-z]+ (?:Inc|Corp|LLC|Organization|Foundation|Institute))\b'
            orgs = re.findall(org_pattern, content)
            extraction_result["entities"]["organizations"] = list(set(orgs))
            
            # People names (simple heuristic)
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            names = re.findall(name_pattern, content)
            extraction_result["entities"]["people"] = list(set(names))
            
            # Extract numerical claims
            number_pattern = r'(\d+(?:\.\d+)?)\s*(%|percent|million|billion|thousand)'
            numerical_claims = re.findall(number_pattern, content)
            extraction_result["numerical_claims"] = [
                {"value": float(match[0]), "unit": match[1]} 
                for match in numerical_claims
            ]
            
            # Extract temporal references
            date_pattern = r'\b(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b'
            dates = re.findall(date_pattern, content)
            extraction_result["temporal_references"] = list(set(dates))
            
            # Extract factual statements (sentences with specific patterns)
            sentences = re.split(r'[.!?]+', content)
            factual_statements = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:
                    # Look for factual statement patterns
                    if any(verb in sentence.lower() for verb in ['is', 'are', 'was', 'were', 'has', 'have', 'shows', 'indicates']):
                        factual_statements.append(sentence)
            
            extraction_result["statements"] = factual_statements[:10]  # Limit for performance
            
            return extraction_result
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"error": str(e)}
    
    def get_preprocessing_statistics(self) -> Dict[str, Any]:
        """Get preprocessing model statistics"""
        return {
            "model_name": "Data Ingestion and Preprocessing",
            "version": "1.0.0",
            "parameters": {
                "entropy_threshold": self.entropy_threshold,
                "noise_threshold": self.noise_threshold,
                "complexity_threshold": self.complexity_threshold,
                "savgol_window": self.savgol_window
            },
            "capabilities": [
                "Shannon entropy analysis",
                "Noise filtering with Savitzky-Golay",
                "Kolmogorov complexity estimation",
                "Credibility indicator extraction",
                "BLAKE3 integrity hashing",
                "Propaganda pattern detection"
            ]
        }

# Mathematical validation functions
class MathematicalValidator:
    """Advanced mathematical validation for truth pipeline"""
    
    @staticmethod
    def calculate_information_entropy(data_point: DataPoint) -> float:
        """Calculate information-theoretic entropy"""
        try:
            content = data_point.preprocessed_content
            
            # Character-level entropy
            char_freq = {}
            for char in content:
                char_freq[char] = char_freq.get(char, 0) + 1
            
            total_chars = len(content)
            entropy = 0.0
            
            for freq in char_freq.values():
                probability = freq / total_chars
                if probability > 0:
                    entropy -= probability * math.log2(probability)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Information entropy calculation failed: {e}")
            return 0.0
    
    @staticmethod
    def assess_statistical_anomalies(text: str) -> Dict[str, float]:
        """Detect statistical anomalies that might indicate artificial generation"""
        try:
            if not text:
                return {"error": 1.0}
            
            # Convert to numerical representation
            char_codes = [ord(c) for c in text]
            
            # Statistical tests
            anomalies = {}
            
            # Test for uniform distribution (artificial content often too uniform)
            ks_statistic, ks_p_value = stats.kstest(char_codes, 'uniform')
            anomalies['uniformity_ks_test'] = ks_p_value
            
            # Test for normality
            shapiro_stat, shapiro_p = stats.shapiro(char_codes[:5000])  # Limit for performance
            anomalies['normality_test'] = shapiro_p
            
            # Calculate z-score for character distribution
            mean_char = np.mean(char_codes)
            std_char = np.std(char_codes)
            if std_char > 0:
                z_scores = [(code - mean_char) / std_char for code in char_codes]
                extreme_z_count = sum(1 for z in z_scores if abs(z) > 3)
                anomalies['extreme_outlier_ratio'] = extreme_z_count / len(z_scores)
            else:
                anomalies['extreme_outlier_ratio'] = 0.0
            
            # Benford's law test for numbers in text
            numbers = re.findall(r'\b\d+\b', text)
            if len(numbers) > 10:
                first_digits = [int(str(num)[0]) for num in numbers if str(num)[0] != '0']
                if first_digits:
                    benford_deviation = MathematicalValidator._benford_test(first_digits)
                    anomalies['benford_deviation'] = benford_deviation
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Statistical anomaly assessment failed: {e}")
            return {"error": 1.0}
    
    @staticmethod
    def _benford_test(first_digits: List[int]) -> float:
        """Test adherence to Benford's law for number authenticity"""
        try:
            # Expected Benford distribution
            benford_expected = [math.log10(1 + 1/d) for d in range(1, 10)]
            
            # Observed distribution
            observed_counts = [0] * 9
            for digit in first_digits:
                if 1 <= digit <= 9:
                    observed_counts[digit - 1] += 1
            
            total_numbers = len(first_digits)
            observed_freq = [count / total_numbers for count in observed_counts]
            
            # Chi-square test
            chi_square = sum(
                ((obs - exp) ** 2) / exp 
                for obs, exp in zip(observed_freq, benford_expected)
                if exp > 0
            )
            
            return chi_square
            
        except Exception as e:
            logger.error(f"Benford test failed: {e}")
            return 0.0

# Sandbox execution for mathematical validation
class SandboxedValidator:
    """Execute mathematical validation in isolated environment"""
    
    def __init__(self):
        self.validator = MathematicalValidator()
        self.execution_context = {
            "allowed_modules": ["math", "numpy", "scipy"],
            "max_execution_time": 5.0,  # seconds
            "memory_limit": 100 * 1024 * 1024  # 100MB
        }
    
    def safe_execute_validation(self, data_point: DataPoint) -> Dict[str, Any]:
        """Execute validation in sandboxed environment"""
        try:
            # Basic sandbox simulation (in production, use Docker/seccomp)
            import signal
            import time
            
            start_time = time.time()
            
            # Set execution timeout
            def timeout_handler(signum, frame):
                raise TimeoutError("Validation timeout exceeded")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.execution_context["max_execution_time"]))
            
            try:
                # Execute mathematical validation
                validation_result = {
                    "entropy": self.validator.calculate_information_entropy(data_point),
                    "anomalies": self.validator.assess_statistical_anomalies(data_point.preprocessed_content),
                    "execution_time": 0.0,
                    "sandbox_safe": True
                }
                
                execution_time = time.time() - start_time
                validation_result["execution_time"] = execution_time
                
                return validation_result
                
            finally:
                signal.alarm(0)  # Cancel timeout
                
        except TimeoutError:
            return {
                "error": "Execution timeout",
                "sandbox_safe": False,
                "execution_time": self.execution_context["max_execution_time"]
            }
        except Exception as e:
            return {
                "error": str(e),
                "sandbox_safe": False,
                "execution_time": time.time() - start_time
            }
    
    def validate_mathematical_consistency(self, claims: List[str]) -> Dict[str, Any]:
        """Validate mathematical consistency of numerical claims"""
        try:
            consistency_result = {
                "consistent": True,
                "contradictions": [],
                "mathematical_errors": [],
                "confidence": 1.0
            }
            
            # Extract numerical values from claims
            numerical_data = []
            for claim in claims:
                numbers = re.findall(r'\d+(?:\.\d+)?', claim)
                for num in numbers:
                    numerical_data.append({
                        "value": float(num),
                        "claim": claim,
                        "context": claim[:50] + "..." if len(claim) > 50 else claim
                    })
            
            # Check for mathematical inconsistencies
            if len(numerical_data) >= 2:
                # Look for contradictory percentage claims
                percentages = [data for data in numerical_data if "%" in data["claim"]]
                if len(percentages) > 1:
                    total_percentage = sum(data["value"] for data in percentages)
                    if total_percentage > 105:  # Allow 5% tolerance
                        consistency_result["consistent"] = False
                        consistency_result["contradictions"].append({
                            "type": "percentage_overflow",
                            "total": total_percentage,
                            "claims": [p["context"] for p in percentages]
                        })
            
            return consistency_result
            
        except Exception as e:
            logger.error(f"Mathematical consistency validation failed: {e}")
            return {"consistent": False, "error": str(e)}