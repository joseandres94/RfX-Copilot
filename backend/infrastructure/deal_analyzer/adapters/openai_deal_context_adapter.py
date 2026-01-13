import json
import re
import logging
import openai
from typing import List
from ....domain.ingestion.entities.chunk import Chunk
from ....domain.deal_analyzer.entities.deal_context import DealContext
from ....application.deal_analyzer.interfaces.deal_context_llm_provider import DealContextLLMProvider
from .prompt_builders.deal_context_prompt_builder import DealContextPromptBuilder
from ..models.deal_context_dto import DealContextDTO
from ..mappers.deal_context_mapper import DealContextMapper
from ...shared.config.settings import LLMSettings

logger = logging.getLogger(__name__)

class OpenAIDealContextAdapter(DealContextLLMProvider):
    """Adapter for OpenAI API"""

    def __init__(self, settings: LLMSettings) -> None:
        """Initialize OpenAI deal context adapter.

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

    def generate_deal_context(
        self,
        list_chunks: List[Chunk],
    ) -> tuple[DealContext, List[str]]:
        """
        Generate a deal context using the OpenAI API.
        """
        # Get system prompt and user prompt
        prompt_builder = DealContextPromptBuilder()
        system_prompt = prompt_builder.get_system_prompt(language="English")
        user_prompt = prompt_builder.get_user_prompt(list_chunks=list_chunks)

        # Call LLM
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        # Extract JSON text from response.output (list)
        json_text = self._extract_json_text(response)
        
        # Clean JSON text (remove markdown code fences, trailing commas, etc.)
        json_text = self._clean_json_text(json_text)
        
        # Validate JSON syntax first
        try:
            json.loads(json_text)
        except json.JSONDecodeError as e:
            # Log error with context
            error_pos = e.pos
            start = max(0, error_pos - 200)
            end = min(len(json_text), error_pos + 200)
            context = json_text[start:end]
            logger.error(f"Invalid JSON at position {error_pos}: {e.msg}")
            logger.error(f"Context around error:\n...{context}...")
            # Save full JSON for debugging
            try:
                import uuid
                debug_file = f"debug_json_error_{uuid.uuid4().hex[:8]}.txt"
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(json_text)
                logger.error(f"Full JSON saved to {debug_file}")
            except Exception:
                pass
            raise ValueError(f"Invalid JSON from LLM: {e.msg} at line {e.lineno}, column {e.colno}")
        
        # Validate and parse with Pydantic (automatic validation)
        deal_context_dto = DealContextDTO.model_validate_json(json_text)
        
        # Convert DTO to Domain entity
        deal_context = DealContextMapper.to_domain(deal_context_dto)
        deal_context.explicit_demo_or_poc_requests.evidence_refs

        # Get ids of relevant RFX chunks context
        relevant_rfx_chunks_ids = self._get_ids_relevant_rfx_chunks_context(deal_context)

        return deal_context, relevant_rfx_chunks_ids

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
        
        # Remove trailing commas before closing braces/brackets (common JSON error)
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Remove control characters (\u0000-\u001F) except \n, \r, \t which are valid in JSON strings
        # JSON allows \n, \r, \t but not other control chars like \x00, \x01, etc.
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text

    def _get_ids_relevant_rfx_chunks_context(self, deal_context: DealContext) -> List[str]:
        """Get the ids of the relevant RFX chunks context"""
        ids = []
        seen = set()

        def add_refs(refs):
            nonlocal ids
            for r in refs or []:
                cid = r.chunk_id
                if cid and cid not in seen:
                    seen.add(cid)
                    ids.append(cid)

        # 1) demo/poc requests
        add_refs(deal_context.explicit_demo_or_poc_requests.evidence_refs)

        # 2) eval criteria
        for c in deal_context.evaluation_and_selection.evaluation_criteria:
            add_refs(c.evidence_refs)

        # 3) must-have requirements
        for req in deal_context.requirements:
            if req.priority == "must":
                add_refs(req.evidence_refs)

        # 4) security / timeline / submission instructions
        add_refs(deal_context.security_compliance.evidence_refs)
        add_refs(deal_context.delivery_timeline.evidence_refs)
        add_refs(deal_context.document_metadata.submission_instructions.evidence_refs)

        return ids
