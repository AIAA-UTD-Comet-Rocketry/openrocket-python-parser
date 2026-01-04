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
from kivy.uix.spinner import Spinner
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

    def _get_ui_scale(self, settings):
        ui_scale = settings['ui_scale']
        if settings['units'] == 'millimeters':
            ui_scale /= MILLIMETERS_PER_INCH
        return ui_scale

    def _draw_polygon(self, shape_data, settings):
        """Draws a polygon (like a fin) on the canvas."""
        points = shape_data['points']
        ui_scale = self._get_ui_scale(settings)

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
        ui_scale = self._get_ui_scale(settings)

        center_x = self.center_x
        center_y = self.center_y

        scaled_od = od * ui_scale
        scaled_id = _id * ui_scale

        Line(circle=(center_x, center_y, scaled_od / 2), width=2)
        Line(circle=(center_x, center_y, scaled_id / 2), width=2)

        if 'hole' in shape_data:
            self._draw_holes(shape_data['hole'], center_x, center_y, ui_scale, settings)

        self._add_ring_labels(od, _id, center_x, center_y, scaled_od, settings)

    def _draw_bulkhead(self, shape_data, settings):
        """Draws a bulkhead on the canvas."""
        od = shape_data['od']
        ui_scale = self._get_ui_scale(settings)

        center_x = self.center_x
        center_y = self.center_y

        scaled_od = od * ui_scale

        Line(circle=(center_x, center_y, scaled_od / 2), width=2)

        if 'hole' in shape_data:
            self._draw_holes(shape_data['hole'], center_x, center_y, ui_scale, settings)

        self._add_bulkhead_labels(od, center_x, center_y, scaled_od, settings)

    def _draw_holes(self, hole_data, center_x, center_y, ui_scale, settings):
        """Draws configured holes on the canvas."""
        hole_type = hole_data.get('type', 'None')
        if hole_type == 'None':
            return

        diameter = hole_data.get('diameter', 0.0)
        if diameter <= 0:
            return

        scaled_dia = diameter * ui_scale
        
        # Base position
        hole_x = 0
        hole_y = 0
        if not hole_data.get('centered', True):
            hole_x = hole_data.get('x', 0.0) * ui_scale
            hole_y = hole_data.get('y', 0.0) * ui_scale

        Color(1, 0, 0, 1) # Red for holes

        if hole_type == 'Single (Eyebolt)':
            self._draw_single_hole(center_x + hole_x, center_y + hole_y, scaled_dia)
            
            if hole_data.get('symmetric', False):
                # Mirror across Y axis (negate X)
                # Note: hole_x is relative to center, so -hole_x is the mirror
                self._draw_single_hole(center_x - hole_x, center_y + hole_y, scaled_dia)

        elif hole_type == 'Double (U-Bolt)':
            separation = hole_data.get('separation', 0.0) * ui_scale
            # Draw two holes centered around the position
            # Assuming separation is center-to-center distance
            # And the pair is centered at (hole_x, hole_y)
            
            # Hole 1
            h1_x = hole_x - (separation / 2)
            h1_y = hole_y
            self._draw_single_hole(center_x + h1_x, center_y + h1_y, scaled_dia)
            
            # Hole 2
            h2_x = hole_x + (separation / 2)
            h2_y = hole_y
            self._draw_single_hole(center_x + h2_x, center_y + h2_y, scaled_dia)

            if hole_data.get('symmetric', False):
                # Mirror the pair
                # Mirror Hole 1
                mh1_x = -h1_x
                mh1_y = h1_y
                self._draw_single_hole(center_x + mh1_x, center_y + mh1_y, scaled_dia)
                
                # Mirror Hole 2
                mh2_x = -h2_x
                mh2_y = h2_y
                self._draw_single_hole(center_x + mh2_x, center_y + mh2_y, scaled_dia)

        Color(*settings['shape_color']) # Reset color

    def _draw_single_hole(self, x, y, diameter):
        Line(circle=(x, y, diameter / 2), width=1.5)

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

        # Hole Type Spinner
        row_type = BoxLayout(size_hint_y=None, height=40)
        row_type.add_widget(Label(text="Type"))
        self.spin_type = Spinner(
            text='None',
            values=('None', 'Single (Eyebolt)', 'Double (U-Bolt)'),
            size_hint_x=1.5
        )
        self.spin_type.bind(text=self.on_change)
        row_type.add_widget(self.spin_type)
        self.add_widget(row_type)

        # Diameter
        self.row_dia = BoxLayout(size_hint_y=None, height=40)
        self.lbl_diameter = Label(text="Diameter")
        self.row_dia.add_widget(self.lbl_diameter)
        self.txt_diameter = TextInput(text="0.0", multiline=False)
        self.txt_diameter.bind(text=self.on_change)
        self.row_dia.add_widget(self.txt_diameter)
        self.add_widget(self.row_dia)

        # Separation (for U-Bolt)
        self.row_sep = BoxLayout(size_hint_y=None, height=40)
        self.lbl_sep = Label(text="Separation")
        self.row_sep.add_widget(self.lbl_sep)
        self.txt_sep = TextInput(text="0.0", multiline=False)
        self.txt_sep.bind(text=self.on_change)
        self.row_sep.add_widget(self.txt_sep)
        self.add_widget(self.row_sep)

        # Center Checkbox
        self.row_center = BoxLayout(size_hint_y=None, height=40)
        self.row_center.add_widget(Label(text="Center Hole(s)"))
        self.chk_center = VisibleCheckBox(active=True)
        self.chk_center.bind(active=self.on_change)
        self.row_center.add_widget(self.chk_center)
        self.add_widget(self.row_center)

        # X Position
        self.row_x = BoxLayout(size_hint_y=None, height=40)
        self.row_x.add_widget(Label(text="X Offset"))
        self.txt_x = TextInput(text="0.0", multiline=False, disabled=True)
        self.txt_x.bind(text=self.on_change)
        self.row_x.add_widget(self.txt_x)
        self.add_widget(self.row_x)

        # Y Position
        self.row_y = BoxLayout(size_hint_y=None, height=40)
        self.row_y.add_widget(Label(text="Y Offset"))
        self.txt_y = TextInput(text="0.0", multiline=False, disabled=True)
        self.txt_y.bind(text=self.on_change)
        self.row_y.add_widget(self.txt_y)
        self.add_widget(self.row_y)

        # Symmetric Mirror (for Centering Ring)
        self.row_sym = BoxLayout(size_hint_y=None, height=40)
        self.row_sym.add_widget(Label(text="Symmetric Mirror"))
        self.chk_sym = VisibleCheckBox(active=False)
        self.chk_sym.bind(active=self.on_change)
        self.row_sym.add_widget(self.chk_sym)
        self.add_widget(self.row_sym)

        self.add_widget(Widget()) # Spacer

        # Initially hide the panel
        self.opacity = 0.0
        self.disabled = True

    def on_change(self, *args):
        hole_type = self.spin_type.text
        is_none = hole_type == 'None'
        is_ubolt = hole_type == 'Double (U-Bolt)'
        is_centered = self.chk_center.active

        # Visibility logic
        self.row_dia.opacity = 0 if is_none else 1
        self.row_dia.disabled = is_none
        self.txt_diameter.disabled = is_none

        self.row_sep.opacity = 1 if is_ubolt else 0
        self.row_sep.disabled = not is_ubolt
        self.txt_sep.disabled = not is_ubolt

        self.row_center.opacity = 0 if is_none else 1
        self.row_center.disabled = is_none
        self.chk_center.disabled = is_none

        self.row_x.opacity = 0 if is_none else 1
        self.row_x.disabled = is_none or is_centered
        self.txt_x.disabled = is_none or is_centered

        self.row_y.opacity = 0 if is_none else 1
        self.row_y.disabled = is_none or is_centered
        self.txt_y.disabled = is_none or is_centered

        # Symmetric row visibility is handled in update_for_component
        if self.row_sym.opacity == 1:
             self.row_sym.disabled = is_none
             self.chk_sym.disabled = is_none

        self.update_callback()

    def update_for_component(self, component, units='inches'):
        """Enables or disables the panel based on component type."""
        if component and component['type'] in ['ring', 'bulkhead']:
            self.disabled = False
            self.opacity = 1.0
            
            # Update unit label
            unit_name = "in" if units == 'inches' else "mm"
            self.lbl_diameter.text = f"Bolt Dia ({unit_name})"
            self.lbl_sep.text = f"Separation ({unit_name})"

            # Show symmetric option only for rings
            if component['type'] == 'ring':
                self.row_sym.opacity = 1
                self.row_sym.disabled = self.spin_type.text == 'None'
            else:
                self.row_sym.opacity = 0
                self.row_sym.disabled = True
        else:
            self.disabled = True
            self.opacity = 0.0

        # Trigger visibility update
        self.on_change()

    def reset(self):
        """Resets the settings to default values."""
        self.spin_type.text = 'None'
        self.txt_diameter.text = "0.0"
        self.txt_sep.text = "0.0"
        self.chk_center.active = True
        self.txt_x.text = "0.0"
        self.txt_y.text = "0.0"
        self.chk_sym.active = False

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
        sep = self.parse_value(self.txt_sep.text)
        x = self.parse_value(self.txt_x.text)
        y = self.parse_value(self.txt_y.text)

        return {
            'type': self.spin_type.text,
            'diameter': dia,
            'separation': sep,
            'centered': self.chk_center.active,
            'x': x,
            'y': y,
            'symmetric': self.chk_sym.active and self.row_sym.opacity == 1
        }
