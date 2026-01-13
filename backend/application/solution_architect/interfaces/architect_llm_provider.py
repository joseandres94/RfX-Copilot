from abc import ABC, abstractmethod


class ArchitectLLMProvider(ABC):
    @abstractmethod
    def generate_solution(
        self,
        deal_context: dict,
        relevant_rfx_chunks: list[dict],
        knowledge_context: list[str]
    ) -> dict:
        """Generate proposal for demo based on the deal context, relevant rfx chunks and knowledge context"""
        pass