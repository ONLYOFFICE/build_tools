import os
import json
import re
import shutil
import argparse
import generate_docs_plugins_json

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
    text = re.sub(r'^\s*//.*$', '', text, flags=re.MULTILINE)  # single-line
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)     # multi-line
    return text.strip()

def correct_description(string):
    """
    Cleans up or transforms certain tags in a doclet description:
      - <b> => **
      - <note>...</note> => 💡 ...
      - Provide a default if None.
    """
    if string is None:
        return 'No description provided.'
    
    # Replace <b> tags with markdown bold
    string = re.sub(r'<b>', '**', string)
    string = re.sub(r'</b>', '**', string)
    # Convert <note>...</note> to a little icon + text
    string = re.sub(r'<note>(.*?)</note>', r'💡 \1', string, flags=re.DOTALL)
    return string

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
    return re.sub(r'[\r\n]+', ' ', string)

# Convert Array.<T> => T[] (including nested arrays).
def convert_jsdoc_array_to_ts(type_str: str) -> str:
    """
    Recursively replaces 'Array.<T>' with 'T[]',
    handling nested arrays like 'Array.<Array.<string>>' => 'string[][]'.
    """
    pattern = re.compile(r'Array\.<([^>]+)>')
    
    while True:
        match = pattern.search(type_str)
        if not match:
            break
        
        inner_type = match.group(1).strip()
        # Recursively convert inner parts
        inner_type = convert_jsdoc_array_to_ts(inner_type)
        
        # Replace the outer Array.<...> with ...[]
        type_str = (
            type_str[:match.start()] 
            + f"{inner_type}[]" 
            + type_str[match.end():]
        )
    
    return type_str

def escape_text_outside_code_blocks(markdown: str) -> str:
    """
    Splits content by fenced code blocks, escapes MDX-unsafe characters
    (<, >, {, }) only in the text outside those code blocks.
    """
    # A regex to capture fenced code blocks with ```
    parts = re.split(r'(```.*?```)', markdown, flags=re.DOTALL)
    
    # Even indices (0, 2, 4, ...) are outside code blocks,
    # odd indices (1, 3, 5, ...) are actual code blocks.
    for i in range(0, len(parts), 2):
        # Only escape in parts outside code blocks
        parts[i] = (parts[i]
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('{', '&#123;')
                    .replace('}', '&#125;')
                   )
    return "".join(parts)

def get_base_type(ts_type: str) -> str:
    """
    Given a TypeScript-like type (e.g. "Drawing[][]"), return the
    'base' portion by stripping trailing "[]". For "Drawing[][]",
    returns "Drawing". For "Array.<Drawing>", you'd convert it first
    to "Drawing[]" then return "Drawing".
    """
    while ts_type.endswith('[]'):
        ts_type = ts_type[:-2]
    return ts_type

def generate_data_types_markdown(types, enumerations, classes, root='../../'):
    """
    1) Convert each raw JSDoc type from Array.<T> to T[].
    2) Split union types if needed (usually they're provided as separate
       elements in 'types' already, but let's be safe).
    3) For each type, extract the base type (e.g. "Drawing" from "Drawing[]").
    4) If the base type matches an enumeration or class, link the entire
       T[]-based string.
    5) Join with " | ".
    """

    # Convert each raw type from JSDoc to TS
    converted = [convert_jsdoc_array_to_ts(t) for t in types]  # e.g. ["Drawing[]", "Foo[]", ...]

    # For each converted type (like "Drawing[]"), see if the base is in enumerations or classes
    def link_if_known(ts_type):
        base = get_base_type(ts_type)  # e.g. "Drawing" from "Drawing[]"

        # Check enumerations first
        for enum in enumerations:
            if enum['name'] == base:
                # Replace the entire token with a link
                return f"[{ts_type}]({root}Enumeration/{base}.md)"

        # Check classes
        if base in classes:
            return f"[{ts_type}]({root}{base}/{base}.md)"

        # Otherwise just return as-is
        return ts_type

    # Build final list of possibly-linked types
    linked = [link_if_known(ts_t) for ts_t in converted]

    # Join them with " | "
    param_types_md = r' \| '.join(linked)

    # If there's still leftover angle brackets for generics, gently escape or link them
    # e.g. "Object.<string, number>" => "Object.&lt;string, number&gt;"
    # or do more specialized linking if you want to handle them deeper.
    def replace_leftover_generics(match):
        element = match.group(1).strip()
        return f"&lt;{element}&gt;"
    
    param_types_md = re.sub(r'<([^<>]+)>', replace_leftover_generics, param_types_md)

    return param_types_md

