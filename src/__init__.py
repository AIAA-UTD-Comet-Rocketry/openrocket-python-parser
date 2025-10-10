"""
Main entry point for openrocket_parser. Configures the logging, for now.
"""

import logging

# Configure the basic logging to show a specific formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
