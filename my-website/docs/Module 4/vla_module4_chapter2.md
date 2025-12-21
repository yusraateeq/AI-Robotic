# Chapter 2: Voice-to-Action - Speech Recognition and Command Processing

## Introduction

Voice is the most natural way for humans to communicate with robots. This chapter covers implementing robust speech recognition using OpenAI Whisper, processing voice commands, and translating them into actionable robot directives. We'll build a complete voice-to-action pipeline that works reliably in real-world environments.

## Speech Recognition Pipeline

### Overview

```
Audio Input (Microphone)
        ↓
Audio Processing
├─ Denoising
├─ Format conversion
└─ Normalization
        ↓
Speech Recognition (Whisper)
├─ Acoustic model
├─ Language model
└─ Confidence scores
        ↓
Transcription
└─ "Pick up the red cube"
        ↓
Command Parsing
├─ Intent extraction
├─ Entity recognition
└─ Parameter extraction
        ↓
Robot Action
```

## Whisper Setup and Integration

### Installation

```bash
#!/bin/bash
# Install OpenAI Whisper

pip install openai-whisper
pip install librosa
pip install sounddevice
pip install soundfile

# Download Whisper model
# Models: tiny, base, small, medium, large
# Larger = more accurate but slower

# For real-time on CPU
whisper_model="base"

# For high accuracy on GPU
whisper_model="medium"
```

### Basic Whisper Implementation

```python
"""
Basic speech recognition with Whisper
"""

import whisper
import numpy as np
import librosa
from typing import Tuple, Dict

class WhisperASR:
    """Automatic Speech Recognition using OpenAI Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: "tiny" (fastest), "small", "medium", "large" (most accurate)
        """
        self.model = whisper.load_model(model_size)
        self.device = self.model.device
        
        self.model_size = model_size
        self.transcriptions = []
    
    def transcribe_file(self, audio_file: str) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_file: Path to audio file
        
        Returns:
            Dictionary with transcription and metadata
        """
        result = self.model.transcribe(audio_file, language="en")
        
        return {
            'text': result['text'],
            'confidence': result.get('confidence', 0.9),
            'language': result['language'],
            'segments': result['segments']
        }
    
    def transcribe_audio_array(self, audio: np.ndarray, 
                               sr: int = 16000) -> Dict:
        """
        Transcribe audio from numpy array
        
        Args:
            audio: Audio samples (float32, range [-1, 1])
            sr: Sample rate (Hz)
        
        Returns:
            Transcription dictionary
        """
        # Resample if necessary
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        
        # Normalize
        if audio.max() > 1.0 or audio.min() < -1.0:
            audio = audio / np.max(np.abs(audio))
        
        # Transcribe
        result = self.model.transcribe(
            audio,
            language="en",
            fp16=True  # Use FP16 for speed on GPU
        )
        
        return {
            'text': result['text'],
            'confidence': self._estimate_confidence(result),
            'segments': result['segments']
        }
    
    def _estimate_confidence(self, result) -> float:
        """Estimate overall transcription confidence"""
        # Average probabilities from segments
        if 'segments' not in result or not result['segments']:
            return 0.9
        
        probs = [seg.get('confidence', 0.9) for seg in result['segments']]
        return np.mean(probs) if probs else 0.9

class RealtimeAudioCapture:
    """Capture audio in real-time from microphone"""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_recording = False
        
        import sounddevice as sd
        self.sd = sd
    
    def record_until_silence(self, silence_duration: float = 2.0,
                            silence_threshold: float = 0.02) -> np.ndarray:
        """
        Record audio until silence detected
        
        Args:
            silence_duration: Seconds of silence to end recording
            silence_threshold: RMS threshold for silence
        
        Returns:
            Audio array
        """
        print("Recording... (silence to stop)")
        
        frames = []
        silence_frames = 0
        max_silence_frames = int(self.sample_rate * silence_duration / self.chunk_size)
        
        stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            dtype=np.float32
        )
        
        with stream:
            while True:
                data, overflow = stream.read(self.chunk_size)
                
                frames.append(data.squeeze())
                
                # Check for silence
                rms = np.sqrt(np.mean(data**2))
                
                if rms < silence_threshold:
                    silence_frames += 1
                    if silence_frames > max_silence_frames:
                        break
                else:
                    silence_frames = 0
        
        # Concatenate all frames
        audio = np.concatenate(frames)
        
        print(f"Recording complete. Duration: {len(audio)/self.sample_rate:.1f}s")
        
        return audio
    
    def record_duration(self, duration: float) -> np.ndarray:
        """Record for fixed duration"""
        print(f"Recording for {duration}s...")
        
        stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            dtype=np.float32
        )
        
        with stream:
            data, overflow = stream.read(int(self.sample_rate * duration))
        
        return data.squeeze()
```

