from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.chat_agent.adapters.openai_speech_adapters import OpenAISpeechAdapter
from backend.infrastructure.shared.config.settings import LLMSettings
from ..domain.chat_agent.repositories.consent_repository import ConsentRepository
from ..domain.chat_agent.repositories.audit_logger import AuditLogger
from ..domain.chat_agent.services.summary_parser import SummaryParser
from ..domain.ingestion.services.document_parser import DocumentParser
from ..domain.ingestion.repositories.document_repository import DocumentRepository
from ..domain.shared.repositories.chat_messages_repository import ChatMessagesRepository
from ..domain.shared.repositories.vector_db_repository import VectorDBRepository
from ..domain.ingestion.services.document_chunker import DocumentChunker
from ..domain.shared.services.embedding_service import EmbeddingService
from ..application.ingestion.use_cases.ingest_document_use_case import IngestDocumentUseCase
from ..application.chat_agent.use_cases.generate_response_use_case import GenerateResponseUseCase
from ..application.chat_agent.use_cases.save_consent_use_case import SaveConsentUseCase
from ..application.chat_agent.use_cases.speech_use_case import SpeechUseCase
from ..application.summarizer_agent.use_cases.generate_summary_use_case import GenerateSummaryUseCase
from ..application.solution_architect.use_cases.generate_demo_spec_use_case import GenerateDemoSpecUseCase
from ..application.chat_agent.interfaces.chat_llm_provider import ChatLLMProvider
from ..application.chat_agent.interfaces.speech_llm_provider import SpeechLLMProvider
from ..application.summarizer_agent.interfaces.summarizer_llm_provider import SummarizerLLMProvider
from ..application.solution_architect.interfaces.architect_llm_provider import ArchitectLLMProvider
from ..infrastructure.chat_agent.persistence.sql_chat_repository import SQLChatRepository
from ..infrastructure.chat_agent.persistence.file_consent_repository import FileConsentRepository
from ..infrastructure.chat_agent.persistence.audit_logger_repository import AuditLoggerRepository
from ..infrastructure.shared.persistence.file_document_repository import FileDocumentRepository
from ..infrastructure.chat_agent.adapters.openai_chat_adapter import OpenAIChatAdapter
from ..infrastructure.summarizer_agent.adapters.openai_summarizer_adapter import OpenAISummarizerAdapter
from ..infrastructure.ingestion.adapters.pdf_parser import PDFParser
from ..infrastructure.ingestion.adapters.docx_parser import DOCXParser
from ..infrastructure.ingestion.adapters.txt_parser import TXTParser
from ..infrastructure.ingestion.adapters.document_parser_service import DocumentParserService
from ..infrastructure.shared.persistence.chromadb_repository import ChromaDBRepository
from ..infrastructure.shared.services.langchain_document_chunker import LangchainDocumentChunker
from ..infrastructure.shared.services.openai_embedding_service import OpenAIEmbeddingService
from ..dependencies import get_db_session
from ..application.deal_analyzer.use_cases.generate_deal_context_use_case import GenerateDealContextUseCase
from ..application.deal_analyzer.interfaces.deal_context_llm_provider import DealContextLLMProvider
from ..infrastructure.deal_analyzer.adapters.openai_deal_context_adapter import OpenAIDealContextAdapter
from ..infrastructure.engagement_manager.adapters.openai_engagement_adapter import OpenAIEngagementAdapter
from ..application.engagement_manager.interfaces.engagement_llm_provider import EngagementLLMProvider
from ..application.engagement_manager.use_cases.analyze_gaps_use_case import AnalyzeGapsUseCase
from ..domain.shared.repositories.deal_repository import DealRepository
from ..domain.shared.repositories.event_store import EventStore
from ..infrastructure.shared.persistence.file_deal_repository import FileDealRepository
from ..infrastructure.shared.persistence.in_memory_event_store import InMemoryEventStore
from ..application.pipeline.pipeline_runner import PipelineRunner
from ..dependencies import get_llm_settings


# Repositories
def get_chat_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> ChatMessagesRepository:
    """Dependency to get the chat repository"""
    return SQLChatRepository(db_session=db_session)

