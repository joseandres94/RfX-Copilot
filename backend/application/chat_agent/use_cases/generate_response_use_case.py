from uuid import uuid4
from datetime import datetime

from ....domain.shared.repositories.chat_messages_repository import ChatMessagesRepository
from ....domain.shared.entities.chat_message import ChatMessage, Role
from ....domain.shared.entities.deal import Deal
from ....domain.shared.value_objects.session_id import SessionId
from ....domain.shared.value_objects.language import Language
from ....domain.chat_agent.repositories.audit_logger import AuditLogger
from ....domain.ingestion.entities.chunk import Chunk
from ....domain.shared.repositories.vector_db_repository import VectorDBRepository
from ....domain.shared.services.embedding_service import EmbeddingService
from ....domain.shared.repositories.deal_repository import DealRepository
from ....application.chat_agent.interfaces.chat_llm_provider import ChatLLMProvider

import logging
logger = logging.getLogger(__name__)


class GenerateResponseUseCase:
    """Use case for generating a response (summary or QA) to a user query"""
    def __init__(
        self,
        chat_repository: ChatMessagesRepository,
        embedding_service: EmbeddingService,
        vector_db_repository: VectorDBRepository,
        chat_llm_provider: ChatLLMProvider,
        audit_logger: AuditLogger
    ):
        self.chat_repository = chat_repository
        self.embedding_service = embedding_service
        self.vector_db_repository = vector_db_repository
        self.chat_llm_provider = chat_llm_provider
        self.audit_logger = audit_logger

    async def execute(
        self,
        session_id: SessionId,
        deal: Deal,
        user_query: str,
        language: Language
    ) -> ChatMessage:
        """Execute the use case"""
        
        # Validate input
        if not user_query.strip():
            raise ValueError("User query is required")
        if language not in [language.value for language in Language]:
            raise ValueError("Language is required")

        # Log audit
        self.audit_logger.log(
            event="user_query_received",
            session_id=session_id,
            payload={
                "user_query": user_query,
                "language": language
            }
        )

        # Get history messages
        history_messages = await self.chat_repository.get_history_messages(session_id)
        print(f"History messages: {history_messages}")
        
        # Create user message
        stage = "qa"
        user_message = ChatMessage(
            id=str(uuid4()),
            session_id=session_id,
            role=Role.USER,
            content=user_query,
            type="text",
            stage=stage,
            timestamp=datetime.now(),
            language=language
        )
        
        # Save user message
        await self.chat_repository.save_message(user_message)

        # Search for relevant chunks
        embedded_query = self.embedding_service.create_embeddings([Chunk(id=str(uuid4()), content=user_query, document_id=user_message.id, filename="user_query")])
        relevant_chunks_query = self.vector_db_repository.search_chunks(collection_name="RfX_documents", query=embedded_query[0].embedding)
        print(f"Relevant chunks query: {relevant_chunks_query}")

        # Get deal context
        deal_context = deal.deal_context_model_json
        relevant_rfx_chunks_ids = deal.relevant_rfx_chunks_ids
        relevant_rfx_chunks = self.vector_db_repository.get_chunks('RfX_documents', relevant_rfx_chunks_ids)
        demo_brief = deal.demo_brief_json
        gaps = deal.gaps_json

        # Generate response
        response = self.chat_llm_provider.generate_response(
            user_message,
            history_messages,
            relevant_chunks_query,
            deal_context,
            relevant_rfx_chunks,
            demo_brief,
            gaps
        )
        print(f"Response: {response}")
                
        # Create assistant message
        assistant_message = ChatMessage(
            id=str(uuid4()),
            session_id=session_id,
            role=Role.ASSISTANT,
            content=response,
            type="text",
            stage=stage,
            timestamp=datetime.now(),
            language=language
        )

        # Save assistant message
        await self.chat_repository.save_message(assistant_message)

        # Log audit
        self.audit_logger.log(
            event="response_generated",
            session_id=session_id,
            payload={
                "response": response,
                "stage": stage
            }
        )
        return assistant_message
