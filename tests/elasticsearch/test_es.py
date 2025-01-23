import os

import pytest
from pydantic import SecretStr

from noc_ai.lookups.elastic_stack.agent import ElasticStackAgent


@pytest.fixture(scope="session", autouse=True)
def elastic_agent() -> ElasticStackAgent:
    return ElasticStackAgent(
        api_key=SecretStr(os.getenv("ELASTICSEARCH_API_KEY", "")),
        host=os.getenv("ELASTICSEARCH_URL", ""),
    )


@pytest.mark.skipif(
    os.getenv("ELASTICSEARCH_API_KEY") is None, reason="no api key"
)
def test_search_alert(elastic_agent: ElasticStackAgent) -> None:
    data = elastic_agent.search_alert(
        index_pattern="sn-imported",
        alert_data="CPU use is 99 percent on getvisprod02.liberty.edu:9100",
    )
    assert data["hits"]["total"]["value"] > 0
