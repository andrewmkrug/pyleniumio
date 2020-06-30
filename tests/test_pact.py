import pytest
import requests
from pactman import Consumer, Provider, Like, Equals
from pydantic import BaseModel


BASE_URL = 'https://deckofcardsapi.com/api/deck'


class Deck(BaseModel):
    success: bool = Field(..., True)
    deck_id: str
    remaining: int
    shuffled: bool


@pytest.fixture
def pact():
    return Consumer('Consumer') \
        .has_pact_with(Provider('Provider'),
                       host_name='localhost',
                       port=1234,
                       version='3.0.0')


def get_new_deck() -> Deck:
    deck = requests.get(f'http://localhost:1234/api/deck/new/shuffle/', params={'deck_count': '1'}).json()
    return Deck(**deck)


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
        .with_request('GET', path='/api/deck/new/shuffle/', query={'deck_count': '1'}) \
        .will_respond_with(200, body=expected)

    with pact:
        result = get_new_deck()

    assert result.deck_id == 'vvp7djnpqyax'


def test_create_new_shuffled_deck(api):
    expected_deck = Deck(
        success=True,
        deck_id="vvp7djnpqyax",
        remaining=52,
        shuffled=True
    )
    response = api.get(f'{BASE_URL}/new/shuffle/?deck_count=1')
    deck = Deck(**response.json())
    assert deck.deck_id == ''
    assert deck.success
    assert deck.shuffled
