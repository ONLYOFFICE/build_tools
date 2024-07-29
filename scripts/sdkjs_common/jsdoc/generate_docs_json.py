import os
import subprocess
import json
import argparse
import re

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

def generate(output_dir):
    missing_examples_file = f'{output_dir}/missing_examples.txt'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Recreate missing_examples.txt file
    with open(missing_examples_file, 'w', encoding='utf-8') as f:
        f.write('')

    # Generate JSON documentation
    for config in configs:
        editor_name = config.split('/')[-1].replace('.json', '')
        output_file = os.path.join(output_dir, editor_name + ".json")
        command = f"set EDITOR={editors_maps[editor_name]} && npx jsdoc -c {config} -X > {output_file}"
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
                    file_path = '../../../../' + doclet['see'][0]
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
                        
                        # Format content for doclet['example']
                        doclet['example'] = remove_js_comments(comment) + "```js\n" + remove_builder_lines(code_content) + "\n```"
                    else:
                        # Record missing examples in missing_examples.txt
                        with open(missing_examples_file, 'a', encoding='utf-8') as missing_file:
                            missing_file.write(f"{file_path}\n")
        
        # Write the modified JSON file back
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    print("Documentation generation completed.")

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

def get_current_branch(path):
    try:
        # Navigate to the specified directory and get the current branch name
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default="../../../../document-builder-declarations/document-builder"  # Default value
    )
    args = parser.parse_args()
    
    branch_name = get_current_branch("../../../../sdkjs")
    if branch_name:
        args.destination = f"{args.destination}/{branch_name}"
    
    generate(args.destination)
