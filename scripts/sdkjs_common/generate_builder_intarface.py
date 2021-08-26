#!/usr/bin/env python
import os
import shutil

def readFile(path):
  with open(path, "r") as file:
    filedata = file.read()
  return filedata

def writeFile(path, content):
  if (os.path.isfile(path)):
    os.remove(path)

  with open(path, "w") as file:
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
    retType = retParam.replace("|", " ").split(" ")[0]
    retTypeLower = retType.lower()
    retValue = ""
    if -1 != retType.find("\""):
      retValue = "\"\""
    elif "bool" == retTypeLower:
      retValue = "true"
    elif "string" == retTypeLower:
      retValue = "\"\""
    elif "number" == retTypeLower:
      retValue = "0"
    elif "undefined" == retTypeLower:
      retValue = "undefined"
    elif "null" == retTypeLower:
      retValue = "null"
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
    decoration = "/**" + rec[0:indexEndDecoration + 2]
    decoration = decoration.replace("Api\n", "ApiInterface\n")
    decoration = decoration.replace("Api ", "ApiInterface ")
    decoration = decoration.replace("{Api}", "{ApiInterface}")
    decoration = decoration.replace("@return ", "@returns ")
    decoration = decoration.replace("@returns {?", "@returns {")
    if -1 != decoration.find("@name ApiInterface"):
      self.append_record(decoration, "var ApiInterface = function() {};\nvar Api = new ApiInterface();\n", True)
      return
    code = rec[indexEndDecoration + 2:]
    code = code.strip("\t\n\r ")
    lines = code.split("\n")
    codeCorrect = ""
    sFuncName = ""
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
      file_content = readFile(file)
      arrRecords = file_content.split("/**")
      arrRecords = arrRecords[1:-1]
      for record in arrRecords:
        self.check_record(record)
      self.numfile += 1
    correctContent = ''.join(self.records)
    correctContent += "\n"
    os.mkdir('deploy/api_builder/' + self.folder)
    writeFile("deploy/api_builder/" + self.folder + "/api.js", correctContent)
    return

def convert_to_interface(arrFiles, sEditorType):
  editor = EditorApi()
  editor.initFiles(sEditorType, arrFiles)
  editor.generate()
  return

old_cur = os.getcwd()
os.chdir("../../../sdkjs")
if True == os.path.isdir('deploy/api_builder'):
  shutil.rmtree('deploy/api_builder', ignore_errors=True)
os.mkdir('deploy/api_builder')
convert_to_interface(["word/apiBuilder.js"], "word")
convert_to_interface(["word/apiBuilder.js", "slide/apiBuilder.js"], "slide")
convert_to_interface(["word/apiBuilder.js", "slide/apiBuilder.js", "cell/apiBuilder.js"], "cell")
os.chdir(old_cur)
