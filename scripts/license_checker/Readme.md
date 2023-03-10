# license_checker

## Overview

**license_checker** allow you to automatically check
licenses inside specified code files.

## How to use

### Running

**Note**: Pyhton 3.9 and above required
(otherwise `TypeError: 'type' object is not subscriptable`)

* Linux

  ```bash
  python3 license_checker.py
  ```

* Windows

  ```bash
  python license_checker.py
  ```

## How to configure

The checker settings are specified in the `config.json`.
The path to the license template is indicated there.

### How to specify a license template

The license template is a plain text
file where the license text is indicated
as you would like to see the license at
the beginning of the file.

### How to configure `config.json`

#### Сonfig parameters

* `basePath` specifies which folder the
paths will be relative to.
**For example:**

  ```json
  "basePath": "../../../"
  ```

* `reportFolder` specifies in which folder to
save text files with reports.
**For example:**

  ```json
  "reportFolder": "build_tools/scripts/license_checker/reports"
  ```

* `licensePath` specifies the path to the license template.
**For example:**

  ```json
  "licensePath": "build_tools/scripts/license_checker/license_template.txt"
  ```

* `printChecking` specifies whether to output
information about which file is
being checked to the console.
**For example:**

  ```json
  "printChecking": false
  ```

* `printReports` specifies whether to output
reports to the console.
**For example:**

  ```json
  "printReports": false
  ```

* `fix` specifies which categories of reports
should be repaired automatically.
Possible array values:
`"OUTDATED"`,
`"NO_LICENSE"`,
`"INVALID_LICENSE"`,
`"LEN_MISMATCH"`.
**For example:**

  ```json
  "fix": ["OUTDATED", "NO_LICENSE"],
  ```

  Automatically repair files where the license is outdated or not found.

* `configs` license check and repair configurations.

  * `dir` folder to check.
  **For example:**

    ```json
    "dir": "sdkjs"
    ```

  * `fileExtensions` file extensions to check.
  **For example:**

    ```json
    "fileExtensions": [".js"]
    ```
  
  * `startMultiComm` the line that starts the multiline comment.
  **For example:**

    ```json
    "startMultiComm": "/*"
    ```

  * `endMultiComm` the line that ends the multiline comment.
  You should carefully consider the formatting
  of the string, all spaces are taken into account.
  This affects how the license check works.
  **For example:**

    ```json
    "endMultiComm": " */"
    ```

    Space at the beginning for a prettier comment.

  * `prefix` the line on which each comment
  line will begin, except for the
  beginning and end.
  **For example:**

      ```json
      "prefix": " *"
      ```

      Space at the beginning for a prettier comment.
  * `ignoreListDir` folder paths to ignore.
  **For example:**

    ```json
    "ignoreListDir": [
      "sdkjs/deploy",
      "sdkjs/develop",
      "sdkjs/configs",
      "sdkjs/common/AllFonts.js",
      "sdkjs/slide/themes/themes.js"
    ]
    ```

  * `ignoreListDirName` folder names to ignore.
  **For example:**

    ```json
    "ignoreListDirName": [
      "node_modules",
      "vendor"
    ]
    ```

  * `ignoreListFile` file paths to ignore.
  **For example:**

    ```json
    "ignoreListFile": [
      "sdkjs/develop/awesomeFileToIgnore.js",
    ]
    ```

  Any number of configurations can be
  specified, they can overlap
  if we need to check
  files in the same folder in different ways.

