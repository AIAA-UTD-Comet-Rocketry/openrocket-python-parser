"""
NoseCone functionality for generic nosecones. Each shape of nosecone may extend this one if it needs
to read completely different fields
"""

from openrocket_parser.components.components import register_component, Subcomponent


@register_component('nosecone')
class NoseCone(Subcomponent):
    """
    NoseCone Subcomponent from OpenRocket, created when a nosecone xml element is found
    """
    _FIELDS = [
        ('shape', './/shape', str, 'ogive'),
    ]

