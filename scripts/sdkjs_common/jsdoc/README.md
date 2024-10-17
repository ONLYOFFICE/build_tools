
# Documentation Generation Guide

This guide explains how to generate documentation for Onlyoffice Builder/Plugins API using the provided Python scripts: `generate_docs_json.py`, `generate_docs_plugins_json.py`, `generate_docs_md.py`. These scripts are used to create JSON and Markdown documentation for the `apiBuilder.js` files from the word, cell, and slide editors.

## Requirements

```bash
Node.js v20 and above
Python v3.10 and above
```

## Installation

```bash
git clone https://github.com/ONLYOFFICE/build_tools.git
cd build_tools/scripts/sdkjs_common/jsdoc
npm install
```

## Scripts Overview

### `generate_docs_json.py`

This script generates JSON documentation based on the `apiBuilder.js` files.

- **Usage**:
  ```bash
  python generate_docs_json.py output_path
  ```

- **Parameters**:
  - `output_path` (optional): The directory where the JSON documentation will be saved. If not specified, the default path is `../../../../office-js-api-declarations/office-js-api`.

### `generate_docs_plugins_json.py`

This script generates JSON documentation based on the `api_plugins.js` files.

- **Usage**:
  ```bash
  python generate_docs_plugins_json.py output_path
  ```

- **Parameters**:
  - `output_path` (optional): The directory where the JSON documentation will be saved. If not specified, the default path is `../../../../office-js-api-declarations/office-js-api-plugins`.

### `generate_docs_md.py`

This script generates Markdown documentation from the `apiBuilder.js` files.

- **Usage**:
  ```bash
  python generate_docs_md.py output_path
  ```

- **Parameters**:
  - `output_path` (optional): The directory where the Markdown documentation will be saved. If not specified, the default path is `../../../../office-js-api/`.

## Example

To generate JSON documentation with the default output path:
```bash
python generate_docs_json.py /path/to/save/json
```

To generate JSON documentation with the default output path:
```bash
python generate_docs_plugins_json.py /path/to/save/json
```

To generate Markdown documentation and specify a custom output path:
```bash
python generate_docs_md.py /path/to/save/markdown
```

## Notes

- Make sure to have all necessary permissions to run these scripts and write to the specified directories.
- The output directories will be created if they do not exist.

