import pygame
import os
import random
import math
from datetime import datetime

# Инициализация всех модулей Pygame
pygame.init()

# --- Конфигурационные константы ---
CANVAS_SIZE = 64        # Размер виртуального холста в пикселях (64*64)
MENU_WIDTH = 80         # Ширина меню слева
BUTTON_HEIGHT = 30      # Высота кнопок
WINDOW_HEIGHT = 700     # Высота окна
WINDOW_WIDTH = WINDOW_HEIGHT + MENU_WIDTH  # Общая ширина окна
FPS = 200                # Кадровая частота

# Базовые цвета палитры (ID 0-11)
PALETTE = [
    (255, 255, 255),  # 0: Белый
    (0, 0, 0),        # 1: Черный
    (255, 0, 0),      # 2: Красный
    (0, 255, 0),      # 3: Зеленый
    (0, 0, 255),      # 4: Синий
    (255, 255, 0),    # 5: Желтый
    (255, 0, 255),    # 6: Пурпурный
    (0, 255, 255),    # 7: Голубой
    (128, 128, 128),  # 8: Серый
    (255, 128, 0),    # 9: Оранжевый
    (128, 0, 255),    # A: Фиолетовый
    (0, 128, 128),    # B: Бирюзовый
]

# Цвета интерфейса
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Создаем папку для сохранения изображений
script_dir = os.path.dirname(os.path.abspath(__file__))
date_str = datetime.now().strftime("%S.%M.%H.%d.%m.%y")
save_directory = os.path.join(script_dir, f'imgs_{date_str}')
os.makedirs(save_directory, exist_ok=True)

# --- Настройка дисплея ---
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Мини-холст 64x64")

# Убираем иконку pygame
icon = pygame.Surface((1, 1))
icon.set_alpha(0)
pygame.display.set_icon(icon)

# Виртуальный холст
canvas = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE))
canvas.fill(WHITE)

# Шрифт для текста
font = pygame.font.Font(None, 20)
small_font = pygame.font.Font(None, 16)

# --- Функции для работы с миксовыми цветами ---

def seed_to_params(seed_str):
    """Преобразует 6-hex сид в параметры: угол и 5 цветов"""
    if len(seed_str) != 6:
        return 0, [0, 0, 0, 0, 0]
    
    angle_idx = int(seed_str[0], 16) % 13  # 0-C (0-12)
    angle = angle_idx * math.pi / 12
    colors = [int(c, 16) % 12 for c in seed_str[1:6]]
    return angle, colors

def params_to_seed(angle_idx, colors):
    """Преобразует параметры в 6-hex сид"""
    angle_hex = format(angle_idx % 13, 'X')
    color_hex = ''.join([format(c % 12, 'X') for c in colors])
    return angle_hex + color_hex

def generate_valid_seeds():
    """Генерирует валидные сиды для фона и кисти"""
    while True:
        bg_angle = random.randint(0, 12)
        brush_angle = random.randint(0, 12)
        
        if bg_angle == brush_angle:
            continue
        
        bg_colors = [random.randint(0, 11) for _ in range(5)]
        brush_colors = [random.randint(0, 11) for _ in range(5)]
        
        # Проверяем, что хотя бы 2 цвета отличаются
        diff_count = sum(1 for i in range(5) if bg_colors[i] != brush_colors[i])
        if diff_count >= 2:
            bg_seed = params_to_seed(bg_angle, bg_colors)
            brush_seed = params_to_seed(brush_angle, brush_colors)
            return bg_seed, brush_seed

def get_mixed_color(seed_str, x, y):
    """Вычисляет цвет пикселя на основе сида и координат"""
    angle, colors = seed_to_params(seed_str)
    
    # Вычисляем позицию вдоль линии штриховки
    pos = x * math.cos(angle) + y * math.sin(angle)
    
    # Определяем, какой цвет использовать на основе позиции
    stripe_width = 4
    color_idx = int(pos / stripe_width) % 5
    
    return PALETTE[colors[color_idx]]

def create_mixed_surface(seed_str, size):
    """Создает поверхность с миксовым цветом"""
    surface = pygame.Surface((size, size))
    for y in range(size):
        for x in range(size):
            color = get_mixed_color(seed_str, x, y)
            surface.set_at((x, y), color)
    return surface

# --- Инициализация состояния ---
bg_seed, brush_seed = generate_valid_seeds()
current_bg_color = 0  # Индекс цвета фона (0-11 обычные, 12 - микс)
current_brush_color = 1  # Индекс цвета кисти
save_counter = 0

