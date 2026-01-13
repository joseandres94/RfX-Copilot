from abc import ABC, abstractmethod

class SummarizerLLMProvider(ABC):
    """Interface for Summarizer LLM providers"""
    @abstractmethod
    def generate_summary(self, deal_context: dict) -> str:
        """Generate a DIC in markdown format"""
        pass
