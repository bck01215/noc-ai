from noc_ai.actions.tickets.app import create_ticket


def test_create_ticket() -> None:
    # Assert that the function returns the expected value
    assert create_ticket()
