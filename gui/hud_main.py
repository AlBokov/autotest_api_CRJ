import dearpygui.dearpygui as dpg
import os
import sys
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from src.open_parser_yaml import OpenApiParser
from src.client import ApiClient
from src.validator_response import check_api_response

import random
import math
import time

# ====================== Волны ======================
NUM_WAVES = 2                    # сколько волн будет
WAVE_HEIGHT = 80                 # высота каждой волны в пикселях
WAVE_SPEED = [0.8, 1.1, 0.7, 1.3, 0.9, 1.0, 0.6, 1.2]  # разная скорость для каждой волны

# Цвета в стиле киберпанк (от голубого к фиолетовому)
WAVE_COLORS = [
    (37, 37, 37, 180),     # ярко-голубой
    (255, 50, 255, 160),
    (80, 180, 200, 90),
    (120, 140, 255, 130),
    (160, 100, 255, 120),
    (200, 80, 255, 110),
    (220, 60, 255, 100),
    (255, 50, 200, 90)
]

# Данные для каждой волны (будем обновлять каждые несколько кадров)
wave_data = [[0.0] * 400 for _ in range(NUM_WAVES)]   # 400 точек на волну

def update_waves():
    """Обновляет данные волн (случайный шум + движение)"""
    for i in range(NUM_WAVES):
        # Сдвигаем все точки влево
        wave_data[i] = wave_data[i][1:] + [wave_data[i][0]]
        
        # Генерируем новую точку справа с небольшим шумом
        noise = random.gauss(0, 0.25)                    # случайный шум
        last_value = wave_data[i][-2] if len(wave_data[i]) > 1 else 0
        new_value = last_value * 0.85 + noise * 1.8      # плавность + шум
        
        # Ограничиваем высоту
        new_value = max(-1.0, min(1.0, new_value))
        wave_data[i][-1] = new_value

def draw_cyber_waves():
    """Рисует киберпанк-волны — исправленная версия"""
    if not dpg.does_item_exist("wave_drawlist"):
        return

    # Очищаем предыдущий кадр
    dpg.delete_item("wave_drawlist", children_only=True)

    for i in range(NUM_WAVES):
        points = []
        color = WAVE_COLORS[i % len(WAVE_COLORS)]
        
        base_y = 50 + i * (WAVE_HEIGHT + 25)   # вертикальное смещение волн

        for x in range(400):
            y_offset = wave_data[i][x] * (WAVE_HEIGHT // 2 - 15)
            y = base_y + int(y_offset)
            points.append((x * 2, y))           # x * 2 = ширина волны

        # Основная линия (толстая, полупрозрачная)
        dpg.draw_polyline(
            points=points,
            color=color,
            thickness=3.0,
            parent="wave_drawlist"
        )

        # Тонкая яркая линия сверху (свечение)
        dpg.draw_polyline(
            points=points,
            color=(min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40), 255),
            thickness=1.2,
            parent="wave_drawlist"
        )

dpg.create_context()

dpg.configure_app(docking=False, docking_space=False)

# ====================== Изображение для фона ======================
width, height, channels, image_data = dpg.load_image("C:/Users/User/Desktop/ProjectPython/autotest_api/gui/banner.jpg")

# 2. Регистрируем текстуру
with dpg.texture_registry():
    dpg.add_static_texture(width=width, height=height, default_value=image_data, tag="bg_texture")



# ====================== ЦВЕТА (более яркий cyberpunk) ======================
NEON_CYAN = (0, 240, 255, 255)
NEON_DARK = (0, 200, 220, 55)
PANEL_BG = (241, 225, 235, 180)      # полупрозрачный тёмно-синий фон
BG_DARK = (8, 8, 25, 55)
TEST_BG = (233, 191, 213, 40)
FIL = (178, 11, 201, 220)
FIL_TG = (178, 11, 201, 100)
BLAK = (13, 2, 15, 255)
GOLD = (239, 228, 11, 190)

# ====================== ШРИФТЫ ======================
font_candidates = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\seguiemj.ttf",
    r"C:\Windows\Fonts\consola.ttf",
]

default_font = title_font = None
with dpg.font_registry():
    for path in font_candidates:
        if os.path.exists(path):
            print(f"✅ Шрифт: {path}")
            with dpg.font(path, 18) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            with dpg.font(path, 26) as title_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            break
    if default_font is None:
        with dpg.font("ProggyClean", 18) as default_font:
            pass

dpg.bind_font(default_font)




# ====================== ТЕМА ======================
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, PANEL_BG)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, PANEL_BG)
        dpg.add_theme_color(dpg.mvThemeCol_Border, NEON_CYAN)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, FIL_TG)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, FIL)
        dpg.add_theme_color(dpg.mvThemeCol_Button, FIL_TG)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, NEON_CYAN)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, FIL)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5)   # выравнивание по центру
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
dpg.bind_theme(global_theme)

# ====================== ГЛОБАЛЬНЫЕ ======================
client = None
parser = None
current_operation = None

def init_backend():
    global client, parser
    try:
        client = ApiClient()
        parser = OpenApiParser('config/operation.yaml')
        print("✅ Backend успешно инициализирован")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# ====================== CALLBACKS ======================
