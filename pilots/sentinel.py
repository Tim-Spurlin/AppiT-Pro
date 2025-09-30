"""
Pilot 0.0: Sentinel - Pre-zero over-analyzer
Prevents repetition, detects regressions, maintains vigilance
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import difflib

logger = logging.getLogger(__name__)

class SentinelPilot:
    """
    Sentinel: The vigilant guardian against mistakes and repetition
    
    Responsibilities:
    - Record every event with precise timestamps
    - Detect repetition patterns and prevent redundant work
    - Analyze mistakes and learn from errors
    - Maintain consistency across all operations
    - Pre-validate all actions before execution
    """
    
    def __init__(self, memory_path: str = "~/.local/share/haasp/sentinel"):
        self.memory_path = Path(memory_path).expanduser()
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Event storage
        self.events_db = self.memory_path / "events.db"
        self.mistakes_db = self.memory_path / "mistakes.db"
        
        # State tracking
        self.active_sessions = {}
        self.content_hashes = set()
        self.pattern_cache = {}
        
        # Configuration
        self.config = {
            "repetition_threshold": 0.85,  # Similarity threshold for repetition
            "mistake_memory_days": 30,     # How long to remember mistakes
            "event_retention_days": 90,    # Event log retention
            "max_session_duration": 3600,  # Max session time (1 hour)
            "consistency_checks": True,
            "learn_from_errors": True
        }
        
        self.init_databases()
        logger.info("Sentinel Pilot initialized - vigilance activated")
    
    def init_databases(self):
        """Initialize event and mistake tracking databases"""
        # Events database
        conn = sqlite3.connect(self.events_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                content_hash TEXT,
                pilot_id TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                risk_level TEXT DEFAULT 'low',
                validated BOOLEAN DEFAULT 0
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                pilot_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                event_count INTEGER DEFAULT 0,
                mistake_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Mistakes database
        conn = sqlite3.connect(self.mistakes_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mistake_type TEXT NOT NULL,
                content_hash TEXT,
                error_message TEXT,
                stack_trace TEXT,
                context JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                frequency INTEGER DEFAULT 1,
                last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolution TEXT,
                prevention_strategy TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE,
                pattern_description TEXT,
                occurrence_count INTEGER DEFAULT 1,
                risk_score REAL DEFAULT 0.0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def validate_action(self, action_type: str, content: str, 
                            pilot_id: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Pre-validate any action before execution
        Returns validation result with risk assessment
        """
        try:
            validation_start = datetime.now()
            
            # Generate content hash for repetition detection
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            validation_result = {
                "action_type": action_type,
                "content_hash": content_hash,
                "pilot_id": pilot_id,
                "timestamp": validation_start.isoformat(),
                "validated": False,
                "risk_level": "unknown",
                "issues": [],
                "recommendations": []
            }
            
            # Check 1: Repetition detection
            repetition_check = await self._check_repetition(content_hash, content, action_type)
            if repetition_check["is_repetition"]:
                validation_result["issues"].append({
                    "type": "repetition",
                    "severity": "medium",
                    "message": f"Similar action detected {repetition_check['similarity']:.2%} match",
                    "previous_occurrence": repetition_check["previous_timestamp"]
                })
            
            # Check 2: Historical mistakes
            mistake_check = await self._check_historical_mistakes(content_hash, action_type)
            if mistake_check["has_failed_before"]:
                validation_result["issues"].append({
                    "type": "historical_failure",
                    "severity": "high", 
                    "message": f"Similar action failed {mistake_check['failure_count']} times",
                    "last_failure": mistake_check["last_failure"],
                    "prevention_strategy": mistake_check["prevention_strategy"]
                })
            
            # Check 3: Consistency validation
            consistency_check = await self._check_consistency(action_type, content, metadata)
            if not consistency_check["consistent"]:
                validation_result["issues"].append({
                    "type": "consistency",
                    "severity": "medium",
                    "message": consistency_check["message"],
                    "conflicts": consistency_check["conflicts"]
                })
            
            # Check 4: Risk assessment
            risk_assessment = await self._assess_risk(action_type, content, pilot_id)
            validation_result["risk_level"] = risk_assessment["level"]
            validation_result["risk_factors"] = risk_assessment["factors"]
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(validation_result)
            validation_result["recommendations"] = recommendations
            
            # Final validation decision
            severe_issues = [issue for issue in validation_result["issues"] 
                           if issue["severity"] in ["high", "critical"]]
            
            validation_result["validated"] = len(severe_issues) == 0
            validation_result["validation_time_ms"] = (datetime.now() - validation_start).total_seconds() * 1000
            
            # Record validation event
            await self._record_event("validation", validation_result, pilot_id)
            
            logger.debug(f"Validation complete: {action_type} - {'✅ APPROVED' if validation_result['validated'] else '❌ BLOCKED'}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "validated": False,
                "error": str(e),
                "risk_level": "critical"
            }
    
    async def _check_repetition(self, content_hash: str, content: str, action_type: str) -> Dict[str, Any]:
        """Check for repetitive actions"""
        try:
            conn = sqlite3.connect(self.events_db)
            
            # Look for similar content in recent events
            cursor = conn.execute("""
                SELECT content_hash, metadata, timestamp
                FROM events 
                WHERE event_type = ? AND timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 100
            """, (action_type,))
            
            similar_events = []
            for row in cursor.fetchall():
                stored_hash, metadata_json, timestamp = row
                
                if stored_hash == content_hash:
                    # Exact match
                    conn.close()
                    return {
                        "is_repetition": True,
                        "similarity": 1.0,
                        "previous_timestamp": timestamp,
                        "match_type": "exact"
                    }
                
                # Check content similarity for near-duplicates
                try:
                    stored_metadata = json.loads(metadata_json) if metadata_json else {}
                    stored_content = stored_metadata.get("content_preview", "")
                    
                    if stored_content:
                        similarity = self._calculate_similarity(content, stored_content)
                        if similarity >= self.config["repetition_threshold"]:
                            similar_events.append({
                                "similarity": similarity,
                                "timestamp": timestamp,
                                "hash": stored_hash
                            })
                            
                except Exception:
                    continue
            
            conn.close()
            
            if similar_events:
                best_match = max(similar_events, key=lambda x: x["similarity"])
                return {
                    "is_repetition": True,
                    "similarity": best_match["similarity"],
                    "previous_timestamp": best_match["timestamp"],
                    "match_type": "similar"
                }
            
            return {"is_repetition": False}
            
        except Exception as e:
            logger.error(f"Repetition check failed: {e}")
            return {"is_repetition": False, "error": str(e)}
    
    async def _check_historical_mistakes(self, content_hash: str, action_type: str) -> Dict[str, Any]:
        """Check if similar actions have failed before"""
        try:
            conn = sqlite3.connect(self.mistakes_db)
            
            cursor = conn.execute("""
                SELECT mistake_type, frequency, last_occurrence, resolution, prevention_strategy
                FROM mistakes 
                WHERE content_hash = ? OR mistake_type = ?
                ORDER BY last_occurrence DESC
            """, (content_hash, action_type))
            
            mistakes = cursor.fetchall()
            conn.close()
            
            if mistakes:
                total_failures = sum(row[1] for row in mistakes)
                latest_failure = mistakes[0]
                
                return {
                    "has_failed_before": True,
                    "failure_count": total_failures,
                    "last_failure": latest_failure[2],
                    "resolution": latest_failure[3],
                    "prevention_strategy": latest_failure[4] or "No strategy recorded"
                }
            
            return {"has_failed_before": False}
            
        except Exception as e:
            logger.error(f"Historical mistake check failed: {e}")
            return {"has_failed_before": False, "error": str(e)}
    
    async def _check_consistency(self, action_type: str, content: str, metadata: Dict) -> Dict[str, Any]:
        """Validate consistency with system state and policies"""
        try:
            consistency_result = {
                "consistent": True,
                "conflicts": [],
                "message": "No consistency issues detected"
            }
            
            # Check against system policies
            if metadata:
                # File path validation
                file_path = metadata.get("file_path", "")
                if file_path:
                    # Check against deny patterns
                    deny_patterns = ["node_modules", "third_party", ".git", "__pycache__"]
                    for pattern in deny_patterns:
                        if pattern in file_path:
                            consistency_result["consistent"] = False
                            consistency_result["conflicts"].append(f"File in restricted path: {pattern}")
                
                # Size limits
                content_size = len(content)
                if content_size > 100000:  # 100KB limit
                    consistency_result["consistent"] = False
                    consistency_result["conflicts"].append(f"Content too large: {content_size} bytes")
            
            # Action-specific consistency checks
            if action_type == "code_edit":
                # Check for dangerous patterns
                dangerous_patterns = ["rm -rf", "sudo", "eval(", "exec("]
                for pattern in dangerous_patterns:
                    if pattern in content:
                        consistency_result["consistent"] = False
                        consistency_result["conflicts"].append(f"Dangerous pattern detected: {pattern}")
            
            if consistency_result["conflicts"]:
                consistency_result["message"] = f"Found {len(consistency_result['conflicts'])} conflicts"
            
            return consistency_result
            
        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return {"consistent": False, "error": str(e)}
    
    async def _assess_risk(self, action_type: str, content: str, pilot_id: str) -> Dict[str, Any]:
        """Assess risk level for the proposed action"""
        try:
            risk_factors = []
            risk_score = 0.0
            
            # Content-based risk factors
            if "delete" in content.lower() or "remove" in content.lower():
                risk_factors.append("destructive_operation")
                risk_score += 0.3
            
            if any(pattern in content for pattern in ["sudo", "rm -rf", "DROP TABLE"]):
                risk_factors.append("high_privilege_operation")
                risk_score += 0.5
            
            if len(content) > 50000:  # Large changes
                risk_factors.append("large_change_size")
                risk_score += 0.2
            
            # Context-based risk factors
            if action_type in ["code_edit", "file_delete", "system_command"]:
                risk_factors.append("system_modification")
                risk_score += 0.2
            
            # Pilot-based risk assessment
            pilot_risk_levels = {
                "pilot_0_sentinel": 0.0,    # Sentinel is always safe
                "pilot_1_doc_architect": 0.1,  # Documentation is low risk
                "pilot_2_remediator": 0.3,     # Code fixes have moderate risk
                "pilot_3_codewright": 0.4      # Code generation has higher risk
            }
            
            pilot_risk = pilot_risk_levels.get(pilot_id, 0.2)
            risk_score += pilot_risk
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "critical"
            elif risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "level": risk_level,
                "score": risk_score,
                "factors": risk_factors,
                "pilot_contribution": pilot_risk
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {"level": "high", "error": str(e)}
    
    async def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        for issue in validation_result.get("issues", []):
            issue_type = issue["type"]
            
            if issue_type == "repetition":
                recommendations.append("Consider if this action is necessary - similar work was done recently")
                recommendations.append("Review previous results before proceeding")
            
            elif issue_type == "historical_failure":
                recommendations.append("This type of action has failed before - proceed with caution")
                recommendations.append("Review failure logs and apply prevention strategies")
            
            elif issue_type == "consistency":
                recommendations.append("Address consistency conflicts before proceeding")
                recommendations.append("Validate system state and dependencies")
        
        risk_level = validation_result.get("risk_level", "unknown")
        if risk_level in ["high", "critical"]:
            recommendations.append("High risk operation - consider manual review")
            recommendations.append("Create backup/snapshot before proceeding")
        
        return recommendations
    
    async def _record_event(self, event_type: str, event_data: Dict, pilot_id: str, 
                          session_id: str = None) -> str:
        """Record event in the vigilance log"""
        try:
            if session_id is None:
                session_id = f"session_{pilot_id}_{int(time.time())}"
            
            # Generate event record
            content_preview = str(event_data).get("content", "")[:200]
            content_hash = hashlib.sha256(content_preview.encode()).hexdigest()
            
            event_record = {
                "event_type": event_type,
                "content_hash": content_hash,
                "pilot_id": pilot_id,
                "session_id": session_id,
                "metadata": json.dumps(event_data),
                "risk_level": event_data.get("risk_level", "low")
            }
            
            # Store in database
            conn = sqlite3.connect(self.events_db)
            cursor = conn.execute("""
                INSERT INTO events (event_type, content_hash, pilot_id, session_id, metadata, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_record["event_type"],
                event_record["content_hash"], 
                event_record["pilot_id"],
                event_record["session_id"],
                event_record["metadata"],
                event_record["risk_level"]
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded event {event_id}: {event_type}")
            return str(event_id)
            
        except Exception as e:
            logger.error(f"Event recording failed: {e}")
            return ""
    
    async def record_mistake(self, mistake_type: str, error_message: str, 
                           content: str, context: Dict = None) -> bool:
        """Record a mistake for future prevention"""
        try:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            conn = sqlite3.connect(self.mistakes_db)
            
            # Check if this mistake already exists
            cursor = conn.execute("""
                SELECT id, frequency FROM mistakes 
                WHERE content_hash = ? AND mistake_type = ?
            """, (content_hash, mistake_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update frequency
                conn.execute("""
                    UPDATE mistakes 
                    SET frequency = frequency + 1, last_occurrence = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (existing[0],))
            else:
                # Insert new mistake
                conn.execute("""
                    INSERT INTO mistakes 
                    (mistake_type, content_hash, error_message, context)
                    VALUES (?, ?, ?, ?)
                """, (mistake_type, content_hash, error_message, json.dumps(context or {})))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded mistake: {mistake_type}")
            return True
            
        except Exception as e:
            logger.error(f"Mistake recording failed: {e}")
            return False
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content pieces"""
        try:
            # Use difflib for text similarity
            similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
            return similarity
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    async def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """Analyze a completed session for patterns and improvements"""
        try:
            conn = sqlite3.connect(self.events_db)
            
            # Get session events
            cursor = conn.execute("""
                SELECT event_type, risk_level, timestamp, metadata
                FROM events 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return {"error": "Session not found"}
            
            # Analyze patterns
            analysis = {
                "session_id": session_id,
                "total_events": len(events),
                "risk_distribution": {},
                "event_types": {},
                "timeline": [],
                "patterns_detected": [],
                "recommendations": []
            }
            
            # Count risk levels and event types
            for event in events:
                event_type, risk_level, timestamp, metadata = event
                
                analysis["risk_distribution"][risk_level] = analysis["risk_distribution"].get(risk_level, 0) + 1
                analysis["event_types"][event_type] = analysis["event_types"].get(event_type, 0) + 1
                analysis["timeline"].append({
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "risk_level": risk_level
                })
            
            # Detect patterns
            high_risk_events = analysis["risk_distribution"].get("high", 0)
            if high_risk_events > 5:
                analysis["patterns_detected"].append("High frequency of risky operations")
                analysis["recommendations"].append("Consider reducing operation scope or adding validation steps")
            
            repetitive_types = [k for k, v in analysis["event_types"].items() if v > 10]
            if repetitive_types:
                analysis["patterns_detected"].append(f"Repetitive operations: {', '.join(repetitive_types)}")
                analysis["recommendations"].append("Consider automation or batching for repetitive tasks")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Session analysis failed: {e}")
            return {"error": str(e)}
    
    async def get_sentinel_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive sentinel vigilance report"""
        try:
            since_time = datetime.now() - timedelta(hours=time_window_hours)
            
            conn = sqlite3.connect(self.events_db)
            
            # Get event summary
            cursor = conn.execute("""
                SELECT event_type, risk_level, COUNT(*) as count
                FROM events 
                WHERE timestamp > ?
                GROUP BY event_type, risk_level
                ORDER BY count DESC
            """, (since_time.isoformat(),))
            
            event_summary = {}
            total_events = 0
            
            for row in cursor.fetchall():
                event_type, risk_level, count = row
                if event_type not in event_summary:
                    event_summary[event_type] = {}
                event_summary[event_type][risk_level] = count
                total_events += count
            
            # Get mistake summary
            cursor = conn.execute("""
                SELECT mistake_type, COUNT(*) as count, MAX(last_occurrence) as latest
                FROM mistakes 
                WHERE last_occurrence > ?
                GROUP BY mistake_type
                ORDER BY count DESC
            """, (since_time.isoformat(),))
            
            mistake_summary = {}
            for row in cursor.fetchall():
                mistake_type, count, latest = row
                mistake_summary[mistake_type] = {"count": count, "latest": latest}
            
            conn.close()
            
            # Calculate vigilance metrics
            high_risk_events = sum(
                summary.get("high", 0) + summary.get("critical", 0)
                for summary in event_summary.values()
            )
            
            vigilance_score = 1.0 - (high_risk_events / max(total_events, 1))
            
            report = {
                "time_window_hours": time_window_hours,
                "total_events": total_events,
                "event_summary": event_summary,
                "mistake_summary": mistake_summary,
                "vigilance_metrics": {
                    "vigilance_score": vigilance_score,
                    "high_risk_ratio": high_risk_events / max(total_events, 1),
                    "mistake_prevention_rate": 1.0 - (len(mistake_summary) / max(total_events, 1))
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Sentinel report generation failed: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self):
        """Clean up old events and mistakes based on retention policy"""
        try:
            current_time = datetime.now()
            
            # Clean old events
            event_cutoff = current_time - timedelta(days=self.config["event_retention_days"])
            conn = sqlite3.connect(self.events_db)
            cursor = conn.execute("DELETE FROM events WHERE timestamp < ?", (event_cutoff.isoformat(),))
            events_deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            # Clean old mistakes
            mistake_cutoff = current_time - timedelta(days=self.config["mistake_memory_days"])
            conn = sqlite3.connect(self.mistakes_db)
            cursor = conn.execute("DELETE FROM mistakes WHERE last_occurrence < ?", (mistake_cutoff.isoformat(),))
            mistakes_deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleanup completed: removed {events_deleted} events, {mistakes_deleted} mistakes")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive sentinel statistics"""
        try:
            # Event statistics
            conn = sqlite3.connect(self.events_db)
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT risk_level, COUNT(*) 
                FROM events 
                GROUP BY risk_level
            """)
            risk_distribution = dict(cursor.fetchall())
            conn.close()
            
            # Mistake statistics
            conn = sqlite3.connect(self.mistakes_db)
            cursor = conn.execute("SELECT COUNT(*) FROM mistakes")
            total_mistakes = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT mistake_type, SUM(frequency) 
                FROM mistakes 
                GROUP BY mistake_type
                ORDER BY SUM(frequency) DESC
                LIMIT 5
            """)
            top_mistakes = dict(cursor.fetchall())
            conn.close()
            
            return {
                "events": {
                    "total": total_events,
                    "risk_distribution": risk_distribution
                },
                "mistakes": {
                    "total": total_mistakes,
                    "top_types": top_mistakes
                },
                "vigilance": {
                    "active_sessions": len(self.active_sessions),
                    "content_hashes_tracked": len(self.content_hashes),
                    "pattern_cache_size": len(self.pattern_cache)
                },
                "config": self.config
            }
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {e}")
            return {"error": str(e)}