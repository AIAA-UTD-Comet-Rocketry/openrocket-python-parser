from dataclasses import dataclass, field
from typing import List, Dict, Any
import pandas as pd


@dataclass
class FlightEvent:
    """Represents a discrete flight event like apogee or burnout."""
    time: float
    type: str
    source: str = None
