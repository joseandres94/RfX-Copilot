import openai
from ....application.summarizer_agent.interfaces.summarizer_llm_provider import SummarizerLLMProvider
from .prompt_builders.summary_prompt_buildler import SummaryPromptBuilder
from ...shared.config.settings import LLMSettings

class OpenAISummarizerAdapter(SummarizerLLMProvider):
    """Adapter for OpenAI API"""

    def __init__(self, settings: LLMSettings) -> None:
        """Initialize OpenAI summarizer adapter.

        Args:
            settings: LLM configuration settings

        Raises:
            ValueError: If OpenAI API key is not provided
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI()

    def generate_summary(self, deal_context: dict) -> str:
        """Generate a DIC in markdown format"""
        prompt_builder = SummaryPromptBuilder()
        system_prompt = prompt_builder.get_system_prompt()
        user_prompt = prompt_builder.get_user_prompt(deal_context)

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt
        )
        return response.output_text
