import os

import pytest
from pydantic import SecretStr

from noc_ai.llm import NocAiLlm


@pytest.fixture(scope="session", autouse=True)
def llm_agent() -> NocAiLlm:
    return NocAiLlm(api_key=SecretStr(os.getenv("OPENAI_API_KEY", "")))


@pytest.mark.skipif(os.getenv("OPENAI_API_KEY") is None, reason="no api key")
def test_llm_basic_alert(llm_agent: NocAiLlm) -> None:
    res = llm_agent.handle_alert(
        alert_data="CPU use is 99 percent on getvisprod02.liberty.edu:9100"
    )
    assert res
