from typing import List
from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('stage')
class Stage(XMLComponent):
    def __init__(self, element: Element):
        super().__init__(element)
        self.subcomponents: List[XMLComponent] = [
            component_factory(e) for e in self.element
        ]