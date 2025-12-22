#!/usr/bin/env python3

import sys
import os
sys.path.append('../../../scripts')

import base

URL = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/sysroot/"

SYSROOTS = {
  "amd64": "ubuntu16-amd64-sysroot.tar.gz",
  "arm64": "ubuntu16-arm64-sysroot.tar.gz",
}

def patch_linker_scripts(sysroot_path, arch):
  """Fix absolute paths in linker scripts to use sysroot-relative paths"""
  
  # Determine directories to patch
  lib_dirs = []
  
  if arch == "arm64":
    lib_dirs = [
      os.path.join(sysroot_path, "usr/lib/aarch64-linux-gnu")
    ]
  elif arch == "amd64":
    lib_dirs = [
      os.path.join(sysroot_path, "usr/lib/x86_64-linux-gnu"),
      os.path.join(sysroot_path, "usr/aarch64-linux-gnu/lib")
    ]
  else:
    return
  
  total_patched = 0
  
  for lib_dir in lib_dirs:
    if not os.path.exists(lib_dir):
      print(f"Warning: {lib_dir} not found, skipping")
      continue
    
    print(f"Patching linker scripts in {lib_dir}...")
    patched_count = 0
    
    for filename in os.listdir(lib_dir):
      if not filename.endswith(".so"):
        continue
      
      filepath = os.path.join(lib_dir, filename)
      if not os.path.isfile(filepath):
        continue
      
      # Check if it's a text file (linker script)
      try:
        with open(filepath, 'r') as f:
          content = f.read()
        
        # Skip if not a linker script
        if "GROUP" not in content and "INPUT" not in content:
          continue
          
        original_content = content
        
        # STEP 1: Normalize all /usr/lib paths to /lib
        # ORDER MATTERS - do longest paths first to avoid partial matches
        
        # For aarch64
        content = content.replace("/usr/aarch64-linux-gnu/lib/", "/lib/aarch64-linux-gnu/")
        content = content.replace("/usr/lib/aarch64-linux-gnu/", "/lib/aarch64-linux-gnu/")
        
        # For x86_64  
        content = content.replace("/usr/x86_64-linux-gnu/lib/", "/lib/x86_64-linux-gnu/")
        content = content.replace("/usr/lib/x86_64-linux-gnu/", "/lib/x86_64-linux-gnu/")
        
        # STEP 2: Add = prefix for sysroot-relative paths
        content = content.replace("/lib/aarch64-linux-gnu/", "=/lib/aarch64-linux-gnu/")
        content = content.replace("/lib/x86_64-linux-gnu/", "=/lib/x86_64-linux-gnu/")
        
        # Write back only if changed
        if content != original_content:
          with open(filepath, 'w') as f:
            f.write(content)
          
          print(f"  Patched: {filename}")
          patched_count += 1
      except Exception as e:
        # Not a text file or other error, skip
        pass
    
    total_patched += patched_count
    print(f"Patched {patched_count} linker scripts in {lib_dir}")
  
  print(f"Total patched: {total_patched} linker scripts")
  
  # Create symlinks from /lib to /usr/lib for library resolution
  create_lib_symlinks(sysroot_path, arch)
  
  # Fix absolute symlinks to relative ones
  fix_absolute_symlinks(sysroot_path, arch)


def create_lib_symlinks(sysroot_path, arch):
  """Create symlinks from /lib to /usr/lib for library resolution"""
  print(f"Creating library symlinks in {sysroot_path}...")
  
  if arch == "arm64":
    lib_symlink_dir = os.path.join(sysroot_path, "lib/aarch64-linux-gnu")
    lib_target_dir = os.path.join(sysroot_path, "usr/lib/aarch64-linux-gnu")
  elif arch == "amd64":
    lib_symlink_dir = os.path.join(sysroot_path, "lib/x86_64-linux-gnu")
    lib_target_dir = os.path.join(sysroot_path, "usr/lib/x86_64-linux-gnu")
  else:
    return
  
  # Create /lib/{arch} directory
  os.makedirs(lib_symlink_dir, exist_ok=True)
  
  if not os.path.exists(lib_target_dir):
    print(f"  Warning: Target directory {lib_target_dir} does not exist")
    return
  
  symlink_count = 0
  
  # Create symlinks for all files in /usr/lib/{arch}
  for filename in os.listdir(lib_target_dir):
    target = os.path.join(lib_target_dir, filename)
    link = os.path.join(lib_symlink_dir, filename)
    
    # Skip if symlink already exists
    if os.path.exists(link) or os.path.islink(link):
      continue
    
    # Create relative symlink
    rel_target = os.path.relpath(target, lib_symlink_dir)
    try:
      os.symlink(rel_target, link)
      symlink_count += 1
    except OSError as e:
      print(f"  Warning: Could not create symlink {link}: {e}")
  
  print(f"Created {symlink_count} symlinks in {lib_symlink_dir}")


def fix_absolute_symlinks(sysroot_path, arch):
  """Fix absolute symlinks in /usr/lib to use relative paths"""
  print(f"Fixing absolute symlinks in {sysroot_path}...")
  
  if arch == "arm64":
    lib_dir = os.path.join(sysroot_path, "usr/lib/aarch64-linux-gnu")
  elif arch == "amd64":
    lib_dir = os.path.join(sysroot_path, "usr/lib/x86_64-linux-gnu")
  else:
    return
  
  if not os.path.exists(lib_dir):
    print(f"  Warning: {lib_dir} not found")
    return
  
  fixed_count = 0
  
  # Find all .so symlinks pointing to /lib/
  for filename in os.listdir(lib_dir):
    if not filename.endswith(".so"):
      continue
    
    filepath = os.path.join(lib_dir, filename)
    
    # Check if it's a symlink
    if not os.path.islink(filepath):
      continue
    
    # Get symlink target
    target = os.readlink(filepath)
    
    # Check if it's an absolute path starting with /lib/
    if target.startswith("/lib/"):
      # Convert to relative path: /lib/... -> ../../../lib/...
      relative_target = os.path.join("../../..", target[1:])  # Remove leading /
      
      # Remove old symlink and create new one
      os.unlink(filepath)
      os.symlink(relative_target, filepath)
      
      print(f"  Fixed: {filename} -> {relative_target}")
      fixed_count += 1
  
  print(f"Fixed {fixed_count} absolute symlinks")

def download_and_extract(name):
  archive = SYSROOTS[name]
  base.download(URL + archive, "./" + archive)
  base.cmd("tar", ["-xzf", "./" + archive])

  sysroot_name = archive.replace(".tar.gz", "")
  patch_linker_scripts(sysroot_name, name)

def main():
  if len(sys.argv) != 2:
    print("Usage: fetch.py [amd64|arm64|all]")
    sys.exit(1)

  target = sys.argv[1]

  if target == "all":
    for name in SYSROOTS:
      download_and_extract(name)
  elif target in SYSROOTS:
    download_and_extract(target)
  else:
    print(f"Unknown target: {target}")
    print("Valid values: amd64, arm64, all")
    sys.exit(1)

if __name__ == "__main__":
    main()
