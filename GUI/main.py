from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
import json
import os
from datetime import datetime

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        try:
            Window.clearcolor = (1, 1, 1, 1)  # Белый фон
            layout = FloatLayout()
            layout.add_widget(Label(text='Fitness Tracker', font_size=40, color=(0, 0.5, 0, 1), pos_hint={'top': 0.9}))  # Заголовок сверху
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
        except Exception as e:
            print(f"Ошибка в MainScreen: {e}")

    def switch_to_workout_menu(self, instance):
        self.manager.current = 'workout_menu'

class WorkoutMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutMenuScreen, self).__init__(**kwargs)
        try:
            Window.clearcolor = (1, 1, 1, 1)  # Белый фон
            layout = FloatLayout()
            layout.add_widget(Label(text='Workout Menu', font_size=40, color=(0, 0.5, 0, 1), pos_hint={'top': 0.9}))  # Заголовок сверху
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
        except Exception as e:
            print(f"Ошибка в WorkoutMenuScreen: {e}")

    def switch_to_history(self, instance):
        self.manager.current = 'history'

    def switch_to_workouts(self, instance):
        self.manager.current = 'workouts'

    def switch_to_main(self, instance):
        self.manager.current = 'main'

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)
        try:
            Window.clearcolor = (1, 1, 1, 1)  # Белый фон
            self.time_elapsed = 0
            self.timer_running = False
            self.timer_event = None
            self.timer_label = None

            main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
            main_layout.add_widget(Label(text='Тренировки', font_size=40, color=(0, 0.5, 0, 1)))
            self.timer_label = Label(text='00:00', font_size=35, color=(0, 0.5, 0, 1))
            main_layout.add_widget(self.timer_label)

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
        except Exception as e:
            print(f"Ошибка в WorkoutScreen: {e}")

    def start_workout(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
            print("Тренировка начата!")

    def stop_workout(self, instance):
        if self.timer_running:
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
            print(f"Тренировка остановлена. Время: {self.timer_label.text}")

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
            workout_entry = {'time': workout_time, 'date': current_date}
            self.save_to_file(workout_entry)
            print(f"Время сохранено: {workout_time} на {current_date}")
            if self.timer_running:
                if self.timer_event:
                    self.timer_event.cancel()
                self.timer_running = False
            self.time_elapsed = 0
            self.timer_label.text = '00:00'
            if 'history' in self.manager.screen_names:
                self.manager.get_screen('history').update_history()

    def save_to_file(self, workout_entry):
        file_name = 'workout_history.json'
        history = []
        try:
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    history = json.load(f)
                    print(f"Загружено из файла: {history}")
            if not isinstance(history, list):
                history = []
            history.append(workout_entry)
            with open(file_name, 'w') as f:
                json.dump(history, f, indent=2)
                print(f"Сохранено в файл: {history}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def switch_to_workout_menu(self, instance):
        if self.timer_running:
            if self.timer_event:
                self.timer_event.cancel()
            self.timer_running = False
        self.manager.current = 'workout_menu'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        try:
            Window.clearcolor = (1, 1, 1, 1)  # Белый фон
            main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
            main_layout.add_widget(Label(text='История тренировок', font_size=40, color=(0, 0.5, 0, 1)))
            self.history_label = Label(text='Нет записей', font_size=25, color=(0, 0.5, 0, 1))
            main_layout.add_widget(self.history_label)
            clear_button = Button(
                text='Clear History',
                font_size=20,
                size_hint_y=0.2,
                background_color=(0.6, 0.1, 0.1, 1),
                color=(1, 1, 1, 1)
            )
            clear_button.bind(on_press=self.clear_history)
            main_layout.add_widget(clear_button)
            back_button = Button(
                text='Back',
                font_size=20,
                size_hint_y=0.2,
                background_color=(0, 0, 0, 1),
                color=(1, 1, 1, 1)
            )
            back_button.bind(on_press=self.switch_to_workout_menu)
            main_layout.add_widget(back_button)
            self.add_widget(main_layout)
            self.update_history()
        except Exception as e:
            print(f"Ошибка в HistoryScreen: {e}")

    def update_history(self):
        file_name = 'workout_history.json'
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r') as f:
                    history = json.load(f)
                    print(f"История из файла: {history}")
                    if history:
                        display_text = '\n'.join([f"Дата: {entry['date']} - Время: {entry['time']}" for entry in history])
                        self.history_label.text = display_text if display_text else 'Нет записей'
                    else:
                        self.history_label.text = 'Нет записей'
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON. Файл может быть поврежден.")
                self.history_label.text = 'Нет записей'
        else:
            self.history_label.text = 'Нет записей'

    def clear_history(self, instance):
        file_name = 'workout_history.json'
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print("История очищена.")
                self.update_history()
            except Exception as e:
                print(f"Ошибка при очистке: {e}")
        else:
            self.history_label.text = 'Нет записей'

    def switch_to_workout_menu(self, instance):
        self.manager.current = 'workout_menu'

class WorkoutApp(App):
    def build(self):
        try:
            sm = ScreenManager(transition=NoTransition())
            sm.add_widget(MainScreen(name='main'))
            sm.add_widget(WorkoutMenuScreen(name='workout_menu'))
            sm.add_widget(WorkoutScreen(name='workouts'))
            sm.add_widget(HistoryScreen(name='history'))
            return sm
        except Exception as e:
            print(f"Ошибка в WorkoutApp: {e}")
            return None

if __name__ == '__main__':
    try:
        WorkoutApp().run()
    except Exception as e:
        print(f"Ошибка при запуске: {e}")