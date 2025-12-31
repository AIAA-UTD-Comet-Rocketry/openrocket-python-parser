"""
Handles the generation of SVG files for rocket components.
"""
import svgwrite
import math
from openrocket_parser.tools.fabricator_tool.geometry import FinConfiguration, GeometryEngine
from openrocket_parser.units import MILLIMETERS_PER_INCH


def export_component_to_svg(comp, filename, settings, hole_settings=None):
    """
    Exports a component (fin, ring, or bulkhead) to an SVG file.
    """
    if comp['type'] == 'fin':
        _export_fin(comp, filename, settings)
    elif comp['type'] == 'ring':
        _export_ring(comp, filename, settings, hole_settings)
    elif comp['type'] == 'bulkhead':
        _export_bulkhead(comp, filename, settings, hole_settings)


def _get_unit_to_px(settings):
    dpi = settings['dpi']
    is_mm = settings['units'] == 'millimeters'
    return dpi if not is_mm else (dpi / MILLIMETERS_PER_INCH)


def _export_fin(comp, filename, settings):
    """Exports a fin component to SVG."""
    unit_to_px = _get_unit_to_px(settings)
    margin = 0.5 * unit_to_px
    is_mm = settings['units'] == 'millimeters'

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

    # Scale points to pixels
    scaled_points = [(p[0] * unit_to_px, p[1] * unit_to_px) for p in points]

    min_x = min(p[0] for p in scaled_points)
    min_y = min(p[1] for p in scaled_points)
    max_x = max(p[0] for p in scaled_points)
    max_y = max(p[1] for p in scaled_points)

    width_px = (max_x - min_x) + 2 * margin
    height_px = (max_y - min_y) + 2 * margin
    
    width_phys = width_px / unit_to_px
    height_phys = height_px / unit_to_px
    unit_suffix = "mm" if is_mm else "in"

    dwg = svgwrite.Drawing(filename, size=(f"{width_phys:.3f}{unit_suffix}", f"{height_phys:.3f}{unit_suffix}"),
                           viewBox=f"0 0 {width_px} {height_px}")

    offset_x = -min_x + margin
    offset_y = -min_y + margin
    offset_points = [(p[0] + offset_x, p[1] + offset_y) for p in scaled_points]

    dwg.add(dwg.polygon(points=offset_points, fill='none', stroke='black', stroke_width=1))

    _add_svg_fin_labels(dwg, fin, offset_points, unit_to_px, offset_x, offset_y, unit_suffix)
    dwg.save()


def _export_ring(comp, filename, settings, hole_settings):
    """Exports a ring component to SVG."""
    unit_to_px = _get_unit_to_px(settings)
    margin = 0.5 * unit_to_px
    is_mm = settings['units'] == 'millimeters'

    od = comp['od'] * unit_to_px
    _id = comp['id'] * unit_to_px

    width_px = od + 2 * margin
    height_px = od + 2 * margin
    width_phys = width_px / unit_to_px
    height_phys = height_px / unit_to_px
    unit_suffix = "mm" if is_mm else "in"

    dwg = svgwrite.Drawing(filename, size=(f"{width_phys:.3f}{unit_suffix}", f"{height_phys:.3f}{unit_suffix}"),
                           viewBox=f"0 0 {width_px} {height_px}")

    center_coord = width_px / 2
    center = (center_coord, center_coord)

    dwg.add(dwg.circle(center=center, r=od / 2, fill='none', stroke='black', stroke_width=1))
    dwg.add(dwg.circle(center=center, r=_id / 2, fill='none', stroke='black', stroke_width=1))

    if hole_settings and hole_settings['enabled'] and hole_settings['diameter'] > 0:
        _draw_svg_hole(dwg, hole_settings, center, unit_to_px)

    _add_svg_ring_labels(dwg, comp, center, od, unit_suffix)
    dwg.save()


