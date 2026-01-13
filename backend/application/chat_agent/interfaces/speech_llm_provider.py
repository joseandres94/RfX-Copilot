from abc import ABC, abstractmethod
from ....domain.shared.value_objects.language import Language

class SpeechLLMProvider(ABC):
    """Interface for speech utility from LLM providers"""
    @abstractmethod
    def stt(self, path_recording: str) -> str:
        """Call Speech-to-Text model"""
        pass

    @abstractmethod
    def tts(self, tts_text: str, language: Language) -> bytes:
        """Call Text-to-Speech model"""
        pass