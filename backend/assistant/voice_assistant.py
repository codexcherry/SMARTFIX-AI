#!/usr/bin/env python
# voice_assistant.py - Voice-enabled assistant with STT and TTS capabilities
import os
import sys
import time
import logging
import threading
import queue
import json
from typing import Optional, Dict, Any

# Import the LLM assistant
from llm_assistant import LLMAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
WHISPER_MODEL_PATH = os.path.join("models", "whisper-tiny.bin")
PIPER_MODEL_DIR = os.path.join("models", "piper")

class VoiceAssistant:
    """Voice-enabled assistant with STT and TTS capabilities"""
    
    def __init__(self):
        """Initialize the voice assistant"""
        self.llm_assistant = LLMAssistant()
        self.stt_available = self._init_stt()
        self.tts_available = self._init_tts()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.wake_word_detected = threading.Event()
    
    def _init_stt(self) -> bool:
        """Initialize the speech-to-text system"""
        try:
            # Try to import whisper.cpp Python bindings
            from whisper_cpp import Whisper
            
            if not os.path.exists(WHISPER_MODEL_PATH):
                logger.warning(f"Whisper model not found at {WHISPER_MODEL_PATH}")
                logger.info("STT not available. Using text-only mode.")
                return False
            
            logger.info(f"Loading Whisper model from {WHISPER_MODEL_PATH}...")
            self.whisper = Whisper(WHISPER_MODEL_PATH)
            logger.info("Whisper model loaded successfully")
            
            # Try to import PyAudio for microphone input
            import pyaudio
            self.pyaudio = pyaudio.PyAudio()
            
            return True
        except ImportError as e:
            logger.warning(f"STT dependencies not available: {e}")
            logger.info("Install whisper_cpp and pyaudio for voice input")
            return False
        except Exception as e:
            logger.error(f"Error initializing STT: {e}")
            return False
    
    def _init_tts(self) -> bool:
        """Initialize the text-to-speech system"""
        try:
            # Try to import piper TTS
            from piper import PiperVoice
            
            if not os.path.exists(PIPER_MODEL_DIR):
                logger.warning(f"Piper models not found at {PIPER_MODEL_DIR}")
                logger.info("TTS not available. Using text-only mode.")
                return False
            
            # Find available voice models
            voice_files = [f for f in os.listdir(PIPER_MODEL_DIR) 
                          if f.endswith('.onnx')]
            
            if not voice_files:
                logger.warning("No Piper voice models found")
                return False
            
            # Use the first available voice
            voice_path = os.path.join(PIPER_MODEL_DIR, voice_files[0])
            config_path = voice_path.replace('.onnx', '.json')
            
            if not os.path.exists(config_path):
                logger.warning(f"Voice config not found: {config_path}")
                return False
            
            logger.info(f"Loading Piper TTS voice: {voice_files[0]}...")
            self.piper = PiperVoice(voice_path, config_path)
            logger.info("Piper TTS loaded successfully")
            
            return True
        except ImportError:
            logger.warning("Piper TTS not available")
            logger.info("Install piper-tts for voice output")
            return False
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            return False
    
    def _init_wake_word(self) -> bool:
        """Initialize the wake word detection system"""
        try:
            import openwakeword
            
            logger.info("Loading wake word models...")
            self.wake_word_detector = openwakeword.Model(
                wakeword_models=["hey_jarvis"]
            )
            logger.info("Wake word detection ready")
            
            return True
        except ImportError:
            logger.warning("Wake word detection not available")
            logger.info("Install openwakeword for wake word detection")
            return False
        except Exception as e:
            logger.error(f"Error initializing wake word detection: {e}")
            return False
    
    def listen(self) -> Optional[str]:
        """Listen for speech and convert to text"""
        if not self.stt_available:
            logger.error("STT not available")
            return None
        
        try:
            import pyaudio
            import numpy as np
            
            logger.info("Listening...")
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            RECORD_SECONDS = 5
            
            stream = self.pyaudio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Convert audio data to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            
            # Transcribe audio
            result = self.whisper.transcribe(audio_data)
            
            if result:
                logger.info(f"Transcribed: {result}")
                return result
            else:
                logger.info("No speech detected")
                return None
            
        except Exception as e:
            logger.error(f"Error listening: {e}")
            return None
    
    def speak(self, text: str) -> bool:
        """Convert text to speech and play it"""
        if not self.tts_available:
            logger.error("TTS not available")
            return False
        
        try:
            import sounddevice as sd
            import numpy as np
            
            logger.info(f"Speaking: {text[:50]}...")
            
            # Generate audio from text
            audio_data = self.piper(text)
            
            # Play audio
            sd.play(audio_data, self.piper.sample_rate)
            sd.wait()
            
            return True
        except Exception as e:
            logger.error(f"Error speaking: {e}")
            return False
    
    def run_voice_mode(self):
        """Run the assistant in voice mode"""
        if not self.stt_available:
            logger.error("STT not available. Cannot run in voice mode.")
            return
        
        print("\n" + "="*50)
        print("SmartFix AI Voice Assistant")
        print("="*50)
        print("Press Enter to start listening, or type 'exit' to quit")
        print("="*50 + "\n")
        
        while True:
            input("Press Enter to start listening...")
            
            # Listen for speech
            query = self.listen()
            
            if not query:
                print("I didn't catch that. Please try again.")
                continue
            
            print(f"\nYou: {query}")
            
            # Process query
            answer = self.llm_assistant.process_query(query)
            
            print(f"\nAssistant: {answer}")
            
            # Speak the answer
            if self.tts_available:
                self.speak(answer)
    
    def run_text_mode(self):
        """Run the assistant in text mode"""
        print("\n" + "="*50)
        print("SmartFix AI Troubleshooting Assistant")
        print("="*50)
        if self.llm_assistant.llm_available:
            print("Running with local LLM for enhanced responses")
        else:
            print("Running in RAG-only mode (no LLM)")
        print("Ask a troubleshooting question (type 'exit' to quit)")
        print("="*50 + "\n")
        
        while True:
            query = input("\nYou: ").strip()
            if query.lower() in ("exit", "quit", "bye"):
                print("\nThank you for using SmartFix AI. Goodbye!")
                break
            
            if not query:
                continue
            
            answer = self.llm_assistant.process_query(query)
            print("\nAssistant:\n" + answer)

def main():
    """Main function to run the voice assistant"""
    assistant = VoiceAssistant()
    
    if assistant.stt_available and assistant.tts_available:
        assistant.run_voice_mode()
    else:
        logger.info("Voice capabilities not available. Running in text mode.")
        assistant.run_text_mode()

if __name__ == "__main__":
    main()
