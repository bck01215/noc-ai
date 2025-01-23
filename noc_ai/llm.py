"""instantiate llm."""

import json
import os
from typing import Annotated, Any, TypedDict

from elastic_transport import ObjectApiResponse
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import SecretStr

from noc_ai.lookups.elastic_stack.agent import ElasticStackAgent, TicketData


class AlertActionState(TypedDict):
    """alert action state."""

    alert_data: str
    best_ticket: TicketData | None
    messages: Annotated[list, add_messages]


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
        self.graph_builder = StateGraph(AlertActionState)
        self.graph_builder.add_node(
            "get_alert_es_result", self.get_alert_es_result
        )
        self.graph_builder.add_node("pretty_print_dict", self.pretty_print_dict)
        self.graph_builder.add_edge(START, "get_alert_es_result")
        self.graph_builder.add_edge("get_alert_es_result", "pretty_print_dict")
        self.graph_builder.add_edge("pretty_print_dict", END)
        self.graph = self.graph_builder.compile()

    def get_alert_es_result(self, state: AlertActionState) -> AlertActionState:
        """
        Determine the action to take based on the alert data.

        Args:
            alert_data (str): The alert data to process.

        Returns:
            str: The action to take.
        """
        resp = self.es.search_alert(
            index_pattern="sn-imported", alert_data=state.get("alert_data")
        )
        data = self.get_best_result(resp)
        state["best_ticket"] = data
        return state

    def get_best_result(
        self, data: ObjectApiResponse[Any]
    ) -> TicketData | None:
        return self.es.get_best_result(data)

    def pretty_print_dict(self, state: AlertActionState) -> None:
        print(json.dumps(state.get("best_ticket"), indent=2))

    def handle_alert(self, alert_data: str) -> AlertActionState:
        state_init: AlertActionState = {
            "alert_data": alert_data,
            "best_ticket": None,
            "messages": [],
        }
        self.graph.invoke(state_init)
        return state_init
