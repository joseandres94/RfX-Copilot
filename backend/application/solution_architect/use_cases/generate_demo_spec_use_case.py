from typing import List
from ....application.solution_architect.interfaces.architect_llm_provider import ArchitectLLMProvider
from ....domain.shared.repositories.vector_db_repository import VectorDBRepository


class GenerateDemoSpecUseCase:
    def __init__(
        self,
        vector_db_repository: VectorDBRepository,
        architect_llm_provider: ArchitectLLMProvider,
    ):
        self.vector_db_repository = vector_db_repository
        self.architect_llm_provider = architect_llm_provider

    def execute(self, deal_context: dict, relevant_rfx_chunks_ids: List[str]) -> tuple[str, dict]:
        """
        Generates a demo specification based on the deal context and relevant RFX chunks.

        Args:
            deal_context: Context model from the Deal Analyzer
            relevant_rfx_chunks_ids: IDs of the relevant RFX chunks context

        Returns:
            Tuple with demo brief markdown and demo brief spec
        """
        # Search similarities
        relevant_rfx_chunks = self.vector_db_repository.get_chunks('RfX_documents', relevant_rfx_chunks_ids)
        relevant_rfx_chunks = [{'chunk_id': chunk.id, 'content': chunk.content} for chunk in relevant_rfx_chunks]

        # Generate proposal
        response = self.architect_llm_provider.generate_solution(deal_context, relevant_rfx_chunks, [])
        
        return response['demo_brief_markdown'], response['demo_brief_spec']
