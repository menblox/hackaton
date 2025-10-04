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
import random
import matplotlib.pyplot as plt
import numpy as np

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
        
        # Icon replaced with text
        history_icon = Label(
            text='H',
            font_size='40sp',
            size_hint_x=0.3,
            color=COLORS['primary'],
            bold=True
        )
        
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
        
        workout_icon = Label(
            text='W',
            font_size='40sp',
            size_hint_x=0.3,
            color=COLORS['primary'],
            bold=True
        )
        
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
        
        # Metrics
        metrics = workout.get('metrics', {})
        metrics_layout = GridLayout(cols=3, size_hint_y=0.6, spacing=10, padding=[0, 10, 0, 0])
        
        metrics_data = [
            ('Выносливость', f"{metrics.get('max_endurance', 0):.0f}"),
            ('Мощность', f"{metrics.get('max_power', 0):.0f}"),
            ('Пульс', f"{metrics.get('max_heart_rate', 0):.0f}")
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
            text='Данные датчиков: не активны',
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

    def start_workout(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
            self.sensor_event = Clock.schedule_interval(self.collect_sensor_data, 0.5)
            self.sensor_label.text = 'Тренировка начата! Данные собираются...'
            print("Тренировка начата!")

    def stop_workout(self, instance):
        if self.timer_running:
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
            if hasattr(self, 'sensor_event'):
                self.sensor_event.cancel()
            self.sensor_label.text = f'Тренировка остановлена. Время: {self.timer_label.text}'
            print(f"Тренировка остановлена. Время: {self.timer_label.text}")

    def collect_sensor_data(self, dt):
        if self.timer_running:
            endurance = random.randint(50, 100)
            power = random.randint(60, 120)
            heart_rate = random.randint(70, 160)
            
            sensor_reading = {
                'timestamp': self.time_elapsed,
                'endurance': endurance,
                'power': power,
                'heart_rate': heart_rate
            }
            
            self.sensor_data.append(sensor_reading)
            self.sensor_label.text = f'Выносливость: {endurance} | Мощность: {power} | Пульс: {heart_rate}'

    def update_timer(self, dt):
        if self.timer_running:
            self.time_elapsed += 1
            minutes = self.time_elapsed // 60
            seconds = self.time_elapsed % 60
            self.timer_label.text = f'{minutes:02d}:{seconds:02d}'

    def save_workout(self, instance):
        if self.time_elapsed > 0:
            minutes = self.time_elapsed // 60
            seconds = self.time_elapsed % 60
            workout_time = f'{minutes:02d}:{seconds:02d}'
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            endurance_values = [data['endurance'] for data in self.sensor_data] if self.sensor_data else [0]
            power_values = [data['power'] for data in self.sensor_data] if self.sensor_data else [0]
            heart_rate_values = [data['heart_rate'] for data in self.sensor_data] if self.sensor_data else [0]
            
            max_endurance = max(endurance_values)
            avg_endurance = sum(endurance_values) / len(endurance_values)
            max_power = max(power_values)
            avg_power = sum(power_values) / len(power_values)
            max_heart_rate = max(heart_rate_values)
            avg_heart_rate = sum(heart_rate_values) / len(heart_rate_values)
            
            workout_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            workout_folder = f'workouts/workout_{workout_id}'
            os.makedirs(workout_folder, exist_ok=True)
            
            graph_path = f'{workout_folder}/graph.png'
            self.create_workout_graph(self.sensor_data, graph_path)
            
            workout_entry = {
                'id': workout_id,
                'time': workout_time,
                'date': current_date,
                'duration_seconds': self.time_elapsed,
                'sensor_data': self.sensor_data,
                'workout_folder': workout_folder,
                'graph_path': graph_path,
                'metrics': {
                    'max_endurance': max_endurance,
                    'avg_endurance': round(avg_endurance, 2),
                    'max_power': max_power,
                    'avg_power': round(avg_power, 2),
                    'max_heart_rate': max_heart_rate,
                    'avg_heart_rate': round(avg_heart_rate, 2)
                }
            }
            
            success = self.save_to_database(workout_entry)
            if success:
                self.sensor_label.text = f'Тренировка сохранена! Время: {workout_time}'
                if self.timer_running:
                    if self.timer_event:
                        self.timer_event.cancel()
                    if hasattr(self, 'sensor_event'):
                        self.sensor_event.cancel()
                    self.timer_running = False
                self.time_elapsed = 0
                self.sensor_data = []
                self.timer_label.text = '00:00'
                
                if 'history' in self.manager.screen_names:
                    self.manager.get_screen('history').update_history()
            else:
                self.sensor_label.text = 'Ошибка сохранения тренировки'

    def create_workout_graph(self, sensor_data, save_path):
        if not sensor_data:
            return
            
        times = [data['timestamp'] for data in sensor_data]
        endurance = [data['endurance'] for data in sensor_data]
        power = [data['power'] for data in sensor_data]
        heart_rate = [data['heart_rate'] for data in sensor_data]
        
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(times, endurance, color='#2E86AB', linewidth=2.5, label='Выносливость')
        plt.title('Динамика показателей во время тренировки', fontsize=14, fontweight='bold')
        plt.ylabel('Выносливость', fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 2)
        plt.plot(times, power, color='#A23B72', linewidth=2.5, label='Мощность')
        plt.ylabel('Мощность', fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 3)
        plt.plot(times, heart_rate, color='#F18F01', linewidth=2.5, label='Пульс')
        plt.xlabel('Время (секунды)', fontweight='bold')
        plt.ylabel('Пульс (уд/мин)', fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
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
            if hasattr(self, 'sensor_event'):
                self.sensor_event.cancel()
            self.timer_running = False
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
        info_card = CardLayout(height=140)
        info_layout = GridLayout(cols=2, size_hint_y=1, spacing=10, padding=10)
        
        info_data = [
            ('Дата:', workout.get('date', 'Неизвестно')),
            ('Время тренировки:', workout.get('time', '00:00')),
            ('Длительность (сек):', str(workout.get('duration_seconds', 0)))
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
        
        # Workout metrics
        metrics = workout.get('metrics', {})
        metrics_card = CardLayout(height=220)
        metrics_content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        metrics_title = Label(
            text='МЕТРИКИ ТРЕНИРОВКИ',
            font_size='18sp',
            color=COLORS['primary'],
            bold=True,
            size_hint_y=0.2
        )
        metrics_content.add_widget(metrics_title)
        
        metrics_grid = GridLayout(cols=2, size_hint_y=0.8, spacing=15)
        
        metrics_data = [
            ('Макс. выносливость:', f"{metrics.get('max_endurance', 0):.0f}"),
            ('Ср. выносливость:', f"{metrics.get('avg_endurance', 0):.1f}"),
            ('Макс. мощность:', f"{metrics.get('max_power', 0):.0f}"),
            ('Ср. мощность:', f"{metrics.get('avg_power', 0):.1f}"),
            ('Макс. пульс:', f"{metrics.get('max_heart_rate', 0):.0f}"),
            ('Ср. пульс:', f"{metrics.get('avg_heart_rate', 0):.1f}")
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
                text='ГРАФИК ПОКАЗАТЕЛЕЙ',
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
        
        # Sensor summary
        sensor_data = workout.get('sensor_data', [])
        if sensor_data:
            summary_card = CardLayout(height=120)
            summary_content = BoxLayout(orientation='vertical', spacing=8, padding=15)
            
            summary_title = Label(
                text='СВОДКА ПО ДАТЧИКАМ',
                font_size='16sp',
                color=COLORS['primary'],
                bold=True,
                size_hint_y=0.3
            )
            
            summary_text = (f"• Всего записей: {len(sensor_data)}\n"
                          f"• Период измерения: {sensor_data[0].get('timestamp', 0)} - {sensor_data[-1].get('timestamp', 0)} сек\n"
                          f"• Частота измерений: {len(sensor_data) / workout.get('duration_seconds', 1):.2f} записей/сек")
            
            summary_label = Label(
                text=summary_text,
                font_size='14sp',
                color=COLORS['text_primary'],
                size_hint_y=0.7,
                halign='left'
            )
            summary_label.bind(size=summary_label.setter('text_size'))
            
            summary_content.add_widget(summary_title)
            summary_content.add_widget(summary_label)
            summary_card.add_widget(summary_content)
            self.detail_layout.add_widget(summary_card)
        
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