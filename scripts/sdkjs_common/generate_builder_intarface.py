#!/usr/bin/env python
import os
import shutil
import re
import argparse

def readFile(path):
  with open(path, "r", errors='replace') as file:
    filedata = file.read()
  return filedata

def writeFile(path, content):
  if (os.path.isfile(path)):
    os.remove(path)

  with open(path, "w", encoding='utf-8') as file:
    file.write(content)
  return

class EditorApi(object):
  def __init__(self):
    self.records = []
    self.init = False
    self.folder = "word"
    self.type = "CDE"
    self.numfile = 0
    self.files = []
    return

  def initFiles(self, type, files):
    self.folder = type
    if "word" == self.folder:
      self.type = "CDE"
    elif "slide" == self.folder:
      self.type = "CPE"
    else:
      self.type = "CSE"
    self.files = files
    return

  def getReturnValue(self, description):
    paramStart = description.find("@returns {")
    if -1 == paramStart:
      return "{}"
    paramEnd = description.find("}", paramStart)
    retParam = description[paramStart + 10:paramEnd]
    isArray = False
    if -1 != retParam.find("[]"):
      isArray = True
      retParam = retParam.replace("[]", "")
    retType = retParam.replace("|", " ").replace(".", " ").split(" ")[0]
    retTypeLower = retType.lower()
    retValue = ""
    if -1 != retType.find("\""):
      retValue = "\"\""
    elif "boolean" == retTypeLower or "bool" == retTypeLower:
      retValue = "true"
    elif "string" == retTypeLower:
      retValue = "\"\""
    elif "number" == retTypeLower:
      retValue = "0"
    elif "undefined" == retTypeLower:
      retValue = "undefined"
    elif "null" == retTypeLower:
      retValue = "null"
    elif "array" == retTypeLower:
      retValue = "[]"
    elif "base64img" == retTypeLower:
      retValue = "base64img"
    elif "error" == retTypeLower:
      retValue = "undefined"
    else:
      retValue = "new " + retType + "()"
    if isArray:
      retValue = "[" + retValue + "]"
    return "{ return " + retValue + "; }"

  def check_record(self, recordData):
    rec = recordData
    rec = rec.replace("\t", "")
    rec = rec.replace('\n    ', '\n')
    indexEndDecoration = rec.find("*/")

    indexOfStartPropName = rec.find('Object.defineProperty(')
    if indexOfStartPropName != -1:
      propName = re.search(r'"([^\"]*)"', rec[indexOfStartPropName:])[0]
    else:
      propName = None

    decoration = "/**" + rec[0:indexEndDecoration + 2]
    decoration = decoration.replace("Api\n", "ApiInterface\n")
    decoration = decoration.replace("Api ", "ApiInterface ")
    decoration = decoration.replace("{Api}", "{ApiInterface}")
    decoration = decoration.replace("@return ", "@returns ")
    decoration = decoration.replace("@returns {?", "@returns {")
    decoration = decoration.replace("?}", "}")
    if -1 != decoration.find("@name ApiInterface"):
      self.append_record(decoration, "var ApiInterface = function() {};\nvar Api = new ApiInterface();\n", True)
      return
    code = rec[indexEndDecoration + 2:]
    code = code.replace("=\n", "= ").strip("\t\n\r ")
    lines = code.split("\n")
    codeCorrect = ""
    sMethodName = re.search(r'.prototype.(.*)=', code)

    is_found_function = False
    addon_for_func = "{}"
    if -1 != decoration.find("@return"):
      addon_for_func = "{ return null; }"

    for line in lines:
      line = line.strip("\t\n\r ")
      line = line.replace("{", "")
      line = line.replace("}", "")
      lineWithoutSpaces = line.replace(" ", "")
      if not is_found_function and 0 == line.find("function "):
        if -1 == decoration.find("@constructor"):
          return
        codeCorrect += (line + addon_for_func + "\n")
        is_found_function = True
      if not is_found_function and -1 != line.find(".prototype."):
        codeCorrect += (line + self.getReturnValue(decoration) + ";\n")
        is_found_function = True
      if -1 != lineWithoutSpaces.find(".prototype="):
        codeCorrect += (line + "\n")
      if -1 != line.find(".prototype.constructor"):
        codeCorrect += (line + "\n")
    codeCorrect = codeCorrect.replace("Api.prototype", "ApiInterface.prototype")
    self.append_record(decoration, codeCorrect)
    className = codeCorrect[0:codeCorrect.find('.')]
    
    # если свойство определено сразу под методом (без декорации)
    if propName is not None and sMethodName is not None:
      prop_define = f'{className}.prototype.{propName[1:-1]} = {className}.prototype.{sMethodName.group(1)}();\n'
      self.append_record(decoration, prop_define)
    #иначе
    elif propName is not None:
      className = re.search(r'.defineProperty\((.*).prototype', code).group(1).strip()
      returnValue = 'undefined' if decoration.find('@return') == -1 else self.getReturnValue(decoration)
      if (returnValue != 'undefined'):
        returnValue = re.search(r'{ return (.*); }', returnValue).group(1).strip()
      prop_define = f'{className}.prototype.{propName[1:-1]} = {returnValue};\n'
      self.append_record(decoration, prop_define)
    return

  def append_record(self, decoration, code, init=False):
    if init:
      if not self.init:
        self.init = True
        self.records.append(decoration + "\n" + code + "\n\n")
      return
    # check on private
    if -1 != code.find(".prototype.private_"):
      return
    # add records only for current editor
    index_type_editors = decoration.find("@typeofeditors")
    if -1 != index_type_editors:
      index_type_editors_end = decoration.find("]", index_type_editors) 
      if -1 != index_type_editors_end:
        editors_support = decoration[index_type_editors:index_type_editors_end]
        if -1 == editors_support.find(self.type):
          return
        
    decoration = "\n".join(
        line for line in decoration.splitlines()
        if "@typeofeditors" not in line and "@see" not in line
    )
    
    # optimizations for first file
    if 0 == self.numfile:
      self.records.append(decoration + "\n" + code + "\n")
      return
    # check override js classes
    if 0 == code.find("function "):
      index_end_name = code.find("(")
      function_name = code[9:index_end_name].strip(" ")
      for rec in range(len(self.records)):
        if -1 != self.records[rec].find("function " + function_name + "("):
          self.records[rec] = ""
        elif -1 != self.records[rec].find("function " + function_name + " ("):
          self.records[rec] = ""
        elif -1 != self.records[rec].find("\n" + function_name + ".prototype."):
          self.records[rec] = ""

    self.records.append(decoration + "\n" + code + "\n")
    return

  def generate(self):
    for file in self.files:
      file_content = readFile(f'{sdkjs_dir}/{file}')
      arrRecords = file_content.split("/**")
      arrRecords = arrRecords[1:-1]
      for record in arrRecords:
        self.check_record(record)
      self.numfile += 1
    correctContent = ''.join(self.records)
    correctContent += "\n"
    os.mkdir(args.destination + self.folder)
    writeFile(args.destination + self.folder + "/api.js", correctContent)
    return

def convert_to_interface(arrFiles, sEditorType):
  editor = EditorApi()
  editor.initFiles(sEditorType, arrFiles)
  editor.generate()
  return

sdkjs_dir = "../../../sdkjs"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument(
        "destination", 
        type=str, 
        help="Destination directory for the generated documentation",
        nargs='?',  # Indicates the argument is optional
        default="../../../web-apps/vendor/monaco/libs/"  # Default value
    )
    args = parser.parse_args()
    
    old_cur = os.getcwd()
    
    if True == os.path.isdir(args.destination):
      shutil.rmtree(args.destination, ignore_errors=True)
    os.mkdir(args.destination)
    convert_to_interface(["word/apiBuilder.js", "../sdkjs-forms/apiBuilder.js"], "word")
    convert_to_interface(["word/apiBuilder.js", "slide/apiBuilder.js"], "slide")
    convert_to_interface(["word/apiBuilder.js", "slide/apiBuilder.js", "cell/apiBuilder.js"], "cell")
    os.chdir(old_cur)


