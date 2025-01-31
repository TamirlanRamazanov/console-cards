import pygame
import random
from deck import Deck, populate_deck
from player import Player, deal_cards
from card import Card
from factions import FACTIONS
from faction_manager import FactionManager
from game_state import GameState
from card_view import CardView
from game_core import Game, GameConstants
from turn_manager import TurnManager
from game_view import GameView

# Инициализация Pygame
pygame.init()
pygame.font.init()  # Инициализация шрифтов
font = pygame.font.Font(None, 36)  # Создание шрифта для текста

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 100, 150
BACKGROUND_COLOR = (34, 139, 34)  # Темно-зеленый цвет
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Отступы и позиционирование для информационной панели
INFO_PANEL_LEFT = 20  # Отступ слева для информационного текста
INFO_PANEL_TOP = 20   # Отступ сверху для информационного текста
INFO_LINE_HEIGHT = 30 # Высота строки ��екста

# Позиционирование игрового стола
TABLE_OFFSET_Y = 400  # Смещение стола от верха экрана
TABLE_AREA = pygame.Rect(
    100,  # Отступ слева
    TABLE_OFFSET_Y,  # Позиция Y
    SCREEN_WIDTH-200,  # Ширина стола
    CARD_HEIGHT  # Высота области стола
)

# Позиционирование карт игроков
PLAYER1_CARDS_Y = TABLE_OFFSET_Y - CARD_HEIGHT - 50  # Карты первого игрока над столом
PLAYER2_CARDS_Y = TABLE_OFFSET_Y + CARD_HEIGHT + 50  # Карты второго игрока под столом
CARDS_SPACING = CARD_WIDTH + 10  # Расстояние между картами
CARDS_START_X = 50  # Начальная позиция X для карт

# Позиционирование кнопки завершения хода
END_TURN_BUTTON_WIDTH = 140
END_TURN_BUTTON_HEIGHT = 60
END_TURN_BUTTON = pygame.Rect(
    SCREEN_WIDTH - 150,  # Отступ справа
    SCREEN_HEIGHT - 100,  # Отступ снизу
    END_TURN_BUTTON_WIDTH,
    END_TURN_BUTTON_HEIGHT
)

# Позиционирование кнопки взятия карт
TAKE_CARDS_BUTTON_WIDTH = 140
TAKE_CARDS_BUTTON_HEIGHT = 60
TAKE_CARDS_BUTTON = pygame.Rect(
    SCREEN_WIDTH - 300,  # Отступ справа (левее кнопки End Turn)
    SCREEN_HEIGHT - 100,  # Отступ снизу
    TAKE_CARDS_BUTTON_WIDTH,
    TAKE_CARDS_BUTTON_HEIGHT
)

# Добавим новую кнопку для перевода
TRANSFER_BUTTON_WIDTH = 140
TRANSFER_BUTTON_HEIGHT = 60
TRANSFER_BUTTON = pygame.Rect(
    SCREEN_WIDTH - 450,  # Левее кнопки Take Cards
    SCREEN_HEIGHT - 100,
    TRANSFER_BUTTON_WIDTH,
    TRANSFER_BUTTON_HEIGHT
)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Game")

# Шрифты
try:
    font = pygame.font.Font(None, 24)
except Exception as e:
    print(f"Error loading font: {e}")
    pygame.quit()
    exit()

