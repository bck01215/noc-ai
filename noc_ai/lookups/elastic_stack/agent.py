"""elastic_stack_agent handles elastic stack functions."""

import os
from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch
from pydantic import SecretStr


class ElasticStackAgent:
    """
    Initialize an ElasticStackAgent.

    Args:
    - username (str): username for elastic stack agent
    - password (SecretStr): password for elastic stack agent
    """

    def __init__(self, api_key: SecretStr, host: str) -> None:
        if not api_key:
            api_key = SecretStr(os.getenv("ELASTICSEARCH_API_KEY", ""))
            if not api_key:
                raise ValueError("ELASTICSEARCH_API_KEY is not set")
        if not host:
            host = os.getenv("ELASTICSEARCH_URL", "")
            if not host:
                raise ValueError("ELASTICSEARCH_URL is not set")
        self.client = Elasticsearch(
            host,
            api_key=api_key.get_secret_value(),
            verify_certs=False,
            ssl_show_warn=False,
        )

    def search_alert(
        self, index_pattern: str, alert_data: str
    ) -> ObjectApiResponse[Any]:
        default_query = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "fields": [
                                "short_description^4",
                                "description^2",
                                "comments",
                                "work_notes",
                            ],
                            "query": alert_data,
                            "operator": "and",
                            "type": "phrase_prefix",
                        }
                    },
                }
            }
        }
        data = self.client.search(
            index=index_pattern,
            body=default_query,
        )
        return data
