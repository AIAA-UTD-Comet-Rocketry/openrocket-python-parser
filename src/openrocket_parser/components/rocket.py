"""
Rocket component related functionality. This is the top level component,
and all other components and subcomponents will be within the Rocket
"""

from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('rocket')
class Rocket(XMLComponent):
    """
    Rocket Main component, created once the rocket xml element is found in the .ork file
    Supports multi-stage setups
    """
    _FIELDS = [
        ("designer", ".//designer", str, "Unknown"),
        ("name", ".//name", str, "Unknown")
    ]

    def __init__(self, element: Element):
        super().__init__(element)
        self.stages = [component_factory(e) for e in self.findall('.//stage')]
