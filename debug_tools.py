from deck import Deck, create_card
from player import Player

class DebugDealer:
    def __init__(self):
        self.full_deck = Deck()  # Полная колода для справки
        self.test_deck = Deck()  # Тестовая колода
        self.populate_full_deck()
        
    def populate_full_deck(self):
        """Заполняет полную колоду всеми картами для справки."""
        from deck import populate_deck
        populate_deck(self.full_deck)
    
    def setup_test_game(self, player1_cards=None, player2_cards=None, deck_cards=None):
        """
        Настраивает тестовую игру с заданными картами.
        
        Args:
            player1_cards (list): Список имен карт для первого игрока
            player2_cards (list): Список имен карт для второго игрока
            deck_cards (list): Список имен карт для колоды
        
        Returns:
            tuple: (player1, player2, deck)
        """
        # Создаем игроков
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        
        # Очищаем тестовую колоду
        self.test_deck = Deck()
        
        # Функция для поиска карты по имени
        def find_card(name):
            for card in self.full_deck.cards:
                if card.name == name:
                    return create_card(card.name, card.rank, card.faction_ids)
            raise ValueError(f"Card '{name}' not found in full deck")
        
        # Раздаем карты игрокам
        if player1_cards:
            for card_name in player1_cards:
                player1.receive_card(find_card(card_name))
                
        if player2_cards:
            for card_name in player2_cards:
                player2.receive_card(find_card(card_name))
                
        # Добавляем карты в колоду
        if deck_cards:
            for card_name in deck_cards:
                self.test_deck.add_card(find_card(card_name))
                
        return player1, player2, self.test_deck
    
    def print_game_state(self, player1, player2, deck):
        """Выводит текущее состояние игры."""
        print("\n=== Debug Game State ===")
        print("\nPlayer 1 hand:")
        for card in player1.hand:
            print(f"  {card}")
            
        print("\nPlayer 2 hand:")
        for card in player2.hand:
            print(f"  {card}")
            
        print("\nDeck cards:")
        for card in deck.cards:
            print(f"  {card}")
            
        print("\nDiscard pile:")
        print(deck.display_discard_pile())
        print("=====================")

# Пример использования:
if __name__ == "__main__":
    debug = DebugDealer()
    
    # Пример настройки тестовой игры
    test_setup = {
        'player1_cards': [
            "Monkey D Luffy",
            "Roronoa Zoro",
            "Winsmoke Sanji",
            "Boa Hancock",
            "Nico Robin",
            "Jinbei"
        ],
        'player2_cards': [
            "Marshall D Teach",
            "Shanks",
            "Drakul Mihawk",
            "Trafalgar D Water Law",
            "Marguerite",
            "Clown Buggy"
        ],
        'deck_cards': [
            "Gol D Roger",
            "Prime Whitebeard",
            "Monkey D Dragon"
        ]
    }
    
    # Создаем тестовую игру
    p1, p2, deck = debug.setup_test_game(**test_setup)
    
    # Выводим состояние
    debug.print_game_state(p1, p2, deck) 