def _export_bulkhead(comp, filename, settings, hole_settings):
    """Exports a bulkhead component to SVG."""
    unit_to_px = _get_unit_to_px(settings)
    margin = 0.5 * unit_to_px
    is_mm = settings['units'] == 'millimeters'

    od = comp['od'] * unit_to_px

    width_px = od + 2 * margin
    height_px = od + 2 * margin
    width_phys = width_px / unit_to_px
    height_phys = height_px / unit_to_px
    unit_suffix = "mm" if is_mm else "in"

    dwg = svgwrite.Drawing(filename, size=(f"{width_phys:.3f}{unit_suffix}", f"{height_phys:.3f}{unit_suffix}"),
                           viewBox=f"0 0 {width_px} {height_px}")

    center_coord = width_px / 2
    center = (center_coord, center_coord)

    dwg.add(dwg.circle(center=center, r=od / 2, fill='none', stroke='black', stroke_width=1))

    if hole_settings and hole_settings['enabled'] and hole_settings['diameter'] > 0:
        _draw_svg_hole(dwg, hole_settings, center, unit_to_px)

    _add_svg_bulkhead_labels(dwg, comp, center, od, unit_suffix)
    dwg.save()


def _draw_svg_hole(dwg, hole_settings, center, unit_to_px):
    hole_dia = hole_settings['diameter'] * unit_to_px
    hole_x = 0
    hole_y = 0
    if not hole_settings['centered']:
        hole_x = hole_settings['x'] * unit_to_px
        hole_y = hole_settings['y'] * unit_to_px

    hole_center = (center[0] + hole_x, center[1] + hole_y)
    dwg.add(dwg.circle(center=hole_center, r=hole_dia / 2, fill='none', stroke='red', stroke_width=1))


def _add_svg_fin_labels(dwg, fin, offset_points, unit_to_px, offset_x, offset_y, unit_suffix):
    """Adds measurement labels to a fin SVG."""
    font_attrs = {'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'middle'}

    # Root Chord
    dwg.add(dwg.text(f"Root: {fin.root_chord:.3f}{unit_suffix}", 
                     insert=(offset_x + (fin.root_chord * unit_to_px) / 2, offset_y - 10),
                     **font_attrs))

    # Tip Chord (Bottom)
    sweep_length = fin.height * math.tan(math.radians(fin.sweep_angle))
    tip_y = offset_y + fin.height * unit_to_px
    tip_start_x = offset_x + sweep_length * unit_to_px
    dwg.add(dwg.text(f"Tip: {fin.tip_chord:.3f}{unit_suffix}", 
                     insert=(tip_start_x + (fin.tip_chord * unit_to_px) / 2, tip_y + 20), 
                     **font_attrs))

    # Height (Right)
    max_x_offset = max(p[0] for p in offset_points)
    side_font_attrs = font_attrs.copy()
    side_font_attrs['text_anchor'] = 'start'
    
    dwg.add(dwg.text(f"H: {fin.height:.3f}{unit_suffix}", 
                     insert=(max_x_offset + 10, offset_y + (fin.height * unit_to_px) / 2), 
                     **side_font_attrs))
    
    # Sweep Angle
    dwg.add(dwg.text(f"Sweep: {fin.sweep_angle:.1f}°", 
                     insert=(offset_x - 10, offset_y + (fin.height * unit_to_px) / 2), 
                     **{'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'end'}))


def _add_svg_ring_labels(dwg, comp, center, od, unit_suffix):
    """Adds measurement labels to a ring SVG."""
    font_attrs = {'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'middle'}
    dwg.add(dwg.text(f"OD: {comp['od']:.3f}{unit_suffix}", insert=(center[0], center[1] - od / 2 - 10), **font_attrs))
    dwg.add(dwg.text(f"ID: {comp['id']:.3f}{unit_suffix}", insert=(center[0], center[1] + od / 2 + 20), **font_attrs))


def _add_svg_bulkhead_labels(dwg, comp, center, od, unit_suffix):
    """Adds measurement labels to a bulkhead SVG."""
    font_attrs = {'font_size': '12px', 'font_family': 'Arial', 'fill': 'blue', 'text_anchor': 'middle'}
    dwg.add(dwg.text(f"OD: {comp['od']:.3f}{unit_suffix}", insert=(center[0], center[1] - od / 2 - 10), **font_attrs))