## Advanced Speech Processing

### Noise Reduction

```python
"""
Improve speech recognition with audio preprocessing
"""

import scipy.signal as signal

class AudioPreprocessor:
    """Preprocess audio for better recognition"""
    
    @staticmethod
    def denoise(audio: np.ndarray, sr: int = 16000, 
               noise_duration: float = 1.0) -> np.ndarray:
        """
        Reduce background noise
        
        Assumes first noise_duration seconds are noise profile
        """
        # Get noise profile from beginning
        noise_sample_count = int(sr * noise_duration)
        noise_profile = audio[:noise_sample_count]
        
        # Compute noise spectrum
        noise_spectrum = np.abs(np.fft.rfft(noise_profile))
        noise_mean = np.mean(noise_spectrum, axis=0)
        
        # Apply spectral subtraction
        denoised = []
        
        for frame_start in range(0, len(audio), sr // 4):
            frame_end = min(frame_start + sr // 4, len(audio))
            frame = audio[frame_start:frame_end]
            
            # FFT
            spectrum = np.fft.rfft(frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            # Subtract noise spectrum
            alpha = 3.0  # Subtraction factor
            magnitude_denoised = np.maximum(magnitude - alpha * noise_mean, 0)
            
            # Reconstruct
            spectrum_denoised = magnitude_denoised * np.exp(1j * phase)
            frame_denoised = np.fft.irfft(spectrum_denoised)
            
            denoised.append(frame_denoised)
        
        return np.concatenate(denoised)
    
    @staticmethod
    def normalize_loudness(audio: np.ndarray, target_db: float = -20) -> np.ndarray:
        """Normalize audio loudness"""
        # Compute current RMS
        rms = np.sqrt(np.mean(audio**2))
        
        if rms == 0:
            return audio
        
        # Convert to dB
        current_db = 20 * np.log10(rms)
        
        # Compute gain
        gain = 10 ** ((target_db - current_db) / 20)
        
        return np.clip(audio * gain, -1, 1)
    
    @staticmethod
    def remove_silence(audio: np.ndarray, sr: int = 16000,
                      threshold: float = 0.02) -> np.ndarray:
        """Remove silent sections"""
        # Compute frame energy
        frame_len = sr // 10  # 100ms frames
        frames = []
        
        for i in range(0, len(audio), frame_len):
            frame = audio[i:i+frame_len]
            energy = np.sqrt(np.mean(frame**2))
            frames.append(energy)
        
        # Find non-silent frames
        frames = np.array(frames)
        active_frames = frames > threshold
        
        # Expand slightly to include edges
        for i in range(len(active_frames)-1):
            if active_frames[i] and active_frames[i+1]:
                active_frames[i] = True
                active_frames[i+1] = True
        
        # Extract audio from active frames
        audio_desilenced = []
        for i, is_active in enumerate(active_frames):
            if is_active:
                start = i * frame_len
                end = min((i+1) * frame_len, len(audio))
                audio_desilenced.append(audio[start:end])
        
        return np.concatenate(audio_desilenced) if audio_desilenced else audio
```

## Command Understanding

### Intent and Entity Recognition

