import os
import tempfile
from pathlib import Path

from ....domain.shared.value_objects.language import Language
from ....application.chat_agent.interfaces.speech_llm_provider import SpeechLLMProvider

import logging
logger = logging.getLogger(__name__)


class SpeechUseCase:
    """Use case for generating voice from text"""
    def __init__(self, speech_llm_provider: SpeechLLMProvider):
        self.speech_llm_provider = speech_llm_provider

    def execute_stt(self, audio_file: bytes, filename: str) -> str:
        """Transcribe audio to text"""
        # Save to temp file
        suffix = Path(filename or "audio.wav").suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_file)
            tmp.flush()

        try:
            # Transcribe audio to text
            transcription = self.speech_llm_provider.stt(tmp.name)
            return transcription
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            raise Exception("Failed to transcribe audio.")
        finally:
            os.unlink(tmp.name)

    def execute_tts(self, text_message: str, language: Language) -> bytes:
        """Generate voice from text"""
        audio = self.speech_llm_provider.tts(text_message=text_message, language=language)
        return audio