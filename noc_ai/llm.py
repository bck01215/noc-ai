"""instantiate llm."""

import json
import os
from typing import Any

from elastic_transport import ObjectApiResponse
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, Graph
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
        self.graph_builder = Graph()
        self.graph_builder.add_node(
            "get_alert_es_result", self.get_alert_es_result
        )
        self.graph_builder.add_node("get_best_result", self.get_best_result)
        self.graph_builder.add_node("pretty_print_dict", self.pretty_print_dict)
        self.graph_builder.add_edge(START, "get_alert_es_result")
        self.graph_builder.add_edge("get_alert_es_result", "get_best_result")
        self.graph_builder.add_edge("get_best_result", "pretty_print_dict")
        self.graph_builder.add_edge("pretty_print_dict", END)
        self.graph = self.graph_builder.compile()

    def get_alert_es_result(self, alert_data: str) -> ObjectApiResponse[Any]:
        """
        Determine the action to take based on the alert data.

        Args:
            alert_data (str): The alert data to process.

        Returns:
            str: The action to take.
        """
        return self.es.search_alert(
            index_pattern="sn-imported", alert_data=alert_data
        )

    def get_best_result(self, data: ObjectApiResponse[Any]) -> dict:
        return self.es.get_best_result(data)

    def pretty_print_dict(self, data: dict) -> None:
        print(json.dumps(data, indent=2))

    def handle_alert(self, alert_data: str) -> None:
        self.graph.invoke(alert_data)
