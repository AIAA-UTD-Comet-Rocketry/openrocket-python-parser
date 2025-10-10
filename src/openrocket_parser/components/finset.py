from openrocket_parser.components.components import register_component, Subcomponent, XMLComponent


@register_component('finset')
class FinSet(Subcomponent):
    _FIELDS = [
        ('fincount', './/fincount', int, 4),
        ('rootchord', './/rootchord', XMLComponent._get_float, 0.0),
        ('tipchord', './/tipchord', XMLComponent._get_float, 0.0),
        ('height', './/height', XMLComponent._get_float, 0.0),
        # @TODO add the rest
    ]