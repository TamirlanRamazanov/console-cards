import pygame
import math

class CardView:
    def __init__(self, card, width=400):
        # Базовые размеры
        self.width = width
        self.height = int(width * 1.5)  # Соотношение 2:3
        
        # Цвета
        self.BEIGE = (245, 245, 220)
        self.LIGHT_BLUE = (173, 216, 230)
        self.DARK_BLUE = (135, 206, 235)
        self.BROWN = (139, 69, 19)
        self.LIGHT_BROWN = (205, 133, 63)
        self.BLACK = (0, 0, 0)
        
        # Данные карты
        self.card = card
        
        # Создание поверхности карты
        self.surface = pygame.Surface((self.width, self.height))
        self.render()
        
    def create_gradient_background(self, rect):
        gradient = pygame.Surface(rect.size)
        for y in range(rect.height):
            # Создаем градиент от светло-голубого к более темному
            color = pygame.Color(self.LIGHT_BLUE)
            dark_color = pygame.Color(self.DARK_BLUE)
            factor = y / rect.height
            r = int(color.r + (dark_color.r - color.r) * factor)
            g = int(color.g + (dark_color.g - color.g) * factor)
            b = int(color.b + (dark_color.b - color.b) * factor)
            pygame.draw.line(gradient, (r, g, b), (0, y), (rect.width, y))
        return gradient
        
    def render(self):
        # Фон карты (бежевый)
        self.surface.fill(self.BEIGE)
        
        # Внутренняя часть с отступами
        padding = int(self.width * 0.05)
        inner_rect = pygame.Rect(
            padding, padding,
            self.width - 2*padding,
            self.height - 2*padding
        )
        
        # Градиентный фон
        gradient = self.create_gradient_background(inner_rect)
        self.surface.blit(gradient, inner_rect)
        
        # Овал для портрета
        oval_height = int(self.height * 0.6)
        oval_width = int(self.width * 0.8)
        oval_x = (self.width - oval_width) // 2
        oval_y = padding + int(self.height * 0.1)
        pygame.draw.ellipse(self.surface, self.BROWN, 
                          (oval_x, oval_y, oval_width, oval_height), 3)
        
        # Кружок для ранга
        rank_circle_radius = int(self.width * 0.12)
        rank_x = self.width - rank_circle_radius - padding - 10
        rank_y = oval_y + rank_circle_radius - 10
        pygame.draw.circle(self.surface, self.BROWN, 
                         (rank_x, rank_y), rank_circle_radius, 2)
        
        # Отрисовка ранга
        font = pygame.font.Font(None, int(rank_circle_radius * 1.5))
        rank_text = font.render(str(self.card.rank), True, self.BLACK)
        rank_rect = rank_text.get_rect(center=(rank_x, rank_y))
        self.surface.blit(rank_text, rank_rect)
        
        # Кружки для фракций
        faction_circle_radius = int(self.width * 0.08)
        faction_y = oval_y + oval_height + faction_circle_radius
        spacing = (self.width - 2*padding - 5*faction_circle_radius*2) // 4
        
        for i in range(5):
            x = padding + faction_circle_radius + i * (faction_circle_radius*2 + spacing)
            pygame.draw.circle(self.surface, self.BROWN, 
                             (x, faction_y), faction_circle_radius, 2)
        
        # Полоска для имени
        name_height = int(self.height * 0.1)
        name_y = self.height - name_height - padding
        
        # Создаем параболическую форму для полоски имени
        points = []
        name_width = self.width - 2*padding
        curve_height = 5  # Высота изгиба параболы
        
        for x in range(name_width):
            # Параболическая формула
            y = 4 * curve_height * (x/name_width) * (1 - x/name_width)
            points.append((x + padding, name_y + y))
            
        # Добавляем нижние точки для замкнутой формы
        points.extend([
            (self.width - padding, name_y + name_height),
            (padding, name_y + name_height)
        ])
        
        pygame.draw.polygon(self.surface, self.LIGHT_BROWN, points)
        
        # Отрисовка имени
        name_font = pygame.font.Font(None, int(name_height * 0.7))
        name_text = name_font.render(self.card.name, True, self.BLACK)
        name_rect = name_text.get_rect(
            center=(self.width//2, name_y + name_height//2)
        )
        self.surface.blit(name_text, name_rect)

    def draw(self, screen, pos):
        screen.blit(self.surface, pos)


# Пример использования:
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Card View Test")
    
    # Создаем тестовую карту
    from card import Card
    test_card = Card("Monkey D. Luffy", 5)
    test_card.add_faction("pirate")
    test_card.add_faction("strawhat")
    
    # Создаем отображение карты
    card_view = CardView(test_card)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill((255, 255, 255))  # Белый фон
        card_view.draw(screen, (300, 100))  # Отрисовка карты
        pygame.display.flip()
        
    pygame.quit() 