#!/usr/bin/env python3
import os
import json
import re
import shutil
import argparse
import generate_docs_events_json

# Папки для каждого editor_name
editors = {
    "word": "text-document-api",
    "cell": "spreadsheet-api",
    "slide": "presentation-api",
    "forms": "form-api"
}

missing_examples = []
used_enumerations = set()


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_markdown_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def remove_js_comments(text):
    text = re.sub(r'^\s*//.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text.strip()


def correct_description(string, root='', isInTable=False):
    """
    Cleans or transforms specific tags in the doclet description:
      - <b> => ** (bold text)
      - <note>...</note> => 💡 ...
      - {@link ...} is replaced with a Markdown link
      - If the description is missing, returns a default value.
      - All '\r' characters are replaced with '\n'.
    """
    if string is None:
        return 'No description provided.'

    if False == isInTable:
        # Line breaks
        string = string.replace('\r', '\\\n')
    
    # Replace <b> tags with Markdown bold formatting
    string = re.sub(r'<b>', '-**', string)
    string = re.sub(r'</b>', '**', string)
    
    # Replace <note> tags with an icon and text
    string = re.sub(r'<note>(.*?)</note>', r'💡 \1', string, flags=re.DOTALL)
    
    # Process {@link ...} constructions
    string = process_link_tags(string, root)
    
    return string

def process_link_tags(text, root=''):
    """
    Finds patterns like {@link ...} and replaces them with Markdown links.
    If the prefix 'global#' is found, a link to a typedef is generated,
    otherwise, a link to a class method is created.
    For a method, if an alias is not specified, the name is left in the format 'Class#Method'.
    """
    reserved_links = {
        '/docbuilder/global#ShapeType': f"{'../../../../../../' if root == '' else '../../../../../' if root == '../' else root}docs/office-api/usage-api/text-document-api/Enumeration/ShapeType.md",
        '/plugin/config': 'https://api.onlyoffice.com/docs/plugin-and-macros/structure/configuration/',
        '/docbuilder/basic': 'https://api.onlyoffice.com/docs/office-api/usage-api/text-document-api/'
    }

    def replace_link(match):
        content = match.group(1).strip()  # Example: "/docbuilder/global#ShapeType shape type" or "global#ErrorValue ErrorValue"
        parts = content.split()
        ref = parts[0]
        label = parts[1] if len(parts) > 1 else None

        if ref.startswith('/'):
            # Handle reserved links using mapping
            if ref in reserved_links:
                url = reserved_links[ref]
                display_text = label if label else ref
                return f"[{display_text}]({url})"
            elif ref.startswith('/docs/plugins/'):
                url = f'../../{ref.split('/docs/plugins/')[1]}.md'
                display_text = label if label else ref
                return f"[{display_text}]({url})"
            else:
                # If the link is not in the mapping, return the original construction
                return match.group(0)
        elif ref.startswith("global#"):
            # Handle links to typedef (similar logic as before)
            typedef_name = ref.split("#")[1]
            used_enumerations.add(typedef_name)
            display_text = label if label else typedef_name
            return f"[{display_text}]({root}Enumeration/Event_{typedef_name}.md)"
        else:
            # Handle links to class methods like ClassName#MethodName
            try:
                class_name, method_name = ref.split("#")
            except ValueError:
                return match.group(0)
            display_text = label if label else ref  # Keep the full notation, e.g., "Api#CreateSlide"
            return f"[{display_text}]({root}{class_name}/Methods/{method_name}.md)"

    return re.sub(r'{@link\s+([^}]+)}', replace_link, text)

def remove_line_breaks(s):
    return re.sub(r'[\r\n]+', ' ', s)


def convert_jsdoc_array_to_ts(type_str):
    p = re.compile(r'Array\.<([^>]+)>')
    while True:
        m = p.search(type_str)
        if not m:
            break
        inner = convert_jsdoc_array_to_ts(m.group(1).strip())
        type_str = type_str[:m.start()] + inner + '[]' + type_str[m.end():]
    return type_str


def generate_data_types_markdown(types, enumerations, root=''):
    converted = [convert_jsdoc_array_to_ts(t) for t in types]
    primitives = {"string", "number", "boolean", "null", "undefined", "any", "object", "false", "true", "json", "function", "date", "{}"}
    result = []
    enum_names = {e['name'] for e in enumerations}
    for t in converted:
        base = t.rstrip('[]')
        dims = t[len(base):]
        if base in enum_names:
            used_enumerations.add(base)
            link = f"[Event_{base}]({root}../Enumeration/Event_{base}.md)"
        elif base in primitives or re.match(r"^['\"].*['\"]$", base) or re.match(r"^-?\d+(\.\d+)?$", base):
            link = base
        else:
            link = base
        result.append(link + dims)
    return " | ".join(result)


def escape_text_outside_code_blocks(md):
    parts = re.split(r'(```.*?```)', md, flags=re.DOTALL)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace('<', '&lt;').replace('>', '&gt;')
    return "".join(parts)


def generate_event_markdown(event, enumerations):
    name = event['name']
    desc = correct_description(event.get('description', ''))
    params = event.get('params', [])

    md = f"# {name}\n\n{desc}\n\n"

    # Parameters
    md += "## Parameters\n\n"
    if params:
        md += "| **Name** | **Data type** | **Description** |\n"
        md += "| --------- | ------------- | ----------- |\n"
        for p in params:
            t_md = generate_data_types_markdown(
                p.get('type', {}).get('names', []),
                enumerations
            )
            d = remove_line_breaks(correct_description(p.get('description', ''), isInTable=True))
            md += f"| {p['name']} | {t_md} | {d} |\n"
        md += "\n"
    else:
        md += "This event has no parameters.\n\n"

    for ex in event.get('examples', []):
        code = remove_js_comments(ex).strip()
        md += f"```javascript\n{code}\n```\n\n"

    return escape_text_outside_code_blocks(md)


def generate_enumeration_markdown(enumeration, enumerations):
    """
    Generates Markdown documentation for a 'typedef' doclet.
    This version only works with `enumeration['examples']` (an array of strings),
    ignoring any single `enumeration['examples']` field.
    """
    enum_name = enumeration['name']

    if enum_name not in used_enumerations:
        return None
    
    description = enumeration.get('description', 'No description provided.')
    description = correct_description(description, '../')

    # Only use the 'examples' array
    examples = enumeration.get('examples', [])

    content = f"# Event_{enum_name}\n\n{description}\n\n"

    parsed_type = enumeration['type'].get('parsedType')
    if not parsed_type:
        # If parsedType is missing, just list 'type.names' if available
        type_names = enumeration['type'].get('names', [])
        if type_names:
            content += "## Type\n\n"
            t_md = generate_data_types_markdown(type_names, enumerations)
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
                    used_enumerations.add(raw_t)
                    content += f"- [{raw_t}](../Enumeration/Event_{raw_t}.md)\n"
                else:
                    content += f"- {raw_t}\n"

        # 2) Handle TypeApplication (e.g. Object.<string, string>)
        elif ptype == 'TypeApplication':
            content += "## Type\n\nObject\n\n"
            type_names = enumeration['type'].get('names', [])
            if type_names:
                t_md = generate_data_types_markdown(type_names, enumerations)
                content += f"**Type:** {t_md}\n\n"

        # 3) If properties are present, treat it like an object
        if enumeration.get('properties') is not None:
            content += generate_properties_markdown(enumeration['properties'], enumerations)

        # 4) If it's neither TypeUnion nor TypeApplication, just output the type names
        if ptype not in ('TypeUnion', 'TypeApplication'):
            type_names = enumeration['type'].get('names', [])
            if type_names:
                content += "## Type\n\n"
                t_md = generate_data_types_markdown(type_names, enumerations)
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
                
                content += f"```javascript\n{code}\n```\n"
            else:
                if len(examples) > 1:
                    content += f"**Example {i}:**\n\n{comment}\n\n"
                # No special fences, just show as code
                content += f"```javascript\n{cleaned_example}\n```\n"

    return escape_text_outside_code_blocks(content)

def generate_properties_markdown(properties, enumerations):
    if properties is None:
        return ''
    
    content = "## Properties\n\n"
    content += "| Name | Type | Description |\n"
    content += "| ---- | ---- | ----------- |\n"

    for prop in sorted(properties, key=lambda m: m['name']):
        prop_name = prop['name']
        prop_description = prop.get('description', 'No description provided.')
        prop_description = remove_line_breaks(correct_description(prop_description, isInTable=True))
        prop_types = prop['type']['names'] if prop.get('type') else []
        param_types_md = generate_data_types_markdown(prop_types, enumerations)
        content += f"| {prop_name} | {param_types_md} | {prop_description} |\n"

    # Escape outside code blocks
    return escape_text_outside_code_blocks(content)

def clean_editor_dir(editor_dir):
    for root, dirs, files in os.walk(editor_dir, topdown=False):
        for file in files:
            if not file.endswith(('.json')):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # remove empty folder
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

def clean_enum_files(editor_dir: str):
    for root, _, files in os.walk(editor_dir, topdown=False):
        for file in files:
            if True == file.startswith('Event_') and False == file.endswith('.json'):
                os.remove(os.path.join(root, file))

def process_events(data, editor_dir):
    enumerations = []
    events = []

    for doclet in data:
        kind = doclet.get('kind')
        if kind == 'typedef':
            enumerations.append(doclet)
        elif kind == 'event':
            events.append(doclet)

    events_dir = f'{editor_dir}/Events'
    clean_editor_dir(events_dir)
    os.makedirs(events_dir, exist_ok=True)
    used_enumerations.clear()

    # пишем события
    for ev in events:
        path = os.path.join(events_dir, f"{ev['name']}.md")
        write_markdown_file(path, generate_event_markdown(ev, enumerations))
        if not ev.get('examples'):
            missing_examples.append(os.path.relpath(path, events_dir))

    # пишем перечисления, используемые событиями
    enum_dir = os.path.join(editor_dir, 'Enumeration')
    clean_enum_files(enum_dir)
    
    os.makedirs(enum_dir, exist_ok=True)
    prev = -1
    while len(used_enumerations) != prev:
        prev = len(used_enumerations)
        for e in enumerations:
            if e['name'] in used_enumerations:
                generate_enumeration_markdown(e, enumerations)
    for e in enumerations:
        if e['name'] in used_enumerations:
            path = os.path.join(enum_dir, f"Event_{e['name']}.md")
            write_markdown_file(path, generate_enumeration_markdown(e, enumerations))
            if not e.get('examples'):
                missing_examples.append(os.path.relpath(path, editor_dir))


def generate_events(output_dir):
    if output_dir.endswith('/'):
        output_dir = output_dir[:-1]
    tmp = os.path.join(output_dir, 'tmp_json')

    generate_docs_events_json.generate(tmp, md=True)

    for editor_name, folder in editors.items():
        data = load_json(os.path.join(tmp, f"{editor_name}.json"))
        process_events(data, os.path.join(output_dir, folder))

    shutil.rmtree(tmp)
    print("Done. Missing examples:", missing_examples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate events documentation")
    parser.add_argument(
        "destination",
        nargs="?",
        default="../../../../../api.onlyoffice.com/site/docs/plugin-and-macros/interacting-with-editors/",
        help="Output directory"
    )
    args = parser.parse_args()
    generate_events(args.destination)