```python
"""
Parse voice commands into intents and entities
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class IntentType(Enum):
    """Robot action intents"""
    PICK_UP = "pick_up"
    PLACE = "place"
    MOVE = "move"
    NAVIGATE = "navigate"
    PUSH = "push"
    ROTATE = "rotate"
    OPEN = "open"
    CLOSE = "close"
    IDENTIFY = "identify"
    FOLLOW = "follow"
    WAIT = "wait"
    HELP = "help"

@dataclass
class Entity:
    """Recognized entity in command"""
    type: str  # 'object', 'location', 'action', 'property'
    value: str
    confidence: float

@dataclass
class ParsedCommand:
    """Parsed voice command"""
    intent: IntentType
    entities: List[Entity]
    raw_text: str
    confidence: float

class CommandParser:
    """Parse voice commands into structured format"""
    
    # Rule-based patterns for common commands
    PATTERNS = {
        IntentType.PICK_UP: [
            r"(?:pick up|grab|grasp|take)(?:\s+(?:the|a))?\s+(.+?)(?:\s+and|$)",
            r"(?:get|fetch)\s+(?:the|a)?\s+(.+?)(?:\s+and|$)"
        ],
        IntentType.PLACE: [
            r"(?:put|place|set down)\s+(?:the|a)?\s+(\w+)\s+(?:on|in|at)\s+(?:the|a)?\s+(.+?)$",
            r"(?:drop|release)\s+(?:the|a)?\s+(\w+)\s+(?:on|in|at)\s+(?:the|a)?\s+(.+?)$"
        ],
        IntentType.MOVE: [
            r"(?:move|shift)\s+(?:the|a)?\s+(\w+)\s+(?:to|towards)\s+(?:the|a)?\s+(.+?)$"
        ],
        IntentType.NAVIGATE: [
            r"(?:go to|navigate to|move to)\s+(?:the|a)?\s+(.+?)$",
            r"(?:walk|move)\s+(?:to|towards)\s+(?:the|a)?\s+(.+?)$"
        ]
    }
    
    # Object color/property patterns
    COLOR_PATTERN = r"(red|green|blue|yellow|white|black|gray|orange|purple)\s+(\w+)"
    SIZE_PATTERN = r"(small|large|big|tiny|huge)\s+(\w+)"
    
    def __init__(self):
        self.intent_confidence = {}
    
    def parse(self, text: str, use_llm: bool = False) -> ParsedCommand:
        """
        Parse voice command
        
        Args:
            text: Transcribed text
            use_llm: Use LLM for parsing (more accurate but slower)
        
        Returns:
            Parsed command with intent and entities
        """
        text = text.strip().lower()
        
        if use_llm:
            return self._parse_with_llm(text)
        else:
            return self._parse_with_patterns(text)
    
    def _parse_with_patterns(self, text: str) -> ParsedCommand:
        """Parse using regex patterns"""
        
        best_intent = None
        best_match = None
        best_confidence = 0
        
        # Try each intent pattern
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = 0.9 - (0.1 if intent in self.PATTERNS else 0)
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_match = match
                        best_confidence = confidence
        
        if best_intent is None:
            # Fallback: check for action keywords
            if any(word in text for word in ['pick', 'grab', 'take']):
                best_intent = IntentType.PICK_UP
            elif any(word in text for word in ['place', 'put', 'set']):
                best_intent = IntentType.PLACE
            elif any(word in text for word in ['go', 'move', 'navigate']):
                best_intent = IntentType.NAVIGATE
            else:
                best_intent = IntentType.HELP
                best_confidence = 0.5
        
        # Extract entities
        entities = self._extract_entities(text)
        
        return ParsedCommand(
            intent=best_intent,
            entities=entities,
            raw_text=text,
            confidence=best_confidence
        )
    
    def _parse_with_llm(self, text: str) -> ParsedCommand:
        """Parse using LLM for better accuracy"""
        # Requires LLM integration
        # Will be covered in Chapter 3
        pass
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract objects, locations, and properties"""
        entities = []
        
        # Colors
        color_matches = re.findall(self.COLOR_PATTERN, text)
        for color, obj in color_matches:
            entities.append(Entity(
                type='property',
                value=f'{color} {obj}',
                confidence=0.85
            ))
        
        # Sizes
        size_matches = re.findall(self.SIZE_PATTERN, text)
        for size, obj in size_matches:
            entities.append(Entity(
                type='property',
                value=f'{size} {obj}',
                confidence=0.85
            ))
        
        # Location keywords
        locations = ['table', 'shelf', 'floor', 'bin', 'corner', 'center']
        for loc in locations:
            if loc in text:
                entities.append(Entity(
                    type='location',
                    value=loc,
                    confidence=0.9
                ))
        
        return entities
```

## ROS 2 Integration

### Voice Command Node

