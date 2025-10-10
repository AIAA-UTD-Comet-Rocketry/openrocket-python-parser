import logging
from typing import Type, List
from xml.etree.ElementTree import Element

COMPONENT_REGISTRY = {}

def register_component(tag_name: str):
    """A decorator to automatically register component classes in the factory."""

    def decorator(cls: Type['XMLComponent']):
        COMPONENT_REGISTRY[tag_name] = cls
        return cls

    return decorator


def component_factory(element: Element) -> 'XMLComponent':
    """Creates a component instance based on the XML element's tag."""
    tag = element.tag
    component_class = COMPONENT_REGISTRY.get(tag)

    if component_class:
        return component_class(element)

    logging.warning(f"No specific class found for tag '{tag}'. Using default Subcomponent.")
    # Fallback to a generic component if the tag is not recognized.
    return Subcomponent(element)


class XMLComponent:
    """
    An improved base class for all XML-based components.

    It uses a declarative `_FIELDS` map to automatically parse and assign attributes,
    reducing boilerplate code in subclasses.
    """
    # Define fields to be parsed from XML.
    # Format: ('attribute_name', 'xml_path', type_conversion_function, default_value)
    _FIELDS = [
        ('name', './/name', str, lambda e: e.tag),  # Use a lambda for dynamic default
        ('id', './/id', str, None),
        ('configid', './/configid', str, None),
    ]

    def __init__(self, element: Element):
        if element is None:
            raise ValueError("Cannot initialize XMLComponent with a None element.")
        self.element: Element = element
        self.tag: str = element.tag

        # Automatically parse all fields defined in the class hierarchy
        all_fields = []
        for cls in reversed(self.__class__.__mro__):
            if hasattr(cls, '_FIELDS'):
                all_fields.extend(cls._FIELDS)

        for attr_name, path, converter, default in all_fields:
            self._parse_and_set_attr(attr_name, path, converter, default)

    def _parse_and_set_attr(self, attr_name, path, converter, default):
        """Finds text in XML, converts it, and sets it as an attribute."""
        raw_value = self.element.findtext(path)

        value = None
        if raw_value is not None:
            try:
                value = converter(raw_value)
            except (ValueError, TypeError) as e:
                logging.error(
                    f"Could not convert value '{raw_value}' for '{attr_name}' using {converter.__name__}. Error: {e}")
                value = default() if callable(default) else default
        else:
            value = default(self.element) if callable(default) else default

        setattr(self, attr_name, value)

    def findall(self, path: str) -> List[Element]:
        """Convenience wrapper for element.findall."""
        return self.element.findall(path)

    @staticmethod
    def _get_float(value_str: str) -> float:
        """Robustly converts a string to a float, handling 'auto' values."""
        if value_str is None: return 0.0
        clean_str = value_str.strip().lower()
        # Handle the auto values so they don't break the entire conversion
        if clean_str.startswith('auto'):
            clean_str = clean_str.replace('auto', '').strip()
            if not clean_str: return 0.0
        return float(clean_str)

    @staticmethod
    def _get_bool(value_str: str) -> bool:
        """Converts a string to a boolean."""
        if value_str is None: return False
        return value_str.strip().lower() in ['true', 'yes', '1']

@register_component('subcomponent')
class Subcomponent(XMLComponent):
    _FIELDS = [
        ('length', './/length', XMLComponent._get_float, 0.0),
        ('radius', './/radius', XMLComponent._get_float, 0.0),
        ('position', './/position', XMLComponent._get_float, 0.0),
        ('material', './/material', str, 'Unknown'),
        ('thickness', './/thickness', XMLComponent._get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent._get_float, 0.0),
        ('innerradius', './/innerradius', XMLComponent._get_float, 0.0),
    ]

    def __init__(self, element: Element):
        super().__init__(element)
        self.subcomponents: List[XMLComponent] = [
            component_factory(e) for e in self.findall('.//subcomponents/*')
        ]
