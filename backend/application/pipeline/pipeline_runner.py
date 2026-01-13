import logging
import traceback
from datetime import datetime
from typing import Optional, List

from ...domain.shared.entities.deal import Deal, DealStatus, PipelineStep
from ...domain.ingestion.entities.chunk import Chunk
from ...domain.shared.entities.pipeline_event import PipelineEvent, EventType
from ...domain.shared.repositories.deal_repository import DealRepository
from ...domain.shared.repositories.event_store import EventStore
from ...domain.shared.value_objects.session_id import SessionId
from ...application.ingestion.use_cases.ingest_document_use_case import IngestDocumentUseCase
from ...application.deal_analyzer.use_cases.generate_deal_context_use_case import GenerateDealContextUseCase
from ...application.summarizer_agent.use_cases.generate_summary_use_case import GenerateSummaryUseCase
from ...application.solution_architect.use_cases.generate_demo_spec_use_case import GenerateDemoSpecUseCase
from ...application.engagement_manager.use_cases.analyze_gaps_use_case import AnalyzeGapsUseCase

logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Orchestrator for the sequential RfX processing pipeline.
    
    Pipeline: Ingestion → Deal Analyzer → Summarizer → Solution Architect → Engagement Manager
    """
    
    def __init__(
        self,
        deal_repository: DealRepository,
        event_store: EventStore,
        ingest_document_uc: IngestDocumentUseCase,
        generate_deal_context_uc: GenerateDealContextUseCase,
        generate_summary_uc: GenerateSummaryUseCase,
        generate_demo_spec_uc: GenerateDemoSpecUseCase,
        analyze_gaps_uc: AnalyzeGapsUseCase,
    ):
        self.deal_repository = deal_repository
        self.event_store = event_store
        self.ingest_document_uc = ingest_document_uc
        self.generate_deal_context_uc = generate_deal_context_uc
        self.generate_summary_uc = generate_summary_uc
        self.generate_demo_spec_uc = generate_demo_spec_uc
        self.analyze_gaps_uc = analyze_gaps_uc
    
    async def run_pipeline(self, deal_id: str, file_content: bytes) -> None:
        """
        Runs the complete pipeline for a deal, orchestrating the Use Cases.
        
        Args:
            deal_id: ID of the deal to process
            file_content: Content of the RfX file
        """
        try:
            # Retrieve deal
            deal = self.deal_repository.get(deal_id)
            if not deal:
                logger.error(f"Deal {deal_id} not found")
                return

            # Create a unique session_id for this deal
            session_id = SessionId(deal_id)
            
            logger.info(f"Starting pipeline for deal {deal_id}")
            self._emit_event(deal_id, EventType.INFO, PipelineStep.INGESTION.value, 
                           "🟦 Starting RfX processing...")
            
            # Step 1: Document Ingestion
            document = self._run_ingestion(deal, file_content)
            if not document:
                return  # Error already handled
            
            # Step 2: Deal Analyzer
            deal_context = self._run_deal_analyzer(deal, document)
            if not deal_context:
                return  # Error already handled
            
            # Step 3: Summarizer
            dic_markdown = self._run_summarizer(deal, deal_context)
            if not dic_markdown:
                return  # Error already handled
            
            # Step 4: Solution Architect
            demo_result = self._run_solution_architect(deal, deal_context)
            if not demo_result:
                return  # Error already handled
            
            # Step 5: Gap Analysis
            gaps_result = self._run_engagement_manager(deal, deal_context, demo_result["demo_brief_json"])
            if not gaps_result:
                return  # Error already handled
            
            # Finalize pipeline
            deal.status = DealStatus.READY
            deal.current_step = PipelineStep.COMPLETED
            self.deal_repository.save(deal)
            
            self._emit_event(
                deal_id, 
                EventType.INFO, 
                PipelineStep.COMPLETED.value,
                "✅ Pipeline completed - You can chat with the copilot now!"
            )
            
            logger.info(f"Pipeline completed successfully for deal {deal_id}")
            
        except Exception as e:
            logger.error(f"Unexpected error in pipeline for deal {deal_id}: {e}", exc_info=True)
            self._handle_error(deal_id, PipelineStep.INGESTION, str(e), traceback.format_exc())
    
    def _run_ingestion(self, deal: Deal, file_content: bytes) -> List[Chunk]:
        """
        Step 1: Ingestion
        
        Uses IngestDocumentUseCase to parse the document, chunk and embed it, and save it to the vector database.
        """
        try:
            # Create session
            #await self.chat_repository.create_session(session_id, language)
            
            deal.current_step = PipelineStep.INGESTION
            self.deal_repository.save(deal)
            
            self._emit_event(deal.id, EventType.INFO, PipelineStep.INGESTION.value,
                           "📄 Parsing document...")

            list_chunks = self.ingest_document_uc.execute(
                deal_id=deal.id,
                file_content=file_content,
                filename=deal.filename,
                collection_name="RfX_documents"
            )
            
            deal.document_id = deal.id
            self.deal_repository.save(deal)
            
            # Emit ingestion success event
            self._emit_event(deal.id, EventType.RESULT, PipelineStep.INGESTION.value,
                           "✅ Document parsed and processed")
            
            return list_chunks
            
        except Exception as e:
            logger.error(f"Error in ingestion step: {e}", exc_info=True)
            self._handle_error(deal.id, PipelineStep.INGESTION, str(e), traceback.format_exc())
            return None
    
    def _run_deal_analyzer(self, deal: Deal, list_chunks: List[Chunk]) -> Optional[dict]:
        """
        Step 2: Deal Analyzer
        
        Uses GenerateDealContextUseCase to generate the deal context.
        """
        try:
            deal.current_step = PipelineStep.DEAL_ANALYZER
            self.deal_repository.save(deal)
            
            self._emit_event(deal.id, EventType.INFO, PipelineStep.DEAL_ANALYZER.value,
                           "🔍 Extracting Deal Intelligence Card...")

            deal.deal_context_model_json, deal.relevant_rfx_chunks_ids = self.generate_deal_context_uc.execute(
                list_chunks=list_chunks,
            )

            # Save deal context to the database
            self.deal_repository.save(deal)
            
            # Extract stats for the message
            num_requirements = len(deal.deal_context_model_json.get("requirements", []))
            customer_name = deal.deal_context_model_json.get("document_metadata", {}).get("customer_name", "N/A")
            
            self._emit_event(
                deal.id, 
                EventType.RESULT, 
                PipelineStep.DEAL_ANALYZER.value,
                f"✅ Deal Intelligence Card generated: {num_requirements} requirements identified for {customer_name}",
                payload={"num_requirements": num_requirements, "customer": customer_name}
            )
            
            return deal.deal_context_model_json
            
        except Exception as e:
            logger.error(f"Error in deal analyzer step: {e}", exc_info=True)
            self._handle_error(deal.id, PipelineStep.DEAL_ANALYZER, str(e), traceback.format_exc())
            return None
    
    def _run_summarizer(self, deal: Deal, deal_context: dict) -> Optional[str]:
        """
        Step 3: Summarizer - Generate DIC
        
        Uses GenerateSummaryUseCase to create the summary.
        """
        try:
            deal.current_step = PipelineStep.SUMMARIZER
            self.deal_repository.save(deal)
            
            self._emit_event(deal.id, EventType.INFO, PipelineStep.SUMMARIZER.value,
                           "📝 Generating executive summary (DIC)...")
            
            # Use the use case to generate the summary
            deal.dic_markdown = self.generate_summary_uc.execute(
                deal_context=deal_context,
            )
            
            # Save the DIC to the database
            self.deal_repository.save(deal)
            
            self._emit_event(
                deal.id, 
                EventType.RESULT, 
                PipelineStep.SUMMARIZER.value,
                "✅ DIC (Deal Intelligence Card) generated"
            )
            
            return deal.dic_markdown
            
        except Exception as e:
            logger.error(f"Error in summarizer step: {e}", exc_info=True)
            self._handle_error(deal.id, PipelineStep.SUMMARIZER, str(e), traceback.format_exc())
            return None
    
    def _run_solution_architect(self, deal: Deal, deal_context: dict) -> Optional[dict]:
        """
        Step 4: Solution Architect - Generate Demo Brief
        
        Uses GenerateDemoSpecUseCase to generate the proposed solution.
        """
        try:
            deal.current_step = PipelineStep.SOLUTION_ARCHITECT
            self.deal_repository.save(deal)
            
            self._emit_event(deal.id, EventType.INFO, PipelineStep.SOLUTION_ARCHITECT.value,
                           "🏗️ Designing demo proposal...")
            
            # Use the use case to generate the demo spec
            # The use case fetches the summary from the chat history and creates the proposal
            demo_brief_markdown, demo_brief_spec = self.generate_demo_spec_uc.execute(deal_context, deal.relevant_rfx_chunks_ids)
            
            # Save the demo brief
            deal.demo_brief_markdown = demo_brief_markdown
            deal.demo_brief_json = demo_brief_spec
            self.deal_repository.save(deal)
            
            self._emit_event(
                deal.id, 
                EventType.RESULT, 
                PipelineStep.SOLUTION_ARCHITECT.value,
                "✅ Demo Brief generated"
            )
            
            return {
                "demo_brief_markdown": demo_brief_markdown,
                "demo_brief_json": deal.demo_brief_json
            }
            
        except Exception as e:
            logger.error(f"Error in solution architect step: {e}", exc_info=True)
            self._handle_error(deal.id, PipelineStep.SOLUTION_ARCHITECT, str(e), traceback.format_exc())
            return None
    
    def _run_engagement_manager(self, deal: Deal, deal_context: dict, demo_brief_spec: dict) -> Optional[dict]:
        """
        Step 5: Engagement Manager - Analyze gaps
        
        Uses AnalyzeGapsUseCase to analyze gaps between requirements and solution.
        """
        try:
            deal.current_step = PipelineStep.ENGAGEMENT_MANAGER
            self.deal_repository.save(deal)
            
            self._emit_event(deal.id, EventType.INFO, PipelineStep.ENGAGEMENT_MANAGER.value,
                           "🎯 Analyzing gaps and risks...")
            
            # Use the use case to analyze gaps
            gap_analysis_markdown, gap_analysis_spec = self.analyze_gaps_uc.execute(
                deal_context=deal_context,
                relevant_rfx_chunks_ids=deal.relevant_rfx_chunks_ids,
                demo_brief_spec=demo_brief_spec
            )
            
            # Save results
            deal.gaps_markdown = gap_analysis_markdown
            deal.gaps_json = gap_analysis_spec
            self.deal_repository.save(deal)
            
            # Extract stats for the message from actual gap_analysis_spec structure
            gaps = gap_analysis_spec.get("gaps", [])
            total_gaps = len(gaps)
            high_severity_gaps = len([g for g in gaps if g.get("severity") == "high"])
            
            if high_severity_gaps > 0:
                message = f"⚠️ Gap analysis completed: {total_gaps} gaps identified ({high_severity_gaps} high severity)"
            elif total_gaps > 0:
                message = f"✅ Gap analysis completed: {total_gaps} gaps identified (all medium/low severity)"
            else:
                message = "✅ Gap analysis completed: no gaps identified"
            
            self._emit_event(
                deal.id, 
                EventType.RESULT, 
                PipelineStep.ENGAGEMENT_MANAGER.value,
                message,
                payload={"total_gaps": total_gaps, "high_severity_gaps": high_severity_gaps}
            )
            
            return gap_analysis_spec
            
        except Exception as e:
            logger.error(f"Error in engagement manager step: {e}", exc_info=True)
            self._handle_error(deal.id, PipelineStep.ENGAGEMENT_MANAGER, str(e), traceback.format_exc())
            return None
    
    def _emit_event(
        self, 
        deal_id: str, 
        event_type: EventType, 
        step: str, 
        message: str,
        payload: Optional[dict] = None
    ) -> None:
        """Emit an event to the event store"""
        event = PipelineEvent(
            id=0,  # Will be set in the store
            deal_id=deal_id,
            timestamp=datetime.now(),
            type=event_type,
            step=step,
            message=message,
            payload=payload
        )
        self.event_store.append_event(deal_id, event)
    
    def _handle_error(self, deal_id: str, step: PipelineStep, error_msg: str, stack_trace: str) -> None:
        """Handles pipeline errors"""
        try:
            deal = self.deal_repository.get(deal_id)
            if deal:
                deal.status = DealStatus.ERROR
                deal.error_message = error_msg
                deal.error_step = step
                self.deal_repository.save(deal)
            
            # Emit error event
            self._emit_event(
                deal_id,
                EventType.ERROR,
                step.value,
                f"❌ Error in {step.value}: {error_msg[:200]}",
                payload={"error": error_msg, "stack_trace": stack_trace[:500]}
            )
            
            logger.error(f"Pipeline failed for deal {deal_id} at step {step.value}")
            
        except Exception as e:
            logger.error(f"Error handling error for deal {deal_id}: {e}", exc_info=True)

