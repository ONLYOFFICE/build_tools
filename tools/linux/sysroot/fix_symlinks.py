import os
import sys
import uuid

# change symbolic link to relative paths
def fix_symlinks(top_dir='./sysroot_ubuntu_1604'):
    for root, dirs, files in os.walk(top_dir):
        for name in files:
            path = os.path.join(root, name)
            if not os.path.islink(path):
                continue
            try:
                target = os.readlink(path)
            except OSError as e:
                print(f"Error reading link '{path}': {e}", file=sys.stderr)
                continue
            
            if not target.startswith('/'):
                continue
            
            new_target = top_dir + target
            new_target_rel = os.path.relpath(new_target, os.path.dirname(path))
            temp_name = f".tmp.{uuid.uuid4().hex}"
            temp_path = os.path.join(root, temp_name)
            try:
                os.symlink(new_target_rel, temp_path)
            except OSError as e:
                print(f"Failed to create temporary symlink for '{path}': {e}", file=sys.stderr)
                continue
            try:
                os.replace(temp_path, path)
                print(f"Updated: {path} -> {new_target_rel}")
            except OSError as e:
                print(f"Failed to replace symlink '{path}': {e}", file=sys.stderr)
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = './sysroot_ubuntu_1604'
    fix_symlinks(directory)
