import xml.etree.ElementTree as ET
import sys
import os

def process_xmi(input_file, output_file):
    # Namespaces found in the XMI files
    namespaces = {
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

    # Register namespaces to preserve prefixes during writing
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {input_file}: {e}")
        sys.exit(1)

    # Step 1: Map Token xmi:id to its begin and end attributes
    token_data = {}
    # Use the 'type' namespace for Token tags
    token_tag = f"{{{namespaces['type']}}}Token"
    xmi_id_attr = f"{{{namespaces['xmi']}}}id"

    for token in root.findall(f".//{token_tag}"):
        tid = token.get(xmi_id_attr)
        begin = token.get('begin')
        end = token.get('end')
        if tid:
            token_data[tid] = {'begin': begin, 'end': end}

    # Step 2: Update UDependency tags in the 'syntax' namespace
    dep_tag = f"{{{namespaces['syntax']}}}UDependency"
    updated_count = 0

    for dep in root.findall(f".//{dep_tag}"):
        gov_id = dep.get('Governor')
        dep_id = dep.get('Dependent')

        # Add "begin" attribute from Governor's Token
        if gov_id in token_data:
            begin_val = token_data[gov_id]['begin']
            if begin_val is not None:
                dep.set('begin', begin_val)

        # Add "end" attribute from Dependent's Token
        if dep_id in token_data:
            end_val = token_data[dep_id]['end']
            if end_val is not None:
                dep.set('end', end_val)
        
        updated_count += 1

    # Step 3: Write the updated XML to the output file
    try:
        tree.write(output_file, encoding='UTF-8', xml_declaration=True)
        print(f"Successfully processed {updated_count} UDependency tags.")
        print(f"Output saved to: {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python automate_udependency.py <input_file> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    process_xmi(input_path, output_path)
