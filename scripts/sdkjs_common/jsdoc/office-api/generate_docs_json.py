import os
import subprocess
import json
import argparse
import re
import platform

root = '../../../../..'

# Configuration files
configs = [
    "./config/word.json",
    "./config/cell.json",
    "./config/slide.json",
    "./config/forms.json"
]

editors_maps = {
    "word":     "CDE",
    "cell":     "CSE",
    "slide":    "CPE",
    "forms":    "CFE"
}

def generate(output_dir, md=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate JSON documentation
    for config in configs:
        editor_name = config.split('/')[-1].replace('.json', '')
        output_file = os.path.join(output_dir, editor_name + ".json")
        command_set_env = "export"
        if (platform.system().lower() == "windows"):
            command_set_env = "set"
        command = f"{command_set_env} EDITOR={editors_maps[editor_name]} && npx jsdoc -c {config} -X > {output_file}"
        print(f"Generating {editor_name}.json: {command}")
        subprocess.run(command, shell=True)

    # Append examples to JSON documentation
    for config in configs:
        editor_name = config.split('/')[-1].replace('.json', '')
        output_file = os.path.join(output_dir, editor_name + ".json")
        
        # Read the JSON file
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Modify JSON data
        for doclet in data:
            if 'see' in doclet:
                if doclet['see'] is not None:
                    if editor_name == 'forms':
                        doclet['see'][0] = doclet['see'][0].replace('{Editor}', 'Word')
                    else:
                        doclet['see'][0] = doclet['see'][0].replace('{Editor}', editor_name.title())

                    file_path = f'{root}/' + doclet['see'][0]

                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as see_file:
                            example_content = see_file.read()
                        
                        # Extract the first line as a comment if it exists
                        lines = example_content.split('\n')
                        if lines[0].startswith('//'):
                            comment = lines[0] + '\n'
                            code_content = '\n'.join(lines[1:])
                        else:
                            comment = ''
                            code_content = example_content
                        
                        if md == True:
                            doclet['example'] = remove_js_comments(comment) + "```js\n" + code_content + "\n```"
                        
                        if md == False:
                            document_type = editor_name
                            if "forms" == document_type:
                                document_type = "pdf"
                            doclet['description'] = doclet['description'] + f'\n\n## Try it\n\n ```js document-builder={{"documentType": "{document_type}"}}\n{code_content}\n```'
        
        # Write the modified JSON file back
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    print("Documentation generation for builder completed.")

def remove_builder_lines(text):
    lines = text.splitlines()  # Split text into lines
    filtered_lines = [line for line in lines if not line.strip().startswith("builder.")]
    return "\n".join(filtered_lines)

def remove_js_comments(text):
    # Remove single-line comments, leaving text after //
    text = re.sub(r'^\s*//\s?', '', text, flags=re.MULTILINE)
    # Remove multi-line comments, leaving text after /*
    text = re.sub(r'/\*\s*|\s*\*/', '', text, flags=re.DOTALL)
    return text.strip()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default=f"{root}/office-js-api-declarations/office-js-api"
    )
    args = parser.parse_args()
    generate(args.destination)