def generate_class_markdown(class_name, methods, properties, enumerations, classes):
    content = f"# {class_name}\n\nRepresents the {class_name} class.\n\n"
    content += generate_properties_markdown(properties, enumerations, classes)

    content += "## Methods\n\n"
    for method in methods:
        method_name = method['name']
        content += f"- [{method_name}](./Methods/{method_name}.md)\n"

    # Escape just before returning
    return escape_text_outside_code_blocks(content)

def generate_method_markdown(method, enumerations, classes, example_editor_name):
    """
    Generates Markdown for a method doclet, relying only on `method['examples']`
    (array of strings). Ignores any single `method['example']` field.
    """

    method_name = method['name']
    description = method.get('description', 'No description provided.')
    description = correct_description(description)
    params = method.get('params', [])
    returns = method.get('returns', [])
    memberof = method.get('memberof', '')

    # Use the 'examples' array only
    examples = method.get('examples', [])

    content = f"# {method_name}\n\n{description}\n\n"
    
    # Syntax
    param_list = ', '.join([param['name'] for param in params]) if params else ''
    content += f"## Syntax\n\n```javascript\nexpression.{method_name}({param_list});\n```\n\n"
    if memberof:
        content += f"`expression` - A variable that represents a [{memberof}](../{memberof}.md) class.\n\n"

    # Parameters
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

    # Returns
    content += "\n## Returns\n\n"
    if returns:
        return_type_list = returns[0].get('type', {}).get('names', [])
        return_type_md = generate_data_types_markdown(return_type_list, enumerations, classes)
        content += return_type_md
    else:
        content += "This method doesn't return any data."

    # Process examples array
    if examples:
        if len(examples) > 1:
            content += "\n\n## Examples\n\n"
        else:
            content += "\n\n## Example\n\n"

        for i, ex_line in enumerate(examples, start=1):
            # Remove JS comments
            cleaned_example = remove_js_comments(ex_line).strip()

            # Attempt splitting if the user used ```js
            if '```js' in cleaned_example:
                comment, code = cleaned_example.split('```js', 1)
                comment = comment.strip()
                code = code.strip()
                if len(examples) > 1:
                    content += f"**Example {i}:**\n\n{comment}\n\n"
                
                content += f"```javascript {example_editor_name}\n{code}\n```\n"
            else:
                if len(examples) > 1:
                    content += f"**Example {i}:**\n\n{comment}\n\n"
                # No special fences, just show as code
                content += f"```javascript {example_editor_name}\n{cleaned_example}\n```\n"

    return escape_text_outside_code_blocks(content)

def generate_properties_markdown(properties, enumerations, classes, root='../'):
    if properties is None:
        return ''
    
    content = "## Properties\n\n"
    content += "| Name | Type | Description |\n"
    content += "| ---- | ---- | ----------- |\n"

    for prop in properties:
        prop_name = prop['name']
        prop_description = prop.get('description', 'No description provided.')
        prop_description = remove_line_breaks(correct_description(prop_description))
        prop_types = prop['type']['names'] if prop.get('type') else []
        param_types_md = generate_data_types_markdown(prop_types, enumerations, classes, root)
        content += f"| {prop_name} | {param_types_md} | {prop_description} |\n"

    # Escape outside code blocks
    return escape_text_outside_code_blocks(content)

