#!/usr/bin/env python3
import os
import sys

def replace_prefix_in_directory(root_dir: str, new_value: str):
    old = "prefix=/usr"
    new = f"prefix={new_value}"

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r") as f:
                    data = f.read()
            except (UnicodeDecodeError, PermissionError, OSError):
                continue

            if old in data:
                data = data.replace(old, new)
                with open(filepath, "w") as f:
                    f.write(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    root = sys.argv[1]
    value = sys.argv[2]

    replace_prefix_in_directory(root, value)

