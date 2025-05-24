import xml.etree.ElementTree as ET
from collections import defaultdict
import json

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


def generate_config_xml(classes, root_class_name, indent=4):
    def build_xml(class_name, level=0):
        class_info = classes[class_name]
        indent_str = ' ' * (level * indent)
        xml_lines = []
        
        xml_lines.append(f"{indent_str}<{class_name}>")
        
        for attr in class_info['attributes']:
            xml_lines.append(f"{indent_str}{' ' * indent}<{attr['name']}>{attr['type']}</{attr['name']}>")
        
        for child in sorted(class_info['children']):
            xml_lines.extend(build_xml(child, level + 1))
        
        xml_lines.append(f"{indent_str}</{class_name}>")
        
        return xml_lines
    
    root_class = next((c for c in classes.values() if c['isRoot']), None)
    if not root_class:
        root_class = classes.get(root_class_name)
    
    if not root_class:
        raise ValueError("Не найден корневой класс")
    
    xml_lines = build_xml(root_class['name'])
    return '\n'.join(xml_lines)


def generate_meta_json(classes, multiplicity_map):
    meta = []
    
    for class_name in classes:
        class_info = classes[class_name]
        parameters = []
        
        for attr in class_info['attributes']:
            parameters.append({
                'name': attr['name'],
                'type': attr['type']
            })
        
        for child in class_info['children']:
            param = {
                'name': child,
                'type': 'class'
            }
            parameters.append(param)
        
        class_entry = {
            'class': class_name,
            'documentation': class_info['documentation'],
            'isRoot': class_info['isRoot'],
            'parameters': parameters
        }
        

        # у класса рут нет полей max и min
        if not class_info['isRoot']:
            min_val = '1'
            max_val = '1'
            for parent in classes:
                if class_name in classes[parent]['children']:
                    multiplicity = multiplicity_map[parent][class_name]
                    if '..' in multiplicity:
                        min_val, max_val = multiplicity.split('..')
                    else:
                        min_val = max_val = multiplicity
                    break
            
            class_entry['min'] = min_val
            class_entry['max'] = max_val
        
        meta.append(class_entry)
    
    return json.dumps(meta, indent=4)



def main():
    input_file = 'impulse_test_input.xml'
    
    try:
        classes, aggregations = parse_xml(input_file)
    except NameError:
        print('Обнаружено неизвестное поле во входном файле.')
        exit()

    multiplicity_map = build_hierarchy(classes, aggregations)

    #print(classes)
    #print(aggregations)

    root_class = next((c['name'] for c in classes.values() if c['isRoot']), None)
    if not root_class:
        root_class = 'BTS'
    
    config_xml = generate_config_xml(classes, root_class, multiplicity_map)
    with open('./out/config.xml', 'w') as f:
        f.write(config_xml)

    meta_json = generate_meta_json(classes, multiplicity_map)
    with open("./out/meta.json", 'w') as f:
        f.write(meta_json)

if __name__ == '__main__':
    main()