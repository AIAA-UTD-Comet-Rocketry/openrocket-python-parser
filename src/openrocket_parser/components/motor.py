"""
All Motor related functionality to represent OpenRocket motors and motor related subcomponents
"""

from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('motor')
class Motor(XMLComponent):
    """
    Motor Subcomponent from OpenRocket, created when a motor xml element is found
    """
    _FIELDS = [
        ('designation', './/designation', str, ''),
        ('manufacturer', './/manufacturer', str, ''),
        ('diameter', './/diameter', XMLComponent.get_float, 0.0),
        ('length', './/length', XMLComponent.get_float, 0.0),
    ]

@register_component('motormount')
class MotorMount(XMLComponent):
    """
    MotorMount Subcomponent from OpenRocket, created when a motormount xml element is found
    """
    _FIELDS = [
        ('ignition_event', './/ignitionevent', str, 'launch'),
        ('overhang', './/overhang', XMLComponent.get_float, 0.0),
    ]

    def __init__(self, element: Element):
        super().__init__(element)
        self.motors = [component_factory(e) for e in self.findall('.//motor')]
