from deck import Deck, populate_deck
from player import Player, deal_cards
from faction_manager import FactionManager
from debug_tools import DebugDealer
import random

class GameConstants:
    MAX_CARDS_IN_HAND = 6
    MAX_TABLE_SLOTS = 6
    MIN_CARDS_TO_ATTACK = 1

class Game:
    def __init__(self):
        self.faction_manager = FactionManager()
        self.table = [(None, None) for _ in range(GameConstants.MAX_TABLE_SLOTS)]
        self.deck = None
        self.player1 = None
        self.player2 = None
        
    def initialize_game(self, mode):
        if mode == '1':
            self._setup_real_game()
        else:
            self._setup_test_game()
            
    def _setup_real_game(self):
        self.deck = Deck()
        populate_deck(self.deck)
        random.shuffle(self.deck.cards)
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        deal_cards(self.deck, [self.player1, self.player2])
        
    def _setup_test_game(self):
        debug = DebugDealer()
        test_setup = {
            'player1_cards': [
                "Scratchmen Apoo",
                "Old Monkey D Garp",
                "Gol D Roger",
                "Monkey D Dragon",
                "Aokiji"
            ],
            'player2_cards': [
                "Prime Rayleigh",
                "Old Rayleigh",
                "Prime Monkey D Garp",
                "Shanks",
                "Old Whitebeard"
            ],
            'deck_cards': [
                # "Gol D Roger"
                # "Prime Whitebeard",
                # "Monkey D Dragon"
                # "Zeff"
            ]
        }
        self.player1, self.player2, self.deck = debug.setup_test_game(**test_setup)

    def find_player_with_lowest_rank(self):
        lowest_rank = float('inf')
        player_with_lowest = None
        
        for player in [self.player1, self.player2]:
            for card in player.hand:
                if card.rank < lowest_rank:
                    lowest_rank = card.rank
                    player_with_lowest = player
                    
        return player_with_lowest

    def draw_cards(self, player):
        if not self.deck.cards:
            return False
            
        cards_needed = GameConstants.MAX_CARDS_IN_HAND - len(player.hand)
        if cards_needed <= 0:
            return False
            
        cards_drawn = []
        for _ in range(cards_needed):
            if self.deck.cards:
                card = self.deck.cards.pop(0)
                player.receive_card(card)
                cards_drawn.append(card.name)
            else:
                break
        
        if cards_drawn:
            print(f"\n{player.name} draws cards: {', '.join(cards_drawn)}")
            return True
        return False

    def handle_end_of_turn_draws(self, attacker, defender):
        if not self.deck.cards:
            return
            
        print("\nEnd of turn card draw phase:")
        attacker_drew = self.draw_cards(attacker)
        defender_drew = self.draw_cards(defender)
        
        if not attacker_drew and not defender_drew:
            print("No cards were drawn this turn.")
        
        if not self.deck.cards and (attacker_drew or defender_drew):
            print("\nDeck is now empty!")

    def get_other_player(self, player):
        return self.player2 if player == self.player1 else self.player1