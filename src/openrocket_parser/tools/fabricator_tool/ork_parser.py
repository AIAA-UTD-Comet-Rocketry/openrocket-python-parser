"""
Parses OpenRocket (.ork) files to extract component data for laser cutting.
"""
import math
import logging

from openrocket_parser import load_rocket_from_xml


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
                
    return extracted_components


def _m_to_in(meters):
    """Converts meters to inches."""
    return (meters or 0.0) * 39.3701


def _extract_fin_data(comp, name):
    """Extracts and calculates data for a TrapezoidFinSet."""
    height = _m_to_in(getattr(comp, 'height', 0.0))
    sweep_length = _m_to_in(getattr(comp, 'sweeplength', 0.0))
    
    sweep_angle = 0.0
    if height > 0:
        sweep_angle = math.degrees(math.atan(sweep_length / height))

    return {
        'name': name,
        'type': 'fin',
        'root_chord': _m_to_in(getattr(comp, 'rootchord', 0.0)),
        'tip_chord': _m_to_in(getattr(comp, 'tipchord', 0.0)),
        'height': height,
        'sweep_angle': sweep_angle,
        'tab_height': _m_to_in(getattr(comp, 'tabheight', 0.0)),
        'tab_length': _m_to_in(getattr(comp, 'tablength', 0.0)),
        'tab_pos': _m_to_in(getattr(comp, 'tabposition', 0.0)),
    }


def _extract_ring_data(comp, name):
    """Extracts and calculates data for a CenteringRing."""
    outer_radius = _m_to_in(getattr(comp, 'outerradius', 0.0))
    inner_radius = _m_to_in(getattr(comp, 'innerradius', 0.0))
    
    return {
        'name': name,
        'type': 'ring',
        'od': outer_radius * 2,
        'id': inner_radius * 2,
    }
