from typing import List
from xml.etree.ElementTree import Element

from src.openrocket_parser.components import register_component, XMLComponent, component_factory


@register_component('stage')
class Stage(XMLComponent):
    def __init__(self, element: Element):
        super().__init__(element)
        # A stage's direct children are its components
        self.subcomponents: List[XMLComponent] = [
            component_factory(e) for e in self.element
        ]