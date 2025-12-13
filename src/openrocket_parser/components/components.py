"""
Components collects a
"""

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
    def get_float(value_str: str) -> float:
        """Robustly converts a string to a float, handling 'auto' values."""
        if value_str is None:
            return 0.0
        clean_str = value_str.strip().lower()
        # Handle the auto values so they don't break the entire conversion
        if clean_str.startswith('auto'):
            clean_str = clean_str.replace('auto', '').strip()
            if not clean_str:
                return 0.0
        return float(clean_str)

    @staticmethod
    def get_bool(value_str: str) -> bool:
        """Converts a string to a boolean."""
        if value_str is None:
            return False
        return value_str.strip().lower() in ['true', 'yes', '1']


@register_component('subcomponent')
class Subcomponent(XMLComponent):
    """"
    Subcomponents enables shared functionality for all components - such as length, radius, material, etc
    """
    _FIELDS = [
        ('length', './/length', XMLComponent.get_float, 0.0),
        ('radius', './/radius', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('material', './/material', str, 'Unknown'),
        ('thickness', './/thickness', XMLComponent.get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent.get_float, 0.0),
        ('innerradius', './/innerradius', XMLComponent.get_float, 0.0),
    ]

    def __init__(self, element: Element):
        super().__init__(element)
        self.subcomponents: List[XMLComponent] = [
            component_factory(e) for e in self.findall('.//subcomponents/*')
        ]


@register_component('bulkhead')
class Bulkhead(Subcomponent):
    _FIELDS = [
        ('instancecount', './/instancecount', int, 1),
        ('instanceseparation', './/instanceseparation', XMLComponent.get_float, 0.0),
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './/material', str, 'Unknown'),
        ('length', './/length', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent.get_float, 0.0),
    ]


@register_component('shockcord')
class ShockCord(Subcomponent):
    _FIELDS = [
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './/packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './/packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('cordlength', './/cordlength', XMLComponent.get_float, 0.0),
        ('material', './/material', str, 'Unknown'),
    ]


@register_component('tubecoupler')
class TubeCoupler(Subcomponent):
    _FIELDS = [
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './/material', str, 'Unknown'),
        ('length', './/length', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent.get_float, 0.0),
        ('thickness', './/thickness', XMLComponent.get_float, 0.0),
    ]


@register_component('parachute')
class Parachute(Subcomponent):
    _FIELDS = [
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './/packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './/packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('cd', './/cd', XMLComponent.get_float, 0.0),
        ('material', './/material', str, 'Unknown'),
        ('deployevent', './/deployevent', str, 'ejection'),
        ('deployaltitude', './/deployaltitude', XMLComponent.get_float, 0.0),
        ('deploydelay', './/deploydelay', XMLComponent.get_float, 0.0),
        ('diameter', './/diameter', XMLComponent.get_float, 0.0),
        ('linecount', './/linecount', int, 0),
        ('linelength', './/linelength', XMLComponent.get_float, 0.0),
        ('linematerial', './/linematerial', str, 'Unknown'),
    ]


@register_component('railbutton')
class RailButton(Subcomponent):
    _FIELDS = [
        ('instancecount', './/instancecount', int, 1),
        ('instanceseparation', './/instanceseparation', XMLComponent.get_float, 0.0),
        ('angleoffset', './/angleoffset', XMLComponent.get_float, 0.0),
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('finish', './/finish', str, 'smooth'),
        ('material', './/material', str, 'Unknown'),
        ('outerdiameter', './/outerdiameter', XMLComponent.get_float, 0.0),
        ('innerdiameter', './/innerdiameter', XMLComponent.get_float, 0.0),
        ('height', './/height', XMLComponent.get_float, 0.0),
        ('baseheight', './/baseheight', XMLComponent.get_float, 0.0),
        ('flangeheight', './/flangeheight', XMLComponent.get_float, 0.0),
        ('screwheight', './/screwheight', XMLComponent.get_float, 0.0),
    ]


@register_component('masscomponent')
class MassComponent(Subcomponent):
    _FIELDS = [
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './/packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './/packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('mass', './/mass', XMLComponent.get_float, 0.0),
        ('masscomponenttype', './/masscomponenttype', str, 'masscomponent'),
    ]


@register_component('innertube')
class InnerTube(Subcomponent):
    _FIELDS = [
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './/material', str, 'Unknown'),
        ('length', './/length', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent.get_float, 0.0),
        ('thickness', './/thickness', XMLComponent.get_float, 0.0),
        ('clusterconfiguration', './/clusterconfiguration', str, 'single'),
        ('clusterscale', './/clusterscale', XMLComponent.get_float, 1.0),
        ('clusterrotation', './/clusterrotation', XMLComponent.get_float, 0.0),
    ]


@register_component('trapezoidfinset')
class TrapezoidFinSet(Subcomponent):
    _FIELDS = [
        ('instancecount', './/instancecount', int, 1),
        ('fincount', './/fincount', int, 0),
        ('radiusoffset', './/radiusoffset', XMLComponent.get_float, 0.0),
        ('angleoffset', './/angleoffset', XMLComponent.get_float, 0.0),
        ('rotation', './/rotation', XMLComponent.get_float, 0.0),
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('finish', './/finish', str, 'smooth'),
        ('material', './/material', str, 'Unknown'),
        ('thickness', './/thickness', XMLComponent.get_float, 0.0),
        ('crosssection', './/crosssection', str, 'square'),
        ('cant', './/cant', XMLComponent.get_float, 0.0),
        ('tabheight', './/tabheight', XMLComponent.get_float, 0.0),
        ('tablength', './/tablength', XMLComponent.get_float, 0.0),
        ('tabposition', './/tabposition', XMLComponent.get_float, 0.0),
        ('filletradius', './/filletradius', XMLComponent.get_float, 0.0),
        ('filletmaterial', './/filletmaterial', str, 'Unknown'),
        ('rootchord', './/rootchord', XMLComponent.get_float, 0.0),
        ('tipchord', './/tipchord', XMLComponent.get_float, 0.0),
        ('sweeplength', './/sweeplength', XMLComponent.get_float, 0.0),
        ('height', './/height', XMLComponent.get_float, 0.0),
    ]


@register_component('centeringring')
class CenteringRing(Subcomponent):
    _FIELDS = [
        ('instancecount', './/instancecount', int, 1),
        ('instanceseparation', './/instanceseparation', XMLComponent.get_float, 0.0),
        ('axialoffset', './/axialoffset', XMLComponent.get_float, 0.0),
        ('position', './/position', XMLComponent.get_float, 0.0),
        ('overridemass', './/overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './/overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './/material', str, 'Unknown'),
        ('length', './/length', XMLComponent.get_float, 0.0),
        ('radialposition', './/radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './/radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './/outerradius', XMLComponent.get_float, 0.0),
        ('innerradius', './/innerradius', XMLComponent.get_float, 0.0),
    ]
