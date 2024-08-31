import os
import json
import re
import shutil
import argparse
import generate_docs_json

# Configuration files
editors = [
    "word",
    "cell",
    "slide",
    "forms"
]

missing_examples = []

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_markdown_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(content)

def remove_js_comments(text):
    # Remove single-line comments, leaving text after //
    text = re.sub(r'^\s*//\s?', '', text, flags=re.MULTILINE)
    # Remove multi-line comments, leaving text after /*
    text = re.sub(r'/\*\s*|\s*\*/', '', text, flags=re.DOTALL)
    return text.strip()

def correct_description(string):
    if string is None:
        return 'No description provided.'
    
    # Replace opening <b> tag with **
    string = re.sub(r'<b>', '**', string)
    # Replace closing </b> tag with **
    string = re.sub(r'</b>', '**', string)
    # Note
    return re.sub(r'<note>(.*?)</note>', r'💡 \1', string, flags=re.DOTALL)

def correct_default_value(value, enumerations, classes):
    if value is None:
        return ''
    
    if value == True:
        value = "true"
    elif value == False:
        value = "false"
    else:
        value = str(value)
    
    return generate_data_types_markdown([value], enumerations, classes)

def remove_line_breaks(string):
    return re.sub(r'[\r\n]', ' ', string)

def generate_data_types_markdown(types, enumerations, classes, root='../../'):
    param_types_md = ' &#124; '.join(types)

    for enum in enumerations:
        if enum['name'] in types:
            param_types_md = param_types_md.replace(enum['name'], f"[{enum['name']}]({root}Enumeration/{enum['name']}.md)")
    for cls in classes:
        if cls in types:
            param_types_md = param_types_md.replace(cls, f"[{cls}]({root}{cls}/{cls}.md)")

    def replace_with_links(match):
        element = match.group(1).strip()
        base_type = element.split('.')[0]  # Take only the first part before the dot, if any
        if any(enum['name'] == base_type for enum in enumerations):
            return f"<[{element}]({root}Enumeration/{base_type}.md)>"
        elif base_type in classes:
            return f"<[{element}]({root}{base_type}/{base_type}.md)>"
        return f"&lt;{element}&gt;"
    
    return re.sub(r'<([^<>]+)>', replace_with_links, param_types_md)

def generate_class_markdown(class_name, methods, properties, enumerations, classes):
    content = f"# {class_name}\n\nRepresents the {class_name} class.\n\n"
    
    content += generate_properties_markdown(properties, enumerations, classes, '../')

    content += "## Methods\n\n"
    for method in methods:
        method_name = method['name']
        content += f"- [{method_name}](./Methods/{method_name}.md)\n"
    return content

def generate_method_markdown(method, enumerations, classes):
    method_name = method['name']
    description = method.get('description', 'No description provided.')
    description = correct_description(description)
    params = method.get('params', [])
    returns = method.get('returns', [])
    example = method.get('example', '')
    memberof = method.get('memberof', '')

    content = f"# {method_name}\n\n{description}\n\n"
    
    # Syntax section
    param_list = ', '.join([param['name'] for param in params]) if params else ''
    content += f"## Syntax\n\nexpression.{method_name}({param_list});\n\n"
    if memberof:
        content += f"`expression` - A variable that represents a [{memberof}](../{memberof}.md) class.\n\n"

    content += "## Parameters\n\n"

    if params:
        content += "| **Name** | **Required/Optional** | **Data type** | **Default** | **Description** |\n"
        content += "| ------------- | ------------- | ------------- | ------------- | ------------- |\n"
        for param in params:
            param_name = param.get('name', 'Unnamed')
            param_types = param.get('type', {}).get('names', []) if param.get('type') else []
            param_types_md = generate_data_types_markdown(param_types, enumerations, classes)
            param_desc = remove_line_breaks(correct_description(param.get('description', 'No description provided.')))
            param_required = "Required" if not param.get('optional') else "Optional"
            param_default = correct_default_value(param.get('defaultvalue', ''), enumerations, classes)

            content += f"| {param_name} | {param_required} | {param_types_md} | {param_default} | {param_desc} |\n"
    else:
        content += "This method doesn't have any parameters.\n"

    content += "\n## Returns\n\n"
    if returns:
        return_type = ', '.join(returns[0].get('type', {}).get('names', [])) if returns[0].get('type') else 'Unknown'
        
        # Check for enumerations and classes in return type and add links if they exist
        return_type_md = generate_data_types_markdown([return_type], enumerations, classes)
        content += return_type_md
    else:
        content += "This method doesn't return any data."
    
    if example:
        # Separate comment and code, and remove comment symbols
        comment, code = example.split('```js', 1)
        comment = remove_js_comments(comment)
        content += f"\n\n## Example\n\n{comment}\n\n```javascript\n{code.strip()}\n"

    return content

