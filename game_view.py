from factions import FACTIONS

class GameView:
    @staticmethod
    def display_table(table, faction_manager):
        table_display = []
        for attack_card, defense_card in table:
            attack_str = attack_card.name_only() if attack_card else "None"
            defense_str = defense_card.name_only() if defense_card else "None"
            table_display.append(f"({attack_str}, {defense_str})")
        
        active_factions = faction_manager.get_active_factions()
        active_factions_str = ', '.join(str(FACTIONS[f]) for f in active_factions) if active_factions else 'None'
        
        print("\nTable now:", " | ".join(table_display))
        print("Active factions:", active_factions_str)

    @staticmethod
    def display_player_hand(player):
        print(f"\n{player.name}'s hand:")
        for i, card in enumerate(player.hand, 1):
            print(f"{i}: {card}")

    @staticmethod
    def get_attack_input():
        return input("Select the card numbers to attack (separated by space) or 'f' to finish: ").strip()

    @staticmethod
    def get_defense_input():
        return input("Select cards to defend with (numbers separated by space), 'p' to pick up cards, or 't' to transfer: ").strip()
    
    @staticmethod
    def get_transfer_input():
        return input("Select cards to transfer (numbers separated by space): ").strip()

    @staticmethod
    def get_game_mode():
        while True:
            mode = input("Select game mode (1 - Real Game, 2 - Test Mode): ").strip()
            if mode in ('1', '2'):
                return mode
            print("Invalid input. Please enter 1 or 2.")

    @staticmethod
    def display_game_over(winner):
        print(f"\n{winner.name} wins!")

    @staticmethod
    def display_first_player(player):
        print(f"\nFirst turn by {player.name}")
        input("\nPress Enter to start the game...")

    @staticmethod
    def display_empty_deck():
        print("\nDeck is now empty!")