# Основной цикл программы
clock = pygame.time.Clock()
running = True
drawing = False

def draw_menu():
    """Отрисовка меню слева"""
    # Фон меню
    pygame.draw.rect(screen, GRAY, (0, 0, MENU_WIDTH, WINDOW_HEIGHT))
    
    # Кнопки управления
    buttons = [
        ("Save", "S", 10),
        ("Clear", "C", 50),
        ("Exit", "V", 90),
        ("S+Exit", "Sh+V", 130)
    ]
    
    for text, key, y in buttons:
        pygame.draw.rect(screen, WHITE, (5, y, 70, 30))
        pygame.draw.rect(screen, BLACK, (5, y, 70, 30), 2)
        text_surface = small_font.render(text, True, BLACK)
        screen.blit(text_surface, (10, y + 3))
        key_surface = small_font.render(key, True, DARK_GRAY)
        screen.blit(key_surface, (10, y + 16))
    
    # Заголовки колонок цветов
    y_start = 180
    bg_text = font.render("BG", True, BLACK)
    brush_text = font.render("BR", True, BLACK)
    screen.blit(bg_text, (12, y_start))
    screen.blit(brush_text, (47, y_start))
    
    # Палитра цветов (2 колонки)
    color_size = 30
    for i in range(12):
        y = y_start + 30 + i * 35
        
        # Колонка фона
        pygame.draw.rect(screen, PALETTE[i], (5, y, color_size, color_size))
        pygame.draw.rect(screen, BLACK, (5, y, color_size, color_size), 2)
        if current_bg_color == i:
            pygame.draw.rect(screen, (0, 255, 0), (5, y, color_size, color_size), 3)
        
        # Колонка кисти
        pygame.draw.rect(screen, PALETTE[i], (40, y, color_size, color_size))
        pygame.draw.rect(screen, BLACK, (40, y, color_size, color_size), 2)
        if current_brush_color == i:
            pygame.draw.rect(screen, (0, 255, 0), (40, y, color_size, color_size), 3)
    
    # Миксовые цвета (последний в списке)
    y_mix = y_start + 30 + 12 * 35
    
    # Миксовый фон
    bg_mix_surf = create_mixed_surface(bg_seed, color_size)
    screen.blit(bg_mix_surf, (5, y_mix))
    pygame.draw.rect(screen, BLACK, (5, y_mix, color_size, color_size), 2)
    if current_bg_color == 12:
        pygame.draw.rect(screen, (0, 255, 0), (5, y_mix, color_size, color_size), 3)
    
    # Миксовая кисть
    brush_mix_surf = create_mixed_surface(brush_seed, color_size)
    screen.blit(brush_mix_surf, (40, y_mix))
    pygame.draw.rect(screen, BLACK, (40, y_mix, color_size, color_size), 2)
    if current_brush_color == 12:
        pygame.draw.rect(screen, (0, 255, 0), (40, y_mix, color_size, color_size), 3)
    
    # Отображение сидов
    seed_y = y_mix + 40
    bg_seed_text = small_font.render(f"BG: {bg_seed}", True, BLACK)
    brush_seed_text = small_font.render(f"BR: {brush_seed}", True, BLACK)
    screen.blit(bg_seed_text, (5, seed_y))
    screen.blit(brush_seed_text, (5, seed_y + 15))

def get_drawing_color():
    """Возвращает текущий цвет кисти"""
    if current_brush_color < 12:
        return PALETTE[current_brush_color]
    return None  # Миксовый цвет обрабатывается отдельно

def draw_with_blur(x, y, color_or_seed, is_mixed=False):
    """Рисует с небольшим размытием"""
    # Основная точка
    if is_mixed:
        canvas.set_at((x, y), get_mixed_color(color_or_seed, x, y))
    else:
        pygame.draw.circle(canvas, color_or_seed, (x, y), 0)
    
    # Размытие вокруг (8 соседних пикселей с меньшей непрозрачностью)
    for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < CANVAS_SIZE and 0 <= ny < CANVAS_SIZE:
            if is_mixed:
                new_color = get_mixed_color(color_or_seed, nx, ny)
            else:
                new_color = color_or_seed
            
            # Смешиваем с существующим цветом для эффекта размытия
            try:
                old_color = canvas.get_at((nx, ny))[:3]
                blended = tuple(int(old_color[i] * 0.7 + new_color[i] * 0.3) for i in range(3))
                canvas.set_at((nx, ny), blended)
            except:
                pass