def generate_properties_markdown(properties, enumerations, classes, root='../../'):
    if (properties is None):
        return ''
    
    content = "## Properties\n\n"
    content += "| Name | Type | Description |\n"
    content += "| ---- | ---- | ----------- |\n"
    for prop in properties:
        prop_name = prop['name']
        prop_description = prop.get('description', 'No description provided.')
        prop_description = remove_line_breaks(correct_description(prop_description))
        param_types_md = generate_data_types_markdown(prop['type']['names'], enumerations, classes, root)
        content += f"| {prop_name} | {param_types_md} | {prop_description} |\n"
    content += "\n"

    return content
        

def generate_enumeration_markdown(enumeration, enumerations, classes):
    enum_name = enumeration['name']
    description = enumeration.get('description', 'No description provided.')
    description = correct_description(description)
    example = enumeration.get('example', '')

    content = f"# {enum_name}\n\n{description}\n\n"
    
    if 'TypeUnion' == enumeration['type']['parsedType']['type']:
        content += "## Type\n\nEnumeration\n\n"
        content += "## Values\n\n"
        elements = enumeration['type']['parsedType']['elements']
        for element in elements:
            element_name = element['name'] if element['type'] != 'NullLiteral' else 'null'
            # Check if element is in enumerations or classes before adding link
            if any(enum['name'] == element_name for enum in enumerations):
                content += f"- [{element_name}](../../Enumeration/{element_name}.md)\n"
            elif element_name in classes:
                content += f"- [{element_name}](../../{element_name}/{element_name}.md)\n"
            else:
                content += f"- {element_name}\n"
    elif enumeration['properties'] is not None:
        content += "## Type\n\nObject\n\n"
        content += generate_properties_markdown(enumeration['properties'], enumerations, classes)
    else:
        content += "## Type\n\n"
        types = enumeration['type']['names']
        for t in types:
            t = generate_data_types_markdown([t], enumerations, classes)
            content += t + "\n\n"

    if example:
        # Separate comment and code, and remove comment symbols
        comment, code = example.split('```js', 1)
        comment = remove_js_comments(comment)
        content += f"\n\n## Example\n\n{comment}\n\n```javascript\n{code.strip()}\n"

    return content

def process_doclets(data, output_dir, editor_name):
    classes = {}
    classes_props = {}
    enumerations = []
    editor_dir =  os.path.join(output_dir, editor_name)

    for doclet in data:
        if doclet['kind'] == 'class':
            class_name = doclet['name']
            classes[class_name] = []
            classes_props[class_name] = doclet.get('properties', None)
        elif doclet['kind'] == 'function':
            class_name = doclet.get('memberof')
            if class_name:
                if class_name not in classes:
                    classes[class_name] = []
                classes[class_name].append(doclet)
        elif doclet['kind'] == 'typedef':
            enumerations.append(doclet)

    # Process classes
    for class_name, methods in classes.items():
        class_dir = os.path.join(editor_dir, class_name)
        methods_dir = os.path.join(class_dir, 'Methods')
        os.makedirs(methods_dir, exist_ok=True)

        # Write class file
        class_content = generate_class_markdown(class_name, methods, classes_props[class_name], enumerations, classes)
        write_markdown_file(os.path.join(class_dir, f"{class_name}.md"), class_content)

        # Write method files
        for method in methods:
            method_file_path = os.path.join(methods_dir, f"{method['name']}.md")
            method_content = generate_method_markdown(method, enumerations, classes)
            write_markdown_file(method_file_path, method_content)
            if not method.get('example', ''):
                missing_examples.append(os.path.relpath(method_file_path, output_dir))

    # Process enumerations
    enum_dir = os.path.join(editor_dir, 'Enumeration')
    os.makedirs(enum_dir, exist_ok=True)

    for enum in enumerations:
        enum_file_path = os.path.join(enum_dir, f"{enum['name']}.md")
        enum_content = generate_enumeration_markdown(enum, enumerations, classes)
        write_markdown_file(enum_file_path, enum_content)
        if not enum.get('example', ''):
            missing_examples.append(os.path.relpath(enum_file_path, output_dir))

def generate(output_dir):
    print('Generating Markdown documentation...')
    
    generate_docs_json.generate(output_dir + 'tmp_json', md=True)
    for editor_name in editors:
        input_file = os.path.join(output_dir + 'tmp_json', editor_name + ".json")
        os.makedirs(output_dir + f'/{editor_name.title()}', exist_ok=True)

        data = load_json(input_file)
        process_doclets(data, output_dir, editor_name.title())
    
    shutil.rmtree(output_dir + 'tmp_json')
    print('Done')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default="../../../../office-js-api/"  # Default value
    )
    args = parser.parse_args()
    generate(args.destination)
    print("START_MISSING_EXAMPLES")
    print(",".join(missing_examples))
    print("END_MISSING_EXAMPLES")
