# Contributing to OpenRocketParser

We welcome contributions to the OpenRocketParser library! This guide will walk you through the process of adding new components to the library.

## Adding a New Component

To add a new component, you'll need to:

1.  **Identify the Component's XML Structure:**
    *   Open an `.ork` file (OpenRocket file) that contains the component you want to add.
    *   Locate the XML tag for your component within the `<subcomponents>` section. For example, if you're adding a `Bulkhead`, you'll look for `<bulkhead>`.
    *   Examine the child tags within your component's XML block. These child tags represent the properties of the component (e.g., `<name>`, `<length>`, `<material>`).

2.  **Create a New Python Class:**
    *   Open `src/openrocket_parser/components/components.py`.
    *   Create a new Python class for your component. This class should inherit from `Subcomponent`.
    *   Decorate your class with `@register_component('your_component_tag')`, replacing `'your_component_tag'` with the actual XML tag name (e.g., `'bulkhead'`).

3.  **Define the `_FIELDS` Array:**
    *   Inside your new class, define a `_FIELDS` class attribute. This is a list of tuples, where each tuple describes a property to be parsed from the XML.
    *   Each tuple should follow this format: `('attribute_name', 'xml_path', type_conversion_function, default_value)`
        *   `attribute_name`: The name of the attribute in your Python class (e.g., `'length'`).
        *   `xml_path`: The XPath-like path to the XML tag containing the value (e.g., `'.//length'`).
        *   `type_conversion_function`: A function to convert the XML string value to the desired Python type (e.g., `str`, `int`, `XMLComponent.get_float`, `XMLComponent.get_bool`).
        *   `default_value`: A default value to use if the XML tag is not found or if conversion fails.

    **Example for `Bulkhead`:**

    ```python
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
    ```

4.  **Add Unit Tests:**
    *   Create or update `tests/test_{your_component_name}.py`.
    *   Add a new test function for your component (e.g., `test_your_component_parsing`).
    *   Inside the test function:
        *   Create a sample XML string that represents your component or load an existing xml.
        *   Use `ElementTree.fromstring()` to parse the XML string into an `Element`.
        *   Call `component_factory()` with the `Element` to create an instance of your component. (_Note_: The library uses python's decorators (wrappers) to auto-call registered components, but in tests we need to call it manually)
        *   Use `assert` statements to verify that the attributes of your component instance match the values in your sample XML.

5. **Run Tests:**
    * Execute the tests to ensure your new component is correctly parsed and doesn't introduce any regressions.
    * ```bash
      pytest
      ```
      _Note_ If you have installed the library with pip as per the instructions - your tests will fail since the tested version will not include your new tests. If this happens follow these instructions:
    ```bash
    pip uninstall openrocket-python-parser
    pip install -e .  # the -e indicates to pip to install the current code (.) in edit mode
    pytest  # Now pytest will use your code instead of the pip installed library
    ```

6.  **Submit a Pull Request:**
    *   Commit your changes and submit a pull request to the project.
