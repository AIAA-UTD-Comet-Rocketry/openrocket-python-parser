"""
Handles the generation of SVG files for rocket components.
"""
import svgwrite
import math
from geometry import FinConfiguration, GeometryEngine


def export_to_svg(component):
    """
    Exports a given component to an SVG file.

    Args:
        component (dict): A dictionary containing the component's data.

    Returns:
        str: The filename of the generated SVG file.
    """
    filename = f"{component['name'].replace(' ', '_')}.svg"

    if component['type'] == 'fin':
        _export_fin(component, filename)
    elif component['type'] == 'ring':
        _export_ring(component, filename)

    return filename


def _export_fin(comp, filename):
    """Exports a fin component to SVG."""
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

    # Use 96 DPI for scaling (1 inch = 96 px)
    scale = 96.0
    margin = 0.5 * scale  # 0.5 inch margin

    scaled_points = [(p[0] * scale, p[1] * scale) for p in points]

    min_x = min(p[0] for p in scaled_points)
    min_y = min(p[1] for p in scaled_points)
    max_x = max(p[0] for p in scaled_points)
    max_y = max(p[1] for p in scaled_points)

    width_px = (max_x - min_x) + 2 * margin
    height_px = (max_y - min_y) + 2 * margin
    width_in = width_px / scale
    height_in = height_px / scale

    dwg = svgwrite.Drawing(filename, size=(f"{width_in:.3f}in", f"{height_in:.3f}in"),
                           viewBox=f"0 0 {width_px} {height_px}")

    offset_x = -min_x + margin
    offset_y = -min_y + margin
    offset_points = [(p[0] + offset_x, p[1] + offset_y) for p in scaled_points]

    dwg.add(dwg.polygon(points=offset_points, fill='none', stroke='black', stroke_width=1))

    _add_svg_fin_labels(dwg, fin, offset_points, scale)
    dwg.save()


def _export_ring(comp, filename):
    """Exports a ring component to SVG."""
    scale = 96.0
    margin = 0.5 * scale

    od = comp['od'] * scale
    _id = comp['id'] * scale

    width_px = od + 2 * margin
    height_px = od + 2 * margin
    width_in = width_px / scale
    height_in = height_px / scale

    dwg = svgwrite.Drawing(filename, size=(f"{width_in:.3f}in", f"{height_in:.3f}in"),
                           viewBox=f"0 0 {width_px} {height_px}")

    center_coord = width_px / 2
    center = (center_coord, center_coord)

    dwg.add(dwg.circle(center=center, r=od / 2, fill='none', stroke='black', stroke_width=1))
    dwg.add(dwg.circle(center=center, r=_id / 2, fill='none', stroke='black', stroke_width=1))

    _add_svg_ring_labels(dwg, comp, center, od)
    dwg.save()


def _add_svg_fin_labels(dwg, fin, offset_points, scale):
    """Adds measurement labels to a fin SVG."""
    font_attrs = {'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'middle'}

    min_x = min(p[0] for p in offset_points)
    max_x = max(p[0] for p in offset_points)
    min_y = min(p[1] for p in offset_points)
    max_y = max(p[1] for p in offset_points)

    # Root Chord
    dwg.add(dwg.text(f"Root: {fin.root_chord:.3f}\"", insert=(min_x + (fin.root_chord * scale) / 2, min_y - 10),
                     **font_attrs))
    # Tip Chord
    dwg.add(
        dwg.text(f"Tip: {fin.tip_chord:.3f}\"", insert=(max_x - (fin.tip_chord * scale) / 2, max_y + 20), **font_attrs))
    # Height
    side_attrs = font_attrs.copy()
    side_attrs['text_anchor'] = 'start'
    dwg.add(dwg.text(f"H: {fin.height:.3f}\"", insert=(max_x + 10, min_y + (fin.height * scale) / 2), **side_attrs))
    # Sweep Angle
    end_attrs = font_attrs.copy()
    end_attrs['text_anchor'] = 'end'
    dwg.add(
        dwg.text(f"Sweep: {fin.sweep_angle:.1f}°", insert=(min_x - 10, min_y + (fin.height * scale) / 2), **end_attrs))


def _add_svg_ring_labels(dwg, comp, center, od):
    """Adds measurement labels to a ring SVG."""
    font_attrs = {'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'middle'}
    dwg.add(dwg.text(f"OD: {comp['od']:.3f}\"", insert=(center[0], center[1] - od / 2 - 10), **font_attrs))
    dwg.add(dwg.text(f"ID: {comp['id']:.3f}\"", insert=(center[0], center[1] + od / 2 + 20), **font_attrs))