def get_vector_db_repository() -> VectorDBRepository:
    """Dependency to get the vector DB repository"""
    return ChromaDBRepository()

def get_deal_context_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> DealContextLLMProvider:
    """Dependency to get the deal context LLM provider"""
    return OpenAIDealContextAdapter(llm_settings)

def get_summarizer_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> SummarizerLLMProvider:
    """Dependency to get the LLM provider"""
    return OpenAISummarizerAdapter(llm_settings)

def get_chat_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> ChatLLMProvider:
    """Dependency to get the LLM provider"""
    return OpenAIChatAdapter(llm_settings)

def get_speech_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> SpeechLLMProvider:
    return OpenAISpeechAdapter(llm_settings)

def get_summary_parser() -> SummaryParser:
    """Dependency to get the summary parser"""
    return SummaryParser()

def get_consent_repository() -> ConsentRepository:
    """Dependency to get the consent repository"""
    return FileConsentRepository()

def get_audit_logger() -> AuditLoggerRepository:
    """Dependency to get the audit logger"""
    return AuditLoggerRepository()

def get_pdf_parser() -> PDFParser:
    """Dependency to get the PDF parser"""
    return PDFParser()

def get_docx_parser() -> DOCXParser:
    """Dependency to get the DOCX parser"""
    return DOCXParser()

def get_txt_parser() -> TXTParser:
    """Dependency to get the TXT parser"""
    return TXTParser()

def get_document_parser(
    pdf_parser: Annotated[PDFParser, Depends(get_pdf_parser)],
    docx_parser: Annotated[DOCXParser, Depends(get_docx_parser)],
    txt_parser: Annotated[TXTParser, Depends(get_txt_parser)],
) -> DocumentParserService:
    """Dependency to get the document parser"""
    return DocumentParserService(
        pdf_parser=pdf_parser,
        docx_parser=docx_parser,
        txt_parser=txt_parser
    )

def get_document_chunker() -> DocumentChunker:
    """Dependency to get the document chunker"""
    return LangchainDocumentChunker()

def get_embedding_service(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> EmbeddingService:
    """Dependency to get the embedding service"""
    return OpenAIEmbeddingService(llm_settings)

def get_document_repository() -> DocumentRepository:
    """Dependency to get the document repository"""
    return FileDocumentRepository()

def get_deal_repository() -> DealRepository:
    """Dependency to get the deal repository"""
    return FileDealRepository()

def get_event_store() -> EventStore:
    """Dependency to get the event store"""
    # Singleton para mantener eventos en memoria durante la sesión
    # En producción, esto debería ser Redis o una base de datos
    if not hasattr(get_event_store, "_instance"):
        get_event_store._instance = InMemoryEventStore()
    return get_event_store._instance

def get_engagement_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> EngagementLLMProvider:
    """Dependency to get the engagement manager LLM provider"""
    return OpenAIEngagementAdapter(llm_settings)

def get_architect_llm_provider(
    llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]
) -> ArchitectLLMProvider:
    """Dependency to get the architect LLM provider"""
    from ..infrastructure.solution_architect.adapters.openai_architect_adapter import OpenAIArchitectAdapter
    return OpenAIArchitectAdapter(llm_settings)

