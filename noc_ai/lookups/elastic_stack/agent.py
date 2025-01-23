"""elastic_stack_agent handles elastic stack functions."""

import os
from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch
from pydantic import SecretStr


class ElasticStackAgent:
    """
    Initialize an ElasticStackAgent.

    **Parameters**:
        :param SecretStr api_key: API key to authenticate with Elastic Stack
            services.
            If not provided and not set as an environment variable,
            raises a ValueError.
        :param str host: Elasticsearch cluster URL. If not provided and not set
            as an environment variable, raises a ValueError.

    **Environment Variables**:

        - ELASTICSEARCH_API_KEY: API key to authenticate with Elastic Stack \
services.
        - ELASTICSEARCH_URL: Elasticsearch cluster URL.
    """

    def __init__(
        self, api_key: SecretStr | None = None, host: str = ""
    ) -> None:
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

    def get_best_result(self, data: ObjectApiResponse[Any]) -> dict:
        items = data.get("hits", {}).get("hits", [])
        if len(items) == 0:
            return {}
        return items[0]

    def search_alert(
        self, index_pattern: str, alert_data: str
    ) -> ObjectApiResponse[Any]:
        default_query = {
            "size": 10,
            "query": {
                "multi_match": {
                    "fields": [
                        "short_description^4",
                        "description^2",
                        "comments",
                        "work_notes",
                    ],
                    "query": alert_data,
                    "type": "cross_fields",
                }
            },
        }
        data = self.client.search(
            index=index_pattern,
            body=default_query,
        )
        return data
