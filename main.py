from game_core import Game
from game_state import GameState
from turn_manager import TurnManager
from game_view import GameView
from card_analyzer import CardAnalyzer

def main():
    # Инициализация компонентов
    game = Game()
    state = GameState()
    view = GameView()
    turn_manager = TurnManager(game)
    
    # Настройка игры
    mode = view.get_game_mode()
    game.initialize_game(mode)
    
    # Определение первого игрока
    first_player = game.find_player_with_lowest_rank()
    second_player = game.get_other_player(first_player)
    state.initialize_players(first_player, second_player)
    
    view.display_first_player(first_player)
    
    # Игровой цикл
    while not state.is_game_over:
        if hasattr(state, 'start_with_defense'):  # Добавляем проверку флага
            turn_result = turn_manager.handle_turn(state.current_attacker, state.current_defender, 
                                                 start_with_defense=True)
            delattr(state, 'start_with_defense')  # Удаляем флаг после использования
        else:
            turn_result = turn_manager.handle_turn(state.current_attacker, state.current_defender)
        
        if turn_result == "transfer":
            state.switch_roles()
            state.start_with_defense = True  # Устанавливаем флаг для следующей итерации
            continue  # Пропускаем раздачу карт и продолжаем с защиты
            
        game.handle_end_of_turn_draws(state.current_attacker, state.current_defender)
        
        if state.check_game_over():
            view.display_game_over(state.winner)
            break
            
        if turn_result is True:
            state.switch_roles()

if __name__ == "__main__":
    main()
