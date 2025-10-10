from dataclasses import dataclass, field


@dataclass
class FlightEvent:
    """Represents a discrete flight event like apogee or burnout."""
    time: float
    type: str
    source: str = None