class GameState:
    def __init__(self):
        self.active_factions = set()
        self.current_attacker = None
        self.current_defender = None
        self.table = [(None, None) for _ in range(6)]
        self.phase = "ATTACK"
        self.deck = Deck()
        self.discard_pile = []
        self.faction_manager = FactionManager()  # Добавляем менеджер фракций
        self.waiting_for_defense = False
        self.cards_pending_defense = []
        self.defense_timeout = None
        self.can_attack = True
        self.cards_taken = False
        self.is_game_over = False
        self.winner = None
        self.error_message = None
        self.error_time = None
        self.ERROR_DISPLAY_TIME = 2000  # 2 секунды для показа ошибки

    def process_attack_card(self, card, player):
        """Обработка размещения атакующей карты"""
        try:
            if player != self.current_attacker:
                self.show_error("Сейчас не ваш ход!")
                return False
                
            if not self.can_attack:
                self.show_error("Дождитесь ответа защищающегося!")
                return False
                
            if self.phase != "ATTACK":
                self.show_error("Сейчас фаза защиты!")
                return False

            # Проверяем валидность карты по фракциям
            if not self.faction_manager.validate_card_factions(card):
                self.show_error("Карта не подходит по фракциям!")
                return False

            # Находим пустой слот
            empty_slot_found = False
            for i, (attack, defense) in enumerate(self.table):
                if not attack:
                    empty_slot_found = True
                    self.table[i] = (card, None)
                    self.faction_manager.add_card_factions(card, i * 2)
                    self.waiting_for_defense = True
                    self.cards_pending_defense.append(i)
                    self.defense_timeout = pygame.time.get_ticks() + 5000
                    self.can_attack = False
                    return True
                    
            if not empty_slot_found:
                self.show_error("Нет места на столе!")
                return False

        except Exception as e:
            self.show_error(f"Ошибка: {str(e)}")
            return False

    def process_defense_card(self, card, player):
        """Обработка размещения защитной карты"""
        try:
            if player != self.current_defender:
                self.show_error("Вы не можете защищаться!")
                return False
                
            if self.phase != "DEFENSE":
                self.show_error("Сейчас не фаза защиты!")
                return False

            # Поиск карты для защиты
            for i, (attack, defense) in enumerate(self.table):
                if attack and not defense and attack.rank < card.rank:
                    self.table[i] = (attack, card)
                    self.faction_manager.add_card_factions(card, i * 2 + 1)
                    self.cards_pending_defense.remove(i)
                    if not self.cards_pending_defense:
                        self.waiting_for_defense = False
                        self.can_attack = True
                    return True
                    
            self.show_error("Нет подходящей карты для защиты!")
            return False

        except Exception as e:
            self.show_error(f"Ошибка: {str(e)}")
            return False

    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        self.error_message = message
        self.error_time = pygame.time.get_ticks()

    def update(self):
        """Обновление состояния игры"""
        current_time = pygame.time.get_ticks()
        
        # Очистка сообщения об ошибке после таймаута
        if self.error_message and current_time - self.error_time > self.ERROR_DISPLAY_TIME:
            self.error_message = None
            self.error_time = None

    def switch_players(self):
        self.current_attacker, self.current_defender = self.current_defender, self.current_attacker
        self.phase = "ATTACK"
        self.active_factions.clear()

    def take_cards(self, defender):
        """Обработка взятия карт защищающимся игроком"""
        try:
            if self.phase != "DEFENSE":
                self.show_error("Брать карты можно только в фазе защиты!")
                return False
                
            if defender != self.current_defender:
                self.show_error("Только защищающийся игрок может брать карты!")
                return False
                
            if self.cards_taken:
                self.show_error("Карты уже были взяты в этот ход!")
                return False

            # Добавляем все карты со стола в руку защищающегося
            cards_added = False
            for i, (attack, defense) in enumerate(self.table):
                if attack and not defense:
                    defender.hand.append(attack)
                    cards_added = True
                if defense:  # Если есть карта защиты, тоже добавляем
                    defender.hand.append(defense)

            if not cards_added:
                self.show_error("Нет карт для взятия!")
                return False

            # Очищаем стол
            self.table = [(None, None) for _ in range(6)]
            self.active_factions.clear()
            self.faction_manager.clear()
            self.cards_taken = True
            self.phase = "ATTACK"  # Переключаем фазу на атаку
            self.waiting_for_defense = False
            self.cards_pending_defense = []
            self.can_attack = True
            
            # Меняем игроков местами
            self.current_attacker, self.current_defender = self.current_defender, self.current_attacker
            
            return True

        except Exception as e:
            self.show_error(f"Ошибка при взятии карт: {str(e)}")
            return False

class DraggableCard:
    def __init__(self, card, x, y, owner):
        self.card = card
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.dragging = False
        self.original_pos = (x, y)
        self.owner = owner  # Добавляем владельца карты

    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Проверяем, может ли игрок двигать карту
                if (game_state.phase == "ATTACK" and self.owner == game_state.current_attacker) or \
                   (game_state.phase == "DEFENSE" and self.owner == game_state.current_defender):
                    self.dragging = True
                    return True
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            if TABLE_AREA.colliderect(self.rect):
                # Проверяем правила размещения карты
                if self.can_place_card(game_state):
                    return True
            self.rect.x, self.rect.y = self.original_pos
            return False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - CARD_WIDTH//2
            self.rect.y = event.pos[1] - CARD_HEIGHT//2

    def can_place_card(self, game_state):
        if game_state.phase == "ATTACK":
            # Проверка правил для атакующей карты
            if not game_state.active_factions:
                return True
            return bool(self.card.faction_ids & game_state.active_factions)
        else:  # DEFENSE
            # Находим карту атаки, которую пытаемся покрыть
            for i, (attack_card, defense_card) in enumerate(game_state.table):
                if attack_card and not defense_card:
                    if self.card.rank > attack_card.rank:
                        # Проверка на оби фракции
                        if self.card.faction_ids & game_state.active_factions:
                            return True
            return False

