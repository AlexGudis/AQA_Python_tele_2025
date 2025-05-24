import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_xml(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    classes = {}
    agr = []

    for el in root:
        if el.tag == 'Class':
            class_name = el.attrib['name']
            is_root = el.attrib.get('isRoot', 'false').lower() == 'true'
            documentation = el.attrib.get('documentation', '')
            
            attributes = []
            for attr in el.findall('Attribute'):
                attributes.append({'name': attr.attrib['name'], 'type': attr.attrib['type']})
            
            classes[class_name] = {'name': class_name, 'isRoot': is_root, 'documentation': documentation,
                'attributes': attributes,
                'children': []
            }
        
        elif el.tag == 'Aggregation':
            agr.append({'source': el.attrib['source'], 'target': el.attrib['target'],
                'sourceMultiplicity': el.attrib['sourceMultiplicity'],
                'targetMultiplicity': el.attrib['targetMultiplicity']
            })

        else:
            raise NameError

    return classes, agr


def build_hierarchy(classes, aggregations):
    parent_map = {}
    multiplicity_map = defaultdict(dict)
    
    for agg in aggregations:
        source = agg['source']
        target = agg['target']
        parent_map[source] = target
        multiplicity_map[target][source] = agg['sourceMultiplicity']
    
    for class_name in classes:
        classes[class_name]['children'] = []
    
    for source, target in parent_map.items():
        classes[target]['children'].append(source)
    
    return multiplicity_map



def main():
    input_file = 'impulse_test_input.xml'
    
    try:
        classes, aggregations = parse_xml(input_file)
    except NameError:
        print('Обнаружено неизвестное поле во входном файле.')
        exit()

    multiplicity_map = build_hierarchy(classes, aggregations)

    

    print(classes)

    print(aggregations)

if __name__ == '__main__':
    main()