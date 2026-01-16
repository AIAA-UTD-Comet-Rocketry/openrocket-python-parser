from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.colorpicker import ColorPicker

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

from openrocket_parser.units import METERS_TO_INCHES, METERS_TO_MILLIMETERS


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'

        # Main layout for the screen
        root_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)

        # ScrollView for settings
        scroll = ScrollView(size_hint=(1, 1))
        
        # Content layout inside ScrollView
        content = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        content.bind(minimum_height=content.setter('height'))

        # 1. Export Format
        content.add_widget(MDLabel(text='Export Format:', size_hint_y=None, height=30))
        self.export_format = Spinner(text='svg', values=('svg',), size_hint_y=None, height=40)
        content.add_widget(self.export_format)

        # 2. Export Directory
        self.export_dir = MDTextField(text='.', hint_text="Export Directory", size_hint_y=None, height=40)
        content.add_widget(self.export_dir)

        # 3. DPI Scaling
        self.dpi_scale = MDTextField(text='96.0', hint_text="DPI Scaling (Warning: expert setting)", size_hint_y=None, height=40)
        content.add_widget(self.dpi_scale)

        # 4. UI Scale
        self.ui_scale = MDTextField(text='50', hint_text="UI Scale", size_hint_y=None, height=40)
        content.add_widget(self.ui_scale)

        # 5. Shape Color
        content.add_widget(MDLabel(text='Shape Color:', size_hint_y=None, height=30))
        self.color_picker = ColorPicker(color=(1, 1, 0, 1), size_hint_y=None, height=500)
        content.add_widget(self.color_picker)

        # 6. Conversion from meters to
        content.add_widget(MDLabel(text='Units (from meters to):', size_hint_y=None, height=30))
        self.units = Spinner(text='inches', values=('inches', 'millimeters'), size_hint_y=None, height=40)
        content.add_widget(self.units)
        self.conversion_value = METERS_TO_INCHES

        # 7. Tolerance
        self.tolerance = MDTextField(text='0.0', hint_text="Tolerance (Kerf offset)", size_hint_y=None, height=40)
        content.add_widget(self.tolerance)

        scroll.add_widget(content)
        root_layout.add_widget(scroll)

        # Back Button
        btn_back = MDRaisedButton(text="Back", size_hint_y=None, height=50)
        btn_back.bind(on_press=self.go_to_main)
        root_layout.add_widget(btn_back)

        self.add_widget(root_layout)

    def on_enter(self, *args):
        """Called when the screen is displayed."""
        app = App.get_running_app()
        self.export_format.text = app.settings['export_format']
        self.export_dir.text = app.settings['export_dir']
        self.dpi_scale.text = str(app.settings['dpi'])
        self.ui_scale.text = str(app.settings['ui_scale'])
        self.color_picker.color = app.settings['shape_color']
        self.units.text = app.settings['units']
        self.tolerance.text = str(app.settings.get('tolerance', 0.0))

    def on_leave(self, *args):
        """Called when the screen is left."""
        app = App.get_running_app()
        app.settings['export_format'] = self.export_format.text
        app.settings['export_dir'] = self.export_dir.text
        app.settings['dpi'] = float(self.dpi_scale.text)
        app.settings['ui_scale'] = int(self.ui_scale.text)
        app.settings['shape_color'] = self.color_picker.color
        app.settings['units'] = self.units.text
        app.settings['tolerance'] = float(self.tolerance.text) if self.tolerance.text else 0.0
        if self.units.text == 'inches':
            app.settings['unit_conversion'] = METERS_TO_INCHES
        elif self.units.text == 'millimeters':
            app.settings['unit_conversion'] = METERS_TO_MILLIMETERS
        
        # Refresh data in main screen if units changed
        if self.manager.has_screen('main'):
            main_screen = self.manager.get_screen('main')
            main_screen.refresh_data()

    def go_to_main(self, instance):
        self.manager.current = 'main'
