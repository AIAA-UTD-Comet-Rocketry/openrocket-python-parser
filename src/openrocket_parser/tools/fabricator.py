import logging
import argparse
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from openrocket_parser.tools.fabricator_tool.main_screen import MainScreen
from openrocket_parser.tools.fabricator_tool.settings_screen import SettingsScreen
from openrocket_parser.units import METERS_TO_INCHES


class RocketApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = None

    def build(self):
        self.settings = {
            'export_format': 'svg',
            'export_dir': './exported/',
            'dpi': 96.0,
            'ui_scale': 100,
            'shape_color': (1, 1, 0, 1),
            'unit_conversion': METERS_TO_INCHES,
            'units': 'inches'
        }

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm


def main():
    parser = argparse.ArgumentParser(description="Generate 2D files from OpenRocket components for fabrication.")
    _ = parser.parse_args()

    logging.info(f"Opening fabricator...")
    RocketApp().run()


if __name__ == '__main__':
    main()
