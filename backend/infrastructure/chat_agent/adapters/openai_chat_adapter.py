import openai
from typing import List
from ....domain.shared.entities.chat_message import ChatMessage
from ....domain.ingestion.entities.chunk import Chunk
from ....application.chat_agent.interfaces.chat_llm_provider import ChatLLMProvider
from .prompt_builders.chat_prompt_builder import ChatPromptBuilder
from ...shared.config.settings import LLMSettings


class OpenAIChatAdapter(ChatLLMProvider):
    """Adapter for OpenAI API"""

    def __init__(self, settings: LLMSettings) -> None:
        """Initialize OpenAI chat adapter.

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

    def generate_response(
        self,
        chat_message: ChatMessage,
        history_messages: List[ChatMessage],
        relevant_chunks_query: List[Chunk],
        deal_context: dict,
        relevant_rfx_chunks: List[Chunk],
        demo_brief: dict,
        gaps: dict,
    ) -> str:
        """Generate a response to a user query using the OpenAI API"""
        # Get history messages
        history = "\n".join([f"{message.role.value}: {message.content}" for message in history_messages])
        # Get relevant chunks
        relevant_rfx_chunks_context = self._build_relevant_chunks_message(relevant_rfx_chunks)
        relevant_chunks_query_context = self._build_relevant_chunks_message(relevant_chunks_query)

        # Get system prompt and user prompt
        prompt_builder = ChatPromptBuilder()
        system_prompt = prompt_builder.get_system_prompt(chat_message.language)
        user_prompt = prompt_builder.get_user_prompt(
            question=chat_message.content,
            deal_context=deal_context,
            relevant_rfx_chunks_context=relevant_rfx_chunks_context,
            relevant_chunks_query_context=relevant_chunks_query_context,
            demo_brief_context=demo_brief,
            gaps_context=gaps,
            history_messages=history,
        )

        # Call LLM
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )
        return response.output_text

    def _build_relevant_chunks_message(self, chunks: List[Chunk]) -> str:
        """Build the relevant chunks query context"""
        context = ""
        for chunk in chunks:
            context += f"Chunk ID: {chunk.id}\nChunk Content: {chunk.content}\n"
        return context
