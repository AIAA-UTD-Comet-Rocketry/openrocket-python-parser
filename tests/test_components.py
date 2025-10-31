import pytest
from xml.etree import ElementTree
from openrocket_parser.components.components import component_factory, Bulkhead, ShockCord, TubeCoupler, Parachute, RailButton, MassComponent, InnerTube, TrapezoidFinSet, CenteringRing

def test_bulkhead_parsing():
    xml_string = """
    <bulkhead>
        <name>Test Bulkhead</name>
        <id>123</id>
        <instancecount>2</instancecount>
        <instanceseparation>0.1</instanceseparation>
        <axialoffset>0.2</axialoffset>
        <position>0.3</position>
        <overridemass>0.5</overridemass>
        <overridesubcomponentsmass>true</overridesubcomponentsmass>
        <material>Aluminum</material>
        <length>0.01</length>
        <radialposition>0.05</radialposition>
        <radialdirection>90.0</radialdirection>
        <outerradius>0.03</outerradius>
    </bulkhead>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, Bulkhead)
    assert component.name == "Test Bulkhead"
    assert component.id == "123"
    assert component.instancecount == 2
    assert component.instanceseparation == 0.1
    assert component.axialoffset == 0.2
    assert component.position == 0.3
    assert component.overridemass == 0.5
    assert component.overridesubcomponentsmass is True
    assert component.material == "Aluminum"
    assert component.length == 0.01
    assert component.radialposition == 0.05
    assert component.radialdirection == 90.0
    assert component.outerradius == 0.03

def test_shockcord_parsing():
    xml_string = """
    <shockcord>
        <name>Test Shock Cord</name>
        <id>124</id>
        <axialoffset>0.1</axialoffset>
        <position>0.2</position>
        <overridemass>0.01</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <packedlength>0.02</packedlength>
        <packedradius>0.005</packedradius>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <cordlength>1.5</cordlength>
        <material>Nylon</material>
    </shockcord>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, ShockCord)
    assert component.name == "Test Shock Cord"
    assert component.id == "124"
    assert component.axialoffset == 0.1
    assert component.position == 0.2
    assert component.overridemass == 0.01
    assert component.overridesubcomponentsmass is False
    assert component.packedlength == 0.02
    assert component.packedradius == 0.005
    assert component.cordlength == 1.5
    assert component.material == "Nylon"

def test_tubecoupler_parsing():
    xml_string = """
    <tubecoupler>
        <name>Test Tube Coupler</name>
        <id>125</id>
        <axialoffset>0.05</axialoffset>
        <position>0.1</position>
        <overridemass>0.02</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <material>Cardboard</material>
        <length>0.1</length>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <outerradius>0.03</outerradius>
        <thickness>0.001</thickness>
    </tubecoupler>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, TubeCoupler)
    assert component.name == "Test Tube Coupler"
    assert component.id == "125"
    assert component.axialoffset == 0.05
    assert component.position == 0.1
    assert component.overridemass == 0.02
    assert component.overridesubcomponentsmass is False
    assert component.material == "Cardboard"
    assert component.length == 0.1
    assert component.outerradius == 0.03
    assert component.thickness == 0.001

def test_parachute_parsing():
    xml_string = """
    <parachute>
        <name>Test Parachute</name>
        <id>126</id>
        <axialoffset>0.5</axialoffset>
        <position>0.6</position>
        <overridemass>0.05</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <packedlength>0.03</packedlength>
        <packedradius>0.015</packedradius>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <cd>0.8</cd>
        <material>Ripstop Nylon</material>
        <deployevent>ejection</deployevent>
        <deployaltitude>200.0</deployaltitude>
        <deploydelay>1.0</deploydelay>
        <diameter>1.0</diameter>
        <linecount>8</linecount>
        <linelength>0.5</linelength>
        <linematerial>Kevlar</linematerial>
    </parachute>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, Parachute)
    assert component.name == "Test Parachute"
    assert component.id == "126"
    assert component.axialoffset == 0.5
    assert component.position == 0.6
    assert component.overridemass == 0.05
    assert component.overridesubcomponentsmass is False
    assert component.packedlength == 0.03
    assert component.packedradius == 0.015
    assert component.cd == 0.8
    assert component.material == "Ripstop Nylon"
    assert component.deployevent == "ejection"
    assert component.deployaltitude == 200.0
    assert component.deploydelay == 1.0
    assert component.diameter == 1.0
    assert component.linecount == 8
    assert component.linelength == 0.5
    assert component.linematerial == "Kevlar"