```python
"""
ROS 2 node for voice-to-action
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
import sounddevice as sd
import numpy as np

class VoiceCommandNode(Node):
    """
    Listen to voice commands and dispatch to robot
    """
    
    def __init__(self):
        super().__init__('voice_command_node')
        
        # Initialize components
        self.asr = WhisperASR(model_size="base")
        self.preprocessor = AudioPreprocessor()
        self.parser = CommandParser()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # ROS 2 publishers
        self.command_pub = self.create_publisher(
            String, '/robot/command', 10
        )
        
        self.action_pub = self.create_publisher(
            String, '/robot/action', 10
        )
        
        # Timer for voice capture
        self.capture_timer = self.create_timer(
            0.1, self.listen_and_process
        )
        
        # State
        self.is_listening = False
        self.last_command_time = 0
        
        self.get_logger().info('Voice Command Node initialized')
    
    def listen_and_process(self):
        """Listen for voice commands"""
        
        # Check if listening is enabled
        if not self.is_listening:
            return
        
        try:
            # Record until silence
            audio_capture = RealtimeAudioCapture(
                sample_rate=self.sample_rate
            )
            
            audio = audio_capture.record_until_silence(
                silence_duration=1.0,
                silence_threshold=0.02
            )
            
            # Preprocess audio
            audio = self.preprocessor.normalize_loudness(audio)
            audio = self.preprocessor.denoise(audio, sr=self.sample_rate)
            
            # Transcribe
            result = self.asr.transcribe_audio_array(
                audio, sr=self.sample_rate
            )
            
            self.get_logger().info(
                f"Transcribed: {result['text']} "
                f"(confidence: {result['confidence']:.2f})"
            )
            
            # Parse command
            parsed = self.parser.parse(result['text'])
            
            self.get_logger().info(
                f"Parsed intent: {parsed.intent.value}"
            )
            
            # Publish command
            self.command_pub.publish(String(data=result['text']))
            
            # Dispatch action
            self.dispatch_action(parsed)
            
        except Exception as e:
            self.get_logger().error(f"Error processing voice command: {e}")
    
    def dispatch_action(self, command: ParsedCommand):
        """
        Dispatch parsed command to action system
        """
        action_str = f"intent:{command.intent.value}"
        
        # Add entities to action string
        for entity in command.entities:
            action_str += f"|{entity.type}:{entity.value}"
        
        self.action_pub.publish(String(data=action_str))
    
    def start_listening(self):
        """Enable voice listening"""
        self.is_listening = True
        self.get_logger().info("Started listening for voice commands")
    
    def stop_listening(self):
        """Disable voice listening"""
        self.is_listening = False
        self.get_logger().info("Stopped listening for voice commands")

def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommandNode()
    
    # Start listening
    node.start_listening()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Error Handling and Confidence Thresholding

```python
"""
Robust voice command processing with confidence handling
"""

class VoiceCommandProcessor:
    """Process voice with confidence-based fallback"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.asr = WhisperASR()
        self.parser = CommandParser()
    
    def process_voice_safely(self, audio: np.ndarray) -> Optional[ParsedCommand]:
        """
        Process voice command with safety checks
        
        Returns:
            ParsedCommand if confidence sufficient, None otherwise
        """
        # Transcribe
        result = self.asr.transcribe_audio_array(audio)
        
        if result['confidence'] < self.confidence_threshold:
            return None  # Insufficient confidence
        
        # Parse
        parsed = self.parser.parse(result['text'])
        
        if parsed.confidence < self.confidence_threshold:
            return None  # Could not parse reliably
        
        return parsed
    
    def request_confirmation(self, command: ParsedCommand) -> bool:
        """Ask user to confirm unclear command"""
        print(f"Did you say: {command.intent.value}?")
        print(f"Confidence: {command.confidence:.2%}")
        print("Say 'yes' to confirm or 'no' to retry:")
        
        # Listen for confirmation
        audio = RealtimeAudioCapture().record_duration(3.0)
        result = self.asr.transcribe_audio_array(audio)
        
        return 'yes' in result['text'].lower()
    
    def handle_ambiguous_command(self, audio: np.ndarray) -> Optional[ParsedCommand]:
        """
        Handle ambiguous command with disambiguation
        """
        result = self.asr.transcribe_audio_array(audio)
        
        if result['confidence'] < 0.5:
            print("I didn't catch that. Could you repeat?")
            return None
        
        parsed = self.parser.parse(result['text'])
        
        if parsed.confidence < self.confidence_threshold:
            # Ask for confirmation
            if self.request_confirmation(parsed):
                return parsed
            else:
                return None
        
        return parsed
```

## Summary

Voice-to-action systems enable intuitive robot control through natural speech. By combining robust speech recognition with intelligent command parsing and error handling, we create reliable interfaces that work in real-world environments. Integration with ROS 2 ensures seamless deployment on any robot platform.

## Key Takeaways

- OpenAI Whisper provides excellent speech recognition with multiple model sizes
- Audio preprocessing (denoising, normalization) improves accuracy
- Intent and entity extraction converts transcription to structured commands
- Confidence thresholding prevents unreliable action execution
- Confirmation dialogs handle ambiguous commands gracefully
- ROS 2 integration enables robot-agnostic voice control
- Real-time processing requires careful latency management
- Fallback behaviors ensure safe operation when recognition fails