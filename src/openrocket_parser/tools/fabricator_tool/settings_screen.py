from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 1. Export Format
        layout.add_widget(Label(text='Export Format:'))
        self.export_format = Spinner(text='svg', values=('svg',), size_hint_y=None, height=40)
        layout.add_widget(self.export_format)

        # 2. Export Directory
        layout.add_widget(Label(text='Export Directory:'))
        self.export_dir = TextInput(text='.', size_hint_y=None, height=40)
        layout.add_widget(self.export_dir)

        # 3. DPI Scaling
        layout.add_widget(Label(text='DPI Scaling (Warning: expert setting):'))
        self.dpi_scale = TextInput(text='96.0', size_hint_y=None, height=40)
        layout.add_widget(self.dpi_scale)

        # 4. UI Scale
        layout.add_widget(Label(text='UI Scale:'))
        self.ui_scale = TextInput(text='50', size_hint_y=None, height=40)
        layout.add_widget(self.ui_scale)

        # 5. Shape Color
        layout.add_widget(Label(text='Shape Color:'))
        self.color_picker = ColorPicker(color=(1, 1, 0, 1), size_hint_y=None, height=200)
        layout.add_widget(self.color_picker)

        # 6. Conversion from meters to
        layout.add_widget(Label(text='Units (from meters to):'))
        self.units = Spinner(text='inches', values=('inches',), size_hint_y=None, height=40)
        layout.add_widget(self.units)
        self.conversion_value = 39.3701  # for inches

        self.add_widget(layout)
