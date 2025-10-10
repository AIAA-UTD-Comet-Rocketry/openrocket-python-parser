from xml.etree.ElementTree import Element

from src.openrocket_parser.components import register_component, Subcomponent, component_factory


@register_component('bodytube')
class BodyTube(Subcomponent):
    def __init__(self, element: Element):
        super().__init__(element)
        # Handle nested single components explicitly
        motor_mount_element = self.element.find('.//motormount')
        self.motormount = component_factory(motor_mount_element) if motor_mount_element is not None else None
