from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
import json
import os
from datetime import datetime
import asyncio
import threading
from bleak import BleakScanner, BleakClient

# Improved color scheme with better contrast
COLORS = {
    'primary': get_color_from_hex('#2E86AB'),
    'secondary': get_color_from_hex('#A23B72'),
    'accent': get_color_from_hex('#F18F01'),
    'success': get_color_from_hex('#4CAF50'),
    'danger': get_color_from_hex('#F44336'),
    'light': get_color_from_hex('#F8F9FA'),
    'dark': get_color_from_hex('#212529'),
    'gray': get_color_from_hex('#B0BEC5'),
    'white': get_color_from_hex('#FFFFFF'),
    'card_bg': get_color_from_hex('#FFFFFF'),
    'text_primary': get_color_from_hex('#212529'),
    'text_secondary': get_color_from_hex('#546E7A'),
    'button_start': get_color_from_hex('#F18F01'),
}

# BLE Configuration
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class BLESensorManager:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self.is_scanning = False
        self.current_value = 0
        self.loop = None
        self.thread = None
        
    def start_ble_loop(self):
        """Start BLE in a separate thread"""
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_ble_loop, daemon=True)
            self.thread.start()
    
    def _run_ble_loop(self):
        """Run the asyncio event loop"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    async def _connect_to_sensor(self):
        """Connect to BLE sensor"""
        print("Поиск ESP32...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        target_device = next((d for d in devices if d.name and "Оно живое!" in d.name), None)
        
        if not target_device:
            print("ESP32 не найдена")
            return False
        
        print(f"Найдена: {target_device.name}")
        
        try:
            self.client = BleakClient(target_device)
            await self.client.connect()
            self.is_connected = True
            print("Подключено к датчику!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    async def _read_sensor_data(self):
        """Read data from BLE sensor"""
        if not self.client or not self.is_connected:
            return
        
        try:
            data = await self.client.read_gatt_char(CHARACTERISTIC_UUID)
            sensor_value = data.decode('utf-8').strip()
            
            # Convert to integer, handle potential errors
            try:
                self.current_value = float(sensor_value)
                print(f"📈 Напряжение мышцы: {self.current_value}")
            except ValueError:
                print(f"❌ Неверный формат данных: {sensor_value}")
                
        except Exception as e:
            print(f"❌ Ошибка чтения: {e}")
            self.is_connected = False
    
    def connect_sensor(self):
        """Connect to sensor from main thread"""
        if self.loop and not self.is_connected:
            asyncio.run_coroutine_threadsafe(self._connect_to_sensor(), self.loop)
    
    def read_sensor_data(self):
        """Read sensor data from main thread"""
        if self.loop and self.is_connected:
            asyncio.run_coroutine_threadsafe(self._read_sensor_data(), self.loop)
    
    def disconnect_sensor(self):
        """Disconnect from sensor"""
        if self.loop and self.client and self.is_connected:
            async def disconnect():
                await self.client.disconnect()
                self.is_connected = False
                print("Отключено от датчика")
            
            asyncio.run_coroutine_threadsafe(disconnect(), self.loop)

# Global sensor manager
sensor_manager = BLESensorManager()

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        with self.canvas.before:
            self.bg_color = Color(*COLORS['primary'])
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[15]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class CardLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CardLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [15, 15, 15, 15]
        self.spacing = 10
        
        with self.canvas.before:
            Color(*COLORS['card_bg'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[12]
            )
            Color(*COLORS['gray'])
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0]-1, self.pos[1]-1), 
                size=(self.size[0]+2, self.size[1]+2),
                radius=[13]
            )
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0]-1, self.pos[1]-1)
        self.border_rect.size = (self.size[0]+2, self.size[1]+2)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.clearcolor = COLORS['light']
        
        layout = FloatLayout()
        
        # Background gradient
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(pos=(0, 0), size=Window.size)
            Color(*get_color_from_hex('#1A5276'))
            Rectangle(pos=(0, Window.size[1] * 0.4), size=(Window.size[0], Window.size[1] * 0.6))
        
        # Title
        title_label = Label(
            text='Fitness Tracker',
            font_size='42sp',
            color=COLORS['white'],
            bold=True,
            size_hint=(0.8, None),
            height=60,
            pos_hint={'top': 0.85, 'center_x': 0.5},
            text_size=(Window.size[0] * 0.8, None)
        )
        title_label.bind(texture_size=title_label.setter('size'))
        layout.add_widget(title_label)
        
        subtitle_label = Label(
            text='Достигайте своих целей',
            font_size='20sp',
            color=COLORS['white'],
            size_hint=(0.8, None),
            height=30,
            pos_hint={'top': 0.75, 'center_x': 0.5},
            text_size=(Window.size[0] * 0.8, None)
        )
        subtitle_label.bind(texture_size=subtitle_label.setter('size'))
        layout.add_widget(subtitle_label)
        
        # Start button with contrast color
        start_button = RoundedButton(
            text='НАЧАТЬ',
            font_size='24sp',
            size_hint=(0.6, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            color=COLORS['white']
        )
        start_button.bg_color.rgba = COLORS['button_start']
        start_button.bind(on_press=self.switch_to_workout_menu)
        layout.add_widget(start_button)
        
        self.add_widget(layout)

    def switch_to_workout_menu(self, instance):
        self.manager.current = 'workout_menu'

class WorkoutMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutMenuScreen, self).__init__(**kwargs)
        Window.clearcolor = COLORS['light']
        
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(*COLORS['light'])
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Title
        title_label = Label(
            text='Меню тренировок',
            font_size='32sp',
            color=COLORS['text_primary'],
            bold=True,
            size_hint=(0.8, None),
            height=50,
            pos_hint={'top': 0.9, 'center_x': 0.5},
            text_size=(Window.size[0] * 0.8, None)
        )
        title_label.bind(texture_size=title_label.setter('size'))
        layout.add_widget(title_label)
        
        # Menu cards layout
        menu_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(0.8, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # History card
        history_card = CardLayout(height=120)
        history_content = BoxLayout(orientation='horizontal', spacing=15)
        
        # History icon area (empty now)
        history_icon = BoxLayout(size_hint_x=0.3)
        
        history_text = BoxLayout(orientation='vertical')
        history_title = Label(
            text='История тренировок',
            font_size='20sp',
            color=COLORS['text_primary'],
            bold=True,
            halign='left'
        )
        history_title.bind(size=history_title.setter('text_size'))
        
        history_desc = Label(
            text='Просмотр сохраненных тренировок',
            font_size='14sp',
            color=COLORS['text_secondary'],
            halign='left'
        )
        history_desc.bind(size=history_desc.setter('text_size'))
        
        history_text.add_widget(history_title)
        history_text.add_widget(history_desc)
        
        history_content.add_widget(history_icon)
        history_content.add_widget(history_text)
        
        history_card.add_widget(history_content)
        
        # Make the entire card clickable
        history_card.bind(on_touch_down=lambda instance, touch: 
                         instance.collide_point(*touch.pos) and self.switch_to_history(instance))
        
        # Workout card
        workout_card = CardLayout(height=120)
        workout_content = BoxLayout(orientation='horizontal', spacing=15)
        
        # Workout icon area (empty now)
        workout_icon = BoxLayout(size_hint_x=0.3)
        
        workout_text = BoxLayout(orientation='vertical')
        workout_title = Label(
            text='Начать тренировку',
            font_size='20sp',
            color=COLORS['text_primary'],
            bold=True,
            halign='left'
        )
        workout_title.bind(size=workout_title.setter('text_size'))
        
        workout_desc = Label(
            text='Новая тренировка с отслеживанием',
            font_size='14sp',
            color=COLORS['text_secondary'],
            halign='left'
        )
        workout_desc.bind(size=workout_desc.setter('text_size'))
        
        workout_text.add_widget(workout_title)
        workout_text.add_widget(workout_desc)
        
        workout_content.add_widget(workout_icon)
        workout_content.add_widget(workout_text)
        
        workout_card.add_widget(workout_content)
        
        # Make the entire card clickable
        workout_card.bind(on_touch_down=lambda instance, touch: 
                         instance.collide_point(*touch.pos) and self.switch_to_workouts(instance))
        
        menu_layout.add_widget(history_card)
        menu_layout.add_widget(workout_card)
        layout.add_widget(menu_layout)
        
        # Back button
        back_button = RoundedButton(
            text='Назад',
            font_size='18sp',
            size_hint=(0.4, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            color=COLORS['white']
        )
        back_button.bg_color.rgba = COLORS['secondary']
        back_button.bind(on_press=self.switch_to_main)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def switch_to_history(self, instance):
        self.manager.current = 'history'

    def switch_to_workouts(self, instance):
        self.manager.current = 'workouts'

    def switch_to_main(self, instance):
        self.manager.current = 'main'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        Window.clearcolor = COLORS['light']
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='История тренировок',
            font_size='28sp',
            color=COLORS['text_primary'],
            bold=True,
            size_hint_y=0.1
        )
        main_layout.add_widget(title)
        
        # Workouts area
        scroll_view = ScrollView(
            size_hint=(1, 0.75),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=10,
            bar_color=COLORS['primary']
        )
        self.history_layout = BoxLayout(
            orientation='vertical',
            spacing=15, 
            size_hint_y=None,
            padding=10
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll_view.add_widget(self.history_layout)
        main_layout.add_widget(scroll_view)
        
        # Buttons
        buttons_layout = BoxLayout(size_hint_y=0.15, spacing=15, padding=10)
        
        clear_btn = RoundedButton(
            text='ОЧИСТИТЬ ИСТОРИЮ',
            font_size='16sp',
            color=COLORS['white']
        )
        clear_btn.bg_color.rgba = COLORS['danger']
        clear_btn.bind(on_press=self.clear_history)
        
        back_btn = RoundedButton(
            text='НАЗАД',
            font_size='16sp',
            color=COLORS['white']
        )
        back_btn.bg_color.rgba = COLORS['secondary']
        back_btn.bind(on_press=self.switch_to_workout_menu)
        
        buttons_layout.add_widget(clear_btn)
        buttons_layout.add_widget(back_btn)
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
        
        Clock.schedule_once(lambda dt: self.update_history(), 0.1)

    def update_history(self):
        self.history_layout.clear_widgets()
        self.history_layout.height = 0
        
        try:
            db_file = 'workout_database.json'
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                
                workouts = database.get("workouts", [])
                
                if workouts:
                    workouts.sort(key=lambda x: x.get('date', ''), reverse=True)
                    
                    for workout in workouts:
                        workout_card = self.create_workout_card(workout)
                        self.history_layout.add_widget(workout_card)
                    
                    self.history_layout.height = self.history_layout.minimum_height
                else:
                    no_workouts_label = Label(
                        text='Нет сохраненных тренировок\n\nНачните тренировку и сохраните ее,\nчтобы увидеть здесь историю',
                        font_size='18sp',
                        size_hint_y=None,
                        height=200,
                        halign='center',
                        valign='middle',
                        color=COLORS['text_secondary']
                    )
                    no_workouts_label.bind(size=no_workouts_label.setter('text_size'))
                    self.history_layout.add_widget(no_workouts_label)
            else:
                no_db_label = Label(
                    text='База данных не найдена\n\nСохраните первую тренировку,\nчтобы создать базу данных',
                    font_size='18sp',
                    size_hint_y=None,
                    height=200,
                    halign='center',
                    valign='middle',
                    color=COLORS['text_secondary']
                )
                no_db_label.bind(size=no_db_label.setter('text_size'))
                self.history_layout.add_widget(no_db_label)
                
        except Exception as e:
            error_label = Label(
                text=f'Ошибка загрузки данных:\n{str(e)}',
                font_size='16sp',
                size_hint_y=None,
                height=120,
                halign='center',
                valign='middle',
                color=COLORS['danger']
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.history_layout.add_widget(error_label)

    def create_workout_card(self, workout):
        card = CardLayout(height=180)
        
        content = BoxLayout(orientation='vertical', spacing=8)
        
        # Header with date and time
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        date_parts = workout.get('date', 'Неизвестно').split(' ')
        date_text = date_parts[0] if len(date_parts) > 0 else 'Неизвестно'
        
        date_label = Label(
            text=f"Дата: {date_text}",
            font_size='16sp',
            color=COLORS['primary'],
            bold=True,
            halign='left',
            text_size=(Window.size[0] * 0.35, None)
        )
        date_label.bind(texture_size=date_label.setter('size'))
        
        duration_label = Label(
            text=f"Время: {workout.get('time', '00:00')}",
            font_size='14sp',
            color=COLORS['secondary'],
            halign='right',
            text_size=(Window.size[0] * 0.35, None)
        )
        duration_label.bind(texture_size=duration_label.setter('size'))
        
        header_layout.add_widget(date_label)
        header_layout.add_widget(duration_label)
        
        # Metrics - only muscle tension metrics
        metrics = workout.get('metrics', {})
        metrics_layout = GridLayout(cols=3, size_hint_y=0.6, spacing=10, padding=[0, 10, 0, 0])
        
        metrics_data = [
            ('Макс. напряжение', f"{metrics.get('max_tension', 0):.0f}"),
            ('Ср. напряжение', f"{metrics.get('avg_tension', 0):.0f}"),
            ('Мин. напряжение', f"{metrics.get('min_tension', 0):.0f}")
        ]
        
        for name, value in metrics_data:
            metric_layout = BoxLayout(orientation='vertical', spacing=2)
            
            metric_name = Label(
                text=name,
                font_size='11sp',
                color=COLORS['text_secondary'],
                size_hint_y=0.4,
                text_size=(None, None)
            )
            metric_name.bind(texture_size=metric_name.setter('size'))
            
            metric_value = Label(
                text=value,
                font_size='16sp',
                color=COLORS['text_primary'],
                bold=True,
                size_hint_y=0.6,
                text_size=(None, None)
            )
            metric_value.bind(texture_size=metric_value.setter('size'))
            
            metric_layout.add_widget(metric_name)
            metric_layout.add_widget(metric_value)
            metrics_layout.add_widget(metric_layout)
        
        content.add_widget(header_layout)
        content.add_widget(metrics_layout)
        
        card.add_widget(content)
        
        # Detail view button
        card.bind(on_touch_down=lambda instance, touch: 
                 instance.collide_point(*touch.pos) and self.show_workout_details(workout))
        
        return card

    def show_workout_details(self, workout):
        if hasattr(self.manager, 'get_screen'):
            detail_screen = self.manager.get_screen('workout_detail')
            detail_screen.load_workout_data(workout)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'workout_detail'

    def clear_history(self, instance):
        try:
            db_file = 'workout_database.json'
            if os.path.exists(db_file):
                backup_file = f"workout_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(db_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                empty_db = {"workouts": [], "statistics": {}}
                with open(db_file, 'w', encoding='utf-8') as f:
                    json.dump(empty_db, f, indent=2, ensure_ascii=False)
                
                print(f"История очищена. Резервная копия: {backup_file}")
                self.update_history()
            else:
                print("База данных не найдена для очистки")
                
        except Exception as e:
            print(f"Ошибка при очистке истории: {e}")

    def switch_to_workout_menu(self, instance):
        self.manager.current = 'workout_menu'

    def on_enter(self):
        self.update_history()

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)
        Window.clearcolor = COLORS['light']
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_event = None
        self.timer_label = None
        self.sensor_data = []
        self.sensor_update_event = None

        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=25)
        
        # Title
        title_label = Label(
            text='Тренировка',
            font_size='32sp',
            color=COLORS['text_primary'],
            bold=True,
            size_hint_y=0.15
        )
        main_layout.add_widget(title_label)
        
        # Timer
        timer_card = CardLayout(height=150)
        timer_content = BoxLayout(orientation='vertical', spacing=10)
        
        timer_title = Label(
            text='ВРЕМЯ ТРЕНИРОВКИ',
            font_size='16sp',
            color=COLORS['text_secondary'],
            bold=True
        )
        
        self.timer_label = Label(
            text='00:00',
            font_size='48sp',
            color=COLORS['primary'],
            bold=True
        )
        
        timer_content.add_widget(timer_title)
        timer_content.add_widget(self.timer_label)
        timer_card.add_widget(timer_content)
        main_layout.add_widget(timer_card)
        
        # Sensor data
        sensor_card = CardLayout(height=100)
        self.sensor_label = Label(
            text='Датчик: не подключен\nНажмите "ПОДКЛЮЧИТЬ ДАТЧИК"',
            font_size='18sp',
            color=COLORS['text_primary']
        )
        sensor_card.add_widget(self.sensor_label)
        main_layout.add_widget(sensor_card)
        
        # Control buttons
        control_layout = GridLayout(cols=2, spacing=15, size_hint_y=0.25)
        
        start_button = RoundedButton(
            text='СТАРТ',
            font_size='20sp',
            color=COLORS['white']
        )
        start_button.bind(on_press=self.start_workout)
        
        stop_button = RoundedButton(
            text='СТОП',
            font_size='20sp',
            color=COLORS['white']
        )
        stop_button.bg_color.rgba = COLORS['danger']
        stop_button.bind(on_press=self.stop_workout)
        
        control_layout.add_widget(start_button)
        control_layout.add_widget(stop_button)
        main_layout.add_widget(control_layout)
        
        # Sensor connection button
        sensor_button = RoundedButton(
            text='ПОДКЛЮЧИТЬ ДАТЧИК',
            font_size='20sp',
            size_hint_y=0.12,
            color=COLORS['white']
        )
        sensor_button.bg_color.rgba = COLORS['accent']
        sensor_button.bind(on_press=self.connect_sensor)
        main_layout.add_widget(sensor_button)
        
        # Save button
        save_button = RoundedButton(
            text='СОХРАНИТЬ ТРЕНИРОВКУ',
            font_size='20sp',
            size_hint_y=0.12,
            color=COLORS['white']
        )
        save_button.bg_color.rgba = COLORS['success']
        save_button.bind(on_press=self.save_workout)
        main_layout.add_widget(save_button)
        
        # Back button
        back_button = RoundedButton(
            text='НАЗАД',
            font_size='18sp',
            size_hint_y=0.1,
            color=COLORS['white']
        )
        back_button.bg_color.rgba = COLORS['gray']
        back_button.bind(on_press=self.switch_to_workout_menu)
        main_layout.add_widget(back_button)
        
        self.add_widget(main_layout)
        
        # Start BLE manager
        sensor_manager.start_ble_loop()

    def connect_sensor(self, instance):
        """Connect to BLE sensor"""
        self.sensor_label.text = 'Поиск датчика...'
        sensor_manager.connect_sensor()
        
        # Start checking connection status
        if not self.sensor_update_event:
            self.sensor_update_event = Clock.schedule_interval(self.update_sensor_display, 0.5)

    def update_sensor_display(self, dt):
        """Update sensor data display"""
        if sensor_manager.is_connected:
            sensor_manager.read_sensor_data()
            self.sensor_label.text = f'Напряжение мышцы: {sensor_manager.current_value}'
        else:
            self.sensor_label.text = 'Датчик: не подключен\nНажмите "ПОДКЛЮЧИТЬ ДАТЧИК"'

    def start_workout(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
            self.sensor_label.text = 'Тренировка начата! Данные собираются...'
            print("Тренировка начата!")

    def stop_workout(self, instance):
        if self.timer_running:
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
            self.sensor_label.text = f'Тренировка остановлена. Время: {self.timer_label.text}'
            print(f"Тренировка остановлена. Время: {self.timer_label.text}")

    def collect_sensor_data(self):
        """Collect sensor data from BLE manager"""
        if self.timer_running and sensor_manager.is_connected:
            sensor_reading = {
                'timestamp': self.time_elapsed,
                'tension': sensor_manager.current_value
            }
            
            self.sensor_data.append(sensor_reading)

    def update_timer(self, dt):
        if self.timer_running:
            self.time_elapsed += 1
            self.collect_sensor_data()
            minutes = self.time_elapsed // 60
            seconds = self.time_elapsed % 60
            self.timer_label.text = f'{minutes:02d}:{seconds:02d}'

    def save_workout(self, instance):
        if self.time_elapsed > 0:
            minutes = self.time_elapsed // 60
            seconds = self.time_elapsed % 60
            workout_time = f'{minutes:02d}:{seconds:02d}'
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            tension_values = [data['tension'] for data in self.sensor_data] if self.sensor_data else [0]
            
            max_tension = max(tension_values) if tension_values else 0
            avg_tension = sum(tension_values) / len(tension_values) if tension_values else 0
            min_tension = min(tension_values) if tension_values else 0
            
            workout_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            workout_folder = f'workouts/workout_{workout_id}'
            os.makedirs(workout_folder, exist_ok=True)
            
            graph_path = f'{workout_folder}/graph.png'
            self.create_tension_graph(self.sensor_data, graph_path, max_tension, avg_tension, min_tension)
            
            workout_entry = {
                'id': workout_id,
                'time': workout_time,
                'date': current_date,
                'duration_seconds': self.time_elapsed,
                'sensor_data': self.sensor_data,
                'workout_folder': workout_folder,
                'graph_path': graph_path,
                'metrics': {
                    'max_tension': max_tension,
                    'avg_tension': round(avg_tension, 2),
                    'min_tension': min_tension
                }
            }
            
            success = self.save_to_database(workout_entry)
            if success:
                self.sensor_label.text = f'Тренировка сохранена! Время: {workout_time}'
                if self.timer_running:
                    if self.timer_event:
                        self.timer_event.cancel()
                    self.timer_running = False
                self.time_elapsed = 0
                self.sensor_data = []
                self.timer_label.text = '00:00'
                
                if 'history' in self.manager.screen_names:
                    self.manager.get_screen('history').update_history()
            else:
                self.sensor_label.text = 'Ошибка сохранения тренировки'

    def create_tension_graph(self, sensor_data, save_path, max_tension, avg_tension, min_tension):
        if not sensor_data:
            return
            
        import matplotlib.pyplot as plt
        
        times = [data['timestamp'] for data in sensor_data]
        tension = [data['tension'] for data in sensor_data]
        
        plt.figure(figsize=(12, 8))
        
        # Основной график напряжения мышцы
        plt.plot(times, tension, color='#2E86AB', linewidth=2.5, label='Напряжение мышцы', alpha=0.7)
        
        # Линии для максимального, среднего и минимального значений
        plt.axhline(y=max_tension, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Макс: {max_tension}')
        plt.axhline(y=avg_tension, color='#4ECDC4', linestyle='--', linewidth=2, label=f'Ср: {avg_tension:.1f}')
        plt.axhline(y=min_tension, color='#45B7D1', linestyle='--', linewidth=2, label=f'Мин: {min_tension}')
        
        # Точки для максимального и минимального значений
        if tension:
            max_index = tension.index(max_tension)
            min_index = tension.index(min_tension)
            
            plt.scatter(times[max_index], max_tension, color='#FF6B6B', s=100, zorder=5)
            plt.scatter(times[min_index], min_tension, color='#45B7D1', s=100, zorder=5)
        
        # Заголовок и подписи
        plt.title('Динамика напряжения мышцы во времени', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Время (секунды)', fontsize=12, fontweight='bold')
        plt.ylabel('Уровень напряжения', fontsize=12, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight', facecolor='#F8F9FA')
        plt.close()

    def save_to_database(self, workout_entry):
        try:
            db_file = 'workout_database.json'
            
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
            else:
                database = {"workouts": [], "statistics": {}}
            
            database["workouts"].append(workout_entry)
            
            self.update_statistics(database)
            
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            print(f"Тренировка успешно сохранена в базу данных (ID: {workout_entry['id']})")
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении в базу данных: {e}")
            return False

    def update_statistics(self, database):
        workouts = database["workouts"]
        if workouts:
            total_workouts = len(workouts)
            total_duration = sum(w['duration_seconds'] for w in workouts)
            avg_duration = total_duration / total_workouts
            
            database["statistics"] = {
                "total_workouts": total_workouts,
                "total_duration_seconds": total_duration,
                "average_duration_seconds": round(avg_duration, 2),
                "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def switch_to_workout_menu(self, instance):
        if self.timer_running:
            if self.timer_event:
                self.timer_event.cancel()
            self.timer_running = False
        
        if self.sensor_update_event:
            self.sensor_update_event.cancel()
            
        sensor_manager.disconnect_sensor()
        self.manager.current = 'workout_menu'

class WorkoutDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutDetailScreen, self).__init__(**kwargs)
        Window.clearcolor = COLORS['light']
        
        self.main_layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        self.title_label = Label(
            text='Детали тренировки', 
            font_size='28sp',
            color=COLORS['text_primary'],
            bold=True,
            size_hint_y=0.08
        )
        self.main_layout.add_widget(self.title_label)
        
        scroll_view = ScrollView(
            size_hint=(1, 0.82),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=10,
            bar_color=COLORS['primary']
        )
        self.detail_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=15)
        self.detail_layout.bind(minimum_height=self.detail_layout.setter('height'))
        scroll_view.add_widget(self.detail_layout)
        self.main_layout.add_widget(scroll_view)
        
        back_button = RoundedButton(
            text='НАЗАД К ИСТОРИИ',
            font_size='18sp',
            size_hint_y=0.1,
            color=COLORS['white']
        )
        back_button.bg_color.rgba = COLORS['primary']
        back_button.bind(on_press=self.go_back)
        self.main_layout.add_widget(back_button)
        
        self.add_widget(self.main_layout)
    
    def load_workout_data(self, workout):
        self.detail_layout.clear_widgets()
        
        # Basic info
        info_card = CardLayout(height=100)
        info_layout = GridLayout(cols=2, size_hint_y=1, spacing=10, padding=10)
        
        info_data = [
            ('Дата:', workout.get('date', 'Неизвестно')),
            ('Время тренировки:', workout.get('time', '00:00'))
        ]
        
        for label, value in info_data:
            info_layout.add_widget(Label(
                text=label, 
                font_size='16sp', 
                color=COLORS['text_primary'],
                bold=True,
                halign='left'
            ))
            info_layout.add_widget(Label(
                text=str(value), 
                font_size='16sp', 
                color=COLORS['text_secondary'],
                halign='right'
            ))
        
        info_card.add_widget(info_layout)
        self.detail_layout.add_widget(info_card)
        
        # Workout metrics - only tension metrics
        metrics = workout.get('metrics', {})
        metrics_card = CardLayout(height=150)
        metrics_content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        metrics_title = Label(
            text='МЕТРИКИ НАПРЯЖЕНИЯ МЫШЦЫ',
            font_size='18sp',
            color=COLORS['primary'],
            bold=True,
            size_hint_y=0.2
        )
        metrics_content.add_widget(metrics_title)
        
        metrics_grid = GridLayout(cols=2, size_hint_y=0.8, spacing=15)
        
        # Calculate min tension if not present
        min_tension = metrics.get('min_tension', 0)
        if min_tension == 0 and workout.get('sensor_data'):
            tension_values = [data['tension'] for data in workout['sensor_data']]
            min_tension = min(tension_values) if tension_values else 0
        
        metrics_data = [
            ('Макс. напряжение:', f"{metrics.get('max_tension', 0):.0f}"),
            ('Ср. напряжение:', f"{metrics.get('avg_tension', 0):.1f}"),
            ('Мин. напряжение:', f"{min_tension:.0f}")
        ]
        
        for label, value in metrics_data:
            label_widget = Label(
                text=label, 
                font_size='16sp', 
                color=COLORS['text_primary'],
                halign='left'
            )
            value_widget = Label(
                text=str(value), 
                font_size='16sp', 
                color=COLORS['secondary'],
                bold=True,
                halign='right'
            )
            metrics_grid.add_widget(label_widget)
            metrics_grid.add_widget(value_widget)
        
        metrics_content.add_widget(metrics_grid)
        metrics_card.add_widget(metrics_content)
        self.detail_layout.add_widget(metrics_card)
        
        # Workout graph
        graph_path = workout.get('graph_path', '')
        if graph_path and os.path.exists(graph_path):
            graph_card = CardLayout(height=450)
            graph_content = BoxLayout(orientation='vertical', spacing=10, padding=15)
            
            graph_title = Label(
                text='ДИНАМИКА НАПРЯЖЕНИЯ МЫШЦЫ',
                font_size='18sp',
                color=COLORS['primary'],
                bold=True,
                size_hint_y=0.1
            )
            graph_content.add_widget(graph_title)
            
            try:
                graph_image = Image(
                    source=graph_path,
                    size_hint=(1, 0.9),
                    allow_stretch=True,
                    keep_ratio=True
                )
                graph_content.add_widget(graph_image)
            except Exception as e:
                error_label = Label(
                    text=f'Ошибка загрузки графика: {str(e)}',
                    font_size='14sp',
                    size_hint_y=0.9,
                    color=COLORS['danger']
                )
                graph_content.add_widget(error_label)
            
            graph_card.add_widget(graph_content)
            self.detail_layout.add_widget(graph_card)
        else:
            no_graph_card = CardLayout(height=80)
            no_graph_label = Label(
                text='График недоступен',
                font_size='16sp',
                color=COLORS['text_secondary']
            )
            no_graph_card.add_widget(no_graph_label)
            self.detail_layout.add_widget(no_graph_card)
        
        self.detail_layout.height = self.detail_layout.minimum_height
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'history'

class WorkoutApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(WorkoutMenuScreen(name='workout_menu'))
        sm.add_widget(WorkoutScreen(name='workouts'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        return sm

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('workouts', exist_ok=True)
    
    # Run the app
    WorkoutApp().run()