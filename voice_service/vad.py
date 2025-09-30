"""
Voice Activity Detection for Linux/PipeWire
Adapted from TelePrompt patterns for HAASP voice activation
"""

import numpy as np
import sounddevice as sd
import asyncio
import logging
import json
import time
from collections import deque
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """
    RMS-based Voice Activity Detection for PipeWire
    Features:
    - Automatic noise floor calibration
    - Circular buffer for speech segment capture
    - Configurable thresholds and timing
    - Real-time processing with low latency
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # VAD parameters
        self.noise_floor = None
        self.speech_threshold = None
        self.silence_threshold = None
        
        # State tracking
        self.is_speech_active = False
        self.speech_start_time = None
        self.silence_duration = 0
        self.min_speech_duration = 0.5  # seconds
        self.max_silence_duration = 1.0  # seconds
        
        # Audio buffer (10 seconds capacity)
        self.buffer_size = sample_rate * 10
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.speech_segments = []
        
        # Configuration
        self.config = {
            "noise_floor_multiplier": 2.0,
            "speech_threshold_multiplier": 3.0,
            "calibration_duration": 5.0,
            "min_segment_length": 1.0,
            "max_segment_length": 30.0
        }
        
        # Callbacks
        self.on_speech_start = None
        self.on_speech_end = None
        self.on_segment_ready = None
        
        logger.info("VoiceActivityDetector initialized")
    
    async def calibrate_noise_floor(self, duration: float = None) -> Dict[str, float]:
        """
        Calibrate noise floor using ambient audio
        Must be called before voice detection
        """
        if duration is None:
            duration = self.config["calibration_duration"]
        
        logger.info(f"Calibrating noise floor for {duration} seconds...")
        logger.info("Please remain quiet during calibration...")
        
        try:
            # Collect ambient audio samples
            rms_samples = []
            samples_needed = int(duration * self.sample_rate / self.chunk_size)
            
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio input status: {status}")
                
                # Calculate RMS for this chunk
                rms = np.sqrt(np.mean(indata.flatten() ** 2))
                rms_samples.append(rms)
            
            # Record ambient audio
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=audio_callback,
                device=self._find_best_input_device()
            ):
                await asyncio.sleep(duration)
            
            if not rms_samples:
                raise Exception("No audio samples collected during calibration")
            
            # Calculate noise floor statistics
            rms_array = np.array(rms_samples)
            mean_rms = np.mean(rms_array)
            std_rms = np.std(rms_array)
            max_rms = np.max(rms_array)
            
            # Set thresholds based on noise floor
            self.noise_floor = mean_rms
            self.speech_threshold = mean_rms * self.config["speech_threshold_multiplier"]
            self.silence_threshold = mean_rms * self.config["noise_floor_multiplier"]
            
            calibration_result = {
                "noise_floor": float(self.noise_floor),
                "speech_threshold": float(self.speech_threshold),
                "silence_threshold": float(self.silence_threshold),
                "stats": {
                    "mean_rms": float(mean_rms),
                    "std_rms": float(std_rms),
                    "max_rms": float(max_rms),
                    "samples_collected": len(rms_samples)
                },
                "calibrated_at": datetime.now().isoformat()
            }
            
            logger.info("Noise floor calibration completed")
            logger.info(f"Speech threshold: {self.speech_threshold:.6f}")
            
            return calibration_result
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return {"error": str(e)}
    
    def _find_best_input_device(self) -> Optional[str]:
        """Find best PipeWire input device"""
        try:
            devices = sd.query_devices()
            
            # Look for PipeWire devices first
            for device in devices:
                name = device['name'].lower()
                if ('pipewire' in name or 'pulse' in name) and device['max_input_channels'] > 0:
                    logger.info(f"Selected audio device: {device['name']}")
                    return device['name']
            
            # Fallback to default
            default_device = sd.default.device[0]
            if default_device is not None:
                device_info = sd.query_devices(default_device)
                logger.info(f"Using default audio device: {device_info['name']}")
                return default_device
            
            return None
            
        except Exception as e:
            logger.error(f"Device selection failed: {e}")
            return None
    
    def process_audio_chunk(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Process audio chunk and detect speech events
        Returns: None, 'speech_start', 'speech_end', or 'segment_ready'
        """
        try:
            if self.speech_threshold is None:
                logger.warning("VAD not calibrated - call calibrate_noise_floor() first")
                return None
            
            # Add to circular buffer
            self.audio_buffer.extend(audio_data.flatten())
            
            # Calculate RMS for current chunk
            rms = np.sqrt(np.mean(audio_data.flatten() ** 2))
            
            current_time = time.time()
            
            # State machine for speech detection
            if not self.is_speech_active:
                # Currently in silence, check for speech start
                if rms > self.speech_threshold:
                    self.is_speech_active = True
                    self.speech_start_time = current_time
                    self.silence_duration = 0
                    
                    logger.debug(f"Speech started (RMS: {rms:.6f})")
                    
                    if self.on_speech_start:
                        self.on_speech_start()
                    
                    return "speech_start"
            
            else:
                # Currently in speech, check for speech end
                if rms < self.silence_threshold:
                    self.silence_duration += self.chunk_size / self.sample_rate
                    
                    # Check if silence duration exceeds threshold
                    if self.silence_duration >= self.max_silence_duration:
                        speech_duration = current_time - self.speech_start_time
                        
                        # Only process if speech was long enough
                        if speech_duration >= self.min_speech_duration:
                            segment = self.extract_speech_segment()
                            self.speech_segments.append({
                                "audio": segment,
                                "start_time": self.speech_start_time,
                                "duration": speech_duration,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            logger.debug(f"Speech ended, segment captured ({speech_duration:.2f}s)")
                            
                            if self.on_segment_ready:
                                self.on_segment_ready(segment)
                            
                            # Reset state
                            self.is_speech_active = False
                            self.speech_start_time = None
                            self.silence_duration = 0
                            
                            if self.on_speech_end:
                                self.on_speech_end()
                            
                            return "segment_ready"
                        
                        else:
                            # Too short, reset without capturing
                            self.is_speech_active = False
                            self.speech_start_time = None
                            self.silence_duration = 0
                            return "speech_end"
                
                else:
                    # Still in speech, reset silence counter
                    self.silence_duration = 0
            
            return None
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return None
    
    def extract_speech_segment(self) -> np.ndarray:
        """Extract speech segment from circular buffer"""
        try:
            if not self.speech_start_time:
                return np.array([])
            
            # Calculate segment length in samples
            current_time = time.time()
            segment_duration = current_time - self.speech_start_time
            segment_samples = int(segment_duration * self.sample_rate)
            
            # Extract from buffer (most recent samples)
            buffer_array = np.array(self.audio_buffer)
            
            if len(buffer_array) >= segment_samples:
                segment = buffer_array[-segment_samples:]
            else:
                segment = buffer_array
            
            return segment
            
        except Exception as e:
            logger.error(f"Segment extraction failed: {e}")
            return np.array([])
    
    def get_latest_segment(self) -> Optional[Dict[str, Any]]:
        """Get the most recent speech segment"""
        if self.speech_segments:
            return self.speech_segments[-1]
        return None
    
    def clear_segments(self):
        """Clear stored speech segments"""
        self.speech_segments.clear()
        logger.debug("Cleared speech segments")
    
    def get_vad_statistics(self) -> Dict[str, Any]:
        """Get VAD performance statistics"""
        return {
            "calibration": {
                "noise_floor": self.noise_floor,
                "speech_threshold": self.speech_threshold,
                "silence_threshold": self.silence_threshold
            },
            "state": {
                "is_speech_active": self.is_speech_active,
                "silence_duration": self.silence_duration,
                "buffer_fill": len(self.audio_buffer) / self.buffer_size
            },
            "segments": {
                "total_captured": len(self.speech_segments),
                "latest_timestamp": self.speech_segments[-1]["timestamp"] if self.speech_segments else None
            },
            "config": self.config
        }

class PipeWireAudioCapture:
    """
    Audio capture optimized for PipeWire on Linux
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = None
        self.stream = None
        self.is_recording = False
        
        # Audio processing
        self.vad = VoiceActivityDetector(sample_rate)
        self.audio_callback = None
        
        logger.info("PipeWireAudioCapture initialized")
    
    def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available audio input devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        "id": i,
                        "name": device['name'],
                        "channels": device['max_input_channels'],
                        "sample_rate": device['default_samplerate'],
                        "api": device.get('hostapi_name', 'unknown'),
                        "is_pipewire": 'pipewire' in device['name'].lower() or 'pulse' in device['name'].lower()
                    })
            
            return input_devices
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return []
    
    def select_device(self, device_id: Optional[int] = None, prefer_pipewire: bool = True):
        """Select audio input device"""
        try:
            devices = self.discover_devices()
            
            if device_id is not None:
                # Use specified device
                for device in devices:
                    if device["id"] == device_id:
                        self.device = device_id
                        logger.info(f"Selected device {device_id}: {device['name']}")
                        return
            
            # Auto-select best device
            if prefer_pipewire:
                for device in devices:
                    if device["is_pipewire"]:
                        self.device = device["id"]
                        logger.info(f"Auto-selected PipeWire device: {device['name']}")
                        return
            
            # Fallback to first available device
            if devices:
                self.device = devices[0]["id"]
                logger.info(f"Using fallback device: {devices[0]['name']}")
            else:
                logger.error("No input devices found")
                
        except Exception as e:
            logger.error(f"Device selection failed: {e}")
    
    async def start_capture(self, audio_callback: Callable = None):
        """Start continuous audio capture with VAD"""
        try:
            if self.device is None:
                self.select_device()
            
            if audio_callback:
                self.audio_callback = audio_callback
            
            # Calibrate VAD if not already done
            if self.vad.speech_threshold is None:
                logger.info("VAD not calibrated, running calibration...")
                await self.vad.calibrate_noise_floor()
            
            logger.info("Starting audio capture...")
            self.is_recording = True
            
            def stream_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio stream status: {status}")
                
                # Process through VAD
                vad_event = self.vad.process_audio_chunk(indata)
                
                # Handle VAD events
                if vad_event == "segment_ready":
                    segment = self.vad.get_latest_segment()
                    if segment and self.audio_callback:
                        # Call async callback in thread pool
                        asyncio.create_task(self._handle_segment_async(segment))
                
                # Call user callback if provided
                if self.audio_callback:
                    try:
                        self.audio_callback(indata, vad_event)
                    except Exception as e:
                        logger.error(f"Audio callback error: {e}")
            
            # Start audio stream
            self.stream = sd.InputStream(
                device=self.device,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.vad.chunk_size,
                callback=stream_callback,
                dtype=np.float32
            )
            
            self.stream.start()
            logger.info("Audio capture started successfully")
            
            # Keep capture running
            while self.is_recording:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Audio capture failed: {e}")
            self.is_recording = False
    
    async def _handle_segment_async(self, segment: Dict[str, Any]):
        """Handle speech segment asynchronously"""
        try:
            logger.info(f"Processing speech segment ({segment['duration']:.2f}s)")
            
            # Here you would typically:
            # 1. Transcribe the audio (via Whisper, Grok, etc.)
            # 2. Add to conversation memory
            # 3. Trigger appropriate pilot response
            
            # For now, just log the segment info
            audio_data = segment["audio"]
            logger.info(f"Segment captured: {len(audio_data)} samples, RMS: {np.sqrt(np.mean(audio_data**2)):.6f}")
            
        except Exception as e:
            logger.error(f"Segment handling failed: {e}")
    
    def stop_capture(self):
        """Stop audio capture"""
        try:
            self.is_recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            logger.info("Audio capture stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop capture: {e}")
    
    def save_segment_to_file(self, segment: Dict[str, Any], file_path: str):
        """Save speech segment to WAV file"""
        try:
            import soundfile as sf
            
            audio_data = segment["audio"]
            sf.write(file_path, audio_data, self.sample_rate)
            
            logger.info(f"Saved speech segment to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save segment: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get VAD and capture statistics"""
        return {
            "vad": self.vad.get_vad_statistics(),
            "capture": {
                "device": self.device,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "is_recording": self.is_recording,
                "buffer_size": self.buffer_size
            },
            "segments": {
                "total_captured": len(self.vad.speech_segments),
                "latest": self.vad.get_latest_segment()
            }
        }

class SpeechTranscriptionService:
    """
    Speech transcription using Grok API or local models
    """
    
    def __init__(self, rag_orchestrator):
        self.rag = rag_orchestrator
        self.temp_audio_dir = Path("~/.local/share/haasp/temp_audio").expanduser()
        self.temp_audio_dir.mkdir(parents=True, exist_ok=True)
        
    async def transcribe_audio(self, audio_segment: np.ndarray, 
                             sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio segment to text
        """
        try:
            # Save audio to temporary file
            temp_file = self.temp_audio_dir / f"speech_{int(time.time())}.wav"
            
            import soundfile as sf
            sf.write(str(temp_file), audio_segment, sample_rate)
            
            # For now, use Grok for transcription (placeholder)
            # In production, you might use:
            # - Local Whisper model
            # - OpenAI Whisper API
            # - Google Speech-to-Text
            
            # Simulate transcription for now
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Clean up temp file
            temp_file.unlink()
            
            # Placeholder transcription
            transcription = "Audio transcription would go here"
            
            return {
                "transcription": transcription,
                "confidence": 0.95,
                "language": "en",
                "duration": len(audio_segment) / sample_rate,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"error": str(e)}
    
    async def process_voice_command(self, transcription: str, pilot_id: str = None) -> Dict[str, Any]:
        """Process transcribed voice command through RAG system"""
        try:
            # Determine command type
            command_type = self._classify_command(transcription)
            
            # Process through appropriate pilot
            if command_type == "code_question":
                response = await self.rag.query_rag(
                    transcription, task_type="code", pilot_id="pilot_3_codewright"
                )
            elif command_type == "documentation":
                response = await self.rag.query_rag(
                    transcription, task_type="documentation", pilot_id="pilot_1_doc_architect"
                )
            elif command_type == "debugging":
                response = await self.rag.query_rag(
                    transcription, task_type="debugging", pilot_id="pilot_2_remediator"
                )
            else:
                response = await self.rag.query_rag(
                    transcription, task_type="general", pilot_id=pilot_id
                )
            
            return {
                "voice_input": transcription,
                "command_type": command_type,
                "response": response,
                "processed_by": pilot_id or "general"
            }
            
        except Exception as e:
            logger.error(f"Voice command processing failed: {e}")
            return {"error": str(e)}
    
    def _classify_command(self, transcription: str) -> str:
        """Classify voice command type"""
        text_lower = transcription.lower()
        
        if any(keyword in text_lower for keyword in ["debug", "error", "fix", "problem"]):
            return "debugging"
        elif any(keyword in text_lower for keyword in ["document", "explain", "describe"]):
            return "documentation"
        elif any(keyword in text_lower for keyword in ["code", "function", "implement", "write"]):
            return "code_question"
        else:
            return "general"

class VoiceServiceAPI:
    """
    FastAPI service exposing voice activation endpoints
    """
    
    def __init__(self, rag_orchestrator):
        self.capture = PipeWireAudioCapture()
        self.transcription = SpeechTranscriptionService(rag_orchestrator)
        self.is_active = False
        
    async def start_voice_service(self):
        """Start the voice activation service"""
        try:
            logger.info("Starting voice activation service...")
            
            # Set up callbacks
            self.capture.vad.on_speech_start = self._on_speech_start
            self.capture.vad.on_speech_end = self._on_speech_end
            self.capture.vad.on_segment_ready = self._on_segment_ready
            
            # Start capture
            self.is_active = True
            await self.capture.start_capture()
            
        except Exception as e:
            logger.error(f"Voice service failed: {e}")
            self.is_active = False
    
    def _on_speech_start(self):
        """Handle speech start event"""
        logger.debug("🎤 Speech detection started")
    
    def _on_speech_end(self):
        """Handle speech end event"""
        logger.debug("🔇 Speech detection ended")
    
    async def _on_segment_ready(self, audio_segment: np.ndarray):
        """Handle complete speech segment"""
        try:
            logger.info("🎵 Processing speech segment...")
            
            # Transcribe audio
            transcription_result = await self.transcription.transcribe_audio(audio_segment)
            
            if "transcription" in transcription_result:
                # Process as voice command
                command_result = await self.transcription.process_voice_command(
                    transcription_result["transcription"]
                )
                
                logger.info(f"Voice command processed: {command_result.get('command_type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Segment processing failed: {e}")
    
    def stop_voice_service(self):
        """Stop voice activation service"""
        self.is_active = False
        self.capture.stop_capture()
        logger.info("Voice service stopped")
    
    async def calibrate_microphone(self) -> Dict[str, Any]:
        """Calibrate microphone for voice detection"""
        return await self.capture.vad.calibrate_noise_floor()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get voice service status"""
        return {
            "active": self.is_active,
            "audio_devices": self.capture.discover_devices(),
            "selected_device": self.capture.device,
            "vad_calibrated": self.capture.vad.speech_threshold is not None,
            "statistics": self.capture.get_statistics()
        }