from game_view import GameView
from factions import FACTIONS

class TurnManager:
    def __init__(self, game):
        self.game = game
        self.view = GameView()
        
    def handle_turn(self, attacker, defender, start_with_defense = False):
        if not start_with_defense:
            print(f"\n{attacker.name}'s turn to attack.")
            
            self.game.faction_manager.set_table(self.game.table)
            self.view.display_table(self.game.table, self.game.faction_manager)

        attack_continues = True
        while True:
            if start_with_defense:
                # Сразу переходим к защите
                defense_result = self._handle_defense_phase(defender, attacker)
                start_with_defense = False  # Сбрасываем флаг после первой защиты
                
                if defense_result == "take":
                    self._clear_table()
                    self.game.handle_end_of_turn_draws(attacker, defender)
                    return False
                elif defense_result == "transfer":
                    return "transfer"
            else:
                # Фаза атаки
                attack_result = self._handle_attack_phase(attacker, defender)
                
                if attack_result is None:
                    continue
                    
                # Если игрок завершил ход ('f')
                if attack_result is False:
                    # Проверяем, есть ли успешно отбитые карты
                    if any(pair[1] is not None for pair in self.game.table):
                        self._clear_table()
                        return True  # Смена ролей после успешной защиты
                    else:
                        self._clear_table()
                        return False  # Нет смены ролей, если нет отбитых карт
                    
                # Если атака успешна, переходим к защите
                if attack_result is True:
                    defense_result = self._handle_defense_phase(defender, attacker)
                    if defense_result == "take":  
                        self._clear_table()
                        self.game.handle_end_of_turn_draws(attacker, defender)
                        return False
                    elif defense_result == "transfer":
                        return "transfer"  # Возвращаем специальное значение для перевода

                    # else: # Успешная защита (False) или неуспешная (True)
                    #     # Продолжаем ход атакующего после защиты
                    #     self.view.display_table(self.game.table, self.game.faction_manager)

        self._clear_table()
        return False  # По умолчанию не меняем роли

    def _handle_attack_phase(self, attacker, defender):
        self.view.display_player_hand(attacker)
        attack_input = self.view.get_attack_input()

        # Проверяем на пустой ввод или некорректные символы
        if not attack_input or any(c not in '0123456789f ' for c in attack_input):
            print("Invalid input. Please enter numbers separated by spaces or 'f' to finish.")
            return None

        if attack_input.lower() == 'f':
            if any(pair[0] is not None for pair in self.game.table):
                return False
            else:
                print("You must play at least one card!")
                return None

        try:
            # Преобразуем ввод в список индексов
            attack_indices = [int(index) - 1 for index in attack_input.split()]
            
            # Проверяем на дубликаты
            if len(attack_indices) != len(set(attack_indices)):
                print("You cannot select the same card multiple times!")
                return None
                
            # Проверяем валидность индексов
            if any(index < 0 or index >= len(attacker.hand) for index in attack_indices):
                print("Invalid card number(s).")
                return None

            # Проверяем количество карт в руке защищающегося
            if len(attack_indices) > len(defender.hand):
                print(f"You cannot attack with more cards than defender has ({len(defender.hand)} cards).")
                return None

            attack_cards = [attacker.hand[index] for index in attack_indices]

            # Проверяем количество свободных слотов
            empty_slots = sum(1 for pair in self.game.table if pair[0] is None)
            if len(attack_cards) > empty_slots:
                print(f"Not enough space on the table. Maximum cards you can play: {empty_slots}")
                return None

            if not self.game.faction_manager.validate_multiple_cards(attack_cards):
                print("Invalid card combination - cards must share at least one faction with active factions.")
                return None

            # Размещаем карты атаки на столе
            for attack_card in attack_cards:
                slot_index = next(i for i, pair in enumerate(self.game.table) if pair[0] is None)
                self.game.table[slot_index] = (attack_card, None)
                self.game.faction_manager.add_card_factions(attack_card, slot_index * 2)
                attacker.hand.remove(attack_card)

            self.view.display_table(self.game.table, self.game.faction_manager)
            return True

        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces.")
            return None

    def _handle_defense_phase(self, defender, attacker):
        while True:
            self.view.display_player_hand(defender)
            defense_input = self.view.get_defense_input()

            cards_to_defend = sum(1 for pair in self.game.table if pair[0] is not None and pair[1] is None)

            if defense_input.lower() == 'p':
                # Добавляем атакующие карты в руку защищающегося
                taken_cards = []
                for pair in self.game.table:
                    if pair[0]:
                        defender.hand.append(pair[0])
                        taken_cards.append(pair[0].name)
                
                if taken_cards:
                    print(f"\n{defender.name} takes cards: {', '.join(taken_cards)}") # TODO: maybe переделать на picks up cards:

                    print(f"{attacker.name} continues their turn.")
                    # Очищаем стол и фракции после взятия карт
                    self._clear_table()
                    
                    # Отображаем пустой стол и активные фракции
                    self.view.display_table(self.game.table, self.game.faction_manager) 
                    return "take"  # Оставляем "take" как внутреннее значение
                
            if defense_input.lower() == 't':
                if self._can_transfer(defender, attacker):
                    transfer_result = self._handle_transfer(defender, attacker)
                    if transfer_result:
                        return "transfer"
                continue
            
            if not defense_input:
                continue

            if not self._process_defense_input(defense_input, defender, cards_to_defend):
                continue

            return True

    def _can_transfer(self, defender, attacker):
        """Проверяет возможность перевода карт."""
        # Проверяем, что нет карт в слотах защиты
        if any(pair[1] is not None for pair in self.game.table):
            print("Cannot transfer when there are defended cards on the table.")
            return False

        # Подсчитываем атакующие карты на столе
        attack_cards = [pair[0] for pair in self.game.table if pair[0] is not None]
        if not attack_cards:
            print("No cards to transfer.")
            return False

        # Проверяем, что у атакующего достаточно карт в руке
        if len(attacker.hand) < len(attack_cards) + 1:  # +1 для минимум одной карты перевода
            print(f"Attacker doesn't have enough cards ({len(attacker.hand)}) to defend potential transfer.")
            return False

        return True

    def _handle_transfer(self, defender, attacker):
        """Обрабатывает перевод карт."""
        self.view.display_player_hand(defender)
        transfer_input = self.view.get_transfer_input()

        if not transfer_input:
            return False

        try:
            transfer_indices = [int(index) - 1 for index in transfer_input.split()]
            if any(index < 0 or index >= len(defender.hand) for index in transfer_indices):
                print("Invalid card number(s).")
                return False

            transfer_cards = [defender.hand[index] for index in transfer_indices]

            # Получаем все атакующие карты на столе
            attack_cards = [pair[0] for pair in self.game.table if pair[0] is not None]

            # Проверяем общие фракции
            all_cards = attack_cards + transfer_cards
            if not self.game.faction_manager.validate_multiple_cards(all_cards):
                print("Transfer cards must share at least one faction with attacking cards.")
                return False

            # Проверяем, что не превышен лимит карт на столе
            if len(attack_cards) + len(transfer_cards) > 6:
                print("Total number of cards would exceed table limit (6).")
                return False

            # Проверяем, что не превышено количество карт в руке будущего защищающегося
            if len(attack_cards) + len(transfer_cards) > len(attacker.hand):
                print(f"Total cards would exceed attacker's hand size ({len(attacker.hand)}).")
                return False

            # Добавляем карты перевода на стол
            empty_slots = [i for i, pair in enumerate(self.game.table) if pair[0] is None]
            for card, slot in zip(transfer_cards, empty_slots):
                self.game.table[slot] = (card, None)
                self.game.faction_manager.add_card_factions(card, slot * 2)
                defender.hand.remove(card)

            self.view.display_table(self.game.table, self.game.faction_manager)
            print(f"\n{defender.name} transfers cards. {attacker.name} must now defend!")
            return True

        except ValueError:
            print("Invalid input. Please enter valid numbers separated by spaces.")
            return False

    def _handle_taking_cards(self, defender):
        taken_cards = []
        for i, pair in enumerate(self.game.table):
            if pair[0] is not None:
                defender.hand.append(pair[0])
                taken_cards.append(pair[0].name)
            if pair[1] is not None:
                defender.hand.append(pair[1])
                taken_cards.append(pair[1].name)
            self.game.table[i] = (None, None)
        print(f"\n{defender.name} takes cards: {', '.join(taken_cards)}")

    def _process_defense_input(self, defense_input, defender, cards_to_defend):
        try:
            defense_indices = [int(index) - 1 for index in defense_input.split()]
            if any(index < 0 or index >= len(defender.hand) for index in defense_indices):
                print("Invalid card number(s).")
                return False
            defense_cards = [defender.hand[index] for index in defense_indices]
        except (ValueError, IndexError):
            print("Invalid input. Please enter valid numbers separated by spaces.")
            return False

        if len(defense_indices) != cards_to_defend:
            print(f"You must select exactly {cards_to_defend} card(s) to defend.")
            return False
        
        if len(defense_indices) > len(defender.hand):
            print(f"You don't have enough cards. You need {cards_to_defend} cards but only have {len(defender.hand)}.")
            return False

        if not self._validate_defense(defense_cards):
            return False

        self._place_defense_cards(defense_cards, defender)
        self.view.display_table(self.game.table, self.game.faction_manager)
        return True

    def _validate_defense(self, defense_cards):
        defense_cards_copy = defense_cards.copy()
        for i, (attack_card, _) in enumerate(self.game.table):
            if attack_card is not None and self.game.table[i][1] is None:
                defense_card = defense_cards_copy.pop(0)
                if defense_card.rank < attack_card.rank:
                    print(f"Card {defense_card.name} (rank {defense_card.rank}) cannot beat {attack_card.name} (rank {attack_card.rank})")
                    return False
        return True

    def _place_defense_cards(self, defense_cards, defender):
        defense_index = 0
        for i in range(len(self.game.table)):
            if self.game.table[i][0] is not None and self.game.table[i][1] is None:
                attack_card = self.game.table[i][0]
                defense_card = defense_cards[defense_index]
                self.game.table[i] = (attack_card, defense_card)
                self.game.faction_manager.add_card_factions(defense_card, i * 2 + 1)
                defender.hand.remove(defense_card)
                defense_index += 1
                if defense_index >= len(defense_cards):
                    break

    def _clear_table(self):
        for attack_card, defense_card in self.game.table:
            if attack_card:
                self.game.deck.add_to_discard_pile(attack_card)
            if defense_card:
                self.game.deck.add_to_discard_pile(defense_card)
        
        for i in range(len(self.game.table)):
            self.game.table[i] = (None, None)
        
        self.game.faction_manager.clear() 