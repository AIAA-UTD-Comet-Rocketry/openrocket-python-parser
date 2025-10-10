"""
Simulation Data depends on a list of events from OpenRocket.
The timed events are used within the library as pandas dataframes
"""
from dataclasses import dataclass


@dataclass
class FlightEvent:
    """Represents a discrete flight event like apogee or burnout."""
    time: float
    type: str
    source: str = None
