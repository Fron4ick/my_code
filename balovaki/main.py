import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os
from datetime import datetime
import random
import math

# --- Конфигурация ---
CANVAS_SIZE = 64  # Размер виртуального холста в пикселях
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PIXEL_SIZE = 8  # Размер одного пикселя на экране

# Базовые цвета для палитры (RGB)
BASE_COLORS = [
    (255, 255, 255),  # Белый
    (0, 0, 0),        # Черный
    (255, 0, 0),      # Красный
    (0, 255, 0),      # Зеленый
    (0, 0, 255),      # Синий
    (255, 255, 0),    # Желтый
    (255, 0, 255),    # Пурпурный
    (0, 255, 255),    # Циан
    (128, 128, 128),  # Серый
    (255, 128, 0),    # Оранжевый
    (128, 0, 255),    # Фиолетовый
    (0, 128, 128),    # Бирюзовый
]

class PixelArtEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Пиксель-арт редактор 64×64")
        
        # Создание директории для сохранения
        script_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
        date_str = datetime.now().strftime("%S.%M.%H.%d.%m.%y")
        self.save_directory = os.path.join(script_dir, f'imgs_{date_str}')
        os.makedirs(self.save_directory, exist_ok=True)
        self.save_counter = 0
        
        # Холст (numpy array для быстрой работы)
        self.canvas_data = np.ones((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8) * 255
        
        # Текущие цвета и сиды
        self.current_brush_color = (0, 0, 0)
        self.current_bg_color = (255, 255, 255)
        self.brush_seed = self.generate_seed()
        self.bg_seed = self.generate_seed()
        self.ensure_seeds_different()
        
        self.drawing = False
        
        # UI
        self.setup_ui()
        self.update_canvas_display()
        
        # Биндинги клавиш
        self.root.bind('s', lambda e: self.save_and_new())
        self.root.bind('S', lambda e: self.save_and_new())
        self.root.bind('c', lambda e: self.clear_canvas())
        self.root.bind('C', lambda e: self.clear_canvas())
        self.root.bind('v', lambda e: self.quit_app(False))
        self.root.bind('V', lambda e: self.quit_app(True))
        
    def generate_seed(self):
        """Генерирует сид из 6 hex символов"""
        angle_idx = random.randint(0, 12)  # 0 до C (12)
        colors = [random.randint(0, len(BASE_COLORS)-1) for _ in range(5)]
        return f"{angle_idx:X}{colors[0]:X}{colors[1]:X}{colors[2]:X}{colors[3]:X}{colors[4]:X}"
    
    def ensure_seeds_different(self):
        """Обеспечивает различие сидов по правилам"""
        while True:
            if self.brush_seed[0] == self.bg_seed[0]:
                self.bg_seed = self.generate_seed()
                continue
            
            # Проверка на минимум 2 различия в цветовых ключах
            differences = sum(1 for i in range(1, 6) if self.brush_seed[i] != self.bg_seed[i])
            if differences >= 2:
                break
            self.bg_seed = self.generate_seed()
    
    def seed_to_color(self, seed):
        """Преобразует сид в миксовый цвет"""
        angle_idx = int(seed[0], 16)
        angle = angle_idx * math.pi / 12
        
        color_indices = [int(seed[i], 16) % len(BASE_COLORS) for i in range(1, 6)]
        colors = [BASE_COLORS[idx] for idx in color_indices]
        
        # Миксуем цвета с весами на основе угла
        weights = [1 + math.sin(angle + i) for i in range(5)]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        r = sum(c[0] * w for c, w in zip(colors, weights))
        g = sum(c[1] * w for c, w in zip(colors, weights))
        b = sum(c[2] * w for c, w in zip(colors, weights))
        
        return (int(r), int(g), int(b))
    
    def setup_ui(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель с кнопками и палитрами
        left_panel = tk.Frame(main_frame, width=200, bg='#f0f0f0')
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        # Кнопки управления
        btn_frame = tk.Frame(left_panel, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Сохранить (S)", command=self.save_and_new, width=15).pack(pady=2)
        tk.Button(btn_frame, text="Очистить (C)", command=self.clear_canvas, width=15).pack(pady=2)
        tk.Button(btn_frame, text="Выход (V)", command=lambda: self.quit_app(False), width=15).pack(pady=2)
        tk.Button(btn_frame, text="Сохр.и выход (Shift+V)", command=lambda: self.quit_app(True), width=15).pack(pady=2)
        
        # Палитра кисти
        tk.Label(left_panel, text="Цвет кисти", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        self.brush_palette = tk.Frame(left_panel, bg='#f0f0f0')
        self.brush_palette.pack()
        self.create_color_palette(self.brush_palette, 'brush')
        
        # Палитра фона
        tk.Label(left_panel, text="Цвет фона", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        self.bg_palette = tk.Frame(left_panel, bg='#f0f0f0')
        self.bg_palette.pack()
        self.create_color_palette(self.bg_palette, 'bg')
        
        # Область холста
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_display = tk.Canvas(canvas_frame, width=CANVAS_SIZE*PIXEL_SIZE, 
                                        height=CANVAS_SIZE*PIXEL_SIZE, bg='white')
        self.canvas_display.pack(padx=20, pady=20)
        
        # Биндинги мыши
        self.canvas_display.bind('<Button-1>', self.start_drawing)
        self.canvas_display.bind('<B1-Motion>', self.draw)
        self.canvas_display.bind('<ButtonRelease-1>', self.stop_drawing)
    
    def create_color_palette(self, parent, palette_type):
        """Создает палитру цветов в виде двух колонок"""
        for i in range(6):
            row_frame = tk.Frame(parent, bg='#f0f0f0')
            row_frame.pack(pady=1)
            
            for j in range(2):
                idx = i * 2 + j
                if idx < len(BASE_COLORS):
                    color = BASE_COLORS[idx]
                    color_hex = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
                    btn = tk.Button(row_frame, bg=color_hex, width=4, height=2,
                                  command=lambda c=color, pt=palette_type: self.select_color(c, pt))
                    btn.pack(side=tk.LEFT, padx=2)
                elif idx == len(BASE_COLORS):
                    # Кнопка микс
                    btn = tk.Button(row_frame, text="MIX", width=4, height=2,
                                  command=lambda pt=palette_type: self.select_mix_color(pt))
                    btn.pack(side=tk.LEFT, padx=2)
    
    def select_color(self, color, palette_type):
        """Выбор обычного цвета"""
        if palette_type == 'brush':
            self.current_brush_color = color
            print(f"Цвет кисти: {color}")
        else:
            self.current_bg_color = color
            self.fill_background(color)
            print(f"Цвет фона: {color}")
    
    def select_mix_color(self, palette_type):
        """Выбор миксового цвета"""
        if palette_type == 'brush':
            self.brush_seed = self.generate_seed()
            self.ensure_seeds_different()
            self.current_brush_color = self.seed_to_color(self.brush_seed)
            print(f"Микс кисти (сид: {self.brush_seed}): {self.current_brush_color}")
        else:
            self.bg_seed = self.generate_seed()
            self.ensure_seeds_different()
            self.current_bg_color = self.seed_to_color(self.bg_seed)
            self.fill_background(self.current_bg_color)
            print(f"Микс фона (сид: {self.bg_seed}): {self.current_bg_color}")
    
    def fill_background(self, color):
        """Заливает фон цветом"""
        self.canvas_data[:, :] = color
        self.update_canvas_display()
    
    def start_drawing(self, event):
        self.drawing = True
        self.draw(event)
    
    def stop_drawing(self, event):
        self.drawing = False
    
    def draw(self, event):
        """Рисование с размытием"""
        if not self.drawing:
            return
        
        x = int(event.x / PIXEL_SIZE)
        y = int(event.y / PIXEL_SIZE)
        
        if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
            # Рисуем с мягким градиентом (3x3 область с альфа-блендингом)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < CANVAS_SIZE and 0 <= ny < CANVAS_SIZE:
                        # Вычисляем вес (центр сильнее)
                        distance = math.sqrt(dx*dx + dy*dy)
                        alpha = max(0, 1 - distance / 1.5)
                        
                        # Блендим цвета
                        old_color = self.canvas_data[ny, nx]
                        new_color = [
                            int(old_color[i] * (1 - alpha) + self.current_brush_color[i] * alpha)
                            for i in range(3)
                        ]
                        self.canvas_data[ny, nx] = new_color
            
            self.update_canvas_display()
    
    def update_canvas_display(self):
        """Обновляет отображение холста"""
        # Создаем PIL изображение
        img = Image.fromarray(self.canvas_data, 'RGB')
        # Масштабируем
        img = img.resize((CANVAS_SIZE * PIXEL_SIZE, CANVAS_SIZE * PIXEL_SIZE), Image.NEAREST)
        
        # Конвертируем в PhotoImage
        self.photo = tk.PhotoImage(data=img.tobytes(), width=img.width, height=img.height)
        self.canvas_display.create_image(0, 0, image=self.photo, anchor=tk.NW)
    
    def save_and_new(self):
        """Сохраняет холст и создает новый"""
        filename = os.path.join(self.save_directory, f'canvas_{self.save_counter:04d}.png')
        img = Image.fromarray(self.canvas_data, 'RGB')
        img.save(filename)
        print(f"Холст сохранен: {filename}")
        
        self.canvas_data[:, :] = 255
        self.save_counter += 1
        self.update_canvas_display()
    
    def clear_canvas(self):
        """Очищает холст"""
        self.canvas_data[:, :] = 255
        self.update_canvas_display()
        print("Холст очищен")
    
    def quit_app(self, save_before_quit):
        """Выход из приложения"""
        if save_before_quit:
            self.save_and_new()
            print("Сохранено и завершено")
        else:
            print("Завершено без сохранения")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtEditor(root)
    root.mainloop()
