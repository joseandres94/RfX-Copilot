import logging
from ....application.summarizer_agent.interfaces.summarizer_llm_provider import SummarizerLLMProvider

logger = logging.getLogger(__name__)

class GenerateSummaryUseCase:
    """Use case for generating a summary"""
    def __init__(
        self,
        summarizer_llm_provider: SummarizerLLMProvider,
    ):
        self.summarizer_llm_provider = summarizer_llm_provider

    def execute(
        self,
        deal_context: dict,
    ) -> str:
        """Execute the use case"""
        try:
            # Generate DIC
            dic_markdown = self.summarizer_llm_provider.generate_summary(deal_context)
            print(f"DIC: {dic_markdown}")

            return dic_markdown
        except Exception as e:
            logger.error(f"Error generating DIC: {e}")
            raise e
