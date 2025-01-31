# faction_manager.py
from factions import FACTIONS

class FactionManager:
    def __init__(self):
        self.faction_slots = [{'active': set(), 'inactive': set()} for _ in range(12)]
        self.active_factions = set()
        self.table = None  # Добавляем поле для хранения состояния стола

    def set_table(self, table):
        """Устанавливает текущее состояние стола."""
        self.table = table

    def add_card_factions(self, card, slot_index):
        """
        Добавляет фракции карты в определенный слот и обновляет активные фракции.
        """
        if 0 <= slot_index < 12:
            # Если это слот для карты защиты (нечетный индекс)
            if slot_index % 2 == 1:
                # Все фракции карты защиты становятся активными
                self.faction_slots[slot_index]['active'] = set(card.faction_ids)
                self.update_active_factions()
                return

            # Находим все возможные связи
            connected_slots = []
            for i, slot in enumerate(self.faction_slots):
                if slot['active']:
                    common_factions = card.faction_ids & slot['active']
                    if common_factions:
                        # Определяем, какая карта находится в этом слоте
                        table_index = i // 2  # Преобразуем индекс слота в индекс пары на столе
                        card_index = i % 2    # 0 для атакующей карты, 1 для защищающейся
                        if self.table and self.table[table_index][card_index]:
                            card_in_slot = self.table[table_index][card_index]
                            connected_slots.append((i, common_factions, card_in_slot))

            # Если есть несколько возможных связей, предлагаем выбор
            if len(connected_slots) > 1:
                print(f"\nВыберите карту, с которой хотите связать {card.name}:")
                for idx, (_, common_facs, connected_card) in enumerate(connected_slots, 1):
                    print(f"{idx}: {connected_card.name} (общие фракции: {', '.join(FACTIONS[f] for f in common_facs)})")
                
                while True:
                    try:
                        choice = int(input("Выберите номер (1-{0}): ".format(len(connected_slots)))) - 1
                        if 0 <= choice < len(connected_slots):
                            connected_slot_index, common_factions, _ = connected_slots[choice]
                            break
                        else:
                            print("Неверный выбор. Попробуйте снова.")
                    except ValueError:
                        print("Пожалуйста, введите число.")
            
            elif connected_slots:  # Если есть только одна связь
                connected_slot_index, common_factions, _ = connected_slots[0]
            else:  # Если нет связей
                self.faction_slots[slot_index]['active'] = set(card.faction_ids)
                self.update_active_factions()
                return

            # Обновляем активные фракции для обеих карт
            self.faction_slots[slot_index]['active'] = common_factions
            self.faction_slots[connected_slot_index]['active'] = common_factions
            
            self.update_active_factions()

    def update_active_factions(self):
        """Обновляет общий набор активных фракций."""
        all_active = set()
        
        # Собираем все активные фракции из слотов
        for slot in self.faction_slots:
            if slot['active']:
                all_active.update(slot['active'])
        
        self.active_factions = all_active

    def validate_card_factions(self, card):
        """Проверяет, может ли карта быть сыграна."""
        if not self.active_factions:
            return True
        return bool(card.faction_ids & self.active_factions)

    def get_active_factions(self):
        """Возвращает текущий набор активных фракций."""
        return self.active_factions

    def clear(self):
        """Очищает все слоты и активные фракции."""
        self.faction_slots = [{'active': set(), 'inactive': set()} for _ in range(12)]
        self.active_factions.clear()

    def validate_multiple_cards(self, cards):
        """
        Проверяет, могут ли карты быть сыграны вместе.
        
        Args:
            cards: Список карт для проверки
        
        Returns:
            bool: True если карты могут быть сыграны вместе, False в противном случае
        """
        if not cards:
            return False
            
        if len(cards) == 1:
            return self.validate_card_factions(cards[0])
            
        # Находим общие фракции между всеми картами
        common_factions = set.intersection(*(card.faction_ids for card in cards))
        
        # Если нет активных фракций, достаточно иметь общие фракции между картами
        if not self.active_factions:
            return bool(common_factions)
            
        # Иначе должно быть пересечение с активными фракциями
        return bool(common_factions & self.active_factions)

    def get_possible_connections(self, card):
        """
        Находит возможные карты для связи с новой картой.
        
        Returns:
            list: Список кортежей (индекс_слота, общие_фракции)
        """
        connections = []
        for i, slot in enumerate(self.faction_slots):
            if slot['active']:
                common_factions = card.faction_ids & slot['active']
                if common_factions:
                    connections.append((i, common_factions))
        return connections