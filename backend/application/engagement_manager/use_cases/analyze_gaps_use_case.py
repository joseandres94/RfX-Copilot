import logging
from typing import List

from ....application.engagement_manager.interfaces.engagement_llm_provider import EngagementLLMProvider
from ....domain.shared.repositories.vector_db_repository import VectorDBRepository

logger = logging.getLogger(__name__)


class AnalyzeGapsUseCase:
    """
    Use case to analyze gaps between RfX requirements and the proposed solution.
    """
    
    def __init__(self, vector_db_repository: VectorDBRepository, engagement_llm_provider: EngagementLLMProvider):
        self.vector_db_repository = vector_db_repository
        self.engagement_llm_provider = engagement_llm_provider
    
    def execute(
        self,
        deal_context: dict,
        relevant_rfx_chunks_ids: List[str],
        demo_brief_spec: dict,
    ) -> tuple[str, dict]:
        """
        Runs the gap analysis.
        
        Args:
            deal_context: Context model from the Deal Analyzer
            relevant_rfx_chunks_ids: IDs of the relevant RFX chunks context
            demo_brief_spec: Demo Brief from the Solution Architect
            
        Returns:
            Tuple with gap_analysis_markdown and gap_analysis_spec
        """
        try:
            # Search similarities
            relevant_rfx_chunks = self.vector_db_repository.get_chunks('RfX_documents', relevant_rfx_chunks_ids)
            relevant_rfx_chunks = [{'chunk_id': chunk.id, 'content': chunk.content} for chunk in relevant_rfx_chunks]

            result = self.engagement_llm_provider.analyze_gaps(
                deal_context=deal_context,
                demo_brief_spec=demo_brief_spec,
                relevant_rfx_chunks_context=relevant_rfx_chunks
            )
            
            logger.info("Gap analysis completed successfully")
            return result['gap_analysis_markdown'], result['gap_analysis_spec']
            
        except Exception as e:
            logger.error(f"Error analyzing gaps: {e}", exc_info=True)
            raise
