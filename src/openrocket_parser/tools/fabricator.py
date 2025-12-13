import logging
from dataclasses import dataclass
import math

import argparse
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
import svgwrite
import os
from tools.fabricator_tool.ork_parser import load_ork_file
from tools.fabricator_tool.ui_components import PreviewWidget
from tools.fabricator_tool.geometry import GeometryEngine


@dataclass
class FinConfiguration:
    # Corresponds to 'Root chord' in OpenRocket
    root_chord: float
    # Corresponds to 'Tip chord' in OpenRocket. This defines the length of the top edge.
    tip_chord: float
    # Corresponds to 'Height' in OpenRocket (sometimes called 'span')
    height: float
    # Corresponds to 'Sweep angle' in OpenRocket (in degrees)
    sweep_angle: float
    tab_height: float = 0.0
    tab_length: float = 0.0
    tab_pos: float = 0.0


class RocketBuilder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # State
        self.components = []
        self.selected_component = None

        # UI Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_load = Button(text="Load .ork file", background_color=(0.2, 0.6, 0.8, 1))
        btn_load.bind(on_press=self.show_load_dialog)
        self.lbl_status = Label(text='No file loaded')
        header.add_widget(btn_load)
        header.add_widget(self.lbl_status)
        self.add_widget(header)

        # Main Content
        content = BoxLayout(orientation='horizontal', spacing=10)

        # Left: Component List
        self.scroll_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.scroll_list.bind(minimum_height=self.scroll_list.setter('height'))
        
        scrollview = ScrollView(size_hint_x=0.4) # Occupy 40% of horizontal space
        scrollview.add_widget(self.scroll_list)
        content.add_widget(scrollview)

        # Right: Preview
        self.preview_area = PreviewWidget()
        content.add_widget(self.preview_area)

        self.add_widget(content)

        # Footer
        footer = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_export = Button(text='Export Selection to SVG', background_color=(0.2, 0.8, 0.2, 1))
        btn_export.bind(on_press=self.export_selection)
        footer.add_widget(btn_export)
        self.add_widget(footer)

    def show_load_dialog(self, instance):
        self.load_file(r"C:\Users\fenrr\iCloudDrive\Rocketry\L1 - Silver Surfer\rocket.ork")

    def load_file(self, filepath):
        self.lbl_status.text = f"Loaded: {os.path.basename(filepath)}"
        self.scroll_list.clear_widgets()

        self.components = load_ork_file(filepath)

        for i, comp in enumerate(self.components):
            btn = Button(text=comp['name'], size_hint_y=None, height=40)
            btn.bind(on_press=lambda x, idx=i: self.select_component(idx))
            self.scroll_list.add_widget(btn)

    def select_component(self, index):
        comp = self.components[index]
        self.selected_component = comp
        self.lbl_status.text = f'Selected: {comp['name']}'

        # Generate Geometry
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

        self.preview_area.draw_shape(shape_data)

    def export_selection(self, instance):
        if not self.selected_component:
            self.lbl_status.text = 'Error: No component selected'
            return

        filename = f"{self.selected_component['name'].replace(' ', '_')}.svg"
        comp = self.selected_component
        
        # Use 96 DPI for scaling (1 inch = 96 px)
        scale = 96.0 
        margin = 0.5 * scale  # 0.5 inch margin

        if comp['type'] == 'fin':
            fin = FinConfiguration(
                root_chord=comp['root_chord'],
                tip_chord=comp['tip_chord'],
                height=comp['height'],
                sweep_angle=comp['sweep_angle'],
                tab_height=comp.get('tab_height', 0.0),
                tab_length=comp.get('tab_length', 0.0),
                tab_pos=comp.get('tab_pos', 0.0)
            )
            points = GeometryEngine.calculate_trapezoidal_fin(fin)

            # Scale points
            scaled_points = [(p[0] * scale, p[1] * scale) for p in points]

            # Find bounding box
            min_x = min(p[0] for p in scaled_points)
            min_y = min(p[1] for p in scaled_points)
            max_x = max(p[0] for p in scaled_points)
            max_y = max(p[1] for p in scaled_points)
            
            # Calculate document dimensions
            width_px = (max_x - min_x) + 2 * margin
            height_px = (max_y - min_y) + 2 * margin
            
            width_in = width_px / scale
            height_in = height_px / scale
            
            # Initialize drawing with inch units
            dwg = svgwrite.Drawing(filename, size=(f"{width_in:.3f}in", f"{height_in:.3f}in"), 
                                   viewBox=f"0 0 {width_px} {height_px}")

            offset_x = -min_x + margin
            offset_y = -min_y + margin

            # Create offset points
            offset_points = [(p[0] + offset_x, p[1] + offset_y) for p in scaled_points]

            dwg.add(dwg.polygon(points=offset_points, fill='none', stroke='black', stroke_width=1))
            
            # Measurements
            font_attrs = {
                'font_size': '12px',
                'font_family': 'Arial',
                'fill': 'blue',
                'text_anchor': 'middle'
            }
            
            # Root Chord (Top)
            dwg.add(dwg.text(f"Root: {fin.root_chord:.3f}\"", 
                             insert=(offset_x + (fin.root_chord * scale) / 2, offset_y - 10),
                             **font_attrs))
            
            # Tip Chord (Bottom)
            sweep_length = fin.height * math.tan(math.radians(fin.sweep_angle))
            tip_y = offset_y + fin.height * scale
            tip_start_x = offset_x + sweep_length * scale
            dwg.add(dwg.text(f"Tip: {fin.tip_chord:.3f}\"", 
                             insert=(tip_start_x + (fin.tip_chord * scale) / 2, tip_y + 20),
                             **font_attrs))
                             
            # Height (Right)
            max_x_offset = max(p[0] for p in offset_points)
            side_font_attrs = font_attrs.copy()
            side_font_attrs['text_anchor'] = 'start'
            
            dwg.add(dwg.text(f"H: {fin.height:.3f}\"", 
                             insert=(max_x_offset + 10, offset_y + (fin.height * scale) / 2),
                             **side_font_attrs))

            # Sweep Angle (Left of the shape, to avoid interference)
            # Position it to the left of the leading edge
            dwg.add(dwg.text(f"Sweep: {fin.sweep_angle:.1f}°", 
                             insert=(offset_x - 10, offset_y + (fin.height * scale) / 2),
                             **{'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'end'}))

        elif comp['type'] == 'ring':
            # Scale dimensions
            od = comp['od'] * scale
            id = comp['id'] * scale
            
            # Dimensions
            width_px = od + 2 * margin
            height_px = od + 2 * margin
            width_in = width_px / scale
            height_in = height_px / scale

            dwg = svgwrite.Drawing(filename, size=(f"{width_in:.3f}in", f"{height_in:.3f}in"), 
                                   viewBox=f"0 0 {width_px} {height_px}")

            # Center coordinates
            center_coord = width_px / 2
            center = (center_coord, center_coord)

            dwg.add(dwg.circle(center=center, r=od / 2, fill='none', stroke='black', stroke_width=1))
            dwg.add(dwg.circle(center=center, r=id / 2, fill='none', stroke='black', stroke_width=1))
            
            font_attrs = {
                'font_size': '12px',
                'font_family': 'Arial',
                'fill': 'blue',
                'text_anchor': 'middle'
            }
            # OD Label (Top, outside)
            dwg.add(dwg.text(f"OD: {comp['od']:.3f}\"", insert=(center[0], center[1] - od/2 - 10), **font_attrs))
            # ID Label (Bottom, outside OD to avoid interference)
            dwg.add(dwg.text(f"ID: {comp['id']:.3f}\"", insert=(center[0], center[1] + od/2 + 20), **font_attrs))

        dwg.save()
        self.lbl_status.text = f'Exported: {filename}'


class RocketApp(App):
    def build(self):
        return RocketBuilder()


def main():
    """Main function to parse arguments and launch the visualizer."""
    parser = argparse.ArgumentParser(description="Generate 2D files from OpenRocket components for fabrication.")

    # Load data using our library
    logging.info(f"Opening fabricator...")
    RocketApp().run()


if __name__ == '__main__':
    main()
