import logging

from .simulations.loader import XmlSimulationLoader, CsvSimulationLoader
from .simulations.simulation_data import FlightEvent
from components.components import component_factory
from simulations.loader import load_rocket_from_xml

print("OpenRocket Parser library loaded.") # Optional: a friendly message on import