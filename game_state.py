class GameState:
    def __init__(self):
        self.current_attacker = None
        self.current_defender = None
        self.is_game_over = False
        self.winner = None
        
    def initialize_players(self, first_player, second_player):
        self.current_attacker = first_player
        self.current_defender = second_player
        
    def switch_roles(self):
        self.current_attacker, self.current_defender = self.current_defender, self.current_attacker
        
    def check_game_over(self):
        if not self.current_attacker.hand:
            self.is_game_over = True
            self.winner = self.current_attacker
            return True
        if not self.current_defender.hand:
            self.is_game_over = True
            self.winner = self.current_defender
            return True
        return False 