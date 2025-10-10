"""
FinSet related functionality
"""
from openrocket_parser.components.components import register_component, Subcomponent, XMLComponent


@register_component('finset')
class FinSet(Subcomponent):
    """
    FindSet Subcomponent from OpenRocket, created when a finset xml element is found
    """
    _FIELDS = [
        ('fincount', './/fincount', int, 4),
        ('rootchord', './/rootchord', XMLComponent.get_float, 0.0),
        ('tipchord', './/tipchord', XMLComponent.get_float, 0.0),
        ('height', './/height', XMLComponent.get_float, 0.0),
        # @TODO add the rest as needed
    ]