def generate_enumeration_markdown(enumeration, enumerations, classes, example_editor_name):
    """
    Generates Markdown documentation for a 'typedef' doclet.
    This version only works with `enumeration['examples']` (an array of strings),
    ignoring any single `enumeration['examples']` field.
    """

    enum_name = enumeration['name']
    description = enumeration.get('description', 'No description provided.')
    description = correct_description(description)

    # Only use the 'examples' array
    examples = enumeration.get('examples', [])

    content = f"# {enum_name}\n\n{description}\n\n"

    parsed_type = enumeration['type'].get('parsedType')
    if not parsed_type:
        # If parsedType is missing, just list 'type.names' if available
        type_names = enumeration['type'].get('names', [])
        if type_names:
            content += "## Type\n\n"
            t_md = generate_data_types_markdown(type_names, enumerations, classes)
            content += t_md + "\n\n"
    else:
        ptype = parsed_type['type']

        # 1) Handle TypeUnion
        if ptype == 'TypeUnion':
            content += "## Type\n\nEnumeration\n\n"
            content += "## Values\n\n"
            for raw_t in enumeration['type']['names']:
                # Attempt linking
                if any(enum['name'] == raw_t for enum in enumerations):
                    content += f"- [{raw_t}](../Enumeration/{raw_t}.md)\n"
                elif raw_t in classes:
                    content += f"- [{raw_t}](../{raw_t}/{raw_t}.md)\n"
                else:
                    content += f"- {raw_t}\n"

        # 2) Handle TypeApplication (e.g. Object.<string, string>)
        elif ptype == 'TypeApplication':
            content += "## Type\n\nObject\n\n"
            type_names = enumeration['type'].get('names', [])
            if type_names:
                t_md = generate_data_types_markdown(type_names, enumerations, classes)
                content += f"**Type:** {t_md}\n\n"

        # 3) If properties are present, treat it like an object
        if enumeration.get('properties') is not None:
            content += generate_properties_markdown(enumeration['properties'], enumerations, classes)

        # 4) If it's neither TypeUnion nor TypeApplication, just output the type names
        if ptype not in ('TypeUnion', 'TypeApplication'):
            type_names = enumeration['type'].get('names', [])
            if type_names:
                content += "## Type\n\n"
                t_md = generate_data_types_markdown(type_names, enumerations, classes)
                content += t_md + "\n\n"

    # Process examples array
    if examples:
        if len(examples) > 1:
            content += "\n\n## Examples\n\n"
        else:
            content += "\n\n## Example\n\n"

        for i, ex_line in enumerate(examples, start=1):
            # Remove JS comments
            cleaned_example = remove_js_comments(ex_line).strip()

            # Attempt splitting if the user used ```js
            if '```js' in cleaned_example:
                comment, code = cleaned_example.split('```js', 1)
                comment = comment.strip()
                code = code.strip()
                if len(examples) > 1:
                    content += f"**Example {i}:**\n\n{comment}\n\n"
                
                content += f"```javascript {example_editor_name}\n{code}\n```\n"
            else:
                if len(examples) > 1:
                    content += f"**Example {i}:**\n\n{comment}\n\n"
                # No special fences, just show as code
                content += f"```javascript {example_editor_name}\n{cleaned_example}\n```\n"

    return escape_text_outside_code_blocks(content)

def process_doclets(data, output_dir, editor_name):
    classes = {}
    classes_props = {}
    enumerations = []
    editor_dir =  os.path.join(output_dir, editor_name)
    example_editor_name = 'editor-'
    
    if editor_name == 'Word':
        example_editor_name += 'docx'
    elif editor_name == 'Forms':
        example_editor_name += 'pdf'
    elif editor_name == 'Slide':
        example_editor_name += 'pptx'
    elif editor_name == 'Cell':
        example_editor_name += 'xlsx'

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
        class_content = generate_class_markdown(
            class_name, 
            methods, 
            classes_props[class_name], 
            enumerations, 
            classes
        )
        write_markdown_file(os.path.join(class_dir, f"{class_name}.md"), class_content)

        # Write method files
        for method in methods:
            method_file_path = os.path.join(methods_dir, f"{method['name']}.md")
            method_content = generate_method_markdown(method, enumerations, classes, example_editor_name)
            write_markdown_file(method_file_path, method_content)

            if not method.get('examples', ''):
                missing_examples.append(os.path.relpath(method_file_path, output_dir))

    # Process enumerations
    enum_dir = os.path.join(editor_dir, 'Enumeration')
    os.makedirs(enum_dir, exist_ok=True)

    for enum in enumerations:
        enum_file_path = os.path.join(enum_dir, f"{enum['name']}.md")
        enum_content = generate_enumeration_markdown(enum, enumerations, classes, example_editor_name)
        if enum_content is None:
            continue

        write_markdown_file(enum_file_path, enum_content)
        if not enum.get('examples', ''):
            missing_examples.append(os.path.relpath(enum_file_path, output_dir))

def generate(output_dir):
    print('Generating Markdown documentation...')
    
    if output_dir[-1] == '/':
        output_dir = output_dir[:-1]
    
    generate_docs_plugins_json.generate(output_dir + '/tmp_json', md=True)
    for editor_name in editors:
        input_file = os.path.join(output_dir + '/tmp_json', editor_name + ".json")

        shutil.rmtree(output_dir + f'/{editor_name.title()}', ignore_errors=True)
        os.makedirs(output_dir + f'/{editor_name.title()}')

        data = load_json(input_file)
        process_doclets(data, output_dir, editor_name.title())
    
    shutil.rmtree(output_dir + '/tmp_json')
    print('Done')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default="../../../../office-js-api/Plugins/"  # Default value
    )
    args = parser.parse_args()
    generate(args.destination)
    print("START_MISSING_EXAMPLES")
    print(",".join(missing_examples))
    print("END_MISSING_EXAMPLES")
