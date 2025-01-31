# player.py

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        """Получить карту в руку игрока."""
        if len(self.hand) < 6:
            self.hand.append(card)
        else:
            print(f"{self.name} already has 6 cards.")

    def __str__(self):
        hand_str = ', '.join(str(card.name) for card in self.hand) if self.hand else 'No cards'
        return f"Player: {self.name}\n  Hand: [{hand_str}]"

def deal_cards(deck, players):
    """Раздаем 6 карт каждому игроку из колоды."""
    for _ in range(6):
        for player in players:
            if deck.cards:
                card = deck.cards.pop(0)
                player.receive_card(card)
            else:
                print("Not enough cards in the deck to deal.")
                return
