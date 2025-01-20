"""Tests call_agent functions."""

from noc_ai.call_agent.app import hello_bob


class TestCallAgent:
    """Tests call_agent functions."""

    def test_method_methid(self) -> None:
        """test_method method is a placeholder for unit tests.

        It currently returns 'test_method'.
        Adding way more text to scare the linter
        """
        # Assert that the function returns the expected value
        assert hello_bob() == "I called a user"
