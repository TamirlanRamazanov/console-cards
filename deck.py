# deck.py

from card import Card
from deck_data import CARDS_DATA

class Deck:
    def __init__(self):
        self.cards = []
        self.discard_pile = []  # Стопка сброса

    def add_card(self, card):
        """Add card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Remove card from the deck."""
        self.cards.remove(card)

    def add_to_discard_pile(self, card):
        """Add card to the discard pile."""
        self.discard_pile.append(card)

    def __str__(self):
        return '\n'.join(str(card) for card in self.cards)

    def display_discard_pile(self):
        """Display all cards in the discard pile."""
        if self.discard_pile:
            return '\n'.join(str(card) for card in self.discard_pile)
        else:
            return "Discard pile is empty."

# Function to create a card and add factions
def create_card(name, rank, factions):
    card = Card(name, rank)
    for faction in factions:
        card.add_faction(faction)
    return card

def populate_deck(deck):
    """Populate the deck with predefined cards."""
    for name, rank, factions in CARDS_DATA:
        deck.add_card(create_card(name, rank, factions))

# Create deck and populate it
deck = Deck()
populate_deck(deck)

# Print all cards in the deck
print(deck)