def draw_card(screen, card, x, y):
    """Рисует карту на экране."""
    pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
    
    # Отображение имени карты
    text_surface = font.render(f"{card.name}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 5))
    
    # Отображение ранга
    text_surface = font.render(f"Rank: {card.rank}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 25))
    
    # Отображение номеров фракций
    factions_text = ', '.join(str(fid) for fid in card.faction_ids)
    text_surface = font.render(f"Factions: {factions_text}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 45))

def draw_game_state(screen, font, game_state):
    current_y = INFO_PANEL_TOP
    
    # Отображение фазы
    phase_text = f"Phase: {game_state.phase}"
    text_surface = font.render(phase_text, True, BLACK)
    screen.blit(text_surface, (INFO_PANEL_LEFT, current_y))
    current_y += INFO_LINE_HEIGHT
    
    # Отображение активных фракций
    active_factions_text = f"Active Factions: {', '.join(map(str, game_state.active_factions))}"
    text_surface = font.render(active_factions_text, True, BLACK)
    screen.blit(text_surface, (INFO_PANEL_LEFT, current_y))
    current_y += INFO_LINE_HEIGHT
    
    # Отображение игроков
    attacker_text = f"Attacker: {game_state.current_attacker.name}"
    defender_text = f"Defender: {game_state.current_defender.name}"
    screen.blit(font.render(attacker_text, True, BLACK), (INFO_PANEL_LEFT, current_y))
    current_y += INFO_LINE_HEIGHT
    screen.blit(font.render(defender_text, True, BLACK), (INFO_PANEL_LEFT, current_y))
    current_y += INFO_LINE_HEIGHT
    
    # Отображение информации о колоде
    deck_text = f"Cards in Deck: {len(game_state.deck.cards)}"
    discard_text = f"Cards in Discard Pile: {len(game_state.discard_pile)}"
    screen.blit(font.render(deck_text, True, BLACK), (INFO_PANEL_LEFT, current_y))
    current_y += INFO_LINE_HEIGHT
    screen.blit(font.render(discard_text, True, BLACK), (INFO_PANEL_LEFT, current_y))

def update_draggable_cards(player, y_position):
    """Обновляет список перетаскиваемых карт для игрока"""
    return [
        DraggableCard(
            card,
            CARDS_START_X + i * CARDS_SPACING,
            y_position,
            player
        ) for i, card in enumerate(player.hand)
    ]

def process_card_placement(card, game_state, player1_cards, player2_cards):
    """Обрабатывает размещение карты на столе"""
    if game_state.phase == "ATTACK":
        if game_state.process_attack_card(card.card, card.owner):
            if card in player1_cards:
                player1_cards.remove(card)
            else:
                player2_cards.remove(card)
    else:  # DEFENSE
        if game_state.process_defense_card(card.card, card.owner):
            if card in player1_cards:
                player1_cards.remove(card)
            else:
                player2_cards.remove(card)

def draw_game_field(screen, game_state, player1_cards, player2_cards):
    """Отрисовывает игровое поле и все карты"""
    # Отрисовка стола
    pygame.draw.rect(screen, (24, 129, 24), TABLE_AREA, 2)
    
    # Отрисовка карт на столе
    for i, (attack, defense) in enumerate(game_state.table):
        if attack:
            draw_card(screen, attack, 
                    TABLE_AREA.x + i * (CARD_WIDTH + 10), 
                    TABLE_AREA.y)
        if defense:
            draw_card(screen, defense, 
                    TABLE_AREA.x + i * (CARD_WIDTH + 10), 
                    TABLE_AREA.y + CARD_HEIGHT//2)

    # Отрисовка карт игроков
    for card in player1_cards:
        draw_card(screen, card.card, card.rect.x, card.rect.y)
    for card in player2_cards:
        draw_card(screen, card.card, card.rect.x, card.rect.y)

    # Отрисовка со��бщения об ошибке
    if game_state.error_message:
        error_surface = font.render(game_state.error_message, True, (255, 0, 0))
        error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(error_surface, error_rect)

    # Отрисовка текущей фазы и активного игрока
    phase_text = f"Фаза: {'Атака' if game_state.phase == 'ATTACK' else 'Защита'}"
    phase_surface = font.render(phase_text, True, BLACK)
    screen.blit(phase_surface, (1020, 20))

    active_player = game_state.current_attacker.name if game_state.phase == "ATTACK" else game_state.current_defender.name
    player_surface = font.render(f"Ходит: {active_player}", True, BLACK)
    screen.blit(player_surface, (1020, 60))

    if game_state.phase == "DEFENSE" and not game_state.cards_taken:
        pygame.draw.rect(screen, WHITE, TRANSFER_BUTTON)
        text_surface = font.render("Transfer", True, BLACK)
        screen.blit(text_surface, (TRANSFER_BUTTON.x + 10, TRANSFER_BUTTON.y + 15))

def highlight_valid_targets(screen, card, game_state):
    """Подсвечивает возможные цели для карты"""
    if game_state.phase == "DEFENSE":
        for i, (attack, defense) in enumerate(game_state.table):
            if attack and not defense and attack.rank < card.rank:
                # Рисуем зеленую рамку вокруг возможной цели
                target_rect = pygame.Rect(
                    TABLE_AREA.x + i * (CARD_WIDTH + 10),
                    TABLE_AREA.y,
                    CARD_WIDTH,
                    CARD_HEIGHT
                )
                pygame.draw.rect(screen, (0, 255, 0), target_rect, 2)

def main():
    try:
        # Инициализация игры
        game_state = GameState()
        game_state.deck = Deck()
        populate_deck(game_state.deck)
        random.shuffle(game_state.deck.cards)
        
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        deal_cards(game_state.deck, [player1, player2])

        # Определение первого игрока по наименьшему рангу
        game_state.current_attacker = min([player1, player2], 
                                      key=lambda p: min(card.rank for card in p.hand))
        game_state.current_defender = player2 if game_state.current_attacker == player1 else player1

        # Создание перетаскиваемых карт
        player1_cards = [
            DraggableCard(card, CARDS_START_X + i * CARDS_SPACING, 
                         PLAYER1_CARDS_Y, player1)
            for i, card in enumerate(player1.hand)
        ]
        player2_cards = [
            DraggableCard(card, CARDS_START_X + i * CARDS_SPACING,
                         PLAYER2_CARDS_Y, player2)
            for i, card in enumerate(player2.hand)
        ]

        running = True
        while running:
            try:
                screen.fill(BACKGROUND_COLOR)
                
                # Обновление состояния игры
                game_state.update()
                
                # Проверка окончания игры
                if not player1_cards or not player2_cards:
                    game_state.is_game_over = True
                    game_state.winner = (player1 if not player1_cards else player2)
                    print(f"{game_state.winner.name} wins!")
                    running = False
                    continue

                # Отрисовка игрового состояния
                draw_game_state(screen, font, game_state)
                
                # Отрисовка кнопок
                pygame.draw.rect(screen, WHITE, END_TURN_BUTTON)
                text_surface = font.render("End Turn", True, BLACK)
                screen.blit(text_surface, (END_TURN_BUTTON.x + 10, END_TURN_BUTTON.y + 15))

                # Отрисовка кнопки взятия карт только для защищающегося в фазе защиты
                if game_state.phase == "DEFENSE" and not game_state.cards_taken:
                    pygame.draw.rect(screen, WHITE, TAKE_CARDS_BUTTON)
                    text_surface = font.render("Take Cards", True, BLACK)
                    screen.blit(text_surface, (TAKE_CARDS_BUTTON.x + 10, TAKE_CARDS_BUTTON.y + 15))

                # Обработка событий
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Обработка нажатия кнопок
                        if END_TURN_BUTTON.collidepoint(event.pos):
                            if game_state.phase == "ATTACK":
                                game_state.phase = "DEFENSE"
                            else:
                                game_state.switch_players()
                                game_state.cards_taken = False
                                game_state.faction_manager.clear()

                        elif (TAKE_CARDS_BUTTON.collidepoint(event.pos) and 
                              game_state.phase == "DEFENSE" and 
                              not game_state.cards_taken):
                            try:
                                if game_state.take_cards(game_state.current_defender):
                                    # Обновляем отображаемые карты
                                    if game_state.current_defender == player1:
                                        player1_cards = update_draggable_cards(player1, PLAYER1_CARDS_Y)
                                    else:
                                        player2_cards = update_draggable_cards(player2, PLAYER2_CARDS_Y)
                            except Exception as e:
                                game_state.show_error(f"Ошибка при взятии карт: {str(e)}")

                    # Обработка перетаскивания карт с защитой от ошибок
                    for card in player1_cards + player2_cards:
                        try:
                            if card.handle_event(event, game_state):
                                process_card_placement(card, game_state, player1_cards, player2_cards)
                        except Exception as e:
                            game_state.show_error(f"Ошибка при перемещении карты: {str(e)}")

                # Отрисовка игрового поля и карт
                draw_game_field(screen, game_state, player1_cards, player2_cards)
                
                pygame.display.flip()

            except Exception as e:
                game_state.show_error(f"Ошибка в игровом цикле: {str(e)}")
                continue

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()