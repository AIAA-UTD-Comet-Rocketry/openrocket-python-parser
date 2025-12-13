from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button


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

        btn_back = Button(text="Back", size_hint_y=None, height=40)
        btn_back.bind(on_press=self.go_to_main)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_enter(self, *args):
        """Called when the screen is displayed."""
        app = App.get_running_app()
        self.export_format.text = app.settings['export_format']
        self.export_dir.text = app.settings['export_dir']
        self.dpi_scale.text = str(app.settings['dpi'])
        self.ui_scale.text = str(app.settings['ui_scale'])
        self.color_picker.color = app.settings['shape_color']
        self.units.text = app.settings['units']

    def on_leave(self, *args):
        """Called when the screen is left."""
        app = App.get_running_app()
        app.settings['export_format'] = self.export_format.text
        app.settings['export_dir'] = self.export_dir.text
        app.settings['dpi'] = float(self.dpi_scale.text)
        app.settings['ui_scale'] = int(self.ui_scale.text)
        app.settings['shape_color'] = self.color_picker.color
        app.settings['units'] = self.units.text
        if self.units.text == 'inches':
            app.settings['unit_conversion'] = 39.3701

    def go_to_main(self, instance):
        self.manager.current = 'main'
