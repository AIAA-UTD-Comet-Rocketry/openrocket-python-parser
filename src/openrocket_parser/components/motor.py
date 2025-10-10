from xml.etree.ElementTree import Element

from src.openrocket_parser.components import register_component, XMLComponent, component_factory


@register_component('motor')
class Motor(XMLComponent):
    _FIELDS = [
        ('designation', './/designation', str, ''),
        ('manufacturer', './/manufacturer', str, ''),
        ('diameter', './/diameter', XMLComponent._get_float, 0.0),
        ('length', './/length', XMLComponent._get_float, 0.0),
    ]

@register_component('motormount')
class MotorMount(XMLComponent):
    _FIELDS = [
        ('ignition_event', './/ignitionevent', str, 'launch'),
        ('overhang', './/overhang', XMLComponent._get_float, 0.0),
    ]

    def __init__(self, element: Element):
        super().__init__(element)
        self.motors = [component_factory(e) for e in self.findall('.//motor')]
