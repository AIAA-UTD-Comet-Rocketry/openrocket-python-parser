"""
Defines the Kivy UI components for the LaserCutExporter application.
"""
import logging
import math
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Line, Rectangle

from openrocket_parser.units import MILLIMETERS_PER_INCH


class PreviewWidget(Widget):
    """
    A widget for rendering a preview of a selected rocket component.
    It handles drawing, scaling, and centering of shapes.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw_shape(self, shape_data, settings):
        """
        Clears the canvas and all child widgets, then draws the new shape.
        """
        logging.debug(f"--- draw_shape called for: {shape_data.get('type', 'None')} ---")
        self.canvas.clear()
        self.clear_widgets()

        logging.debug(f"After clearing, widget has {len(self.children)} children.")

        if not shape_data:
            return

        with self.canvas:
            Color(*settings['shape_color'])  # Use color from settings

            if shape_data['type'] == 'polygon':
                self._draw_polygon(shape_data, settings)
            elif shape_data['type'] == 'ring':
                self._draw_ring(shape_data, settings)
            elif shape_data['type'] == 'bulkhead':
                self._draw_bulkhead(shape_data, settings)

    def _draw_polygon(self, shape_data, settings):
        """Draws a polygon (like a fin) on the canvas."""
        points = shape_data['points']
        ui_scale = settings['ui_scale']

        # Adjust scale for mm to keep preview size reasonable
        if settings['units'] == 'millimeters':
            ui_scale /= MILLIMETERS_PER_INCH

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        shape_width = (max_x - min_x) * ui_scale
        shape_height = (max_y - min_y) * ui_scale
        
        center_offset_x = (self.width - shape_width) / 2
        center_offset_y = (self.height - shape_height) / 2

        screen_points = []
        for x, y in points:
            screen_x = ((x - min_x) * ui_scale) + center_offset_x + self.x
            screen_y = ((y - min_y) * ui_scale) + center_offset_y + self.y
            screen_points.extend([screen_x, screen_y])

        Line(points=screen_points, width=2, close=True)

        if 'fin_info' in shape_data:
            self._add_fin_labels(shape_data['fin_info'], points, settings, ui_scale)

    def _draw_ring(self, shape_data, settings):
        """Draws a ring on the canvas."""
        od = shape_data['od']
        _id = shape_data['id']
        ui_scale = settings['ui_scale']

        # Adjust scale for mm to keep preview size reasonable
        if settings['units'] == 'millimeters':
            ui_scale /= MILLIMETERS_PER_INCH

        center_x = self.center_x
        center_y = self.center_y

        scaled_od = od * ui_scale
        scaled_id = _id * ui_scale

        Line(circle=(center_x, center_y, scaled_od / 2), width=2)
        Line(circle=(center_x, center_y, scaled_id / 2), width=2)

        if 'hole' in shape_data:
            self._draw_hole(shape_data['hole'], center_x, center_y, ui_scale, settings)

        self._add_ring_labels(od, _id, center_x, center_y, scaled_od, settings)

    def _draw_bulkhead(self, shape_data, settings):
        """Draws a bulkhead on the canvas."""
        od = shape_data['od']
        ui_scale = settings['ui_scale']

        # Adjust scale for mm to keep preview size reasonable
        if settings['units'] == 'millimeters':
            ui_scale /= MILLIMETERS_PER_INCH

        center_x = self.center_x
        center_y = self.center_y

        scaled_od = od * ui_scale

        Line(circle=(center_x, center_y, scaled_od / 2), width=2)

        if 'hole' in shape_data:
            self._draw_hole(shape_data['hole'], center_x, center_y, ui_scale, settings)

        self._add_bulkhead_labels(od, center_x, center_y, scaled_od, settings)

    def _draw_hole(self, hole_data, center_x, center_y, ui_scale, settings):
        """Draws a configured hole on the canvas."""
        if not hole_data.get('enabled', False):
            return

        diameter = hole_data.get('diameter', 0.0)
        if diameter <= 0:
            return

        scaled_dia = diameter * ui_scale

        hole_x = 0
        hole_y = 0

        if not hole_data.get('centered', True):
            hole_x = hole_data.get('x', 0.0) * ui_scale
            hole_y = hole_data.get('y', 0.0) * ui_scale

        # Draw hole in red
        Color(1, 0, 0, 1)
        Line(circle=(center_x + hole_x, center_y + hole_y, scaled_dia / 2), width=1.5)
        # Reset color
        Color(*settings['shape_color'])

    def _add_fin_labels(self, fin, points, settings, ui_scale):
        """Adds measurement labels for a fin."""
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)

        shape_width = (max_x - min_x) * ui_scale
        
        center_offset_x = (self.width - shape_width) / 2
        center_offset_y = (self.height - (fin.height * ui_scale)) / 2

        unit_suffix = "mm" if settings['units'] == 'millimeters' else "\""

        # Root Chord
        root_center_x = ((fin.root_chord / 2 - min_x) * ui_scale) + center_offset_x
        root_y = ((-min_y) * ui_scale) + center_offset_y - 20
        self.add_label(f"Root: {fin.root_chord:.2f}{unit_suffix}", root_center_x, root_y)

        # Tip Chord
        sweep_len = fin.height * math.tan(math.radians(fin.sweep_angle))
        tip_center_x = ((sweep_len + fin.tip_chord / 2 - min_x) * ui_scale) + center_offset_x
        tip_y = ((fin.height - min_y) * ui_scale) + center_offset_y + 20
        self.add_label(f"Tip: {fin.tip_chord:.2f}{unit_suffix}", tip_center_x, tip_y)

        # Height
        height_x = ((max_x - min_x) * ui_scale) + center_offset_x + 40
        height_y = ((fin.height / 2 - min_y) * ui_scale) + center_offset_y
        self.add_label(f"H: {fin.height:.2f}{unit_suffix}", height_x, height_y)

        # Sweep Angle
        sweep_x = ((-min_x) * ui_scale) + center_offset_x - 40
        sweep_y = ((fin.height / 2 - min_y) * ui_scale) + center_offset_y
        self.add_label(f"Sweep: {fin.sweep_angle:.1f}°", sweep_x, sweep_y)

    def _add_ring_labels(self, od, _id, center_x, center_y, scaled_od, settings):
        """Adds measurement labels for a ring."""
        unit_suffix = "mm" if settings['units'] == 'millimeters' else "\""
        self.add_label(f"OD: {od:.2f}{unit_suffix}", center_x, center_y + (scaled_od / 2) + 20)
        self.add_label(f"ID: {_id:.2f}{unit_suffix}", center_x, center_y - (scaled_od / 2) - 20)

    def _add_bulkhead_labels(self, od, center_x, center_y, scaled_od, settings):
        """Adds measurement labels for a bulkhead."""
        unit_suffix = "mm" if settings['units'] == 'millimeters' else "\""
        self.add_label(f"OD: {od:.2f}{unit_suffix}", center_x, center_y + (scaled_od / 2) + 20)

    def add_label(self, text, x, y):
        """Adds a text label directly to this widget."""
        #lbl = Label(text=text, center_x=x, center_y=y, size_hint=(None, None), size=(120, 30), color=(0.2, 0.6, 1, 1))
        #self.add_widget(lbl)


class VisibleCheckBox(CheckBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)  # Slightly lighter grey
            # Draw a small square centered on the checkbox
            # CheckBox default size is usually around 30x30 or 40x40 depending on hint
            # We'll make a 20x20 box in the center
            self.bg_rect = Rectangle(size=(20, 20))
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        # Center the background rectangle
        cx, cy = self.center
        self.bg_rect.pos = (cx - 10, cy - 10)


class ComponentSettingsPanel(BoxLayout):
    def __init__(self, update_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = 0.3
        self.padding = 10
        self.spacing = 5
        self.update_callback = update_callback

        self.add_widget(Label(text="Hole Configuration", size_hint_y=None, height=40, bold=True))

        # Enable Hole
        row_enable = BoxLayout(size_hint_y=None, height=40)
        row_enable.add_widget(Label(text="Enable Hole"))
        self.chk_enable = VisibleCheckBox(active=False)
        self.chk_enable.bind(active=self.on_change)
        row_enable.add_widget(self.chk_enable)
        self.add_widget(row_enable)

        # Diameter
        row_dia = BoxLayout(size_hint_y=None, height=40)
        self.lbl_diameter = Label(text="Diameter")
        row_dia.add_widget(self.lbl_diameter)
        self.txt_diameter = TextInput(text="0.0", multiline=False)
        self.txt_diameter.bind(text=self.on_change)
        row_dia.add_widget(self.txt_diameter)
        self.add_widget(row_dia)

        # Center Checkbox
        row_center = BoxLayout(size_hint_y=None, height=40)
        row_center.add_widget(Label(text="Center Hole"))
        self.chk_center = VisibleCheckBox(active=True)
        self.chk_center.bind(active=self.on_change)
        row_center.add_widget(self.chk_center)
        self.add_widget(row_center)

        # X Position
        row_x = BoxLayout(size_hint_y=None, height=40)
        row_x.add_widget(Label(text="X Offset"))
        self.txt_x = TextInput(text="0.0", multiline=False, disabled=True)
        self.txt_x.bind(text=self.on_change)
        row_x.add_widget(self.txt_x)
        self.add_widget(row_x)

        # Y Position
        row_y = BoxLayout(size_hint_y=None, height=40)
        row_y.add_widget(Label(text="Y Offset"))
        self.txt_y = TextInput(text="0.0", multiline=False, disabled=True)
        self.txt_y.bind(text=self.on_change)
        row_y.add_widget(self.txt_y)
        self.add_widget(row_y)

        self.add_widget(Widget()) # Spacer

        # Initially hide the panel
        self.opacity = 0.0
        self.disabled = True

    def on_change(self, *args):
        # Update disabled state of X/Y based on Center checkbox
        is_centered = self.chk_center.active
        self.txt_x.disabled = is_centered
        self.txt_y.disabled = is_centered

        self.update_callback()

    def update_for_component(self, component, units='inches'):
        """Enables or disables the panel based on component type."""
        if component and component['type'] in ['ring', 'bulkhead']:
            self.disabled = False
            self.opacity = 1.0
            
            # Update unit label
            unit_name = "in" if units == 'inches' else "mm"
            self.lbl_diameter.text = f"Diameter ({unit_name})"
        else:
            self.disabled = True
            self.opacity = 0.0

    def reset(self):
        """Resets the settings to default values."""
        self.chk_enable.active = False
        self.txt_diameter.text = "0.0"
        self.chk_center.active = True
        self.txt_x.text = "0.0"
        self.txt_y.text = "0.0"

    def parse_value(self, text):
        if not text:
            return 0.0
        try:
            # Allow basic math expressions like 1/2
            return float(eval(text, {"__builtins__": None}, {}))
        except Exception:
            return 0.0

    def get_settings(self):
        dia = self.parse_value(self.txt_diameter.text)
        x = self.parse_value(self.txt_x.text)
        y = self.parse_value(self.txt_y.text)

        return {
            'enabled': self.chk_enable.active,
            'diameter': dia,
            'centered': self.chk_center.active,
            'x': x,
            'y': y
        }
