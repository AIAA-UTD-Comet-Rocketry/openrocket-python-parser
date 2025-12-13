"""
Defines the Kivy UI components for the LaserCutExporter application.
"""
import logging
import math
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Line


class PreviewWidget(Widget):
    """
    A widget for rendering a preview of a selected rocket component.
    It handles drawing, scaling, and centering of shapes.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_scale = 50 # Customizable scale factor for UI preview

    def draw_shape(self, shape_data):
        """
        Clears the canvas and all child widgets, then draws the new shape.
        """
        logging.debug(f"--- draw_shape called for: {shape_data.get('type', 'None')} ---")
        logging.debug(f"Before clearing, widget has {len(self.children)} children.")
        
        # Clear both the canvas (for lines) and all child widgets (for labels)
        self.canvas.clear()
        self.clear_widgets()
        
        logging.debug(f"After clearing, widget has {len(self.children)} children.")

        if not shape_data:
            return

        with self.canvas:
            Color(1, 1, 0)  # Set drawing color to yellow

            if shape_data['type'] == 'polygon':
                self._draw_polygon(shape_data)
            elif shape_data['type'] == 'ring':
                self._draw_ring(shape_data)
        
        logging.debug(f"After drawing, widget has {len(self.children)} children (the new labels).")

    def _draw_polygon(self, shape_data):
        """Draws a polygon (like a fin) on the canvas."""
        points = shape_data['points']
        
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        shape_width = (max_x - min_x) * self.ui_scale
        shape_height = (max_y - min_y) * self.ui_scale
        
        center_offset_x = (self.width - shape_width) / 2
        center_offset_y = (self.height - shape_height) / 2

        screen_points = []
        for x, y in points:
            screen_x = ((x - min_x) * self.ui_scale) + center_offset_x
            screen_y = ((y - min_y) * self.ui_scale) + center_offset_y
            screen_points.extend([screen_x, screen_y])

        Line(points=screen_points, width=2, close=True)
        
        if 'fin_info' in shape_data:
            self._add_fin_labels(shape_data['fin_info'], points)

    def _draw_ring(self, shape_data):
        """Draws a ring on the canvas."""
        od = shape_data['od']
        _id = shape_data['id']

        center_x = self.width / 2
        center_y = self.height / 2
        
        scaled_od = od * self.ui_scale
        scaled_id = _id * self.ui_scale

        Line(circle=(center_x, center_y, scaled_od / 2), width=2)
        Line(circle=(center_x, center_y, scaled_id / 2), width=2)
        
        self._add_ring_labels(od, _id, center_x, center_y, scaled_od)

    def _add_fin_labels(self, fin, points):
        """Adds measurement labels for a fin."""
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        shape_width = (max_x - min_x) * self.ui_scale
        shape_height = (max_y - min_y) * self.ui_scale
        
        center_offset_x = (self.width - shape_width) / 2
        center_offset_y = (self.height - shape_height) / 2

        # Root Chord
        root_center_x = ((fin.root_chord / 2 - min_x) * self.ui_scale) + center_offset_x
        root_y = ((-min_y) * self.ui_scale) + center_offset_y - 20
        self.add_label(f"Root: {fin.root_chord:.2f}\"", root_center_x, root_y)

        # Tip Chord
        sweep_len = fin.height * math.tan(math.radians(fin.sweep_angle))
        tip_center_x = ((sweep_len + fin.tip_chord / 2 - min_x) * self.ui_scale) + center_offset_x
        tip_y = ((fin.height - min_y) * self.ui_scale) + center_offset_y + 20
        self.add_label(f"Tip: {fin.tip_chord:.2f}\"", tip_center_x, tip_y)

        # Height
        height_x = ((max_x - min_x) * self.ui_scale) + center_offset_x + 40
        height_y = ((fin.height / 2 - min_y) * self.ui_scale) + center_offset_y
        self.add_label(f"H: {fin.height:.2f}\"", height_x, height_y)

        # Sweep Angle
        sweep_x = ((-min_x) * self.ui_scale) + center_offset_x - 40
        sweep_y = ((fin.height / 2 - min_y) * self.ui_scale) + center_offset_y
        self.add_label(f"Sweep: {fin.sweep_angle:.1f}°", sweep_x, sweep_y)

    def _add_ring_labels(self, od, _id, center_x, center_y, scaled_od):
        """Adds measurement labels for a ring."""
        self.add_label(f"OD: {od:.2f}\"", center_x, center_y + (scaled_od / 2) + 20)
        self.add_label(f"ID: {_id:.2f}\"", center_x, center_y - (scaled_od / 2) - 20)

    def add_label(self, text, x, y):
        """Adds a text label directly to this widget."""
        # lbl = Label(text=text, center_x=x, center_y=y, size_hint=(None, None), size=(120, 30), color=(0.2, 0.6, 1, 1))
        # self.add_widget(lbl)
