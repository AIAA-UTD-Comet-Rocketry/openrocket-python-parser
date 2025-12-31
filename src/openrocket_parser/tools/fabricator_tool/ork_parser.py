"""
Parses OpenRocket (.ork) files to extract component data for laser cutting.
"""
import math
import logging
from kivy.app import App

from openrocket_parser import load_rocket_from_xml
from openrocket_parser.units import METERS_TO_INCHES


def _collect_subcomponents(component):
    """
    Recursively collects all subcomponents of a given component.
    Returns a list of components.
    """
    components = []
    if hasattr(component, 'subcomponents') and component.subcomponents:
        for child in component.subcomponents:
            components.append(child)
    return components


def load_ork_file(filepath):
    """
    Parses an OpenRocket .ork file and extracts data for laser-cuttable
    components like fins and centering rings.

    Args:
        filepath (str): The absolute path to the .ork file.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents
                    a component with its relevant geometric data. Returns an
                    empty list if parsing fails.
    """
    try:
        rocket = load_rocket_from_xml(filepath)
    except Exception as e:
        logging.error(f"Failed to load or parse the rocket from '{filepath}': {e}")
        return []

    extracted_components = []
    all_components = []

    # 1. Try to iterate through stages first (standard ORK structure)
    if hasattr(rocket, 'stages'):
        for stage in rocket.stages:
            # Collect all things inside this stage
            all_components.extend(_collect_subcomponents(stage))

    # 2. Fallback: If no stages found (or different structure), try root subcomponents
    if not all_components and hasattr(rocket, 'subcomponents'):
        all_components.extend(_collect_subcomponents(rocket))
    
    for comp in all_components:
        class_name = comp.__class__.__name__
        name = getattr(comp, 'name', f"Unnamed {class_name}")

        if class_name == 'TrapezoidFinSet':
            data = _extract_fin_data(comp, name)
            if data:
                extracted_components.append(data)
        elif class_name == 'CenteringRing':
            data = _extract_ring_data(comp, name)
            if data:
                extracted_components.append(data)
        elif class_name == 'Bulkhead':
            data = _extract_bulkhead_data(comp, name)
            if data:
                extracted_components.append(data)

    return extracted_components


def _convert_units(meters):
    """Converts meters to the currently selected unit (inches or mm)."""
    app = App.get_running_app()
    conversion = app.settings.get('unit_conversion', METERS_TO_INCHES)
    # logging.info(f"Converting {meters}m with factor {conversion}")
    return (meters or 0.0) * conversion


def _extract_fin_data(comp, name):
    """Extracts and calculates data for a TrapezoidFinSet."""
    height = _convert_units(getattr(comp, 'height', 0.0))
    sweep_length = _convert_units(getattr(comp, 'sweeplength', 0.0))

    sweep_angle = 0.0
    if height > 0:
        sweep_angle = math.degrees(math.atan(sweep_length / height))

    return {
        'name': name,
        'type': 'fin',
        'root_chord': _convert_units(getattr(comp, 'rootchord', 0.0)),
        'tip_chord': _convert_units(getattr(comp, 'tipchord', 0.0)),
        'height': height,
        'sweep_angle': sweep_angle,
        'tab_height': _convert_units(getattr(comp, 'tabheight', 0.0)),
        'tab_length': _convert_units(getattr(comp, 'tablength', 0.0)),
        'tab_pos': _convert_units(getattr(comp, 'tabposition', 0.0)),
    }


def _extract_ring_data(comp, name):
    """Extracts and calculates data for a CenteringRing."""
    outer_radius = _convert_units(getattr(comp, 'outerradius', 0.0))
    inner_radius = _convert_units(getattr(comp, 'innerradius', 0.0))

    return {
        'name': name,
        'type': 'ring',
        'od': outer_radius * 2,
        'id': inner_radius * 2,
    }


def _extract_bulkhead_data(comp, name):
    """Extracts and calculates data for a Bulkhead."""
    outer_radius = _convert_units(getattr(comp, 'outerradius', 0.0))

    return {
        'name': name,
        'type': 'bulkhead',
        'od': outer_radius * 2,
    }
