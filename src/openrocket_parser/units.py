"""
Unit conversion utilities for OpenRocket Parser.
"""

METERS_TO_INCHES = 39.3701
METERS_TO_MILLIMETERS = 1000.0
MILLIMETERS_PER_INCH = 25.4

def meters_to_inches(meters):
    """Converts meters to inches."""
    return (meters or 0.0) * METERS_TO_INCHES

def meters_to_millimeters(meters):
    """Converts meters to millimeters."""
    return (meters or 0.0) * METERS_TO_MILLIMETERS

def inches_to_millimeters(inches):
    """Converts inches to millimeters."""
    return (inches or 0.0) * MILLIMETERS_PER_INCH

def millimeters_to_inches(millimeters):
    """Converts millimeters to inches."""
    if millimeters is None:
        return 0.0
    return millimeters / MILLIMETERS_PER_INCH
