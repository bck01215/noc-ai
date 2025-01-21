from noc_ai.actions.ticket_agent.app import sample_method


def test_sample_method() -> None:
    # Assert that the function returns the expected value
    assert sample_method() == "I ticketed a user"
