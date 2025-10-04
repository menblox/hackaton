from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)  # Белый фон
        layout = FloatLayout()
        layout.add_widget(Label(text='Fitness Tracker', font_size=40, color=(0, 0.5, 0, 1), pos_hint={'top': 0.9}))  # Заголовок сверху
        plus_button = Button(
            text='New Workout',  # Текст вместо эмодзи
            font_size=30,
            size_hint=(0.4, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0.1, 0.6, 0.1, 1),  # Темно-зеленый фон
            color=(1, 1, 1, 1)  # Белый текст
        )
        plus_button.bind(on_press=self.switch_to_workouts)
        layout.add_widget(plus_button)
        self.add_widget(layout)

    def switch_to_workouts(self, instance):
        self.manager.current = 'workouts'

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)  # Белый фон
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_event = None
        self.timer_label = None

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        main_layout.add_widget(Label(text='Тренировки', font_size=40, color=(0, 0.5, 0, 1)))  # Заголовок сверху
        self.timer_label = Label(text='00:00', font_size=35, color=(0, 0.5, 0, 1))
        main_layout.add_widget(self.timer_label)

        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        start_button = Button(
            text='Start',  # Текст вместо эмодзи
            font_size=25,
            background_color=(0.1, 0.6, 0.1, 1),  # Темно-зеленый фон
            color=(1, 1, 1, 1)  # Белый текст
        )
        start_button.bind(on_press=self.start_workout)
        button_layout.add_widget(start_button)
        stop_button = Button(
            text='Stop',  # Текст вместо эмодзи
            font_size=25,
            background_color=(0.6, 0.1, 0.1, 1),  # Красный фон
            color=(1, 1, 1, 1)  # Белый текст
        )
        stop_button.bind(on_press=self.stop_workout)
        button_layout.add_widget(stop_button)
        main_layout.add_widget(button_layout)

        back_button = Button(
            text='Back',  # Текст вместо эмодзи
            font_size=20,
            size_hint_y=0.2,
            background_color=(0, 0, 0, 1),  # Черный фон
            color=(1, 1, 1, 1)  # Белый текст
        )
        back_button.bind(on_press=self.switch_to_main)
        main_layout.add_widget(back_button)
        self.add_widget(main_layout)

    def start_workout(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)  # Обновление каждую секунду
            print("Тренировка начата! Данные будут записаны в будущем.")

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

    def switch_to_main(self, instance):
        if self.timer_running:
            if self.timer_event:
                self.timer_event.cancel()
            self.timer_running = False
        self.manager.current = 'main'

class WorkoutApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(WorkoutScreen(name='workouts'))
        return sm

if __name__ == '__main__':
    WorkoutApp().run()