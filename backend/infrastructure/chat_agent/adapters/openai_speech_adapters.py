import openai

from backend.infrastructure.chat_agent.adapters.prompt_builders.speech_prompt_builder import SpeechPromptBuilder
from ....domain.shared.value_objects.language import Language
from ....application.chat_agent.interfaces.speech_llm_provider import SpeechLLMProvider
from .prompt_builders.speech_prompt_builder import SpeechPromptBuilder
from ...shared.config.settings import LLMSettings


class OpenAISpeechAdapter(SpeechLLMProvider):
    """Adapter for OpenAI API"""

    def __init__(self, settings: LLMSettings) -> None:
        """Initialize OpenAI speech adapter.

        Args:
            settings: LLM configuration settings

        Raises:
            ValueError: If OpenAI API key is not provided
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.api_key = settings.openai_api_key
        self.model_stt = settings.openai_model_stt
        self.model_tts = settings.openai_model_tts

        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI()

    def stt(self, path_recording: str) -> str:
        """Call Speech-to-Text model"""
        with open(path_recording, "rb") as audio_file:
            # Call STT model
            transcription = self.client.audio.transcriptions.create(
                model=self.model_stt,
                file=audio_file
            )
            return transcription.text if transcription else ""

    def tts(self, text_message: str, language: Language) -> bytes:
        """Call Text-to-Speech model"""
        prompt_builder = SpeechPromptBuilder()
        audio = self.client.audio.speech.create(
            model=self.model_tts,
            voice="ash",
            input=text_message,
            instructions = prompt_builder.get_system_prompt_tts(language),
            response_format = "wav"
        )
        return audio.content