def select_operation(sender, app_data, user_data):
    global current_operation
    current_operation = user_data
    try:
        req = parser.build_request_example(current_operation, None)
        yaml_str = yaml.dump(req, allow_unicode=True, sort_keys=False, default_flow_style=False)
        dpg.set_value("request_input", yaml_str)
        dpg.set_value("log_text", f"✓ Выбрана операция: {current_operation}")
    except Exception as e:
        dpg.set_value("log_text", f"Ошибка: {e}")

def send_request_callback():
    if not current_operation:
        dpg.set_value("log_text", "Выберите операцию слева!")
        return

    dpg.set_value("log_text", f"Отправка {current_operation}...")
    dpg.set_value("response_text", "Отправка...")

    try:
        request_yaml = dpg.get_value("request_input")
        operation_request = yaml.safe_load(request_yaml)

        response = client.send_request(operation_request)
        parser.old_response = response

        response_yaml = yaml.dump(response, allow_unicode=True, sort_keys=False, default_flow_style=False)
        dpg.set_value("response_text", response_yaml)

        dpg.set_value("log_text", f"✓ {current_operation} выполнен успешно")

        try:
            receipt = response['response']['receiptData']
            client.format_receipt(receipt)
        except:
            pass

        required = parser.get_response_required_fields(current_operation)
        check_api_response(response.get('response', {}), required)

    except Exception as e:
        dpg.set_value("response_text", f"✗ Ошибка: {e}")
        dpg.set_value("log_text", f"✗ Ошибка: {e}")

# ====================== ОКНА ======================
def create_docking_windows():

    # Control Panel
    with dpg.window(label="Control Panel", tag="control_win", width=300, height=420, pos=(10, 10), no_background=False):
        dpg.add_text("Выберите операцию", color=BLAK)
        
        operations_list = ["Sale", "Refund", "Closebatch", "Activate", "Balance"]
        dpg.add_combo(
            items=operations_list,                    # список вариантов
            label="", 
            width=-1,
            tag="operation_combo",                    # тег, чтобы потом читать значение
            callback=select_operation,                # твоя существующая функция
            user_data=None                            # сюда будет приходить выбранный элемент
        )

        dpg.add_separator()
        dpg.add_button(label="Send Request", width=-1, height=55, callback=send_request_callback, tag="send_btn")

    # Request
    with dpg.window(label="Request", tag="request_win", width=420, height=370, pos=(320, 10)):
        dpg.add_input_text(multiline=True, height=340, width=-1, tag="request_input", 
                           default_value="# Выберите операцию слева")

    # Response
    with dpg.window(label="Response", tag="response_win", width=420, height=370, pos=(750, 10)):
        dpg.add_input_text(multiline=True, height=340, width=-1, tag="response_text", 
                           default_value="Waiting for a response...")

    
    # === ОКНО С КИБЕРПАНК ВОЛНАМИ ===
    with dpg.window(label="Настройки", tag="wave_window", width=300, height=265, pos=(10, 495), no_title_bar=True):
        # Создаём drawlist правильно
        with dpg.drawlist(width=400, height=225, tag="wave_drawlist"):
            pass   # оставляем пустым — будем рисовать в callback
    
    with dpg.window(label="Чек", tag="chek_window", width=420, height=350, pos=(320, 390)):
        dpg.add_input_text(multiline=True, height=340, width=-1)
    
    with dpg.window(label="Отчет", tag="report_window", width=420, height=350, pos=(750, 390)):
        dpg.add_input_text(multiline=True, height=340, width=-1)


# ====================== ЗАПУСК ======================
def main():
    dpg.configure_app(docking=True, docking_shift_only=False, docking_space=False)
    
    init_backend()
    create_docking_windows()

    dpg.create_viewport(title="CRJ API Autotest HUD", width=1200, height=800, clear_color=PANEL_BG)
    


    dpg.setup_dearpygui()
    dpg.show_viewport()

        # === ЗАГРУЗКА ФОНОВОЙ КАРТИНКИ ===
    try:
        image_data = dpg.load_image("gui/background.jpg")
        
        if image_data is None:
            raise FileNotFoundError("Файл не найден или повреждён")
            
        w, h, c, texture_id = image_data
        
        # Создаём drawlist для всего viewport
        drawlist = dpg.add_viewport_drawlist(front=False)   # front=False — рисуем на заднем плане
        
        dpg.draw_image(
            texture_id,
            pmin=(0, 0),
            pmax=(w, h),
            uv_min=(0.0, 0.0),
            uv_max=(1.0, 1.0),
            parent=drawlist
        )
        
        print(f"✅ Фон успешно загружен: {w}×{h}")
        
    except Exception as e:
        print(f"❌ Не удалось загрузить фон: {e}")
    
    def animation_loop():
        update_waves()          # обновляем данные волн
        draw_cyber_waves()      # рисуем
        dpg.set_frame_callback(dpg.get_frame_count() + 1, animation_loop)  # повторяем

    dpg.set_frame_callback(5, animation_loop)   
    
    print("🚀 HUD запущен! Теперь должно быть ярко и красиво.")
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()