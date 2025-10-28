"""
Expose the usable components to the library user
"""

from .simulations.loader import XmlSimulationLoader, CsvSimulationLoader
from .simulations.simulation_data import FlightEvent
from .components.components import component_factory
from .core import load_rocket_from_xml

"""
Main entry point for openrocket_parser. Configures the logging, for now.
"""

import logging

# Configure the basic logging to show a specific formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
