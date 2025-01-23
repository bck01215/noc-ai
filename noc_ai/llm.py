"""instantiate llm."""

import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from noc_ai.lookups.elastic_stack.agent import ElasticStackAgent


class LLMError(Exception):
    """llm error."""


class NocAiLlm:
    """instantiate llm."""

    def __init__(self, api_key: SecretStr) -> None:
        """
        Initialize the NocAiLlm instance.

        Args:
            api_key (SecretStr): API key to authenticate with OpenAI services.

        Raises:
            ValueError: If the API key is not provided and cannot be retrieved
                       from the environment variable 'OPENAI_API_KEY'.
            LLMError: If the ElasticStackAgent fails to initialize.
        """
        if not api_key:
            api_key = SecretStr(os.getenv("OPENAI_API_KEY", ""))
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")
        try:
            self.es = ElasticStackAgent()
        except ValueError as e:
            raise LLMError("Failed to initialize ElasticStackAgent") from e

    def validate(self) -> bool:
        return True