def clear_canvas():
    """Очищает холст с учетом текущего цвета фона"""
    if current_bg_color < 12:
        canvas.fill(PALETTE[current_bg_color])
    else:
        # Заполняем миксовым фоном
        for y in range(CANVAS_SIZE):
            for x in range(CANVAS_SIZE):
                color = get_mixed_color(bg_seed, x, y)
                canvas.set_at((x, y), color)

# Начальная очистка
clear_canvas()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            # Сохранить и создать новый холст (S)
            if event.key == pygame.K_s:
                filename = os.path.join(save_directory, f'canvas_{save_counter:04d}.png')
                pygame.image.save(canvas, filename)
                print(f"Холст сохранен как {filename}")
                clear_canvas()
                save_counter += 1

            # Завершение программы (V)
            elif event.key == pygame.K_v:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    # Сохранить и выйти (Shift+V)
                    filename = os.path.join(save_directory, f'canvas_{save_counter:04d}.png')
                    pygame.image.save(canvas, filename)
                    print(f"Холст сохранен как {filename} и программа завершена.")
                else:
                    print("Программа завершена без сохранения.")
                running = False

            # Очистка холста (C)
            elif event.key == pygame.K_c:
                clear_canvas()
                print("Холст очищен.")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_x, mouse_y = event.pos
                
                # Проверка кликов по меню
                if mouse_x < MENU_WIDTH:
                    # Кнопки управления
                    if 10 <= mouse_y <= 40:  # Save
                        filename = os.path.join(save_directory, f'canvas_{save_counter:04d}.png')
                        pygame.image.save(canvas, filename)
                        print(f"Холст сохранен как {filename}")
                        clear_canvas()
                        save_counter += 1
                    elif 50 <= mouse_y <= 80:  # Clear
                        clear_canvas()
                        print("Холст очищен.")
                    elif 90 <= mouse_y <= 120:  # Exit
                        print("Программа завершена без сохранения.")
                        running = False
                    elif 130 <= mouse_y <= 160:  # Save+Exit
                        filename = os.path.join(save_directory, f'canvas_{save_counter:04d}.png')
                        pygame.image.save(canvas, filename)
                        print(f"Холст сохранен как {filename} и программа завершена.")
                        running = False
                    
                    # Выбор цвета фона
                    elif 210 <= mouse_y <= 210 + 13 * 35:
                        color_idx = (mouse_y - 210) // 35
                        if 5 <= mouse_x <= 35 and color_idx <= 12:
                            current_bg_color = color_idx
                            # Генерируем новый сид, если выбран микс
                            if color_idx == 12:
                                bg_seed, brush_seed = generate_valid_seeds()
                            clear_canvas()
                            print(f"Выбран цвет фона: {color_idx}")
                        
                        # Выбор цвета кисти
                        elif 40 <= mouse_x <= 70 and color_idx <= 12:
                            current_brush_color = color_idx
                            # Генерируем новый сид, если выбран микс
                            if color_idx == 12:
                                bg_seed, brush_seed = generate_valid_seeds()
                            print(f"Выбран цвет кисти: {color_idx}")
                else:
                    drawing = True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                mouse_x, mouse_y = event.pos
                if mouse_x >= MENU_WIDTH:  # Рисуем только на холсте
                    # Масштабируем координаты
                    canvas_x = int((mouse_x - MENU_WIDTH) / WINDOW_HEIGHT * CANVAS_SIZE)
                    canvas_y = int(mouse_y / WINDOW_HEIGHT * CANVAS_SIZE)
                    
                    if 0 <= canvas_x < CANVAS_SIZE and 0 <= canvas_y < CANVAS_SIZE:
                        if current_brush_color < 12:
                            color = get_drawing_color()
                            draw_with_blur(canvas_x, canvas_y, color, False)
                        else:
                            draw_with_blur(canvas_x, canvas_y, brush_seed, True)

    # --- Отрисовка кадра ---
    screen.fill(BLACK)
    
    # Отрисовка меню
    draw_menu()
    
    # Масштабирование и отрисовка холста
    scaled_canvas = pygame.transform.scale(canvas, (WINDOW_HEIGHT, WINDOW_HEIGHT))
    screen.blit(scaled_canvas, (MENU_WIDTH, 0))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
