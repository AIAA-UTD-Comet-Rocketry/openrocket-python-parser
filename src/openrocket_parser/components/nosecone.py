from src.openrocket_parser.components.components import register_component, Subcomponent


@register_component('nosecone')
class NoseCone(Subcomponent):
    # NoseCone might have specific fields, but if not, it's just this simple!
    pass
