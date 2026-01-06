"""
Piper TTS integration with streaming sentence support.
"""

import queue
import threading
import numpy as np
import sounddevice as sd
from pathlib import Path

from config import (
    TTS_VOICE_MODEL, TTS_MODEL_URL, TTS_CONFIG_URL,
    GRAY, RESET, CYAN
)

# Lazy import requests to avoid circular imports
import requests
http_session = requests.Session()


class PiperTTS:
    """Lightweight Piper TTS wrapper with streaming sentence support."""
    
    def __init__(self):
        self.enabled = False
        self.voice = None
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        self.interrupt_event = threading.Event()
        self.models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        
        try:
            from piper import PiperVoice
            self.PiperVoice = PiperVoice
            self.available = True
        except ImportError:
            self.available = False
            print(f"{GRAY}[TTS] piper-tts not installed. Run: pip install piper-tts{RESET}")
    
    def download_model(self):
        """Download voice model if not present."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        model_path = self.models_dir / f"{TTS_VOICE_MODEL}.onnx"
        config_path = self.models_dir / f"{TTS_VOICE_MODEL}.onnx.json"
        
        if not model_path.exists():
            print(f"{CYAN}[TTS] Downloading voice model ({TTS_VOICE_MODEL})...{RESET}")
            r = http_session.get(TTS_MODEL_URL, stream=True)
            r.raise_for_status()
            with open(model_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            r = http_session.get(TTS_CONFIG_URL)
            r.raise_for_status()
            with open(config_path, 'wb') as f:
                f.write(r.content)
            print(f"{CYAN}[TTS] Model downloaded!{RESET}")
        
        return str(model_path), str(config_path)
    
    def initialize(self):
        """Load the voice model."""
        if not self.available:
            return False
        
        try:
            model_path, config_path = self.download_model()
            self.voice = self.PiperVoice.load(model_path, config_path)
            self.running = True
            self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.worker_thread.start()
            return True
        except Exception as e:
            print(f"{GRAY}[TTS] Failed to initialize: {e}{RESET}")
            return False
    
    def _speech_worker(self):
        """Background thread that plays queued sentences."""
        while self.running:
            try:
                # Check for interrupt before getting next sentence
                if self.interrupt_event.is_set():
                    self.interrupt_event.clear()
                
                text = self.speech_queue.get(timeout=0.5)
                if text is None:
                    break
                
                # Check again
                if self.interrupt_event.is_set():
                    self.speech_queue.task_done()
                    continue

                self._speak_text(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
    
    def _speak_text(self, text):
        """Synthesize and play text using sounddevice streaming."""
        if not self.voice or not text.strip():
            return
        
        try:
            sample_rate = self.voice.config.sample_rate
            
            # Stream audio directly to output device
            with sd.OutputStream(samplerate=sample_rate, channels=1, dtype='int16', latency='low') as stream:
                self.current_stream = stream
                for audio_chunk in self.voice.synthesize(text):
                    if self.interrupt_event.is_set():
                        stream.abort()  # Instant stop
                        break 
                    data = np.frombuffer(audio_chunk.audio_int16_bytes, dtype=np.int16)
                    stream.write(data)
                self.current_stream = None
                    
        except Exception as e:
            print(f"{GRAY}[TTS Error]: {e}{RESET}")
    
    def queue_sentence(self, sentence):
        """Add a sentence to the speech queue."""
        if self.enabled and self.voice and sentence.strip():
            self.speech_queue.put(sentence)
            
    def stop(self):
        """Interrupt current speech and clear queue."""
        self.interrupt_event.set()
        # Clear queue safely
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()
        # Abort active stream
        if hasattr(self, 'current_stream') and self.current_stream:
            try:
                self.current_stream.abort()
            except:
                pass
            
    def wait_for_completion(self):
        """Wait for all queued speech to finish."""
        if self.enabled:
            self.speech_queue.join()
    
    def toggle(self, enable):
        """Enable/disable TTS."""
        if enable and not self.voice:
            if self.initialize():
                self.enabled = True
                return True
            return False
        self.enabled = enable
        return True
    
    def shutdown(self):
        """Clean up resources."""
        self.running = False
        self.stop()
        self.speech_queue.put(None)


class SentenceBuffer:
    """Buffers streaming text and extracts complete sentences."""
    
    import re
    SENTENCE_ENDINGS = re.compile(r'([.!?])\s+|([.!?])$')
    
    def __init__(self):
        self.buffer = ""
    
    def add(self, text):
        """Add text chunk and return any complete sentences."""
        self.buffer += text
        sentences = []
        
        while True:
            match = self.SENTENCE_ENDINGS.search(self.buffer)
            if match:
                end_pos = match.end()
                sentence = self.buffer[:end_pos].strip()
                if sentence:
                    sentences.append(sentence)
                self.buffer = self.buffer[end_pos:]
            else:
                break
        
        return sentences
    
    def flush(self):
        """Return any remaining text as a final sentence."""
        remaining = self.buffer.strip()
        self.buffer = ""
        return remaining if remaining else None


# Global TTS instance
tts = PiperTTS()