# Use cases
def get_ingest_document_uc(
    document_parser: Annotated[DocumentParser, Depends(get_document_parser)],
    document_chunker: Annotated[DocumentChunker, Depends(get_document_chunker)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_db_repository: Annotated[VectorDBRepository, Depends(get_vector_db_repository)],
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> IngestDocumentUseCase:
    """Dependency to get the ingestion use case"""
    return IngestDocumentUseCase(
        document_parser=document_parser,
        document_chunker=document_chunker,
        embedding_service=embedding_service,
        vector_db_repository=vector_db_repository,
        document_repository=document_repository,
    )

def get_generate_deal_context_uc(
    deal_context_llm_provider: Annotated[DealContextLLMProvider, Depends(get_deal_context_llm_provider)],
) -> GenerateDealContextUseCase:
    """Dependency to get the generate deal context use case"""
    return GenerateDealContextUseCase(
        deal_context_llm_provider=deal_context_llm_provider,
    )

def get_generate_summary_uc(
    summarizer_llm_provider: Annotated[SummarizerLLMProvider, Depends(get_summarizer_llm_provider)],
) -> GenerateSummaryUseCase:
    """Dependency to get the generate summary use case"""
    return GenerateSummaryUseCase(
        summarizer_llm_provider=summarizer_llm_provider,
    )

def get_generate_demo_spec_uc(
    vector_db_repository: Annotated[VectorDBRepository, Depends(get_vector_db_repository)],
    architect_llm_provider: Annotated[ArchitectLLMProvider, Depends(get_architect_llm_provider)],
)-> GenerateDemoSpecUseCase:
    """Dependency to get the generate demo spec use case"""
    return GenerateDemoSpecUseCase(
        vector_db_repository=vector_db_repository,
        architect_llm_provider=architect_llm_provider
    )

def get_generate_response_uc(
    chat_repository: Annotated[ChatMessagesRepository, Depends(get_chat_repository)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    vector_db_repository: Annotated[VectorDBRepository, Depends(get_vector_db_repository)],
    chat_llm_provider: Annotated[ChatLLMProvider, Depends(get_chat_llm_provider)],
    audit_logger: Annotated[AuditLogger, Depends(get_audit_logger)]
) -> GenerateResponseUseCase:
    """Dependency to get the generate response use case"""
    return GenerateResponseUseCase(
        chat_repository=chat_repository,
        embedding_service=embedding_service,
        vector_db_repository=vector_db_repository,
        chat_llm_provider=chat_llm_provider,
        audit_logger=audit_logger
    )

def get_save_consent_uc(
    consent_repository: Annotated[ConsentRepository, Depends(get_consent_repository)],
    audit_logger: Annotated[AuditLogger, Depends(get_audit_logger)]
) -> SaveConsentUseCase:
    """Dependency to get the save consent use case"""
    return SaveConsentUseCase(
        consent_repository=consent_repository,
        audit_logger=audit_logger
    )

def get_speech_uc(
    speech_llm_provider: Annotated[SpeechLLMProvider, Depends(get_speech_llm_provider)]
) -> SpeechUseCase:
    """Dependency to get the Speech use case"""
    return SpeechUseCase(speech_llm_provider=speech_llm_provider)

def get_analyze_gaps_uc(
    vector_db_repository: Annotated[VectorDBRepository, Depends(get_vector_db_repository)],
    engagement_llm_provider: Annotated[EngagementLLMProvider, Depends(get_engagement_llm_provider)]
) -> AnalyzeGapsUseCase:
    """Dependency to get the analyze gaps use case"""
    return AnalyzeGapsUseCase(vector_db_repository=vector_db_repository, engagement_llm_provider=engagement_llm_provider)

def get_pipeline_runner(
    deal_repository: Annotated[DealRepository, Depends(get_deal_repository)],
    event_store: Annotated[EventStore, Depends(get_event_store)],
    ingest_document_uc: Annotated[IngestDocumentUseCase, Depends(get_ingest_document_uc)],
    generate_deal_context_uc: Annotated[GenerateDealContextUseCase, Depends(get_generate_deal_context_uc)],
    generate_summary_uc: Annotated[GenerateSummaryUseCase, Depends(get_generate_summary_uc)],
    generate_demo_spec_uc: Annotated[GenerateDemoSpecUseCase, Depends(get_generate_demo_spec_uc)],
    analyze_gaps_uc: Annotated[AnalyzeGapsUseCase, Depends(get_analyze_gaps_uc)],
) -> PipelineRunner:
    """
    Dependency to get the pipeline runner.
    
    El PipelineRunner recibe Use Cases (no providers) para respetar Clean Architecture.
    Cada Use Case encapsula su lógica de negocio y maneja sus propias dependencias.
    """
    return PipelineRunner(
        deal_repository=deal_repository,
        event_store=event_store,
        ingest_document_uc=ingest_document_uc,
        generate_deal_context_uc=generate_deal_context_uc,
        generate_summary_uc=generate_summary_uc,
        generate_demo_spec_uc=generate_demo_spec_uc,
        analyze_gaps_uc=analyze_gaps_uc,
    )