def test_railbutton_parsing():
    xml_string = """
    <railbutton>
        <name>Test Rail Button</name>
        <id>127</id>
        <instancecount>3</instancecount>
        <instanceseparation>0.2</instanceseparation>
        <angleoffset>45.0</angleoffset>
        <axialoffset>0.1</axialoffset>
        <position>0.2</position>
        <overridemass>0.001</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <finish>glossy</finish>
        <material>Plastic</material>
        <outerdiameter>0.01</outerdiameter>
        <innerdiameter>0.005</innerdiameter>
        <height>0.008</height>
        <baseheight>0.002</baseheight>
        <flangeheight>0.001</flangeheight>
        <screwheight>0.003</screwheight>
    </railbutton>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, RailButton)
    assert component.name == "Test Rail Button"
    assert component.id == "127"
    assert component.instancecount == 3
    assert component.instanceseparation == 0.2
    assert component.angleoffset == 45.0
    assert component.axialoffset == 0.1
    assert component.position == 0.2
    assert component.overridemass == 0.001
    assert component.overridesubcomponentsmass is False
    assert component.finish == "glossy"
    assert component.material == "Plastic"
    assert component.outerdiameter == 0.01
    assert component.innerdiameter == 0.005
    assert component.height == 0.008
    assert component.baseheight == 0.002
    assert component.flangeheight == 0.001
    assert component.screwheight == 0.003

def test_masscomponent_parsing():
    xml_string = """
    <masscomponent>
        <name>Test Mass Component</name>
        <id>128</id>
        <axialoffset>0.1</axialoffset>
        <position>0.2</position>
        <overridemass>0.1</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <packedlength>0.05</packedlength>
        <packedradius>0.02</packedradius>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <mass>0.2</mass>
        <masscomponenttype>lead</masscomponenttype>
    </masscomponent>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, MassComponent)
    assert component.name == "Test Mass Component"
    assert component.id == "128"
    assert component.axialoffset == 0.1
    assert component.position == 0.2
    assert component.overridemass == 0.1
    assert component.overridesubcomponentsmass is False
    assert component.packedlength == 0.05
    assert component.packedradius == 0.02
    assert component.mass == 0.2
    assert component.masscomponenttype == "lead"

def test_innertube_parsing():
    xml_string = """
    <innertube>
        <name>Test Inner Tube</name>
        <id>129</id>
        <axialoffset>0.01</axialoffset>
        <position>0.02</position>
        <overridemass>0.005</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <material>Paper</material>
        <length>0.15</length>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <outerradius>0.01</outerradius>
        <thickness>0.0005</thickness>
        <clusterconfiguration>dual</clusterconfiguration>
        <clusterscale>0.5</clusterscale>
        <clusterrotation>90.0</clusterrotation>
    </innertube>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, InnerTube)
    assert component.name == "Test Inner Tube"
    assert component.id == "129"
    assert component.axialoffset == 0.01
    assert component.position == 0.02
    assert component.overridemass == 0.005
    assert component.overridesubcomponentsmass is False
    assert component.material == "Paper"
    assert component.length == 0.15
    assert component.outerradius == 0.01
    assert component.thickness == 0.0005
    assert component.clusterconfiguration == "dual"
    assert component.clusterscale == 0.5
    assert component.clusterrotation == 90.0

def test_trapezoidfinset_parsing():
    xml_string = """
    <trapezoidfinset>
        <name>Test Trapezoidal Fin Set</name>
        <id>130</id>
        <instancecount>4</instancecount>
        <fincount>3</fincount>
        <radiusoffset>0.001</radiusoffset>
        <angleoffset>30.0</angleoffset>
        <rotation>10.0</rotation>
        <axialoffset>0.05</axialoffset>
        <position>0.06</position>
        <overridemass>0.01</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <finish>matte</finish>
        <material>Fiberglass</material>
        <thickness>0.002</thickness>
        <crosssection>trapezoid</crosssection>
        <cant>5.0</cant>
        <tabheight>0.01</tabheight>
        <tablength>0.05</tablength>
        <tabposition>0.02</tabposition>
        <filletradius>0.001</filletradius>
        <filletmaterial>Epoxy</filletmaterial>
        <rootchord>0.1</rootchord>
        <tipchord>0.05</tipchord>
        <sweeplength>0.03</sweeplength>
        <height>0.04</height>
    </trapezoidfinset>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, TrapezoidFinSet)
    assert component.name == "Test Trapezoidal Fin Set"
    assert component.id == "130"
    assert component.instancecount == 4
    assert component.fincount == 3
    assert component.radiusoffset == 0.001
    assert component.angleoffset == 30.0
    assert component.rotation == 10.0
    assert component.axialoffset == 0.05
    assert component.position == 0.06
    assert component.overridemass == 0.01
    assert component.overridesubcomponentsmass is False
    assert component.finish == "matte"
    assert component.material == "Fiberglass"
    assert component.thickness == 0.002
    assert component.crosssection == "trapezoid"
    assert component.cant == 5.0
    assert component.tabheight == 0.01
    assert component.tablength == 0.05
    assert component.tabposition == 0.02
    assert component.filletradius == 0.001
    assert component.filletmaterial == "Epoxy"
    assert component.rootchord == 0.1
    assert component.tipchord == 0.05
    assert component.sweeplength == 0.03
    assert component.height == 0.04

def test_centeringring_parsing():
    xml_string = """
    <centeringring>
        <name>Test Centering Ring</name>
        <id>131</id>
        <instancecount>2</instancecount>
        <instanceseparation>0.01</instanceseparation>
        <axialoffset>0.03</axialoffset>
        <position>0.04</position>
        <overridemass>0.002</overridemass>
        <overridesubcomponentsmass>false</overridesubcomponentsmass>
        <material>Plywood</material>
        <length>0.005</length>
        <radialposition>0.0</radialposition>
        <radialdirection>0.0</radialdirection>
        <outerradius>0.02</outerradius>
        <innerradius>0.01</innerradius>
    </centeringring>
    """
    element = ElementTree.fromstring(xml_string)
    component = component_factory(element)

    assert isinstance(component, CenteringRing)
    assert component.name == "Test Centering Ring"
    assert component.id == "131"
    assert component.instancecount == 2
    assert component.instanceseparation == 0.01
    assert component.axialoffset == 0.03
    assert component.position == 0.04
    assert component.overridemass == 0.002
    assert component.overridesubcomponentsmass is False
    assert component.material == "Plywood"
    assert component.length == 0.005
    assert component.outerradius == 0.02
    assert component.innerradius == 0.01
