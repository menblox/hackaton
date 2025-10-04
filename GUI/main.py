from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
import json
import os
from datetime import datetime
import random
import matplotlib.pyplot as plt
import numpy as np

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        layout = FloatLayout()
        layout.add_widget(Label(text='Fitness Tracker', font_size=40, color=(0, 0.5, 0, 1), pos_hint={'top': 0.9}))
        start_button = Button(
            text='Start',
            font_size=30,
            size_hint=(0.4, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        start_button.bind(on_press=self.switch_to_workout_menu)
        layout.add_widget(start_button)
        self.add_widget(layout)

    def switch_to_workout_menu(self, instance):
        self.manager.current = 'workout_menu'

class WorkoutMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutMenuScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        layout = FloatLayout()
        layout.add_widget(Label(text='Workout Menu', font_size=40, color=(0, 0.5, 0, 1), pos_hint={'top': 0.9}))
        view_workouts_button = Button(
            text='View Workouts',
            font_size=30,
            size_hint=(0.4, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        view_workouts_button.bind(on_press=self.switch_to_history)
        layout.add_widget(view_workouts_button)
        start_workout_button = Button(
            text='Start Workout',
            font_size=30,
            size_hint=(0.4, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        start_workout_button.bind(on_press=self.switch_to_workouts)
        layout.add_widget(start_workout_button)
        back_button = Button(
            text='Back',
            font_size=30,
            size_hint=(0.4, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_press=self.switch_to_main)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def switch_to_history(self, instance):
        self.manager.current = 'history'

    def switch_to_workouts(self, instance):
        self.manager.current = 'workouts'

    def switch_to_main(self, instance):
        self.manager.current = 'main'

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_event = None
        self.timer_label = None
        self.sensor_data = []

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        main_layout.add_widget(Label(text='Тренировки', font_size=40, color=(0, 0.5, 0, 1)))
        self.timer_label = Label(text='00:00', font_size=35, color=(0, 0.5, 0, 1))
        main_layout.add_widget(self.timer_label)

        self.sensor_label = Label(text='Данные датчиков: не активны', font_size=20, color=(0, 0, 0.5, 1))
        main_layout.add_widget(self.sensor_label)

        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        start_button = Button(
            text='Start',
            font_size=25,
            size_hint=(0.5, 0.25),
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        start_button.bind(on_press=self.start_workout)
        button_layout.add_widget(start_button)
        stop_button = Button(
            text='Stop',
            font_size=25,
            size_hint=(0.5, 0.25),
            background_color=(0.6, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        stop_button.bind(on_press=self.stop_workout)
        button_layout.add_widget(stop_button)
        main_layout.add_widget(button_layout)

        save_button = Button(
            text='Save',
            font_size=25,
            size_hint=(1, 0.25),
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        save_button.bind(on_press=self.save_workout)
        main_layout.add_widget(save_button)

        back_button = Button(
            text='Back',
            font_size=25,
            size_hint=(1, 0.25),
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_press=self.switch_to_workout_menu)
        main_layout.add_widget(back_button)
        self.add_widget(main_layout)

    def start_workout(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
            self.sensor_event = Clock.schedule_interval(self.collect_sensor_data, 0.5)
            print("Тренировка начата!")

    def stop_workout(self, instance):
        if self.timer_running:
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
            if hasattr(self, 'sensor_event'):
                self.sensor_event.cancel()
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
            self.sensor_label.text = f'Выносливость: {endurance}, Мощность: {power}, Пульс: {heart_rate}'

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
                print(f"Тренировка сохранена: {workout_time} на {current_date}")
                if self.timer_running:
                    if self.timer_event:
                        self.timer_event.cancel()
                    if hasattr(self, 'sensor_event'):
                        self.sensor_event.cancel()
                    self.timer_running = False
                self.time_elapsed = 0
                self.sensor_data = []
                self.timer_label.text = '00:00'
                self.sensor_label.text = 'Данные датчиков: не активны'
                
                if 'history' in self.manager.screen_names:
                    self.manager.get_screen('history').update_history()
            else:
                print("Ошибка сохранения тренировки")

    def create_workout_graph(self, sensor_data, save_path):
        if not sensor_data:
            return
            
        times = [data['timestamp'] for data in sensor_data]
        endurance = [data['endurance'] for data in sensor_data]
        power = [data['power'] for data in sensor_data]
        heart_rate = [data['heart_rate'] for data in sensor_data]
        
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(times, endurance, 'b-', linewidth=2, label='Выносливость')
        plt.title('Динамика показателей во время тренировки')
        plt.ylabel('Выносливость')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 2)
        plt.plot(times, power, 'r-', linewidth=2, label='Мощность')
        plt.ylabel('Мощность')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 3)
        plt.plot(times, heart_rate, 'g-', linewidth=2, label='Пульс')
        plt.xlabel('Время (секунды)')
        plt.ylabel('Пульс (уд/мин)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
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

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(
            text='История тренировок',
            font_size='24sp',
            size_hint_y=0.1,
            color=(0, 0.5, 0, 1)
        )
        main_layout.add_widget(title)
        
        scroll_view = ScrollView(
            size_hint=(1, 0.8),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
        self.history_layout = BoxLayout(
            orientation='vertical',
            spacing=10, 
            size_hint_y=None,
            padding=10
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll_view.add_widget(self.history_layout)
        main_layout.add_widget(scroll_view)
        
        buttons_layout = BoxLayout(size_hint_y=0.1, spacing=10, padding=10)
        
        clear_btn = Button(
            text='Clear History',
            font_size='18sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_history)
        
        back_btn = Button(
            text='Back',
            font_size='18sp',
            background_color=(0.3, 0.3, 0.3, 1)
        )
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
                        height=150,
                        halign='center',
                        valign='middle'
                    )
                    no_workouts_label.bind(size=no_workouts_label.setter('text_size'))
                    self.history_layout.add_widget(no_workouts_label)
            else:
                no_db_label = Label(
                    text='База данных не найдена\n\nСохраните первую тренировку,\nчтобы создать базу данных',
                    font_size='18sp',
                    size_hint_y=None,
                    height=150,
                    halign='center',
                    valign='middle',
                    color=(0.5, 0, 0, 1)
                )
                no_db_label.bind(size=no_db_label.setter('text_size'))
                self.history_layout.add_widget(no_db_label)
                
        except Exception as e:
            error_label = Label(
                text=f'Ошибка загрузки данных:\n{str(e)}',
                font_size='16sp',
                size_hint_y=None,
                height=100,
                halign='center',
                valign='middle',
                color=(1, 0, 0, 1)
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.history_layout.add_widget(error_label)

    def create_workout_card(self, workout):
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,  # Немного уменьшили высоту карточки
            padding=[2, 2, 2, 2]
        )
        
        with card_container.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            card_container.rect = Rectangle(pos=card_container.pos, size=card_container.size)
        
        def update_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
        
        card_container.bind(pos=update_rect, size=update_rect)
        
        card_content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=5
        )
        
        with card_content.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            card_content.bg_rect = Rectangle(pos=card_content.pos, size=card_content.size)
        
        def update_bg_rect(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        card_content.bind(pos=update_bg_rect, size=update_bg_rect)
        
        date_parts = workout.get('date', 'Неизвестно').split(' ')
        date_text = date_parts[0] if len(date_parts) > 0 else 'Неизвестно'
        time_text = date_parts[1] if len(date_parts) > 1 else ''
        
        # УМЕНЬШИЛИ ШРИФТЫ ДЛЯ ПРЕДПРОСМОТРА
        date_label = Label(
            text=f"[b]{date_text}[/b] {' ' + time_text if time_text else ''}",
            markup=True,
            font_size='16sp',  # Уменьшили с 18sp
            size_hint_y=0.3,
            halign='left',
            valign='middle',
            color=(0, 0.3, 0.6, 1),
            text_size=(Window.width - 50, None)
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        time_label = Label(
            text=f"Длительность: {workout.get('time', '00:00')}",
            font_size='14sp',  # Уменьшили с 16sp
            size_hint_y=0.25,
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),
            text_size=(Window.width - 50, None)
        )
        time_label.bind(size=time_label.setter('text_size'))
        
        metrics = workout.get('metrics', {})
        metrics_text = (f"Выносливость: макс {metrics.get('max_endurance', 0):.0f}, средн {metrics.get('avg_endurance', 0):.1f}\n"
                       f"Мощность: макс {metrics.get('max_power', 0):.0f}, средн {metrics.get('avg_power', 0):.1f}\n"
                       f"Пульс: макс {metrics.get('max_heart_rate', 0):.0f}, средн {metrics.get('avg_heart_rate', 0):.1f}")
        
        metrics_label = Label(
            text=metrics_text,
            font_size='12sp',  # Уменьшили с 14sp
            size_hint_y=0.45,
            halign='left',
            valign='top',
            color=(0.4, 0.4, 0.4, 1),
            text_size=(Window.width - 50, None)
        )
        metrics_label.bind(size=metrics_label.setter('text_size'))
        
        card_content.add_widget(date_label)
        card_content.add_widget(time_label)
        card_content.add_widget(metrics_label)
        
        card_container.add_widget(card_content)
        
        card_button = Button(
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0)
        )
        card_button.bind(on_press=lambda instance, w=workout: self.show_workout_details(w))
        
        card_container.add_widget(card_button)
        
        return card_container

    def show_workout_details(self, workout):
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

class WorkoutDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutDetailScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.title_label = Label(
            text='Детали тренировки', 
            font_size=32,  # Увеличили шрифт
            size_hint_y=0.1,
            color=(0, 0.5, 0, 1)
        )
        self.main_layout.add_widget(self.title_label)
        
        scroll_view = ScrollView(
            size_hint=(1, 0.8),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
        self.detail_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        self.detail_layout.bind(minimum_height=self.detail_layout.setter('height'))
        scroll_view.add_widget(self.detail_layout)
        self.main_layout.add_widget(scroll_view)
        
        back_button = Button(
            text='Назад к истории',
            font_size=20,
            size_hint_y=0.1,
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_press=self.go_back)
        self.main_layout.add_widget(back_button)
        
        self.add_widget(self.main_layout)
    
    def load_workout_data(self, workout):
        self.detail_layout.clear_widgets()
        
        # Основная информация - УВЕЛИЧИЛИ ШРИФТЫ
        info_layout = GridLayout(cols=2, size_hint_y=None, height=140, spacing=10)
        
        info_layout.add_widget(Label(text='Дата:', font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        info_layout.add_widget(Label(text=workout.get('date', 'Неизвестно'), font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        
        info_layout.add_widget(Label(text='Время тренировки:', font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        info_layout.add_widget(Label(text=workout.get('time', '00:00'), font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        
        info_layout.add_widget(Label(text='Длительность (сек):', font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        info_layout.add_widget(Label(text=str(workout.get('duration_seconds', 0)), font_size=20, color=(0, 0, 0, 1)))  # Увеличили
        
        self.detail_layout.add_widget(info_layout)
        
        # Метрики тренировки - УВЕЛИЧИЛИ ШРИФТЫ
        metrics = workout.get('metrics', {})
        metrics_label = Label(
            text='МЕТРИКИ ТРЕНИРОВКИ',
            font_size=26,  # Увеличили
            size_hint_y=None,
            height=50,  # Увеличили
            color=(0.2, 0.4, 0.6, 1)
        )
        self.detail_layout.add_widget(metrics_label)
        
        metrics_layout = GridLayout(cols=2, size_hint_y=None, height=220, spacing=10)  # Увеличили высоту
        
        metrics_data = [
            ('Макс. выносливость:', f"{metrics.get('max_endurance', 0):.0f}"),
            ('Ср. выносливость:', f"{metrics.get('avg_endurance', 0):.1f}"),
            ('Макс. мощность:', f"{metrics.get('max_power', 0):.0f}"),
            ('Ср. мощность:', f"{metrics.get('avg_power', 0):.1f}"),
            ('Макс. пульс:', f"{metrics.get('max_heart_rate', 0):.0f}"),
            ('Ср. пульс:', f"{metrics.get('avg_heart_rate', 0):.1f}")
        ]
        
        for label, value in metrics_data:
            metrics_layout.add_widget(Label(text=label, font_size=18, color=(0, 0, 0, 1)))  # Увеличили
            metrics_layout.add_widget(Label(text=str(value), font_size=18, color=(0.3, 0.3, 0.3, 1)))  # Увеличили
        
        self.detail_layout.add_widget(metrics_layout)
        
        # График тренировки - УВЕЛИЧИЛИ ШРИФТЫ
        graph_path = workout.get('graph_path', '')
        if graph_path and os.path.exists(graph_path):
            graph_label = Label(
                text='ГРАФИК ПОКАЗАТЕЛЕЙ',
                font_size=26,  # Увеличили
                size_hint_y=None,
                height=50,  # Увеличили
                color=(0.2, 0.4, 0.6, 1)
            )
            self.detail_layout.add_widget(graph_label)
            
            try:
                graph_image = Image(
                    source=graph_path,
                    size_hint=(1, None),
                    height=400
                )
                self.detail_layout.add_widget(graph_image)
            except Exception as e:
                error_label = Label(
                    text=f'Ошибка загрузки графика: {str(e)}',
                    font_size=16,  # Увеличили
                    size_hint_y=None,
                    height=60,
                    color=(1, 0, 0, 1)
                )
                self.detail_layout.add_widget(error_label)
        else:
            no_graph_label = Label(
                text='График недоступен',
                font_size=18,  # Увеличили
                size_hint_y=None,
                height=60,
                color=(0.5, 0.5, 0.5, 1)
            )
            self.detail_layout.add_widget(no_graph_label)
        
        # УБРАЛИ ДАННЫЕ ДАТЧИКОВ (первые 10 записей)
        # Вместо этого можно добавить сводную статистику по датчикам
        sensor_data = workout.get('sensor_data', [])
        if sensor_data:
            summary_label = Label(
                text='СВОДКА ПО ДАТЧИКАМ',
                font_size=26,  # Увеличили
                size_hint_y=None,
                height=50,
                color=(0.2, 0.4, 0.6, 1)
            )
            self.detail_layout.add_widget(summary_label)
            
            summary_text = (f"Всего записей: {len(sensor_data)}\n"
                          f"Период измерения: {sensor_data[0].get('timestamp', 0)} - {sensor_data[-1].get('timestamp', 0)} сек\n"
                          f"Частота измерений: {len(sensor_data) / workout.get('duration_seconds', 1):.2f} записей/сек")
            
            summary_content = Label(
                text=summary_text,
                font_size=18,  # Увеличили
                size_hint_y=None,
                height=100,
                color=(0.4, 0.4, 0.4, 1),
                text_size=(Window.width - 40, None)
            )
            summary_content.bind(size=summary_content.setter('text_size'))
            self.detail_layout.add_widget(summary_content)
        
        self.detail_layout.height = self.detail_layout.minimum_height
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'history'

class WorkoutApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(WorkoutMenuScreen(name='workout_menu'))
        sm.add_widget(WorkoutScreen(name='workouts'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        return sm

if __name__ == '__main__':
    os.makedirs('workouts', exist_ok=True)
    WorkoutApp().run()