from dataclasses import dataclass, field
from typing import Dict, Any, List

import pandas as pd

from openrocket_parser.simulations.simulation_data import FlightEvent


@dataclass
class Simulation:
    """
    Holds the complete data for a single simulation run.
    Flight data is stored in a pandas DataFrame for easy analysis.
    """
    name: str
    description: str
    motor_config: str

    # Summary data from <flightdata> attributes
    summary: Dict[str, Any] = field(default_factory=dict)

    # List of discrete events
    events: List[FlightEvent] = field(default_factory=list)

    # Time-series data
    flight_data: pd.DataFrame = field(default_factory=pd.DataFrame)