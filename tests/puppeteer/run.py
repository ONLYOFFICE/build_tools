#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import json

def get_tests_in_dir(directory):
  files = []
  for file in glob.glob(directory + "/*.js"):
    if base.is_file(file):
      files.append(file)
    elif is_dir(file):
      files += get_tests_in_dir(file)
  return files

params = sys.argv[1:]
if (0 == len(params)):
  print("use: run.py path_to_config [path_to_test]")
  exit(0)

config_path = params[0]
test_file = "./tests"

if (1 < len(params)):
  test_file = params[1]

tests_array = [test_file]
if base.is_dir(test_file):
  tests_array = get_tests_in_dir(test_file)

config_content = "{}"
with open(config_path, "r") as config_path_loader:
  config_content = config_path_loader.read()

print(config_content)

config = json.loads(config_content)
os.environ["PUPPETEER_SKIP_CHROMIUM_DOWNLOAD"] = "true"
if "browser" in config:
  print("browser: " + config["browser"])
  os.environ["PUPPETEER_PRODUCT"] = config["browser"]

if "browserUrl" in config:
  print("browserUrl: " + config["browserUrl"])
  os.environ["PUPPETEER_EXECUTABLE_PATH"] = config["browserUrl"]

if not base.is_dir("./work_directory"):
  base.create_dir("./work_directory")
  base.create_dir("./work_directory/cache")
  base.create_dir("./work_directory/downloads")

for test in tests_array:
  print("run test: " + test)
  run_file = test + ".runned.js"
  base.copy_file("./tester.js", run_file)
  test_content = base.readFile(test)
  test_content = test_content.replace("await Tester.", "Tester.")
  test_content = test_content.replace("Tester.", "await Tester.")
  base.replaceInFile(run_file, "\"%%CODE%%\"", test_content)
  base.cmd("node", [run_file])
  base.delete_file(run_file)
