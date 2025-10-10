from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('rocket')
class Rocket(XMLComponent):
    def __init__(self, element: Element):
        super().__init__(element)
        self.stages = [component_factory(e) for e in self.findall('.//stage')]

