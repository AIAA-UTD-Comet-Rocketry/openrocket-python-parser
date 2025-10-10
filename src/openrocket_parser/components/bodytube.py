"""
BodyTube Component related functionality
"""


from xml.etree.ElementTree import Element

from openrocket_parser.components.components import (
    register_component, Subcomponent, component_factory
)


@register_component('bodytube')
class BodyTube(Subcomponent):
    """
    BodyTube Subcomponent from OpenRocket, created when a bodytube xml element is found
    """
    motormount = None
    def __init__(self, element: Element):
        super().__init__(element)
        motor_mount_element = self.element.find('.//motormount')
        if motor_mount_element is not None:
            self.motormount = component_factory(motor_mount_element)
