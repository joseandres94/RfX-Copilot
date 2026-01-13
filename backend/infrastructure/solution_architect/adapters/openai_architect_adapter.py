import re
import logging
import openai

from ....application.solution_architect.interfaces.architect_llm_provider import ArchitectLLMProvider
from .prompt_builders.architect_prompt_builder import ArchitectPromptBuilder
from ..models.demo_brief_dto import DemoBriefDTO
from ...shared.config.settings import LLMSettings

logger = logging.getLogger(__name__)

class OpenAIArchitectAdapter(ArchitectLLMProvider):
    def __init__(self, settings: LLMSettings) -> None:
        """Initialize OpenAI architect adapter.

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

    def generate_solution(
        self,
        deal_context: dict,
        relevant_rfx_chunks: list[dict],
        knowledge_context: list[str]
    ) -> dict:
        prompt_builder = ArchitectPromptBuilder()
        system_prompt = prompt_builder.get_system_prompt()
        user_prompt = prompt_builder.get_user_prompt(
            deal_context,
            relevant_rfx_chunks,
            knowledge_context
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        # Extract JSON text from response.output (list)
        json_text = self._extract_json_text(response)
        
        # Clean JSON text (remove markdown code fences, trailing commas, etc.)
        json_text = self._clean_json_text(json_text)
        
        # Validate and parse with Pydantic
        demo_brief_dto = DemoBriefDTO.model_validate_json(json_text)
        
        # Convert to dict using Pydantic's built-in method
        return demo_brief_dto.model_dump()

    def _extract_json_text(self, response) -> str:
        """Extract JSON text from OpenAI response.output (which is a list)"""
        for output_item in response.output:
            if hasattr(output_item, 'content') and output_item.content:
                for content_item in output_item.content:
                    if hasattr(content_item, 'text'):
                        return content_item.text.strip()
        
        raise ValueError("No text content found in LLM response")

    def _clean_json_text(self, text: str) -> str:
        """Clean JSON text by removing markdown code fences and fixing common issues"""
        # Remove markdown code fences
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        
        # Remove trailing commas before closing braces/brackets
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Remove control characters (\u0000-\u001F) except \n, \r, \t which are valid in JSON strings
        # JSON allows \n, \r, \t but not other control chars like \x00, \x01, etc.
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
        