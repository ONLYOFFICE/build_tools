import os
import subprocess
import json
import argparse
import re

# Конфигурационные файлы
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

    # Пересоздание файла missing_examples.txt
    with open(missing_examples_file, 'w', encoding='utf-8') as f:
        f.write('')

    # Генерация json документации
    for config in configs:
        editor_name = config.split('/')[-1].replace('.json', '')
        output_file = os.path.join(output_dir, editor_name + ".json")
        command = f"set EDITOR={editors_maps[editor_name]} && npx jsdoc -c {config} -X > {output_file}"
        print(f"Generating {editor_name}.json: {command}")
        subprocess.run(command, shell=True)

    # дозапись примеров в json документацию
    for config in configs:
        editor_name = config.split('/')[-1].replace('.json', '')
        output_file = os.path.join(output_dir, editor_name + ".json")
        
        # Чтение JSON файла
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Модификация JSON данных
        for doclet in data:
            if 'see' in doclet:
                if doclet['see'] is not None:
                    file_path = 'C:\\Users\\khrom\\Desktop\\Onlyoffice\\' + doclet['see'][0]
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as see_file:
                            example_content = see_file.read()
                        
                        # Извлечение первой строки как комментария, если она существует
                        lines = example_content.split('\n')
                        if lines[0].startswith('//'):
                            comment = lines[0] + '\n'
                            code_content = '\n'.join(lines[1:])
                        else:
                            comment = ''
                            code_content = example_content
                        
                        # Форматирование содержимого для doclet['example']
                        doclet['example'] = remove_js_comments(comment) + "```js\n" + remove_builder_lines(code_content) + "\n```"
                    else:
                        # Запись пропущенного примера в файл missing_examples.txt
                        with open(missing_examples_file, 'a', encoding='utf-8') as missing_file:
                            missing_file.write(f"{file_path}\n")
        
        # Запись измененного JSON файла обратно
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    print("Documentation generation completed.")

def remove_builder_lines(text):
    lines = text.splitlines()  # Разделить текст на строки
    filtered_lines = [line for line in lines if not line.strip().startswith("builder.")]
    return "\n".join(filtered_lines)

def remove_js_comments(text):
    # Удаляем однострочные комментарии, оставляя текст после //
    text = re.sub(r'^\s*//\s?', '', text, flags=re.MULTILINE)
    # Удаляем многострочные комментарии, оставляя текст после /*
    text = re.sub(r'/\*\s*|\s*\*/', '', text, flags=re.DOTALL)
    return text.strip()

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
    
    generate(args.destination)