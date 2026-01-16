import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineListItem

from openrocket_parser.tools.fabricator_tool.ui_components import PreviewWidget, ComponentSettingsPanel
from openrocket_parser.tools.fabricator_tool.geometry import GeometryEngine, FinConfiguration
from openrocket_parser.tools.fabricator_tool.ork_parser import load_ork_file
from openrocket_parser.tools.fabricator_tool.svg_exporter import export_component_to_svg


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)

        # State
        self.components = []
        self.selected_component = None
        self.current_filepath = None

        # UI Header
        header = MDBoxLayout(size_hint_y=0.1, spacing=10)
        btn_load = MDRaisedButton(text="Load .ork file")
        btn_load.bind(on_press=self.show_load_dialog)
        btn_settings = MDRaisedButton(text="Settings")
        btn_settings.bind(on_press=self.go_to_settings)
        btn_export = MDRaisedButton(text='Export Selection to SVG')
        btn_export.bind(on_press=self.export_selection)
        header.add_widget(btn_load)
        header.add_widget(btn_settings)
        header.add_widget(btn_export)
        layout.add_widget(header)

        # Main Content
        content = MDBoxLayout(orientation='horizontal', spacing=10)

        # Left: Component List
        self.scroll_list = MDList()
        
        scrollview = ScrollView(size_hint_x=0.3) # Occupy 30% of horizontal space
        scrollview.add_widget(self.scroll_list)
        content.add_widget(scrollview)

        # Center: Preview
        self.preview_area = PreviewWidget(size_hint_x=0.4)
        content.add_widget(self.preview_area)

        # Right: Settings Panel
        self.settings_panel = ComponentSettingsPanel(self.update_preview)
        content.add_widget(self.settings_panel)
        layout.add_widget(content)
        self.lbl_status = MDLabel(text='No file loaded', size_hint_y=0.1, halign="center")
        layout.add_widget(self.lbl_status)

        self.add_widget(layout)

    def go_to_settings(self, instance):
        self.manager.current = 'settings'

    def show_load_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        filechooser = FileChooserListView(path=os.getcwd(), filters=['*.ork'])
        content.add_widget(filechooser)

        buttons = BoxLayout(size_hint_y=None, height=44, spacing=5)
        btn_load = MDRaisedButton(text='Load')
        btn_cancel = MDFlatButton(text='Cancel')
        buttons.add_widget(btn_load)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)

        popup = Popup(title='Load .ork File', content=content, size_hint=(0.9, 0.9))

        def load_selected_file(instance):
            if filechooser.selection:
                self.load_file(filechooser.selection[0])
                popup.dismiss()

        btn_load.bind(on_press=load_selected_file)
        btn_cancel.bind(on_press=popup.dismiss)

        popup.open()

    def load_file(self, filepath):
        self.current_filepath = filepath
        self.lbl_status.text = f"Loaded: {os.path.basename(filepath)}"
        self.scroll_list.clear_widgets()

        self.components = load_ork_file(filepath)

        for i, comp in enumerate(self.components):
            item = OneLineListItem(text=comp['name'])
            item.bind(on_release=lambda x, idx=i: self.select_component(idx))
            self.scroll_list.add_widget(item)

    def refresh_data(self):
        if self.current_filepath:
            # Save current selection index
            selected_idx = -1
            if self.selected_component and self.selected_component in self.components:
                selected_idx = self.components.index(self.selected_component)

            self.load_file(self.current_filepath)

            if 0 <= selected_idx < len(self.components):
                self.select_component(selected_idx)

    def select_component(self, index):
        # Reset settings before selecting new component
        self.selected_component = None
        self.settings_panel.reset()
        
        comp = self.components[index]
        self.selected_component = comp
        self.lbl_status.text = f'Selected: {comp["name"]}'

        # Update settings panel availability
        app = App.get_running_app()
        self.settings_panel.update_for_component(comp, app.settings['units'])

        self.update_preview()

    def update_preview(self, *args):
        if not self.selected_component:
            return

        comp = self.selected_component
        hole_settings = self.settings_panel.get_settings()

        shape_data = {}
        if comp['type'] == 'fin':
            fin = FinConfiguration(
                root_chord=comp['root_chord'],
                tip_chord=comp['tip_chord'],
                height=comp['height'],
                sweep_angle=comp['sweep_angle'],
                tab_height=comp.get('tab_height', 0),
                tab_length=comp.get('tab_length', 0),
                tab_pos=comp.get('tab_pos', 0)
            )
            points = GeometryEngine.calculate_trapezoidal_fin(fin)
            # Pass fin info for labeling
            shape_data = {'type': 'polygon', 'points': points, 'fin_info': fin}
        elif comp['type'] == 'ring':
            shape_data = {'type': 'ring', 'od': comp['od'], 'id': comp['id']}
        elif comp['type'] == 'bulkhead':
            shape_data = {'type': 'bulkhead', 'od': comp['od']}

        if comp['type'] in ['ring', 'bulkhead']:
            shape_data['hole'] = hole_settings

        app = App.get_running_app()
        self.preview_area.draw_shape(shape_data, app.settings)

    def export_selection(self, instance):
        if not self.selected_component:
            self.lbl_status.text = 'Error: No component selected'
            return

        settings = App.get_running_app().settings
        export_dir = settings['export_dir']
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        filename = os.path.join(export_dir, f"{self.selected_component['name'].replace(' ', '_')}.{settings['export_format']}")
        comp = self.selected_component
        hole_settings = self.settings_panel.get_settings()

        export_component_to_svg(comp, filename, settings, hole_settings)
        self.lbl_status.text = f'Exported: {filename}'
