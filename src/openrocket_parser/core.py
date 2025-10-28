"""
Collection of base functionality to load OpenRocket .ork files
"""
import logging
from typing import Optional
import xml.etree.ElementTree as ET

from openrocket_parser.components.rocket import Rocket


def load_rocket_from_xml(file_path: str) -> Rocket:
    """
    Load the .ork file. If it fails, a ValueError will be returned
    :param file_path:
    :return:
    """
    rocket = load_rocket_from_xml_safe(file_path)
    if rocket is None:
        error = f'Could not load rocket from {file_path}'
        logging.error(error)
        raise ValueError(error)
    return rocket

def load_rocket_from_xml_safe(file_path: str, root_ele: str = 'rocket') -> Optional[Rocket]:
    """Loads an entire rocket definition from an OpenRocket XML file, catching errors if they happen """

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        # The main rocket element is usually <openrocket> or <rocket>, but it can be customized if needed.
        rocket_element = root.find(f'.//{root_ele}')
        if rocket_element is None:
            raise ValueError("Could not find a <rocket> element in the XML file.")

        return Rocket(rocket_element)
    except FileNotFoundError:
        logging.error(f"XML file not found at path: {file_path}")
        return None
    except ET.ParseError as e:
        logging.error(f"Error parsing XML file: {e}")
        return None
