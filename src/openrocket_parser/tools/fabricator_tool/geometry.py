"""
Handles the geometric calculations and data structures for rocket components.

This module defines the shapes and logic required to translate component
parameters into drawable and exportable vector points.
"""
import math
from dataclasses import dataclass


@dataclass
class FinConfiguration:
    """
    Stores the geometric parameters for a trapezoidal fin set.
    All length values are in inches.
    """
    # Corresponds to 'Root chord' in OpenRocket
    root_chord: float
    # Corresponds to 'Tip chord' in OpenRocket
    tip_chord: float
    # Corresponds to 'Height' in OpenRocket (sometimes called 'span')
    height: float
    # Corresponds to 'Sweep angle' in OpenRocket (in degrees)
    sweep_angle: float
    # Height of the fin tab
    tab_height: float = 0.0
    # Length of the fin tab
    tab_length: float = 0.0
    # Position of the fin tab relative to the root chord's center
    tab_pos: float = 0.0


class GeometryEngine:
    """
    A utility class that converts component data into 2D shapes.
    """
    @staticmethod
    def calculate_trapezoidal_fin(fin: FinConfiguration) -> list[tuple[float, float]]:
        """
        Calculates the vertex points for a trapezoidal fin.

        The origin (0,0) is the leading edge of the root chord. The polygon is
        traced clockwise from this point.

        Args:
            fin: The FinConfiguration object containing the fin's dimensions.

        Returns:
            A list of (x, y) tuples defining the fin's polygon.
        """
        # Calculate sweep length from sweep angle and height
        sweep_length = fin.height * math.tan(math.radians(fin.sweep_angle))

        # Point 1: Leading edge root
        points = [(0.0, 0.0)]
        # Point 2: Leading edge tip
        points.append((sweep_length, fin.height))
        # Point 3: Trailing edge tip
        points.append((sweep_length + fin.tip_chord, fin.height))
        # Point 4: Trailing edge root
        points.append((fin.root_chord, 0))

        # If a tab exists, trace its path along the root chord
        if fin.tab_height > 0 and fin.tab_length > 0:
            # Tab position is relative to the center of the root chord
            root_center = fin.root_chord / 2
            tab_center = root_center + fin.tab_pos
            
            tab_start_x = tab_center - (fin.tab_length / 2)
            tab_end_x = tab_center + (fin.tab_length / 2)

            # Trace the tab points from the trailing edge root
            points.append((tab_end_x, 0))
            points.append((tab_end_x, -fin.tab_height))
            points.append((tab_start_x, -fin.tab_height))
            points.append((tab_start_x, 0))

        # Final Point: Close the polygon by returning to the origin
        points.append((0.0, 0.0))

        return points
