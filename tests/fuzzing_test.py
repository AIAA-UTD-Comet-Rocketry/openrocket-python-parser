from os.path import exists, join, dirname
import pytest
import logging
import random
import string
from typing import Callable, Optional
import xml.etree.ElementTree as ET
from openrocket_parser.core import load_rocket_from_xml, load_rocket_from_xml_safe


@pytest.fixture
def valid_xml_path():
    """Returns the path to the valid.xml file."""
    return join(dirname(__file__), "valid.xml")


def restore_valid_file(xml_path: str) -> None:
    valid_xml = """
<openrocket version="1.0">
    <rocket>
        <name>My Test Rocket</name>
        <subcomponents>
            <stage/>
        </subcomponents>
    </rocket>
</openrocket>
    """
    with open(xml_path, 'w+') as valid_f:
        valid_f.write(valid_xml)


# Mutators

class Mutators:
    @staticmethod
    def xml_syntax(xml_str: str, find: str = '</rocket>', replace: str = '<rocket>', count: int = 1) -> str:
        return xml_str.replace(find, replace, count)

    @staticmethod
    def remove_tag(xml_str: str, tag: str = "<rocket>", closure_tag: Optional[str] = "</rocket>") -> str:
        tmp = xml_str.replace(tag, "")
        if closure_tag is not None:
            tmp = tmp.replace(closure_tag, "")
        return tmp

    @staticmethod
    def add_random_bytes(xml_str: str) -> str:
        pos = random.randint(0, len(xml_str) - 1)
        bytes_to_add = b'\xFF\x00\x01'.decode('utf-8', errors='ignore')
        # Shorthand in python to break the array into 2 parts:
        # Everything before our random position (not including)
        # Everything after our random position (not including).
        # Then return the parts concatenated with the incorrect bytes created above
        return xml_str[:pos] + bytes_to_add + xml_str[pos:]

    @staticmethod
    def empty_file(_: str) -> str:
        """ empty_file returns an empty string. The input is needed to parametrize the tests"""
        return ""

    @staticmethod
    def incomplete_file(xml_str: str) -> str:
        pos = random.randint(1, len(xml_str) - 2)
        # Break the xml into 2 parts so it becomes invalid
        return xml_str[:pos]


# Test cases below
# Parametrized through pytest to avoid repetition
# Collect Mutators to use with the parameters
mutators = [
    Mutators.xml_syntax,
    Mutators.remove_tag,
    Mutators.add_random_bytes,
    Mutators.empty_file,
    Mutators.incomplete_file
]


# Generators
class Generators:
    @staticmethod
    def random_string(length: int) -> str:
        valid_symbols = string.ascii_letters + string.digits + " "
        # Python shorthand for list generation; create a var of len = length
        # from random choices from the list of valid_symbols
        return ''.join(random.choice(valid_symbols) for _ in range(length))

    @staticmethod
    def dangerous_string(length: int = 20) -> str:
        return "!@#$<&\"" + Generators.random_string(length)

    @staticmethod
    def generate_long_string(length: int = 10000) -> str:
        return Generators.random_string(length)

    @staticmethod
    def generate_dangerous_string(length: int = 20) -> str:
        return Generators.dangerous_string(length)

    @staticmethod
    def generate_unicode() -> str:
        return "🚀"  # Never do this in code please, but this is good for testing unicodes

    @staticmethod
    def generate_empty() -> str:
        return ""


generators = [
    Generators.generate_long_string,
    Generators.generate_empty,
    Generators.generate_dangerous_string,
    Generators.generate_unicode
]


# Mutator based tests
@pytest.mark.parametrize("mutator", mutators)
def test_load_safe_fuzzing(mutator: Callable[[str], str], tmp_path, caplog, valid_xml_path):
    """
    Test the loading of the file in safe mode (no exceptions raised)
    :param mutator: The mutating function to be called
    :param tmp_path: The path to the tmp_folder
    :param caplog is a pytest fixture to capture the result of our fuzzing results
    :return:
    """
    invalid_path = f'{tmp_path}/invalid.{mutator.__name__}.xml'
    with open(valid_xml_path, 'r') as valid_xml:
        mutated = mutator(valid_xml.read())

    # Create the invalid file, store, and load in safe mode
    with open(invalid_path, 'w+') as invalid_file:
        invalid_file.write(mutated)
        with caplog.at_level(logging.ERROR):
            result = load_rocket_from_xml_safe(invalid_path)

    assert result is None, f'Safe mode failed for mutator {mutator.__name__}'
    assert len(caplog.records) >= 1, f'Function did not log an error for mutator {mutator.__name__}'


@pytest.mark.parametrize("mutator", mutators)
def test_load_unsafe_fuzzing(mutator: Callable[[str], str], tmp_path, caplog, valid_xml_path):
    """
    Test the loading of the file in safe mode (no exceptions raised)
    :param mutator: The mutating function to be called
    :param tmp_path: The path to the tmp_folder
    :param caplog is a pytest fixture to capture the result of our fuzzing results
    :return:
    """
    invalid_path = f'{tmp_path}/invalid.{mutator.__name__}.xml'
    with open(valid_xml_path, 'r') as valid_xml:
        mutated = mutator(valid_xml.read())

    # Create the invalid file, store, and load in unsafe mode
    with open(invalid_path, 'w+') as invalid_file:
        invalid_file.write(mutated)
        # Validate that all invalid tests raise a ValueError exception
        with pytest.raises(ValueError):
            load_rocket_from_xml(invalid_path)


# End Mutator based tests

# Generator based tests
@pytest.mark.parametrize("generator", generators)
def test_load_generator_fuzzing_safe(generator, tmp_path, caplog):
    """
    Test generators in safe mode
    :param generator: The generator to use for this run
    :param tmp_path: A pytest fixture to store files temporarily
    :param caplog: A pytest fixture to collect results
    """

    new_value = generator()
    rocket_name = f'Fuzzed by {generator.__name__}'
    # generate fake xml data to inject incorrect values
    root = ET.Element('openrocket')
    rocket_element = ET.SubElement(root, 'rocket')
    ET.SubElement(rocket_element, 'designer').text = new_value
    ET.SubElement(rocket_element, 'name').text = rocket_name

    xml_content = ET.tostring(root).decode('utf-8')
    invalid_path = f'{tmp_path}/invalid.generator.xml'

    try:
        with open(invalid_path, 'w+') as invalid_file:
            invalid_file.write(xml_content)
            assert exists(invalid_path)
            with caplog.at_level(logging.INFO):
                rocket = load_rocket_from_xml_safe(invalid_path)
                if rocket is not None:
                    assert rocket.designer == str(new_value)
                    assert rocket.name == str(rocket_name)
    except Exception as e:
        pytest.fail(f'Unhandled exception {e}')
