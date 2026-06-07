import unittest
import xml.etree.ElementTree as ET
import os
import tempfile
from src.crop_example.automate_udependency import process_xmi

class TestAutomateUDependency(unittest.TestCase):
    def setUp(self):
        self.namespaces = {
            'xmi': 'http://www.omg.org/XMI',
            'cas': 'http:///uima/cas.ecore',
            'dakoda': 'http:///org/dakoda.ecore',
            'type': 'http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore',
            'pos': 'http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore',
            'UniversalDependencies': 'http:///custom/UniversalDependencies.ecore',
            'syntaxdot': 'http:///custom/syntaxdot.ecore',
            'syntax': 'http:///org/dakoda/syntax.ecore',
            'type0': 'http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore'
        }
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def test_basic_transformation(self):
        # Create a minimal XMI content
        xmi_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmlns:xmi="{self.namespaces['xmi']}" xmlns:type="{self.namespaces['type']}" xmlns:syntax="{self.namespaces['syntax']}" xmi:version="2.0">
    <type:Token xmi:id="1" begin="10" end="20"/>
    <type:Token xmi:id="2" begin="30" end="40"/>
    <syntax:UDependency Governor="1" Dependent="2"/>
</xmi:XMI>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xmi', delete=False) as input_file:
            input_file.write(xmi_content)
            input_path = input_file.name

        output_path = input_path + ".out.xmi"

        try:
            process_xmi(input_path, output_path)

            # Verify the output
            tree = ET.parse(output_path)
            root = tree.getroot()
            
            dep_tag = f"{{{self.namespaces['syntax']}}}UDependency"
            dep = root.find(f".//{dep_tag}")
            
            self.assertIsNotNone(dep)
            self.assertEqual(dep.get('begin'), '10')
            self.assertEqual(dep.get('end'), '40')
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_missing_token(self):
        xmi_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmlns:xmi="{self.namespaces['xmi']}" xmlns:type="{self.namespaces['type']}" xmlns:syntax="{self.namespaces['syntax']}" xmi:version="2.0">
    <type:Token xmi:id="1" begin="10" end="20"/>
    <syntax:UDependency Governor="1" Dependent="99"/>
</xmi:XMI>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xmi', delete=False) as input_file:
            input_file.write(xmi_content)
            input_path = input_file.name

        output_path = input_path + ".out.xmi"

        try:
            process_xmi(input_path, output_path)

            tree = ET.parse(output_path)
            root = tree.getroot()
            dep_tag = f"{{{self.namespaces['syntax']}}}UDependency"
            dep = root.find(f".//{dep_tag}")
            
            self.assertEqual(dep.get('begin'), '10')
            self.assertIsNone(dep.get('end')) # Dependent 99 doesn't exist
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_multiple_dependencies(self):
        xmi_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmlns:xmi="{self.namespaces['xmi']}" xmlns:type="{self.namespaces['type']}" xmlns:syntax="{self.namespaces['syntax']}" xmi:version="2.0">
    <type:Token xmi:id="1" begin="0" end="5"/>
    <type:Token xmi:id="2" begin="6" end="10"/>
    <type:Token xmi:id="3" begin="11" end="15"/>
    <syntax:UDependency Governor="1" Dependent="2" xmi:id="100"/>
    <syntax:UDependency Governor="2" Dependent="3" xmi:id="101"/>
</xmi:XMI>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xmi', delete=False) as input_file:
            input_file.write(xmi_content)
            input_path = input_file.name

        output_path = input_path + ".out.xmi"

        try:
            process_xmi(input_path, output_path)

            tree = ET.parse(output_path)
            root = tree.getroot()
            dep_tag = f"{{{self.namespaces['syntax']}}}UDependency"
            deps = root.findall(f".//{dep_tag}")
            
            self.assertEqual(len(deps), 2)
            
            dep100 = next(d for d in deps if d.get(f"{{{self.namespaces['xmi']}}}id") == "100")
            self.assertEqual(dep100.get('begin'), '0')
            self.assertEqual(dep100.get('end'), '10')

            dep101 = next(d for d in deps if d.get(f"{{{self.namespaces['xmi']}}}id") == "101")
            self.assertEqual(dep101.get('begin'), '6')
            self.assertEqual(dep101.get('end'), '15')
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_namespace_preservation(self):
        xmi_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmlns:xmi="{self.namespaces['xmi']}" xmlns:cas="{self.namespaces['cas']}" xmlns:type="{self.namespaces['type']}" xmlns:syntax="{self.namespaces['syntax']}" xmi:version="2.0">
    <cas:NULL xmi:id="0"/>
    <type:Token xmi:id="1" begin="0" end="5"/>
    <syntax:UDependency Governor="1" Dependent="1"/>
</xmi:XMI>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xmi', delete=False) as input_file:
            input_file.write(xmi_content)
            input_path = input_file.name

        output_path = input_path + ".out.xmi"

        try:
            process_xmi(input_path, output_path)

            with open(output_path, 'r') as f:
                content = f.read()
                # Check for namespace prefixes in the output
                self.assertIn('xmlns:xmi', content)
                self.assertIn('xmlns:cas', content)
                self.assertIn('xmlns:type', content)
                self.assertIn('xmlns:syntax', content)
                self.assertIn('<cas:NULL', content)
                self.assertIn('<type:Token', content)
                self.assertIn('<syntax:UDependency', content)
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
