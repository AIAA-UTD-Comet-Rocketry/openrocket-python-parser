# OpenRocket Parser

A Python library to parse OpenRocket (.ork) XML files and simulation data into convenient Python objects and pandas DataFrames.

## Installation

You can install this library directly from GitHub using pip:

```bash
pip install git+[https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
```

## Basic Usage

Here's how to load simulation data from an OpenRocket file:

```python
from openrocket_parser.loaders import load_simulations_from_xml

# Load all simulations from the file
sims = load_simulations_from_xml('my_rocket.ork')

if sims:
    # Get the first simulation
    my_sim = sims[0]

    print(f"Loaded simulation: {my_sim.name}")
    print(f"Time to Apogee: {my_sim.summary.get('timetoapogee')} seconds")

    # The flight data is a pandas DataFrame
    flight_df = my_sim.flight_data
    
    # Print the max altitude from the time-series data
    max_altitude_from_data = flight_df['altitude_m'].max()
    print(f"Max altitude from data: {max_altitude_from_data:.2f} meters")
```