import pygame
import os
from datetime import datetime
from typing import Optional, Tuple

class PixelArtCanvas:
    """
    Класс для создания пиксельного холста для рисования.
    Инкапсулирует всю логику работы с графикой, вводом и сохранением.
    """
    
    def __init__(self, canvas_size: int = 32, window_size: int = 200, 
                 background_color: Tuple[int, int, int] = (255, 255, 255),
                 draw_color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Инициализация холста.
        
        Args:
            canvas_size: Размер виртуального холста в пикселях
            window_size: Размер отображаемого окна в пикселях
            background_color: Цвет фона холста (R, G, B)
            draw_color: Цвет рисования (R, G, B)
        """
        self.canvas_size = canvas_size
        self.window_size = window_size
        self.background_color = background_color
        self.draw_color = draw_color
        
        # Внутреннее состояние
        self._canvas: Optional[pygame.Surface] = None
        self._screen: Optional[pygame.Surface] = None
        self._running = False
        self._drawing = False
        self._save_counter = 0
        self._save_directory = ""
        
        # Инициализация Pygame
        self._initialize_pygame()
        
    def _initialize_pygame(self) -> None:
        """Инициализация графической подсистемы Pygame."""
        pygame.init()
        self._screen = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption("Pixel Art Canvas")
        
        # Создание виртуального холста
        self._canvas = pygame.Surface((self.canvas_size, self.canvas_size))
        self._canvas.fill(self.background_color)
        
        # Создание папки для сохранения
        self._create_save_directory()
    
    def _create_save_directory(self) -> None:
        """Создает папку для сохранения изображений."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        date_str = datetime.now().strftime("%S.%M.%H.%d.%m.%y")
        self._save_directory = os.path.join(script_dir, f'imgs_{date_str}')
        os.makedirs(self._save_directory, exist_ok=True)
    
    def _handle_events(self) -> bool:
        """
        Обработка событий ввода.
        
        Returns:
            bool: False если нужно завершить работу, иначе True
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if not self._handle_keydown(event):
                    return False
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self._drawing = True
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    self._drawing = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if self._drawing:
                    self._draw_on_canvas(event.pos)
                    
        return True
    
    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Обработка нажатий клавиш.
        
        Returns:
            bool: False если нужно завершить работу, иначе True
        """
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
    
    def _draw_on_canvas(self, window_pos: Tuple[int, int]) -> None:
        """Рисует точку на холсте по позиции в окне."""
        canvas_x = int(window_pos[0] / self.window_size * self.canvas_size)
        canvas_y = int(window_pos[1] / self.window_size * self.canvas_size)
        pygame.draw.circle(self._canvas, self.draw_color, (canvas_x, canvas_y), 1)
    
    def _render(self) -> None:
        """Отрисовка текущего состояния."""
        # Масштабируем холст до размеров окна
        scaled_canvas = pygame.transform.scale(self._canvas, 
                                             (self.window_size, self.window_size))
        self._screen.blit(scaled_canvas, (0, 0))
        pygame.display.flip()
    
    def save_canvas(self) -> None:
        """Сохраняет текущий холст в файл."""
        filename = os.path.join(self._save_directory, f'canvas_{self._save_counter:04d}.png')
        pygame.image.save(self._canvas, filename)
        print(f"Холст сохранен как {filename}")
        self._save_counter += 1
    
    def clear_canvas(self) -> None:
        """Очищает холст."""
        self._canvas.fill(self.background_color)
        print("Холст очищен.")
    
    def get_canvas_surface(self) -> pygame.Surface:
        """Возвращает поверхность холста для прямого доступа."""
        return self._canvas
    
    def set_draw_color(self, color: Tuple[int, int, int]) -> None:
        """Устанавливает цвет рисования."""
        self.draw_color = color
    
    def set_background_color(self, color: Tuple[int, int, int]) -> None:
        """Устанавливает цвет фона и очищает холст."""
        self.background_color = color
        self.clear_canvas()
    
    def run(self, fps: int = 60) -> None:
        """
        Запускает главный цикл приложения.
        
        Args:
            fps: Целевая частота кадров
        """
        self._running = True
        clock = pygame.time.Clock()
        
        print("Управление:")
        print("  S - Сохранить и очистить холст")
        print("  V - Выйти без сохранения")
        print("  Shift+V - Сохранить и выйти")
        print("  C - Очистить холст")
        print("  ЛКМ - Рисовать")
        
        while self._running:
            self._running = self._handle_events()
            self._render()
            clock.tick(fps)
        
        self.quit()
    
    def quit(self) -> None:
        """Корректно завершает работу приложения."""
        pygame.quit()


# Пример использования как модуля
if __name__ == "__main__":
    # Создание и запуск экземпляра холста
    app = PixelArtCanvas(
        canvas_size=32,
        window_size=200,
        background_color=(255, 255, 255),  # Белый фон
        draw_color=(0, 0, 0)               # Черные чернила
    )
    app.run()
