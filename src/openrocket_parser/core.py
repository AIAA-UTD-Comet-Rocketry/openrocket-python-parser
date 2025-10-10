from typing import Optional, List

from src.openrocket_parser.components.rocket import Rocket

from src.openrocket_parser import logging
from src.openrocket_parser.simulations.loader import XmlSimulationLoader
from src.openrocket_parser.simulations.simulation import Simulation


def load_rocket_from_xml(file_path: str) -> Rocket:
    rocket = load_rocket_from_xml_safe(file_path)
    if rocket is None:
        raise ValueError(f'Could not load rocket from {file_path}')
    return rocket

def load_rocket_from_xml_safe(file_path: str) -> Optional[Rocket]:
    """Loads an entire rocket definition from an OpenRocket XML file."""
    import xml.etree.ElementTree as ET

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        # The main rocket element is usually <openrocket> or <rocket> // @TODO make this configurable
        rocket_element = root.find('.//rocket')
        if rocket_element is None:
            raise ValueError("Could not find a <rocket> element in the XML file.")

        return Rocket(rocket_element)
    except FileNotFoundError:
        logging.error(f"XML file not found at path: {file_path}")
        return None
    except ET.ParseError as e:
        logging.error(f"Error parsing XML file: {e}")
        return None


