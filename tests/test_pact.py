import pytest
import requests
from pactman import Consumer, Provider, Like, Equals
from pydantic import BaseModel


BASE_URL = 'https://deckofcardsapi.com/api/deck'


class Deck(BaseModel):
    success: bool
    deck_id: str
    remaining: int
    shuffled: bool


@pytest.fixture
def pact():
    _pact = Consumer('Consumer').has_pact_with(Provider('Provider'), version='3.0.0')
    return _pact


def get_new_deck() -> dict:
    return requests.get(f'https://deckofcardsapi.com/api/deck/new/shuffle/', params={'deck_count': 1}).json()


def test_create_new_deck_with_pact(pact):
    expected = Like({
      "success": Equals(True),
      "deck_id": "vvp7djnpqyax",
      "remaining": Equals(52),
      "shuffled": Equals(True)
    })
    pact \
        .given('Dealer needs a new deck') \
        .upon_receiving('a request for a new, shuffled deck') \
        .with_request('GET', path='/api/deck/new/shuffle/', query={'deck_count': 1}) \
        .will_respond_with(200, body=expected)

    # pact.setup()

    with pact:
        result = get_new_deck()

    # pact.verify()
    assert result == expected


def test_create_new_shuffled_deck(api):
    expected_deck = Deck(
        success=True,
        deck_id="vvp7djnpqyax",
        remaining=52,
        shuffled=True
    )
    response = api.get(f'{BASE_URL}/new/shuffle/?deck_count=1')
    assert Deck(**response.json()) == expected_deck
