"""instantiate llm."""

import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class NocAiLlm:
    """instantiate llm."""

    def __init__(self, api_key: SecretStr) -> None:
        if not api_key:
            api_key = SecretStr(os.getenv("OPENAI_API_KEY", ""))
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")
