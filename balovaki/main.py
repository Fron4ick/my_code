import pygame
import os
import random
import math
from datetime import datetime
from typing import Tuple, List, Optional, Dict

class AdvancedPixelCanvas:
    """
    Продвинутый пиксельный холст с системой микширования цветов и интерфейсом.
    """
    
    def __init__(self, canvas_size: int = 64, window_size: int = 600,
                 background_seed: str = "a1b2c3", brush_seed: str = "d4e5f6"):
        """
        Инициализация холста с системой микширования цветов.
        
        Args:
            canvas_size: Размер виртуального холста
            window_size: Размер окна приложения
            background_seed: Сид для генерации фонового градиента
            brush_seed: Сид для генерации кисти с градиентом
        """
        self.canvas_size = canvas_size
        self.window_size = window_size
        self.ui_width = 120  # Ширина левой панели с интерфейсом
        
        # Валидация сидов
        self.background_seed = self._validate_seed(background_seed, "background")
        self.brush_seed = self._validate_seed(brush_seed, "brush")
        
        # Проверка что сиды не совпадают по условиям
        self._validate_seeds_difference()
        
        # Генерация цветовых палитр из сидов
        self.background_colors = self._generate_colors_from_seed(self.background_seed)
        self.brush_colors = self._generate_colors_from_seed(self.brush_seed)
        
        # Текущие цвета
        self.current_bg_color = self.background_colors[0]
        self.current_brush_color = self.brush_colors[0]
        self.mix_brush_color = self._generate_mix_color(self.brush_seed)
        self.mix_bg_color = self._generate_mix_color(self.background_seed)
        
        # Настройки кисти
        self.brush_size = 2
        self.brush_hardness = 0.7  # Жесткость кисти (0-1)
        
        # Инициализация Pygame
        self._initialize_pygame()
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _validate_seed(self, seed: str, seed_type: str) -> str:
        """Валидация и нормализация сида."""
        if len(seed) != 6:
            raise ValueError(f"Сид {seed_type} должен содержать ровно 6 hex-символов")
        
        # Проверяем что все символы валидные hex
        try:
            int(seed, 16)
        except ValueError:
            raise ValueError(f"Сид {seed_type} содержит невалидные hex-символы")
        
        return seed.lower()
    
    def _validate_seeds_difference(self) -> None:
        """Проверяет что сиды отличаются по первому символу и минимум по двум цветовым."""
        if self.background_seed[0] == self.brush_seed[0]:
            raise ValueError("Сид фона и кисти не могут совпадать по первому символу")
        
        # Сравниваем цветовые символы (позиции 1-5)
        bg_color_chars = set(self.background_seed[1:5])
        brush_color_chars = set(self.brush_seed[1:5])
        
        common_chars = bg_color_chars.intersection(brush_color_chars)
        if len(common_chars) > 3:  # Если совпадает больше 3 цветовых символов
            raise ValueError("Сид фона и кисти должны отличаться минимум по 2 цветовым символам")
    
    def _generate_colors_from_seed(self, seed: str) -> List[Tuple[int, int, int]]:
        """Генерирует 5 цветов из сида."""
        colors = []
        angle = (int(seed[0], 16) * math.pi / 12)  # Угол наклона
        
        for i in range(5):
            color_key = int(seed[i+1], 16)  # Берем символы 1-5 для цветов
            
            # Создаем цвет на основе ключа и угла
            r = int(128 + 127 * math.cos(angle + color_key * 0.8))
            g = int(128 + 127 * math.sin(angle + color_key * 1.2))
            b = int(128 + 127 * math.cos(angle + color_key * 1.6))
            
            colors.append((r, g, b))
        
        return colors
    
    def _generate_mix_color(self, seed: str) -> Tuple[int, int, int]:
        """Генерирует микс-цвет на основе всего сида."""
        angle = (int(seed[0], 16) * math.pi / 12)
        
        # Смешиваем все цветовые компоненты
        total_r, total_g, total_b = 0, 0, 0
        
        for i in range(5):
            color_key = int(seed[i+1], 16)
            weight = (i + 1) / 15  # Вес каждого цвета
            
            total_r += weight * (128 + 127 * math.cos(angle + color_key * 0.8))
            total_g += weight * (128 + 127 * math.sin(angle + color_key * 1.2))
            total_b += weight * (128 + 127 * math.cos(angle + color_key * 1.6))
        
        return (int(total_r), int(total_g), int(total_b))
    
    def _initialize_pygame(self) -> None:
        """Инициализация Pygame с настройками."""
        pygame.init()
        
        # Убираем иконку pygame
        pygame.display.set_icon(pygame.Surface((1, 1)))
        
        # Создаем окно
        total_width = self.window_size + self.ui_width
        self._screen = pygame.display.set_mode((total_width, self.window_size))
        pygame.display.set_caption("Advanced Pixel Canvas")
        
        # Создаем холст для рисования
        self._canvas = pygame.Surface((self.canvas_size, self.canvas_size))
        self._canvas.fill(self.current_bg_color)
        
        # Создаем папку для сохранения
        self._create_save_directory()
        
        # Счетчик сохранений
        self._save_counter = 0
    
    def _create_save_directory(self) -> None:
        """Создает папку для сохранения изображений."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        date_str = datetime.now().strftime("%S.%M.%H.%d.%m.%y")
        self._save_directory = os.path.join(script_dir, f'imgs_{date_str}')
        os.makedirs(self._save_directory, exist_ok=True)
    
    def _create_ui_elements(self) -> None:
        """Создает элементы интерфейса."""
        self.buttons = {
            'save': {'rect': pygame.Rect(10, 10, 100, 30), 'text': 'Save (S)', 'action': 'save'},
            'clear': {'rect': pygame.Rect(10, 50, 100, 30), 'text': 'Clear (C)', 'action': 'clear'},
            'quit': {'rect': pygame.Rect(10, 90, 100, 30), 'text': 'Quit (V)', 'action': 'quit'},
            'save_quit': {'rect': pygame.Rect(10, 130, 100, 30), 'text': 'Save+Quit', 'action': 'save_quit'},
        }
        
        # Области выбора цвета кисти
        self.brush_color_rects = []
        for i in range(5):
            rect = pygame.Rect(10, 180 + i * 40, 40, 30)
            self.brush_color_rects.append({'rect': rect, 'color': self.brush_colors[i]})
        
        # Область миксовой кисти
        self.mix_brush_rect = pygame.Rect(60, 180, 40, 30)
        
        # Области выбора цвета фона
        self.bg_color_rects = []
        for i in range(5):
            rect = pygame.Rect(10, 380 + i * 40, 40, 30)
            self.bg_color_rects.append({'rect': rect, 'color': self.background_colors[i]})
        
        # Область миксового фона
        self.mix_bg_rect = pygame.Rect(60, 380, 40, 30)
    
    def _draw_soft_brush(self, pos: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Рисует с размытой кистью."""
        canvas_x = int((pos[0] - self.ui_width) / self.window_size * self.canvas_size)
        canvas_y = int(pos[1] / self.window_size * self.canvas_size)
        
        # Пропускаем если кликнули по UI
        if canvas_x < 0 or canvas_y < 0 or canvas_x >= self.canvas_size or canvas_y >= self.canvas_size:
            return
        
        radius = self.brush_size
        base_color = pygame.Color(*color)
        
        # Создаем временную поверхность для альфа-рисования
        temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        for y in range(-radius, radius):
            for x in range(-radius, radius):
                distance = math.sqrt(x*x + y*y)
                if distance <= radius:
                    # Вычисляем альфу на основе расстояния и жесткости
                    alpha = int(255 * (1 - distance / radius) * self.brush_hardness)
                    if alpha > 0:
                        draw_color = (*base_color[:3], alpha)
                        temp_surface.set_at((x + radius, y + radius), draw_color)
        
        # Накладываем временную поверхность на холст
        self._canvas.blit(temp_surface, (canvas_x - radius, canvas_y - radius), 
                         special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _draw_ui(self) -> None:
        """Отрисовывает интерфейс."""
        # Фон UI
        ui_bg = pygame.Rect(0, 0, self.ui_width, self.window_size)
        pygame.draw.rect(self._screen, (50, 50, 50), ui_bg)
        
        # Кнопки
        font = pygame.font.SysFont(None, 24)
        for button_id, button_data in self.buttons.items():
            color = (100, 100, 200) if button_id in ['save', 'save_quit'] else (200, 100, 100)
            pygame.draw.rect(self._screen, color, button_data['rect'])
            text = font.render(button_data['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button_data['rect'].center)
            self._screen.blit(text, text_rect)
        
        # Цвета кисти
        title = font.render("Brush Colors:", True, (255, 255, 255))
        self._screen.blit(title, (10, 150))
        
        for i, color_rect in enumerate(self.brush_color_rects):
            pygame.draw.rect(self._screen, color_rect['color'], color_rect['rect'])
        
        # Микс-цвет кисти
        pygame.draw.rect(self._screen, self.mix_brush_color, self.mix_brush_rect)
        mix_text = font.render("Mix", True, (255, 255, 255))
        self._screen.blit(mix_text, (65, 215))
        
        # Цвета фона
        title = font.render("BG Colors:", True, (255, 255, 255))
        self._screen.blit(title, (10, 350))
        
        for i, color_rect in enumerate(self.bg_color_rects):
            pygame.draw.rect(self._screen, color_rect['color'], color_rect['rect'])
        
        # Микс-цвет фона
        pygame.draw.rect(self._screen, self.mix_bg_color, self.mix_bg_rect)
        mix_text = font.render("Mix", True, (255, 255, 255))
        self._screen.blit(mix_text, (65, 415))
        
        # Информация о сидах
        seed_font = pygame.font.SysFont(None, 18)
        bg_seed_text = seed_font.render(f"BG: {self.background_seed}", True, (200, 200, 200))
        brush_seed_text = seed_font.render(f"Brush: {self.brush_seed}", True, (200, 200, 200))
        self._screen.blit(bg_seed_text, (10, 550))
        self._screen.blit(brush_seed_text, (10, 570))
    
    def _handle_ui_click(self, pos: Tuple[int, int]) -> bool:
        """Обрабатывает клики по интерфейсу."""
        # Проверяем кнопки
        for button_id, button_data in self.buttons.items():
            if button_data['rect'].collidepoint(pos):
                return button_data['action']
        
        # Проверяем выбор цвета кисти
        for i, color_rect in enumerate(self.brush_color_rects):
            if color_rect['rect'].collidepoint(pos):
                self.current_brush_color = self.brush_colors[i]
                return 'color_selected'
        
        if self.mix_brush_rect.collidepoint(pos):
            self.current_brush_color = self.mix_brush_color
            return 'color_selected'
        
        # Проверяем выбор цвета фона
        for i, color_rect in enumerate(self.bg_color_rects):
            if color_rect['rect'].collidepoint(pos):
                self.current_bg_color = self.background_colors[i]
                self._canvas.fill(self.current_bg_color)
                return 'bg_selected'
        
        if self.mix_bg_rect.collidepoint(pos):
            self.current_bg_color = self.mix_bg_color
            self._canvas.fill(self.current_bg_color)
            return 'bg_selected'
        
        return None
    
    def _handle_events(self) -> bool:
        """Обработка событий."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    action = self._handle_ui_click(event.pos)
                    if action == 'save':
                        self.save_canvas()
                        self.clear_canvas()
                    elif action == 'clear':
                        self.clear_canvas()
                    elif action == 'quit':
                        return False
                    elif action == 'save_quit':
                        self.save_canvas()
                        return False
            
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Левая кнопка зажата
                    # Рисуем только если не в UI области
                    if event.pos[0] > self.ui_width:
                        self._draw_soft_brush(event.pos, self.current_brush_color)
            
            elif event.type == pygame.KEYDOWN:
                if not self._handle_keydown(event):
                    return False
        
        return True
    
    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Обработка горячих клавиш."""
        keys = pygame.key.get_pressed()
        
        if event.key == pygame.K_s:
            self.save_canvas()
            self.clear_canvas()
            return True
            
        elif event.key == pygame.K_v:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.save_canvas()
                print("Холст сохранен и программа завершена.")
            else:
                print("Программа завершена без сохранения.")
            return False
            
        elif event.key == pygame.K_c:
            self.clear_canvas()
            return True
            
        return True
    
    def _render(self) -> None:
        """Отрисовка всего кадра."""
        # Очищаем экран
        self._screen.fill((0, 0, 0))
        
        # Отрисовываем масштабированный холст
        scaled_canvas = pygame.transform.scale(self._canvas, 
                                             (self.window_size, self.window_size))
        self._screen.blit(scaled_canvas, (self.ui_width, 0))
        
        # Отрисовываем UI
        self._draw_ui()
        
        # Обновляем дисплей
        pygame.display.flip()
    
    def save_canvas(self) -> None:
        """Сохраняет текущий холст."""
        filename = os.path.join(self._save_directory, f'canvas_{self._save_counter:04d}.png')
        pygame.image.save(self._canvas, filename)
        print(f"Холст сохранен как {filename}")
        self._save_counter += 1
    
    def clear_canvas(self) -> None:
        """Очищает холст текущим цветом фона."""
        self._canvas.fill(self.current_bg_color)
        print("Холст очищен.")
    
    def run(self, fps: int = 60) -> None:
        """Запускает главный цикл приложения."""
        clock = pygame.time.Clock()
        running = True
        
        print("Управление:")
        print("  S - Сохранить и очистить холст")
        print("  V - Выйти без сохранения")
        print("  Shift+V - Сохранить и выйти")
        print("  C - Очистить холст")
        print("  ЛКМ - Рисовать")
        print("  ЛКМ на цветах - Выбрать цвет кисти/фона")
        
        while running:
            running = self._handle_events()
            self._render()
            clock.tick(fps)
        
        self.quit()
    
    def quit(self) -> None:
        """Корректно завершает работу."""
        pygame.quit()


# Пример использования
if __name__ == "__main__":
    # Можно задать свои сиды или оставить дефолтные
    app = AdvancedPixelCanvas(
        canvas_size=64,
        window_size=600,
        background_seed="a1b2c3",  # Сид фона
        brush_seed="d4e5f6"        # Сид кисти
    )
    app.run()
