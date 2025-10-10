"""
Simulation Loading capabilities. It loads the simulations from either an XML or a CSV export
"""
import abc
import re
import logging
from typing import List
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import pandas as pd

from .simulation import Simulation
from .simulation_data import FlightEvent


def load_simulations_from_xml(file_path: str) -> List[Simulation]:
    """
    Loads all simulations from an OpenRocket XML file.
    """

    try:
        tree = ET.parse(file_path)
        # The loader now expects the parent <simulations> tag
        simulations_element = tree.find('.//simulations')
        if simulations_element is None:
            logging.warning("No <simulations> tag found in the XML file.")
            return []

        loader = XmlSimulationLoader(simulations_element)
        return loader.load()
    except Exception as e:
        logging.error(f"Could not load or parse XML file at {file_path}: {e}")
        return []


class BaseSimulationLoader(abc.ABC):
    """
    Abstract base class for all simulation loaders.
    """

    @abc.abstractmethod
    def load(self) -> List[Simulation]:
        """
        Loads simulation data and returns a list of Simulation objects.
        """


class CsvSimulationLoader(BaseSimulationLoader):
    """
    Loads a simulation from an exported CSV file.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Simulation]:
        try:
            # Using pandas to easily read and process the data
            flight_data = pd.read_csv(self.file_path, comment='#')

            column_map = {
                'Time (s)': 'time',
                'Altitude (m)': 'altitude',
                'Vertical velocity (m/s)': 'vertical_velocity',
                'Vertical acceleration (m/s²)': 'vertical_acceleration',
            }
            flight_data.rename(columns=column_map, inplace=True)

            sim = Simulation(
                name=self.file_path.split('/')[-1],  # Use filename as name
                description=f"Loaded from {self.file_path}",
                motor_config="unknown",  # Not available in CSV
                flight_data=flight_data
            )
            return [sim]  # Return as a list for consistency
        except FileNotFoundError:
            logging.error(f"Error: CSV file not found at {self.file_path}")
            return []


def _clean_header(header_text: str) -> str:
    """Converts a header like 'Vertical velocity (m/s²)' to 'vertical_velocity_ms2'."""
    text = header_text.lower().strip()
    # Replace spaces and parentheses with underscores
    text = re.sub(r'[\s\(\)]+', '_', text)
    # Remove invalid characters
    text = re.sub(r'[^a-z0-9_]', '', text)
    text = text.strip('_')
    return text


class XmlSimulationLoader(BaseSimulationLoader):
    """Loads one or more simulations from an OpenRocket XML element."""

    def __init__(self, simulations_element: Element):
        # Expects the <simulations> tag as input
        self.element = simulations_element

    def load(self) -> List[Simulation]:
        simulations = []
        for sim_element in self.element.findall('./simulation'):
            try:
                flightdata_el = sim_element.find('.//flightdata')
                if flightdata_el is None:
                    continue  # Skip if no flight data

                # Parse summary data from attributes
                summary_data = {
                    key: float(value) for key, value in flightdata_el.attrib.items()
                }

                # Get the main data branch (usually only one)
                branch_el = flightdata_el.find('.//databranch')
                if branch_el is None:
                    continue

                # Parse the column headers from the 'types' attribute
                headers_raw = branch_el.get('types').split(',')
                headers = [_clean_header(h) for h in headers_raw]

                # Parse all datapoints into a list of lists
                data_rows = []
                for dp in branch_el.findall('datapoint'):
                    if dp.text:
                        row_values = [
                            float(p) if p.strip().lower() != 'nan' else None
                            for p in dp.text.split(',')
                        ]
                        data_rows.append(row_values)

                df = pd.DataFrame(data_rows, columns=headers)

                # Parse flight events
                events = [
                    FlightEvent(
                        time=float(evt.get('time')),
                        type=evt.get('type'),
                        source=evt.get('source')
                    ) for evt in branch_el.findall('event')
                ]

                # Assemble the final Simulation object
                sim = Simulation(
                    name=sim_element.findtext('.//name', 'Unnamed Simulation'),
                    description=sim_element.findtext('.//description', ''),
                    motor_config=sim_element.find('.//conditions').get('configid', 'default'),
                    summary=summary_data,
                    events=events,
                    flight_data=df
                )
                simulations.append(sim)
            except Exception as e:
                sim_name = sim_element.findtext('.//name', 'unknown')
                logging.error(f"Failed to parse simulation '{sim_name}': {e}")
                continue

        return simulations
