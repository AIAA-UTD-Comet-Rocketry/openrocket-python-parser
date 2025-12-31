# OpenRocket Parser

A Python library to parse OpenRocket (.ork) XML files and simulation data into convenient Python objects and pandas DataFrames.

## Installing for usage
You can install this library with pip:
```bash
# Installing from pypi
pip install openrocket-python-parser

# Latest version
pip install git+https://github.com/AIAA-UTD-Comet-Rocketry/openrocket-python-parser

# Specific branch
pip install git+https://github.com/AIAA-UTD-Comet-Rocketry/openrocket-python-parser.git@branch-name

# Specific Tag
pip install git+https://github.com/AIAA-UTD-Comet-Rocketry/openrocket-python-parser.git@vMAJOR.MINOR.PATCH
```

## Contributing

```bash
# 1. Clone the repo
git clone https://github.com/AIAA-UTD-Comet-Rocketry/openrocket-python-parser

# 2. Create a virtual environment
cd openrocket-python-parser
python -m venv .venv

# 3. Activate the environment
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate.bat

# 4. Set the library as editable, `.` is the root folder of the cloned repo
pip install -e .

# 5. Install additional dependencies
pip install -r requirements.txt
```

## Basic Usage

Here's how to load simulation data from an OpenRocket file:

```python
from openrocket_parser.simulations.loader import load_simulations_from_xml

sims = load_simulations_from_xml('sample.ork')

if sims:
    # Get the first simulation
    my_sim = sims[0]

    print(f"Loaded simulation: {my_sim.name}")
    print(f"Time to Apogee: {my_sim.summary.get('timetoapogee')} seconds")

    # The flight data is a pandas DataFrame
    flight_df = my_sim.flight_data

    # Print the max altitude from the time-series data
    max_altitude_from_data = flight_df['altitude'].max()
    print(f"Max altitude from data: {max_altitude_from_data:.2f} meters")
```

# Tools
## Visualizer

The visualizer tools allows to visualize the simulation data in real-time, directly from the simulation results in OpenRocket

![OpenRocketTool.gif](docs/OpenRocketTool.gif)

### Basic Usage
```shell
usage: openrocket-visualizer [-h] [--sim SIM] [--speed SPEED] [--no-repeat] file

Animate OpenRocket flight simulation data tool.

positional arguments:
  file           Path to the OpenRocket (.ork) file.

options:
  -h, --help     show this help message and exit
  --sim SIM      The simulation number to visualize (1-based index). Default is 1.
  --speed SPEED  Playback speed multiplier (e.g., 2 for 2x speed, 0.5 for half speed). Default is 1.0.
  --no-repeat    Disable the animation from repeating when it finishes.
```

For convenience, a sample open rocket with basic information can be found in tests/sample.ork

```shell
# This runs the sample.ork simulation data at twice the speed, without repeating
# This requires the visualizer tool to be installed

openrocket-visualizer tests/sample.ork --speed 2 --no-repeat
```

## Fabricator

The fabricator tool allows you to extract 2D-printable components from an OpenRocket design and export them to SVG files for manufacturing.

### Basic Usage
```shell
usage: openrocket-fabricator [-h]

Launch the fabricator helper tool

options:
  -h, --help     show this help message and exit
```

```shell
# Example
openrocket-fabricator
```

### How to Use

1.  **Launch the tool** by running `openrocket-fabricator` in your terminal.
![FileLoaderScreen.jpg](docs/tools/fabricator/FileLoaderScreen.jpg)
2.  **Load an `.ork` file** using the "Load .ork file" button.
3.  **Select a component** from the list on the left. A preview will appear on the right.
![BulkheadScreen.jpg](docs/tools/fabricator/BulkheadScreen.jpg)
![CenteringRingSelection.jpg](docs/tools/fabricator/CenteringRingSelection.jpg)
4.  **Configure Holes (Optional)**: For centering rings and bulkheads, you can now add a custom hole.
    *   Enable the hole using the checkbox in the settings panel.
    *   Set the diameter.
    *   Choose to center it automatically or specify X/Y offsets.
5.  **Export the selection** to an SVG file using the "Export Selection to SVG" button.
![ExportedSVG.jpg](docs/tools/fabricator/ExportedSVG.jpg)

### Customizations
The settings allow to change the color of the UI's components for accessibility:
![SettingsView.jpg](docs/tools/fabricator/SettingsView.jpg)
1. Export Format (Only SVG available at the moment)
2. Export Directory (@TODO - Change the text into a directory picker)
3. DPI Scale: This setting enables the accurate translation from inches to pixes
4. UI Scale: Adjust the size of the selected component in the screen (does not affect SVG export)
5. Shape Color: The color used for the outline of the selected component
6. Conversion units: Currently only enables meters to inches conversion, as OpenRocket uses meters by default

![Settings-colorpicker.jpg](docs/tools/fabricator/Settings-colorpicker.jpg)
### What to Expect

The tool will generate an SVG file for the selected component, including dimension labels to aid in manufacturing. The exported file will be ready for use with laser cutters, CNC machines, or for creating templates.

### Example
Using a Falcon A1 pro - 20W diode laser, the SVGs generated by the tool were directly imported into Falcon Design Space, separated into line engraving and line cutting, and the result is below. The dimensions are 99.799% accurate in these tests.
![cut-pieces.jpg](docs/tools/fabricator/cut-pieces.jpg)
The total time for all the pieces was just under 24 minutes, with conservative cut and engraving speeds (Order of operations is important, make sure to cut last so the piece doesn't move):
1. Line Engraving
   1. Speed: 5000
   2. Power: 30
   3. Passes: 1
2. Image Engraving (CR Logo)
   1. Speed: 5000
   2. Power: 30
   3. Passes: 1
3. Line Cutting
   1. Speed: 400
   2. Power: 100
   3. Passes: 1

## Upcoming Features

*   **Multiple Holes & Symmetry:** Support for adding multiple holes with symmetry options (e.g., for mounting patterns).
*   **Tolerance Adjustments:** Implement a feature to apply a tolerance value that minimally scales the exported shapes. This can compensate for the kerf of a laser cutter, the diameter of an end mill, or other tooling variations.
*   **Configurable Labels:** Add options to configure if and where dimension labels are added to the exported SVG file, giving you more control over the final output.
