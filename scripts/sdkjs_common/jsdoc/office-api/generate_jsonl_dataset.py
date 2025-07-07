import os
import json
import re
import shutil
import argparse
import generate_docs_json
from datetime import datetime

# Configuration files
editors = [
    "word",
    "cell",
    "slide",
    "forms"
]

editors_names = {
    "word": "Word",
    "cell": "Spreadsheet",
    "slide": "Presentation",
    "forms": "Forms"
}

root = '../../../../..'
missing_examples = []

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_file_content(file_path):
    try:
        with open(file_path, encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        missing_examples.append(file_path)
        # print(f"Failed to open file {file_path}: {e}")
        return ""

def extract_js_comments_as_text(text):
    # Extract single-line comments (after //)
    single_line_comments = re.findall(r'^\s*//(.*)$', text, flags=re.MULTILINE)
    # Extract multi-line comments (between /* and */)
    multi_line_comments = re.findall(r'/\*(.*?)\*/', text, flags=re.DOTALL)
    # Combine all found comments into a single list
    all_comments = single_line_comments + multi_line_comments
    # Join comments into a single text, separated by a space
    return " ".join(comment.strip() for comment in all_comments if comment.strip())

def extract_examples_blocks(content: str):
    blocks = []
    current_block = {"comments": [], "code": []}
    in_comment_section = True  # Collect comments until code appears
    current_comment_group = []  # Accumulate lines of the current comment

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            # Empty line
            if in_comment_section and current_comment_group:
                # Finish the current comment group
                comment_text = " ".join(current_comment_group)
                current_block["comments"].append(comment_text)
                current_comment_group = []
            elif not in_comment_section:
                # Empty line in the code – keep it as is
                current_block["code"].append(line)
            continue

        if stripped.startswith("//"):
            if in_comment_section:
                # Remove comment marker and extra spaces
                current_comment_group.append(extract_js_comments_as_text(stripped))
            else:
                # Comment after code starts – finish the current block and start a new one
                blocks.append({
                    "comments": current_block["comments"],
                    "code": "\n".join(current_block["code"]).rstrip()
                })
                current_block = {"comments": [], "code": []}
                in_comment_section = True
                # Start a new comment group with the current line
                current_comment_group = [stripped[2:].strip()]
        else:
            # Code line
            if in_comment_section:
                if current_comment_group:
                    comment_text = " ".join(current_comment_group)
                    current_block["comments"].append(comment_text)
                    current_comment_group = []
                in_comment_section = False
            current_block["code"].append(line)

    # Finalize any remaining comment group
    if in_comment_section and current_comment_group:
        comment_text = " ".join(current_comment_group)
        current_block["comments"].append(comment_text)
    # Save the last block if it's not empty
    if current_block["comments"] or current_block["code"]:
        blocks.append({
            "comments": current_block["comments"],
            "code": "\n".join(current_block["code"]).rstrip()
        })

    return blocks

def extract_examples_blocks_temp(content: str):
    lines = content.splitlines()
    comment_blocks = []
    current_group = []
    first_code_index = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if current_group:
                comment_blocks.append(" ".join(current_group))
                current_group = []
            continue
        if stripped.startswith("//"):
            current_group.append(stripped[2:].strip())
        else:
            if current_group:
                comment_blocks.append(" ".join(current_group))
                current_group = []
            first_code_index = i
            break

    code_part = ""
    if first_code_index is not None:
        code_part = "\n".join(lines[first_code_index:]).rstrip()

    return [{"comments": comment_blocks, "code": code_part}]

def create_entry(system_message, user_message, assistant_message, model):
    entry = {
        "created_at": datetime.now().isoformat(" "),
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ],
        "recommended": False,
        "upvoted": True
    }

    if model is not "":
        entry["model"] = model

    return entry 

def process_doclets(doclets, output_entries, editor_name, model):
    system_message = f'You are an expert in API for library from OnlyOffice. The library provides functions for editing {editors_names[editor_name]} documents. Your functional capabilities: 1) Explanation of Onlyoffice JavaScript API classes and their methods and parameters. 2) Assistance in writing Onlyoffice JavaScript API examples upon user request. 3) Reviewing user examples, assisting in finding and fixing their mistakes.'
    
    for doclet in doclets:
        kind = doclet.get("kind", "").lower()
        see = doclet.get("see", [])
        
        # The "see" field must always be present
        if not see:
            continue
        
        # Processing based on the "kind" value
        if kind == "function":
            method_name = doclet.get("name", "")
            memberof = doclet.get("memberof", "")
            # Functions must have both "name" (method_name) and "memberof" fields filled
            if not (method_name and memberof):
                continue
            default_user_message = f"How do I use the method {method_name} of {memberof} class?"
            
        elif kind == "class":
            class_name = doclet.get("name", "")
            default_user_message = f"How do I instantiate or work with the class {class_name}?"
            
        elif kind == "typedef":
            typedef_name = doclet.get("name", "")
            default_user_message = f"How do I use the typedef {typedef_name}?"
            
        else:
            continue
        
        # Read the content of the first file listed in the "see" field
        content = read_file_content(f'{root}/{see[0]}')
        if content == "":
            continue
        
        # now use only first block cause there is bad comments in examples
        blocks = extract_examples_blocks_temp(content)
        
        for block in blocks:
            assistant_message = block['code']

            # default entry
            output_entries.append(create_entry(system_message, default_user_message, assistant_message, model))

            # If the file content contains comments, create a separate entry for each one
            for comment in block['comments']:
                output_entries.append(create_entry(system_message, comment, assistant_message, model))
            
def generate(output_dir, model):
    print('Generating documentation JSONL dataset...')
    
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    generate_docs_json.generate(f'{output_dir}/tmp_json')
    
    output_entries = []
    output_filename = "dataset.jsonl"

    for editor_name in editors:
        input_file = os.path.join(f'{output_dir}/tmp_json', editor_name + ".json")
        doclets = load_json(input_file)
        process_doclets(doclets, output_entries, editor_name, model)
    
    with open(f'{output_dir}/{output_filename}', "w", encoding="utf-8") as out_file:
        for entry in output_entries:
            out_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    shutil.rmtree(f'{output_dir}/tmp_json')
    print('Done')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation JSONL dataset")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default="../../../../../office-js-api/dataset"  # Default value
    )
    parser.add_argument(
        "model", 
        type=str, 
        help="Type of model",
        nargs='?',  # Indicates the argument is optional
        default=""  # Default value
    )
    args = parser.parse_args()

    generate(args.destination, args.model)
    print("START_MISSING_EXAMPLES")
    print(",".join(missing_examples))
    print("END_MISSING_EXAMPLES")
